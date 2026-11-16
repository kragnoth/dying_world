#!/usr/bin/env python3
"""provenance_audit.py - WHERE does every structure of our datapack come from, and which mods does it need?  Output: docs/provenance_audit.md + .json
Purpose: (1) CurseForge release without third-party permissions: find every structure whose pieces are 100% / partly third-party (mod or kubejs-provided),
         (2) mod-count reduction: per-mod dependency matrix (pieces, blocks, loot, biomes, mobs) + 'what must change to drop mod X'.
Classes of a piece (NBT) / pool / processor:  OWN (script-built, no input)  VANILLA (Mojang resources)  KUBEJS (provided by kubejs/data: gearwrights, vsrevamped, brutos,
  and the custom village HOUSE sets replacing minecraft:village/*/houses -> origin must be confirmed by the user, treated as THIRD-PARTY until then)  MOD:<jar>.
Derived copies inherit their source's class (worn copies of base houses = KUBEJS, mix_worn/<label> = donor mod).
Reads: datapack/data (ours), reference/*.zip (what the pack provides), docs/structure_inventory.json (namespace -> jar), reference/lang (content check).
Safe to re-run; changes nothing except the two docs files."""
import collections, gzip, json, re, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtmini
ROOT = Path(__file__).resolve().parent.parent
DP = ROOT / "datapack/data"
WG, NBTZ = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip"), zipfile.ZipFile(ROOT / "reference/structures_nbt.zip")
LANG = zipfile.ZipFile(ROOT / "reference/lang_en_us.zip")
WGN, NBTN = set(WG.namelist()), set(NBTZ.namelist())
INV = json.load(open(ROOT / "docs/structure_inventory.json"))
PROV = {"minecraft": "vanilla", "dying_world": "OWN"}
for s in INV:
    PROV[s["id"].split(":")[0]] = s["provider"]
    for st in s["structures"]: PROV.setdefault(st["id"].split(":")[0], s["provider"])
PROV.update({"kaisyn": PROV.get("towns_and_towers", "t_and_t"), "brutos": "kubejs (inferred: vsrevamped)", "vsrevamped": "kubejs"})
MODLIST = [l[2:].strip() for l in (ROOT / "docs/mod_list.md").read_text().splitlines() if l.startswith("- ")]
def _n(s): return re.sub(r"[^a-z0-9]", "", s.lower())
def provider(ns):
    if ns in PROV: return PROV[ns]
    hit = [m for m in MODLIST if _n(ns) in _n(m)]
    return hit[0] if hit else "? (not in mod_list.md)"
KUBE_NS = {"gearwrights", "vsrevamped", "brutos"}
OWN_GROUPS = ("mineshaft/", "concrete_pad/", "scavenger_outpost/")
DONOR_OF = {"forest_ruins": "kaisyn", "birch_romanian": "kaisyn", "cherry": "brutos", "snowy_taiga_viking": "kaisyn", "old_growth_polish": "kaisyn",
            "badlands_pueblo": "kaisyn", "wooded_badlands_tipi": "kaisyn", "frozen": "windswept"}
BAD_JSON = []
def rj(t):
    t = re.sub(r"\r", "", t)
    try: return json.loads(t)
    except Exception:
        t2 = re.sub(r"/\*.*?\*/", "", t, flags=re.S); t2 = re.sub(r"(?m)^\s*//.*$", "", t2); t2 = re.sub(r",(\s*[}\]])", r"\1", t2)
        try: return json.loads(t2)
        except Exception: BAD_JSON.append(t[:60]); return None
def jdp_or_ref(rid, kind, ext="json"):
    ns, p = rid.split(":"); f = DP / ns / f"{kind}/{p}.{ext}"
    if f.exists(): return rj(f.read_text()), "dp"
    n = f"data/{ns}/{kind}/{p}.{ext}"
    if n in WGN: return rj(WG.read(n).decode("utf-8")), "ref"
    return None, None
def cls_ns(ns, kind_path=""):
    if ns == "dying_world": return "OWN"
    if ns == "minecraft": return "KUBEJS:village_houses" if re.match(r"village/[a-z]+/houses/", kind_path) else "VANILLA"
    return f"KUBEJS:{ns}" if ns in KUBE_NS else "MOD:" + provider(ns)
def piece_class(ns, p):
    if (DP / ns / f"structure/{p}.nbt").exists():                          # copy inside our datapack
        if ns != "dying_world": return "OWN"
        if p.startswith(OWN_GROUPS): return "OWN"
        m = re.match(r"village/[a-z]+/mix_worn/([a-z_]+)/", p)
        if m: d = DONOR_OF.get(m.group(1), "?"); return f"KUBEJS:{d}" if d in KUBE_NS else "MOD:" + str(provider(d))
        if "/houses_worn/" in p: return "KUBEJS:village_houses"
        if p.startswith("scavenger_stronghold/"): return "VANILLA"       # derived from vanilla bastion/village pieces (gen_pass5_1)
        return "OWN?"
    return cls_ns(ns, p)

NBT_CACHE = {}
def nbt_info(ns, p):
    k = (ns, p)
    if k in NBT_CACHE: return NBT_CACHE[k]
    f = DP / ns / f"structure/{p}.nbt"; n = f"data/{ns}/structure/{p}.nbt"
    raw = f.read_bytes() if f.exists() else (NBTZ.read(n) if n in NBTN else None)
    if raw is None: NBT_CACHE[k] = None; return None
    d = nbtmini.parse(gzip.decompress(raw)); pal = [x["Name"] for x in d["palette"]]
    blocks = collections.Counter(); pools = set(); loot = set()
    for b in d["blocks"]:
        nm = pal[b["state"]]
        if nm == "minecraft:air": continue
        blocks[nm] += 1; nb = b.get("nbt") or {}
        if nm == "minecraft:jigsaw" and nb.get("pool"): pools.add(nb["pool"])
        if nb.get("LootTable"): loot.add(nb["LootTable"])
    NBT_CACHE[k] = (blocks, pools, loot); return NBT_CACHE[k]
def names_in(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("Name", "block") and isinstance(v, str): out.add(v)
            names_in(v, out)
    elif isinstance(obj, list):
        for v in obj: names_in(v, out)
def tag_biome_ns(tid, seen=None):
    seen = seen or set(); out = collections.Counter()
    if tid in seen: return out
    seen.add(tid); t, _ = jdp_or_ref(tid, "tags/worldgen/biome")
    for v in (t or {}).get("values", []):
        v = v["id"] if isinstance(v, dict) else v
        if v.startswith("#"): out += tag_biome_ns(v[1:], seen)
        else: out[v.split(":")[0]] += 1
    return out

def closure(sid):
    s, where = jdp_or_ref(sid, "worldgen/structure")
    R = {"sid": sid, "type": s.get("type") if s else "?", "pieces": {}, "pool_cls": collections.Counter(), "proc_cls": collections.Counter(), "blocks": collections.Counter(),
         "loot": set(), "mobs": set(), "biome_ns": collections.Counter(), "refs": set(),
         "dp_struct": sid if where == "dp" else None, "biome_tag": None, "dp_pools": set(), "dp_nbt": set(), "procs": set()}
    if not s: return R
    for grp in (s.get("spawn_overrides") or {}).values():
        for e in grp.get("spawns", []): R["mobs"].add(e["type"].split(":")[0])
    b = s.get("biomes"); R["biome_tag"] = b[1:] if isinstance(b, str) and b.startswith("#") else None; R["biome_ns"] = tag_biome_ns(b[1:]) if isinstance(b, str) and b.startswith("#") else collections.Counter(x.split(":")[0] for x in (b if isinstance(b, list) else [b or ""]))
    queue, seen, procs = [s["start_pool"]] if s.get("start_pool") else [], set(), set()
    def elems(e):
        if e.get("element_type") == "minecraft:list_pool_element":
            for x in e["elements"]: yield from elems(x)
        else: yield e
    while queue:
        pid = queue.pop()
        if pid in seen or pid == "minecraft:empty": continue
        seen.add(pid); pool, wh = jdp_or_ref(pid, "worldgen/template_pool")
        if not pool: continue
        ns = pid.split(":")[0]
        if wh == "dp": R["dp_pools"].add(pid)
        R["pool_cls"]["OWN" if wh == "dp" and ns == "dying_world" else cls_ns(ns, pid.split(":")[1])] += 1
        if pool.get("fallback"): queue.append(pool["fallback"])
        for e in pool["elements"]:
            for el in elems(e["element"]):
                pr = el.get("processors")
                if isinstance(pr, str) and pr != "minecraft:empty": procs.add(pr); R["procs"].add(pr)
                elif isinstance(pr, dict): names_in(pr, procs_names := set()); R["blocks"].update({n: 0 for n in procs_names})
                loc = el.get("location")
                if not loc: continue
                ns2, p2 = loc.split(":"); info = nbt_info(ns2, p2)
                if info is None: R["refs"].add(f"missing:{loc}"); continue
                c = piece_class(ns2, p2); R["pieces"][loc] = c
                if (DP / ns2 / f"structure/{p2}.nbt").exists(): R["dp_nbt"].add((ns2, p2))
                R["blocks"].update(info[0]); R["loot"] |= info[2]; queue += list(info[1])
    for pr in procs:
        ns = pr.split(":")[0]; R["proc_cls"]["OWN" if ns == "dying_world" else cls_ns(ns)] += 1
        pj, _ = jdp_or_ref(pr, "worldgen/processor_list")
        if pj and ns != "dying_world":
            nm = set(); names_in(pj, nm); R["refs"] |= {f"proc-block:{x}" for x in nm if not x.startswith("minecraft:")}
    return R

def main():
    sets = {}
    for f in sorted((DP / "dying_world/worldgen/structure_set").glob("*.json")):
        sets[f.stem] = [x["structure"] for x in json.loads(f.read_text())["structures"]]
    rows, mods = [], collections.defaultdict(lambda: collections.defaultdict(set))
    modblocks = collections.defaultdict(collections.Counter)
    for sname, sids in sets.items():
        tot = collections.Counter(); sc = collections.Counter(); mobs = set(); structs = 0; blocks = collections.Counter(); bi = collections.Counter(); poolc = collections.Counter(); procc = collections.Counter()
        for sid in sids:
            R = closure(sid); structs += 1
            t = R["type"] or ""
            if t and not t.startswith("minecraft:"):                      # structure TYPE implemented by a mod (code, not pieces)
                c = cls_ns(t.split(":")[0]); tot[c.split(":")[0]] += 1
                mods[c][sname].add(f"<structure type {t}>")
            for loc, c in R["pieces"].items():
                tot[c.split(":")[0]] += 1
                if c.startswith("MOD") or c.startswith("KUBEJS"): mods[c][sname].add(loc)
            blocks.update(R["blocks"]); mobs |= R["mobs"]; bi += R["biome_ns"]; poolc += R["pool_cls"]; procc += R["proc_cls"]
        for b, n in blocks.items():
            ns = b.split(":")[0]
            if ns not in ("minecraft", "dying_world"): modblocks[ns][sname] += n
        third = tot["MOD"] + tot["KUBEJS"]; clean = tot["OWN"] + tot["VANILLA"] + tot["OWN?"]
        pooll = sum(v for k, v in poolc.items() if k.startswith("MOD") or k.startswith("KUBEJS"))
        verdict = "CLEAN" if third == 0 and pooll == 0 else ("100% THIRD-PARTY" if clean == 0 else "MIXED")
        rows.append({"set": sname, "structures": structs, "pieces": dict(tot), "third_pools": pooll, "verdict": verdict, "mod_blocks": sorted({b.split(':')[0] for b in blocks if b.split(':')[0] not in ('minecraft', 'dying_world')}),
                     "mobs": sorted(mobs), "biome_ns": dict(bi), "pool_cls": dict(poolc)})
    # loot items / biome tags in OUR files
    loot_ns = collections.Counter(); 
    for f in (DP / "dying_world/loot_table").rglob("*.json"):
        for m in re.finditer(r'"name":\s*"([a-z0-9_]+):', f.read_text()): loot_ns[m.group(1)] += 1
    tag_ns = collections.Counter()
    for f in (DP / "dying_world/tags/worldgen/biome").rglob("*.json"):
        for v in json.loads(f.read_text())["values"]:
            v = v["id"] if isinstance(v, dict) else v
            if not v.startswith("#"): tag_ns[v.split(":")[0]] += 1
    # lang content keys per namespace (is the mod only structures?)
    content = collections.Counter()
    for n in LANG.namelist():
        m = re.match(r"assets/([^/]+)/lang/en_us\.json", n)
        if m:
            try: d = json.loads(re.sub(r"\r", "", LANG.read(n).decode("utf-8", "replace")))
            except Exception: continue
            content[m.group(1)] = sum(1 for k in d if re.match(r"(item|block|entity|effect|enchantment|potion|fluid)\.", k))
    out = {"sets": rows, "mod_blocks": {k: dict(v) for k, v in modblocks.items()}, "loot_ns": dict(loot_ns), "biome_tag_ns": dict(tag_ns),
           "third_party_pieces": {k: {s: sorted(v) for s, v in d.items()} for k, d in mods.items()}, "content_keys": {k: content[k] for k in list(PROV) if k in content}}
    (ROOT / "docs/provenance_audit.json").write_text(json.dumps(out, indent=1))
    L = ["# Provenance + mod dependency audit (generated by tools/provenance_audit.py; do not edit)\n",
         "Classes: OWN = script-built; VANILLA = Mojang resources; KUBEJS = from kubejs/data (gearwrights, vsrevamped/brutos, custom village HOUSE sets) - **origin to be confirmed by the user, treated as THIRD-PARTY**; MOD = jar-provided (permission needed to redistribute).\n",
         "## 1. Structure sets (what each of OUR sets pulls in)\n", "| set | structures | OWN | VANILLA | KUBEJS | MOD | third-party pools | verdict | mod blocks used | mobs from |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        p = r["pieces"]; L.append(f"| {r['set']} | {r['structures']} | {p.get('OWN',0)+p.get('OWN?',0)} | {p.get('VANILLA',0)} | {p.get('KUBEJS',0)} | {p.get('MOD',0)} | {r['third_pools']} | **{r['verdict']}** | {', '.join(r['mod_blocks']) or '-'} | {', '.join(x for x in r['mobs'] if x != 'minecraft') or '-'} |")
    L += ["\n## 2. Third-party pieces per provider (what would have to be rebuilt or dropped)\n", "| provider | sets using it | distinct pieces |", "|---|---|---|"]
    for prov, d in sorted(mods.items(), key=lambda kv: -sum(len(v) for v in kv[1].values())): L.append(f"| {prov} | {', '.join(sorted(d))} | {sum(len(v) for v in d.values())} |")
    L += ["\n## 3. Mod dependency matrix (namespaces our datapack touches besides vanilla)\n", "'content keys' = items/blocks/entities/effects in the mod's lang file (0 = data-only mod: structures/worldgen). Blocks = block instances placed by our structures (pieces + our own NBT).\n",
          "| namespace | provider | content keys | block instances (sets) | loot entries | biome-tag entries | verdict for dropping |", "|---|---|---|---|---|---|---|"]
    allns = sorted((set(modblocks) | set(loot_ns) | set(tag_ns)) - {"minecraft", "dying_world", "c", "neoforge"})
    tp_by_ns = collections.defaultdict(set)
    for r in rows:
        for ns in r["mod_blocks"]: tp_by_ns[ns].add(r["set"])
    for ns in allns:
        bl = sum(modblocks[ns].values()); sets_ = sorted(modblocks[ns]); why = []
        if bl: why.append(f"swap {bl} blocks in {len(sets_)} sets")
        if loot_ns[ns]: why.append(f"drop/swap {loot_ns[ns]} loot entries")
        if tag_ns[ns]: why.append(f"{tag_ns[ns]} biome ids (optional, lose coverage only)")
        L.append(f"| {ns} | {provider(ns)} | {content.get(ns,0)} | {bl} ({', '.join(sets_[:5])}{'...' if len(sets_)>5 else ''}) | {loot_ns[ns]} | {tag_ns[ns]} | {'; '.join(why) or 'nothing from our datapack'} |")
    L += ["\n## 4. Structure-provider mods (their original sets were disabled in pass 1)\n", "| namespace | provider jar | content keys | referenced by our datapack? |", "|---|---|---|---|"]
    for ns in sorted({s['id'].split(':')[0] for s in INV} - {"minecraft"}):
        pc = [s for k, d in mods.items() if k.endswith(str(PROV[ns])) or k == f"KUBEJS:{ns}" for s in d]
        ref = ("pieces/types in: " + ", ".join(sorted(set(pc)))) if pc else ("blocks/loot/biomes only" if (modblocks[ns] or loot_ns[ns] or tag_ns[ns]) else "no")
        L.append(f"| {ns} | {PROV[ns]} | {content.get(ns, 0)} | {ref} |")
    (ROOT / "docs/provenance_audit.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:30]))

if __name__ == "__main__":
    main()
