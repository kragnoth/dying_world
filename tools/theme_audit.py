#!/usr/bin/env python3
"""theme_audit.py - pass 9-26: score every shipped structure against the modpack's theme rules -> docs/theme_audit.md (+ stdout summary).
Reachability: structure start pool -> pool elements -> jigsaw pools inside each NBT (+ fallbacks + lithostitched add_template_pool_elements from kubejs_base),
dry_land structures -> their layout/template ids. NBTs are read from datapack/, datapack_imported/, the Tarbound jar (if extracted) and the vanilla reference."""
import json, glob, gzip, sys, collections, zipfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import nbtrw
ROOT = Path(__file__).resolve().parent.parent
SRC = [ROOT / "datapack/data", ROOT / "datapack_imported/data", Path("/home/claude/tarbound_jar/data")]
REFZ = zipfile.ZipFile(ROOT / "reference/structures_nbt.zip")
def find(kind, rid):
    ns, p = rid.split(":", 1)
    for r in SRC:
        q = r / ns / kind / f"{p}{'.nbt' if kind == 'structure' else '.json'}"
        if q.exists(): return q.read_bytes() if kind == "structure" else json.loads(q.read_text())
    if kind == "structure":
        n = f"data/{ns}/structure/{p}.nbt"
        if n in REFZ.namelist(): return REFZ.read(n)
    return None
# lithostitched additions
ADD = collections.defaultdict(list)
for f in glob.glob(str(ROOT / "kubejs_base/data/*/lithostitched/worldgen_modifier/*.json")):
    j = json.load(open(f))
    if j.get("type") == "lithostitched:add_template_pool_elements":
        for pool in ([j["template_pools"]] if isinstance(j["template_pools"], str) else j["template_pools"]):
            ADD[pool] += [e["element"].get("location") for e in j["elements"]]
_nbt_cache = {}
def nbt(rid):
    if rid not in _nbt_cache:
        b = find("structure", rid); _nbt_cache[rid] = nbtrw.Struct(b) if b else None
    return _nbt_cache[rid]
def closure(start_pool):
    pools, tpls, todo = set(), set(), [start_pool]
    while todo:
        p = todo.pop()
        if p in pools or p == "minecraft:empty": continue
        pools.add(p); j = find("worldgen/template_pool", p)
        locs = list(ADD.get(p, []))
        if j:
            todo.append(j.get("fallback", "minecraft:empty"))
            for e in j["elements"]:
                el = e["element"]; locs.append(el.get("location"))
                for sub in el.get("elements", []): locs.append(sub.get("location"))
        for l in filter(None, locs):
            if l in tpls: continue
            tpls.add(l); s = nbt(l)
            if s:
                for v in s.b.values():
                    if v[0] == "minecraft:jigsaw" and v[2]:
                        d = v[2][1] if isinstance(v[2], tuple) else v[2]
                        pv = d.get("pool"); pv = pv[1] if isinstance(pv, tuple) else pv
                        if pv: todo.append(pv)
    return pools, tpls
WHITE = ("white_terracotta", "white_concrete", "quartz", "white_wool", "calcite", "polished_diorite", "diorite", "birch_planks", "white_glazed")   # bone blocks = crypt material, not paint
BANNED = ("cherry_", "bamboo", "minecraft:white_concrete", "minecraft:lime_concrete", "minecraft:pink_concrete", "minecraft:light_blue_concrete", "minecraft:magenta_concrete", "minecraft:yellow_concrete", "pink_", "lime_wool", "magenta_wool", "light_blue_wool")
IND = ("industrial_mineshaft", "scavenger_outpost", "concrete_pad", "drowned_radio", "nether_foundry", "proving_grounds")
ABANDON = ("abandoned_", "burnt_", "ruined_", "derelict", "collapsed", "charnel", "shipwreck")
rows = []
for f in sorted(glob.glob(str(ROOT / "datapack/data/dying_world/worldgen/structure/*.json"))):
    sid = Path(f).stem; j = json.load(open(f)); t = j["type"]
    if t == "minecraft:jigsaw": pools, tpls = closure(j["start_pool"])
    elif t == "tarbound:dry_land":
        lay = find("worldgen/structure", j["structure"]); pools, tpls = (closure(lay["start_pool"]) if lay and "start_pool" in lay else (set(), set()))
        if not tpls and lay: tpls = {v for k, v in lay.items() if isinstance(v, str) and ":" in v and nbt(v)}
    else: rows.append((sid, t, None)); continue
    c = collections.Counter(); ents = collections.Counter(); loot = set(); missing = [x for x in tpls if nbt(x) is None]; dv = set(); lit = 0; lanterns_low = 0
    for x in tpls:
        s = nbt(x)
        if not s: continue
        dv.add(s.tree[1].get("DataVersion", (0, 0))[1])
        for e in s.ents: ents[e["nbt"][1]["id"][1]] += 1
        for (px, py, pz), (n, pr, nb) in s.b.items():
            if n in ("minecraft:air", "minecraft:structure_void", "minecraft:jigsaw", "minecraft:cave_air"): continue
            c[n] += 1
            if nb:
                d = nb[1] if isinstance(nb, tuple) else nb; lt = d.get("LootTable"); lt = lt[1] if isinstance(lt, tuple) else lt
                if lt: loot.add(lt)
            if n.endswith("lantern") or n.endswith("_lamp") or "torch" in n or n in ("minecraft:sea_lantern", "minecraft:glowstone", "minecraft:shroomlight"): lit += 1
            if n == "minecraft:lantern" and pr.get("hanging") == "true":
                fl = py - 1
                while fl >= 0 and s.b.get((px, fl, pz), ("",))[0] in ("minecraft:air", "", "minecraft:chain", "minecraft:cobweb"): fl -= 1
                if fl >= 0 and py < fl + 3: lanterns_low += 1
    tot = sum(c.values()) or 1
    ns = collections.Counter()
    for n, k in c.items(): ns[n.split(":")[0]] += k
    white = sum(k for n, k in c.items() if any(w in n for w in WHITE)); rr = ns.get("rustandrebar", 0)
    banned = {n: k for n, k in c.items() if any(b in n for b in BANNED)}
    def loot_ok(l):
        ns, p = l.split(":", 1)
        return ns == "minecraft" or any((r / ns / "loot_table" / f"{p}.json").exists() for r in SRC + [ROOT / "kubejs_base/data"])
    badloot = [l for l in loot if not loot_ok(l)]
    rows.append((sid, t, dict(tpls=len(tpls), missing=missing, blocks=tot, ns=dict(ns), white=white / tot, rr=rr / tot, banned=banned, ents=dict(ents), badloot=badloot,
                              dv=sorted(dv), lights=lit, low_lanterns=lanterns_low, top=c.most_common(6))))
out = ["# Theme audit (pass 9-26)\n", "| structure | pieces | blocks | R&R | white | lights | flags |", "|---|---|---|---|---|---|---|"]
flags_all = {}
for sid, t, m in rows:
    if m is None: out.append(f"| {sid} | ({t}) | | | | | vanilla/mod code structure |"); continue
    fl = []
    if m["missing"]: fl.append(f"MISSING {len(m['missing'])}: {m['missing'][:3]}")
    if m["badloot"]: fl.append(f"loot? {m['badloot']}")
    if m["banned"]: fl.append(f"banned {m['banned']}")
    if m["white"] > .08 and not any(k in sid for k in ("snowy", "end", "lighthouse")): fl.append(f"white {m['white']:.0%}")
    if m["rr"] > .20 and not any(k in sid for k in IND): fl.append(f"R&R {m['rr']:.0%}")
    if m["low_lanterns"]: fl.append(f"low lanterns {m['low_lanterns']}")
    odd = {k: v for k, v in m["ns"].items() if k not in ("minecraft", "rustandrebar", "create", "tarbound")}
    if odd: fl.append(f"namespaces {odd}")
    if any(d > 3955 for d in m["dv"]): fl.append(f"DataVersion {m['dv']}")
    if any(k in sid for k in ABANDON) and m["lights"] > 25: fl.append(f"abandoned but {m['lights']} lights")
    flags_all[sid] = fl
    out.append(f"| {sid} | {m['tpls']} | {m['blocks']} | {m['rr']:.0%} | {m['white']:.0%} | {m['lights']} | {'; '.join(fl) or 'ok'} |")
(ROOT / "docs/theme_audit.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
