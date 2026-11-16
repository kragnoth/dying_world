#!/usr/bin/env python3
"""
gen_pass8_4.py - pass 8-4: OUR abandoned cabin (replaces abandoned_cabins:abandoned_cabin). Safe to re-run.
3 worn hunter/trapper log cabins (structure/cabin/cabin_{spruce,oak,dark_oak}.nbt, 13x10x11): horizontal log walls with upright corner logs,
cobble footing, stone chimney + fireplace on the east gable, front porch with posts/railing/bench, gable roof, bed, table + chairs,
chest + loot barrel, hides (carpets), crafting table, lantern, windows. Variant 2 adds a lean-to woodshed, variant 3 a loft ladder.
Wear: mossy/cracked footing, moss carpet on the roof, vines; nothing missing.
Loot dying_world:chests/cabin (hunter: food, leather, arrows, bow, traps/string, tools). Biomes: forests + taiga (+ snowy taiga), as before.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from buildkit import *

def cabin(wood, seed, extra):
    r = rng("cabin_" + wood, seed); W, H, D = 13, 11, 11; t = Tpl(W, H, D)
    log, pl, strip = M(f"{wood}_log"), M(f"{wood}_planks"), M(f"stripped_{wood}_log")
    for x in range(W):
        for z in range(D):
            t.set(x, 0, z, r.choice([M("coarse_dirt"), M("podzol"), M("dirt_path"), M("coarse_dirt")]))
            for y in range(1, 4): t.set(x, y, z, M("air"))
    x0, x1, z0, z1 = 2, 9, 1, 6                                       # cabin body; porch z7..8
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
            t.set(x, 0, z, worn(r, M("cobblestone"), 1.4) if edge else pl)
            for y in range(1, 4):
                if not edge: t.set(x, y, z, M("air"))
                elif corner: t.set(x, y, z, log, {"axis": "y"})
                else: t.set(x, y, z, log, {"axis": "x" if z in (z0, z1) else "z"})
    gable(t, r, x0, x1, z0, z1, 4, "dark_oak" if wood != "dark_oak" else "spruce", fill=f"{wood}_planks")
    door(t, 5, 1, z1, wood, "south")
    for x, z in ((3, z1), (7, z1), (x0, 3), (5, z0)): t.set(x, 2, z, M("glass_pane"))
    # chimney east gable (outside x10) + fireplace inside at x9
    for y in range(0, 8): t.set(x1 + 1, y, 3, worn(r, M("cobblestone"), 1.6 - y / 8)); t.set(x1 + 1, y, 4, worn(r, M("cobblestone"), 1.6 - y / 8))
    t.set(x1, 1, 3, M("campfire"), {"facing": "west", "lit": "false", "signal_fire": "false", "waterlogged": "false"})
    t.set(x1, 1, 4, M("cobblestone")); t.set(x1, 2, 3, M("cobblestone")); t.set(x1, 2, 4, M("cobblestone"))
    # porch
    for x in range(x0, x1 + 1):
        for z in (7, 8): t.set(x, 0, z, pl)
    for x in (x0, x1):
        for y in (1, 2, 3): t.set(x, y, 8, M(f"{wood}_fence"))
    for x in range(x0, x1 + 1): slab(t, x, 4, 7, wood); slab(t, x, 4, 8, wood)
    for x in range(x0 + 1, x1):
        if x not in (5,): t.set(x, 1, 8, M(f"{wood}_fence")) if x in (x0 + 1, x1 - 1) else None
    stairs(t, 7, 1, 7, wood, "north"); stairs(t, 8, 1, 7, wood, "north")                          # porch bench (back to the wall)
    t.set(3, 1, 7, M("barrel"), {"facing": "up", "open": "false"}, {"id": M("barrel"), "LootTable": "dying_world:chests/cabin"})
    # interior
    bed(t, 3, 1, 2, "brown", "north"); chest(t, 4, 1, 2, "south", "cabin"); t.set(8, 1, 2, M("crafting_table"))
    table(t, 6, 1, 4, wood); chair(t, 6, 1, 3, wood, "north"); chair(t, 7, 1, 4, wood, "east")
    for x, z in ((4, 4), (5, 3), (4, 5)): t.set(x, 1, z, M("brown_carpet"))
    hang_lantern(t, 5, 3, 4); t.set(8, 1, 5, M("barrel"), {"facing": "up", "open": "false"})
    if extra == "shed":                                                # lean-to woodshed west of the cabin
        for z in range(z0 + 1, z1):
            t.set(x0 - 1, 1, z, log, {"axis": "x"}); t.set(x0 - 1, 2, z, log, {"axis": "x"}) if r.random() < .7 else None
            slab(t, x0 - 1, 3, z, wood); slab(t, x0 - 2, 3, z, wood)
            t.set(x0 - 2, 1, z, M("oak_fence"))
    if extra == "loft":                                                # loft over the west half
        for x in range(x0 + 1, 5):
            for z in range(z0 + 1, z1): slab(t, x, 4, z, wood, "bottom")
        for y in (1, 2, 3): t.set(4, y, 5, M("ladder"), {"facing": "north", "waterlogged": "false"})
        t.set(3, 5, 3, M("hay_block"), {"axis": "y"})
    for _ in range(3):                                                 # vines on the north wall
        x = r.randint(x0 + 1, x1 - 1)
        for y in range(1, r.randint(2, 4)): t.set(x, y, z0 - 1, M("vine"), {"south": "true", "north": "false", "east": "false", "west": "false", "up": "false"})
    fix_connections(t)
    return t

def loot():
    w(OUT / "loot_table/chests/cabin.json", {"type": "minecraft:chest", "pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 6}, "entries": [
            item("cooked_porkchop", 4, 1, 3), item("cooked_rabbit", 4, 1, 3), item("sweet_berries", 5, 2, 8), item("bread", 4, 1, 3), item("leather", 6, 1, 4),
            item("rabbit_hide", 4, 1, 4), item("arrow", 6, 4, 12), item("string", 5, 2, 6), item("feather", 4, 2, 6), item("stick", 4, 3, 8),
            item("coal", 4, 2, 6), item("torch", 4, 2, 8), item("leather_boots", 2, worn=True), item("leather_chestplate", 1, worn=True)]},
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": [
            item("bow", 4, worn=True), item("iron_axe", 3, worn=True), item("stone_axe", 3, worn=True), item("tripwire_hook", 3, 1, 3), item("lead", 2),
            item("compass", 1), item("name_tag", 1), item("crossbow", 1, worn=True)]}]})

def main():
    N = OUT / "structure/cabin"; N.mkdir(parents=True, exist_ok=True)
    for wood, extra in (("spruce", "shed"), ("oak", "loft"), ("dark_oak", "")):
        (N / f"cabin_{wood}.nbt").write_bytes(cabin(wood, 1, extra).bytes())
    register("abandoned_cabin", "cabin/start", [("dying_world:cabin/cabin_spruce", 3), ("dying_world:cabin/cabin_oak", 2), ("dying_world:cabin/cabin_dark_oak", 1)],
             ["minecraft:birch_forest", "minecraft:forest", "minecraft:flower_forest", "minecraft:taiga", "minecraft:snowy_taiga",
              opt("minecraft:old_growth_spruce_taiga"), opt("minecraft:old_growth_pine_taiga"), opt("minecraft:dark_forest")])
    loot(); print("8-4: 3 cabins, pool, loot, structure dying_world:abandoned_cabin -> own pool")

if __name__ == "__main__":
    main()
