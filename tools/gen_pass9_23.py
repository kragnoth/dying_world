#!/usr/bin/env python3
"""
gen_pass9_23.py - pass 9-23: RARE DERELICT VARIANTS - placement for the derelict research stations (built by gen_pass9_15 main: ruined finish, unlit street
post stubs, undead spawns) + a COOLED DERELICT FOUNDRY. Run after 9_15, 9_18; before 9_16. Safe to re-run.
- research_gate_{end,nether}_derelict -> settlements set (weight 4 each vs 20 live, via 9_16); research_nether_derelict -> research_nether_stations (1:4);
  research_end_derelict -> research_end_stations (1:4). The derelict End station keeps its guaranteed elytra + return frames.
- dying_world:nether_foundry_derelict: copies of the foundry pieces, furnaces out (lit=false), lava cauldrons -> empty cauldrons, half the soul lanterns gone,
  more cracked nether bricks, cobwebs on the decks; spawns: wither skeleton 12, skeleton 4, blaze 3, magma cube 2. In nether_foundries at 1:4.
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from gen_pass4_2a import M, w, OUT

def foundry():
    src, dst = OUT / "structure/foundry", OUT / "structure/foundry_derelict"; dst.mkdir(parents=True, exist_ok=True)
    for old in dst.glob("*.nbt"): old.unlink()
    for f in src.glob("*.nbt"):
        s = nbtrw.Struct(f.read_bytes()); r = random.Random(zlib.crc32(f.name.encode()))
        for p, (n, props, nbt) in list(s.b.items()):
            if n == M("jigsaw") and nbt:
                d = dict(nbt[1])
                if d["pool"][1].startswith("dying_world:foundry/"): d["pool"] = (8, d["pool"][1].replace("dying_world:foundry/", "dying_world:foundry_derelict/"))
                s.b[p] = (n, props, (10, d))
            elif n == M("blast_furnace"): s.b[p] = (n, dict(props, lit="false"), nbt)
            elif n == M("lava_cauldron"): s.b[p] = (M("cauldron"), {}, None)
            elif n == M("soul_lantern") and r.random() < .5: s.b[p] = (M("air"), {}, None)
            elif n == M("nether_bricks") and r.random() < .25: s.b[p] = (M("cracked_nether_bricks"), {}, None)
            elif n == M("air") and r.random() < .02 and s.b.get((p[0], p[1] - 1, p[2]), ("",))[0].endswith("bricks"): s.b[p] = (M("cobweb"), {}, None)
        (dst / f.name).write_bytes(s.bytes())
    for pool in ("start", "wings", "caps"):
        j = json.loads((OUT / f"worldgen/template_pool/foundry/{pool}.json").read_text())
        j["fallback"] = j["fallback"].replace("dying_world:foundry/", "dying_world:foundry_derelict/")
        for e in j["elements"]: e["element"]["location"] = e["element"]["location"].replace("dying_world:foundry/", "dying_world:foundry_derelict/")
        w(OUT / f"worldgen/template_pool/foundry_derelict/{pool}.json", j)
    j = json.loads((OUT / "worldgen/structure/nether_foundry.json").read_text())
    j["start_pool"] = "dying_world:foundry_derelict/start"; j["biomes"] = "#dying_world:has_structure/nether_foundry"
    j["spawn_overrides"] = {"monster": {"bounding_box": "piece", "spawns": [
        {"type": "minecraft:wither_skeleton", "weight": 12, "minCount": 2, "maxCount": 4}, {"type": "minecraft:skeleton", "weight": 4, "minCount": 2, "maxCount": 4},
        {"type": "minecraft:blaze", "weight": 3, "minCount": 1, "maxCount": 2}, {"type": "minecraft:magma_cube", "weight": 2, "minCount": 2, "maxCount": 3}]}}
    w(OUT / "worldgen/structure/nether_foundry_derelict.json", j)

def sets():
    for name, live, der in (("nether_foundries", "nether_foundry", "nether_foundry_derelict"), ("research_nether_stations", "research_nether", "research_nether_derelict"),
                            ("research_end_stations", "research_end", "research_end_derelict")):
        p = OUT / f"worldgen/structure_set/{name}.json"; j = json.loads(p.read_text())
        j["structures"] = [{"structure": f"dying_world:{live}", "weight": 4}, {"structure": f"dying_world:{der}", "weight": 1}]; w(p, j)

def main():
    for s in ("gate_end", "gate_nether", "nether", "end"): assert (OUT / f"worldgen/structure/research_{s}_derelict.json").exists(), s
    foundry(); sets(); print("9-23: derelict foundry + derelict stations placed (1 in 5 / settlements w4)")

if __name__ == "__main__":
    main()
