#!/usr/bin/env python3
"""
gen_pass4_3a.py - pass 4-3a: SCAVENGER OUTPOSTS (replace pillager outposts). Safe to re-run.

3 script-built camps (structure/scavenger_outpost/camp_<n>.nbt, 17x14x17, y0 = ground layer like the concrete pads):
  broken scrap perimeter (corrugated rusted metal / container wall / chain-link runs, barbed wire on top, gaps, south entrance),
  5x5 girder WATCHTOWER (rung ladder on a metal panel, grate platform at y9 with loot chest, parapet with gaps, sodium floodlight, patchy roof),
  2 corrugated lean-tos with loot barrels, lit burning barrel, scrap piles (drums, gas cylinders, rebar, crates, pallets), danger signs.
  Mostly Rust and Rebar (industrial site per user rule) so one camp pool fits every biome; y0 is a PARTIAL patch (rest = natural ground).

Structures (all share pool dying_world:scavenger_outpost/camps; set dying_world:scavenger_outposts 40/14, 6 chunks from survivor villages):
  guarded_<group> (temperate/cold/arid/wild = the concrete-pad biome groups) weight 4, monster spawn_overrides per group (undead; surface spawns only at night/dark),
  abandoned (any land biome, no overrides) weight 6, raiders (any land, PILLAGERS, rare) weight 1.  => per biome about 36% guarded / 55% abandoned / 9% raiders.
Loot: chests/scavenger_outpost (tower chest: gear + R&R mats), chests/scavenger_scraps (barrels).
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from gen_pass4_2a import M, R, w, item, OUT, CRATES
from gen_pass4_2b import lbarrel

S, HT, C = 17, 14, 8
COLORS = ["red", "blue", "green", "bare"]
GROUPS = ["temperate", "cold", "arid", "wild"]

def sp(t, wt, lo, hi): return {"type": "minecraft:" + t, "weight": wt, "minCount": lo, "maxCount": hi}
SPAWNS = {
    "temperate": [sp("zombie", 100, 1, 3), sp("skeleton", 80, 1, 2), sp("zombie_villager", 20, 1, 1)],
    "cold":      [sp("stray", 80, 1, 2), sp("zombie", 60, 1, 3), sp("skeleton", 40, 1, 2)],
    "arid":      [sp("husk", 100, 1, 3), sp("skeleton", 60, 1, 2)],
    "wild":      [sp("zombie", 80, 1, 3), sp("skeleton", 80, 1, 2), sp("zombie_villager", 20, 1, 1)],
    "raiders":   [sp("pillager", 1, 1, 1)],
}

def camp(seed):
    r = random.Random(zlib.crc32(b"scavenger_outpost") + seed); t = Tpl(S, HT, S)
    inside = lambda x, z: 1 <= x <= 15 and 1 <= z <= 15
    for x in range(S):                                         # partial ground patch + clear low clutter (grass/snow) inside the ring
        for z in range(S):
            if inside(x, z):
                if r.random() < .45: t.set(x, 0, z, r.choice([R("weathered_concrete"), M("gravel"), M("coarse_dirt"), R("tread_plate"), M("gravel")]))
                for y in range(1, 4): t.set(x, y, z, M("air"))
    # perimeter ring at 1 / 15, split in runs
    ring = [(x, 1) for x in range(1, 16)] + [(15, z) for z in range(2, 16)] + [(x, 15) for x in range(14, 0, -1)] + [(1, z) for z in range(14, 1, -1)]
    i = 0
    while i < len(ring):
        n = r.randint(2, 5); kind = r.choices(["corr", "cont", "chain", "gap"], [4, 2, 3, 2])[0]
        col = r.choice(COLORS)
        for x, z in ring[i:i + n]:
            if z == 15 and 6 <= x <= 10: continue                # entrance
            h = 3 if kind == "cont" else r.choice((2, 2, 3))
            if kind == "gap":
                if r.random() < .5: t.set(x, 1, z, R("corrugated_rusted_metal_slab"), {"type": "bottom"})
                continue
            for y in range(1, h + 1):
                if kind == "corr": t.set(x, y, z, R("corrugated_rusted_metal"))
                elif kind == "cont": t.set(x, y, z, R(f"{col}_container_wall"))
                else: t.set(x, y, z, R("chain_link_fence"))
            if kind != "chain" and r.random() < .35: t.set(x, h + 1, z, R("barbed_wire"))
        i += n
    # chain-link connections (states must be in the NBT)
    for (x, y, z), v in list(t.b.items()):
        if v[0] != R("chain_link_fence"): continue
        props = {}
        for d, (dx, dz) in {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}.items():
            nb = t.b.get((x + dx, y, z + dz), ("",))[0]
            props[d] = "true" if nb in (R("chain_link_fence"), R("corrugated_rusted_metal")) or nb.endswith("_container_wall") else "false"
        t.set(x, y, z, R("chain_link_fence"), props)
    # watchtower x9..13 z2..6
    tx0, tz0 = 9, 2
    for x in range(tx0, tx0 + 5):
        for z in range(tz0, tz0 + 5): t.set(x, 0, z, R("weathered_concrete"))
    for x, z in ((tx0, tz0), (tx0 + 4, tz0), (tx0, tz0 + 4), (tx0 + 4, tz0 + 4)):
        for y in range(1, 13): t.set(x, y, z, R("rusted_girder"), {"axis": "y"})
    for x in range(tx0 + 1, tx0 + 4):                          # north panel (ladder backing), y1..9
        for y in range(1, 10): t.set(x, y, tz0, R("corrugated_rusted_metal") if r.random() < .8 else R("riveted_rusted_plating"))
    lx, lz = tx0 + 2, tz0 + 1
    for x in range(tx0 + 1, tx0 + 4):                          # platform y9
        for z in range(tz0 + 1, tz0 + 4):
            if (x, z) != (lx, lz): t.set(x, 9, z, R("rusted_grate"))
    for x in (tx0, tx0 + 4):
        for z in range(tz0 + 1, tz0 + 4): t.set(x, 9, z, R("tread_plate"))
    for z in (tz0 + 4,):
        for x in range(tx0 + 1, tx0 + 4): t.set(x, 9, z, R("tread_plate"))
    for y in range(1, 10): t.set(lx, y, lz, R("rusted_rung_ladder"), {"facing": "south"})
    for x in range(tx0, tx0 + 5):                              # parapet y10 with gaps (none at the corners = girders)
        for z in range(tz0, tz0 + 5):
            edge = x in (tx0, tx0 + 4) or z in (tz0, tz0 + 4)
            corner = x in (tx0, tx0 + 4) and z in (tz0, tz0 + 4)
            if edge and not corner and r.random() < .6: t.set(x, 10, z, R("corrugated_rusted_metal"))
    for x in range(tx0, tx0 + 5):                              # patchy roof y13
        for z in range(tz0, tz0 + 5):
            if r.random() < .7: t.set(x, 13, z, R("corrugated_rusted_metal_slab"), {"type": "bottom"})
    t.set(tx0 + 3, 10, tz0 + 3, M("chest"), {"facing": "west", "type": "single", "waterlogged": "false"},
          {"id": M("chest"), "LootTable": "dying_world:chests/scavenger_outpost"})
    t.set(tx0 + 1, 10, tz0 + 3, r.choice(CRATES))
    # sodium floodlights (jar: facing = direction the lamp points, mount plate on the OPPOSITE side; up = floor mount, down = ceiling mount):
    # hung off the OUTSIDE of the platform edge (mounted on the y9 tread plate), aimed outward and tilted down over the yard/approach
    t.set(tx0 + 5, 9, tz0 + 2, R("sodium_floodlight"), {"facing": "east", "lit": "true"})
    t.set(tx0 + 2, 9, tz0 + 5, R("sodium_floodlight"), {"facing": "south", "lit": "true"})
    t.set(tx0 - 1, 9, tz0 + 2, R("sodium_floodlight"), {"facing": "west", "lit": "false"})
    # lean-tos on the west side: back wall x=2, roof y4 x2..4, posts at x=4
    for z0 in (3, 9) if seed != 2 else (4, 10):
        for z in range(z0, z0 + 4):
            for y in range(1, 4): t.set(2, y, z, R("corrugated_rusted_metal"))
            for x in (2, 3, 4):
                if r.random() < .8: t.set(x, 4, z, R("corrugated_rusted_metal_slab"), {"type": "bottom"})
        for z in (z0, z0 + 3):
            for y in range(1, 4): t.set(4, y, z, R("rusted_girder"), {"axis": "y"})
        lbarrel(t, 3, 1, z0 + 1, "scavenger_scraps")
        if r.random() < .6: lbarrel(t, 3, 1, z0 + 2, r.choice(["scavenger_scraps", "mineshaft_workshop", "mineshaft_fuel"]))
        else: t.set(3, 1, z0 + 2, r.choice(CRATES))
    t.set(C - 1, 1, 11, R("burning_barrel"), {"lit": "true"})
    t.set(C - 2, 1, 11, R("wooden_pallet")); t.set(C, 1, 12, R("wooden_pallet"))
    for _ in range(10):                                        # scrap piles in the yard
        x, z = r.randint(5, 14), r.randint(7, 14)
        if (x, 1, z) in t.b and t.b[(x, 1, z)][0] != M("air"): continue
        k = r.random()
        if k < .25: t.set(x, 1, z, R("rusted_drum"), {"axis": "y"})
        elif k < .4: t.set(x, 1, z, R("gas_cylinders"), {"count": str(r.randint(1, 5)), "facing": r.choice(["north", "south", "east", "west"])})
        elif k < .52: t.set(x, 1, z, R("tar_leaking_drum"), {"facing": r.choice(["north", "south", "east", "west"])})
        elif k < .65: t.set(x, 1, z, R("rebar_bundle"), {"axis": r.choice("xz")})
        else:
            t.set(x, 1, z, r.choice(CRATES))
            if r.random() < .35: t.set(x, 2, z, r.choice(CRATES))
    for x, z, f in ((5, 14, "north"), (11, 14, "north")):      # danger signs on the inside of the south wall (entrance flanks)
        if t.b.get((x, 2, z + 1), ("",))[0] not in ("", M("air")): t.set(x, 2, z, R(r.choice(["sign_danger", "sign_no_entry"])), {"facing": f})
    return t

def loot():
    rr = "rustandrebar"
    gear = [item("crossbow", 4, worn=True), item("bow", 3, worn=True), item("arrow", 8, 6, 18), item("iron_sword", 3, worn=True), item("iron_axe", 3, worn=True),
            item("chainmail_helmet", 2, worn=True), item("chainmail_chestplate", 2, worn=True), item("shield", 2, worn=True), item("spyglass", 1)]
    goods = [item("iron_ingot", 8, 2, 7), item("gold_ingot", 3, 1, 4), item("gunpowder", 5, 2, 6), item("tnt", 2, 1, 3), item("emerald", 3, 1, 4),
             item("ender_pearl", 1, 1, 2), item("golden_apple", 1), item("diamond", 1, 1, 2), item("map", 2), item("name_tag", 1), item("saddle", 1)]
    mats = [item("rebar_bundle", 5, 2, 8, ns=rr), item("rebar_concrete", 5, 8, 24, ns=rr), item("weathered_concrete", 4, 8, 24, ns=rr),
            item("corrugated_rusted_metal", 4, 6, 16, ns=rr), item("rusted_plating", 3, 6, 16, ns=rr), item("chain_link_fence", 3, 6, 16, ns=rr),
            item("barbed_wire", 3, 4, 12, ns=rr), item("salvaged_steel_block", 1, 2, 4, ns=rr)]
    food = [item("bread", 5, 2, 5), item("cooked_beef", 3, 1, 4), item("baked_potato", 4, 2, 6), item("dried_kelp", 3, 4, 10), item("torch", 4, 4, 12)]
    w(OUT / "loot_table/chests/scavenger_outpost.json", {"pools": [
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 3}, "entries": gear},
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": goods},
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": mats},
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": food}]})
    scraps = [item("iron_nugget", 8, 4, 14), item("copper_ingot", 6, 2, 6), item("coal", 7, 3, 10), item("string", 5, 2, 6), item("leather", 4, 1, 4),
              item("rotten_flesh", 5, 2, 6), item("bone", 5, 2, 6), item("arrow", 4, 3, 10), item("flint", 3, 2, 5), item("bucket", 1),
              item("iron_shovel", 2, worn=True), item("rebar_bundle", 4, 1, 4, ns=rr), item("bread", 3, 1, 3)]
    w(OUT / "loot_table/chests/scavenger_scraps.json", {"pools": [{"rolls": {"type": "minecraft:uniform", "min": 3, "max": 6}, "entries": scraps}]})

def structure(name, biomes, spawns):
    ov = {"monster": {"bounding_box": "full", "spawns": spawns}} if spawns else {}
    w(OUT / f"worldgen/structure/{name}.json", {
        "type": "minecraft:jigsaw", "biomes": biomes, "max_distance_from_center": 30, "project_start_to_heightmap": "WORLD_SURFACE_WG", "size": 1,
        "spawn_overrides": ov, "start_height": {"absolute": 0}, "start_pool": "dying_world:scavenger_outpost/camps",
        "step": "surface_structures", "terrain_adaptation": "beard_thin", "use_expansion_hack": False})

def main():
    N = OUT / "structure/scavenger_outpost"; N.mkdir(parents=True, exist_ok=True)
    for s in (1, 2, 3): (N / f"camp_{s}.nbt").write_bytes(camp(s).bytes())
    w(OUT / "worldgen/template_pool/scavenger_outpost/camps.json", {"fallback": "minecraft:empty", "elements": [
        {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:scavenger_outpost/camp_{s}",
                                  "processors": "minecraft:empty", "projection": "rigid"}} for s in (1, 2, 3)]})
    w(OUT / "tags/worldgen/biome/has_structure/scavenger_outpost_any.json",
      {"replace": False, "values": [{"id": f"#dying_world:has_structure/concrete_pad_{g}", "required": False} for g in GROUPS]})
    sets = []
    for g in GROUPS:
        structure(f"scavenger_outpost_{g}", f"#dying_world:has_structure/concrete_pad_{g}", SPAWNS[g]); sets.append((f"scavenger_outpost_{g}", 4))
    structure("scavenger_outpost_abandoned", "#dying_world:has_structure/scavenger_outpost_any", None); sets.append(("scavenger_outpost_abandoned", 6))
    structure("scavenger_outpost_raiders", "#dying_world:has_structure/scavenger_outpost_any", SPAWNS["raiders"]); sets.append(("scavenger_outpost_raiders", 1))
    w(OUT / "worldgen/structure_set/scavenger_outposts.json", {
        "structures": [{"structure": f"dying_world:{n}", "weight": wt} for n, wt in sets],
        "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 14,
                      "salt": zlib.crc32(b"dying_world:scavenger_outposts") % 2000000000,
                      "exclusion_zone": {"other_set": "dying_world:survivor_villages", "chunk_count": 6}}})
    loot()
    print(f"4-3a: 3 camps, {len(sets)} structures in set scavenger_outposts (40/14), 2 loot tables")

if __name__ == "__main__":
    main()
