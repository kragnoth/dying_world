#!/usr/bin/env python3
"""
gen_pass5_1.py - pass 5-1: SCAVENGER STRONGHOLD (bastion replacement), base + barricades + keep + piglins + bastion loot. Safe to re-run.
Run AFTER gen_pass3c4.py (reads the worn plains-family house entries from our minecraft:village/plains/houses override).

Look (user): an ABANDONED VILLAGE with scavenger material on top; R&R allowed as accents, NOT the main build.
- start = script-built KEEP (17x16x17): ruined two-storey cobble/stone-brick + oak house, patched with corrugated metal, roof lookout,
  floodlights mounted on the outside, treasure room (chest dying_world:chests/scavenger_stronghold_treasure = vanilla bastion_treasure
  => netherite upgrade template GUARANTEED; the keep is the start piece so it always exists), upper floor chest (bastion_other copy).
  4 street jigsaws (minecraft:street, y1, edge centres) like a vanilla town centre.
- streets = vanilla ZOMBIE plains streets COPIED (structure/scavenger_stronghold/streets/*), pools retargeted by byte-replace:
  zombie/streets -> our streets, zombie/houses -> our houses (= worn plains-family houses, villagers already stripped), zombie/decor -> our decor,
  cats / iron_golem / villagers -> minecraft:empty.  Street dead ends (pool fallback) = BARRICADES (scrap + planks + barbed wire).
- decor = vanilla zombie decor + scavenger camps/scrap piles/floodlight posts/loot caches (some camps hold a piglin).
- PIGLINS are PLACED ENTITIES (no KubeJS, no respawn): IsImmuneToZombification, PersistenceRequired, random leather/chainmail/iron/gold armour,
  golden sword or crossbow; brutes guard the treasure (golden axe). Note: vanilla finalizeSpawn may still swap a slot for gold armour (10%/slot).
- no spawn_overrides (only placed guards). Set dying_world:scavenger_strongholds 48/16, 8 chunks from survivor villages, any land biome.
"""
import gzip, json, random, sys, zipfile, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl, S as NS, I as NI, B as NB, F as NF, L as NL
from gen_pass4_2a import M, R, w, item, OUT, CRATES
from gen_pass4_2b import lbarrel

ROOT = Path(__file__).resolve().parent.parent
WG = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip"); NBTZ = zipfile.ZipFile(ROOT / "reference/structures_nbt.zip")
LOOTZ = zipfile.ZipFile(ROOT / "reference/loot_and_recipes.zip")
SH = "dying_world:scavenger_stronghold"
RETARGET = {"minecraft:village/plains/zombie/streets": f"{SH}/streets", "minecraft:village/plains/zombie/houses": f"{SH}/houses",
            "minecraft:village/plains/zombie/decor": f"{SH}/decor", "minecraft:village/common/cats": "minecraft:empty",
            "minecraft:village/common/iron_golem": "minecraft:empty", "minecraft:village/plains/villagers": "minecraft:empty",
            "minecraft:village/plains/zombie/villagers": "minecraft:empty"}
def lp(s): b = s.encode(); return len(b).to_bytes(2, "big") + b

# ---------------- piglins ----------------
ARM = {"head": ["leather_helmet", "chainmail_helmet", "iron_helmet", "golden_helmet"], "chest": ["leather_chestplate", "chainmail_chestplate", "iron_chestplate", "golden_chestplate"],
       "legs": ["leather_leggings", "chainmail_leggings", "iron_leggings", "golden_leggings"], "feet": ["leather_boots", "chainmail_boots", "iron_boots", "golden_boots"]}
def stack(name): return (10, {"id": NS("minecraft:" + name), "count": NI(1)}) if name else (10, {})
def piglin(t, r, x, y, z, brute=False):
    a = {k: (r.choice(v) if r.random() < (.85 if brute else .6) else None) for k, v in ARM.items()}
    hand = "golden_axe" if brute else r.choice(["golden_sword", "golden_sword", "crossbow"])
    t.entity(x + .5, y, z + .5, {"id": NS("minecraft:piglin_brute" if brute else "minecraft:piglin"), "IsImmuneToZombification": NB(1), "PersistenceRequired": NB(1),
        "ArmorItems": NL(10, [stack(a["feet"])[1], stack(a["legs"])[1], stack(a["chest"])[1], stack(a["head"])[1]]),
        "HandItems": NL(10, [stack(hand)[1], {}]), "ArmorDropChances": NL(5, [.085] * 4), "HandDropChances": NL(5, [.085, .085])})

def jig_street(t, x, y, z, facing):
    t.set(x, y, z, M("jigsaw"), {"orientation": facing + "_up"}, {"id": M("jigsaw"), "name": "minecraft:street", "target": "minecraft:street",
          "pool": f"{SH}/streets", "final_state": M("structure_void"), "joint": "aligned"})
def jig_bottom(t, x, z):
    t.set(x, 0, z, M("jigsaw"), {"orientation": "down_west"}, {"id": M("jigsaw"), "name": "minecraft:bottom", "target": "minecraft:bottom",
          "pool": "minecraft:empty", "final_state": M("coarse_dirt"), "joint": "rollable"})

def stone(r):
    p = r.random()
    return M("cobblestone") if p < .35 else M("mossy_cobblestone") if p < .5 else M("stone_bricks") if p < .7 else M("cracked_stone_bricks") if p < .85 else M("mossy_stone_bricks")
def planks(r): return M("oak_planks") if r.random() < .8 else M("spruce_planks")

# ---------------- keep (start piece) ----------------
def keep(seed):
    r = random.Random(zlib.crc32(b"scav_keep") + seed); N_, H = 17, 16; t = Tpl(N_, H, N_); c = 8
    for x in range(N_):
        for z in range(N_):
            t.set(x, 0, z, r.choice([M("dirt_path"), M("coarse_dirt"), M("gravel"), M("cobblestone"), M("dirt_path")]))
            for y in range(1, 5): t.set(x, y, z, M("air"))
    x0, x1 = 3, 13                                            # house 11x11, floors y0 / y5, roof y10
    for x in range(x0, x1 + 1):
        for z in range(x0, x1 + 1):
            edge = x in (x0, x1) or z in (x0, x1); corner = x in (x0, x1) and z in (x0, x1)
            t.set(x, 0, z, M("stone_bricks") if r.random() < .6 else M("cobblestone"))
            for y in range(1, 10):
                if corner: t.set(x, y, z, M("oak_log"), {"axis": "y"}); continue
                if not edge: t.set(x, y, z, M("air")); continue
                if y <= 4: blk = stone(r)
                elif y == 5: blk = M("oak_log") if True else None
                else: blk = planks(r)
                hole = r.random() < (.08 if y <= 4 else .22)
                if hole and y >= 3: blk = R("corrugated_rusted_metal") if r.random() < .55 else M("air")      # patched or open breaches
                if y in (2, 3, 7, 8) and (x == c or z == c) and abs((x if z in (x0, x1) else z) - c) == 2: blk = M("air")  # windows
                t.set(x, y, z, blk, {"axis": "x" if z in (x0, x1) else "z"} if blk == M("oak_log") else None)
            if not edge:
                t.set(x, 5, z, planks(r) if r.random() < .85 else M("air"))                                  # upper floor, a few holes
    for z in range(x0 + 1, x1):                                # roof y10: planks with gaps patched by corrugated sheet metal
        for x in range(x0, x1 + 1):
            p = r.random(); t.set(x, 10, z, M("oak_slab") if p < .5 else R("corrugated_rusted_metal_slab") if p < .85 else M("air"), {"type": "bottom"} if p < .85 else None)
    for x in range(x0, x1 + 1):
        for z in (x0, x1): t.set(x, 10, z, M("stone_brick_wall") if r.random() < .5 else R("barbed_wire"))
    for f, (x, z) in {"N": (c, x0), "S": (c, x1), "W": (x0, c), "E": (x1, c)}.items():  # 3-wide doorways on all sides (street axes)
        for d in (-1, 0, 1):
            for y in (1, 2, 3):
                t.set(x + d if f in "NS" else x, y, z if f in "NS" else z + d, M("air"))
    # ladder to the upper floor + roof hatch
    for y in range(1, 11): t.set(x0 + 1, y, x0 + 1, M("ladder"), {"facing": "south"})
    for y in range(1, 11): t.set(x0 + 1, y, x0, stone(r) if y <= 4 else planks(r))   # solid ladder backing
    # treasure corner (SE quarter of the ground floor) behind a scrap barricade
    for z in range(9, 13): t.set(9, 1, z, R("corrugated_rusted_metal")) if z != 11 else None
    for x in range(10, 13): t.set(x, 1, 9, R("corrugated_rusted_metal")) if x != 11 else None
    t.set(12, 1, 12, M("chest"), {"facing": "north", "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": "dying_world:chests/scavenger_stronghold_treasure"})
    for x, z in ((12, 11), (11, 12), (10, 12)): t.set(x, 1, z, r.choice([M("gold_block"), M("raw_gold_block"), M("gilded_blackstone") if False else M("gold_block")]))
    t.set(12, 2, 12, M("gold_block")) if r.random() < .5 else None
    # ground-floor clutter + loot
    lbarrel(t, 4, 1, 12, "scavenger_stronghold_other"); lbarrel(t, 12, 1, 4, "scavenger_stronghold_bridge")
    for x, z in ((4, 11), (5, 12), (12, 5), (11, 4)): t.set(x, 1, z, r.choice(CRATES + [M("barrel")]) if not t.b[(x, 1, z)][0].endswith("barrel") else t.b[(x, 1, z)][0])
    t.set(6, 1, 6, R("burning_barrel"), {"lit": "true"})
    # upper floor: second chest, bunks (hay), lookout
    t.set(12, 6, 12, M("chest"), {"facing": "west", "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": "dying_world:chests/scavenger_stronghold_other"})
    for x, z in ((5, 11), (6, 11), (11, 5), (11, 6)): t.set(x, 6, z, M("hay_block") if r.random() < .6 else r.choice(CRATES))
    lbarrel(t, 4, 6, 7, "scavenger_stronghold_stable")
    # floodlights mounted on the OUTSIDE wall (jar: facing = direction it points; mount on the opposite side)
    for (x, z, f) in ((c + 2, x0 - 1, "north"), (c - 2, x1 + 1, "south"), (x0 - 1, c + 2, "west"), (x1 + 1, c - 2, "east")):
        mx, mz = {"north": (x, z + 1), "south": (x, z - 1), "west": (x + 1, z), "east": (x - 1, z)}[f]
        t.set(mx, 8, mz, planks(r))                                           # make sure the mount block exists
        t.set(x, 8, z, R("sodium_floodlight"), {"facing": f, "lit": "true" if r.random() < .6 else "false"})
    # courtyard: scrap fence segments on the plot edge (village materials + scrap), leaving the street mouths open
    for i in range(N_):
        for (x, z) in ((i, 0), (i, N_ - 1), (0, i), (N_ - 1, i)):
            if abs(i - c) <= 2 or r.random() < .35: continue
            p = r.random(); t.set(x, 1, z, M("oak_fence") if p < .4 else M("cobblestone_wall") if p < .6 else R("chain_link_fence") if p < .8 else R("corrugated_rusted_metal"))
            if r.random() < .3: t.set(x, 2, z, R("barbed_wire"))
    for x, z in ((1, 1), (15, 15), (1, 15)):
        t.set(x, 1, z, r.choice(CRATES)); t.set(x + (1 if x < 8 else -1), 1, z, R("rusted_drum"), {"axis": "y"})
    jig_street(t, c, 1, 0, "north"); jig_street(t, c, 1, N_ - 1, "south"); jig_street(t, 0, 1, c, "west"); jig_street(t, N_ - 1, 1, c, "east")
    # guards: 2 brutes in the treasure corner, piglins in the house + courtyard + roof
    piglin(t, r, 11, 1, 11, brute=True); piglin(t, r, 10, 1, 10, brute=True)
    for (x, y, z) in ((6, 1, 8), (8, 6, 9), (5, 6, 5), (2, 1, 12), (14, 1, 4), (8, 11, 8)): piglin(t, r, x, y, z)
    return t

# ---------------- barricades (street dead ends) ----------------
def barricade(seed):
    r = random.Random(zlib.crc32(b"scav_barricade") + seed); t = Tpl(3, 5, 7)
    gap = r.random() < .35
    for z in range(7):
        for x in (0, 1):
            h = r.choice((2, 3, 3))
            for y in range(1, h + 1):
                if gap and x == 1 and z in (3,) and y <= 2: continue
                p = r.random()
                blk = M("oak_planks") if p < .25 else M("cobblestone") if p < .4 else R("corrugated_rusted_metal") if p < .65 else \
                      M("oak_log") if p < .75 else r.choice(CRATES) if p < .9 else R("rusted_drum")
                t.set(x, y, z, blk, {"axis": "y"} if blk in (M("oak_log"), R("rusted_drum")) else None)
            if r.random() < .5: t.set(x, h + 1, z, R("barbed_wire"))
    t.set(2, 1, 3, M("jigsaw"), {"orientation": "east_up"}, {"id": M("jigsaw"), "name": "minecraft:street", "target": "minecraft:street",
          "pool": "minecraft:empty", "final_state": M("structure_void"), "joint": "aligned"})
    return t

# ---------------- decor ----------------
def decor(kind, seed):
    r = random.Random(zlib.crc32(kind.encode()) + seed); t = Tpl(3, 5, 3)
    jig_bottom(t, 1, 1)
    if kind == "camp":
        t.set(1, 1, 1, R("burning_barrel"), {"lit": "true"}); t.set(0, 1, 0, r.choice(CRATES)); t.set(2, 1, 2, M("oak_slab"), {"type": "bottom"})
        piglin(t, r, 0, 1, 2)
    elif kind == "scrap":
        for x, z in ((0, 0), (1, 0), (0, 1), (2, 1), (1, 2)):
            if r.random() < .7: t.set(x, 1, z, r.choice(CRATES + [R("rebar_bundle"), M("cobblestone"), M("oak_planks")]))
        t.set(1, 1, 1, R("rusted_drum"), {"axis": "y"})
        if r.random() < .5: piglin(t, r, 2, 1, 0)
    elif kind == "light":
        for y in range(1, 4): t.set(1, y, 1, M("oak_fence"))
        t.set(2, 3, 1, R("sodium_floodlight"), {"facing": "east", "lit": "true"})        # mounted on the fence post (west of it)
    elif kind == "cache":
        lbarrel(t, 1, 1, 1, "scavenger_stronghold_bridge"); t.set(0, 1, 1, r.choice(CRATES))
        piglin(t, r, 2, 1, 2)
    elif kind == "guard":                                     # 5-2: sentry pair behind a low scrap barrier
        for x in range(3): t.set(x, 1, 0, r.choice([M("oak_planks"), M("cobblestone"), R("corrugated_rusted_metal")]))
        t.set(1, 2, 0, R("barbed_wire")) if r.random() < .5 else None
        piglin(t, r, 0, 1, 2); piglin(t, r, 2, 1, 2)
    return t

# ---------------- loot ----------------
def loot():
    rr = "rustandrebar"
    build = [item("stone_bricks", 6, 16, 48), item("bricks", 5, 16, 40), item("deepslate_bricks", 4, 16, 32), item("oak_planks", 5, 16, 48),
             item("spruce_log", 4, 8, 24), item("glass", 4, 8, 24), item("iron_bars", 3, 8, 16), item("smooth_stone", 3, 16, 32), item("polished_andesite", 3, 16, 32),
             item("terracotta", 3, 16, 32), item("lantern", 3, 2, 6), item("chain", 3, 4, 12), item("rebar_concrete", 3, 8, 24, ns=rr),
             item("corrugated_rusted_metal", 2, 8, 16, ns=rr), item("salvaged_steel_block", 1, 2, 4, ns=rr)]
    for src, dst, add in (("treasure", "treasure", False), ("other", "other", True), ("bridge", "bridge", True), ("hoglin_stable", "stable", True)):
        j = json.loads(LOOTZ.read(f"data/minecraft/loot_table/chests/bastion_{src}.json"))
        j.pop("random_sequence", None)
        if add: j["pools"].append({"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": build})
        w(OUT / f"loot_table/chests/scavenger_stronghold_{dst}.json", j)
    t = json.loads((OUT / "loot_table/chests/scavenger_stronghold_treasure.json").read_text())
    assert any(e.get("name") == "minecraft:netherite_upgrade_smithing_template" for p in t["pools"] for e in p["entries"]), "template missing"

# ---------------- main ----------------
def pe(loc, wt, proc="minecraft:empty", proj="rigid", typ="minecraft:single_pool_element"):
    return {"weight": wt, "element": {"element_type": typ, "location": loc, "processors": proc, "projection": proj}}

def main():
    N = OUT / "structure/scavenger_stronghold"
    # streets: copy vanilla zombie plains streets with retargeted pools
    zs = json.loads(WG.read("data/minecraft/worldgen/template_pool/village/plains/zombie/streets.json"))
    els = []; n_re = 0
    for e in zs["elements"]:
        loc = e["element"]["location"]; name = loc.rsplit("/", 1)[1]
        raw = gzip.decompress(NBTZ.read(f"data/minecraft/structure/{loc.split(':')[1]}.nbt"))
        for a, b in RETARGET.items(): n_re += raw.count(lp(a)); raw = raw.replace(lp(a), lp(b))
        p = N / f"streets/{name}.nbt"; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(gzip.compress(raw, mtime=0))
        els.append(pe(f"{SH}/streets/{name}", e["weight"], e["element"]["processors"], "terrain_matching"))
    w(OUT / f"worldgen/template_pool/scavenger_stronghold/streets.json", {"fallback": f"{SH}/barricades", "elements": els})
    # houses: worn plains-family houses from our village override
    hj = json.loads((ROOT / "datapack/data/minecraft/worldgen/template_pool/village/plains/houses.json").read_text())
    houses = [e for e in hj["elements"] if "houses_worn" in json.dumps(e)]
    w(OUT / "worldgen/template_pool/scavenger_stronghold/houses.json", {"fallback": "minecraft:village/plains/terminators", "elements": houses})
    # barricades
    for s in (1, 2, 3): p = N / f"barricade_{s}.nbt"; p.write_bytes(barricade(s).bytes())
    w(OUT / "worldgen/template_pool/scavenger_stronghold/barricades.json", {"fallback": "minecraft:empty",
      "elements": [pe(f"{SH}/barricade_{s}", 1, proj="terrain_matching") for s in (1, 2, 3)]})
    # decor: vanilla zombie decor + ours
    zd = json.loads(WG.read("data/minecraft/worldgen/template_pool/village/plains/zombie/decor.json"))
    dec = list(zd["elements"]); kinds = {"camp": 3, "scrap": 3, "light": 2, "cache": 2, "guard": 3}
    for k, wt in kinds.items():
        for s in (1, 2):
            p = N / f"decor/{k}_{s}.nbt"; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(decor(k, s).bytes())
            dec.append(pe(f"{SH}/decor/{k}_{s}", wt))
    w(OUT / "worldgen/template_pool/scavenger_stronghold/decor.json", {"fallback": "minecraft:empty", "elements": dec})
    # keep (start)
    for s in (1, 2): (N / f"keep_{s}.nbt").write_bytes(keep(s).bytes())
    w(OUT / "worldgen/template_pool/scavenger_stronghold/keep.json", {"fallback": "minecraft:empty", "elements": [pe(f"{SH}/keep_{s}", 1) for s in (1, 2)]})
    loot()
    w(OUT / "worldgen/structure/scavenger_stronghold.json", {
        "type": "minecraft:jigsaw", "biomes": "#dying_world:has_structure/scavenger_outpost_any", "max_distance_from_center": 80, "size": 6,
        "project_start_to_heightmap": "WORLD_SURFACE_WG", "spawn_overrides": {}, "start_height": {"absolute": 0}, "start_pool": f"{SH}/keep",
        "step": "surface_structures", "terrain_adaptation": "beard_thin", "use_expansion_hack": False})
    w(OUT / "worldgen/structure_set/scavenger_strongholds.json", {
        "structures": [{"structure": "dying_world:scavenger_stronghold", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 48, "separation": 16, "salt": zlib.crc32(b"dying_world:scavenger_strongholds") % 2000000000,
                      "exclusion_zone": {"other_set": "dying_world:survivor_villages", "chunk_count": 8}}})
    print(f"5-1: {len(els)} streets ({n_re} jigsaw pools retargeted), {len(houses)} worn houses, 3 barricades, {sum(2 for _ in kinds)} decor, 2 keeps, 4 loot tables")

if __name__ == "__main__":
    main()
