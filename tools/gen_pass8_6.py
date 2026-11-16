#!/usr/bin/env python3
"""
gen_pass8_6.py - pass 8-6: OUR wells (replace the 11 forsaken wells). Safe to re-run; run AFTER gen_pass3b2.py / gen_pass3c5.py
(it rewrites dying_world:wells set members but keeps its placement + exclusion zone).
5 worn wells, each a real 3x3 water shaft (template starts 6 blocks underground: start_height -6, water y1..3 sealed by the shaft walls):
  wells/temperate  cobble rim + oak posts + oak gable canopy, crank (fence + chain + lantern)      biomes = concrete_pad_temperate group
  wells/cold       stone-brick rim + spruce posts + spruce canopy, snow-proof slab cap               concrete_pad_cold
  wells/arid       sandstone rim + cut-sandstone pillars + smooth sandstone slab canopy, no roof wood  concrete_pad_arid
  wells/wild       mud-brick rim + mangrove posts + mangrove canopy, vines                             concrete_pad_wild
  wells/washhouse  temperate: open oak shed over the well with 2 water troughs (cauldrons), bench, barrel (loot)
Wear: mossy/cracked rims, moss carpet; nothing missing. Old forsaken-based structure jsons + biome tags under wells/* are deleted.
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from buildkit import *

DEPTH = 6
STYLES = {  # rim, post, roof mat (stairs/slab family), canopy kind
    "temperate": (M("cobblestone"), M("oak_log"), "oak", "gable"),
    "cold": (M("stone_bricks"), M("spruce_log"), "spruce", "gable"),
    "arid": (M("smooth_sandstone"), M("cut_sandstone"), "smooth_sandstone", "flat"),
    "wild": (M("mud_bricks"), M("mangrove_log"), "mangrove", "gable"),
}

def well(style, seed, washhouse=False):
    r = rng("well_" + style, seed); rim, post, roof, canopy = STYLES["temperate" if washhouse else style]
    W = 11 if washhouse else 7; D = 9 if washhouse else 7; t = Tpl(W, DEPTH + 8, D); G = DEPTH
    cx, cz = 3, 3
    for x in range(W):
        for z in range(D):
            t.set(x, G, z, r.choice([M("dirt_path"), M("coarse_dirt"), M("gravel")]) if not washhouse else worn(r, M("cobblestone"), 1.2))
            for y in range(G + 1, G + 4): t.set(x, y, z, M("air"))
    for y in range(0, G + 1):                                       # shaft 5x5 walls, 3x3 water/air inside
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                edge = abs(x - cx) == 2 or abs(z - cz) == 2
                if edge or y == 0: t.set(x, y, z, worn(r, rim if y >= G - 1 else M("cobblestone") if style != "arid" or washhouse else M("sandstone"), 1.6))
                elif y <= 3: t.set(x, y, z, M("water"), {"level": "0"})
                else: t.set(x, y, z, M("air"))
    for x in range(cx - 2, cx + 3):                                 # rim wall y G+1
        for z in range(cz - 2, cz + 3):
            if abs(x - cx) == 2 or abs(z - cz) == 2:
                corner = abs(x - cx) == 2 and abs(z - cz) == 2
                t.set(x, G + 1, z, post if corner else worn(r, rim, 1.2), {"axis": "y"} if corner and post.endswith("_log") else None)
    for (x, z) in ((cx - 2, cz - 2), (cx + 2, cz - 2), (cx - 2, cz + 2), (cx + 2, cz + 2)):
        for y in (G + 2, G + 3): t.set(x, y, z, post, {"axis": "y"} if post.endswith("_log") else None)
    if canopy == "gable": gable(t, r, cx - 2, cx + 2, cz - 2, cz + 2, G + 4, roof, fill=roof + "_planks" if roof != "mangrove" else "mangrove_planks")
    else:
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3): slab(t, x, G + 4, z, roof)
        t.set(cx, G + 4, cz, M("cut_sandstone"))
    if canopy == "gable":                                          # crank beam + chain + lantern over the water
        for x in range(cx - 2, cx + 3): t.set(x, G + 4, cz, M(roof.replace("smooth_sandstone", "oak") + "_fence") if abs(x - cx) < 2 else post, {"axis": "x"} if abs(x - cx) == 2 and post.endswith("_log") else None)
        t.set(cx, G + 3, cz, M("chain"), {"axis": "y", "waterlogged": "false"}); lantern(t, cx, G + 2, cz)
    else:
        t.set(cx, G + 3, cz, M("chain"), {"axis": "y", "waterlogged": "false"}); lantern(t, cx, G + 2, cz)
    if style == "wild":
        for (x, z) in ((cx - 2, cz - 3), (cx + 2, cz + 3)):
            if 0 <= z < D: t.set(x, G + 2, z, M("vine"), {"south": "true" if z < cz else "false", "north": "true" if z > cz else "false", "east": "false", "west": "false", "up": "false"})
    if washhouse:                                                  # open shed x0..10: troughs + bench + barrel
        for (x, z) in ((7, 1), (10, 1), (7, 7), (10, 7)):
            for y in range(G + 1, G + 4): t.set(x, y, z, M("oak_log"), {"axis": "y"})
        for x in range(6, 11):
            for z in range(1, 8): slab(t, x, G + 4, z, "oak")
        t.set(8, G + 1, 2, M("water_cauldron"), {"level": "3"}); t.set(9, G + 1, 2, M("water_cauldron"), {"level": "2"})
        stairs(t, 8, G + 1, 6, "oak", "south"); stairs(t, 9, G + 1, 6, "oak", "south")
        t.set(10, G + 1, 4, M("barrel"), {"facing": "up", "open": "false"}, {"id": M("barrel"), "LootTable": "dying_world:chests/scavenger_scraps"})
        hang_lantern(t, 8, G + 3, 4)
    for _ in range(2):
        if r.random() < .6: t.set(r.choice([cx - 3, cx + 3]) % W, G + 1, r.randint(0, D - 1), M("moss_carpet"))
    fix_connections(t)
    return t

def main():
    D_ = OUT / "worldgen/structure/wells"; T_ = OUT / "tags/worldgen/biome/has_structure/wells"
    for p in (D_, T_):
        if p.exists(): shutil.rmtree(p)
    N = OUT / "structure/wells"; N.mkdir(parents=True, exist_ok=True)
    groups = {"temperate": "concrete_pad_temperate", "cold": "concrete_pad_cold", "arid": "concrete_pad_arid", "wild": "concrete_pad_wild"}
    members = []
    for style, grp in list(groups.items()) + [("washhouse", "concrete_pad_temperate")]:
        (N / f"{style}.nbt").write_bytes(well(style, 1, washhouse=(style == "washhouse")).bytes())
        register(f"wells/{style}", f"wells/{style}", [(f"dying_world:wells/{style}", 1)], [f"#dying_world:has_structure/{grp}"])
        j = json.loads((OUT / f"worldgen/structure/wells/{style}.json").read_text()); j["start_height"] = {"absolute": -DEPTH}
        w(OUT / f"worldgen/structure/wells/{style}.json", j)
        members.append({"structure": f"dying_world:wells/{style}", "weight": 1 if style == "washhouse" else 2})
    p = OUT / "worldgen/structure_set/wells.json"; s = json.loads(p.read_text()); s["structures"] = members; w(p, s)
    print(f"8-6: {len(members)} wells (temperate/cold/arid/wild/washhouse), set dying_world:wells members replaced (placement kept)")

if __name__ == "__main__":
    main()
