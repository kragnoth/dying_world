#!/usr/bin/env python3
"""
gen_pass9_36.py - pass 9-36: SCULK RESEARCH SITE REBUILT as an abandoned dig camp in an open cavern
(user: it read as a 'weird sci-fi horror show'; wanted abandoned research buildings + mining shacks + sculk, built up over time then abandoned).
User choices: OPEN CAVERN, only a FEW VEINS at the edges, keep the HALF-BURIED ANCIENT GATE as the centrepiece.
Run AFTER gen_pass9_12 / 9_35 (it replaces 9-12's sculk station), before 9_16. Safe to re-run.

Layout (jigsaw, terrain_adaptation beard_box -> the ground is carved into a cavern around every piece, like the ancient city):
  pit (start, 27x16x27): the find. A 15x15 excavation 4 deep with a terrace rim, the reinforced-deepslate gate half-buried in a sculk mound,
       scaffolding towers, cut stairs, rails, dead caged lamps, and the Guild survey desk with the ARCHIVE chest (Listening Post Transcript, guaranteed).
  walkways = the camp 'streets': timber-framed mine tracks (spruce posts + beams, boardwalk, rails). walk_inner (ring 1) -> walk_outer -> ...,
       ends fall back to a mine drift dug into the rock. Side jigsaws open the buildings pool of the same ring.
  buildings (story layers): prospector shack, bunkhouse, cook shack, tool shed (camp: planks + corrugated metal), Listening Post + lab
       (Guild: stone brick / cobbled deepslate, copper roof), mine drift (oldest: timber portal into the rock).
  SCULK GRADIENT by ring: pit = heavy (blocks turned to sculk, veins, sensors, shriekers that CAN summon the warden, catalyst at the gate);
       inner ring = some sculk, veins, the odd sensor; outer ring = a few veins only.
Footings (pass 9-76): walkways, drifts and buildings stand on spruce posts + rubble, 10 deep (tools/footing.py).
Loot: the old research_sculk_* tables (ancient-city based; archive/store hand-tuned in user_overrides).
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl, S as NS, B as NB, I as NI
from gen_pass4_2a import M, R, w, OUT
from gen_pass9_11 import pe
from buildkit import rng, chest, bed, full
from footing import add_footing

ROOT_NS = "dying_world"; D = OUT / "structure/sculk_camp"; TP = OUT / "worldgen/template_pool/sculk_camp"; POOL = f"{ROOT_NS}:sculk_camp"
STREET, BLD = f"{ROOT_NS}:camp_street", f"{ROOT_NS}:camp_bld"
FALSE = "false"
def jig(t, x, y, z, orient, name, pool, final):
    t.set(x, y, z, M("jigsaw"), {"orientation": orient}, {"id": M("jigsaw"), "name": name, "target": name, "pool": pool, "final_state": final, "joint": "aligned"})

def pick(r, opts):
    tot = sum(wt for _, wt in opts); x = r.random() * tot
    for n, wt in opts:
        x -= wt
        if x < 0: return n
    return opts[-1][0]

FOOTING = 10
FOOT_FILL = [(M("cobbled_deepslate"), 5), (M("deepslate"), 3), (M("tuff"), 2), (M("cobblestone"), 1)]
STONE = [(M("cobbled_deepslate"), 5), (M("deepslate"), 3), (M("tuff"), 1), (M("gravel"), 1)]
BOARD = [(M("spruce_planks"), 6), (M("stripped_spruce_log"), 1), (M("dark_oak_planks"), 1)]
MASON = [(M("stone_bricks"), 4), (M("cracked_stone_bricks"), 2), (M("cobbled_deepslate"), 3), (M("mossy_stone_bricks"), 1)]
VEIN = (M("sculk_vein"), {"down": "true", "up": FALSE, "north": FALSE, "south": FALSE, "east": FALSE, "west": FALSE, "waterlogged": FALSE})
LEVEL = {"outer": dict(conv=0, vein=.05, sensor=0, shriek=0), "inner": dict(conv=.12, vein=.10, sensor=.015, shriek=0),
         "pit": dict(conv=.40, vein=.15, sensor=.025, shriek=.008)}
SKIP = {M("jigsaw"), M("chest"), M("barrel"), M("lectern"), M("scaffolding"), M("rail"), M("reinforced_deepslate"), M("sculk_catalyst"),
        M("calibrated_sculk_sensor"), M("sculk_sensor"), M("crafting_table"), M("smoker"), M("brewing_stand"), M("grindstone"), M("honeycomb_block")}

def sculk(t, r, level, area=None):
    L = LEVEL[level]
    for (x, y, z), (n, pr, nb) in list(t.b.items()):
        if n in SKIP or n.startswith("rustandrebar") or not full(n) or (area and not area(x, z)): continue
        above = t.b.get((x, y + 1, z))
        if above and above[0] != M("air"): continue
        q = r.random()
        if q < L["conv"]: t.set(x, y, z, M("sculk"))
        if y + 1 >= t.sy: continue
        q = r.random()
        if q < L["vein"]: t.set(x, y + 1, z, *VEIN)
        elif q < L["vein"] + L["sensor"]: t.set(x, y + 1, z, M("sculk_sensor"), {"power": "0", "sculk_sensor_phase": "inactive", "waterlogged": FALSE})
        elif q < L["vein"] + L["sensor"] + L["shriek"]: t.set(x, y + 1, z, M("sculk_shrieker"), {"can_summon": "true", "shrieking": FALSE, "waterlogged": FALSE})

def dead_lamp(t, x, y, z, facing="down"): t.set(x, y, z, R("caged_lamp"), {"facing": facing, "lit": FALSE})
def save(t, name):
    D.mkdir(parents=True, exist_ok=True); (D / f"{name}.nbt").write_bytes(t.bytes()); return f"{POOL}/{name}"

# ------------------------------------------------------------------ the pit (start)
def pit():
    S, H = 27, 16; t = Tpl(S, H, S); r = rng("sculk_camp/pit", 1)
    inside = lambda x, z: 6 <= x <= 20 and 6 <= z <= 20
    for x in range(S):
        for z in range(S):
            if inside(x, z):
                t.set(x, 0, z, pick(r, STONE))
                for y in range(1, 9): t.set(x, y, z, M("air"))
            else:
                for y in range(0, 4): t.set(x, y, z, pick(r, STONE))
                t.set(x, 4, z, pick(r, BOARD) if (abs(x - 13) <= 1 or abs(z - 13) <= 1) else pick(r, STONE))   # plank paths to the 4 exits
                for y in range(5, 10): t.set(x, y, z, M("air"))
    # cut stairs down on the south side, terrace steps on the north
    for i, z in enumerate(range(21, 17, -1)):
        for x in (12, 13, 14):
            t.set(x, 4 - i, z, M("cobbled_deepslate_stairs"), {"facing": "south", "half": "bottom", "shape": "straight", "waterlogged": FALSE})
            for y in range(5 - i, 9): t.set(x, y, z, M("air"))
            for y in range(0, 4 - i): t.set(x, y, z, M("cobbled_deepslate"))
    # the half-buried gate: a sculk/deepslate mound, frame x9..17 on z13, only the upper half shows
    for x in range(8, 19):
        for z in range(10, 17):
            h = 2 if 9 <= x <= 17 and 11 <= z <= 15 else 1
            for y in range(1, h + 1): t.set(x, y, z, M("sculk") if r.random() < .55 else M("deepslate"))
    for y in range(1, 8):
        for x in (9, 17): t.set(x, y, 13, M("reinforced_deepslate"))
    for x in range(9, 18): t.set(x, 7, 13, M("reinforced_deepslate"))
    for x in range(10, 17):
        for y in range(3, 7): t.set(x, y, 13, M("air"))
    t.set(13, 3, 12, M("sculk_catalyst"), {"bloom": FALSE})
    # scaffolding towers + a rope-and-bucket hoist, rails along the rim, dead lamps on posts
    for x, z in ((7, 7), (19, 19), (19, 7)):
        for y in range(1, 6): t.set(x, y, z, M("scaffolding"), {"bottom": FALSE, "distance": "0", "waterlogged": FALSE})
    for z in range(2, 25): t.set(2, 5, z, M("rail"), {"shape": "north_south", "waterlogged": FALSE})
    for x, z in ((4, 4), (22, 4), (4, 22), (22, 22), (13, 4), (4, 13), (22, 13)):
        for y in range(5, 8): t.set(x, y, z, M("spruce_fence"), {"north": FALSE, "south": FALSE, "east": FALSE, "west": FALSE, "waterlogged": FALSE})
        dead_lamp(t, x, 8, z, "up")
    # the Guild survey desk (NE rim): archive chest, lectern, a crate of wax
    for x in range(20, 26):
        for y in range(5, 9):
            if x in (20, 25): t.set(x, y, 1, M("spruce_log"), {"axis": "y"}); t.set(x, y, 5, M("spruce_log"), {"axis": "y"})
    for x in range(20, 26):
        for z in range(1, 6): t.set(x, 9, z, R("corrugated_rusted_metal_slab"), {"type": "bottom", "paint": "brown", "coat": "weathered"})
    chest(t, 22, 5, 2, "south", "research_sculk_archive")
    t.set(24, 5, 2, M("lectern"), {"facing": "south", "has_book": FALSE, "powered": FALSE})
    t.set(23, 5, 2, M("calibrated_sculk_sensor"), {"facing": "south", "power": "0", "sculk_sensor_phase": "inactive", "waterlogged": FALSE})
    t.set(21, 5, 4, R("weathered_wooden_crate")); t.set(24, 5, 4, M("barrel"), {"facing": "up", "open": FALSE})
    # exits to the walkways (rim floor level y4)
    jig(t, 13, 4, 0, "north_up", STREET, f"{POOL}/walk_inner", M("spruce_planks"))
    jig(t, 0, 4, 13, "west_up", STREET, f"{POOL}/walk_inner", M("spruce_planks"))
    jig(t, 26, 4, 13, "east_up", STREET, f"{POOL}/walk_inner", M("spruce_planks"))
    jig(t, 13, 4, 26, "south_up", STREET, f"{POOL}/walk_inner", M("spruce_planks"))
    sculk(t, r, "pit", inside); sculk(t, r, "inner", lambda x, z: not inside(x, z))
    return save(t, "pit")

# ------------------------------------------------------------------ walkways (camp streets)
def walk(name, L, ring, sides, seed):
    t = Tpl(7, 7, L); r = rng(f"sculk_camp/{name}", seed)
    nxt = f"{POOL}/walk_outer"; bld = f"{POOL}/bld_{ring}"
    for z in range(L):
        for x in range(7):
            t.set(x, 0, z, pick(r, BOARD) if 2 <= x <= 4 else pick(r, STONE))
            for y in range(1, 6): t.set(x, y, z, M("air"))
        t.set(5, 1, z, M("rail"), {"shape": "north_south", "waterlogged": FALSE})
        if z % 5 == 2:                                                        # timber frame: posts + cap beam
            for x in (0, 6):
                for y in range(1, 5): t.set(x, y, z, M("spruce_log"), {"axis": "y"})
            for x in range(7): t.set(x, 5, z, M("stripped_spruce_log"), {"axis": "x"})
            if r.random() < .6: dead_lamp(t, 3, 4, z)
    if L > 9 and r.random() < .7: t.set(4, 1, L // 2 + 1, R("rusted_drum"), {"axis": "y"})
    jig(t, 3, 0, 0, "north_up", STREET, nxt, M("spruce_planks"))
    jig(t, 3, 0, L - 1, "south_up", STREET, nxt, M("spruce_planks"))
    m = L // 2 if (L // 2) % 5 != 2 else L // 2 + 1
    if "w" in sides: jig(t, 0, 0, m, "west_up", BLD, bld, M("gravel"))
    if "e" in sides: jig(t, 6, 0, m, "east_up", STREET if sides.get("e") == "street" else BLD, nxt if sides.get("e") == "street" else bld, M("gravel"))
    sculk(t, r, ring)
    return save(t, name)

def drift(name, ring, seed):
    """mine drift: a timber portal cut into the rock, rails running in - the camp's oldest workings (walkway dead end)"""
    t = Tpl(7, 7, 6); r = rng(f"sculk_camp/{name}", seed)
    for x in range(7):
        for z in range(6):
            t.set(x, 0, z, pick(r, STONE))
            for y in range(1, 7): t.set(x, y, z, pick(r, STONE) if z >= 4 or x in (0, 6) else M("air"))
    for y in range(1, 5): t.set(1, y, 1, M("spruce_log"), {"axis": "y"}); t.set(5, y, 1, M("spruce_log"), {"axis": "y"})
    for x in range(1, 6): t.set(x, 5, 1, M("stripped_spruce_log"), {"axis": "x"})
    for z in range(0, 4): t.set(3, 1, z, M("rail"), {"shape": "north_south", "waterlogged": FALSE})
    for x in range(2, 5):
        for y in range(1, 5): t.set(x, y, 4, M("gravel") if y < 3 else pick(r, STONE))   # caved in
    t.set(2, 1, 3, R("rotting_wooden_crate"))
    jig(t, 3, 0, 0, "north_up", STREET, "minecraft:empty", M("spruce_planks"))
    sculk(t, r, ring)
    return t

# ------------------------------------------------------------------ buildings (front = z0, door at x=cx)
def frame(t, r, W, Dp, Hh, walls, roof, floor=BOARD):
    for x in range(W):
        for z in range(Dp):
            t.set(x, 0, z, pick(r, floor))
            for y in range(1, Hh):
                edge = x in (0, W - 1) or z in (0, Dp - 1)
                corner = x in (0, W - 1) and z in (0, Dp - 1)
                t.set(x, y, z, M("spruce_log") if corner else pick(r, walls) if edge else M("air"), {"axis": "y"} if corner else None)
            t.set(x, Hh, z, *roof(x, z))
    cx = W // 2
    for y in (1, 2): t.set(cx, y, 0, M("air"))
    return cx

CAMP_WALL = [(M("spruce_planks"), 5), (R("corrugated_rusted_metal"), 2), (M("stripped_spruce_log"), 1)]
def tin_roof(x, z): return (R("corrugated_rusted_metal_slab"), {"type": "bottom", "paint": "brown", "coat": "weathered"})
def copper_roof(x, z): return (M("weathered_cut_copper_slab"), {"type": "bottom", "waterlogged": FALSE})

def bld_shack(r):
    t = Tpl(7, 6, 7); cx = frame(t, r, 7, 7, 4, CAMP_WALL, lambda x, z: tin_roof(x, z))
    bed(t, 1, 1, 5, "brown", "south"); chest(t, 5, 1, 5, "west", "research_sculk_quarters")
    t.set(5, 1, 2, M("crafting_table")); dead_lamp(t, 3, 3, 3)
    return t, cx, "shack"

def bld_bunkhouse(r):
    t = Tpl(9, 6, 9); cx = frame(t, r, 9, 9, 4, CAMP_WALL, lambda x, z: tin_roof(x, z))
    for z in (2, 5):                                                          # bunks along both walls
        bed(t, 2, 1, z, "gray", "west"); bed(t, 7, 1, z, "gray", "east")
    t.set(4, 1, 6, M("skeleton_skull"), {"rotation": "6", "powered": FALSE}); chest(t, 4, 1, 7, "north", "research_sculk_quarters")
    t.set(4, 1, 4, M("spruce_trapdoor"), {"facing": "north", "half": "top", "open": FALSE, "powered": FALSE, "waterlogged": FALSE})
    dead_lamp(t, 4, 3, 4)
    return t, cx, "bunkhouse"

def bld_cook(r):
    t = Tpl(7, 6, 7); cx = frame(t, r, 7, 7, 4, CAMP_WALL, lambda x, z: tin_roof(x, z))
    for x in range(1, 6):
        for y in (1, 2, 3): t.set(x, y, 0, M("air"))                          # open-fronted lean-to
    t.set(3, 1, 4, M("campfire"), {"facing": "north", "lit": FALSE, "signal_fire": FALSE, "waterlogged": FALSE})
    t.set(1, 1, 5, M("smoker"), {"facing": "east", "lit": FALSE}); t.set(5, 1, 5, M("cauldron"))
    t.set(5, 1, 3, M("barrel"), {"facing": "up", "open": FALSE}); t.set(1, 1, 3, R("weathered_wooden_crate"))
    return t, cx, "cook_shack"

def bld_toolshed(r):
    t = Tpl(5, 5, 7); cx = frame(t, r, 5, 7, 3, CAMP_WALL, lambda x, z: tin_roof(x, z))
    t.set(1, 1, 5, M("damaged_anvil"), {"facing": "east"}); t.set(3, 1, 5, M("grindstone"), {"face": "floor", "facing": "north"})
    chest(t, 3, 1, 3, "west", "research_sculk_store"); t.set(1, 1, 3, R("rusted_steel_crate"))
    return t, cx, "tool_shed"

def bld_listening(r):
    t = Tpl(11, 7, 9); cx = frame(t, r, 11, 9, 5, MASON, lambda x, z: copper_roof(x, z), floor=[(M("polished_deepslate"), 3), (M("deepslate_tiles"), 2)])
    for x in (2, 8): t.set(x, 3, 0, R("steel_factory_window"), {"north": FALSE, "south": FALSE, "east": "true", "west": "true"})
    t.set(2, 1, 6, M("calibrated_sculk_sensor"), {"facing": "east", "power": "0", "sculk_sensor_phase": "inactive", "waterlogged": FALSE})
    t.set(8, 1, 6, M("sculk_sensor"), {"power": "0", "sculk_sensor_phase": "inactive", "waterlogged": FALSE})
    t.set(5, 1, 6, M("spruce_stairs"), {"facing": "west", "half": "top", "shape": "straight", "waterlogged": FALSE})   # overturned table
    t.set(5, 1, 5, M("lectern"), {"facing": "north", "has_book": FALSE, "powered": FALSE})
    chest(t, 9, 1, 7, "west", "research_sculk_archive"); t.set(1, 1, 7, M("barrel"), {"facing": "up", "open": FALSE})
    t.set(1, 2, 7, M("honeycomb_block"))                                       # the wax
    dead_lamp(t, 5, 4, 3)
    return t, cx, "listening_post"

def bld_lab(r):
    t = Tpl(9, 7, 9); cx = frame(t, r, 9, 9, 5, MASON, lambda x, z: copper_roof(x, z), floor=[(M("polished_deepslate"), 3), (M("deepslate_tiles"), 2)])
    for x in range(5, 8):                                                     # the specimen cage
        for z in range(5, 8):
            if x in (5, 7) or z in (5, 7):
                for y in (1, 2, 3): t.set(x, y, z, M("iron_bars"), {"north": FALSE, "south": FALSE, "east": FALSE, "west": FALSE, "waterlogged": FALSE})
    t.set(6, 1, 6, M("sculk_catalyst"), {"bloom": FALSE})
    t.set(1, 1, 3, M("brewing_stand"), {"has_bottle_0": FALSE, "has_bottle_1": FALSE, "has_bottle_2": FALSE})
    t.set(1, 1, 5, M("cauldron")); chest(t, 1, 1, 7, "east", "research_sculk_lab")
    dead_lamp(t, 4, 4, 3)
    return t, cx, "lab"

def bld_drift(r):
    t = drift("drift_entrance", "outer", 9)                                   # its street jigsaw cell (3,0,0) is overwritten by the building jigsaw
    chest(t, 4, 1, 2, "west", "research_sculk_engine")
    return t, 3, "drift_entrance"

BUILDINGS = [(bld_shack, 4), (bld_bunkhouse, 3), (bld_cook, 2), (bld_toolshed, 3), (bld_listening, 1), (bld_lab, 1), (bld_drift, 2)]

def main():
    if D.exists(): shutil.rmtree(D)
    if TP.exists(): shutil.rmtree(TP)
    old = OUT / "structure/station/sculk"
    if old.exists(): shutil.rmtree(old)
    old = OUT / "worldgen/template_pool/station/sculk"
    if old.exists(): shutil.rmtree(old)
    start = pit()
    w(TP / "pit.json", {"fallback": "minecraft:empty", "elements": [pe(start, 1)]})
    for ring in ("inner", "outer"):
        els = [(walk(f"walk_{ring}_11", 11, ring, {"w": 1, "e": 1}, 1), 4), (walk(f"walk_{ring}_17", 17, ring, {"w": 1, "e": 1}, 2), 2),
               (walk(f"walk_{ring}_fork", 11, ring, {"w": 1, "e": "street"}, 3), 2 if ring == "inner" else 1)]
        if ring == "outer":                                                     # outer streets peter out into old drifts
            els.append((save(drift("drift_end_outer", ring, 4), "drift_end_outer"), 2))
        w(TP / f"walk_{ring}.json", {"fallback": f"{POOL}/drift_end", "elements": [pe(l, wt) for l, wt in els]})
        bl = []
        for fn, wt in BUILDINGS:
            r = rng(f"sculk_camp/{fn.__name__}_{ring}", 7); t, cx, name = fn(r)
            jig(t, cx, 0, 0, "north_up", BLD, "minecraft:empty", M("gravel"))
            sculk(t, r, ring)
            bl.append((save(t, f"{name}_{ring}"), wt))
        w(TP / f"bld_{ring}.json", {"fallback": "minecraft:empty", "elements": [pe(l, wt) for l, wt in bl]})
    w(TP / "drift_end.json", {"fallback": "minecraft:empty", "elements": [pe(f"{POOL}/drift_end_outer", 1)]})
    # pass 9-76: every piece but the pit gets a 10-deep footing (spruce posts + rubble). The beard's ground reference is the pit's
    # bottom + 1, three below the camp floor, so without it the band under every floor is carved out (see tools/footing.py).
    for f in sorted(D.glob("*.nbt")):
        if f.stem != "pit": add_footing(f, FOOTING, M("spruce_log"), FOOT_FILL)
    sp = OUT / "worldgen/structure/sculk_research_site.json"; j = json.loads(sp.read_text())
    j.update({"start_pool": f"{POOL}/pit", "size": 7, "max_distance_from_center": 64, "terrain_adaptation": "beard_box"})
    w(sp, j)
    print(f"9-36: sculk research site = dig camp ({len(list(D.glob('*.nbt')))} pieces)")

if __name__ == "__main__":
    main()
