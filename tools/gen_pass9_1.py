#!/usr/bin/env python3
"""
gen_pass9_1.py - pass 9-1: OUR PLAINS-FAMILY houses (most common village family: plains, forest, birch, flower forest, cherry ... see village_biomes.py).
Replaces the house pool of dying_world:village_plains entirely (custom kubejs set of unclear origin + kaisyn donors no longer used).
Run AFTER gen_pass3c4.py and gen_pass7_1.py; then 8_9 (lanterns) and build. Safe to re-run.

Temperate 1800s sub-styles (tools/savanna_kit.py RAMPS): farmhouse (clapboard spruce->oak->birch->whitewash, dark-oak shingles), timber (Tudor:
stone base -> mud brick -> white plaster with dark-oak frame, spruce roof), fieldstone (cobble -> stone -> stone brick -> polished andesite, oak roof).
Builders are the 7-1 ones re-skinned (oak wood, style map creole->farmhouse, limestone->fieldstone, hacienda->timber) + a new BARN (shepherd).
Each building: base / lived (villager jigsaw -> minecraft:village/plains/villagers, plains house loot) / ruined. Pool = lived 40 / ruined 60.
Also writes dying_world:plains/ruined_houses (for a later abandoned-plains rebuild; not hooked yet).
"""
import shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_pass7_1 as S
from savanna_kit import *
from buildkit import M, stairs, slab, door, bed, table, chair, hang_lantern, H4
from gen_pass4_2a import w, OUT

S.WOOD, S.STYLE_MAP, S.PREFIX, S.FAMILY = "oak", {"creole": "farmhouse", "limestone": "fieldstone", "hacienda": "timber"}, "plains_", "plains"

def barn(seed=1):
    b = S.mkB("barn", "creole", 13, 13, 17, seed); t = b.t; b.ground(("grass_block", "coarse_dirt", "dirt_path"))
    b.walls(1, 11, 1, 14, 0, 5, base_h=1)
    for x in (1, 11):                                             # frame posts every 3 blocks on the long walls
        for z in (4, 7, 10):
            for y in range(1, 6): b.role(x, y, z, "trim", {"axis": "y"})
    b.gable(1, 11, 1, 14, 6, "z", ceiling=False)
    for x in range(2, 11):                                        # hay loft over the north third
        for z in range(2, 6): slab(t, x, 4, z, "spruce", "top")
    for x in (4, 5, 6, 7, 8):
        for y in (1, 2, 3): t.set(x, y, 14, M("air"))             # wide doorway (south)
    t.set(5, 1, 14, M("spruce_fence_gate"), {"facing": "south", "in_wall": "false", "open": "true", "powered": "false"})
    t.set(7, 1, 14, M("spruce_fence_gate"), {"facing": "south", "in_wall": "false", "open": "true", "powered": "false"})
    for z in (8, 10, 12):                                         # stalls (fence dividers) on both sides
        for x in (2, 3, 9, 10): t.set(x, 1, z, M("spruce_fence"))
    for (x, z) in ((2, 9), (10, 9), (2, 11), (10, 11), (3, 13)): t.set(x, 1, z, M("hay_block"), {"axis": "y"})
    for x in range(2, 11):
        for z in (2, 3):
            if (x + z) % 3: t.set(x, 5, z, M("hay_block"), {"axis": "x"})
    for y in range(1, 5): t.set(10, y, 6, M("ladder"), {"facing": "west", "waterlogged": "false"})
    b.job(2, 1, 6, "loom", {"facing": "east"}); b.chest(2, 1, 5, "east", "minecraft:chests/village/village_shepherd"); t.set(10, 1, 5, M("barrel"), {"facing": "up", "open": "false"})
    t.set(6, 1, 9, M("water_cauldron"), {"level": "3"}); t.set(4, 1, 6, M("composter"), {"level": "2"})
    for z in (5, 9, 12): hang_lantern(t, 6, 5, z)
    for z in (6, 11): b.window(1, 3, z, "west"); b.window(11, 3, z, "east")
    b.entrance(6, 16, True)
    return b

ROSTER = [  # plains slots (weights ~ vanilla plains: many small houses)
    # 9-2: small cottages up, big buildings (planter 15x13, courtyard 13x13, chapel 17x21, barn 13x17) down - vanilla streets have few/small plots
    (S.creole_cottage, 6), (S.dogtrot, 4), (S.limestone_cottage, 6), (S.casita, 3), (S.planter_house, 1), (S.courtyard_house, 1),
    (S.smokehouse, 2), (S.forge, 2), (S.schoolhouse, 2), (S.chapel, 1), (S.kitchen_garden, 3), (S.orchard, 2), (barn, 1)]

def main():
    N = OUT / "structure/plains"; N.mkdir(parents=True, exist_ok=True)
    els, ruined = [], []
    for fn, wt in ROSTER:
        for v in ("base", "lived", "ruined"):
            b = fn(1); t = b.finalize(v); (N / f"{b.name}_{v}.nbt").write_bytes(t.bytes())
            if v != "base":
                els.append({"weight": wt * (4 if v == "lived" else 6), "element": {"element_type": "minecraft:single_pool_element",
                            "location": f"dying_world:plains/{b.name}_{v}", "processors": "minecraft:empty", "projection": "rigid"}})
        ruined.append({"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:plains/{b.name}_ruined",
                       "processors": "minecraft:empty", "projection": "rigid"}})
    w(OUT.parent / "minecraft/worldgen/template_pool/village/plains/houses.json", {"fallback": "minecraft:village/plains/terminators", "elements": els})
    w(OUT / "worldgen/template_pool/plains/ruined_houses.json", {"fallback": "minecraft:empty", "elements": ruined})
    old = OUT / "structure/village/plains"
    if old.exists(): shutil.rmtree(old)                           # our worn/mix copies of the replaced plains set
    print(f"9-1: {len(ROSTER)} plains buildings x 3 variants; plains house pool = {len(els)} entries (lived 40 / ruined 60)")

if __name__ == "__main__":
    main()
