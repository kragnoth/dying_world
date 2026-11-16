#!/usr/bin/env python3
"""
gen_pass7_1.py - pass 7-1: NEW SAVANNA HOUSES (replace the user's coloured-panel/stilt/teepee savanna set) + hook into dying_world:village_savanna.
Run AFTER gen_pass3c4.py (overwrites minecraft:village/savanna/houses and deletes our old savanna worn copies). Safe to re-run.

Style: 1800s hot-dry US/European blend, 3 sub-styles (docs/style_board_savanna.md): hacienda (stucco/clay tile), creole (birch siding, raised porch,
dark-oak shingles), limestone (sandstone ramp, andesite quoins, spruce roof). Acacia = village identity wood (beams, posts, trim).
Gradient palette engine + ruin logic: tools/savanna_kit.py. Every building exists as base (no villagers, reference), lived (villager spawn
jigsaw, job block reachable) and ruined (same ramp shifted darker from the ground, moss/cracks, furniture swapped, cobwebs; nothing missing).
Front = south; front row z=D-1 is outside (path) with the minecraft:building_entrance jigsaw at the door (vanilla street hookup).
Pool weights: lived 40 / ruined 60 per building weight. Files: structure/savanna/<building>_{base,lived,ruined}.nbt.
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from savanna_kit import *
from buildkit import M, R, stairs, slab, door, bed, table, chair, lantern, hang_lantern, pot, H4
from gen_pass4_2a import w, OUT

LOOT = "minecraft:chests/village/village_savanna_house"
# 9-1: the builders are reused for other families: wood, sub-style mapping, name prefix and village family are module globals
WOOD, STYLE_MAP, PREFIX, FAMILY = "acacia", {}, "", "savanna"
def mkB(name, style, W, H, D, seed=1):
    b = B(PREFIX + name, STYLE_MAP.get(style, style), W, H, D, seed); b.family = FAMILY; return b

def porch_posts(b, xs, z, y0, y1, wood=None):
    wood = wood or WOOD                                           # family wood (was a def-time default = acacia everywhere)
    for x in xs:
        for y in range(y0, y1 + 1): b.set(x, y, z, M(f"{wood}_fence"))

# ---------------- small houses ----------------
def creole_cottage(seed=1):
    b = mkB("creole_cottage", "creole", 9, 10, 10, seed); t = b.t; b.ground()
    b.walls(1, 7, 1, 6, 0, 3)                                   # body 7x6, porch z7..8, path row z9
    b.gable(1, 7, 1, 6, 4, "x")
    for x in range(1, 8):
        for z in (7, 8): b.role(x, 0, z, "floor")
    porch_posts(b, (1, 4, 7), 8, 1, 3); [b.role(x, 4, z, "roof_slab", {"type": "bottom"}) for x in range(0, 9) for z in (7, 8)]
    door(t, 4, 1, 6, WOOD, "south"); b.window(2, 2, 6, "south"); b.window(6, 2, 6, "south"); b.window(1, 2, 3, "west"); b.window(7, 2, 3, "east")
    bed(t, 2, 1, 2, "red", "north"); b.chest(3, 1, 2, "south"); table(t, 6, 1, 3, WOOD); chair(t, 6, 1, 4, WOOD, "south"); chair(t, 5, 1, 3, WOOD, "west")
    t.set(6, 1, 2, M("furnace"), {"facing": "south", "lit": "false"}); hang_lantern(t, 4, 3, 3); pot(t, 2, 1, 5, "cactus") if False else t.set(2, 1, 5, M("potted_cactus"))
    stairs(t, 5, 1, 7, WOOD, "north"); stairs(t, 6, 1, 7, WOOD, "north"); t.set(2, 1, 7, M("barrel"), {"facing": "up", "open": "false"})
    b.entrance(4, 9, True)
    return b

def dogtrot(seed=1):
    b = mkB("dogtrot", "creole", 11, 10, 10, seed); t = b.t; b.ground()
    b.walls(1, 4, 1, 7, 0, 3); b.walls(6, 9, 1, 7, 0, 3)           # two pens, breezeway x5
    for z in range(1, 8): b.role(5, 0, z, "floor")
    b.gable(1, 9, 1, 7, 4, "z")
    door(t, 4, 1, 4, WOOD, "east"); door(t, 6, 1, 4, WOOD, "west")
    for x in (2, 3): b.window(x, 2, 7, "south")
    b.window(8, 2, 7, "south"); b.window(1, 2, 4, "west"); b.window(9, 2, 4, "east")
    bed(t, 2, 1, 2, "white", "north"); bed(t, 3, 1, 2, "white", "north"); b.chest(2, 1, 6, "east"); hang_lantern(t, 3, 3, 4)
    b.job(8, 1, 2, "smoker", {"facing": "south", "lit": "false"}); t.set(7, 1, 2, M("barrel"), {"facing": "up", "open": "false"})
    table(t, 8, 1, 5, WOOD); chair(t, 7, 1, 5, WOOD, "west"); t.set(8, 1, 6, M("water_cauldron"), {"level": "2"}); hang_lantern(t, 7, 3, 4)
    stairs(t, 5, 1, 2, WOOD, "north"); t.set(5, 1, 6, M("potted_" + WOOD + "_sapling"))
    for z in (8,): [b.role(x, 0, z, "floor") for x in range(1, 10)]
    b.entrance(5, 9, True)
    return b

def limestone_cottage(seed=1):
    b = mkB("limestone_cottage", "limestone", 10, 11, 10, seed); t = b.t; b.ground()
    b.walls(1, 7, 1, 7, 0, 4, base_h=2)
    b.gable(1, 7, 1, 7, 5, "x")
    for y in range(0, 9): b.role(8, y, 3, "base" if y < 3 else "wall", band=(0, 8))     # chimney (east)
    t.set(7, 1, 3, M("campfire"), {"facing": "west", "lit": "false", "signal_fire": "false", "waterlogged": "false"}); b.role(7, 2, 3, "inner")
    door(t, 4, 1, 7, "spruce", "south"); b.window(2, 2, 7, "south", tall=True); b.window(6, 2, 7, "south", tall=True); b.window(1, 2, 4, "west", tall=True)
    bed(t, 2, 1, 2, "light_gray", "north"); b.chest(3, 1, 2, "south"); t.set(6, 1, 2, M("bookshelf")); t.set(6, 2, 2, M("bookshelf")); t.set(5, 1, 2, M("bookshelf"))
    table(t, 5, 1, 5, "spruce"); chair(t, 5, 1, 4, "spruce", "north"); chair(t, 6, 1, 5, "spruce", "east"); hang_lantern(t, 4, 4, 4)
    stairs(t, 2, 1, 5, "spruce", "west"); stairs(t, 2, 1, 6, "spruce", "west")        # bench
    t.set(1, 1, 8, M("barrel"), {"facing": "up", "open": "false"}); t.set(7, 1, 8, M("potted_dead_bush"))
    b.entrance(4, 9, True)
    return b

# ---------------- medium ----------------
def casita(seed=1):
    b = mkB("casita", "hacienda", 12, 11, 12, seed); t = b.t; b.ground()
    b.walls(1, 10, 1, 7, 0, 4, base_h=1)
    for y in range(1, 5): b.role(5, y, 2, "inner"); b.role(5, y, 3, "inner"); b.role(5, y, 5, "inner"); b.role(5, y, 6, "inner")    # partition with doorway z4
    b.gable(1, 10, 1, 7, 5, "x")
    for x in range(1, 11):                                        # veranda z8..9 (tile floor, acacia posts, shed roof of tile slabs)
        for z in (8, 9): b.role(x, 0, z, "floor")
    porch_posts(b, (1, 4, 7, 10), 9, 1, 3)
    for x in range(0, 12):
        b.role(x, 4, 8, "roof", {"facing": "north", "half": "top", "shape": "straight"}); b.role(x, 4, 9, "roof", {"facing": "north", "half": "bottom", "shape": "straight"})
    for x in (2, 3, 5, 6, 8, 9): stairs(t, x, 3, 9, WOOD, "east" if x in (2, 5, 8) else "west", "top")    # arch corbels
    door(t, 7, 1, 7, WOOD, "south"); b.window(3, 2, 7, "south"); b.window(9, 2, 7, "south"); b.window(1, 2, 4, "west"); b.window(10, 2, 4, "east")
    for x in (2, 4): bed(t, x, 1, 2, "orange", "north")
    b.chest(3, 1, 2, "south"); stairs(t, 2, 1, 6, WOOD, "west", "top"); t.set(2, 2, 6, M("potted_cactus")); t.set(3, 1, 6, M("barrel"), {"facing": "up", "open": "false"})
    table(t, 8, 1, 4, WOOD); table(t, 8, 1, 5, WOOD); chair(t, 7, 1, 4, WOOD, "west"); chair(t, 9, 1, 5, WOOD, "east")
    t.set(9, 1, 2, M("smoker"), {"facing": "south", "lit": "false"}); t.set(8, 1, 2, M("water_cauldron"), {"level": "3"}); t.set(7, 1, 2, M("barrel"), {"facing": "up", "open": "false"})
    hang_lantern(t, 3, 4, 4); hang_lantern(t, 8, 4, 4); t.set(5, 1, 4, M("air")); t.set(5, 2, 4, M("air"))
    stairs(t, 4, 1, 9, WOOD, "north") if False else None
    for x in (2, 9): t.set(x, 1, 9, M("potted_dead_bush") if x == 9 else M("decorated_pot"), {"facing": "south", "cracked": "false", "waterlogged": "false"} if x == 2 else None)
    b.entrance(7, 11, True)
    return b

def courtyard_house(seed=1):
    b = mkB("courtyard_house", "hacienda", 13, 9, 13, seed); t = b.t; b.ground()
    b.walls(1, 11, 1, 11, 0, 3, base_h=1)                      # outer shell
    for x in range(4, 9):                                        # open courtyard x4..8 z4..11 (inner walls)
        for y in range(1, 4): b.role(x, y, 3, "inner")
    for z in range(3, 11):
        for y in range(1, 4): b.role(3, y, z, "inner"); b.role(9, y, z, "inner")
    b.clear(4, 8, 1, 6, 4, 10)
    for x in range(4, 9):
        for z in range(4, 11): b.role(x, 0, z, "floor")
    for x in range(1, 12):                                       # roofs: inward-sloping tile over the 3 wings
        for z in range(1, 12):
            if 4 <= x <= 8 and 4 <= z <= 11: continue
            b.role(x, 4, z, "roof_slab", {"type": "bottom"})
    for x in range(0, 13): b.role(x, 4, 0, "roof", {"facing": "south", "half": "bottom", "shape": "straight"})
    for z in range(0, 13): b.role(0, 4, z, "roof", {"facing": "east", "half": "bottom", "shape": "straight"}); b.role(12, 4, z, "roof", {"facing": "west", "half": "bottom", "shape": "straight"})
    for x in range(4, 9):                                        # front gate wall z11 with gate
        for y in (1, 2): b.role(x, y, 11, "wall", band=(1, 3))
    t.set(6, 1, 11, M(WOOD + "_fence_gate"), {"facing": "south", "in_wall": "false", "open": "false", "powered": "false"}); t.set(6, 2, 11, M("air"))
    for x, z in ((6, 3), (3, 7), (9, 7)): t.set(x, 1, z, M("air")); t.set(x, 2, z, M("air"))      # doorways into the wings
    t.set(6, 1, 7, M("water_cauldron"), {"level": "3"}); [t.set(x, 1, z, M("potted_red_tulip" if (x + z) % 2 else "potted_cactus")) for x, z in ((4, 4), (8, 4), (4, 10), (8, 10))]
    bed(t, 2, 1, 2, "red", "north"); bed(t, 4, 1, 2, "red", "north"); b.chest(10, 1, 2, "south"); hang_lantern(t, 6, 3, 2)
    b.job(2, 1, 9, "loom", {"facing": "east"}); t.set(2, 1, 8, M("barrel"), {"facing": "up", "open": "false"}); hang_lantern(t, 2, 3, 6)
    t.set(10, 1, 9, M("smoker"), {"facing": "west", "lit": "false"}); table(t, 10, 1, 6, WOOD); chair(t, 10, 1, 5, WOOD, "north"); hang_lantern(t, 10, 3, 7)
    for (x, z) in ((1, 5), (11, 5), (5, 1), (7, 1)): b.window(x, 2, z, {1: "west", 11: "east"}.get(x, "north"))
    b.entrance(6, 12, True)
    return b

# ---------------- big house ----------------
def planter_house(seed=1):
    b = mkB("planter_house", "limestone", 15, 15, 13, seed); t = b.t; b.ground()
    b.walls(1, 13, 1, 8, 0, 4, base_h=2)                          # ground storey limestone
    for x in range(1, 14):
        for z in range(1, 9):
            edge = x in (1, 13) or z in (1, 8)
            b.role(x, 5, z, "floor" if not edge else "trim" if x in (1, 13) and z in (1, 8) else "beam", {"axis": "x" if z in (1, 8) else "z"})
            for y in range(6, 9):
                if not edge: b.set(x, y, z, M("air"))
                elif x in (1, 13) and z in (1, 8): b.role(x, y, z, "trim", {"axis": "y"})
                else: b.t.set(x, y, z, "role:wall"); b.band[(x, y, z)] = (1, 8)   # upper storey continues the ground-storey ramp (lighter)
    b.style_upper = "creole"
    b.gable(1, 13, 1, 8, 9, "x")
    for x in range(1, 14):                                       # porch z9..10 + balcony above (y5 floor, fence rail y6)
        for z in (9, 10): b.role(x, 0, z, "floor"); b.role(x, 5, z, "floor")
    porch_posts(b, (1, 4, 7, 10, 13), 10, 1, 4); porch_posts(b, range(1, 14), 10, 6, 6)
    for x in (1, 13): t.set(x, 6, 9, M(WOOD + "_fence"))
    for x in range(0, 15): slab(t, x, 9, 9, "spruce"); slab(t, x, 9, 10, "spruce")
    door(t, 7, 1, 8, WOOD, "south"); door(t, 7, 6, 8, WOOD, "south")
    for x in (3, 11):
        b.window(x, 2, 8, "south", tall=True); b.window(x, 7, 8, "south")
    for z in (4,): b.window(1, 2, z, "west", tall=True); b.window(13, 2, z, "east", tall=True); b.window(1, 7, z, "west"); b.window(13, 7, z, "east")
    for y in range(1, 6): t.set(12, y, 2, M("ladder"), {"facing": "south", "waterlogged": "false"})        # to the upper floor
    # ground: parlour (sofa + coffee table), dining (2x3), kitchen
    for z in (5, 6): stairs(t, 2, 1, z, WOOD, "west")
    t.set(2, 1, 4, M(WOOD + "_trapdoor"), {"facing": "south", "half": "bottom", "open": "true", "powered": "false", "waterlogged": "false"})
    t.set(2, 1, 7, M(WOOD + "_trapdoor"), {"facing": "north", "half": "bottom", "open": "true", "powered": "false", "waterlogged": "false"})
    slab(t, 4, 1, 5, "spruce"); slab(t, 4, 1, 6, "spruce"); t.set(3, 1, 5, M("red_carpet")); t.set(3, 1, 6, M("red_carpet"))
    for x in (6, 7, 8): table(t, x, 1, 4, WOOD)
    for x in (6, 8): chair(t, x, 1, 3, WOOD, "north"); chair(t, x, 1, 5, WOOD, "south")
    t.set(7, 2, 4, M("candle"), {"candles": "3", "lit": "false", "waterlogged": "false"})   # centrepiece replaces the middle plate
    t.set(11, 1, 2, M("smoker"), {"facing": "south", "lit": "false"}); t.set(10, 1, 2, M("barrel"), {"facing": "up", "open": "false"}); t.set(9, 1, 2, M("water_cauldron"), {"level": "2"})
    for x in (3, 7, 11): hang_lantern(t, x, 4, 4)
    # upper: 2 bedrooms + study
    bed(t, 2, 6, 2, "blue", "north"); bed(t, 3, 6, 2, "blue", "north"); b.chest(4, 6, 2, "south"); bed(t, 9, 6, 2, "white", "north")
    b.job(5, 6, 6, "cartography_table"); chair(t, 5, 6, 7, WOOD, "south"); t.set(4, 6, 7, M("bookshelf")); t.set(6, 6, 7, M("bookshelf"))
    for x in (3, 10): hang_lantern(t, x, 8, 4)
    for x in (3, 11): t.set(x, 1, 9, M("potted_cactus"))
    stairs(t, 5, 1, 9, WOOD, "north"); stairs(t, 9, 1, 9, WOOD, "north")
    b.entrance(7, 11, True)
    for x in range(15): b.role(x, 0, 12, "floor") if False else None
    return b

# ---------------- job buildings ----------------
def smokehouse(seed=1):
    b = mkB("smokehouse", "limestone", 9, 11, 13, seed); t = b.t; b.ground()
    b.walls(1, 7, 1, 10, 0, 3, base_h=2)
    b.gable(1, 7, 1, 10, 4, "z")
    for y in range(0, 9): b.role(4, y, 0, "base" if y < 3 else "wall", band=(0, 8))      # chimney (north)
    b.job(4, 1, 2, "smoker", {"facing": "south", "lit": "false"}); b.role(4, 2, 1, "inner")
    for z in (4, 6): hang_lantern(t, 4, 3, z)
    for x in (2, 6):                                              # meat hooks (chains) + counters
        for z in (3, 5, 7): t.set(x, 3, z, M("chain"), {"axis": "y", "waterlogged": "false"})
    for z in (8, 9): t.set(2, 1, z, M("barrel"), {"facing": "up", "open": "false"}); stairs(t, 6, 1, z, "spruce", "east", "top")
    b.chest(6, 1, 3, "west", "minecraft:chests/village/village_butcher"); t.set(2, 1, 3, M("water_cauldron"), {"level": "3"})
    door(t, 4, 1, 10, "spruce", "south"); b.window(1, 2, 5, "west"); b.window(7, 2, 5, "east")
    t.set(2, 1, 11, M("hay_block"), {"axis": "y"}); t.set(6, 1, 11, M("barrel"), {"facing": "up", "open": "false"})
    b.entrance(4, 12, True)
    return b

def forge(seed=1):
    b = mkB("forge", "limestone", 13, 10, 11, seed); t = b.t; b.ground()
    for x in range(1, 12):
        for z in range(1, 9): b.role(x, 0, z, "floor" if 2 <= x <= 10 and 2 <= z <= 7 else "base")
    for (x, z) in ((1, 1), (11, 1), (1, 8), (11, 8), (6, 1), (6, 8)):
        for y in range(1, 4): b.role(x, y, z, "trim" if y < 3 else "beam", {"axis": "y"})
    for x in range(1, 12):                                        # low walls on the north + west, open front
        for y in (1, 2): b.role(x, y, 1, "wall", band=(1, 3))
    for z in range(1, 9):
        for y in (1, 2): b.role(1, y, z, "wall", band=(1, 3))
    b.gable(1, 11, 1, 8, 4, "x", ceiling=False)                   # open forge: no ceiling (chimney goes through)
    for y in range(1, 9): b.role(3, y, 2, "base" if y < 3 else "wall", band=(1, 8))        # forge chimney
    t.set(3, 1, 3, M("blast_furnace"), {"facing": "south", "lit": "false"}); b.role(4, 1, 2, "base")
    b.job(6, 1, 5, "grindstone", {"face": "floor", "facing": "south"}); t.set(8, 1, 4, M("anvil"), {"facing": "east"}); t.set(9, 1, 2, M("smithing_table"))
    t.set(4, 1, 6, M("water_cauldron"), {"level": "3"}); b.chest(10, 1, 2, "south", "minecraft:chests/village/village_toolsmith"); t.set(10, 1, 5, M("barrel"), {"facing": "up", "open": "false"})
    hang_lantern(t, 6, 3, 4); t.set(2, 1, 7, R("rusted_drum"), {"axis": "y"})
    b.job(7, 1, 2, "fletching_table"); b.job(2, 1, 5, "stonecutter", {"facing": "east"})   # 9-8: fletcher + mason exist in every family
    b.entrance(6, 10, True)
    return b

def schoolhouse(seed=1):
    b = mkB("schoolhouse", "hacienda", 12, 12, 14, seed); t = b.t; b.ground()
    b.walls(1, 10, 1, 11, 0, 4, base_h=1)
    b.gable(1, 10, 1, 11, 5, "z")
    for z in range(2, 11):                                         # bookshelf walls (3 high) with trapdoor trim
        if z in (6,): continue
        for y in (1, 2, 3): t.set(2, y, z, M("bookshelf"))
    b.job(5, 1, 3, "lectern", {"facing": "south", "has_book": "false", "powered": "false"})
    for z in (6, 8):                                               # desks (slab on fence) + stools, 2 rows
        for x in (5, 7):
            table(t, x, 1, z, WOOD); chair(t, x, 1, z + 1, WOOD, "south")
    for x in (7, 8): t.set(x, 2, 1, M("black_carpet") if False else M("dark_oak_planks")) if False else None
    for x in (6, 7, 8): t.set(x, 2, 2, M("dark_oak_trapdoor"), {"facing": "south", "half": "top", "open": "true", "powered": "false", "waterlogged": "false"})  # blackboard
    b.chest(9, 1, 2, "west", "minecraft:chests/village/village_cartographer")
    for z in (4, 9): b.window(10, 2, z, "east", tall=True)
    b.window(1, 2, 6, "west", tall=True); door(t, 6, 1, 11, WOOD, "south")
    for z in (4, 8): hang_lantern(t, 6, 4, z)
    for y in range(5, 9): b.role(6, y, 12, "wall", band=(5, 9)) if False else None
    t.set(4, 1, 12, M("potted_cactus")); t.set(8, 1, 12, M("potted_dead_bush"))
    b.entrance(6, 13, True)
    return b

def chapel(seed=1):
    b = mkB("chapel", "hacienda", 17, 17, 21, seed); t = b.t; b.ground()
    b.walls(3, 13, 2, 17, 0, 6, base_h=1)                         # nave 11 x 16
    b.gable(3, 13, 2, 17, 7, "z", ceiling=False)                  # vaulted nave
    b.walls(10, 14, 15, 19, 0, 11, base_h=1, floor=True)          # bell tower front-right
    for x in range(10, 15):
        for z in range(15, 20): b.role(x, 12, z, "roof_slab", {"type": "bottom"})
    for x in range(11, 14):
        for z in range(16, 19): b.set(x, 7, z, M("air")) if False else None
    for (x, z) in ((12, 15), (12, 19), (10, 17), (14, 17)):
        for y in (9, 10): t.set(x, y, z, M("air"))                # belfry openings
    b.role(12, 8, 17, "floor"); t.set(12, 10, 17, M("bell"), {"attachment": "ceiling", "facing": "north", "powered": "false"}); b.role(12, 11, 17, "beam", {"axis": "y"})
    for y in range(1, 9): t.set(13, y, 18, M("ladder"), {"facing": "west", "waterlogged": "false"})
    door(t, 8, 1, 17, "dark_oak", "south"); t.set(7, 1, 17, M("air")) if False else None
    for z in range(5, 15, 2):                                      # pews (stairs) both sides of the aisle x8
        for x in (5, 6, 10, 11): stairs(t, x, 1, z, WOOD, "south")
    b.job(8, 1, 4, "brewing_stand", {"has_bottle_0": "false", "has_bottle_1": "false", "has_bottle_2": "false"})
    for x in (6, 7, 9, 10): t.set(x, 1, 3, M("smooth_sandstone_slab"), {"type": "top", "waterlogged": "false"})
    for x in (6, 10): t.set(x, 2, 3, M("candle"), {"candles": "4", "lit": "false", "waterlogged": "false"})
    for z in (6, 10, 14): b.window(3, 3, z, "west", tall=True); b.window(13, 3, z, "east", tall=True)
    for z in (5, 9, 13): hang_lantern(t, 8, 6, z)
    b.chest(4, 1, 3, "east", "minecraft:chests/village/village_temple")
    t.set(6, 1, 18, M("potted_cactus")); t.set(5, 1, 19, M("decorated_pot"), {"facing": "south", "cracked": "false", "waterlogged": "false"})
    b.entrance(8, 20, True)
    return b

def kitchen_garden(seed=1):
    b = mkB("kitchen_garden", "hacienda", 15, 7, 9, seed); t = b.t; b.ground(("grass_block", "coarse_dirt"))
    for x in range(0, 15):                                        # low stucco wall around, gate at the front
        for z in (0, 7):
            if z == 7 and 6 <= x <= 8: continue
            b.role(x, 1, z, "wall", band=(1, 2)); b.role(x, 0, z, "base")
    for z in range(0, 8): b.role(0, 1, z, "wall", band=(1, 2)); b.role(14, 1, z, "wall", band=(1, 2))
    crops = ["wheat", "carrots", "potatoes", "beetroots"]
    for x in range(1, 14):
        for z in range(1, 7):
            if x == 7: t.set(x, 0, z, M("water") if z in (2, 3, 4, 5) else M("dirt_path"), {"level": "0"} if z in (2, 3, 4, 5) else None); continue
            if z in (1, 6): t.set(x, 0, z, M("dirt_path")); continue
            t.set(x, 0, z, M("farmland"), {"moisture": "7"}); c = crops[(x - 1) // 3 % 4]
            t.set(x, 1, z, M(c), {"age": str(min(b.r.randint(2, 7), 3 if c == "beetroots" else 7))})
    b.job(1, 1, 1, "composter", {"level": "3"}); t.set(13, 1, 1, M("barrel"), {"facing": "up", "open": "false"})
    for x in (3, 11):                                             # pergola posts + trapdoor top over the path
        for z in (1, 6):
            for y in (1, 2): t.set(x, y, z, M(WOOD + "_fence"))
            t.set(x, 3, z, M(WOOD + "_trapdoor"), {"facing": "north", "half": "bottom", "open": "false", "powered": "false", "waterlogged": "false"})
    t.set(7, 1, 1, M("water_cauldron"), {"level": "3"}); t.set(7, 1, 6, M("lantern"), {"hanging": "false", "waterlogged": "false"}); t.set(7, 0, 6, M("dirt_path"))
    b.entrance(7, 8, True)
    return b

def orchard(seed=1):
    b = mkB("orchard", "creole", 12, 9, 13, seed); t = b.t; b.ground(("grass_block", "coarse_dirt", "grass_block"))
    for (x, z) in ((2, 2), (6, 2), (10, 2), (2, 6), (6, 6), (10, 6)):     # small acacia trees (persistent leaves)
        for y in (1, 2, 3): t.set(x, y, z, M(WOOD + "_log"), {"axis": "y"})
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for y in (3, 4):
                    if (dx, dz, y) != (0, 0, 3) and not (abs(dx) + abs(dz) == 2 and y == 4):
                        t.set(x + dx, y, z + dz, M(WOOD + "_leaves"), {"distance": "1", "persistent": "true", "waterlogged": "false"})
    for x in range(1, 12): t.set(x, 0, 4, M("dirt_path")); t.set(x, 0, 8, M("dirt_path"))
    for x in (1, 3, 5, 9, 11):
        for z in (9, 10): t.set(x, 0, z, M("farmland"), {"moisture": "7"}); t.set(x, 1, z, M("melon_stem" if x < 6 else "pumpkin_stem"), {"age": "5"})
    for x in (7,): t.set(x, 0, 9, M("water"), {"level": "0"}); t.set(x, 0, 10, M("water"), {"level": "0"})
    b.walls(8, 10, 9, 11, 0, 2, base_h=0) if False else None
    b.job(6, 1, 10, "composter", {"level": "4"}); t.set(5, 1, 11, M("hay_block"), {"axis": "y"}); t.set(8, 1, 11, M("barrel"), {"facing": "up", "open": "false"})
    for x in (0, 11):
        for z in range(0, 12): t.set(x, 1, z, M(WOOD + "_fence"))
    for x in range(0, 12):
        if x not in (5, 6, 7): t.set(x, 1, 0, M(WOOD + "_fence"))
    for x in range(0, 12):
        if x not in (5, 6, 7): t.set(x, 1, 11, M(WOOD + "_fence"))
    t.set(6, 1, 11, M(WOOD + "_fence_gate"), {"facing": "south", "in_wall": "false", "open": "false", "powered": "false"})
    b.entrance(6, 12, True)
    return b

ROSTER = [  # (builder, weight)  vanilla-ish slot weights
    (creole_cottage, 3), (dogtrot, 3), (limestone_cottage, 3), (casita, 3), (courtyard_house, 2), (planter_house, 2),
    (smokehouse, 2), (forge, 2), (schoolhouse, 2), (chapel, 1), (kitchen_garden, 3), (orchard, 2)]

def main():
    N = OUT / "structure/savanna"; N.mkdir(parents=True, exist_ok=True)
    els = []
    for fn, wt in ROSTER:
        for v in ("base", "lived", "ruined"):
            b = fn(1); t = b.finalize(v); (N / f"{b.name}_{v}.nbt").write_bytes(t.bytes())
            if v != "base":
                els.append({"weight": wt * (4 if v == "lived" else 6), "element": {"element_type": "minecraft:single_pool_element",
                            "location": f"dying_world:savanna/{b.name}_{v}", "processors": "minecraft:empty", "projection": "rigid"}})
    w(OUT.parent / "minecraft/worldgen/template_pool/village/savanna/houses.json", {"fallback": "minecraft:village/savanna/terminators", "elements": els})
    old = OUT / "structure/village/savanna"
    if old.exists(): shutil.rmtree(old)                           # our worn copies of the replaced custom set
    w(OUT / "worldgen/template_pool/savanna/ruined_houses.json", {"fallback": "minecraft:empty", "elements": [
        {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:savanna/{fn(1).name}_ruined",
         "processors": "minecraft:empty", "projection": "rigid"}} for fn, wt in ROSTER]})
    print(f"7-1: {len(ROSTER)} savanna buildings x 3 variants; savanna house pool = {len(els)} entries (lived 40 / ruined 60)")

if __name__ == "__main__":
    main()
