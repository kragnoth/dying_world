#!/usr/bin/env python3
"""
gen_pass8_3.py - pass 8-3: OUR lighthouse (replaces createnewbeg:lighthouse). Safe to re-run.
Octagonal tower (r=3, 7x7) ~24 high: stone-brick base -> white terracotta shaft with 2 red bands (wear gradient: more moss/cracks low,
cleaner high), ladder on the inside north wall with 3 landing floors (hole at the ladder), gallery balcony with iron-bar rail at the top,
glass lantern room with a centre column carrying 4 lit sodium floodlights (one per side, pointing out) + glowstone core, copper/dark-oak cap.
Keeper's cottage on the east side (spruce/stone, bed, table + chairs, stove, chest, door into the tower).
Loot dying_world:chests/lighthouse (keeper: food, maps, spyglass, compass, nautical bits, R&R lamp parts). Biomes: beaches + stony shores.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from buildkit import *

CCW = {"north": "west", "west": "south", "south": "east", "east": "north"}
def roof(t, cx, cz, B):
    """8-12 (user): tall steep DEEPSLATE pyramid, deepslate wall finial on top, no copper / lightning rod.
    3 tiers: stair ring radius r at y=B+2k, solid tiles inside it at y and y+1 (steep 2:1 profile); corner stairs get outer shapes."""
    for k, r in enumerate((3, 2, 1)):
        y = B + 2 * k
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                dx, dz = x - cx, z - cz
                if max(abs(dx), abs(dz)) < r:
                    t.set(x, y, z, M("deepslate_tiles")); t.set(x, y + 1, z, M("deepslate_tiles")); continue
                f = "south" if dz == -r else "north" if dz == r else "east" if dx == -r else "west"    # high side towards the centre
                shape = "straight"
                if abs(dx) == r and abs(dz) == r:                    # corner: vanilla outer-shape rule (neighbour behind = the other edge)
                    other = "east" if dx == -r else "west"
                    shape = "outer_left" if other == CCW[f] else "outer_right"
                t.set(x, y, z, M("deepslate_tile_stairs"), {"facing": f, "half": "bottom", "shape": shape, "waterlogged": "false"})
    top = B + 6
    t.set(cx, top, cz, M("deepslate_tiles")); t.set(cx, top + 1, cz, M("deepslate_tile_wall")); t.set(cx, top + 2, cz, M("deepslate_tile_wall"))

def lighthouse(seed):
    r = rng("lighthouse", seed); W, H, D = 16, 36, 11; t = Tpl(W, H, D)
    cx, cz, rad = 5, 5, 3
    inside = lambda x, z: abs(x - cx) <= rad and abs(z - cz) <= rad and abs(x - cx) + abs(z - cz) <= rad + 1
    wall = lambda x, z: inside(x, z) and not all(inside(x + dx, z + dz) for dx, dz in H4.values())
    TOP = 22                                                     # gallery floor
    for x in range(W):
        for z in range(D):
            t.set(x, 0, z, worn(r, M("stone_bricks"), 1.5) if (abs(x - cx) <= rad + 1 and abs(z - cz) <= rad + 1) else r.choice([M("gravel"), M("coarse_dirt"), M("cobblestone")]))
            for y in range(1, 4): t.set(x, y, z, M("air"))
    for y in range(1, TOP):
        k = max(.3, 1.8 - y / 10)                                # wear gradient: heavier near the ground
        for x in range(cx - rad, cx + rad + 1):
            for z in range(cz - rad, cz + rad + 1):
                if not inside(x, z): continue
                if wall(x, z):
                    if y <= 4: b = worn(r, M("stone_bricks"), k)
                    elif y in (9, 10, 16, 17): b = M("red_terracotta")
                    else: b = worn(r, M("white_terracotta"), k)
                    t.set(x, y, z, b)
                else: t.set(x, y, z, M("air"))
    for y in (7, 13, 19):                                         # landing floors with a ladder hole
        for x in range(cx - rad, cx + rad + 1):
            for z in range(cz - rad, cz + rad + 1):
                if inside(x, z) and not wall(x, z): t.set(x, y, z, M("spruce_planks"))
    for y in range(1, TOP + 1): t.set(cx, y, cz - rad + 1, M("ladder"), {"facing": "south", "waterlogged": "false"})
    for y in (6, 12, 18):                                         # small windows (panes) on alternating sides
        for x, z in ((cx, cz + rad), (cx + rad, cz), (cx - rad, cz)):
            t.set(x, y, z, M("glass_pane"))
    t.set(cx - 2, 14, cz + 1, M("barrel"), {"facing": "up", "open": "false"}); t.set(cx - 2, 15, cz + 1, M("lantern"), {"hanging": "false", "waterlogged": "false"})  # lantern stands on a (lootless) barrel
    t.set(cx + 1, 8, cz - 1, M("barrel"), {"facing": "up", "open": "false"})
    # gallery y22: SQUARE platform radius 5 (2-wide walkway around the tower, 8-7 feedback) with a straight iron-bar rail on its edge
    for x in range(cx - 5, cx + 6):
        for z in range(cz - 5, cz + 6):
            edge = max(abs(x - cx), abs(z - cz)) == 5
            t.set(x, TOP, z, M("stone_brick_slab") if edge else M("polished_andesite"), {"type": "top", "waterlogged": "false"} if edge else None)
            if edge: t.set(x, TOP + 1, z, M("iron_bars"))
    t.set(cx, TOP, cz - rad + 1, M("ladder"), {"facing": "south", "waterlogged": "false"})
    t.set(cx, TOP + 1, cz - rad + 1, M("air"))
    for y in range(TOP + 1, TOP + 5):                             # lantern room: radius 2 ring of glass on a dark-oak frame
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                ring = max(abs(x - cx), abs(z - cz)) == 2
                if not ring: continue
                corner = abs(x - cx) == 2 and abs(z - cz) == 2
                if (x, z) == (cx, cz - 2) and y <= TOP + 2: t.set(x, y, z, M("air")); continue    # doorway to the gallery (ladder side)
                t.set(x, y, z, M("dark_oak_log") if corner else M("glass_pane") if y < TOP + 4 else M("polished_deepslate"), {"axis": "y"} if corner else None)
    for y in range(TOP + 1, TOP + 4): t.set(cx, y, cz, M("polished_andesite") if y != TOP + 2 else M("glowstone"))
    for f in H4:                                                  # 4 lit floodlights on the centre column, pointing out
        dx, dz = H4[f]; t.set(cx + dx, TOP + 2, cz + dz, R("sodium_floodlight"), {"facing": f, "lit": "true"})
    roof(t, cx, cz, TOP + 5)
    # tower door (south) + keeper's cottage east x9..14 z2..8
    door(t, cx, 1, cz + rad, "spruce", "south")
    x0, x1, z0, z1 = 9, 14, 2, 8
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
            t.set(x, 0, z, worn(r, M("cobblestone"), 1.4) if edge else M("spruce_planks"))
            for y in range(1, 4):
                if not edge: t.set(x, y, z, M("air"))
                elif corner: t.set(x, y, z, M("stripped_spruce_log"), {"axis": "y"})
                else: t.set(x, y, z, worn(r, M("cobblestone"), 1.4) if y == 1 else M("spruce_planks"))
    gable(t, r, x0 + 1, x1, z0, z1, 4, "spruce")                 # eave starts at x0 so it never cuts into the tower
    for x in range(x0 + 1, x1): t.set(x, 3, z0, M("spruce_planks"))
    t.set(cx + rad, 1, cz, M("air")); t.set(cx + rad, 2, cz, M("air"))        # passage tower <-> cottage (tower wall x8 / cottage wall x9)
    door(t, x0, 1, 5, "spruce", "west")
    door(t, x1, 1, 6, "spruce", "east")
    for x, z in ((12, z0), (x1, 4)): t.set(x, 2, z, M("glass_pane"))
    bed(t, 13, 1, 3, "blue", "north"); chest(t, 11, 1, 3, "south", "lighthouse"); table(t, 12, 1, 6)
    chair(t, 11, 1, 6, "spruce", "west"); chair(t, 12, 1, 7, "spruce", "south")   # back away from the table
    t.set(13, 1, 7, M("smoker"), {"facing": "west", "lit": "false"}); hang_lantern(t, 12, 3, 5)
    t.set(10, 1, 7, M("barrel"), {"facing": "up", "open": "false"}, {"id": M("barrel"), "LootTable": "dying_world:chests/lighthouse"})
    fix_connections(t)
    return t

def loot():
    w(OUT / "loot_table/chests/lighthouse.json", {"type": "minecraft:chest", "pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 6}, "entries": [
            item("cod", 6, 2, 6), item("salmon", 5, 1, 4), item("bread", 5, 1, 4), item("dried_kelp", 5, 4, 12), item("candle", 3, 1, 3),
            item("glowstone_dust", 4, 2, 8), item("glass_pane", 3, 2, 8), item("string", 3, 2, 6), item("lead", 2), item("paper", 4, 2, 6),
            item("rusted_plating", 2, 2, 6, ns="rustandrebar"), item("copper_ingot", 4, 2, 6)]},
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": [
            item("spyglass", 3), item("compass", 3), item("map", 3), item("fishing_rod", 3, worn=True), item("nautilus_shell", 1), item("prismarine_shard", 2, 1, 4),
            item("name_tag", 1), item("trident", 1, worn=True)]}]})

def main():
    N = OUT / "structure/lighthouse"; N.mkdir(parents=True, exist_ok=True)
    (N / "lighthouse_1.nbt").write_bytes(lighthouse(1).bytes()); (N / "lighthouse_2.nbt").write_bytes(lighthouse(2).bytes())
    register("lighthouse", "lighthouse/start", [("dying_world:lighthouse/lighthouse_1", 1), ("dying_world:lighthouse/lighthouse_2", 1)],
             ["#minecraft:is_beach", opt("minecraft:stony_shore"), opt("minecraft:snowy_beach")])
    loot(); print("8-3: lighthouse x2, pool, loot, structure dying_world:lighthouse -> own pool (beaches/stony shores)")

if __name__ == "__main__":
    main()
