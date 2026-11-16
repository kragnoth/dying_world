#!/usr/bin/env python3
"""
gen_pass9_24.py - pass 9-24: the last GEARWRIGHTS (third-party-derived) structures rebuilt as ours. Run after 9_21 (rare ramps) and before 9_16. Safe to re-run.
(1) SWAMP abandoned ruins/hamlets/villages: OUR STILT HOUSES. 7 builders (creole cottage 5, dogtrot 4, limestone cottage 4, casita 3, smokehouse 2, forge 1,
    schoolhouse 1) in two swamp ramps (swampwood: mud bricks -> mangrove planks, mangrove beams/roof; swampstone: mossy cobble -> mud bricks -> dark oak),
    RUINED finish, then raised 3 blocks on mangrove-log stilts (yard becomes a deck; only posts touch the marsh - nothing below is replaced, water stays),
    ladder up from the street; entrance jigsaw back at street level. Streets = 9-3 abandoned generator with a mangrove/mud BOARDWALK palette (terrain_matching ->
    planks on the water surface). Pools dying_world:swamp/{ruined_houses, abandoned/streets, abandoned/town_centers}; terrain_adaptation none.
(2) LANDMARKS (single pieces, our builders, existing biomes/spawns/sets kept):
    burnt_homestead (dogtrot / creole cottage / barn), burnt_manor (schoolhouse / courtyard house) - 'burnt' ramp (cobble/blackstone -> charred dark oak,
    blackstone roofs) + scorch pass (coal-block/basalt char, dead campfires, cobwebs); burnt_watchtower (burnt 5x5 tower, lookout);
    ruined_chapel (chapel, mossy ramp, ruined); collapsed_minehead (fieldstone shed + timber headframe with an R&R winding wheel, rails, caved-in shaft mound).
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from savanna_kit import B, RAMPS
import gen_pass7_1 as S
import gen_pass9_1 as P
import gen_pass9_3 as G
import gen_pass9_21          # rare ramps (r_mossy, r_brick ...)
from buildkit import M, R, fix_connections
from gen_pass4_2a import w, OUT

RAMPS.update({
    "swampwood": {"wall": ["mud_bricks", "mangrove_planks", "mangrove_planks", "stripped_mangrove_wood"], "base": ["mud_bricks", "packed_mud", "mud_bricks"],
                  "floor": ["mangrove_planks", "spruce_planks", "mangrove_planks"], "trim": ["stripped_mangrove_log"], "beam": ["mangrove_log"], "roof": "mangrove",
                  "ridge": "mangrove", "inner": ["mangrove_planks"], "ceil": "mangrove"},
    "swampstone": {"wall": ["mossy_cobblestone", "mud_bricks", "dark_oak_planks", "stripped_dark_oak_wood"], "base": ["mossy_cobblestone", "mud_bricks", "mossy_cobblestone"],
                   "floor": ["mangrove_planks", "dark_oak_planks", "mangrove_planks"], "trim": ["stripped_dark_oak_log"], "beam": ["mangrove_log"], "roof": "dark_oak",
                   "ridge": "dark_oak", "inner": ["mud_bricks"], "ceil": "dark_oak"},
    "burnt": {"wall": ["cobblestone", "blackstone", "stripped_dark_oak_wood", "dark_oak_planks"], "base": ["cobblestone", "blackstone", "cobblestone"],
              "floor": ["dark_oak_planks", "stripped_dark_oak_wood", "dark_oak_planks"], "trim": ["stripped_dark_oak_log"], "beam": ["dark_oak_log"], "roof": "blackstone",
              "ridge": "blackstone", "inner": ["blackstone"], "ceil": "dark_oak"}})
SWAMP_ROSTER = [(S.creole_cottage, 5), (S.dogtrot, 4), (S.limestone_cottage, 4), (S.casita, 3), (S.smokehouse, 2), (S.forge, 1), (S.schoolhouse, 1)]
def setfam(wood, smap, prefix, fam="plains"):
    S.WOOD, S.STYLE_MAP, S.PREFIX, S.FAMILY = wood, smap, prefix, fam
    B.STEEP = B.FLAT = False; B.GROUND = ("dirt_path", "coarse_dirt", "grass_block", "coarse_dirt")
def el(loc, wt, proj="rigid"): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": proj}}

# ---------------- (1) swamp stilt houses ----------------
def stilts(t, lift=3):
    W, H, D = t.sx, t.sy, t.sz
    ent = next(((x, y, z) for (x, y, z), (n, pr, nb) in t.b.items() if n == M("jigsaw") and nb and nb.get("name") == "minecraft:building_entrance"), None)
    n = Tpl(W, H + lift, D + 2)
    GROUND = (M("dirt_path"), M("coarse_dirt"), M("grass_block"), M("dirt"), M("mud"))
    for (x, y, z), v in t.b.items():
        if (x, y, z) == ent: continue
        if y == 0 and v[0] in GROUND: v = (M("mangrove_planks") if (x + z) % 5 else M("spruce_planks"), (), None)   # yard -> plank deck
        n.b[(x, y + lift, z)] = v
    deck = [(x, z) for x in range(W) for z in range(D) if t.b.get((x, 0, z), ("",))[0] not in ("", M("air"))]
    for (x, z) in deck:
        if (x % 3 == 0 or x == W - 1) and (z % 3 == 0 or z == D - 1):
            for y in range(lift): n.set(x, y, z, M("mangrove_log"), {"axis": "y"})
    ex = ent[0] if ent else W // 2
    for y in range(1, lift): n.set(ex, y, D - 1, M("mangrove_planks"))
    for y in range(1, lift + 1): n.set(ex, y, D, M("ladder"), {"facing": "south", "waterlogged": "false"})
    for z in (D, D + 1): n.set(ex, 0, z, M("mud")); n.set(ex - 1, 0, z, M("mud")) if ex > 0 else None
    n.set(ex, 1, D + 1, M("jigsaw"), {"orientation": "south_up"}, {"id": M("jigsaw"), "name": "minecraft:building_entrance", "target": "minecraft:building_entrance",
          "pool": "minecraft:empty", "final_state": M("air"), "joint": "aligned"})
    return n

def swamp():
    N = OUT / "structure/swamp"; N.mkdir(parents=True, exist_ok=True)
    for old in N.glob("*.nbt"): old.unlink()
    els = []
    for style in ("swampwood", "swampstone"):
        setfam("mangrove", {"creole": style, "limestone": style, "hacienda": style}, f"swamp_{style}_")
        for fn, wt in SWAMP_ROSTER:
            b = fn(1); t = stilts(b.finalize("ruined")); (N / f"{b.name}_ruined.nbt").write_bytes(t.bytes())
            els.append(el(f"dying_world:swamp/{b.name}_ruined", wt))
    w(OUT / "worldgen/template_pool/swamp/ruined_houses.json", {"fallback": "minecraft:empty", "elements": els})
    G.ABANDONED = True; G.FAMILY = "swamp"
    G.PAL = {"verge": ["mud", "grass_block"], "edge": ["mangrove_planks", "mud", "packed_mud"], "inner": ["mangrove_planks", "spruce_planks"],
             "centre": ["mangrove_planks", "spruce_planks", "mangrove_planks", "mud_bricks"], "fence": "mangrove_fence", "hedge": "mangrove_leaves",
             "flowers": ["short_grass", "fern", "blue_orchid", "short_grass"], "props": [("mangrove_roots", {"waterlogged": "false"}), ("mud_bricks", {})]}
    G.street_j = lambda t, x, z, ori: G.jig(t, x, 1, z, ori, "minecraft:street", "dying_world:swamp/abandoned/streets")
    G.plot_j = lambda t, x, z, ori: G.jig(t, x, 1, z, ori, "minecraft:building_entrance", "dying_world:swamp/ruined_houses")
    G.write_streets(); G.ABANDONED = False
    for kind, size, pool in (("ruin", 1, "dying_world:swamp/ruined_houses"), ("hamlet", 4, "dying_world:swamp/abandoned/town_centers"),
                             ("village", 6, "dying_world:swamp/abandoned/town_centers")):
        p = OUT / f"worldgen/structure/abandoned_{kind}_swamp.json"; j = json.loads(p.read_text())
        j.update({"start_pool": pool, "size": size, "max_distance_from_center": 80 if size > 1 else 32, "terrain_adaptation": "none"}); j.pop("start_jigsaw_name", None)
        w(p, j)
    return len(els)

# ---------------- (2) landmarks ----------------
def scorch(t, seed):
    r = random.Random(seed)
    for p, (n, pr, nb) in list(t.b.items()):
        k = n.split(":")[-1]
        if k.endswith(("_planks", "_wood", "_log")) and r.random() < .12: t.set(*p, M("coal_block") if r.random() < .5 else M("smooth_basalt"))
        elif k in ("cobblestone", "stone_bricks") and r.random() < .15: t.set(*p, M("blackstone"))
        elif k == "glass_pane" and r.random() < .6: t.set(*p, M("iron_bars"))
    floor = [(x, y, z) for (x, y, z), (n, _, _) in t.b.items() if n == M("air") and y >= 1 and t.b.get((x, y - 1, z), ("",))[0].endswith(("_planks", "_wood", "cobblestone"))]
    r.shuffle(floor)
    for (x, y, z) in floor[:3]: t.set(x, y, z, M("campfire"), {"facing": "north", "lit": "false", "signal_fire": "false", "waterlogged": "false"})
    fix_connections(t); return t

def tower(style, name, seed):
    b = B(name, style, 7, 17, 8, seed); b.ground()
    b.walls(1, 5, 1, 5, 0, 10)
    for y in (1, 2): b.set(3, y, 5, M("air"))
    for y in range(1, 11): b.set(2, y, 3, M("ladder"), {"facing": "east", "waterlogged": "false"})
    for x in range(2, 5):
        for z in range(2, 5):
            if (x, z) != (2, 3): b.role(x, 10, z, "floor")
    for x in range(0, 7):
        for z in range(0, 7):
            if x in (0, 6) or z in (0, 6): b.role(x, 10, z, "floor"); b.set(x, 11, z, M("dark_oak_fence") if (x + z) % 2 == 0 else M("air"))
    b.window(1, 6, 3, "west"); b.window(5, 6, 3, "east"); b.window(3, 6, 1, "north")
    b.gable(1, 5, 1, 5, 14, axis="x", over=0, ceiling=False)
    for x in (1, 5):
        for z in (1, 5):
            for y in (11, 12, 13): b.role(x, y, z, "trim", {"axis": "y"})
    b.chest(4, 1, 2, "west", "minecraft:chests/village/village_plains_house")
    return b

def minehead():
    b = B("collapsed_minehead", "fieldstone", 16, 14, 12, 1); b.ground(("coarse_dirt", "gravel", "dirt_path", "coarse_dirt")); r = random.Random(5)
    b.walls(0, 6, 2, 8, 0, 4); b.gable(0, 6, 2, 8, 5, axis="z", over=0)
    for y in (1, 2): b.set(6, y, 5, M("air"))
    b.chest(1, 1, 3, "east", "dying_world:chests/mineshaft_storage"); b.set(1, 1, 7, M("barrel"), {"facing": "up", "open": "false"})
    b.set(5, 1, 3, M("crafting_table")); b.set(3, 1, 7, R("rusted_steel_crate"))
    for x in range(7, 11): b.set(x, 1, 5, M("rail"), {"shape": "east_west", "waterlogged": "false"})
    for (x, z) in ((10, 3), (14, 3), (10, 8), (14, 8)):             # headframe legs + braces
        for y in range(1, 11): b.set(x, y, z, M("spruce_log"), {"axis": "y"})
    for y in (5, 10):
        for x in range(10, 15): b.set(x, y, 3, M("spruce_log"), {"axis": "x"}); b.set(x, y, 8, M("spruce_log"), {"axis": "x"})
        for z in range(4, 8): b.set(10, y, z, M("spruce_log"), {"axis": "z"}); b.set(14, y, z, M("spruce_log"), {"axis": "z"})
    for x in range(11, 14):
        for z in range(4, 8): b.set(x, 10, z, M("spruce_planks"))
    b.set(12, 11, 5, R("rusted_encased_cogwheel"), {"axis": "x", "top_shaft": "true", "bottom_shaft": "true"}); b.set(12, 11, 6, R("rusted_encased_cogwheel"), {"axis": "x", "top_shaft": "true", "bottom_shaft": "true"})
    for y in range(4, 10): b.set(12, y, 5, M("chain"), {"axis": "y", "waterlogged": "false"})
    for x in range(11, 14):                                          # caved-in shaft mound
        for z in range(4, 8):
            b.set(x, 0, z, r.choice([M("gravel"), M("cobblestone"), M("mossy_cobblestone")]))
            if r.random() < .5: b.set(x, 1, z, r.choice([M("gravel"), M("cobblestone"), M("cobweb")]))
    b.set(12, 1, 6, M("rail"), {"shape": "east_west", "waterlogged": "false"})
    return b

def landmarks():
    D = OUT / "structure/landmarks"; D.mkdir(parents=True, exist_ok=True)
    for old in D.glob("*.nbt"): old.unlink()
    made = {}
    setfam("dark_oak", {"creole": "burnt", "limestone": "burnt", "hacienda": "burnt"}, "burnt_")
    made["burnt_homestead"] = [(f.__name__, scorch(f(1).finalize("ruined"), i)) for i, f in enumerate((S.dogtrot, S.creole_cottage, P.barn))]
    made["burnt_manor"] = [(f.__name__, scorch(f(1).finalize("ruined"), 10 + i)) for i, f in enumerate((S.schoolhouse, S.courtyard_house))]
    made["burnt_watchtower"] = [("tower", scorch(tower("burnt", "burnt_watchtower", 1).finalize("ruined"), 20))]
    setfam("oak", {"creole": "r_mossy", "limestone": "r_mossy", "hacienda": "r_mossy"}, "chapel_")
    made["ruined_chapel"] = [("chapel", S.chapel(1).finalize("ruined"))]
    setfam("spruce", {}, "")
    made["collapsed_minehead"] = [("minehead", minehead().finalize("ruined"))]
    for lm, pieces in made.items():
        for n, t in pieces: (D / f"{lm}_{n}.nbt").write_bytes(t.bytes())
        w(OUT / f"worldgen/template_pool/landmarks/{lm}.json", {"fallback": "minecraft:empty", "elements": [el(f"dying_world:landmarks/{lm}_{n}", 1) for n, _ in pieces]})
        p = OUT / f"worldgen/structure/{lm}.json"; j = json.loads(p.read_text())
        j.update({"start_pool": f"dying_world:landmarks/{lm}", "size": 1, "max_distance_from_center": 40}); j.pop("start_jigsaw_name", None); w(p, j)
    setfam("acacia", {}, "", "savanna")
    return {k: len(v) for k, v in made.items()}

def main():
    n = swamp(); lm = landmarks()
    print(f"9-24: swamp stilt houses {n} + boardwalk streets; landmarks {lm}")

if __name__ == "__main__":
    main()
