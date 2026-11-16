#!/usr/bin/env python3
"""
gen_pass1.py - (re)generate the "disable all natural structures" datapack and
the structure inventory docs from a packwork.zip.

Re-run whenever the modlist changes (new mods = new structure sets):
    python3 tools/gen_pass1.py --packwork /path/to/packwork.zip
    python3 tools/gen_pass1.py --packwork ... --check     # only report drift

Outputs (relative to project root):
    datapack/                       the disable datapack (data/<ns>/worldgen/structure_set/*.json)
    docs/structure_inventory.md     human-readable inventory
    docs/structure_inventory.json   full machine-readable inventory (reference for later passes)
    docs/disabled_structure_sets.txt
    docs/feature_structure_candidates.md   feature-based "structures" (NOT disabled yet)

Method: every worldgen/structure_set is overridden at its original id with an
empty "structures" list. Nothing can spawn from an empty set, and the original
(possibly modded-type) placement is replaced by a plain vanilla random_spread so
it can't depend on any mod codec.
"""
import argparse, collections, json, re, shutil, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_FORMAT = 48  # 1.21.1 data pack format
EMPTY_SET = {
    "structures": [],
    "placement": {"type": "minecraft:random_spread", "spacing": 34, "separation": 8, "salt": 0},
}
SET_RE = re.compile(r"^data/([^/]+)/worldgen/structure_set/(.+)\.json$")
NBT_RE = re.compile(r"^data/([^/]+)/structures?/.+\.nbt$")
POOL_RE = re.compile(r"^data/([^/]+)/worldgen/template_pool/.+\.json$")
BM_RE = re.compile(r"^data/([^/]+)/neoforge/biome_modifier/.+\.json$")


def loads(b: bytes):
    """JSON loader tolerant of // and /* */ comments and trailing commas."""
    s = b.decode("utf-8-sig", "replace")
    out, i, instr = [], 0, False
    while i < len(s):
        c = s[i]
        if instr:
            out.append(c)
            if c == "\\":
                out.append(s[i + 1:i + 2]); i += 1
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True; out.append(c)
        elif c == "/" and s[i + 1:i + 2] == "/":
            while i < len(s) and s[i] != "\n":
                i += 1
            continue
        elif c == "/" and s[i + 1:i + 2] == "*":
            i = s.index("*/", i + 2) + 2
            continue
        else:
            out.append(c)
        i += 1
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))


def providers(z):
    """namespace -> top provider jar, parsed from _packwork_sources.md section 6."""
    res = {}
    try:
        txt = z.read("_packwork_sources.md").decode()
    except KeyError:
        return res
    for m in re.finditer(r"^- `([^`]+)`: (.+)$", txt.split("## 6.")[-1], re.M):
        res[m.group(1)] = re.sub(r" \(\d+\)$", "", m.group(2).split(", ")[0])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packwork", required=True)
    ap.add_argument("--check", action="store_true", help="report drift only, write nothing")
    a = ap.parse_args()

    z = zipfile.ZipFile(a.packwork)
    names = z.namelist()
    prov = providers(z)

    sets = sorted(n for n in names if SET_RE.match(n))
    set_ids = [f"{SET_RE.match(n).group(1)}:{SET_RE.match(n).group(2)}" for n in sets]

    dp = ROOT / "datapack"
    existing = {str(p.relative_to(dp)).replace("\\", "/")
                for p in dp.rglob("worldgen/structure_set/*.json")
                if "data/dying_world/" not in p.as_posix()} if dp.exists() else set()
    wanted = {n for n in sets}
    if a.check:
        print(f"packwork structure sets : {len(wanted)}")
        print(f"datapack structure sets : {len(existing)}")
        print("missing from datapack   :", sorted(wanted - existing) or "none")
        print("stale in datapack       :", sorted(existing - wanted) or "none")
        return

    # ---- datapack -----------------------------------------------------------
    # only touch files this script owns (structure_set overrides); later passes add other files
    for old in dp.glob("data/*/worldgen/structure_set/*.json") if dp.exists() else []:
        if "data/dying_world/" not in old.as_posix():   # keep our own curated sets
            old.unlink()
    for n in sets:
        p = dp / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(EMPTY_SET, indent=2) + "\n")
    (dp / "pack.mcmeta").write_text(json.dumps({"pack": {
        "pack_format": PACK_FORMAT,
        "description": "Dying World - pass 1: all natural structure sets disabled"}}, indent=2) + "\n")

    # ---- inventory ----------------------------------------------------------
    inv, struct_cache = [], {}

    def structure_info(sid):
        if sid in struct_cache:
            return struct_cache[sid]
        ns, _, rel = sid.partition(":")
        info = {"id": sid, "type": "?", "step": "?", "biomes": "?"}
        try:
            j = loads(z.read(f"data/{ns}/worldgen/structure/{rel}.json"))
            b = j.get("biomes")
            info.update(type=j.get("type", "?").split(":")[-1], step=j.get("step", "?"),
                        biomes=b if isinstance(b, str) else f"[{len(b)} biomes]" if b else "?")
        except Exception:
            info["type"] = "(unreadable/missing)"
        struct_cache[sid] = info
        return info

    for n, sid in zip(sets, set_ids):
        ns = sid.split(":")[0]
        entry = {"id": sid, "provider": prov.get(ns, "?"), "placement": {}, "structures": []}
        try:
            j = loads(z.read(n))
            p = j.get("placement", {})
            entry["placement"] = {k: p[k] for k in
                ("type", "spacing", "separation", "salt", "frequency", "distance", "count", "spread")
                if k in p}
            for s in j.get("structures", []):
                d = dict(structure_info(s["structure"])); d["weight"] = s.get("weight", 1)
                entry["structures"].append(d)
        except Exception as e:
            entry["error"] = str(e)
        inv.append(entry)

    docs = ROOT / "docs"; docs.mkdir(exist_ok=True)
    (docs / "structure_inventory.json").write_text(json.dumps(inv, indent=1))
    (docs / "disabled_structure_sets.txt").write_text("\n".join(set_ids) + "\n")

    nbt, pools = collections.Counter(), collections.Counter()
    for n in names:
        if m := NBT_RE.match(n): nbt[m.group(1)] += 1
        if m := POOL_RE.match(n): pools[m.group(1)] += 1
    by_ns = collections.defaultdict(list)
    for e in inv:
        by_ns[e["id"].split(":")[0]].append(e)

    L = ["# Structure inventory (generated by tools/gen_pass1.py)", "",
         f"{len(inv)} structure sets across {len(by_ns)} namespaces. Full detail: `structure_inventory.json`.", "",
         "## By namespace", "", "| namespace | provider jar | sets | structures | nbt files | template pools |",
         "|---|---|---|---|---|---|"]
    for ns in sorted(by_ns):
        es = by_ns[ns]
        L.append(f"| {ns} | {prov.get(ns, '?')} | {len(es)} | {sum(len(e['structures']) for e in es)} "
                 f"| {nbt[ns]} | {pools[ns]} |")
    L += ["", "## Sets", "", "| set | placement | n | structures (first 4) | biomes of first |", "|---|---|---|---|---|"]
    for e in inv:
        p = e["placement"]
        pl = f"{p.get('type', '?').split(':')[-1]} {p.get('spacing', '')}/{p.get('separation', '')}".strip(" /")
        names4 = ", ".join(s["id"].split(":")[-1] for s in e["structures"][:4])
        if len(e["structures"]) > 4: names4 += f" +{len(e['structures']) - 4}"
        b = e["structures"][0]["biomes"] if e["structures"] else ""
        L.append(f"| {e['id']} | {pl} | {len(e['structures'])} | {names4} | {b} |")
    (docs / "structure_inventory.md").write_text("\n".join(L) + "\n")

    # ---- feature-based structure candidates (not disabled) -------------------
    cand = []
    for n in names:
        if BM_RE.match(n):
            try:
                j = loads(z.read(n))
            except Exception:
                continue
            if j.get("type", "").endswith("add_features") and j.get("step") in (
                    "surface_structures", "underground_structures"):
                f = j.get("features")
                cand.append((n[5:].replace("/neoforge/biome_modifier", ""), f if isinstance(f, str) else ", ".join(f), j.get("step")))
    F = ["# Feature-based structure candidates (NOT disabled in pass 1)", "",
         "Biome modifiers that add features in the *_structures steps. These are not structure sets, so",
         "pass 1 does not touch them. Decide per item in pass 2 (disable with a `neoforge:none` override of",
         "the same biome_modifier path, or keep). Vanilla also has feature-based things (monster rooms,",
         "fossils, desert wells, geodes, etc.) which live in biome JSON - handle with a `neoforge:remove_features`",
         "biome modifier in pass 2.", "", "| biome_modifier | features | step |", "|---|---|---|"]
    F += [f"| {a_} | {b_} | {c_} |" for a_, b_, c_ in sorted(cand)]
    (docs / "feature_structure_candidates.md").write_text("\n".join(F) + "\n")

    print(f"structure sets disabled : {len(sets)}")
    print(f"feature candidates      : {len(cand)}")
    print("now run: python3 tools/build.py")


if __name__ == "__main__":
    main()
