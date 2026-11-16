#!/usr/bin/env python3
"""
gen_pass9_11.py - pass 9-11: INCURSION RESEARCH STATIONS (user decision after the 9-8 walkthrough). Safe to re-run.
Medieval-alchemist x dieselpunk research stations on both sides of a dimension. Each one is a jigsaw mini-complex (fortress / end-city feel):
a HUB (start piece, portal + open front entrance) -> corridors (straight 9/15, tee, cross, corner) -> dead-end rooms (lab, engine, archive, quarters, store),
caps as fallback. Connector name/target `dying_world:station`, y1 face centre, 5x5 openings, size 6 / radius 64, beard_box.
Sites (palette + loot + spawns):
  gate_end    (overworld, land)  : END PORTAL FRAME ring, 12 frames, NO eyes (user: eyes of ender still required); endermen spawn in the dark halls (pearls).
  gate_nether (overworld, land)  : LIT nether portal; nether blocks creeping over the floor; spawns ZOMBIFIED PIGLINS only (user rule).
  nether      (nether)           : portal frame complete but UNLIT ('you can get in, might have to work to get out'); overworld moss/dirt creeping in;
                                   spawns ZOMBIES + SKELETONS (user rule, no husks). start y 36-72 (carved into the netherrack).
  end         (End highlands)    : purpur/end-stone; ONE GUARANTEED ELYTRA chest on the hub plinth; placed persistent shulkers (shells); end-city treasure.
Datapack limit (user accepted): portals are NOT paired across dimensions - vanilla linking rules apply.
Sets: dying_world:research_gates (both overworld gates, 48/18, 6 chunks from survivor villages), research_nether_stations (28/10, 3 from dying_world:nether_fortress),
research_end_stations (20/11 = end-city spacing).
"""
import json, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl, S as NS, B as NB
from gen_pass4_2a import M, R, w, item, OUT
from buildkit import rng, chest, bed, connect_pipes

J = "dying_world:station"
SITES = ("gate_end", "gate_nether", "nether", "end")
ZIP = __import__("zipfile").ZipFile(Path(__file__).resolve().parent.parent / "reference/loot_and_recipes.zip")

def pick(r, opts):
    p = r.random(); acc = 0
    for name, ch in opts:
        acc += ch
        if p < acc: return name
    return opts[-1][0]

PAL = {
    "ow": dict(wall=[(M("deepslate_bricks"), .42), (M("cracked_deepslate_bricks"), .12), (M("polished_deepslate"), .14), (R("riveted_rusted_plating"), .17), (R("rusted_plating"), .15)],
               base=[(R("sooty_brick"), .8), (M("cobbled_deepslate"), .2)], trim=[(R("riveted_rusted_plating"), 1)],
               floor=[(M("polished_andesite"), .4), (R("tread_plate"), .35), (M("stone_bricks"), .15), (M("cracked_stone_bricks"), .1)],
               ceil=[(M("deepslate_tiles"), .8), (M("cracked_deepslate_tiles"), .2)], pillar=R("salvaged_steel_block"),
               light=(R("caged_lamp"), {"facing": "down", "lit": "false"}), light_on=(R("caged_lamp"), {"facing": "down", "lit": "true"}), lit=.35, pot="potted_crimson_fungus"),
    "nether": dict(wall=[(M("polished_blackstone_bricks"), .45), (M("cracked_polished_blackstone_bricks"), .15), (M("blackstone"), .1), (R("red_oxide_plating"), .3)],
               base=[(R("firebrick"), .85), (M("gilded_blackstone"), .02), (M("blackstone"), .13)], trim=[(R("red_oxide_plating"), 1)],
               floor=[(M("polished_blackstone"), .4), (R("tread_plate"), .3), (M("smooth_basalt"), .3)],
               ceil=[(M("polished_blackstone_bricks"), .7), (M("basalt"), .3)], pillar=M("polished_basalt"),
               light=(M("soul_lantern"), {"hanging": "true", "waterlogged": "false"}), light_on=(M("soul_lantern"), {"hanging": "true", "waterlogged": "false"}), lit=.25, pot="potted_warped_fungus", windows=False),
    "end": dict(wall=[(M("end_stone_bricks"), .5), (M("purpur_block"), .22), (R("industrial_blue_plating"), .2), (M("obsidian"), .08)],
               base=[(M("obsidian"), .6), (M("purpur_block"), .4)], trim=[(M("purpur_block"), 1)],
               floor=[(M("purpur_block"), .45), (M("end_stone_bricks"), .35), (R("tread_plate"), .2)],
               ceil=[(M("end_stone_bricks"), .8), (M("purpur_block"), .2)], pillar=M("purpur_pillar"),
               light=(M("end_rod"), {"facing": "down"}), light_on=(M("end_rod"), {"facing": "down"}), lit=.6, pot="potted_wither_rose", pipes=False),
}
PAL_OF = {"gate_end": "ow", "gate_nether": "ow", "nether": "nether", "end": "end"}

class P:
    """one station piece; walls/floor/ceiling shell + openings + jigsaws"""
    def __init__(s, site, name, sx, sy, sz, seed=0):
        s.site, s.name, s.t, s.r, s.p = site, name, Tpl(sx, sy, sz), rng(f"{site}/{name}", seed), PAL[PAL_OF[site]]
        s.sx, s.sy, s.sz = sx, sy, sz
        s.fill = s.p.get("fill", M("air"))                   # 9-12: water-filled sunken site
    def b(s, x, y, z, name, props=None, nbt=None): s.t.set(x, y, z, name, props, nbt)
    def blk(s, x, y, z, role):
        n = s.p["pillar"] if role == "pillar" else pick(s.r, s.p[role])
        s.b(x, y, z, n, {"axis": "y"} if n in (M("purpur_pillar"), M("polished_basalt"), R("salvaged_steel_block")) else None)
    def shell(s):
        X, Y, Z = s.sx - 1, s.sy - 1, s.sz - 1
        for x in range(s.sx):
            for z in range(s.sz):
                s.blk(x, 0, z, "floor"); s.blk(x, Y, z, "ceil")
                for y in range(1, Y):
                    if x in (0, X) or z in (0, Z):
                        corner = x in (0, X) and z in (0, Z)
                        s.blk(x, y, z, "pillar" if corner else "base" if y == 1 else "trim" if y == Y - 1 else "wall")
                    else:
                        s.b(x, y, z, s.fill)
    def opening(s, face, full=False):
        """5 wide x 5 high hole centred on a face (full=True: whole interior width, used by corridor ends)"""
        X, Z = s.sx - 1, s.sz - 1
        if face in "ns":
            z = 0 if face == "n" else Z; c = s.sx // 2
            xs = range(1, X) if full else range(c - 2, c + 3)
            for x in xs:
                for y in range(1, 6): s.b(x, y, z, s.fill)
        else:
            x = 0 if face == "w" else X; c = s.sz // 2
            zs = range(1, Z) if full else range(c - 2, c + 3)
            for z in zs:
                for y in range(1, 6): s.b(x, y, z, s.fill)
    def jig(s, face, pool=True, final=None):
        X, Z = s.sx - 1, s.sz - 1
        x, z, f = {"n": (s.sx // 2, 0, "north"), "s": (s.sx // 2, Z, "south"), "w": (0, s.sz // 2, "west"), "e": (X, s.sz // 2, "east")}[face]
        s.b(x, 1, z, M("jigsaw"), {"orientation": f + "_up"}, {"id": M("jigsaw"), "name": J, "target": J,
            "pool": f"dying_world:station/{s.site}/wings" if pool else "minecraft:empty", "final_state": final or s.fill, "joint": "aligned"})
    def light(s, x, y, z):
        on = s.r.random() < s.p["lit"]
        n, pr = s.p["light_on" if on else "light"]
        if n == R("caged_lamp"): pr = dict(pr, lit="true" if on else "false")
        s.b(x, y, z, n, pr)
    def window(s, x, y, z, along):
        s.b(x, y, z, R("steel_factory_window"), {"north": "true" if along == "z" else "false", "south": "true" if along == "z" else "false",
                                                  "east": "true" if along == "x" else "false", "west": "true" if along == "x" else "false"})
    def chest(s, x, y, z, facing, kind): chest(s.t, x, y, z, facing, f"research_{s.site}_{kind}")
    def save(s, d):
        connect_pipes(s.t); (d / f"{s.name}.nbt").write_bytes(s.t.bytes()); return f"dying_world:station/{s.site}/{s.name}"

# ---------------- corridors ----------------
def corridor(site, L, name, seed):
    p = P(site, name, 7, 7, L, seed); p.shell(); p.opening("n", True); p.opening("s", True); p.jig("n"); p.jig("s")
    for z in range(2, L - 2):
        if z % 4 == 2:
            for x in (0, 6):
                for y in range(1, 6): p.blk(x, y, z, "pillar")
        elif z % 4 == 0 and p.p.get("windows", True):
            for x in (0, 6): p.window(x, 3, z, "z")
        if z % 6 == 3: p.light(3, 5, z)
        if p.r.random() < .12: p.b(p.r.choice((1, 5)), 1, z, p.r.choice([R("rusted_drum"), R("gas_cylinders"), R("rusted_steel_crate")]))
    # pipe run along the ceiling corner (dieselpunk)
    for z in range(1, L - 1): p.b(5, 5, z, R("rusted_fluid_pipe"), {d: "true" for d in ("north", "east", "south", "west", "up", "down")}) if p.p.get("pipes", True) else None
    return p

def junction(site, faces, name, seed):
    p = P(site, name, 7, 7, 7, seed); p.shell()
    for f in faces: p.opening(f, True); p.jig(f)
    p.light(3, 5, 3)
    return p

def cap(site):
    p = P(site, "cap", 7, 7, 1)
    for x in range(7):
        for y in range(7): p.blk(x, y, 0, "floor" if y == 0 else "ceil" if y == 6 else "base" if y == 1 else "wall")
    wall = pick(p.r, p.p["wall"]); p.jig("n", pool=False, final=wall)
    return p

# ---------------- rooms (13x9x13, entrance north) ----------------
def room(site, kind, seed):
    p = P(site, kind, 13, 9, 13, seed); p.shell(); p.opening("n"); p.jig("n", pool=False); r = p.r
    for x, z in ((3, 6), (9, 6)): p.light(x, 7, z)
    if p.p.get("windows", True):
        for z in (4, 8): p.window(0, 4, z, "z"); p.window(12, 4, z, "z")
    if kind == "lab":                                     # alchemist
        for x in range(2, 11): p.b(x, 1, 11, M("bookshelf"))
        for x in (3, 6, 9):
            p.b(x, 1, 7, M("spruce_planks")); p.b(x, 2, 7, M("brewing_stand"), {"has_bottle_0": "false", "has_bottle_1": "false", "has_bottle_2": "false"})
            p.b(x + 1, 1, 7, M("spruce_planks")); p.b(x + 1, 2, 7, M("candle"), {"candles": str(r.randint(1, 3)), "lit": "false", "waterlogged": "false"})
        p.b(1, 1, 3, M("water_cauldron"), {"level": "3"}); p.b(11, 1, 3, M("cauldron"))
        p.b(6, 1, 9, M("lectern"), {"facing": "north", "has_book": "false", "powered": "false"})
        p.b(1, 1, 9, M("barrel"), {"facing": "up", "open": "false"}); p.b(1, 2, 9, M(p.p["pot"]))
        p.b(11, 1, 9, R("rusted_mechanical_pump"), {"facing": "up"}); p.b(11, 2, 9, R("rusted_fluid_pipe"), {d: "true" for d in ("north", "east", "south", "west", "up", "down")})
        p.b(2, 1, 5, M("amethyst_cluster"), {"facing": "up", "waterlogged": "false"}) if r.random() < .6 else None
        p.chest(11, 1, 7, "west", "lab")
        if site.startswith("gate_"):                       # 9-13: caged allay specimen (allays had no source: outposts/mansions disabled)
            for x in (1, 2, 3):
                for z in (5, 6, 7):
                    for y in (1, 2, 3):
                        if x in (1, 3) or z in (5, 7) or y in (1, 3): p.b(x, y, z, M("glass") if y == 2 else M("polished_andesite"))
                        else: p.b(x, y, z, M("air"))
            p.t.entity(2.5, 2, 6.5, {"id": NS("minecraft:allay"), "PersistenceRequired": NB(1)})
    elif kind == "engine":                                # dieselpunk
        for x in range(2, 11):
            p.b(x, 1, 10, R("hazard_plating")); p.b(x, 2, 10, R("rusted_encased_cogwheel") if x % 2 else R("rusted_casing"),
                                                     {"axis": "z", "top_shaft": "true", "bottom_shaft": "true"} if x % 2 else None)
        for x in (2, 10):
            for y in range(1, 8): p.b(x, y, 6, R("rusted_fluid_pipe"), {d: "true" for d in ("north", "east", "south", "west", "up", "down")})
        p.b(6, 1, 6, M("blast_furnace"), {"facing": "north", "lit": "false"}); p.b(5, 1, 6, M("furnace"), {"facing": "north", "lit": "false"})
        p.b(7, 1, 6, R("rusted_mechanical_pump"), {"facing": "north"})
        p.b(1, 1, 2, R("gas_cylinders"), {"count": str(r.randint(3, 8)), "facing": "east"}); p.b(11, 1, 2, R("rusted_drum"), {"axis": "y"})
        p.b(11, 2, 2, R("rusted_drum"), {"axis": "y"}) if r.random() < .5 else None
        p.b(6, 3, 12, R("sign_high_voltage"), {"facing": "north"})
        p.chest(1, 1, 8, "east", "engine")
    elif kind == "archive":
        for z in (3, 6, 9):
            for x in list(range(2, 5)) + list(range(8, 11)):
                for y in (1, 2, 3): p.b(x, y, z, M("bookshelf") if r.random() < .85 else p.fill)
        p.b(6, 1, 10, M("lectern"), {"facing": "north", "has_book": "false", "powered": "false"}); p.b(6, 1, 11, M("cartography_table"))
        p.chest(11, 1, 11, "west", "archive")
    elif kind == "quarters":
        for x in (2, 5, 8, 10):
            bed(p.t, x, 1, 10, r.choice(["gray", "brown", "black", "white"]), "south")
        for x in (3, 9): p.b(x, 1, 3, M("barrel"), {"facing": "up", "open": "false"})
        p.chest(1, 1, 6, "east", "quarters"); p.b(6, 1, 6, M("spruce_planks")); p.b(6, 2, 6, M(p.p["pot"]))
    elif kind == "store":
        for x in range(1, 12):
            for z in (10, 11):
                if r.random() < .55: p.b(x, 1, z, r.choice([R("rusted_steel_crate"), R("wire_mesh_crate"), R("weathered_wooden_crate"), M("barrel")]))
                if r.random() < .25: p.b(x, 2, z, r.choice([R("rusted_steel_crate"), R("weathered_wooden_crate")]))
        p.chest(5, 1, 9, "north", "store"); p.chest(7, 1, 9, "north", "store")
    return p

# ---------------- hubs (17x13x17 start piece; south face = open entrance to the outside) ----------------
def hub(site):
    p = P(site, "hub", 17, 13, 17); p.shell(); r = p.r
    for f in "nwe": p.opening(f); p.jig(f)
    p.opening("s")                                        # front door to the world
    for x in (6, 10):
        for y in range(1, 7): p.blk(x, y, 16, "pillar")
    for x in range(6, 11): p.blk(x, 6, 16, "trim")
    for x, z in ((3, 3), (13, 3), (3, 13), (13, 13)):
        for y in range(1, 12): p.blk(x, y, z, "pillar")
    for x in (4, 8, 12):
        for z in (4, 12): p.light(x, 11, z)
    if p.p.get("windows", True):
        for z in (5, 11): p.window(0, 6, z, "z"); p.window(16, 6, z, "z")
    if site == "gate_end":
        for i in (7, 8, 9):                                # 12 frames facing the centre, empty (eyes of ender required)
            p.b(i, 1, 6, M("end_portal_frame"), {"facing": "south", "eye": "false"}); p.b(i, 1, 10, M("end_portal_frame"), {"facing": "north", "eye": "false"})
            p.b(6, 1, i, M("end_portal_frame"), {"facing": "east", "eye": "false"}); p.b(10, 1, i, M("end_portal_frame"), {"facing": "west", "eye": "false"})
        for x in range(5, 12):
            for z in range(5, 12):
                if not (6 <= x <= 10 and 6 <= z <= 10): p.b(x, 0, z, M("obsidian") if r.random() < .5 else M("crying_obsidian"))
        p.b(2, 1, 8, M("lectern"), {"facing": "east", "has_book": "false", "powered": "false"})
        p.b(14, 1, 7, M("spruce_planks")); p.b(14, 2, 7, M("brewing_stand"), {"has_bottle_0": "false", "has_bottle_1": "false", "has_bottle_2": "false"})
        p.chest(14, 1, 9, "west", "lab"); p.chest(2, 1, 6, "east", "archive")
    elif site in ("gate_nether", "nether"):
        for y in range(1, 6):                               # obsidian frame 4x5, portal 2x3 (axis x)
            for x in range(6, 10):
                edge = y in (1, 5) or x in (6, 9)
                if edge: p.b(x, y, 8, M("obsidian"))
                elif site == "gate_nether": p.b(x, y, 8, M("nether_portal"), {"axis": "x"})
        creep = [(M("netherrack"), .5), (M("crimson_nylium"), .2), (M("soul_soil"), .15), (M("magma_block"), .15)] if site == "gate_nether" else \
                [(M("moss_block"), .45), (M("coarse_dirt"), .25), (M("mossy_cobblestone"), .2), (M("rooted_dirt"), .1)]
        for x in range(1, 16):
            for z in range(1, 16):
                d = abs(x - 7.5) + abs(z - 8)
                if r.random() < max(0, 1 - d / 7): p.b(x, 0, z, pick(r, creep))
        if site == "gate_nether":
            for x, z in ((5, 7), (10, 9), (8, 11)): p.b(x, 1, z, M("crimson_roots")) if r.random() < .7 else None
        else:
            for x, z in ((5, 7), (10, 9), (8, 11)): p.b(x, 1, z, M("short_grass")) if r.random() < .7 else None
            p.b(4, 1, 8, M("chest"), {"facing": "east", "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": "dying_world:chests/research_nether_portal"})
        p.chest(14, 1, 9, "west", "lab"); p.chest(2, 1, 12, "east", "store")
    elif site == "end":
        for x in range(6, 11):
            for z in range(6, 11): p.b(x, 1, z, M("obsidian") if (x in (6, 10) or z in (6, 10)) else M("purpur_block"))
        p.b(8, 2, 8, M("chest"), {"facing": "south", "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": "dying_world:chests/research_end_elytra"})
        for x, z in ((6, 6), (10, 6), (6, 10), (10, 10)): p.b(x, 2, z, M("end_rod"), {"facing": "up"})
        for x, z in ((2, 2), (14, 2), (2, 14), (14, 14)):   # persistent shulkers (shells)
            p.t.entity(x + .5, 1, z + .5, {"id": NS("minecraft:shulker"), "PersistenceRequired": NB(1), "AttachFace": NB(0), "Color": NB(16)})
        p.chest(14, 1, 8, "west", "store")
    return p

# ---------------- loot ----------------
def potion(pid, wgt): return {"type": "minecraft:item", "name": "minecraft:potion", "weight": wgt, "functions": [{"function": "minecraft:set_potion", "id": pid}]}
def book(wgt): return {"type": "minecraft:item", "name": "minecraft:book", "weight": wgt, "functions": [{"function": "minecraft:enchant_randomly"}]}
def table(name, *pools):
    w(OUT / f"loot_table/chests/{name}.json", {"type": "minecraft:chest", "pools": [{"rolls": {"type": "minecraft:uniform", "min": lo, "max": hi}, "entries": e} for lo, hi, e in pools]})

def loot():
    rr = "rustandrebar"
    tech = [item("iron_ingot", 8, 2, 6), item("copper_ingot", 8, 3, 9), item("redstone", 6, 4, 12), item("coal", 6, 4, 12), item("gold_ingot", 3, 1, 3),
            item("rebar_bundle", 4, 2, 6, ns=rr), item("caged_lamp", 2, 1, 3, ns=rr), item("tread_plate", 3, 4, 10, ns=rr), item("gunpowder", 3, 2, 5)]
    books = [item("paper", 8, 3, 9), item("book", 6, 1, 3), book(4), item("writable_book", 2), item("compass", 2), item("map", 3), item("ink_sac", 3, 1, 4)]
    camp = [item("bread", 8, 2, 5), item("cooked_beef", 5, 1, 4), item("torch", 6, 4, 12), item("string", 4, 2, 6), item("leather", 4, 1, 4), item("candle", 3, 1, 4)]
    alch = [item("glass_bottle", 8, 2, 6), item("nether_wart", 6, 2, 6), item("glowstone_dust", 5, 2, 6), item("redstone", 5, 2, 6), item("sugar", 4, 2, 5),
            item("fermented_spider_eye", 3, 1, 2), item("amethyst_shard", 3, 2, 5)]
    site_lab = {
        "gate_end": [item("ender_pearl", 8, 1, 4), item("blaze_powder", 6, 2, 5), item("ender_eye", 2, 1, 2), item("obsidian", 3, 2, 5), potion("minecraft:night_vision", 2)],
        "gate_nether": [potion("minecraft:fire_resistance", 6), item("magma_cream", 5, 1, 3), item("blaze_powder", 4, 1, 4), item("obsidian", 4, 2, 6),
                        item("flint_and_steel", 3), item("gold_nugget", 5, 3, 9), item("fire_charge", 3, 1, 3)],
        "nether": [potion("minecraft:fire_resistance", 5), item("blaze_rod", 2, 1, 2), item("ghast_tear", 1), item("quartz", 6, 3, 9), item("magma_cream", 4, 1, 3),
                   item("gold_ingot", 4, 1, 3), item("flint_and_steel", 3), item("fire_charge", 3, 1, 3)],
        "end": [item("chorus_fruit", 6, 2, 6), item("popped_chorus_fruit", 5, 2, 6), item("ender_pearl", 6, 1, 4), item("shulker_shell", 2, 1, 2),
                item("dragon_breath", 2, 1, 2), item("end_rod", 4, 1, 3), potion("minecraft:slow_falling", 3)]}
    for s in SITES:
        table(f"research_{s}_lab", (2, 4, alch), (2, 4, site_lab[s]))
        table(f"research_{s}_engine", (3, 6, tech))
        table(f"research_{s}_archive", (2, 5, books), (0, 1, site_lab[s]))
        table(f"research_{s}_quarters", (3, 6, camp + ([item("cobblestone", 4, 8, 16), item("oak_log", 4, 4, 10), item("wheat_seeds", 3, 2, 6), item("oak_sapling", 2, 1, 3)] if s == "nether" else [])))
        table(f"research_{s}_store", (2, 4, tech), (2, 4, camp), (1, 2, site_lab[s]))
    table("research_nether_portal", (1, 1, [item("flint_and_steel", 1)]), (1, 3, [item("obsidian", 4, 1, 3), item("fire_charge", 3, 1, 2), potion("minecraft:fire_resistance", 2)]))
    # End: the vanilla end-city treasure table + a guaranteed elytra (user: one per End station)
    ect = json.loads(ZIP.read("data/minecraft/loot_table/chests/end_city_treasure.json")); ect.pop("random_sequence", None)
    w(OUT / "loot_table/chests/research_end_store.json", ect)
    ely = json.loads(json.dumps(ect)); ely["pools"].insert(0, {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:elytra"}]})
    w(OUT / "loot_table/chests/research_end_elytra.json", ely)

# ---------------- registration ----------------
def pe(loc, wt): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}
def salt(n): return zlib.crc32(n.encode()) % 2000000000

STRUCT = {
    "gate_end": dict(biomes="#dying_world:has_structure/scavenger_outpost_any", h={"absolute": 0}, proj="WORLD_SURFACE_WG", step="surface_structures",
                     spawns={"monster": {"bounding_box": "piece", "spawns": [{"type": "minecraft:enderman", "weight": 1, "minCount": 1, "maxCount": 2}]}}),
    "gate_nether": dict(biomes="#dying_world:has_structure/scavenger_outpost_any", h={"absolute": 0}, proj="WORLD_SURFACE_WG", step="surface_structures",
                        spawns={"monster": {"bounding_box": "piece", "spawns": [{"type": "minecraft:zombified_piglin", "weight": 1, "minCount": 2, "maxCount": 4}]}}),
    "nether": dict(biomes="#dying_world:has_structure/research_nether", h={"type": "minecraft:uniform", "min_inclusive": {"absolute": 36}, "max_inclusive": {"absolute": 72}},
                   proj=None, step="underground_decoration",
                   spawns={"monster": {"bounding_box": "piece", "spawns": [{"type": "minecraft:zombie", "weight": 2, "minCount": 2, "maxCount": 4},
                                                                           {"type": "minecraft:skeleton", "weight": 2, "minCount": 1, "maxCount": 3}]}}),
    "end": dict(biomes="#dying_world:has_structure/research_end", h={"absolute": 0}, proj="WORLD_SURFACE_WG", step="surface_structures", spawns={}),
}

def main():
    loot()
    w(OUT / "tags/worldgen/biome/has_structure/research_nether.json", {"replace": False, "values": ["#minecraft:is_nether"]})
    w(OUT / "tags/worldgen/biome/has_structure/research_end.json", {"replace": False, "values": ["minecraft:end_highlands"]})
    n = 0
    for site in SITES:
        d = OUT / f"structure/station/{site}"; d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.nbt"): old.unlink()
        hubloc = hub(site).save(d)
        wings = [(corridor(site, 9, "corridor_9", 1).save(d), 4), (corridor(site, 15, "corridor_15", 2).save(d), 3),
                 (junction(site, "nwe", "tee", 3).save(d), 2), (junction(site, "nswe", "cross", 4).save(d), 1), (junction(site, "ne", "corner", 5).save(d), 2)]
        for i, k in enumerate(("lab", "engine", "archive", "quarters", "store")): wings.append((room(site, k, 10 + i).save(d), 2))
        caploc = cap(site).save(d); n += len(wings) + 2
        pool = f"dying_world:station/{site}"
        w(OUT / f"worldgen/template_pool/station/{site}/hub.json", {"fallback": "minecraft:empty", "elements": [pe(hubloc, 1)]})
        w(OUT / f"worldgen/template_pool/station/{site}/wings.json", {"fallback": f"{pool}/caps", "elements": [pe(l, wt) for l, wt in wings]})
        w(OUT / f"worldgen/template_pool/station/{site}/caps.json", {"fallback": "minecraft:empty", "elements": [pe(caploc, 1)]})
        c = STRUCT[site]; j = {"type": "minecraft:jigsaw", "biomes": c["biomes"], "max_distance_from_center": 64, "size": 6, "spawn_overrides": c["spawns"],
                               "start_height": c["h"], "start_pool": f"{pool}/hub", "step": c["step"], "terrain_adaptation": "beard_box", "use_expansion_hack": False}
        if c["proj"]: j["project_start_to_heightmap"] = c["proj"]
        w(OUT / f"worldgen/structure/research_{site}.json", j)
    w(OUT / "worldgen/structure_set/research_gates.json", {"structures": [{"structure": "dying_world:research_gate_end", "weight": 1}, {"structure": "dying_world:research_gate_nether", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 48, "separation": 18, "salt": salt("dying_world:research_gates"),
                      "exclusion_zone": {"other_set": "dying_world:survivor_villages", "chunk_count": 6}}})
    w(OUT / "worldgen/structure_set/research_nether_stations.json", {"structures": [{"structure": "dying_world:research_nether", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 28, "separation": 10, "salt": salt("dying_world:research_nether_stations"),
                      "exclusion_zone": {"other_set": "dying_world:nether_fortress", "chunk_count": 3}}})
    w(OUT / "worldgen/structure_set/research_end_stations.json", {"structures": [{"structure": "dying_world:research_end", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 20, "separation": 11, "spread_type": "triangular", "salt": salt("dying_world:research_end_stations")}})
    print(f"9-11: 4 research stations, {n} pieces, 3 structure sets, {5 * 4 + 3} loot tables")

if __name__ == "__main__":
    main()
