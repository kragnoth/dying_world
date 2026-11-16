#!/usr/bin/env python3
"""
gen_pass8_2.py - pass 8-2: OUR abandoned smithy (replaces createnewbeg:abandoned_smithy). Safe to re-run.

2 script-built variants (structure/smithy/smithy_{1,2}.nbt), vanilla materials + a few Rust & Rebar accents, WORN not ruined
(user rule: wear = moss / mossy / cracked / lesser versions, never missing walls):
  1 forge house  11x10x9: stone-brick plinth walls + spruce log frame + spruce plank upper walls, dark-oak gable roof (ridge along x),
                 forge (blast furnace + furnace) under a cobble chimney, open-front work bay under a lean-to, anvil/smithing table/grindstone,
                 quench cauldron, ore & coal bins, smith's chest, tool barrel.
  2 open forge   9x8x9: half-walled timber pavilion with roof, central forge hearth + chimney, small locked storeroom (door) with the chest.
Loot: dying_world:chests/smithy (vanilla weaponsmith + toolsmith + armorer pools merged, + iron/coal/R&R scrap).
Structure: dying_world:abandoned_smithy (same id + set as before, now our pool), biomes #dying_world:has_structure/abandoned_smithy
           = any land group (scavenger_outpost_any). beard_box (no floating). createnewbeg no longer referenced.
"""
import json, random, sys, zipfile, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from gen_pass4_2a import M, R, w, item, OUT
from gen_pass4_2b import lbarrel
from buildkit import fix_connections

ROOT = Path(__file__).resolve().parent.parent
LOOTZ = zipfile.ZipFile(ROOT / "reference/loot_and_recipes.zip")

def worn(r, name):
    """replace-only wear: mossy / cracked / lesser versions"""
    p = r.random()
    if name == M("cobblestone"): return M("mossy_cobblestone") if p < .3 else name
    if name == M("stone_bricks"): return M("mossy_stone_bricks") if p < .2 else M("cracked_stone_bricks") if p < .35 else name
    if name == M("spruce_planks"): return M("stripped_spruce_wood") if p < .06 else name
    return name

def chest(t, x, y, z, facing, table="smithy"):
    t.set(x, y, z, M("chest"), {"facing": facing, "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": f"dying_world:chests/{table}"})

def gable(t, r, x0, x1, z0, z1, y, mat="dark_oak"):
    """roof over x0..x1 / z0..z1 with 1-block eaves, ridge along x; gable ends filled with planks. returns ridge y"""
    for x in range(x0, x1 + 1):                                   # top plate (8-7 feedback: no gap between wall top and roof)
        for zz in (z0, z1): t.set(x, y, zz, worn(r, M("spruce_planks")))
    k = 0
    while True:
        za, zb = z0 - 1 + k, z1 + 1 - k
        if za > zb: break
        for x in range(x0 - 1, x1 + 2):
            if za == zb: t.set(x, y + k, za, M(f"{mat}_slab"), {"type": "bottom", "waterlogged": "false"})
            else:
                t.set(x, y + k, za, M(f"{mat}_stairs"), {"facing": "south", "half": "bottom", "shape": "straight", "waterlogged": "false"})
                t.set(x, y + k, zb, M(f"{mat}_stairs"), {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"})
        if k >= 1:
            for x in (x0, x1):
                for zz in range(za, zb + 1): t.set(x, y + k - 1, zz, worn(r, M("spruce_planks")))
        if zb - za <= 1: break
        k += 1
    for _ in range(3):                                            # a little moss on the eaves (wear, not holes)
        x = r.randint(x0, x1); zz = r.choice([z0 - 1, z1 + 1])
        if r.random() < .5: t.set(x, y + 1, zz, M("moss_carpet"))
    return y + k

def smithy_house(seed):
    r = random.Random(zlib.crc32(b"smithy_house") + seed); W, H, D = 11, 11, 9; t = Tpl(W, H, D)
    for x in range(W):
        for z in range(D):
            t.set(x, 0, z, worn(r, M("cobblestone")) if 1 <= x <= 9 and 1 <= z <= 7 else r.choice([M("coarse_dirt"), M("gravel"), M("dirt_path")]))
            for y in range(1, 4): t.set(x, y, z, M("air"))
    x0, x1, z0, z1 = 1, 9, 1, 5                                   # enclosed house x1..9 z1..5; work bay z6..7 (open front, south)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
            t.set(x, 0, z, worn(r, M("stone_bricks")) if edge else M("spruce_planks") if r.random() < .7 else worn(r, M("cobblestone")))
            for y in range(1, 5):
                if not edge: t.set(x, y, z, M("air")); continue
                if corner: t.set(x, y, z, M("spruce_log"), {"axis": "y"}); continue
                t.set(x, y, z, worn(r, M("stone_bricks")) if y <= 2 else worn(r, M("spruce_planks")))
    for x in range(x0, x1 + 1):                                    # top beam ring y4 = stripped logs along walls
        for z in (z0, z1): t.set(x, 4, z, M("stripped_spruce_log"), {"axis": "x"})
    for z in range(z0, z1 + 1):
        for x in (x0, x1): t.set(x, 4, z, M("stripped_spruce_log"), {"axis": "z"})
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)): t.set(x, 4, z, M("spruce_log"), {"axis": "y"})
    for x in (3, 7): t.set(x, 3, z0, M("spruce_trapdoor"), {"facing": "north", "half": "top", "open": "true", "powered": "false", "waterlogged": "false"})  # shutters
    for x in (3, 7): t.set(x, 2, z0, M("iron_bars"), {"east": "false", "west": "false", "north": "false", "south": "false", "waterlogged": "false"})
    t.set(x0, 2, 3, M("iron_bars"), {"east": "false", "west": "false", "north": "false", "south": "false", "waterlogged": "false"})
    for x in (4, 5, 6):                                            # wide opening to the work bay
        for y in (1, 2, 3): t.set(x, y, z1, M("air"))
    t.set(5, 3, z1, M("spruce_planks"))
    t.set(4, 3, z1, M("spruce_stairs"), {"facing": "east", "half": "top", "shape": "straight", "waterlogged": "false"})
    t.set(6, 3, z1, M("spruce_stairs"), {"facing": "west", "half": "top", "shape": "straight", "waterlogged": "false"})
    gable(t, r, x0, x1, z0, z1, 5)
    # lean-to over the work bay z6..7: posts at x1/x9 z7, slab roof y4
    for x in (x0, x1):
        for y in range(1, 4): t.set(x, y, 7, M("spruce_fence"), {"east": "false", "west": "false", "north": "false", "south": "false", "waterlogged": "false"})
    for x in range(x0, x1 + 1):
        for z in (6, 7): t.set(x, 4, z, M("spruce_slab"), {"type": "bottom", "waterlogged": "false"})
    # forge: west end, blast furnace + furnace, chimney up through the roof
    t.set(2, 1, 2, M("blast_furnace"), {"facing": "east", "lit": "false"}); t.set(2, 1, 3, M("furnace"), {"facing": "east", "lit": "false"})
    for y in range(2, 10): t.set(2, y, 2, worn(r, M("cobblestone")) if y > 2 else M("bricks"))
    t.set(2, 2, 3, M("bricks")); t.set(2, 10, 2, M("campfire"), {"facing": "east", "lit": "false", "signal_fire": "false", "waterlogged": "false"})
    t.set(2, 1, 4, M("water_cauldron"), {"level": "3"})
    # work bay tools
    t.set(3, 1, 6, M("chipped_anvil"), {"facing": "east"}); t.set(5, 1, 7, M("smithing_table")); t.set(7, 1, 6, M("grindstone"), {"face": "floor", "facing": "north"})
    t.set(8, 1, 7, R("rusted_drum"), {"axis": "y"}); t.set(2, 1, 7, R("rebar_bundle"), {"axis": "x"})
    # interior: chest, tool barrel, ore/coal bins (barrels), workbench
    chest(t, 8, 1, 2, "west"); lbarrel(t, 8, 1, 4, "smithy")
    t.set(6, 1, 2, M("crafting_table")); t.set(5, 1, 2, M("coal_block"))
    t.set(4, 1, 2, M("iron_bars"), {"east": "false", "west": "false", "north": "false", "south": "false", "waterlogged": "false"})
    t.set(4, 3, 3, M("lantern"), {"hanging": "true", "waterlogged": "false"}); t.set(4, 4, 3, M("chain"), {"axis": "y", "waterlogged": "false"})
    t.set(7, 3, 7, M("lantern"), {"hanging": "true", "waterlogged": "false"})
    # vines on the north wall (wear)
    for x in range(x0 + 1, x1):
        if r.random() < .3:
            for y in range(1, r.randint(2, 4)):
                if t.b.get((x, y, 0), (M("air"),))[0] == M("air"): t.set(x, y, 0, M("vine"), {"south": "true", "north": "false", "east": "false", "west": "false", "up": "false"})
    fix_connections(t)
    return t

def open_forge(seed):
    r = random.Random(zlib.crc32(b"open_forge") + seed); W, H, D = 9, 10, 9; t = Tpl(W, H, D)
    for x in range(W):
        for z in range(D):
            t.set(x, 0, z, worn(r, M("cobblestone")) if 1 <= x <= 7 and 1 <= z <= 7 else r.choice([M("coarse_dirt"), M("gravel")]))
            for y in range(1, 4): t.set(x, y, z, M("air"))
    x0, x1, z0, z1 = 1, 7, 1, 7
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1), (4, z0), (4, z1)):
        for y in range(1, 4): t.set(x, y, z, M("spruce_log"), {"axis": "y"})
    for x in range(x0, x1 + 1):                                  # half walls (fence + plank sill) on the east/west sides only
        for z in (z0, z1):
            if t.b.get((x, 1, z), (M("air"),))[0] == M("air"): t.set(x, 1, z, worn(r, M("cobblestone")))
    for x in range(x0, x1 + 1):
        for z in (z0, z1): t.set(x, 4, z, M("stripped_spruce_log"), {"axis": "x"})
    for z in range(z0, z1 + 1):
        for x in (x0, x1): t.set(x, 4, z, M("stripped_spruce_log"), {"axis": "z"})
    gable(t, r, x0, x1, z0, z1, 5, "spruce")
    # storeroom in the NE corner (x5..7, z1..3), walls + door
    for x in range(5, 8):
        for z in range(1, 4):
            edge = x in (5, 7) or z in (1, 3)
            for y in range(1, 4):
                if edge and t.b.get((x, y, z), (M("air"),))[0] in (M("air"), M("cobblestone"), M("mossy_cobblestone")): t.set(x, y, z, worn(r, M("spruce_planks")))
    t.set(6, 1, 3, M("spruce_door"), {"facing": "south", "half": "lower", "hinge": "left", "open": "false", "powered": "false"})
    t.set(6, 2, 3, M("spruce_door"), {"facing": "south", "half": "upper", "hinge": "left", "open": "false", "powered": "false"})
    chest(t, 6, 1, 2, "south")
    # central hearth: 2 blast furnaces back to back + chimney
    t.set(3, 1, 4, M("blast_furnace"), {"facing": "south", "lit": "false"}); t.set(3, 1, 3, M("bricks"))
    for y in range(2, 9): t.set(3, y, 3, M("bricks") if y < 5 else worn(r, M("cobblestone")))
    t.set(3, 2, 4, M("bricks")); t.set(2, 1, 4, M("water_cauldron"), {"level": "2"})
    t.set(4, 1, 5, M("damaged_anvil"), {"facing": "north"}); t.set(2, 1, 6, M("smithing_table")); lbarrel(t, 6, 1, 6, "smithy")
    t.set(5, 1, 6, R("rusted_drum"), {"axis": "y"}); t.set(6, 1, 5, M("grindstone"), {"face": "floor", "facing": "west"})
    t.set(4, 3, 5, M("lantern"), {"hanging": "true", "waterlogged": "false"}); t.set(4, 4, 5, M("chain"), {"axis": "y", "waterlogged": "false"})
    fix_connections(t)
    return t

def loot():
    pools = []
    for src in ("village_weaponsmith", "village_toolsmith", "village_armorer"):
        j = json.loads(LOOTZ.read(f"data/minecraft/loot_table/chests/village/{src}.json")); pools += j["pools"]
    pools.append({"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": [
        item("iron_ingot", 8, 2, 6), item("coal", 8, 4, 12), item("raw_iron", 5, 2, 6), item("iron_nugget", 6, 4, 16), item("chain", 3, 2, 6),
        item("rebar_bundle", 3, 1, 4, ns="rustandrebar"), item("rusted_plating", 2, 2, 8, ns="rustandrebar"), item("bucket", 2), item("shears", 2)]})
    w(OUT / "loot_table/chests/smithy.json", {"type": "minecraft:chest", "pools": pools})

def main():
    N = OUT / "structure/smithy"; N.mkdir(parents=True, exist_ok=True)
    (N / "smithy_1.nbt").write_bytes(smithy_house(1).bytes()); (N / "smithy_2.nbt").write_bytes(open_forge(1).bytes())
    w(OUT / "worldgen/template_pool/smithy/start.json", {"fallback": "minecraft:empty", "elements": [
        {"weight": w_, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:smithy/smithy_{n}", "processors": "minecraft:empty", "projection": "rigid"}}
        for n, w_ in ((1, 3), (2, 2))]})
    w(OUT / "tags/worldgen/biome/has_structure/abandoned_smithy.json", {"replace": False, "values": ["#dying_world:has_structure/scavenger_outpost_any"]})
    w(OUT / "worldgen/structure/abandoned_smithy.json", {
        "type": "minecraft:jigsaw", "biomes": "#dying_world:has_structure/abandoned_smithy", "max_distance_from_center": 30, "size": 1,
        "project_start_to_heightmap": "WORLD_SURFACE_WG", "spawn_overrides": {}, "start_height": {"absolute": 0}, "start_pool": "dying_world:smithy/start",
        "step": "surface_structures", "terrain_adaptation": "beard_box", "use_expansion_hack": False})
    loot()
    print("8-2: smithy_1 (forge house) + smithy_2 (open forge), pool, loot, structure dying_world:abandoned_smithy -> own pool")

if __name__ == "__main__":
    main()
