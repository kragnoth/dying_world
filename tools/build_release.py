#!/usr/bin/env python3
"""build_release.py - CURSEFORGE-SAFE build: keeps only structures whose pieces are OWN / VANILLA / confirmed in tools/release_policy.json.
Output: dist/release/dying_world_release_datapack.zip + docs/release_report.md (kept, dropped + why, rebuild queue, mod requirements).
How: copies datapack/ to dist/release/tree, strips third-party pool elements (donor houses, third-party base houses...), recomputes each structure's closure with the
provenance audit, drops structures/sets that still pull third-party pieces, pools, processors or structure types (or have no houses left), copies only the files the kept
structures need (+ the empty structure_set overrides that disable natural structures), fixes exclusion zones, then scans the result for third-party namespaces.
Run `python3 tools/build_release.py` (validates nothing else; run tools/build.py for the full private build)."""
import collections, gzip, json, re, shutil, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_audit as PA
ROOT = PA.ROOT
POL = json.loads((ROOT / "tools/release_policy.json").read_text())
CONF = set(POL.get("confirmed_mine", [])); PERM = [x.lower() for x in POL.get("permission_granted", [])]
TREE = ROOT / "dist/release/tree"; SRC = ROOT / "datapack/data"

def ok(c):
    if c in ("OWN", "OWN?", "VANILLA"): return True
    if c.startswith("KUBEJS:"): return "kubejs" in CONF or c.split(":", 1)[1] in CONF
    if c.startswith("MOD:"): return any(t in c.lower() for t in PERM)
    return False
def jload(f): return json.loads(f.read_text())
def jsave(f, o): f.parent.mkdir(parents=True, exist_ok=True); f.write_text(json.dumps(o, indent=2) + "\n")

def strip_element(e):                                           # True = keep
    el = e["element"] if "element" in e else e
    if el.get("element_type") == "minecraft:list_pool_element":
        el["elements"] = [x for x in el["elements"] if strip_element(x)]; return bool(el["elements"])
    loc = el.get("location")
    if not loc: return True                                     # empty / feature elements
    ns, p = loc.split(":"); c = PA.piece_class(ns, p)
    if not ok(c): return False
    pr = el.get("processors")
    if isinstance(pr, str) and pr != "minecraft:empty":
        pns = pr.split(":")[0]
        if pns not in ("minecraft", "dying_world") and not any(t in PA.provider(pns).lower() for t in PERM): return False
        if pns == "dying_world" and pr.startswith("dying_world:mix/"): return False     # combined donor processors
    return True

def main():
    if TREE.parent.exists(): shutil.rmtree(TREE.parent)
    shutil.copytree(SRC, TREE / "data")
    PA.DP = TREE / "data"; PA.NBT_CACHE.clear()
    # 1. strip third-party elements from every pool we ship
    for f in list((TREE / "data").rglob("template_pool/**/*.json")):
        pool = jload(f); n0 = len(pool["elements"])
        pool["elements"] = [e for e in pool["elements"] if strip_element(e)]
        if len(pool["elements"]) != n0: jsave(f, pool)
    # 2. closure of every set / structure
    sets = {f.stem: jload(f) for f in sorted((TREE / "data/dying_world/worldgen/structure_set").glob("*.json"))}
    kept, dropped, need = {}, [], collections.defaultdict(set)
    ranking = {}
    for sname, sd in sets.items():
        good = []
        for st in sd["structures"]:
            sid = st["structure"]; R = PA.closure(sid); why = []
            t = R["type"] or ""
            if t and not t.startswith("minecraft:") and not any(x in PA.provider(t.split(":")[0]).lower() for x in PERM) and t.split(":")[0] != "dying_world": why.append(f"structure type {t}")
            bad = collections.Counter(c.split(":")[0] + ":" + (c.split(":", 1)[1] if ":" in c else "") for c in R["pieces"].values() if not ok(c))
            if bad: why.append("third-party pieces " + ", ".join(f"{k.rstrip(':')} x{v}" for k, v in bad.items()))
            tp = [k for k in R["pool_cls"] if (k.startswith("MOD") or k.startswith("KUBEJS")) and not ok(k)]
            if tp: why.append("third-party pools " + ", ".join(tp))
            tpp = [k for k in R["proc_cls"] if (k.startswith("MOD") or k.startswith("KUBEJS")) and not ok(k)]
            if tpp: why.append("third-party processors")
            m = re.match(r"dying_world:village_([a-z]+)$", sid)
            if m:
                hp = TREE / f"data/minecraft/worldgen/template_pool/village/{m.group(1)}/houses.json"
                if not hp.exists() or not any("location" in x["element"] for x in jload(hp)["elements"]): why.append("no houses left after stripping")
            if why: ranking[sid] = (len(R["pieces"]), why)
            else: good.append((sid, R))
        if good and sname not in POL.get("force_drop_sets", []): kept[sname] = good
        else: dropped.append(sname)
    for s in POL.get("force_keep_sets", []):
        if s in dropped: dropped.remove(s)
    # 3. files needed by kept structures
    keep_files = set()
    def add(path):
        if path.exists(): keep_files.add(path)
    def add_tag(tid, kind):
        ns, p = tid.split(":"); f = TREE / f"data/{ns}/tags/{kind}/{p}.json"
        if f.exists() and f not in keep_files:
            keep_files.add(f)
            for v in jload(f)["values"]:
                v = v["id"] if isinstance(v, dict) else v
                if v.startswith("#"): add_tag(v[1:], kind)
    req = collections.defaultdict(collections.Counter)
    for sname, good in kept.items():
        add(TREE / f"data/dying_world/worldgen/structure_set/{sname}.json")
        for sid, R in good:
            ns, p = sid.split(":")
            add(TREE / f"data/{ns}/worldgen/structure/{p}.json")
            if R["biome_tag"]: add_tag(R["biome_tag"], "worldgen/biome")
            for pid in R["dp_pools"]: ns2, p2 = pid.split(":"); add(TREE / f"data/{ns2}/worldgen/template_pool/{p2}.json")
            for ns2, p2 in R["dp_nbt"]: add(TREE / f"data/{ns2}/structure/{p2}.nbt")
            for pr in R["procs"]:
                ns2, p2 = pr.split(":"); f = TREE / f"data/{ns2}/worldgen/processor_list/{p2}.json"
                if f.exists():
                    add(f)
                    for mm in re.finditer(r'"#([a-z0-9_]+):([a-z0-9_/]+)"', f.read_text()): add_tag(f"{mm.group(1)}:{mm.group(2)}", "block")
            for lt in R["loot"]: ns2, p2 = lt.split(":"); add(TREE / f"data/{ns2}/loot_table/{p2}.json")
            for b, n in R["blocks"].items():
                if n and b.split(":")[0] not in ("minecraft", "dying_world"): req[b.split(":")[0]]["blocks"] += n
            for mb in R["mobs"]:
                if mb != "minecraft": req[mb]["mobs"] += 1
            for bn, cnt in R["biome_ns"].items():
                if bn not in ("minecraft", "dying_world", "c"): req[bn]["biome ids (optional)"] += cnt
    for f in (TREE / "data").rglob("structure_set/*.json"):                  # keep every set that merely DISABLES a natural set
        if f.parts[-5] != "dying_world" and jload(f).get("structures") == []: keep_files.add(f)
    # 4. write release tree (+ exclusion zones of dropped sets removed)
    out = ROOT / "dist/release/rel"; shutil.rmtree(out, ignore_errors=True); kept_sets = set(kept)
    for f in sorted(keep_files):
        dst = out / "data" / f.relative_to(TREE / "data"); dst.parent.mkdir(parents=True, exist_ok=True)
        if f.name in {s + ".json" for s in sets} and f.parent.name == "structure_set" and f.parts[-5] == "dying_world":
            d = jload(f); ez = d["placement"].get("exclusion_zone")
            if ez and ez["other_set"].split(":")[1] not in kept_sets: del d["placement"]["exclusion_zone"]
            d["structures"] = [s for s in d["structures"] if s["structure"] in {sid for sid, _ in kept[f.stem]}]
            jsave(dst, d)
        else: shutil.copy2(f, dst)
    # loot item namespaces
    for f in out.rglob("loot_table/**/*.json"):
        for m in re.finditer(r'"name":\s*"([a-z0-9_]+):', f.read_text()):
            if m.group(1) != "minecraft": req[m.group(1)]["loot entries"] += 1
    (out / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 48, "description": "Dying World - release (no third-party structure content)"}}, indent=2) + "\n")
    # 5. scan for third-party namespaces in what we ship
    TP = {"kaisyn", "brutos", "gearwrights", "vsrevamped", "towns_and_towers", "forsaken", "createnewbeg", "abandoned_cabins", "watchtower_building", "windswept",
          "hearths", "cultivar", "formationsnether", "formationsoverworld", "caverns_and_chasms", "tarbound", "supplementaries", "atmospheric", "autumnity", "environmental"}
    TP = {t for t in TP if not any(t in x for x in PERM) and t not in CONF}
    hits = collections.Counter()
    for f in out.rglob("*"):
        if not f.is_file() or "structure_set" in f.parts and f.parts[-5] != "dying_world": continue
        if "biome" in f.parts and "tags" in f.parts: continue          # optional biome ids only: a dependency note, not third-party content
        raw = f.read_bytes()
        if f.suffix == ".nbt": raw = gzip.decompress(raw)
        for t in TP:
            ns_dir = f.relative_to(out).parts[1] == t if len(f.relative_to(out).parts) > 1 else False
            if re.search(rb'[#"\x00-\x1f]%s:' % t.encode(), raw) and f.suffix != ".nbt" or (f.suffix == ".nbt" and re.search(rb"[^a-z_]%s:" % t.encode(), raw) and False): hits[(t, f.relative_to(out).as_posix())] += 1
    zp = ROOT / "dist/release/dying_world_release_datapack.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.rglob("*")):
            if f.is_file(): z.write(f, f.relative_to(out).as_posix())
    # 6. report
    L = ["# Release build report (generated by tools/build_release.py)\n", f"Policy: confirmed_mine={sorted(CONF) or '-'}; permission_granted={PERM or '-'}\n",
         f"Release zip: `dist/release/dying_world_release_datapack.zip` ({zp.stat().st_size // 1024} KB), {sum(1 for f in out.rglob('*') if f.is_file())} files.\n", "## Kept sets\n"]
    for s, good in kept.items(): L.append(f"- **{s}**: {', '.join(sid.split(':')[1] for sid, _ in good)}")
    L += ["\n## Dropped (rebuild queue: fewest third-party pieces first = easiest)\n", "| structure | third-party pieces | why |", "|---|---|---|"]
    for sid, (n, why) in sorted(ranking.items(), key=lambda kv: kv[1][0]): L.append(f"| {sid} | {n} | {'; '.join(why)} |")
    L += ["\n## Mods the RELEASE datapack needs (hard = blocks/loot/mobs placed; soft = biome ids, optional)\n", "| namespace | provider | what |", "|---|---|---|"]
    for ns, c in sorted(req.items()): L.append(f"| {ns} | {PA.provider(ns)} | {', '.join(f'{k}: {v}' for k, v in c.items())} |")
    audit = json.loads((ROOT / "docs/provenance_audit.json").read_text()); ck = audit.get("content_keys", {})
    inv_ns = sorted({s["id"].split(":")[0] for s in PA.INV} - {"minecraft"})
    L += ["\n## Mods you could drop from the PACK (worldgen side only)\n", "Structure-provider mods with NO hard reference left in the release datapack. 'lang keys' = items/blocks/entities the mod adds (0 or none = probably structures only; CHECK you do not use anything else from it).\n",
          "| namespace | provider | lang keys | still referenced by the release? | verdict |", "|---|---|---|---|---|"]
    for ns in inv_ns:
        prov_ = PA.provider(ns); hard = ns in req and any(k in req[ns] for k in ("blocks", "loot entries", "mobs")); soft = ns in req and not hard
        kj = prov_ == "kubejs"
        verdict = ("delete its files from kubejs/data once replaced" if kj else "REMOVE if you do not use its content" if ck.get(ns, 0) == 0 else "content mod: your call (nothing from it is needed by the release)")
        if hard: verdict = "keep (our structures place its blocks)"
        L.append(f"| {ns} | {prov_} | {ck.get(ns, 0)} | {'HARD' if hard else 'biomes only' if soft else 'no'} | {verdict} |")
    L += ["\n## Third-party namespace scan of the release files\n", "- " + ("CLEAN (no references)" if not hits else "\n- ".join(f"{t} in `{p}`" for (t, p) in sorted(hits)))]
    (ROOT / "docs/release_report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:12])); print("...", len(ranking), "structures dropped; hits:", len(hits))

if __name__ == "__main__":
    main()
