#!/usr/bin/env python3
"""
gen_pass9_20.py - pass 9-20: ARCHAEOLOGY + SNIFFERS, and the LAST KUBEJS VILLAGE PIECES replaced by ours. Run after the family generators (9_1, 9_3, 9_4, 9_5,
9_6), 9_12, 9_13; BEFORE 9_19 (stronghold houses inherit the dig spots from the ruined houses). Safe to re-run (re-stamps from the generated NBTs).

(A) OUR ARCHAEOLOGY TABLES dying_world:archaeology/* (one item per brush, vanilla sets + dying-world extras + better odds, SNIFFER EGGS on land):
    ruins_common (sherds ~1/3, emeralds, nuggets, seeds, candles, copper, rebar, sniffer egg ~2%), ruins_rare (trail trims, dune/wild trims, relic disc,
    sniffer egg ~9%, diamonds, enchanted book, golden apple), desert_dig (desert sherds, tnt/gunpowder, dune trim, sniffer egg ~5%), seabed (ocean sherds,
    SNIFFER EGG ~15%, prismarine, nautilus shell).
(B) SUSPICIOUS BLOCKS placed (always on a supported cell, never on jigsaws):
    ruined houses of all 5 families (2-3 in the yard ground; desert -> sand/desert_dig, others gravel/ruins_common 85% + ruins_rare 15%),
    abandoned street pieces (2 per piece), wells (2 round the base), dig sites (now our tables), sunken research lab hub (5 x seabed sand).
    -> the scavenger stronghold houses (9-19, built from the ruined houses) inherit them.
(C) LAST KUBEJS VILLAGE PIECES -> OURS: every survivor village used the kubejs town centres (plains_market, ...), street terminators, villager pools and decor pools.
    Now: dying_world:<fam>/town_centers (17x17 plaza: roofed well, BELL (meeting point), 2 market stalls, benches, lamp posts, 2 villager + 1 iron-golem jigsaws,
    4 street exits), dying_world:<fam>/street_ends (fence + gate), and our content written into the vanilla-named pools the street NBTs point at:
    minecraft:village/<fam>/villagers (unemployed villagers of the family type, babies, a nitwit) and minecraft:village/<fam>/decor (lamp post, hay/barrel stack,
    planter, bench, crate pile). Iron golem = our own dying_world:village_iron_golem piece.
(D) Files in datapack_imported that still referenced brutos / vsrevamped / repurposed structures are deleted (none of them shipped any more).
"""
import json, random, sys, zlib, gzip
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from nbtw import Tpl, S as NS, I as NI, B as NB
from buildkit import M, R, fix_connections
from gen_pass4_2a import w, item, OUT
import gen_pass9_3 as G

ROOT = Path(__file__).resolve().parent.parent
FAMS = ("plains", "taiga", "snowy", "desert", "savanna")
A = "dying_world:archaeology"

# ---------------- (A) tables ----------------
def it(n, wt, lo=None, hi=None): return item(n, wt, lo, hi)
def book(wt): return {"type": "minecraft:item", "name": "minecraft:book", "weight": wt, "functions": [{"function": "minecraft:enchant_randomly"}]}
def sh(n, wt=1): return it(f"{n}_pottery_sherd", wt)
def tables():
    T = {
        "ruins_common": [it("emerald", 3), it("gold_nugget", 3, 1, 4), it("iron_nugget", 3, 2, 6), it("coal", 3), it("bone", 3), it("brick", 2), it("flint", 2),
                         it("string", 2), it("wheat_seeds", 2), it("beetroot_seeds", 1), it("pumpkin_seeds", 1), it("candle", 2), it("lead", 1), it("flower_pot", 1),
                         it("copper_ingot", 2), {"type": "minecraft:item", "name": "rustandrebar:rebar_bundle", "weight": 1}, it("name_tag", 1), it("sniffer_egg", 1),
                         sh("arms_up", 2), sh("brewer", 2), sh("archer"), sh("miner"), sh("prize"), sh("skull"), sh("angler"), sh("shelter"), sh("snort"),
                         sh("blade"), sh("explorer"), sh("mourner"), sh("plenty"), sh("sheaf"), sh("friend"), sh("heart")],
        "ruins_rare": [it("wayfinder_armor_trim_smithing_template", 2), it("raiser_armor_trim_smithing_template", 2), it("shaper_armor_trim_smithing_template", 2),
                       it("host_armor_trim_smithing_template", 2), it("dune_armor_trim_smithing_template", 1), it("wild_armor_trim_smithing_template", 1),
                       it("music_disc_relic", 2), it("sniffer_egg", 3), sh("burn"), sh("danger"), sh("heartbreak"), sh("howl"), it("diamond", 2), it("golden_apple", 1),
                       book(2), it("emerald", 4, 2, 4)],
        "desert_dig": [sh("archer", 2), sh("miner", 2), sh("prize", 2), sh("skull", 2), sh("arms_up", 2), sh("brewer", 2), it("emerald", 3), it("gold_nugget", 3, 1, 4),
                       it("tnt", 1), it("gunpowder", 2), it("diamond", 1), it("dune_armor_trim_smithing_template", 1), it("sniffer_egg", 2), it("suspicious_stew", 1),
                       it("bone", 2), it("brick", 1)],
        "seabed": [sh("angler"), sh("shelter"), sh("snort"), sh("blade"), sh("explorer"), sh("mourner"), sh("plenty"), it("sniffer_egg", 4), it("emerald", 2),
                   it("gold_nugget", 3, 1, 4), it("prismarine_shard", 2, 1, 3), it("nautilus_shell", 1), it("coal", 2), it("iron_axe", 1)]}
    for n, e in T.items(): w(OUT / f"loot_table/archaeology/{n}.json", {"type": "minecraft:archaeology", "pools": [{"rolls": 1, "entries": e}]})

# ---------------- (B) suspicious blocks ----------------
GROUNDISH = ("gravel", "coarse_dirt", "dirt_path", "grass_block", "dirt", "podzol", "rooted_dirt", "snow_block", "packed_mud", "sand", "mud")
SOLID_BELOW_EXCL = ("air", "water", "structure_void", "jigsaw")
def sus_state(s, x, y, z, sand, table):
    s.set(x, y, z, M("suspicious_sand" if sand else "suspicious_gravel"), {"dusted": "0"}, (10, {"id": (8, M("brushable_block")), "LootTable": (8, table)}))
def stamp(path, n, sand, pick, seed, need_open=True, ys=(0,)):
    """turn up to n ground cells (y in ys, ground-ish block, open sky above, not next to a jigsaw) into suspicious blocks"""
    s = nbtrw.Struct(path.read_bytes()); r = random.Random(zlib.crc32(str(path.name).encode()) + seed)
    for p, (nm, _, _) in list(s.b.items()):                         # re-run safe: earlier stamps back to ground
        if nm in (M("suspicious_sand"), M("suspicious_gravel")) and p[1] in ys: s.set(*p, M("sand") if nm == M("suspicious_sand") else M("gravel"))
    sx, sy, sz = s.size; cand = []
    for (x, y, z), (nm, _, _) in s.b.items():
        if y not in ys or nm.split(":")[-1] not in GROUNDISH: continue
        above = s.b.get((x, y + 1, z), ("minecraft:air",))[0]
        if above not in (M("air"), M("structure_void"), M("short_grass")): continue
        if need_open and any(s.b.get((x, yy, z), ("minecraft:air",))[0] not in (M("air"), M("structure_void")) for yy in range(y + 2, sy)): continue
        if y > 0 and any(k in s.b.get((x, y - 1, z), ("minecraft:air",))[0] for k in SOLID_BELOW_EXCL): continue
        if any("jigsaw" in s.b.get((x + dx, y + dy, z + dz), ("",))[0] for dx in (-1, 0, 1) for dz in (-1, 0, 1) for dy in (0, 1)): continue
        cand.append((x, y, z))
    r.shuffle(cand); k = 0
    for (x, y, z) in cand[:n]:
        sus_state(s, x, y, z, sand, pick(r)); k += 1
    path.write_bytes(s.bytes()); return k

def stamp_all():
    tot = {}
    land = lambda r: f"{A}/ruins_rare" if r.random() < .15 else f"{A}/ruins_common"
    for fam in FAMS:
        sand = fam == "desert"; pick = (lambda r: f"{A}/desert_dig" if r.random() < .85 else f"{A}/ruins_rare") if sand else land
        n = 0
        for p in sorted((OUT / f"structure/{fam}").glob("*_ruined.nbt")): n += stamp(p, 3, sand, pick, 1)
        for p in sorted((OUT / f"structure/{fam}/abandoned/streets").glob("*.nbt")): n += stamp(p, 2, sand, pick, 2)
        tot[fam] = n
    n = 0
    for p in sorted((OUT / "structure/wells").glob("*.nbt")):                # silt at the bottom of the shaft (under the water)
        s = nbtrw.Struct(p.read_bytes()); r = random.Random(zlib.crc32(p.name.encode())); arid = "arid" in p.name
        for q, (nm, _, _) in list(s.b.items()):                         # re-run safe
            if "suspicious" in nm: s.set(*q, M("gravel"))
        cells = sorted((x, y, z) for (x, y, z), (nm, _, _) in s.b.items() if "water" not in nm and nm != M("air")
                       and s.b.get((x, y + 1, z), ("",))[0] == M("water") and "jigsaw" not in nm)
        low = [c for c in cells if c[1] == min((c[1] for c in cells), default=0)]
        r.shuffle(low)
        for (x, y, z) in low[:2]:
            sus_state(s, x, y, z, arid, f"{A}/desert_dig" if arid else (f"{A}/ruins_rare" if r.random() < .25 else f"{A}/ruins_common")); n += 1
        p.write_bytes(s.bytes())
    tot["wells"] = n
    p = OUT / "structure/station/sunken/hub.nbt"; s = nbtrw.Struct(p.read_bytes()); r = random.Random(7); k = 0
    for (x, z) in ((3, 6), (4, 10), (12, 5), (13, 11), (6, 13)):        # sea-floor sample beds in the hub floor
        sus_state(s, x, 0, z, True, f"{A}/seabed"); k += 1
    p.write_bytes(s.bytes()); tot["sunken"] = k
    return tot

def digsites():
    """9-13 dig sites -> our tables (rewrite the LootTable of every brushable block)"""
    for kind, mix in (("arid", [(f"{A}/desert_dig", .75), (f"{A}/ruins_rare", .1), (f"{A}/seabed", .15)]),
                      ("temp", [(f"{A}/ruins_common", .65), (f"{A}/ruins_rare", .15), (f"{A}/seabed", .2)])):
        p = OUT / f"structure/digsite/{kind}.nbt"; s = nbtrw.Struct(p.read_bytes()); r = random.Random(11)
        for pos, (nm, props, nbt) in list(s.b.items()):
            if "suspicious" in nm:
                q = r.random(); acc = 0
                for t, c in mix:
                    acc += c
                    if q < acc: break
                s.set(*pos, nm, props, (10, {"id": (8, M("brushable_block")), "LootTable": (8, t)}))
        p.write_bytes(s.bytes())

# ---------------- (C) town centres, street ends, villagers, decor ----------------
PAL = {
    "plains": dict(G.PAL),
    "taiga": {"verge": ["podzol", "coarse_dirt"], "edge": ["rooted_dirt", "gravel", "coarse_dirt"], "inner": ["dirt_path", "cobblestone"],
              "centre": ["cobblestone", "mossy_cobblestone", "spruce_planks", "dirt_path"], "fence": "spruce_fence", "hedge": "spruce_leaves",
              "flowers": ["fern", "sweet_berry_bush", "fern", "large_fern"], "props": [("spruce_log", {"axis": "x"}), ("barrel", {"facing": "up", "open": "false"})]},
    "snowy": {"verge": ["snow_block", "coarse_dirt"], "edge": ["gravel", "coarse_dirt", "packed_ice"], "inner": ["dirt_path", "cobblestone"],
              "centre": ["cobblestone", "stone_bricks", "gravel", "dirt_path"], "fence": "spruce_fence", "hedge": "spruce_leaves",
              "flowers": ["fern", "sweet_berry_bush", "fern", "fern"], "props": [("spruce_log", {"axis": "x"}), ("barrel", {"facing": "up", "open": "false"})]},
    "desert": {"verge": ["sand", "smooth_sandstone"], "edge": ["sandstone", "gravel", "coarse_dirt"], "inner": ["dirt_path", "smooth_sandstone"],
               "centre": ["smooth_sandstone", "cut_sandstone", "sandstone", "dirt_path"], "fence": "sandstone_wall", "hedge": None,
               "flowers": ["dead_bush", "dead_bush", "short_grass", "dead_bush"], "props": [("barrel", {"facing": "up", "open": "false"}), ("hay_block", {"axis": "y"})]},
    "savanna": {"verge": ["grass_block", "coarse_dirt"], "edge": ["coarse_dirt", "packed_mud", "gravel"], "inner": ["dirt_path", "packed_mud"],
                "centre": ["mud_bricks", "packed_mud", "cobblestone", "dirt_path"], "fence": "acacia_fence", "hedge": "acacia_leaves",
                "flowers": ["short_grass", "dead_bush", "short_grass", "orange_tulip"], "props": [("hay_block", {"axis": "y"}), ("barrel", {"facing": "up", "open": "false"})]}}
WOOD = {"plains": "oak", "taiga": "spruce", "snowy": "spruce", "desert": "spruce", "savanna": "acacia"}
RIM = {"plains": "stone_brick_wall", "taiga": "mossy_cobblestone_wall", "snowy": "stone_brick_wall", "desert": "sandstone_wall", "savanna": "mud_brick_wall"}
WOOL = {"plains": ("red_wool", "yellow_wool"), "taiga": ("brown_wool", "green_wool"), "snowy": ("blue_wool", "white_wool"), "desert": ("orange_wool", "red_wool"),
        "savanna": ("orange_wool", "brown_wool")}   # 9-26: lime read as the rejected colour panels
FENCE_STATE = lambda wood: {"north": "false", "south": "false", "east": "false", "west": "false", "waterlogged": "false"}

def jig(t, x, y, z, ori, name, pool, final, joint="aligned"):
    t.set(x, y, z, M("jigsaw"), {"orientation": ori}, {"id": M("jigsaw"), "name": name, "target": name, "pool": pool, "final_state": final, "joint": joint})

def town_center(fam):
    G.PAL = PAL[fam]; G.ABANDONED = False
    t = Tpl(17, 6, 17); r = random.Random(zlib.crc32(fam.encode()))
    def dist(x, z): return max(0, min(3, min(max(abs(x - 8), abs(z - 8)) - 5, abs(x - 8), abs(z - 8))))
    G.surface(t, r, 5, {(x, z): dist(x, z) for x in range(17) for z in range(17)})
    wd = WOOD[fam]; ground = M(PAL[fam]["centre"][0])
    for x in range(6, 11):                                               # roofed well 5x5
        for z in range(6, 11):
            corner = x in (6, 10) and z in (6, 10); ring = x in (6, 10) or z in (6, 10)
            if corner:
                for y in (1, 2, 3): t.set(x, y, z, M(f"{wd}_fence"))
            elif ring: t.set(x, 1, z, M(RIM[fam]))
            else: t.set(x, 0, z, M("water"), {"level": "0"})
            t.set(x, 4, z, M(f"{wd}_slab"), {"type": "bottom", "waterlogged": "false"})
    t.set(8, 3, 8, M("chain"), {"axis": "y", "waterlogged": "false"}); t.set(8, 2, 8, M("lantern"), {"hanging": "true", "waterlogged": "false"})
    t.set(8, 1, 12, M("bell"), {"attachment": "floor", "facing": "north", "powered": "false"})       # meeting point
    for (x0, z0, wool) in ((2, 2, WOOL[fam][0]), (12, 12, WOOL[fam][1])):  # market stalls
        for dx in range(3):
            for dz in range(3):
                x, z = x0 + dx, z0 + dz
                if dx in (0, 2) and dz in (0, 2):
                    for y in (1, 2): t.set(x, y, z, M(f"{wd}_fence"))
                t.set(x, 3, z, M(wool))
        t.set(x0 + 1, 1, z0 + 2 if x0 < 8 else z0, M(f"{wd}_slab"), {"type": "top", "waterlogged": "false"})
        t.set(x0 + 1, 1, z0 + 1, M("barrel"), {"facing": "up", "open": "false"})
    for (x, z, f) in ((12, 3, "north"), (13, 3, "north"), (3, 13, "south"), (4, 13, "south")):   # benches (back away from the plaza)
        t.set(x, 1, z, M(f"{wd}_stairs"), {"facing": f, "half": "bottom", "shape": "straight", "waterlogged": "false"})
    for (x, z) in ((1, 6), (15, 10), (6, 15), (10, 1)): G.lamp(t, x, z)
    for (x, z, o) in ((8, 0, "north_up"), (8, 16, "south_up"), (0, 8, "west_up"), (16, 8, "east_up")):
        jig(t, x, 1, z, o, "minecraft:street", f"minecraft:village/{fam}/streets", M("air"))
    for (x, z) in ((5, 8), (11, 8)): jig(t, x, 0, z, "up_north", "minecraft:bottom", f"minecraft:village/{fam}/villagers", ground, "rollable")
    jig(t, 8, 0, 4, "up_north", "minecraft:bottom", "dying_world:village_iron_golem", ground, "rollable")
    fix_connections(t); return t

def street_end(fam):
    t = Tpl(7, 4, 2); wd = WOOD[fam]; G.PAL = PAL[fam]
    for x in range(7):
        t.set(x, 0, 0, M(PAL[fam]["edge"][0])); t.set(x, 0, 1, M(PAL[fam]["verge"][0]))
        for z in (0, 1):
            for y in (1, 2, 3): t.set(x, y, z, M("air"))
        if x != 3: t.set(x, 1, 0, M(PAL[fam]["fence"]))
    for x in (0, 6): t.set(x, 2, 0, M(PAL[fam]["fence"]))
    gate = f"minecraft:{wd}_fence_gate[facing=north,open=false,in_wall=false,powered=false]"
    jig(t, 3, 1, 0, "north_up", "minecraft:street", "minecraft:empty", gate)
    fix_connections(t); return t

def villager(fam, prof="none", baby=False):
    t = Tpl(1, 3, 1)
    jig(t, 0, 0, 0, "down_north", "minecraft:bottom", "minecraft:empty", M("air"), "rollable")
    nbt = {"id": NS("minecraft:villager"), "VillagerData": (10, {"type": NS(f"minecraft:{fam}"), "profession": NS(f"minecraft:{prof}"), "level": NI(1)})}
    if baby: nbt["Age"] = NI(-24000)
    t.entity(.5, 0, .5, nbt); return t

def decor(fam, kind):
    wd = WOOD[fam]
    if kind == "lamp":
        t = Tpl(1, 4, 1); t.set(0, 1, 0, M(f"{wd}_fence")); t.set(0, 2, 0, M(f"{wd}_fence")); t.set(0, 3, 0, M("lantern"), {"hanging": "false", "waterlogged": "false"})
        jig(t, 0, 0, 0, "down_north", "minecraft:bottom", "minecraft:empty", M(f"{wd}_fence")); return t
    t = Tpl(2, 3, 2)
    for x in range(2):
        for z in range(2):
            for y in range(3): t.set(x, y, z, M("air"))
    if kind == "stack":
        t.set(0, 0, 0, M("hay_block"), {"axis": "y"}); t.set(1, 0, 0, M("barrel"), {"facing": "up", "open": "false"}); t.set(0, 1, 0, M("hay_block"), {"axis": "x"})
        jig(t, 0, 0, 1, "down_north", "minecraft:bottom", "minecraft:empty", M("air"))
    elif kind == "planter":
        t.set(0, 0, 0, M("composter"), {"level": "3"}); t.set(1, 0, 0, M(f"{wd}_planks")); t.set(1, 1, 0, M("flower_pot"))
        jig(t, 0, 0, 1, "down_north", "minecraft:bottom", "minecraft:empty", M("air"))
    elif kind == "bench":
        t.set(0, 0, 0, M(f"{wd}_stairs"), {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"})
        t.set(1, 0, 0, M(f"{wd}_stairs"), {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"})
        jig(t, 0, 0, 1, "down_north", "minecraft:bottom", "minecraft:empty", M("air"))
    elif kind == "crates":
        t.set(0, 0, 0, R("weathered_wooden_crate")); t.set(1, 0, 0, M("barrel"), {"facing": "up", "open": "false"}); t.set(0, 1, 0, R("weathered_wooden_crate"))
        jig(t, 1, 0, 1, "down_north", "minecraft:bottom", "minecraft:empty", M("air"))
    return t

def pe(loc, wt, proj="rigid"): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": proj}}
def villages():
    MV = OUT.parent / "minecraft/worldgen/template_pool/village"
    for fam in FAMS:
        d = OUT / f"structure/{fam}/village"; d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.nbt"): old.unlink()
        (d / "town_center.nbt").write_bytes(town_center(fam).bytes()); (d / "street_end.nbt").write_bytes(street_end(fam).bytes())
        vs = [("villager", villager(fam), 10), ("villager_baby", villager(fam, baby=True), 3), ("nitwit", villager(fam, "nitwit"), 1)]
        ds = [(f"decor_{k}", decor(fam, k), wt) for k, wt in (("lamp", 4), ("stack", 2), ("planter", 2), ("bench", 2), ("crates", 1))]
        for n, t, _ in vs + ds: (d / f"{n}.nbt").write_bytes(t.bytes())
        L = lambda n: f"dying_world:{fam}/village/{n}"
        w(OUT / f"worldgen/template_pool/{fam}/town_centers.json", {"fallback": "minecraft:empty", "elements": [pe(L("town_center"), 1)]})
        w(OUT / f"worldgen/template_pool/{fam}/street_ends.json", {"fallback": "minecraft:empty", "elements": [pe(L("street_end"), 1, "terrain_matching")]})
        w(MV / f"{fam}/villagers.json", {"fallback": "minecraft:empty", "elements": [pe(L(n), wt) for n, _, wt in vs]})
        w(MV / f"{fam}/decor.json", {"fallback": "minecraft:empty", "elements": [pe(L(n), wt) for n, _, wt in ds] + [{"weight": 4, "element": {"element_type": "minecraft:empty_pool_element"}}]})
        for pool, fb in (("streets", f"dying_world:{fam}/street_ends"), ("houses", "minecraft:empty")):
            p = MV / f"{fam}/{pool}.json"; j = json.loads(p.read_text()); j["fallback"] = fb; w(p, j)
        sp = OUT / f"worldgen/structure/village_{fam}.json"; j = json.loads(sp.read_text()); j["start_pool"] = f"dying_world:{fam}/town_centers"; w(sp, j)
    g = Tpl(1, 4, 1); jig(g, 0, 0, 0, "down_north", "minecraft:bottom", "minecraft:empty", M("air"), "rollable")   # our own golem piece
    g.entity(.5, 0, .5, {"id": NS("minecraft:iron_golem")}); (OUT / "structure/village_iron_golem.nbt").write_bytes(g.bytes())
    w(OUT / "worldgen/template_pool/village_iron_golem.json", {"fallback": "minecraft:empty", "elements": [pe("dying_world:village_iron_golem", 1)]})
    old = MV / "savanna/town_centers.json"
    if old.exists(): old.unlink()

# ---------------- (D) imported leftovers ----------------
def purge_imported():
    gone = []
    for p in sorted((ROOT / "datapack_imported/data").rglob("*")):
        if not p.is_file() or p.suffix not in (".json", ".nbt"): continue
        b = gzip.decompress(p.read_bytes()) if p.suffix == ".nbt" else p.read_bytes()
        if any(k in b.lower() for k in (b"brutos", b"vsrevamped", b"repurposed")): p.unlink(); gone.append(str(p.relative_to(ROOT)))
    return gone

def main():
    tables(); digsites(); tot = stamp_all(); villages(); gone = purge_imported()
    print(f"9-20: archaeology tables 4; suspicious blocks {tot}; 5 town centres/street ends/villager+decor pools ours; purged imported: {gone}")

if __name__ == "__main__":
    main()
