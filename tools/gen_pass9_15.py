#!/usr/bin/env python3
"""
gen_pass9_15.py - pass 9-15(b): RESEARCH STATIONS AS VILLAGES. Run after gen_pass9_11.py (loot tables, biome tags, structure json). Safe to re-run.
9-15  : user on 9-11 (above-ground mineshafts, entrance straight to the portal, R&R as main material) -> hall + streets + outbuildings.
9-15b : user on 9-15: 'too tall and too empty', 'palette should borrow from their representative dimension, not stark white', no portal in the End one
        -> compact hall (21x?x19, 5-high walls, gable roof, small tower), furnished rooms, lower outbuildings, per-site palettes, End return portal.
Layout: START = research hall: front archway (south) -> entry hall (brewing benches, cauldrons, books, table, distillery, carpet runner) -> partition doorway
-> inner sanctum at the back with the portal. Street jigsaws on 4 sides -> narrow streets (9-3 generator) -> outbuildings (workshop, specimen garden,
library tower, quarters, storehouse, boiler house, watch post), dead ends = wall ends.
Palettes (savanna_kit gradient ramps) borrow from the linked dimension:
  gate_end    : deepslate + end stone bricks + purpur trim + obsidian beams, deepslate-tile roof; chorus specimen bed; deepslate/end-stone paving
  gate_nether : stone/deepslate base -> nether brick/red nether brick, crimson timber, nether-brick roof; nether-wart bed; blackstone paving
  nether      : blackstone/basalt -> nether bricks/red nether bricks, crimson timber; soul lanterns; nether-brick causeways with railings
  end         : obsidian base -> end stone bricks -> purpur, purpur roof; end rods; purpur walkways with iron railings; chorus bed
Portals: gate_end 12 empty frames (eyes required) | gate_nether lit | nether frame unlit + flint&steel | END: 12 EMPTY FRAMES too - filling them in the End
makes an end portal, which in the End leads back to the overworld (the 'work to get back out'). Elytra chest on a plinth beside it + 4 shulkers.
R&R = flavor (chimney, distillery pipes, boiler house).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl, S as NS, B as NB
from savanna_kit import B, RAMPS
from buildkit import M, R, door, bed, hang_lantern, fix_connections, connect_pipes
from gen_pass4_2a import w, OUT
import gen_pass9_3 as G
import gen_pass9_11 as K

SITES = ("gate_end", "gate_nether", "nether", "end")
SIDE = {"gate_end": "ow", "gate_nether": "ow", "nether": "nether", "end": "end"}
RAMPS.update({
    "st_gate_end": {"wall": ["cobbled_deepslate", "deepslate_bricks", "end_stone_bricks", "end_stone_bricks"], "base": ["cobbled_deepslate", "deepslate_bricks", "polished_deepslate"],
                    "floor": ["dark_oak_planks", "polished_deepslate", "dark_oak_planks"], "trim": ["purpur_block"], "beam": ["obsidian"],
                    "roof": "deepslate_tile", "ridge": "purpur", "inner": ["deepslate_bricks", "end_stone_bricks"], "ceil": "dark_oak"},
    "st_gate_nether": {"wall": ["cobblestone", "stone_bricks", "nether_bricks", "red_nether_bricks"], "base": ["cobbled_deepslate", "blackstone", "cobblestone"],
                       "floor": ["crimson_planks", "spruce_planks", "crimson_planks"], "trim": ["stripped_crimson_hyphae"], "beam": ["crimson_hyphae"],
                       "roof": "nether_brick", "ridge": "red_nether_brick", "inner": ["stone_bricks", "nether_bricks"], "ceil": "crimson"},
    "st_nether": {"wall": ["blackstone", "polished_blackstone_bricks", "nether_bricks", "red_nether_bricks"], "base": ["blackstone", "basalt", "polished_blackstone_bricks"],
                  "floor": ["crimson_planks", "warped_planks", "crimson_planks"], "trim": ["stripped_crimson_hyphae"], "beam": ["crimson_hyphae"],
                  "roof": "nether_brick", "ridge": "red_nether_brick", "inner": ["nether_bricks", "polished_blackstone_bricks"], "ceil": "crimson"},
    "st_end": {"wall": ["obsidian", "end_stone_bricks", "purpur_block", "purpur_block"], "base": ["obsidian", "obsidian", "end_stone_bricks"],
               "floor": ["purpur_block", "obsidian", "end_stone_bricks"], "trim": ["purpur_block"], "beam": ["obsidian"],
               "roof": "purpur", "ridge": "end_stone_brick", "inner": ["end_stone_bricks", "purpur_block"], "ceil": "purpur"}})
GROUND = {"gate_end": ("dirt_path", "coarse_dirt", "grass_block", "gravel"), "gate_nether": ("coarse_dirt", "netherrack", "grass_block", "gravel"),
          "nether": ("nether_bricks", "blackstone", "soul_soil", "netherrack"), "end": ("end_stone", "end_stone_bricks", "obsidian")}
WOOD = {"gate_end": "dark_oak", "gate_nether": "crimson", "nether": "crimson", "end": "dark_oak"}
CARPET = {"gate_end": "purple_carpet", "gate_nether": "red_carpet", "nether": "red_carpet", "end": "magenta_carpet"}
LIGHT = {"gate_end": "lantern", "gate_nether": "lantern", "nether": "soul_lantern", "end": "lantern"}
PIPE = {d: "true" for d in ("north", "east", "south", "west", "up", "down")}
SUFFIX, VARIANT = "", "lived"        # 9-23: ("_derelict", "ruined") builds the rare abandoned stations
SJ = lambda site: f"dying_world:station/{site}{SUFFIX}"
BREW = {"has_bottle_0": "false", "has_bottle_1": "false", "has_bottle_2": "false"}

def mk(site, name, W, H, D, seed=1):
    B.STEEP = False; B.FLAT = False
    b = B(f"station_{site}_{name}", f"st_{site}", W, H, D, seed); b.site = site; b.side = SIDE[site]; return b
def hang(b, x, y, z):
    hang_lantern(b.t, x, y, z)
    if LIGHT[b.site] != "lantern": b.set(x, y - 1, z, M(LIGHT[b.site]), {"hanging": "true", "waterlogged": "false"})
def chestK(b, x, y, z, facing, kind): b.chest(x, y, z, facing, f"dying_world:chests/research_{b.site}_{kind}")
def street_jig(b, x, z, ori):
    b.set(x, 1, z, M("jigsaw"), {"orientation": ori}, {"id": M("jigsaw"), "name": "minecraft:street", "target": "minecraft:street",
          "pool": f"{SJ(b.site)}/streets", "final_state": M("air"), "joint": "aligned"})
def box(b, x0, x1, z0, z1, top, door_x=None, windows=True, wy=2):
    b.walls(x0, x1, z0, z1, 0, top)
    if door_x is not None:
        for y in (1, 2): b.set(door_x, y, z1, M("air"))
        door(b.t, door_x, 1, z1, WOOD[b.site], "south")
    if windows:
        for z in range(z0 + 2, z1 - 1, 3): b.window(x0, wy, z, "west"); b.window(x1, wy, z, "east")
        for x in range(x0 + 2, x1 - 1, 3): b.window(x, wy, z0, "north")
def front(b, z1, door_x):
    for x in range(b.t.sx):
        b.set(x, 0, z1 + 1, M(b.r.choice(GROUND[b.site]))); b.set(x, 1, z1 + 1, M("air")); b.set(x, 2, z1 + 1, M("air"))
    b.entrance(door_x, z1 + 1, False)
def frames(b, cx, cz):
    """12 empty end portal frames around a 3x3 centre (cx,cz) - eyes of ender required"""
    for i in (-1, 0, 1):
        b.set(cx + i, 1, cz - 2, M("end_portal_frame"), {"facing": "south", "eye": "false"}); b.set(cx + i, 1, cz + 2, M("end_portal_frame"), {"facing": "north", "eye": "false"})
        b.set(cx - 2, 1, cz + i, M("end_portal_frame"), {"facing": "east", "eye": "false"}); b.set(cx + 2, 1, cz + i, M("end_portal_frame"), {"facing": "west", "eye": "false"})
    for i in (-1, 0, 1):
        for j in (-1, 0, 1): b.set(cx + i, 0, cz + j, M("obsidian"))

# ---------------- research hall (start piece): 21 x H x 19, building x2..18 z2..16 ----------------
def hall(site):
    side = SIDE[site]; tt = 19 if side == "end" else 15                 # tower top (clears the y14 ridge)
    b = mk(site, "hall", 21, tt + 5, 19); r = b.r; b.ground(GROUND[site])
    box(b, 2, 18, 2, 16, 5, wy=2)
    for x in (9, 10, 11):                                                 # front archway
        for y in (1, 2, 3): b.set(x, y, 16, M("air"))
    for y in (1, 2, 3, 4): b.role(8, y, 16, "trim", {"axis": "y"}); b.role(12, y, 16, "trim", {"axis": "y"})
    for x in range(8, 13): b.role(x, 4, 16, "beam", {"axis": "x"})
    for x in range(3, 18):                                                # partition z9 with a doorway
        for y in range(1, 6):
            if 9 <= x <= 11 and y <= 3: b.set(x, y, 9, M("air"))
            else: b.role(x, y, 9, "inner", band=(1, 5))
    b.gable(2, 18, 2, 16, 6, axis="x", over=1)
    for x in range(14, 19):                                               # NE tower x14..18 z2..6
        for z in range(2, 7):
            for y in range(1, tt + 1):
                if x in (14, 18) or z in (2, 6):
                    c = x in (14, 18) and z in (2, 6)
                    b.role(x, y, z, "trim" if c else "wall", {"axis": "y"} if c else None, band=(1, tt))
                else: b.set(x, y, z, M("air"))
    for y in (1, 2): b.set(14, y, 4, M("air"))
    for y in range(1, tt): b.set(17, y, 4, M("ladder"), {"facing": "west", "waterlogged": "false"})
    for x in range(15, 18):
        for z in range(3, 6):
            if (x, z) != (17, 4): b.role(x, tt - 1, z, "floor")
    b.window(18, tt - 3, 4, "east"); b.window(16, tt - 3, 2, "north"); b.window(16, 8, 2, "north")
    b.gable(14, 18, 2, 6, tt + 1, axis="z", over=1, ceiling=False)
    # ---- entry hall z10..15 ----
    for z in (11, 13):
        b.set(3, 1, z, M(f"{WOOD[site]}_planks")); b.set(3, 2, z, M("brewing_stand"), BREW); b.set(3, 1, z + 1, M("water_cauldron"), {"level": "3"})
    b.set(3, 1, 15, M("barrel"), {"facing": "up", "open": "false"}); b.set(3, 2, 15, M("flower_pot"))
    for z in range(10, 15):
        for y in (1, 2, 3): b.set(17, y, z, M("bookshelf") if (z + y) % 4 else M("chiseled_bookshelf"), {"facing": "west", **{f"slot_{i}_occupied": "false" for i in range(6)}} if (z + y) % 4 == 0 else None)
    b.set(16, 1, 12, M("lectern"), {"facing": "west", "has_book": "false", "powered": "false"})
    for x in range(6, 9):                                                 # work table west of the runner
        b.set(x, 1, 12, M(f"{WOOD[site]}_slab"), {"type": "top", "waterlogged": "false"})
    b.set(6, 2, 12, M("candle"), {"candles": "3", "lit": "false", "waterlogged": "false"}); b.set(8, 2, 12, M("brewing_stand"), BREW)
    for x in range(12, 15): b.set(x, 1, 12, M(f"{WOOD[site]}_slab"), {"type": "top", "waterlogged": "false"})
    b.set(13, 2, 12, M("candle"), {"candles": "2", "lit": "false", "waterlogged": "false"})
    for z in range(10, 16):
        for x in (9, 10, 11): b.set(x, 1, z, M(CARPET[site]))
    for y in range(1, 5): b.set(5, y, 15, R("rusted_fluid_pipe"), PIPE)          # distillery
    b.set(4, 1, 15, R("rusted_drum"), {"axis": "y"}); b.set(6, 1, 15, R("rusted_mechanical_pump"), {"facing": "up"})
    for x in range(5, 9): b.set(x, 5, 15, R("rusted_fluid_pipe"), PIPE)
    chestK(b, 4, 1, 10, "east", "lab"); chestK(b, 16, 1, 15, "west", "archive")
    hang(b, 7, 5, 11); hang(b, 13, 5, 11); hang(b, 10, 5, 14)
    # ---- sanctum z3..8 (x3..13; tower takes x14..18 z2..6) ----
    for x, z in ((3, 3), (3, 8), (13, 8)):
        for y in range(1, 6): b.role(x, y, z, "trim", {"axis": "y"})
    if site in ("gate_end", "end"):
        frames(b, 8, 5)
        if site == "end":
            b.set(12, 1, 7, M("obsidian")); b.set(12, 2, 7, M("chest"), {"facing": "west", "type": "single", "waterlogged": "false"},
                                                {"id": M("chest"), "LootTable": "dying_world:chests/research_end_elytra"})
            b.set(12, 1, 4, M("end_rod"), {"facing": "up"}); b.set(4, 1, 4, M("end_rod"), {"facing": "up"})
            for x, z in ((4, 7), (12, 3), (5, 14), (15, 11)):
                b.t.entity(x + .5, 1, z + .5, {"id": NS("minecraft:shulker"), "PersistenceRequired": NB(1), "AttachFace": NB(0), "Color": NB(16)})
            chestK(b, 4, 1, 6, "east", "store")
        else:
            for x in range(5, 12):
                for z in (3, 7, 8):
                    if b.get(x, 0, z) not in (M("obsidian"),) and r.random() < .5: b.set(x, 0, z, M("end_stone_bricks") if r.random() < .6 else M("crying_obsidian"))
            chestK(b, 12, 1, 7, "west", "store")
    else:                                                                 # nether portal (frame x6..9 z4, axis x)
        for y in range(1, 6):
            for x in range(6, 10):
                if y in (1, 5) or x in (6, 9): b.set(x, y, 4, M("obsidian"))
                elif site == "gate_nether": b.set(x, y, 4, M("nether_portal"), {"axis": "x"})
                else: b.set(x, y, 4, M("air"))
        creep = [(M("netherrack"), .5), (M("crimson_nylium"), .2), (M("soul_soil"), .15), (M("magma_block"), .15)] if site == "gate_nether" else \
                [(M("moss_block"), .45), (M("coarse_dirt"), .25), (M("mossy_cobblestone"), .2), (M("rooted_dirt"), .1)]
        for x in range(3, 14):
            for z in range(3, 9):
                if r.random() < max(0, 1 - (abs(x - 7.5) + abs(z - 4) * 1.4) / 7): b.set(x, 0, z, K.pick(r, creep))
        if site == "nether":
            b.set(11, 1, 6, M("chest"), {"facing": "west", "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": "dying_world:chests/research_nether_portal"})
        chestK(b, 4, 1, 7, "east", "store")
    hang(b, 5, 5, 6); hang(b, 11, 5, 6)
    for y in range(0, 11):                                                # R&R chimney on the west side
        for z in (12, 13): b.set(1, y, z, R("sooty_brick") if y % 4 else R("riveted_rusted_plating"))
    b.set(1, 11, 12, R("rusted_fluid_pipe"), PIPE)
    t = b.finalize(VARIANT)
    street_jig(b, 10, 0, "north_up"); street_jig(b, 0, 9, "west_up"); street_jig(b, 20, 9, "east_up"); street_jig(b, 10, 18, "south_up")
    return t

# ---------------- outbuildings (front = south; entrance jigsaw on the yard row) ----------------
def house(site, name, W, D, top, seed, roof=True):
    b = mk(site, name, W, top + min(W, D) // 2 + 3, D + 1, seed); b.ground(GROUND[site])
    box(b, 0, W - 1, 0, D - 1, top, door_x=W // 2)
    if roof: b.gable(0, W - 1, 0, D - 1, top + 1, axis="z" if W < D else "x", over=0)
    front(b, D - 1, W // 2); return b

def workshop(site):
    b = house(site, "workshop", 9, 7, 4, 1)
    for x in (2, 4): b.set(x, 1, 1, M(f"{WOOD[site]}_planks")); b.set(x, 2, 1, M("brewing_stand"), BREW)
    b.set(3, 1, 1, M("water_cauldron"), {"level": "3"}); b.set(6, 1, 1, M("crafting_table")); b.set(7, 1, 1, M("smithing_table"))
    b.set(7, 1, 2, M("anvil"), {"facing": "north"}); chestK(b, 7, 1, 4, "west", "lab")
    if site.startswith("gate_"):                                          # allay specimen cage (allays had no other source)
        for x in (1, 2, 3):
            for z in (3, 4, 5):
                for y in (1, 2, 3):
                    if x in (1, 3) or z in (3, 5) or y in (1, 3): b.set(x, y, z, M("glass") if y == 2 else M("polished_andesite"))
                    else: b.set(x, y, z, M("air"))
        b.t.entity(2.5, 2, 4.5, {"id": NS("minecraft:allay"), "PersistenceRequired": NB(1)})
    else: b.set(1, 1, 4, M("barrel"), {"facing": "up", "open": "false"}); b.set(1, 1, 3, M("cauldron"))
    hang(b, 5, 4, 3); return b.finalize(VARIANT)

def garden(site):
    """specimen garden: small potting shed + a bed of the linked dimension's plant (chorus on end stone / nether wart on soul sand)"""
    b = mk(site, "garden", 13, 10, 8, 2); b.ground(GROUND[site])
    box(b, 0, 5, 0, 6, 4, door_x=3); b.gable(0, 5, 0, 6, 5, axis="z", over=0); front(b, 6, 3)
    b.set(1, 1, 1, M("composter"), {"level": "4"}); b.set(4, 1, 1, M("barrel"), {"facing": "up", "open": "false"})
    for z in (2, 3, 4): b.set(1, 1, z, M(f"{WOOD[site]}_slab"), {"type": "top", "waterlogged": "false"})
    b.set(1, 2, 3, M("flower_pot")); chestK(b, 4, 1, 4, "west", "lab"); hang(b, 3, 4, 3)
    chorus = site in ("gate_end", "end"); fence = "iron_bars" if site == "end" else f"{WOOD[site]}_fence"
    for x in range(7, 13):
        for z in range(0, 7):
            if x in (7, 12) or z in (0, 6):
                b.set(x, 0, z, M(GROUND[site][1])); b.set(x, 1, z, M(fence) if (x, z) != (9, 6) else M("air"))
            else:
                b.set(x, 0, z, M("end_stone" if chorus else "soul_sand"))
                if chorus: b.set(x, 1, z, M("chorus_flower"), {"age": "0"}) if (x + z) % 3 == 0 else None
                else: b.set(x, 1, z, M("nether_wart"), {"age": "3"})
    return b.finalize(VARIANT)

def library(site):
    top = 11 if site == "end" else 8
    b = house(site, "library", 7, 7, top, 3)
    for y in range(1, top): b.set(1, y, 3, M("ladder"), {"facing": "east", "waterlogged": "false"})
    for x in range(2, 6):
        for y in (1, 2): b.set(x, y, 1, M("bookshelf"))
        for y in (6, 7): b.set(x, y, 1, M("bookshelf"))
    for x in range(1, 6):
        for z in range(1, 6):
            if (x, z) != (1, 3): b.role(x, 4, z, "floor")
    b.set(5, 1, 3, M("lectern"), {"facing": "west", "has_book": "false", "powered": "false"}); chestK(b, 5, 5, 4, "west", "archive")
    b.set(3, 5, 4, M(CARPET[site])); b.set(4, 5, 4, M(CARPET[site])); hang(b, 4, top, 3)
    b.set(2, 1, 5, M(LIGHT[site]), {"hanging": "false", "waterlogged": "false"})
    return b.finalize(VARIANT)

def quarters(site):
    b = house(site, "quarters", 9, 7, 4, 4)
    for x in (1, 3, 5, 7): bed(b.t, x, 1, 1, "purple" if site in ("gate_end", "end") else "red" if site != "gate_end" else "gray", "south")
    for x in (2, 4, 6): b.set(x, 1, 1, M(f"{WOOD[site]}_slab"), {"type": "bottom", "waterlogged": "false"})
    chestK(b, 7, 1, 4, "west", "quarters"); b.set(1, 1, 4, M("barrel"), {"facing": "up", "open": "false"})
    for x in (3, 4, 5): b.set(x, 1, 4, M(CARPET[site]))
    hang(b, 4, 4, 3); return b.finalize(VARIANT)

def storehouse(site):
    b = house(site, "storehouse", 9, 7, 4, 5); r = b.r
    for x in range(1, 8):
        for z in (1, 2):
            if r.random() < .7: b.set(x, 1, z, r.choice([M("barrel"), M("barrel"), M("hay_block"), R("weathered_wooden_crate")]))
            if r.random() < .35: b.set(x, 2, z, r.choice([M("barrel"), R("weathered_wooden_crate")]))
    chestK(b, 1, 1, 4, "east", "store"); chestK(b, 7, 1, 4, "west", "store"); hang(b, 4, 4, 4)
    return b.finalize(VARIANT)

def boiler(site):
    b = house(site, "boiler", 9, 7, 4, 6)
    b.set(4, 1, 1, M("blast_furnace"), {"facing": "south", "lit": "false"}); b.set(3, 1, 1, M("furnace"), {"facing": "south", "lit": "false"})
    b.set(5, 1, 1, R("rusted_mechanical_pump"), {"facing": "south"}); b.set(6, 1, 1, R("gas_cylinders"), {"count": "5", "facing": "south"})
    for y in (2, 3, 4): b.set(4, y, 1, R("rusted_fluid_pipe"), PIPE)
    for x in range(2, 7): b.set(x, 4, 2, R("rusted_fluid_pipe"), PIPE)
    b.set(7, 1, 2, R("rusted_encased_cogwheel"), {"axis": "x", "top_shaft": "true", "bottom_shaft": "true"})
    chestK(b, 7, 1, 4, "west", "engine"); b.set(1, 1, 4, R("rusted_drum"), {"axis": "y"}); b.set(1, 1, 3, M("barrel"), {"facing": "up", "open": "false"})
    t = b.finalize(VARIANT)
    for y in range(0, b.t.sy - 1): b.set(1, y, 1, R("sooty_brick") if y % 4 else R("riveted_rusted_plating"))   # smokestack
    b.set(1, b.t.sy - 1, 1, R("caged_lamp"), {"facing": "up", "lit": "false"})
    return t

def watchpost(site):
    b = mk(site, "watchpost", 5, 10, 6, 7); b.ground(GROUND[site])
    box(b, 0, 4, 0, 4, 6, door_x=2, windows=False)
    b.window(0, 4, 2, "west"); b.window(4, 4, 2, "east"); b.window(2, 4, 0, "north")
    for y in range(1, 7): b.set(1, y, 2, M("ladder"), {"facing": "east", "waterlogged": "false"})
    for x in range(1, 4):
        for z in range(1, 4):
            if (x, z) != (1, 2): b.role(x, 6, z, "floor")
    for x in range(5):
        for z in range(5):
            if x in (0, 4) or z in (0, 4): b.set(x, 7, z, M(f"{WOOD[site]}_fence") if (x + z) % 2 == 0 else M("air"))
    b.set(3, 7, 3, M(LIGHT[site]), {"hanging": "false", "waterlogged": "false"})
    front(b, 4, 2); return b.finalize(VARIANT)

def wall_end(site):
    t = Tpl(7, 6, 1); side = SIDE[site]
    wall = {"gate_end": "cobbled_deepslate_wall", "gate_nether": "blackstone_wall", "nether": "nether_brick_fence", "end": "end_stone_brick_wall"}[site]
    post = {"gate_end": "deepslate_bricks", "gate_nether": "nether_bricks", "nether": "nether_bricks", "end": "purpur_block"}[site]
    for x in range(7):
        t.set(x, 0, 0, M(GROUND[site][1]))
        if x in (0, 6):
            for y in (1, 2, 3): t.set(x, y, 0, M(post))
            t.set(x, 4, 0, M(LIGHT[site]), {"hanging": "false", "waterlogged": "false"})
        elif x == 3: t.set(x, 1, 0, M("jigsaw"), {"orientation": "north_up"}, {"id": M("jigsaw"), "name": "minecraft:street", "target": "minecraft:street",
                                                                                "pool": "minecraft:empty", "final_state": M("iron_bars") if side == "end" else M(f"{WOOD[site]}_fence_gate"), "joint": "aligned"})
        else: t.set(x, 1, 0, M(wall)); t.set(x, 2, 0, M(wall))
    fix_connections(t); return t

# ---------------- streets (9-3 generator, per-site palette) ----------------
SPAL = {
    "gate_end": {"verge": ["grass_block", "coarse_dirt"], "edge": ["gravel", "coarse_dirt", "cobbled_deepslate"], "inner": ["deepslate_bricks", "cobbled_deepslate"],
                 "centre": ["polished_deepslate", "deepslate_tiles", "end_stone_bricks", "cobbled_deepslate"], "fence": "dark_oak_fence", "hedge": "oak_leaves",
                 "flowers": ["allium", "azure_bluet", "lily_of_the_valley"], "props": [("barrel", {"facing": "up", "open": "false"}), ("composter", {"level": "0"})]},
    "gate_nether": {"verge": ["grass_block", "coarse_dirt"], "edge": ["gravel", "netherrack", "coarse_dirt"], "inner": ["blackstone", "nether_bricks"],
                    "centre": ["polished_blackstone_bricks", "nether_bricks", "blackstone", "cobblestone"], "fence": "crimson_fence", "hedge": None,
                    "flowers": ["crimson_roots", "warped_roots", "poppy"], "props": [("barrel", {"facing": "up", "open": "false"}), ("magma_block", None)]},
    "nether": {"verge": ["nether_bricks", "red_nether_bricks"], "edge": ["nether_bricks", "polished_blackstone_bricks", "blackstone"], "inner": ["polished_blackstone", "nether_bricks"],
               "centre": ["polished_blackstone_bricks", "nether_bricks", "cracked_polished_blackstone_bricks", "blackstone"], "fence": "nether_brick_fence", "hedge": None,
               "flowers": ["nether_brick_fence"], "props": [("nether_brick_fence", None)]},
    "end": {"verge": ["end_stone_bricks", "obsidian"], "edge": ["end_stone_bricks", "purpur_block", "end_stone"], "inner": ["purpur_block", "end_stone_bricks"],
            "centre": ["purpur_block", "end_stone_bricks", "obsidian", "end_stone_bricks"], "fence": "iron_bars", "hedge": None,
            "flowers": ["iron_bars"], "props": [("iron_bars", None)]},
}
_base_props = G.verge_props
def streets(site):
    side = SIDE[site]; G.FAMILY = f"station_{site}"; G.ABANDONED = VARIANT == "ruined"; G.PAL = SPAL[site]   # derelict: unlit post stubs
    G.street_j = lambda t, x, z, ori: G.jig(t, x, 1, z, ori, "minecraft:street", f"{SJ(site)}/streets")
    G.plot_j = lambda t, x, z, ori: G.jig(t, x, 1, z, ori, "minecraft:building_entrance", f"{SJ(site)}/buildings")
    G.decor_j = lambda t, x, z: None
    def vp(t, r, x, z, n):
        if side in ("nether", "end"): t.set(x, 1, z, M(G.PAL["fence"]))          # causeway / walkway railing
        elif n < -.5 and r.random() < .25: t.set(x, 1, z, r.choice([R("rusted_drum"), R("weathered_wooden_crate")]))
        else: _base_props(t, r, x, z, n)
    G.verge_props = vp
    out = [("straight16_1", G.straight(16, 1), 5), ("straight16_2", G.straight(16, 2), 5), ("straight10_1", G.straight(10, 3), 3),
           ("cross_1", G.junction("cross", 1), 1), ("tee_1", G.junction("tee", 1), 3), ("corner_1", G.junction("corner", 1), 3), ("end_1", G.junction("end", 1), 1)]
    if LIGHT[site] != "lantern":
        for _, t, _ in out:
            for p, (n, pr, nb) in list(t.b.items()):
                if n == M("lantern"): t.b[p] = (M(LIGHT[site]), pr, nb)
    G.verge_props = _base_props; G.ABANDONED = False
    return out

def pe(loc, wt, proj="rigid"): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": proj}}

DERELICT_SPAWNS = {
    "gate_end": [("zombie", 3, 1, 3), ("skeleton", 3, 1, 2), ("enderman", 1, 1, 1)],
    "gate_nether": [("zombie", 3, 1, 3), ("skeleton", 2, 1, 2), ("zombified_piglin", 2, 1, 3)],
    "nether": [("zombie", 3, 2, 4), ("skeleton", 3, 1, 3), ("wither_skeleton", 2, 1, 2)], "end": []}

def build(site):
    d = OUT / f"structure/station/{site}{SUFFIX}"
    if d.exists():
        for old in d.rglob("*.nbt"): old.unlink()
    (d / "streets").mkdir(parents=True, exist_ok=True)
    loc = lambda n: f"{SJ(site)}/{n}"
    t = hall(site); connect_pipes(t); (d / "hall.nbt").write_bytes(t.bytes())
    blds = [("workshop", workshop, 3), ("garden", garden, 2), ("library", library, 2), ("quarters", quarters, 3),
            ("storehouse", storehouse, 3), ("boiler", boiler, 2), ("watchpost", watchpost, 2)]
    for n, fn, _ in blds:
        t = fn(site); connect_pipes(t); (d / f"{n}.nbt").write_bytes(t.bytes())
    st = streets(site); proj = "rigid" if SIDE[site] == "nether" else "terrain_matching"
    for n, t, _ in st: (d / f"streets/{n}.nbt").write_bytes(t.bytes())
    (d / "wall_end.nbt").write_bytes(wall_end(site).bytes())
    P = OUT / f"worldgen/template_pool/station/{site}{SUFFIX}"; P.mkdir(parents=True, exist_ok=True)
    for old in P.glob("*.json"): old.unlink()
    w(P / "hall.json", {"fallback": "minecraft:empty", "elements": [pe(loc("hall"), 1)]})
    w(P / "buildings.json", {"fallback": "minecraft:empty", "elements": [pe(loc(n), wt) for n, _, wt in blds]})
    w(P / "streets.json", {"fallback": f"{SJ(site)}/ends", "elements": [pe(loc(f"streets/{n}"), wt, proj) for n, _, wt in st]})
    w(P / "ends.json", {"fallback": "minecraft:empty", "elements": [pe(loc("wall_end"), 1, proj)]})
    base = json.loads((OUT / f"worldgen/structure/research_{site}.json").read_text())
    base.update({"start_pool": f"{SJ(site)}/hall", "size": 4, "max_distance_from_center": 56, "terrain_adaptation": "beard_box"})
    if site == "nether": base["start_height"] = {"type": "minecraft:uniform", "min_inclusive": {"absolute": 40}, "max_inclusive": {"absolute": 70}}
    if SUFFIX:
        sp = DERELICT_SPAWNS[site]
        base["spawn_overrides"] = {"monster": {"bounding_box": "piece", "spawns": [{"type": f"minecraft:{m}", "weight": wt, "minCount": a, "maxCount": b} for m, wt, a, b in sp]}} if sp else {}
    w(OUT / f"worldgen/structure/research_{site}{SUFFIX}.json", base)

def main():
    global SUFFIX, VARIANT
    for SUFFIX, VARIANT in (("", "lived"), ("_derelict", "ruined")):
        for site in SITES: build(site)
    SUFFIX, VARIANT = "", "lived"
    print("9-15b/9-23: 4 research stations + 4 rare derelict variants (ruined finish, unlit streets, undead)")

if __name__ == "__main__":
    main()
