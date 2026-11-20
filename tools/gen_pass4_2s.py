#!/usr/bin/env python3
"""
gen_pass4_2s.py - pass 4-2s: CENTRAL SHAFT for the industrial mineshaft (run AFTER gen_pass4_2a/2b/2c; overrides the start pool, structure json and set). Safe to re-run.

The mineshaft is now anchored on a vertical shaft: surface HEAD (headframe + control shed) -> COLLAR (solid 15x15 block under the head) ->
8 x SEGMENT (11x16x11, interior 9x9, ladder on the north wall, corner girders, wall lamps) -> CAP (sump with loot barrels). Segments with side openings
(E / S / W; north wall = ladder) carry a grate landing and a tunnel connector (`dying_world:tunnel`) that expands the old tunnel/hall/room network.
Facts / limits (vanilla jigsaw): the structure box is +-max_distance_from_center (128) around the START piece in all 3 axes, so with the head at the surface the shaft
reaches y = surface-128 (bedrock where the surface is <= ~64; in higher terrain the shaft ends above bedrock, bottom is natural rock). Caps are the fallback of the
`shaft` pool, tried when no full segment fits.
Vertical jigsaws: orientation up_north/down_north + joint `aligned` => every segment keeps the head's rotation, so the ladder stays on one wall.
Shaft pieces are NOT protected (they cross caverns as a tube); all branch pieces use dying_world:mineshaft_no_float (see gen_pass4_2a.no_float()).
Structure: start_height 0 + project_start_to_heightmap WORLD_SURFACE_WG, step surface_structures, size 14, max_distance 128, terrain_adaptation none.
Set: spacing 32 / separation 10 / frequency 0.5, 4 chunks from survivor villages.
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from rr_connect import connect
from gen_pass4_2a import M, R, TUN, wall, lamp, w, OUT, CRATES
from gen_pass4_2b import lbarrel

SHAFT, TUNPOOL, SHAFTPOOL = "dying_world:shaft", "dying_world:mineshaft/tunnels", "dying_world:mineshaft/shaft"
S, C, Y0, SEGH = 11, 5, 5, 16

def jigv(t, x, y, z, front, pool):
    t.set(x, y, z, M("jigsaw"), {"orientation": front + "_north"},
          {"id": M("jigsaw"), "name": SHAFT, "target": SHAFT, "pool": pool, "final_state": M("air"), "joint": "aligned"})
def jigh(t, x, y, z, facing):
    t.set(x, y, z, M("jigsaw"), {"orientation": facing + "_up"},
          {"id": M("jigsaw"), "name": TUN, "target": TUN, "pool": TUNPOOL, "final_state": M("air"), "joint": "aligned"})
def wlamp(t, r, x, y, z, facing): t.set(x, y, z, R("caged_lamp"), {"facing": facing, "lit": "true" if r.random() < .6 else "false"})
def ladder(t, x, z, y0, y1):
    for y in range(y0, y1 + 1): t.set(x, y, z, R("rusted_rung_ladder"), {"facing": "south"})
def floor_block(r):
    p = r.random(); return R("weathered_concrete") if p < .55 else R("rebar_concrete") if p < .85 else R("tread_plate")

def shell(t, r, h, solid_floor=False):
    for y in range(h):
        for x in range(S):
            for z in range(S):
                if 0 < x < S - 1 and 0 < z < S - 1: t.set(x, y, z, floor_block(r) if (solid_floor and y == 0) else M("air"))
                else: t.set(x, y, z, wall(r))
    for x, z in ((1, 1), (9, 1), (1, 9), (9, 9)):
        for y in range(h): t.set(x, y, z, R("rusted_girder"), {"axis": "y"})
    ladder(t, C, 1, 1 if solid_floor else 0, h - 1)

def lamps(t, r, h, openings):
    for y in (3, 11) if h >= 12 else (h // 2,):
        for f, (x, z, face) in {"N1": (3, 1, "south"), "N2": (7, 1, "south"), "W": (1, 5, "east"), "E": (9, 5, "west"), "S": (5, 9, "north")}.items():
            if f[0] in openings and Y0 <= y <= Y0 + 7: continue
            if t.b.get((x, y, z), ("",))[0] == M("air"): wlamp(t, r, x, y, z, face)

def segment(name, openings, seed):
    r = random.Random(zlib.crc32(name.encode()) + seed); t = Tpl(S, SEGH, S); shell(t, r, SEGH)
    if openings:                                    # landing level: full grate floor, only the ladder cell open
        for x in range(1, S - 1):
            for z in range(1, S - 1):
                if (x, z) in ((1, 1), (9, 1), (1, 9), (9, 9)) or (x, z) == (C, 1): continue
                t.set(x, Y0, z, R("rusted_grate"))
        for z in (3, 7):                                # support beams under the floor
            for x in range(2, S - 2): t.set(x, Y0 - 1, z, R("rusted_beam"), {"axis": "x"})
    for f in openings:
        if f in "EW":
            xw = S - 1 if f == "E" else 0
            for z in range(2, 9):
                for y in range(Y0 + 1, Y0 + 7): t.set(xw, y, z, M("air"))
            jigh(t, xw, Y0 + 3, C, "east" if f == "E" else "west")
        else:
            for x in range(2, 9):
                for y in range(Y0 + 1, Y0 + 7): t.set(x, y, S - 1, M("air"))
            jigh(t, C, Y0 + 3, S - 1, "south")
    lamps(t, r, SEGH, openings)
    jigv(t, C, SEGH - 1, C, "up", "minecraft:empty"); jigv(t, C, 0, C, "down", SHAFTPOOL)
    return t

def cap(name, h, seed):
    r = random.Random(zlib.crc32(name.encode()) + seed); t = Tpl(S, h, S); shell(t, r, h, solid_floor=True)
    if h >= 8: lamps(t, r, h, "")
    for x, z in ((2, 8), (8, 8), (3, 8)):                       # sump: loot barrels + crates + oil
        if r.random() < .6: lbarrel(t, x, 1, z, r.choice(["mineshaft_storage", "mineshaft_workshop", "mineshaft_stash", "mineshaft_fuel"]))
        else: t.set(x, 1, z, r.choice(CRATES))
    for _ in range(6):
        x, z = r.randint(2, 8), r.randint(2, 8)
        if t.b.get((x, 1, z), ("",))[0] == M("air"): t.set(x, 1, z, R("oil_puddle"))
    jigv(t, C, h - 1, C, "up", "minecraft:empty")
    return t

def collar(seed):
    r = random.Random(7700 + seed); t = Tpl(15, 10, 15)
    for y in range(10):
        for x in range(15):
            for z in range(15):
                hole = 3 <= x <= 11 and 3 <= z <= 11
                t.set(x, y, z, M("air") if hole else wall(r))
    for x, z in ((3, 3), (11, 3), (3, 11), (11, 11)):
        for y in range(10): t.set(x, y, z, R("rusted_girder"), {"axis": "y"})
    ladder(t, 7, 3, 0, 9)
    jigv(t, 7, 9, 7, "up", "minecraft:empty"); jigv(t, 7, 0, 7, "down", SHAFTPOOL)
    return t

def head(seed):
    r = random.Random(8800 + seed); W, D, HT = 23, 17, 15; t = Tpl(W, HT, D)
    for x in range(W):
        for z in range(D):
            t.set(x, 0, z, floor_block(r))
            for y in range(1, HT): t.set(x, y, z, M("air"))                       # carve the box (hillsides)
    for x in range(4, 13):
        for z in range(4, 13): t.set(x, 0, z, M("air"))                           # shaft opening 9x9
    for x in range(2, 15):                                                         # hazard stripes around the opening
        for z in (2, 14): t.set(x, 0, z, R("hazard_plating")) if r.random() < .5 else None
    for z in range(2, 15):
        for x in (2, 14): t.set(x, 0, z, R("hazard_plating")) if r.random() < .5 else None
    for i in range(3, 14):                                                         # low curb ring (slabs), gap at the ladder exit
        for x, z in ((i, 3), (i, 13), (3, i), (13, i)):
            if z == 3 and 7 <= x <= 9: continue
            t.set(x, 1, z, R("rusted_plating_slab"), {"type": "bottom"})
    ladder(t, 8, 4, 0, 2)
    for x, z in ((3, 3), (13, 3), (3, 13), (13, 13)):                             # headframe legs + top frame
        for y in range(1, 13): t.set(x, y, z, R("rusted_girder"), {"axis": "y"})
    # girders are the big members (legs, top ring), beams the small ones (the cross member); pass 9-81
    for x in range(4, 13):
        for z in (3, 13): t.set(x, 12, z, R("rusted_girder"), {"axis": "x"})
        end = {"neg": "girder"} if x == 4 else {"pos": "girder"} if x == 12 else {}
        t.set(x, 12, 8, R("rusted_beam"), {"axis": "x", "low": "true", **end})   # low: flush with the block's bottom
    for z in range(4, 13):
        for x in (3, 13): t.set(x, 12, z, R("rusted_girder"), {"axis": "z"})
    t.set(8, 11, 8, R("pulley_block"), {"facing": "south"})
    lamp(t, r, 5, 11, 8); lamp(t, r, 11, 11, 8)                                    # hung from the cross beam
    for x in range(15, 22):                                                         # control shed x15..21 z4..12, h 4, roof y5
        for z in range(4, 13):
            for y in range(1, 6):
                edge = x in (15, 21) or z in (4, 12)
                if y == 5: t.set(x, y, z, R("corrugated_rusted_metal"))
                elif edge: t.set(x, y, z, R("corrugated_rusted_metal") if r.random() < .8 else R("riveted_rusted_plating"))
    for z in (7, 8):
        for y in range(1, 4): t.set(15, y, z, M("air"))                           # door (west wall, faces the shaft)
    for x, z in ((17, 4), (19, 4), (17, 12), (19, 12)): t.set(x, 3, z, R("broken_factory_window"))
    lbarrel(t, 20, 1, 6, "mineshaft_workshop"); lbarrel(t, 20, 1, 7, "mineshaft_office")
    for x, y, z in ((20, 1, 10), (20, 2, 10), (19, 1, 11), (17, 1, 11)): t.set(x, y, z, r.choice(CRATES))
    t.set(20, 3, 9, R("sign_danger"), {"facing": "west"}); wlamp(t, r, 18, 4, 8, "down")
    for x, z in ((16, 5), (20, 11), (16, 11)): t.set(x, 4, z, M("cobweb"))
    for _ in range(10):                                                              # outside clutter
        x, z = r.randint(1, W - 2), r.randint(1, D - 2)
        if t.b.get((x, 1, z), ("",))[0] == M("air") and not (2 <= x <= 14 and 2 <= z <= 14) and not (14 <= x <= 22 and 3 <= z <= 13):
            t.set(x, 1, z, r.choice(CRATES + [R("rusted_drum"), R("tar_leaking_drum"), R("wooden_pallet")]))
    jigv(t, 8, 0, 8, "down", "dying_world:mineshaft/shaft_collar")
    return t

def pool(name, elements, fallback="minecraft:empty"):
    w(OUT / f"worldgen/template_pool/mineshaft/{name}.json", {"fallback": fallback, "elements": elements})
def pe(loc, weight): return elem(loc, weight, "minecraft:empty")
from gen_pass4_2a import elem

# 4-2c3: undead-only natural spawns inside the mineshaft pieces (replaces the biome monster list; normal light/mob-cap rules).
# husk/stray skipped (their spawn rules need sky). drowned only spawn in water (flooded variants later).
SPAWNS = {"monster": {"bounding_box": "piece", "spawns": [
    {"type": "minecraft:zombie", "weight": 100, "minCount": 2, "maxCount": 4},
    {"type": "minecraft:skeleton", "weight": 80, "minCount": 1, "maxCount": 3},
    {"type": "minecraft:zombie_villager", "weight": 25, "minCount": 1, "maxCount": 2},
    {"type": "minecraft:drowned", "weight": 15, "minCount": 1, "maxCount": 3}]}}

def main():
    N = OUT / "structure/mineshaft"; kit = {}
    for s in (1, 2): kit[f"shaft_head_{s}"] = head(s)
    kit["shaft_collar_1"] = collar(1)
    variants = {"plain_1": ("", 1), "plain_2": ("", 2), "branch_s": ("S", 1), "branch_e": ("E", 1), "branch_w": ("W", 1), "branch_ew": ("EW", 1), "branch_esw": ("EWS", 1)}
    for k, (op, sd) in variants.items(): kit[f"shaft_{k}"] = segment(f"shaft_{k}", op, sd)
    for h in (16, 8, 4): kit[f"shaft_cap_{h}"] = cap(f"shaft_cap_{h}", h, h)
    for n, t in kit.items(): connect(t); (N / f"{n}.nbt").write_bytes(t.bytes())
    pool("start", [pe("shaft_head_1", 1), pe("shaft_head_2", 1)])
    pool("shaft_collar", [pe("shaft_collar_1", 1)])
    wt = {"plain_1": 3, "plain_2": 3, "branch_s": 2, "branch_e": 1, "branch_w": 1, "branch_ew": 2, "branch_esw": 1}
    pool("shaft", [pe(f"shaft_{k}", v) for k, v in wt.items()], fallback="dying_world:mineshaft/shaft_caps")
    pool("shaft_caps", [pe("shaft_cap_16", 2), pe("shaft_cap_8", 2), pe("shaft_cap_4", 1)])
    w(OUT / "worldgen/structure/industrial_mineshaft.json", {
        "type": "minecraft:jigsaw", "biomes": "#dying_world:has_structure/industrial_mineshaft", "max_distance_from_center": 128, "size": 14,
        "spawn_overrides": SPAWNS, "start_height": {"absolute": 0}, "project_start_to_heightmap": "WORLD_SURFACE_WG",
        "start_pool": "dying_world:mineshaft/start", "step": "surface_structures", "terrain_adaptation": "none", "use_expansion_hack": False})
    w(OUT / "worldgen/structure_set/industrial_mineshafts.json", {
        "structures": [{"structure": "dying_world:industrial_mineshaft", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 32, "separation": 10, "frequency": 0.5,
                      "salt": zlib.crc32(b"dying_world:industrial_mineshafts") % 2000000000,
                      "exclusion_zone": {"other_set": "dying_world:survivor_villages", "chunk_count": 4}}})
    print(f"4-2s: {len(kit)} shaft pieces (head x2, collar, {len(variants)} segments, 3 caps); size 14, radius 128, surface start, set 32/10 freq .5")

if __name__ == "__main__":
    main()
