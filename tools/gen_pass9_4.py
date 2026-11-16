#!/usr/bin/env python3
"""
gen_pass9_4.py - pass 9-4: OUR TAIGA FAMILY (houses + streets), plains recipe. Run AFTER 3c4, 7_1, 9_1, 9_3, 8_11 (it overrides the taiga pools); then 8_9, build.
Houses: 7-1/9-1 builders re-skinned in spruce with STEEP 2:1 roofs (savanna_kit B.STEEP) and taiga sub-styles: logcabin (dark-oak -> spruce -> stripped spruce,
dark-oak roof), stonetimber (cobble/stone-brick lower -> spruce plank/stripped spruce upper, dark-oak frame, spruce roof), heavystone (cobble -> stone brick -> andesite,
dark-oak roof) + NEW longhouse (Nordic hall, central hearth, long tables, beds along the walls) and sawmill (open shed, stonecutter = mason job, log stacks, saw bench).
Streets: gen_pass9_3 generator with a taiga palette (podzol/coarse dirt verges + ferns/sweet berries, rooted dirt/gravel edges, dirt path, centre cobble/mossy cobble/spruce planks,
spruce fence lamp posts, spruce leaf hedges, stacked logs/barrels).
Pools: minecraft:village/taiga/houses (lived 40 / ruined 60) + minecraft:village/taiga/streets = ours only; dying_world:taiga/ruined_houses for later abandoned use.
"""
import shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_pass7_1 as S, gen_pass9_1 as P, gen_pass9_3 as ST
from savanna_kit import *
from buildkit import M, stairs, slab, door, bed, table, chair, hang_lantern
from gen_pass4_2a import w, OUT

S.WOOD, S.STYLE_MAP, S.PREFIX, S.FAMILY = "spruce", {"creole": "logcabin", "limestone": "heavystone", "hacienda": "stonetimber"}, "taiga_", "taiga"
B.STEEP = True
B.GROUND = ("podzol", "coarse_dirt", "dirt_path", "grass_block")

def longhouse(seed=1):
    b = S.mkB("longhouse", "creole", 11, 9, 20, seed); t = b.t; b.ground(("podzol", "coarse_dirt", "dirt_path"))
    b.walls(1, 9, 1, 17, 0, 3, base_h=1)
    for z in (5, 9, 13):                                          # roof-post frame
        for x in (1, 9):
            for y in range(1, 4): b.role(x, y, z, "trim", {"axis": "y"})
    b.gable(1, 9, 1, 17, 4, "z", ceiling=False)
    for z in range(6, 13): t.set(5, 0, z, M("cobblestone"))      # hearth strip
    t.set(5, 1, 9, M("campfire"), {"facing": "north", "lit": "false", "signal_fire": "false", "waterlogged": "false"})
    for z in (6, 7, 11, 12):                                      # long tables + benches
        table(t, 3, 1, z, "spruce"); table(t, 7, 1, z, "spruce")
        stairs(t, 2, 1, z, "spruce", "west"); stairs(t, 8, 1, z, "spruce", "east")
    bed(t, 3, 1, 2, "brown", "north"); bed(t, 7, 1, 2, "brown", "north"); bed(t, 3, 1, 16, "gray", "south"); bed(t, 7, 1, 16, "gray", "south")
    b.chest(5, 1, 2, "south"); t.set(8, 1, 15, M("barrel"), {"facing": "up", "open": "false"}); t.set(2, 1, 9, M("smoker"), {"facing": "east", "lit": "false"})
    for z in (4, 9, 14): hang_lantern(t, 5, 3, z)
    door(t, 5, 1, 17, "spruce", "south"); b.window(1, 2, 7, "west"); b.window(9, 2, 11, "east"); b.window(1, 2, 13, "west")
    b.entrance(5, 19, True)
    return b

def sawmill(seed=1):
    b = S.mkB("sawmill", "hacienda", 13, 9, 11, seed); t = b.t; b.ground(("podzol", "coarse_dirt", "dirt_path"))
    for x in range(1, 12):
        for z in range(1, 9): b.role(x, 0, z, "floor" if 2 <= x <= 10 and 2 <= z <= 7 else "base")
    for (x, z) in ((1, 1), (6, 1), (11, 1), (1, 8), (6, 8), (11, 8)):
        for y in range(1, 4): b.role(x, y, z, "trim", {"axis": "y"})
    for x in range(1, 12):
        for y in (1, 2): b.role(x, y, 1, "wall", band=(1, 3))
    b.gable(1, 11, 1, 8, 4, "x", ceiling=False)
    b.job(6, 1, 4, "stonecutter", {"facing": "south"})            # saw bench (mason job)
    for x in (4, 5, 7, 8): t.set(x, 1, 4, M("stripped_spruce_log"), {"axis": "x"})
    for (x, z) in ((2, 6), (2, 7), (3, 7), (10, 6), (10, 7), (9, 7)):  # log stacks
        t.set(x, 1, z, M("spruce_log"), {"axis": "z"})
        if (x + z) % 2: t.set(x, 2, z, M("spruce_log"), {"axis": "z"})
    b.chest(10, 1, 2, "south", "minecraft:chests/village/village_mason"); t.set(2, 1, 2, M("barrel"), {"facing": "up", "open": "false"})
    t.set(9, 1, 2, M("grindstone"), {"face": "floor", "facing": "south"}); hang_lantern(t, 6, 3, 6)
    b.entrance(6, 10, True)
    return b

ROSTER = [(S.creole_cottage, 6), (S.dogtrot, 3), (S.limestone_cottage, 6), (S.casita, 3), (S.planter_house, 1), (longhouse, 2), (sawmill, 2),
          (S.smokehouse, 2), (S.forge, 2), (S.schoolhouse, 2), (S.chapel, 1), (S.kitchen_garden, 2), (S.orchard, 1), (P.barn, 1)]

ST.FAMILY = "taiga"
ST.PAL = {"verge": ["podzol", "coarse_dirt"], "edge": ["rooted_dirt", "gravel", "coarse_dirt"], "inner": ["dirt_path", "cobblestone"],
          "centre": ["cobblestone", "mossy_cobblestone", "spruce_planks", "dirt_path"], "fence": "spruce_fence", "hedge": "spruce_leaves",
          "flowers": ["fern", "sweet_berry_bush", "fern", "large_fern"], "props": [("spruce_log", {"axis": "x"}), ("barrel", {"facing": "up", "open": "false"})]}

def main():
    N = OUT / "structure/taiga"; N.mkdir(parents=True, exist_ok=True)
    els, ruined = [], []
    for fn, wt in ROSTER:
        for v in ("base", "lived", "ruined"):
            b = fn(1); t = b.finalize(v); (N / f"{b.name}_{v}.nbt").write_bytes(t.bytes())
            if v != "base":
                els.append({"weight": wt * (4 if v == "lived" else 6), "element": {"element_type": "minecraft:single_pool_element",
                            "location": f"dying_world:taiga/{b.name}_{v}", "processors": "minecraft:empty", "projection": "rigid"}})
        ruined.append({"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:taiga/{b.name}_ruined",
                       "processors": "minecraft:empty", "projection": "rigid"}})
    w(OUT.parent / "minecraft/worldgen/template_pool/village/taiga/houses.json", {"fallback": "minecraft:village/taiga/terminators", "elements": els})
    w(OUT / "worldgen/template_pool/taiga/ruined_houses.json", {"fallback": "minecraft:empty", "elements": ruined})
    old = OUT / "structure/village/taiga"
    if old.exists(): shutil.rmtree(old)
    n = ST.write_streets()
    print(f"9-4: {len(ROSTER)} taiga buildings x 3 variants (steep roofs); house pool {len(els)} entries; {n} taiga street pieces")

if __name__ == "__main__":
    main()
