#!/usr/bin/env python3
"""
gen_pass9_12.py - pass 9-12: REPLACEMENTS for the disabled monument / trial chambers / ancient city (user decision after 9-8: 'build our replacements').
Run after gen_pass9_11.py (reuses its station kit: hub -> corridors -> rooms, caps). Safe to re-run.
  sunken  = SUNKEN RESEARCH LAB (ocean monument): deep oceans, ocean floor, water-filled prismarine/blue-plating station. 1 persistent ELDER GUARDIAN in the hub
            (vanilla drops: wet sponge, tide trim 20%), guardians spawn in the pieces (prismarine), wet sponge blocks, chests = underwater-ruin loot + sponge/prismarine.
  proving = PROVING GROUNDS (trial chambers): underground (-40..-16, encapsulated), tuff/copper/rusted plating. BREEZE SPAWNER wind-tunnel rooms (breeze rods, wind charges),
            VAULT blocks with the vanilla reward tables (normal: trial key; ominous: ominous trial key -> heavy core/mace, flow/bolt trims, breach/density/wind burst),
            keys from the supply chests (vanilla trial_chambers/supply + keys).
  sculk   = SCULK RESEARCH SITE (ancient city): deep dark, y -45..-30, deepslate station overgrown by sculk; shriekers CAN summon the warden; chests = vanilla
            ancient_city loot (echo shards, swift sneak, ward/silence trims, disc 5 fragments).
"""
import json, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import S as NS, B as NB, I as NI
import gen_pass9_11 as K
from gen_pass9_11 import P, PAL, PAL_OF, corridor, junction, room, cap, pe, salt, pick, ZIP
from gen_pass4_2a import M, R, w, item, OUT
from buildkit import full

PAL["sea"] = dict(wall=[(M("prismarine_bricks"), .4), (M("dark_prismarine"), .25), (M("prismarine"), .15), (R("industrial_blue_plating"), .2)],
                  base=[(M("dark_prismarine"), 1)], trim=[(R("industrial_blue_plating"), 1)],
                  floor=[(M("prismarine_bricks"), .5), (R("tread_plate"), .2), (M("dark_prismarine"), .3)], ceil=[(M("dark_prismarine"), .7), (M("prismarine_bricks"), .3)],
                  pillar=M("dark_prismarine"), light=(M("sea_lantern"), None), light_on=(M("sea_lantern"), None), lit=.7, pot="potted_dead_bush", fill=M("water"))
PAL["proving"] = dict(wall=[(M("tuff_bricks"), .4), (M("polished_tuff"), .2), (M("chiseled_tuff"), .05), (M("weathered_cut_copper"), .15), (R("rusted_plating"), .2)],
                  base=[(M("tuff_bricks"), .7), (R("sooty_brick"), .3)], trim=[(M("oxidized_cut_copper"), .7), (R("riveted_rusted_plating"), .3)],
                  floor=[(M("polished_tuff"), .4), (R("tread_plate"), .3), (M("tuff_tiles"), .3)], ceil=[(M("tuff_bricks"), .7), (M("weathered_copper_grate"), .3)],
                  pillar=R("salvaged_steel_block"), light=(R("caged_lamp"), {"facing": "down", "lit": "false"}), light_on=(M("copper_bulb"), {"lit": "true", "powered": "false"}),
                  lit=.6, pot="potted_cactus", windows=False)
PAL["sculk"] = dict(wall=[(M("deepslate_tiles"), .35), (M("cracked_deepslate_tiles"), .15), (M("deepslate_bricks"), .25), (M("polished_deepslate"), .1), (M("sculk"), .15)],
                  base=[(M("cobbled_deepslate"), .6), (M("sculk"), .4)], trim=[(M("polished_deepslate"), .8), (M("reinforced_deepslate"), .2)],
                  floor=[(M("sculk"), .45), (M("deepslate_tiles"), .3), (M("polished_deepslate"), .25)], ceil=[(M("deepslate_tiles"), .7), (M("sculk"), .3)],
                  pillar=M("polished_basalt"), light=(M("sculk_vein"), {"up": "true", "down": "false", "north": "false", "south": "false", "east": "false", "west": "false", "waterlogged": "false"}),
                  light_on=(M("sculk_vein"), {"up": "true", "down": "false", "north": "false", "south": "false", "east": "false", "west": "false", "waterlogged": "false"}),
                  lit=0, pot="potted_dead_bush", windows=False)
PAL_OF.update({"sunken": "sea", "proving": "proving", "sculk": "sculk"})
SITES = ("sunken", "proving", "sculk")

def vault(p, x, y, z, facing, ominous):
    p.b(x, y, z, M("vault"), {"facing": facing, "ominous": str(ominous).lower(), "vault_state": "inactive"},
        {"id": M("vault"), "config": (10, {"loot_table": NS("minecraft:chests/trial_chambers/reward" + ("_ominous" if ominous else "")),
                                           "key_item": (10, {"id": NS("minecraft:" + ("ominous_trial_key" if ominous else "trial_key")), "count": NI(1)})})})

def spawner(p, x, y, z, mob):
    p.b(x, y, z, M("spawner"), None, {"id": M("mob_spawner"), "SpawnData": (10, {"entity": (10, {"id": NS(M(mob))})})})

def sculkify(p, k=1.0):
    """overgrowth on top of a finished piece: veins on floors, sensors + shriekers (can summon the warden), never on jigsaws"""
    r = p.r
    for (x, y, z), (name, props, nbt) in list(p.t.b.items()):
        if name != M("air") or y < 1: continue
        below = p.t.b.get((x, y - 1, z), ("",))[0]
        if not full(below): continue
        q = r.random() / k
        if q < .06: p.b(x, y, z, M("sculk_vein"), {"down": "true", "up": "false", "north": "false", "south": "false", "east": "false", "west": "false", "waterlogged": "false"})
        elif q < .075: p.b(x, y, z, M("sculk_sensor"), {"power": "0", "sculk_sensor_phase": "inactive", "waterlogged": "false"})
        elif q < .08: p.b(x, y, z, M("sculk_shrieker"), {"can_summon": "true", "shrieking": "false", "waterlogged": "false"})

def hub(site):
    p = P(site, "hub", 17, 13, 17); p.shell(); r = p.r
    for f in "nwe": p.opening(f); p.jig(f)
    p.opening("s")
    for x in (6, 10):
        for y in range(1, 7): p.blk(x, y, 16, "pillar")
    for x, z in ((3, 3), (13, 3), (3, 13), (13, 13)):
        for y in range(1, 12): p.blk(x, y, z, "pillar")
    for x in (4, 8, 12):
        for z in (4, 12): p.light(x, 11, z)
    if site == "sunken":
        for x in range(6, 11):
            for z in range(6, 11):
                if x in (6, 10) or z in (6, 10): p.b(x, 1, z, M("prismarine_brick_slab"), {"type": "bottom", "waterlogged": "true"})
        for x, z in ((7, 7), (9, 9), (8, 7), (7, 9)): p.b(x, 1, z, M("wet_sponge"))
        p.b(8, 1, 8, M("sea_lantern"))
        p.t.entity(8.5, 3, 4.5, {"id": NS("minecraft:elder_guardian"), "PersistenceRequired": NB(1)})
        p.chest(14, 1, 8, "west", "store"); p.chest(2, 1, 8, "east", "lab")
    elif site == "proving":
        for x in range(5, 12):
            for z in range(5, 12): p.b(x, 0, z, M("chiseled_copper") if (x + z) % 2 else M("waxed_oxidized_copper"))
        vault(p, 7, 1, 8, "south", False); vault(p, 9, 1, 8, "south", False); vault(p, 8, 1, 6, "south", True)
        p.chest(2, 1, 8, "east", "supply"); p.chest(14, 1, 8, "west", "supply")
    elif site == "sculk":
        for y in range(1, 8):                                 # reinforced-deepslate gate (ancient-city frame)
            for x in (5, 11): p.b(x, y, 8, M("reinforced_deepslate"))
        for x in range(5, 12): p.b(x, 8, 8, M("reinforced_deepslate"))
        p.b(8, 1, 8, M("sculk_catalyst"), {"bloom": "false"})
        for x in (7, 9): p.b(x, 1, 8, M("sculk_shrieker"), {"can_summon": "true", "shrieking": "false", "waterlogged": "false"})
        p.chest(2, 1, 8, "east", "store"); p.chest(14, 1, 8, "west", "archive")
        sculkify(p)
    return p

def special_rooms(site):
    out = []
    if site == "proving":
        p = P(site, "breeze_tunnel", 13, 9, 13, 21); p.shell(); p.opening("n"); p.jig("n", pool=False)
        for x in range(1, 12):
            for y in range(1, 8):
                if x in (1, 11): p.b(x, y, 6, R("rusted_grate"))       # wind baffles
        for x in range(2, 11): p.b(x, 7, 6, R("rusted_grate"))
        p.b(6, 1, 9, M("waxed_oxidized_copper")); spawner(p, 6, 2, 9, "breeze")
        for x in (3, 9): p.b(x, 1, 11, R("rusted_encased_cogwheel"), {"axis": "z", "top_shaft": "true", "bottom_shaft": "true"})
        p.chest(1, 1, 3, "east", "breeze"); p.light(6, 7, 3)
        out.append((p, 3))
        p = P(site, "vault_room", 13, 9, 13, 22); p.shell(); p.opening("n"); p.jig("n", pool=False)
        for x in range(3, 10): p.b(x, 1, 10, M("tuff_brick_slab"), {"type": "bottom", "waterlogged": "false"})
        vault(p, 4, 2, 10, "north", False); vault(p, 8, 2, 10, "north", False); vault(p, 6, 2, 10, "north", p.r.random() < .5)
        p.chest(1, 1, 6, "east", "supply"); p.light(6, 7, 6)
        out.append((p, 2))
    return out

def table(name, *pools):
    w(OUT / f"loot_table/chests/{name}.json", {"type": "minecraft:chest", "pools": [{"rolls": {"type": "minecraft:uniform", "min": lo, "max": hi}, "entries": e} for lo, hi, e in pools]})
def vanilla(name):
    j = json.loads(ZIP.read(f"data/minecraft/loot_table/chests/{name}.json")); j.pop("random_sequence", None); return j

def loot():
    tech = [item("iron_ingot", 8, 2, 6), item("copper_ingot", 8, 3, 9), item("redstone", 6, 4, 12), item("coal", 6, 4, 12), item("gold_ingot", 3, 1, 3)]
    books = [item("paper", 8, 3, 9), item("book", 6, 1, 3), {"type": "minecraft:item", "name": "minecraft:book", "weight": 4, "functions": [{"function": "minecraft:enchant_randomly"}]}]
    camp = [item("bread", 8, 2, 5), item("torch", 6, 4, 12), item("string", 4, 2, 6), item("candle", 3, 1, 4)]
    sea = [item("wet_sponge", 6, 1, 3), item("sponge", 3, 1, 2), item("prismarine_shard", 8, 3, 9), item("prismarine_crystals", 6, 2, 6), item("sea_lantern", 3, 1, 2),
           item("nautilus_shell", 2), item("dark_prismarine", 3, 2, 6)]
    for k in ("lab", "engine", "archive", "quarters", "store"):
        u = vanilla("underwater_ruin_big"); u["pools"].append({"rolls": {"type": "minecraft:uniform", "min": 1, "max": 3}, "entries": sea})
        if k == "store": u["pools"].append({"rolls": 1, "entries": [item("tide_armor_trim_smithing_template", 1), {"type": "minecraft:empty", "weight": 5}]})
        w(OUT / f"loot_table/chests/research_sunken_{k}.json", u)
        w(OUT / f"loot_table/chests/research_sculk_{k}.json", vanilla("ancient_city_ice_box" if k == "quarters" else "ancient_city"))
    keys = [item("trial_key", 6, 1, 2), item("ominous_trial_key", 1)]
    sup = vanilla("trial_chambers/supply"); sup["pools"].append({"rolls": 1, "entries": keys + [{"type": "minecraft:empty", "weight": 3}]})
    w(OUT / "loot_table/chests/research_proving_supply.json", sup)
    table("research_proving_breeze", (1, 2, [item("trial_key", 1, 1, 2)]), (0, 1, [item("ominous_trial_key", 1)]), (2, 4, [item("wind_charge", 4, 2, 6), item("arrow", 4, 4, 12)]))
    for k in ("lab", "engine", "archive", "quarters", "store"):
        w(OUT / f"loot_table/chests/research_proving_{k}.json", vanilla("trial_chambers/" + {"lab": "intersection", "engine": "intersection_barrel", "archive": "corridor",
                                                                                              "quarters": "entrance", "store": "supply"}[k]))

STRUCT = {
    "sunken": dict(biomes=["#minecraft:is_deep_ocean"], h={"absolute": 0}, proj="OCEAN_FLOOR_WG", adapt="beard_box", step="surface_structures",
                   spawns={"monster": {"bounding_box": "piece", "spawns": [{"type": "minecraft:guardian", "weight": 1, "minCount": 2, "maxCount": 4}]}},
                   placement=dict(spacing=32, separation=5, spread_type="triangular")),
    "proving": dict(biomes="#dying_world:has_structure/scavenger_outpost_any", h={"type": "minecraft:uniform", "min_inclusive": {"absolute": -40}, "max_inclusive": {"absolute": -16}},
                    proj=None, adapt="encapsulate", step="underground_structures", spawns={}, placement=dict(spacing=34, separation=12)),
    "sculk": dict(biomes=["minecraft:deep_dark"], h={"type": "minecraft:uniform", "min_inclusive": {"absolute": -45}, "max_inclusive": {"absolute": -30}},
                  proj=None, adapt="beard_box", step="underground_decoration", spawns={}, placement=dict(spacing=24, separation=8)),
}
NAMES = {"sunken": "sunken_research_lab", "proving": "proving_grounds", "sculk": "sculk_research_site"}

def main():
    loot(); n = 0
    for site in SITES:
        d = OUT / f"structure/station/{site}"; d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.nbt"): old.unlink()
        hubloc = hub(site).save(d)
        pieces = [(corridor(site, 9, "corridor_9", 1), 4), (corridor(site, 15, "corridor_15", 2), 3), (junction(site, "nwe", "tee", 3), 2),
                  (junction(site, "nswe", "cross", 4), 1), (junction(site, "ne", "corner", 5), 2)]
        pieces += [(room(site, k, 10 + i), 2) for i, k in enumerate(("lab", "engine", "archive", "quarters", "store"))] + special_rooms(site)
        if site == "sculk":
            for pc, _ in pieces: sculkify(pc)
        wings = [(pc.save(d), wt) for pc, wt in pieces]
        caploc = cap(site).save(d); n += len(wings) + 2
        pool = f"dying_world:station/{site}"
        w(OUT / f"worldgen/template_pool/station/{site}/hub.json", {"fallback": "minecraft:empty", "elements": [pe(hubloc, 1)]})
        w(OUT / f"worldgen/template_pool/station/{site}/wings.json", {"fallback": f"{pool}/caps", "elements": [pe(l, wt) for l, wt in wings]})
        w(OUT / f"worldgen/template_pool/station/{site}/caps.json", {"fallback": "minecraft:empty", "elements": [pe(caploc, 1)]})
        c = STRUCT[site]; name = NAMES[site]
        biomes = c["biomes"]
        if isinstance(biomes, list):
            w(OUT / f"tags/worldgen/biome/has_structure/{name}.json", {"replace": False, "values": biomes}); biomes = f"#dying_world:has_structure/{name}"
        j = {"type": "minecraft:jigsaw", "biomes": biomes, "max_distance_from_center": 64, "size": 6, "spawn_overrides": c["spawns"], "start_height": c["h"],
             "start_pool": f"{pool}/hub", "step": c["step"], "terrain_adaptation": c["adapt"], "use_expansion_hack": False}
        if c["proj"]: j["project_start_to_heightmap"] = c["proj"]
        w(OUT / f"worldgen/structure/{name}.json", j)
        w(OUT / f"worldgen/structure_set/{name}.json", {"structures": [{"structure": f"dying_world:{name}", "weight": 1}],
            "placement": dict({"type": "minecraft:random_spread", "salt": salt(f"dying_world:{name}")}, **c["placement"])})
    print(f"9-12: 3 replacement sites ({', '.join(NAMES.values())}), {n} pieces")

if __name__ == "__main__":
    main()
