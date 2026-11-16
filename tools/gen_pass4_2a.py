#!/usr/bin/env python3
"""
gen_pass4_2a.py - pass 4-2a: INDUSTRIAL MINESHAFT (mineshaft replacement), core kit. Safe to re-run.

Procedural jigsaw network (like vanilla mineshafts) built from script-written NBT:
  tunnels : 9x8xL concrete shells, interior 7 wide x 6 high (room for Create trains), tracks (create:track) on some straights
            straight_track/straight_plain (15 long), straight_door (13 wide: side alcoves that accept rooms), corner, tee, hub (13x13, start piece), cap (dead end)
  rooms   : storage_closet (barrels with loot, Rust and Rebar crates = decoration only)
Connectors: all tunnel openings sit at local y=3 centre of the face (name/target `dying_world:tunnel`); room doors at y=2 (`dying_world:room_door`).
Every jigsaw final_state = air. Pool fallback of `tunnels` = dead-end caps (used at max depth / when nothing fits).
EFFICIENCY (avoid cascading chunk generation): jigsaw `size` 10, `max_distance_from_center` 112 (<8 chunks), no heightmap projection (fixed Y range),
  terrain_adaptation none, step underground_structures, rare random_spread (30/10, frequency 0.6), shells are closed (no holes into caves/water).
NOTE (4-2s): the structure json/start pool/set written here are OVERRIDDEN by gen_pass4_2s.py (central shaft). Run order: 2a, 2b, 2c, 2s.
Files: structure/mineshaft/*.nbt, worldgen/template_pool/mineshaft/*.json, worldgen/structure/industrial_mineshaft.json,
  worldgen/structure_set/industrial_mineshafts.json, tags/.../has_structure/industrial_mineshaft.json, loot_table/chests/mineshaft_storage.json
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import biome_tags as bt
from nbtw import Tpl
from rr_connect import connect

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "datapack/data/dying_world"
M = lambda n: "minecraft:" + n
R = lambda n: "rustandrebar:" + n
TUN, DOOR = "dying_world:tunnel", "dying_world:room_door"
H = 8
CRATES = [R("rusted_steel_crate"), R("wire_mesh_crate"), R("weathered_wooden_crate"), R("rotting_wooden_crate")]

def wall(r):
    p = r.random()
    return R("rebar_concrete") if p < .5 else R("weathered_concrete") if p < .88 else R("sooty_brick") if p < .94 else R("rusted_plating")

def jig(t, x, y, z, facing, name, pool):
    t.set(x, y, z, M("jigsaw"), {"orientation": facing + "_up"},
          {"id": M("jigsaw"), "name": name, "target": name, "pool": pool, "final_state": M("air"), "joint": "aligned"})

def lamp(t, r, x, y, z):
    # ONE r.random() call (keeps every piece's random stream identical to 4-2a). Mix: 12% flickering batten, 23% hanging bulb (lit),
    # rest caged lamps of which ~60% lit (the rest dead = dying world). Models checked in the R&R jar: lit=true/false have separate on/off models.
    p = r.random()
    if p < .12:
        t.set(x, y, z, R("fluorescent_batten"), {"axis": "x", "facing": "down", "lit": "true", "flickering": "true", "dark": "false"})
    elif p < .35:
        t.set(x, y, z, R("hanging_bulb"), {"lit": "true"})
    else:
        t.set(x, y, z, R("caged_lamp"), {"facing": "down", "lit": "true" if (p - .35) / .65 < .6 else "false"})

def barrel(t, x, y, z):
    t.set(x, y, z, M("barrel"), {"facing": "up", "open": "false"}, {"id": M("barrel"), "LootTable": "dying_world:chests/mineshaft_storage"})

def box_piece(w, l, faces, seed, name, track=False, door=False, ribs=(), pillars=False, cap=False):
    r = random.Random(zlib.crc32(name.encode()) + seed)
    pad = 2 if door else 0
    t = Tpl(w + 2 * pad, H, l); ox = pad; cx, cz = w // 2, l // 2
    for x in range(w):
        for z in range(l):
            for y in range(H):
                inside = 0 < x < w - 1 and 0 < y < H - 1 and 0 < z < l - 1
                if inside: t.set(ox + x, y, z, M("air"))
                elif y == 0:
                    p = r.random(); hz = abs(x - cx) == 2 and track
                    t.set(ox + x, y, z, R("hazard_plating") if hz and p < .35 else R("weathered_concrete") if p < .65 else R("rebar_concrete") if p < .88 else R("tread_plate"))
                else: t.set(ox + x, y, z, wall(r))
    for f in faces:                                   # 7x6 openings + connectors
        if f in "NS":
            z0 = 0 if f == "N" else l - 1
            for x in range(cx - 3, cx + 4):
                for y in range(1, 7): t.set(ox + x, y, z0, M("air"))
            jig(t, ox + cx, 3, z0, "north" if f == "N" else "south", TUN, "dying_world:mineshaft/tunnels")
        else:
            x0 = 0 if f == "W" else w - 1
            for z in range(cz - 3, cz + 4):
                for y in range(1, 7): t.set(ox + x0, y, z, M("air"))
            jig(t, ox + x0, 3, cz, "west" if f == "W" else "east", TUN, "dying_world:mineshaft/tunnels")
    if door:                                          # side alcoves: 3x4 opening, 2 deep, jigsaw at outer edge
        dz = cz
        for side, d, wx in (("W", -1, ox), ("E", 1, ox + w - 1)):
            for z in range(dz - 1, dz + 2):
                for y in range(1, 5): t.set(wx, y, z, M("air"))
            for k in (1, 2):
                for z in range(dz - 2, dz + 3):
                    for y in range(0, 6):
                        t.set(wx + d * k, y, z, M("air") if (1 <= y <= 4 and abs(z - dz) <= 1) else wall(r))
            jig(t, wx + 2 * d, 2, dz, "west" if side == "W" else "east", DOOR, "dying_world:mineshaft/rooms")
    if track:
        for z in range(l): t.set(ox + cx, 1, z, "create:track", {"shape": "zo"})
    for z in ribs:                                    # reinforcing ribs: full-height girder posts + main beam BETWEEN them (ends connect as 'column') + lamp
        for x in range(2, w - 2): t.set(ox + x, 6, z, R("rusted_beam"), {"axis": "x"})
        for x in (1, w - 2):
            for y in range(1, 7): t.set(ox + x, y, z, R("rusted_girder"), {"axis": "y"})
        lamp(t, r, ox + cx, 5, z)
    rs = sorted(ribs)                                 # sub girders along the ceiling centre, butting into the main beams ('flange' ends)
    for a, b in zip(rs, rs[1:]):
        for z in range(a + 1, b): t.set(ox + cx, 6, z, R("rusted_girder"), {"axis": "z"})
    if not ribs: lamp(t, r, ox + cx, 6, cz)
    if pillars:
        for x, z in ((2, 2), (w - 3, 2), (2, l - 3), (w - 3, l - 3)):
            for y in range(1, 7): t.set(ox + x, y, z, R("rusted_girder"), {"axis": "y"})
    for z in range(2, l - 2):                         # wall-side clutter + cobwebs, kept out of door zones
        if door and abs(z - cz) <= 2: continue
        for x in (1, w - 2):
            if not t.has(ox + x, 1, z) and r.random() < .03:
                t.set(ox + x, 1, z, r.choice([R("rusted_drum"), R("weathered_wooden_crate"), R("tar_leaking_drum"), R("wooden_pallet")]))
            if not t.has(ox + x, 6, z) and r.random() < .04: t.set(ox + x, 6, z, M("cobweb"))
    if cap:                                           # dead-end stash
        for i, x in enumerate(sorted(r.sample(range(2, w - 2), 3))):
            if r.random() < .6: barrel(t, ox + x, 1, l - 2)
            else: t.set(ox + x, 1, l - 2, r.choice(CRATES))
            if r.random() < .5: t.set(ox + x, 2, l - 2, r.choice(CRATES))
    return t

def closet(seed):
    r = random.Random(7000 + seed); t = Tpl(11, 6, 9)
    for x in range(11):
        for z in range(9):
            for y in range(6):
                inside = 0 < x < 10 and 0 < y < 5 and 0 < z < 8
                if inside: t.set(x, y, z, M("air"))
                elif y == 0: t.set(x, y, z, R("weathered_concrete") if r.random() < .6 else R("rebar_concrete"))
                else: t.set(x, y, z, wall(r))
    for x in range(4, 7):
        for y in range(1, 5): t.set(x, y, 0, M("air"))
    jig(t, 5, 2, 0, "north", DOOR, "minecraft:empty")
    for x in range(1, 10):                            # back wall: barrels (loot) + crates (decor)
        if r.random() < .65: barrel(t, x, 1, 7)
        elif r.random() < .6: t.set(x, 1, 7, r.choice(CRATES))
        if r.random() < .25: t.set(x, 2, 7, r.choice(CRATES))
    for z in range(2, 7):                             # side walls: crate stacks
        for x in (1, 9):
            if r.random() < .55:
                t.set(x, 1, z, r.choice(CRATES))
                if r.random() < .4: t.set(x, 2, z, r.choice(CRATES))
    for _ in range(r.randint(1, 3)):                  # loose pallets / drum in the middle
        x, z = r.randint(3, 7), r.randint(2, 6)
        if not t.has(x, 1, z) or t.b[(x, 1, z)][0] == M("air"): t.set(x, 1, z, r.choice([R("wooden_pallet"), R("rusted_drum")]))
    lamp(t, r, 5, 4, 4)
    return t

def w(p, o): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o, indent=2) + "\n")
NOFLOAT = "dying_world:mineshaft_no_float"
def elem(loc, weight, proc=NOFLOAT): return {"weight": weight, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:mineshaft/{loc}",
                                                            "processors": proc, "projection": "rigid"}}

def item(name, weight, lo=None, hi=None, worn=False, ns="minecraft"):
    e = {"type": "minecraft:item", "name": ns + ":" + name, "weight": weight, "functions": []}
    if lo is not None: e["functions"].append({"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}})
    if worn: e["functions"].append({"function": "minecraft:set_damage", "damage": {"type": "minecraft:uniform", "min": 0.25, "max": 0.8}})
    if not e["functions"]: del e["functions"]
    return e

def loot():
    rr = "rustandrebar"
    mats = [item("rebar_bundle", 6, 2, 8, ns=rr), item("rebar_concrete", 6, 8, 24, ns=rr), item("weathered_concrete", 5, 8, 24, ns=rr),
            item("rusted_plating", 4, 6, 16, ns=rr), item("tread_plate", 3, 4, 12, ns=rr), item("hazard_plating", 2, 4, 10, ns=rr),
            item("salvaged_steel_block", 2, 2, 6, ns=rr), item("firebrick", 3, 8, 16, ns=rr), item("sooty_brick", 3, 8, 16, ns=rr),
            item("caged_lamp", 2, 1, 3, ns=rr), item("bricks", 4, 8, 20), item("iron_bars", 3, 6, 14), item("obsidian", 2, 2, 6)]
    scrap = [item("iron_ingot", 8, 2, 6), item("iron_nugget", 6, 4, 14), item("copper_ingot", 6, 3, 8), item("coal", 7, 4, 12), item("redstone", 5, 4, 10),
             item("gunpowder", 3, 2, 5), item("string", 3, 2, 6), item("flint", 3, 2, 5), item("torch", 5, 4, 12), item("bucket", 2),
             item("bread", 3, 1, 3), item("iron_pickaxe", 2, worn=True), item("iron_shovel", 1, worn=True), item("gold_ingot", 2, 1, 3), item("diamond", 1, 1, 1)]
    w(OUT / "loot_table/chests/mineshaft_storage.json", {"pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": mats},
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": scrap}]})

def no_float():
    """Branch pieces never replace AIR/cave air already in the world (protected_blocks): where a branch would run through a cavern the part over
    open air is simply not built (collapsed gap) instead of a closed box hanging in the void. Water/lava are NOT protected (shell stays sealed)."""
    w(OUT / "tags/block/mineshaft_open.json", {"replace": False, "values": ["minecraft:air", "minecraft:cave_air", "minecraft:void_air"]})
    w(OUT / "worldgen/processor_list/mineshaft_no_float.json", {"processors": [{"processor_type": "minecraft:protected_blocks", "value": "#dying_world:mineshaft_open"}]})

def main():
    no_float()
    N = OUT / "structure/mineshaft"; N.mkdir(parents=True, exist_ok=True)
    kit = {}   # name -> Tpl
    for s in (1, 2):
        kit[f"straight_track_{s}"] = box_piece(9, 15, "NS", s, "straight_track", track=True, ribs=(2, 7, 12))
        kit[f"straight_plain_{s}"] = box_piece(9, 15, "NS", s, "straight_plain", ribs=(2, 7, 12) if s == 1 else (4, 10))
        kit[f"straight_door_{s}"] = box_piece(9, 15, "NS", s, "straight_door", track=(s == 1), door=True, ribs=(3, 11))
        kit[f"corner_{s}"] = box_piece(9, 9, "NE", s, "corner")
        kit[f"tee_{s}"] = box_piece(9, 9, "NSE", s, "tee")
        kit[f"hub_{s}"] = box_piece(13, 13, "NSEW", s, "hub", pillars=True)
        kit[f"cap_{s}"] = box_piece(9, 7, "N", s, "cap", cap=True, ribs=(3,))
    for s in (1, 2, 3): kit[f"storage_closet_{s}"] = closet(s)
    for n, t in kit.items(): connect(t); (N / f"{n}.nbt").write_bytes(t.bytes())
    P = OUT / "worldgen/template_pool/mineshaft"
    w(P / "start.json", {"fallback": "minecraft:empty", "elements": [elem("hub_1", 1), elem("hub_2", 1)]})
    wts = {"straight_track": 2, "straight_plain": 1, "straight_door": 2, "corner": 1, "tee": 1, "hub": 1}   # per variant (2 variants each)
    w(P / "tunnels.json", {"fallback": "dying_world:mineshaft/caps",
        "elements": [elem(f"{k}_{s}", v) for k, v in wts.items() for s in (1, 2)]})
    w(P / "caps.json", {"fallback": "minecraft:empty", "elements": [elem("cap_1", 1), elem("cap_2", 1)]})
    w(P / "rooms.json", {"fallback": "minecraft:empty", "elements": [elem(f"storage_closet_{s}", 1) for s in (1, 2, 3)] +
                         [{"weight": 3, "element": {"element_type": "minecraft:empty_pool_element"}}]})
    w(OUT / "worldgen/structure/industrial_mineshaft.json", {
        "type": "minecraft:jigsaw", "biomes": "#dying_world:has_structure/industrial_mineshaft", "max_distance_from_center": 112, "size": 10,
        "spawn_overrides": {}, "start_height": {"type": "minecraft:uniform", "min_inclusive": {"absolute": -48}, "max_inclusive": {"absolute": 16}},
        "start_pool": "dying_world:mineshaft/start", "step": "underground_structures", "terrain_adaptation": "none", "use_expansion_hack": False})
    R_ = bt.resolve
    skip = R_("minecraft:is_ocean") | R_("minecraft:is_deep_ocean") | R_("c:is_shallow_ocean") | R_("minecraft:is_river") | R_("minecraft:is_nether") | R_("minecraft:is_end") | \
           R_("c:is_cave") | R_("c:caves") | R_("c:is_mushroom") | {b for b in bt.ALL_BIOMES if any(k in b for k in ("cave", "deeps", "dripstone", "deep_dark", "void", "marker"))}
    land = [b for b in bt.ALL_BIOMES if b not in skip] + ["minecraft:lush_caves", "minecraft:dripstone_caves"]
    w(OUT / "tags/worldgen/biome/has_structure/industrial_mineshaft.json", {"replace": False, "values": [{"id": b, "required": False} for b in land]})
    w(OUT / "worldgen/structure_set/industrial_mineshafts.json", {
        "structures": [{"structure": "dying_world:industrial_mineshaft", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 30, "separation": 10, "frequency": 0.6,
                      "salt": zlib.crc32(b"dying_world:industrial_mineshafts") % 2000000000}})
    loot()
    print(f"mineshaft: {len(kit)} NBT pieces, {len(land)} biomes, spacing 30/10 freq .6, size 10, radius 112")

if __name__ == "__main__":
    main()
