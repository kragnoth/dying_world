#!/usr/bin/env python3
"""
gen_pass8_5.py - pass 8-5: OUR abandoned watchtower (replaces watchtower_building:abandoned_watchtower). Safe to re-run.
2 worn variants in structure/watchtower/:
  timber_1 (9x19x9): stone-brick ground storey (door, chest, barrel), 4 log legs to the lookout, plank backing + ladder on the north side,
           fence cross-rails, lookout platform y11 with fence rail, unlit signal brazier (campfire), bell, chest; spruce pyramid-ish gable roof.
  stone_1 (7x17x7): square cobble/stone-brick keep tower (wear gradient), ladder inside with 2 landings, crenellated top with a wooden roofed lookout.
Loot dying_world:chests/watchtower (watchman: arrows, bow/crossbow, spyglass, food, torches). Biomes: plains/forests/taiga as before (+ meadow, windswept forest).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from buildkit import *

def timber(seed):
    r = rng("watchtower_timber", seed); W, H, D = 9, 19, 9; t = Tpl(W, H, D)
    for x in range(W):
        for z in range(D):
            t.set(x, 0, z, r.choice([M("coarse_dirt"), M("gravel"), M("dirt_path")]))
            for y in range(1, 4): t.set(x, y, z, M("air"))
    x0, x1 = 2, 6
    for x in range(x0, x1 + 1):                                     # ground storey y0..4 stone
        for z in range(x0, x1 + 1):
            edge = x in (x0, x1) or z in (x0, x1)
            t.set(x, 0, z, worn(r, M("stone_bricks"), 1.6) if edge else M("spruce_planks"))
            for y in range(1, 5):
                t.set(x, y, z, worn(r, M("cobblestone") if y <= 2 else M("stone_bricks"), 1.8 - y / 4) if edge else M("air"))
    for x in range(x0 + 1, x1):
        for z in range(x0 + 1, x1): t.set(x, 5, z, M("spruce_planks"))
    door(t, 4, 1, x1, "spruce", "south"); t.set(x0, 2, 4, M("iron_bars")); t.set(x1, 2, 4, M("iron_bars"))
    chest(t, 5, 1, 3, "west", "watchtower"); t.set(3, 1, 5, M("barrel"), {"facing": "up", "open": "false"}); hang_lantern(t, 4, 4, 4)
    for (x, z) in ((x0, x0), (x1, x0), (x0, x1), (x1, x1)):         # legs
        for y in range(5, 15): t.set(x, y, z, M("spruce_log"), {"axis": "y"})
    for y in range(5, 12): t.set(4, y, x0, M("spruce_planks"))      # ladder backing (north)
    for y in range(1, 12): t.set(4, y, x0 + 1, M("ladder"), {"facing": "south", "waterlogged": "false"})
    t.set(4, 5, x0 + 1, M("ladder"), {"facing": "south", "waterlogged": "false"})
    for y in (7, 10):                                              # fence rails between legs
        for i in range(x0 + 1, x1):
            for (x, z) in ((i, x0), (i, x1), (x0, i), (x1, i)):
                if (x, z) != (4, x0): t.set(x, y, z, M("spruce_fence"))
    for x in range(x0 - 1, x1 + 2):                                 # lookout platform y11 (1 overhang)
        for z in range(x0 - 1, x1 + 2):
            if (x, z) == (4, x0 + 1): continue
            t.set(x, 11, z, M("spruce_planks") if r.random() < .9 else M("stripped_spruce_wood"))
            if x in (x0 - 1, x1 + 1) or z in (x0 - 1, x1 + 1): t.set(x, 12, z, M("spruce_fence"))
    t.set(4, 12, x0 - 1, M("air"))
    t.set(5, 12, 5, M("campfire"), {"facing": "north", "lit": "false", "signal_fire": "false", "waterlogged": "false"})
    chest(t, 3, 12, 5, "east", "watchtower")
    t.set(4, 14, 4, M("bell"), {"attachment": "ceiling", "facing": "north", "powered": "false"})
    for (x, z) in ((x0, x0), (x1, x0), (x0, x1), (x1, x1)): t.set(x, 12, z, M("spruce_log"), {"axis": "y"})
    gable(t, r, x0, x1, x0, x1, 15, "spruce", fill="spruce_planks")
    for x in range(x0 + 1, x1):                                    # ceiling under the roof (bell hangs from it)
        for z in range(x0 + 1, x1): t.set(x, 15, z, M("spruce_planks"))
    fix_connections(t)
    return t

def stone(seed):
    r = rng("watchtower_stone", seed); W, H, D = 9, 18, 9; t = Tpl(W, H, D)
    for x in range(W):
        for z in range(D):
            t.set(x, 0, z, r.choice([M("coarse_dirt"), M("gravel"), M("cobblestone")]))
            for y in range(1, 4): t.set(x, y, z, M("air"))
    x0, x1, TOP = 1, 7, 13
    for y in range(0, TOP + 1):
        for x in range(x0, x1 + 1):
            for z in range(x0, x1 + 1):
                edge = x in (x0, x1) or z in (x0, x1)
                if edge or y == 0: t.set(x, y, z, worn(r, M("cobblestone") if y <= 3 else M("stone_bricks"), max(.4, 1.8 - y / 6)))
                else: t.set(x, y, z, M("air"))
    for y in (5, 9, TOP):                                          # landings
        for x in range(x0 + 1, x1):
            for z in range(x0 + 1, x1): t.set(x, y, z, M("spruce_planks"))
    for y in range(1, TOP + 1): t.set(4, y, x0 + 1, M("ladder"), {"facing": "south", "waterlogged": "false"})
    door(t, 4, 1, x1, "spruce", "south")
    for y in (3, 7, 11):
        for (x, z) in ((x0, 4), (x1, 4), (4, x1)): t.set(x, y, z, M("iron_bars"))
    for i in range(x0, x1 + 1):                                    # crenellation
        for (x, z) in ((i, x0), (i, x1), (x0, i), (x1, i)):
            if i % 2 == 1: t.set(x, TOP + 1, z, worn(r, M("stone_bricks"), .5))
    for (x, z) in ((2, 2), (6, 2), (2, 6), (6, 6)):                 # wooden lookout roof on posts
        for y in (TOP + 1, TOP + 2): t.set(x, y, z, M("spruce_fence"))
    for x in range(1, 8):
        for z in range(1, 8):
            if 2 <= x <= 6 and 2 <= z <= 6: slab(t, x, TOP + 3, z, "spruce")
    chest(t, 5, TOP + 1, 4, "west", "watchtower"); t.set(3, TOP + 1, 5, M("campfire"), {"facing": "north", "lit": "false", "signal_fire": "false", "waterlogged": "false"})
    chest(t, 6, 1, 6, "north", "watchtower"); hang_lantern(t, 4, 4, 4); bed(t, 2, 6, 5, "white", "north")
    fix_connections(t)
    return t

def loot():
    w(OUT / "loot_table/chests/watchtower.json", {"type": "minecraft:chest", "pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 6}, "entries": [
            item("arrow", 8, 4, 16), item("bread", 5, 1, 4), item("cooked_beef", 3, 1, 3), item("apple", 4, 1, 4), item("torch", 5, 3, 10),
            item("coal", 4, 2, 6), item("string", 3, 2, 5), item("iron_nugget", 4, 3, 9), item("paper", 3, 1, 4)]},
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": [
            item("bow", 4, worn=True), item("crossbow", 3, worn=True), item("spyglass", 3), item("iron_sword", 2, worn=True), item("shield", 2, worn=True),
            item("chainmail_helmet", 2, worn=True), item("map", 2), item("goat_horn", 1)]}]})

def main():
    N = OUT / "structure/watchtower"; N.mkdir(parents=True, exist_ok=True)
    (N / "timber_1.nbt").write_bytes(timber(1).bytes()); (N / "stone_1.nbt").write_bytes(stone(1).bytes())
    register("abandoned_watchtower", "watchtower/start", [("dying_world:watchtower/timber_1", 3), ("dying_world:watchtower/stone_1", 2)],
             ["minecraft:plains", "minecraft:birch_forest", "minecraft:forest", "minecraft:flower_forest", "minecraft:taiga",
              opt("minecraft:meadow"), opt("minecraft:windswept_forest")])
    loot(); print("8-5: timber + stone watchtower, pool, loot, structure dying_world:abandoned_watchtower -> own pool")

if __name__ == "__main__":
    main()
