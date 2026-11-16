#!/usr/bin/env python3
"""
gen_pass4_2b.py - pass 4-2b: MORE MINESHAFT ROOMS + LOOT TUNING (adds to the 4-2a kit; run AFTER gen_pass4_2a.py; safe to re-run).
Rooms are 11x6x9 like the storage closets (door jigsaw at (5,2,0) facing north), so they fit every door alcove unchanged.
  workshop_1/2    : anvil, grindstone, blast furnace, crafting table, barrels (loot mineshaft_workshop), crates
  office_1/2      : bookshelves, lectern, bunk bed, cobwebs, barrels (loot mineshaft_office)
  fuel_store_1/2  : gas cylinders, tar-leaking drums, burning barrel (unlit), oil puddles, danger sign, barrels (loot mineshaft_fuel)
  stash_cell_1    : rare: rebar-heavy cell with a real chest + barrels (loot mineshaft_stash, best loot in the shaft)
Rooms pool: 3 closets + 2+2+2 + 1 stash, empty weight 10 (~half of alcoves still stay empty).
"""
import random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from rr_connect import connect
from gen_pass4_2a import M, R, DOOR, CRATES, wall, jig, lamp, w, elem, item, OUT

def lbarrel(t, x, y, z, table):
    t.set(x, y, z, M("barrel"), {"facing": "up", "open": "false"}, {"id": M("barrel"), "LootTable": f"dying_world:chests/{table}"})

def shell(seed, name, rebar=False):
    r = random.Random(zlib.crc32(name.encode()) + seed); t = Tpl(11, 6, 9)
    for x in range(11):
        for z in range(9):
            for y in range(6):
                inside = 0 < x < 10 and 0 < y < 5 and 0 < z < 8
                if inside: t.set(x, y, z, M("air"))
                elif y == 0: t.set(x, y, z, R("weathered_concrete") if r.random() < .6 else R("rebar_concrete"))
                else: t.set(x, y, z, R("rebar_concrete") if rebar and r.random() < .7 else wall(r))
    for x in range(4, 7):
        for y in range(1, 5): t.set(x, y, 0, M("air"))
    jig(t, 5, 2, 0, "north", DOOR, "minecraft:empty")
    return t, r

def free(t, x, y, z): return not t.has(x, y, z) or t.b[(x, y, z)][0] == M("air")

def workshop(seed):
    t, r = shell(seed, "workshop")
    items = ["anvil", "grindstone", "blast_furnace", "crafting_table", "barrel", "barrel", "barrel", "barrel", "crate"]
    r.shuffle(items)
    for i, it in enumerate(items):
        x = 1 + i
        if it == "anvil": t.set(x, 1, 7, M("anvil"), {"facing": "east"})
        elif it == "grindstone": t.set(x, 1, 7, M("grindstone"), {"face": "floor", "facing": "north"})
        elif it == "blast_furnace": t.set(x, 1, 7, M("blast_furnace"), {"facing": "north", "lit": "false"})
        elif it == "crafting_table": t.set(x, 1, 7, M("crafting_table"))
        elif it == "barrel": lbarrel(t, x, 1, 7, "mineshaft_workshop")
        else: t.set(x, 1, 7, r.choice(CRATES))
    for x in range(4, 7):                              # hazard strip in front of the bench
        for z in range(4, 6): t.set(x, 0, z, R("hazard_plating"))
    for z in range(2, 6):
        for x in (1, 9):
            if r.random() < .45: t.set(x, 1, z, r.choice(CRATES + [R("rusted_drum")]))
    lamp(t, r, 5, 4, 4)
    return t

def office(seed):
    t, r = shell(seed, "office")
    for x in range(1, 5):                              # bookshelf wall
        for y in (1, 2, 3):
            if r.random() < .85: t.set(x, y, 7, M("bookshelf"))
    t.set(6, 1, 7, M("lectern"), {"facing": "north"})
    lbarrel(t, 8, 1, 7, "mineshaft_office"); lbarrel(t, 9, 1, 7, "mineshaft_office")
    t.set(9, 1, 3, M("gray_bed"), {"facing": "north", "part": "foot"})   # bunk along the east wall (head toward north)
    t.set(9, 1, 2, M("gray_bed"), {"facing": "north", "part": "head"})
    for x, z in ((1, 6), (9, 6), (1, 1)):
        if free(t, x, 4, z): t.set(x, 4, z, M("cobweb"))
    if r.random() < .6: t.set(1, 1, 2, r.choice(CRATES))
    t.set(3, 1, 4, M("cauldron"))
    lamp(t, r, 5, 4, 4)
    return t

def fuel_store(seed):
    t, r = shell(seed, "fuel_store")
    t.set(5, 3, 7, R("sign_high_voltage"), {"facing": "north"})
    for x in range(1, 10):
        p = r.random()
        if p < .25: t.set(x, 1, 7, R("gas_cylinders"), {"count": str(r.randint(2, 6)), "facing": "north"})
        elif p < .45: t.set(x, 1, 7, R("tar_leaking_drum"), {"facing": "north"})
        elif p < .6: t.set(x, 1, 7, R("rusted_drum"), {"axis": "y"})
        elif p < .8: lbarrel(t, x, 1, 7, "mineshaft_fuel")
    t.set(r.randint(2, 8), 1, 6, R("burning_barrel"), {"lit": "false"})
    for _ in range(2):
        x, z = r.randint(2, 8), r.randint(2, 5)
        if free(t, x, 1, z): t.set(x, 1, z, R("oil_puddle"))
    for z in range(2, 6):
        if r.random() < .4: t.set(1, 1, z, r.choice([R("rusted_drum"), R("tar_leaking_drum")]) if False else R("rusted_drum"), {"axis": "y"})
    lamp(t, r, 5, 4, 4)
    return t

def stash_cell(seed):
    t, r = shell(seed, "stash_cell", rebar=True)
    t.set(5, 1, 7, M("chest"), {"facing": "north", "type": "single"}, {"id": M("chest"), "LootTable": "dying_world:chests/mineshaft_stash"})
    lbarrel(t, 3, 1, 7, "mineshaft_stash"); lbarrel(t, 7, 1, 7, "mineshaft_stash")
    for x in (2, 4, 6, 8): t.set(x, 1, 7, r.choice([R("rebar_cage"), R("rusted_steel_crate")]))
    t.set(5, 3, 7, R("sign_danger"), {"facing": "north"})
    for x, z in ((1, 6), (9, 6), (1, 1), (9, 1)): t.set(x, 4, z, M("cobweb"))
    for z in range(2, 6):
        for x in (1, 9):
            if r.random() < .5: t.set(x, 1, z, r.choice(CRATES))
    lamp(t, r, 5, 4, 4)
    return t

def table(name, pools):
    w(OUT / f"loot_table/chests/{name}.json", {"pools": [{"rolls": {"type": "minecraft:uniform", "min": lo, "max": hi}, "entries": ents} for lo, hi, ents in pools]})

def loot():
    rr = "rustandrebar"
    table("mineshaft_workshop", [
        (2, 4, [item("iron_ingot", 8, 2, 6), item("iron_nugget", 6, 4, 14), item("copper_ingot", 5, 3, 8), item("chain", 4, 4, 10), item("iron_bars", 3, 6, 14),
                item("flint_and_steel", 2), item("bucket", 2), item("redstone", 3, 4, 9), item("coal", 4, 4, 12)]),
        (1, 2, [item("iron_pickaxe", 3, worn=True), item("iron_axe", 3, worn=True), item("iron_shovel", 2, worn=True), item("iron_sword", 2, worn=True),
                item("shears", 2, worn=True), item("iron_chestplate", 1, worn=True), item("iron_helmet", 1, worn=True), item("rebar_bundle", 4, 2, 8, ns=rr)])])
    table("mineshaft_office", [
        (2, 4, [item("paper", 10, 2, 8), item("book", 6, 1, 3), item("ink_sac", 4, 1, 4), item("feather", 3, 1, 4), item("glass_bottle", 3, 1, 3)]),
        (1, 2, [item("map", 3), item("compass", 3), item("clock", 3), item("spyglass", 1), item("lead", 2, 1, 2), item("name_tag", 1), item("writable_book", 2)])])
    table("mineshaft_fuel", [
        (2, 4, [item("coal", 9, 6, 16), item("charcoal", 5, 4, 10), item("gunpowder", 4, 2, 6), item("flint_and_steel", 2), item("fire_charge", 3, 1, 4),
                item("bucket", 3), item("torch", 4, 6, 16), item("coal_block", 2, 1, 2), item("lava_bucket", 1)])])
    stash_book = {"type": "minecraft:item", "name": "minecraft:book", "weight": 3, "functions": [{"function": "minecraft:enchant_randomly"}]}
    table("mineshaft_stash", [
        (3, 5, [item("iron_ingot", 6, 4, 10), item("gold_ingot", 5, 2, 6), item("diamond", 3, 1, 2), item("emerald", 3, 1, 4), item("redstone", 3, 6, 12),
                item("ender_pearl", 2, 1, 2), item("golden_apple", 1), item("rebar_bundle", 4, 6, 16, ns=rr), item("name_tag", 1), stash_book])])

def main():
    N = OUT / "structure/mineshaft"
    kit = {}
    for s in (1, 2):
        kit[f"workshop_{s}"] = workshop(s); kit[f"office_{s}"] = office(s); kit[f"fuel_store_{s}"] = fuel_store(s)
    kit["stash_cell_1"] = stash_cell(1)
    for n, t in kit.items(): connect(t); (N / f"{n}.nbt").write_bytes(t.bytes())
    names = [f"storage_closet_{s}" for s in (1, 2, 3)] + list(kit)
    w(OUT / "worldgen/template_pool/mineshaft/rooms.json", {"fallback": "minecraft:empty", "elements":
        [elem(n, 1) for n in names] + [{"weight": 10, "element": {"element_type": "minecraft:empty_pool_element"}}]})
    loot()
    print(f"4-2b: {len(kit)} new room pieces, rooms pool = {len(names)} rooms + empty(10), 4 new loot tables")

if __name__ == "__main__":
    main()
