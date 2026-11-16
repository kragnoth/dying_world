#!/usr/bin/env python3
"""
gen_pass4_1.py - pass 4-1: CONCRETE PADS with broken-down LEAN-TOS (replaces ruined portals). Safe to re-run.

Builds (script-written .nbt, no outside assets):
  structure/concrete_pad/<wood>_<n>.nbt   9x5x9: RUST AND REBAR concrete pad (rustandrebar:rebar_concrete = visible rebar, weathered_concrete,
                                           tread_plate, hazard_plating; y0 = flush with ground) + broken lean-to (corrugated rusted metal roof/back wall,
                                           biome-wood posts + plank patches) + chest + barrel + burning barrel + salvage (crates, pallets, drums, rebar bundles).
  worldgen/template_pool/concrete_pad/<group>.json, worldgen/structure/concrete_pad_<group>.json (minecraft:jigsaw, 1 piece)
  worldgen/structure_set/concrete_pads.json   44/16, 3 chunks away from survivor villages
  tags/.../has_structure/concrete_pad_<group>.json  (explicit optional biome lists, disjoint groups)
  loot_table/chests/concrete_pad.json (obsidian/bricks/building mats + mid loot) and concrete_pad_scraps.json (barrel)
Wood palettes by biome group (user: no oak in a spruce biome):
  temperate (village 'plains' family)   oak + birch      cold (taiga + snowy)  spruce
  arid (desert + savanna)               acacia           wild (all other land: swamp, jungle, mountains, dark forest...) dark_oak
Block states for rustandrebar blocks are left at defaults (only slab 'type' is set); orientation-dependent blocks are avoided.
"""
import gzip, json, random, struct, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import biome_tags as bt
import village_biomes as vb

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "datapack/data/dying_world"
DATA_VERSION = 3955  # 1.21.1
SX, SY, SZ = 9, 5, 9

# ---------------------------------------------------------------- tiny NBT writer
def _s(s): b = s.encode("utf8"); return struct.pack(">H", len(b)) + b
def _pay(t, v):
    if t == 1: return struct.pack(">b", v)
    if t == 3: return struct.pack(">i", v)
    if t == 8: return _s(v)
    if t == 9:
        it, items = v; return struct.pack(">bi", it, len(items)) + b"".join(_pay(it, x) for x in items)
    if t == 10:
        return b"".join(struct.pack(">b", tt) + _s(k) + _pay(tt, vv) for k, (tt, vv) in v.items()) + b"\x00"
    raise ValueError(t)
def nbt_bytes(root): return gzip.compress(struct.pack(">b", 10) + _s("") + _pay(10, root), mtime=0)
S = lambda v: (8, v); I = lambda v: (3, v); C = lambda d: (10, d)
def L(t, items): return (9, (t, items))

# ---------------------------------------------------------------- structure builder
class Tpl:
    def __init__(self): self.b = {}
    def set(self, x, y, z, name, props=None, nbt=None):
        assert 0 <= x < SX and 0 <= y < SY and 0 <= z < SZ, (x, y, z)
        self.b[(x, y, z)] = (name, tuple(sorted((props or {}).items())), nbt)
    def drop(self, x, y, z): self.b.pop((x, y, z), None)
    def bytes(self):
        pal, idx, blocks = [], {}, []
        for pos in sorted(self.b, key=lambda p: (p[1], p[2], p[0])):
            name, props, nbt = self.b[pos]
            k = (name, props)
            if k not in idx:
                idx[k] = len(pal)
                e = {"Name": S(name)}
                if props: e["Properties"] = C({a: S(str(c)) for a, c in props})
                pal.append(e)
            e = {"pos": L(3, list(pos)), "state": I(idx[k])}
            if nbt: e["nbt"] = C({a: S(c) for a, c in nbt.items()})
            blocks.append(e)
        return nbt_bytes({"DataVersion": I(DATA_VERSION), "size": L(3, [SX, SY, SZ]),
                          "palette": L(10, pal), "blocks": L(10, blocks), "entities": L(10, [])})

def build(wood, seed):
    r = random.Random(seed * 7919 + zlib.crc32(wood.encode()))
    t = Tpl(); M = lambda n: "minecraft:" + n; R = lambda n: "rustandrebar:" + n
    planks, log = M(wood + "_planks"), M(wood + "_log")
    corr, corr_slab = R("corrugated_rusted_metal"), R("corrugated_rusted_metal_slab")
    # y0: Rust and Rebar concrete pad (visible rebar), ragged edges
    for x in range(SX):
        for z in range(SZ):
            edge = x in (0, SX - 1) or z in (0, SZ - 1)
            p = r.random()
            if edge:
                n = (R("weathered_concrete") if p < .40 else R("rebar_concrete") if p < .60 else M("coarse_dirt") if p < .78
                     else M("mossy_cobblestone") if p < .90 else M("andesite"))
            else:
                n = (R("rebar_concrete") if p < .42 else R("weathered_concrete") if p < .88 else R("tread_plate") if p < .93
                     else R("hazard_plating") if p < .96 else R("rebar_concrete"))
            t.set(x, 0, z, n)
    # lean-to along the north side: rusted corrugated back wall (with biome planks patched in), posts, sloping roof z1..z4
    for x in range(1, 8):
        for y in (1, 2, 3):
            p = r.random()
            if p < .22: continue                       # broken gap
            if p < .27: t.set(x, y, 1, M("cobweb")); continue
            q = r.random()
            t.set(x, y, 1, corr if q < .55 else planks if q < .85 else R("riveted_rusted_plating"))
    for x in (1, 7):                                   # back corner posts: biome wood or rusted beam
        for y in (1, 2, 3):
            if r.random() < .85: t.set(x, y, 1, log, {"axis": "y"})
    for x in (1, 4, 7):                                # front posts, sometimes snapped
        for y in range(1, 1 + r.choice((2, 2, 2, 1))):
            t.set(x, y, 4, log, {"axis": "y"})
    for x in range(1, 8):                              # roof: corrugated sheets, high at back, low at front
        for z, y, kind in ((1, 4, "full"), (2, 4, "bot"), (3, 3, "top"), (4, 3, "bot")):
            if r.random() < .27: continue
            if kind == "full": t.set(x, y, z, corr)
            else: t.set(x, y, z, corr_slab, {"type": "bottom" if kind == "bot" else "top"})
    for x in (1, 7):                                   # side rail left over from the roof edge
        if r.random() < .5: t.set(x, 4, 2, log, {"axis": "z"})
    # contents
    cx = r.choice((3, 4, 5))
    t.set(cx, 1, 2, M("chest"), {"facing": "south", "type": "single", "waterlogged": "false"},
          {"id": M("chest"), "LootTable": "dying_world:chests/concrete_pad"})
    if r.random() < .8:
        bx = r.choice([x for x in (2, 3, 4, 5, 6) if abs(x - cx) > 1])
        t.set(bx, 1, 2, M("barrel"), {"facing": "up", "open": "false"},
              {"id": M("barrel"), "LootTable": "dying_world:chests/concrete_pad_scraps"})
    t.set(r.choice((3, 4, 5)), 1, 6, R("burning_barrel"))
    # fallen post + salvage + rebar sticking out of the broken edge
    fz = r.choice((5, 6, 7)); fx = r.choice((1, 2, 5))
    for dx in range(3): t.set(fx + dx, 1, fz, log, {"axis": "x"})
    junk = [R("weathered_concrete_slab"), R("rebar_bundle"), R("weathered_wooden_crate"), R("wooden_pallet"), R("rusted_drum"),
            R("tar_leaking_drum"), R("gas_cylinders"), R("rotting_wooden_crate"), M("cobweb")]
    for _ in range(r.randint(4, 7)):
        x, z = r.randrange(SX), r.randrange(SZ)
        if (x, 1, z) not in t.b and not (1 <= x <= 7 and 1 <= z <= 4):
            t.set(x, 1, z, r.choice(junk))
    for _ in range(3):
        x, z = r.choice(((0, r.randrange(SZ)), (SX - 1, r.randrange(SZ)), (r.randrange(SX), SZ - 1)))
        if (x, 1, z) not in t.b: t.set(x, 1, z, R("rebar_bundle"))
    return t

GROUPS = {  # group -> [(wood, seeds)]
    "temperate": [("oak", (1, 2, 3)), ("birch", (1, 2))],
    "cold": [("spruce", (1, 2, 3))],
    "arid": [("acacia", (1, 2, 3))],
    "wild": [("dark_oak", (1, 2, 3))],
}

def w(p, o): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o, indent=2) + "\n")

def item(name, weight, lo=None, hi=None, worn=False, ns="minecraft"):
    e = {"type": "minecraft:item", "name": ns + ":" + name, "weight": weight, "functions": []}
    if lo is not None:
        e["functions"].append({"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}})
    if worn:
        e["functions"].append({"function": "minecraft:set_damage", "damage": {"type": "minecraft:uniform", "min": 0.25, "max": 0.8}})
    if not e["functions"]: del e["functions"]
    return e

def loot():
    building = [item("obsidian", 4, 3, 8), item("bricks", 8, 10, 28), item("stone_bricks", 6, 10, 24), item("deepslate_bricks", 3, 8, 16),
                item("glass", 4, 6, 14), item("iron_bars", 4, 6, 14), item("terracotta", 3, 8, 16), item("smooth_stone", 3, 8, 16),
                item("crying_obsidian", 1, 1, 3), item("iron_block", 1, 1, 1),
                item("rebar_concrete", 7, 8, 20, ns="rustandrebar"), item("weathered_concrete", 5, 8, 20, ns="rustandrebar"),
                item("firebrick", 4, 8, 16, ns="rustandrebar"), item("sooty_brick", 3, 8, 16, ns="rustandrebar"),
                item("rusted_plating", 3, 6, 14, ns="rustandrebar"), item("rebar_bundle", 3, 2, 6, ns="rustandrebar"),
                item("hazard_plating", 2, 4, 10, ns="rustandrebar"), item("salvaged_steel_block", 2, 2, 5, ns="rustandrebar")]
    mid = [item("iron_ingot", 8, 2, 6), item("gold_ingot", 4, 1, 4), item("copper_ingot", 6, 3, 8), item("coal", 6, 4, 10), item("redstone", 5, 4, 10),
           item("lapis_lazuli", 3, 3, 8), item("gunpowder", 4, 2, 5), item("string", 4, 2, 6), item("flint", 3, 2, 6),
           item("iron_pickaxe", 2, worn=True), item("iron_axe", 2, worn=True), item("iron_shovel", 2, worn=True), item("iron_sword", 2, worn=True),
           item("iron_chestplate", 1, worn=True), item("golden_apple", 1, 1, 1), item("diamond", 1, 1, 1), item("bucket", 2), item("compass", 1), item("clock", 1)]
    food = [item("bread", 6, 1, 4), item("apple", 4, 1, 3), item("baked_potato", 4, 1, 4), item("cooked_chicken", 2, 1, 2), item("carrot", 3, 1, 4), item("torch", 6, 4, 12)]
    # ruined-portal replacement: vanilla ruined_portal entries copied verbatim from reference/ (same weights/functions) + netherrack/magma remnants
    import zipfile
    vz = zipfile.ZipFile(ROOT / "reference/loot_and_recipes.zip")
    portal = json.loads(vz.read("data/minecraft/loot_table/chests/ruined_portal.json"))["pools"][0]["entries"]
    portal += [item("netherrack", 30, 6, 16), item("magma_block", 18, 2, 6)]
    big = {"pools": [{"rolls": {"type": "minecraft:uniform", "min": 2, "max": 3}, "entries": building},
                     {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 5}, "entries": portal},
                     {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 3}, "entries": mid},
                     {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": food}]}
    small = {"pools": [{"rolls": {"type": "minecraft:uniform", "min": 1, "max": 3}, "entries": food + [item("coal", 4, 2, 6), item("string", 3, 1, 4), item("iron_nugget", 4, 2, 8)]},
                       {"rolls": {"type": "minecraft:uniform", "min": 0, "max": 1},   # scraps of the lost gateway
                        "entries": [item("flint", 6, 1, 3), item("fire_charge", 4, 1, 2), item("netherrack", 6, 2, 8), item("magma_block", 3, 1, 3), item("gold_nugget", 5, 2, 8)]}]}
    w(OUT / "loot_table/chests/concrete_pad.json", big)
    w(OUT / "loot_table/chests/concrete_pad_scraps.json", small)

def main():
    # nbt + pools
    for g, woods in GROUPS.items():
        els = []
        for wood, seeds in woods:
            for s in seeds:
                name = f"{wood}_{s}"
                p = OUT / "structure/concrete_pad" / f"{name}.nbt"; p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(build(wood, s).bytes())
                els.append({"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:concrete_pad/{name}",
                                                       "processors": "minecraft:empty", "projection": "rigid"}})
        w(OUT / f"worldgen/template_pool/concrete_pad/{g}.json", {"fallback": "minecraft:empty", "elements": els})
        w(OUT / f"worldgen/structure/concrete_pad_{g}.json", {
            "type": "minecraft:jigsaw", "biomes": f"#dying_world:has_structure/concrete_pad_{g}", "max_distance_from_center": 30,
            "project_start_to_heightmap": "WORLD_SURFACE_WG", "size": 1, "spawn_overrides": {}, "start_height": {"absolute": 0},
            "start_pool": f"dying_world:concrete_pad/{g}", "step": "surface_structures", "terrain_adaptation": "beard_thin", "use_expansion_hack": False})
    # biome groups (disjoint): reuse village families; everything else on land = wild
    fam, _ = vb.families()
    R = bt.resolve
    skip = R("minecraft:is_ocean") | R("minecraft:is_deep_ocean") | R("c:is_shallow_ocean") | R("minecraft:is_river") | R("minecraft:is_nether") | R("minecraft:is_end") | \
           R("c:is_cave") | R("c:caves") | R("c:is_mushroom") | {b for b in bt.ALL_BIOMES if any(k in b for k in ("cave", "deeps", "dripstone", "deep_dark", "void", "marker"))}
    land = [b for b in bt.ALL_BIOMES if b not in skip]
    grp = {"temperate": set(fam["plains"]), "cold": set(fam["taiga"]) | set(fam["snowy"]), "arid": set(fam["desert"]) | set(fam["savanna"])}
    grp = {k: sorted(v & set(land)) for k, v in grp.items()}
    used = set().union(*grp.values())
    grp["wild"] = [b for b in land if b not in used]
    for g, bs in grp.items():
        w(OUT / f"tags/worldgen/biome/has_structure/concrete_pad_{g}.json", {"replace": False, "values": [{"id": b, "required": False} for b in bs]})
    # set
    w(OUT / "worldgen/structure_set/concrete_pads.json", {
        "structures": [{"structure": f"dying_world:concrete_pad_{g}", "weight": 1} for g in GROUPS],
        "placement": {"type": "minecraft:random_spread", "spacing": 44, "separation": 16, "salt": zlib.crc32(b"dying_world:concrete_pads") % 2000000000,
                      "exclusion_zone": {"other_set": "dying_world:survivor_villages", "chunk_count": 3}}})
    loot()
    print("pads:", {g: len(v) for g, v in grp.items()}, "biomes;", sum(len(v) for v in GROUPS.values()), "wood groups;",
          sum(len(s) for v in GROUPS.values() for _, s in v), "nbt variants")

if __name__ == "__main__":
    main()
