#!/usr/bin/env python3
"""
gen_pass9_13.py - pass 9-13: last walkthrough holes (sniffer eggs, sherds, relic disc, leftover trims, allays). Run after 4_3a, 5_1, 9_11, 9_12. Safe to re-run.
  DIG SITES (new, surface): archaeology research camps over a stepped excavation pit full of SUSPICIOUS SAND/GRAVEL with the vanilla archaeology tables:
     arid  : sand pit -> archaeology/desert_pyramid + ocean_ruin_warm (SNIFFER EGG source) ; finds crate = desert_pyramid chest (DUNE trim)
     temp  : gravel pit -> archaeology/trail_ruins_common/_rare (sherds, RELIC disc, wayfinder/raiser/shaper/host trims) + ocean_ruin_cold ; finds crate = jungle_temple chest (WILD trim)
     both  : tent, sorting table, guaranteed BRUSHES in the camp chest, terraced (walkable) pit + scaffold survey tower, lantern posts (head-clear).
  TRIMS: sentry -> scavenger outpost chest (pool, ~25%), vex -> scavenger stronghold treasure (~15%) (pillager outposts / mansions are disabled).
  ALLAYS: a caged, persistent allay specimen in the lab of both overworld research gates (built in gen_pass9_11 room 'lab').
"""
import json, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl, S as NS, B as NB
from gen_pass4_2a import M, R, w, item, OUT
from buildkit import rng, chest, register
from gen_pass9_11 import ZIP, salt

def sus(t, x, y, z, block, table):
    t.set(x, y, z, M(block), {"dusted": "0"}, {"id": M("brushable_block"), "LootTable": f"minecraft:archaeology/{table}"})

def dig(kind):
    """15x10x15; ground level = y4 (structure start_height -4 puts y4 on the surface); pit x3..11 z3..11 stepped down to y1"""
    t = Tpl(15, 10, 15); r = rng("digsite/" + kind)
    soil, loose = (M("sandstone"), M("sand")) if kind == "arid" else (M("dirt"), M("gravel"))
    sblock = "suspicious_sand" if kind == "arid" else "suspicious_gravel"
    tables = (["desert_pyramid"] * 3 + ["ocean_ruin_warm"]) if kind == "arid" else (["trail_ruins_common"] * 5 + ["trail_ruins_rare", "ocean_ruin_cold"])
    for x in range(15):
        for z in range(15):
            t.set(x, 0, z, soil)
            d = max(abs(x - 7), abs(z - 7))                     # 0 centre .. 7 edge
            floor = 1 if d <= 2 else 2 if d <= 3 else 3 if d <= 4 else 4  # stepped terraces
            for y in range(1, floor): t.set(x, y, z, soil)
            if floor < 4:
                t.set(x, floor - 1, z, loose if r.random() < .6 else soil)
                if r.random() < (.35 if d <= 3 else .2): sus(t, x, floor - 1, z, sblock, r.choice(tables))
            for y in range(floor, 10): t.set(x, y, z, M("air"))
    for y in range(1, 5): t.set(5, y, 5, M("scaffolding"), {"bottom": "false", "distance": "0", "waterlogged": "false"})   # terraces are walkable steps; scaffold = survey tower
    # camp on the rim (y4): tent, sorting table, chests, lantern posts
    wool = M("brown_wool" if kind == "arid" else "green_wool")
    for x in range(0, 4):
        for z in range(11, 15):
            if x in (0, 3) and z in (11, 14):
                for y in (4, 5): t.set(x, y, z, M("spruce_fence"), {"north": "false", "south": "false", "east": "false", "west": "false", "waterlogged": "false"})
            t.set(x, 6, z, wool)
    t.set(1, 4, 13, M("barrel"), {"facing": "up", "open": "false"}, {"id": M("barrel"), "LootTable": f"dying_world:chests/digsite_finds_{kind}"})
    chest(t, 2, 4, 13, "north", "digsite_camp")
    for x in (12, 13): t.set(x, 4, 1, M("spruce_planks"))                     # sorting table
    t.set(12, 5, 1, M("decorated_pot"), {"facing": "south", "cracked": "false", "waterlogged": "false"})
    t.set(13, 4, 2, M("spruce_stairs"), {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"})
    for x, z in ((0, 0), (14, 14), (14, 0)):
        for y in (4, 5, 6): t.set(x, y, z, M("spruce_fence"), {"north": "false", "south": "false", "east": "false", "west": "false", "waterlogged": "false"})
        t.set(x, 7, z, M("lantern"), {"hanging": "false", "waterlogged": "false"})
    t.set(3, 4, 6, M("suspicious_sand" if kind == "arid" else "suspicious_gravel"), {"dusted": "0"},
          {"id": M("brushable_block"), "LootTable": "minecraft:archaeology/" + ("desert_well" if kind == "arid" else "trail_ruins_common")})
    return t

def vanilla(name):
    j = json.loads(ZIP.read(f"data/minecraft/loot_table/chests/{name}.json")); j.pop("random_sequence", None); return j

def add_pool(rel, pool, marker):
    p = OUT / f"loot_table/chests/{rel}.json"; j = json.loads(p.read_text())
    j["pools"] = [q for q in j["pools"] if q.get("dw_marker") != marker] + [dict(pool, dw_marker=marker)]
    w(p, j)

def main():
    for kind, tag in (("arid", "concrete_pad_arid"), ("temp", "concrete_pad_temperate")):
        (OUT / "structure/digsite").mkdir(parents=True, exist_ok=True)
        (OUT / f"structure/digsite/{kind}.nbt").write_bytes(dig(kind).bytes())
        name = f"dig_site_{kind}"
        register(name, f"digsite/{kind}", [(f"dying_world:digsite/{kind}", 1)], None, adaptation="beard_thin", size=1, radius=16)
        sj = json.loads((OUT / f"worldgen/structure/{name}.json").read_text())
        sj["biomes"] = f"#dying_world:has_structure/{tag}"; sj["start_height"] = {"absolute": -4}
        w(OUT / f"worldgen/structure/{name}.json", sj)
    w(OUT / "worldgen/structure_set/dig_sites.json", {"structures": [{"structure": "dying_world:dig_site_arid", "weight": 1}, {"structure": "dying_world:dig_site_temp", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 14, "salt": salt("dying_world:dig_sites"),
                      "exclusion_zone": {"other_set": "dying_world:survivor_villages", "chunk_count": 4}}})
    w(OUT / "loot_table/chests/digsite_camp.json", {"type": "minecraft:chest", "pools": [
        {"rolls": 1, "entries": [item("brush", 1)]},
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": [item("bread", 5, 1, 3), item("torch", 5, 3, 8), item("paper", 4, 2, 6), item("string", 3, 1, 4),
                                                                           item("iron_shovel", 2), item("brush", 2), item("candle", 2, 1, 3), item("map", 1)]}]})
    w(OUT / "loot_table/chests/digsite_finds_arid.json", vanilla("desert_pyramid"))
    w(OUT / "loot_table/chests/digsite_finds_temp.json", vanilla("jungle_temple"))
    add_pool("scavenger_outpost", {"rolls": 1, "entries": [item("sentry_armor_trim_smithing_template", 1), {"type": "minecraft:empty", "weight": 3}]}, "9-13 sentry")
    add_pool("scavenger_stronghold_treasure", {"rolls": 1, "entries": [item("vex_armor_trim_smithing_template", 3), {"type": "minecraft:empty", "weight": 17}]}, "9-13 vex")
    print("9-13: 2 dig sites (suspicious sand/gravel, sniffer eggs, sherds, relic, dune/wild + trail trims), sentry/vex trims, caged allays")

if __name__ == "__main__":
    main()
