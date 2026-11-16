"""
buildkit.py - shared helpers for script-built replacement structures (pass 8-2 onward).
Wear rule (user): WORN, not ruined -> moss / mossy / cracked / lesser versions, never missing walls.
"""
import json, random, zlib
from gen_pass4_2a import M, R, w, item, OUT
from gen_pass4_2b import lbarrel

H4 = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
NOT_FULL = ("air", "stairs", "slab", "fence", "pane", "bars", "wall", "door", "trapdoor", "torch", "lantern", "chain", "carpet", "ladder",
            "vine", "flower", "pot", "bed", "button", "plate", "sign", "campfire", "cauldron", "anvil", "chest", "barrel_", "glass_pane", "leaves", "floodlight", "rail")

def rng(tag, seed=0): return random.Random(zlib.crc32(tag.encode()) + seed)

WEAR = {M("cobblestone"): [(M("mossy_cobblestone"), .3)],
        M("stone_bricks"): [(M("mossy_stone_bricks"), .18), (M("cracked_stone_bricks"), .15)],
        M("bricks"): [(M("mud_bricks"), .04)],
        M("polished_andesite"): [(M("andesite"), .2)],
        M("smooth_sandstone"): [(M("sandstone"), .25)], M("cut_sandstone"): [(M("sandstone"), .2)],
        M("stone"): [(M("cobblestone"), .15), (M("mossy_cobblestone"), .08)],
        M("deepslate_bricks"): [(M("cracked_deepslate_bricks"), .2)], M("deepslate_tiles"): [(M("cracked_deepslate_tiles"), .2)],
        M("white_terracotta"): [(M("light_gray_terracotta"), .12)], M("terracotta"): [(M("brown_terracotta"), .1)]}
def worn(r, name, k=1.0):
    """replace-only wear; k scales the chance (e.g. 1.6 near the ground, .5 up high = gradient)"""
    p = r.random(); acc = 0
    for alt, ch in WEAR.get(name, []):
        acc += ch * k
        if p < acc: return alt
    return name

def full(name): return bool(name) and not any(s in name.split(":")[1] for s in NOT_FULL)

def chest(t, x, y, z, facing, table):
    t.set(x, y, z, M("chest"), {"facing": facing, "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": f"dying_world:chests/{table}"})

def stairs(t, x, y, z, mat, facing, half="bottom"):
    t.set(x, y, z, M(f"{mat}_stairs"), {"facing": facing, "half": half, "shape": "straight", "waterlogged": "false"})

def slab(t, x, y, z, mat, typ="bottom"): t.set(x, y, z, M(f"{mat}_slab"), {"type": typ, "waterlogged": "false"})

def door(t, x, y, z, mat, facing, hinge="left", open_="false"):
    for half, dy in (("lower", 0), ("upper", 1)):
        t.set(x, y + dy, z, M(f"{mat}_door"), {"facing": facing, "half": half, "hinge": hinge, "open": open_, "powered": "false"})

def bed(t, x, y, z, color, facing):
    """head at (x,y,z); foot one block opposite the facing direction"""
    dx, dz = H4[facing]
    t.set(x, y, z, M(f"{color}_bed"), {"facing": facing, "part": "head", "occupied": "false"})
    t.set(x - dx, y, z - dz, M(f"{color}_bed"), {"facing": facing, "part": "foot", "occupied": "false"})

def table(t, x, y, z, wood="spruce"):
    t.set(x, y, z, M(f"{wood}_fence")); t.set(x, y + 1, z, M(f"{wood}_pressure_plate"), {"powered": "false"})

def chair(t, x, y, z, wood, facing):  # stair seat; facing = side of the BACK (point it away from the table)
    stairs(t, x, y, z, wood, facing)

def lantern(t, x, y, z, hanging=True): t.set(x, y, z, M("lantern"), {"hanging": "true" if hanging else "false", "waterlogged": "false"})
def hang_lantern(t, x, y, z):
    t.set(x, y, z, M("chain"), {"axis": "y", "waterlogged": "false"}); lantern(t, x, y - 1, z)
def pot(t, x, y, z, plant="dead_bush"): t.set(x, y, z, M(f"potted_{plant}"))

def gable(t, r, x0, x1, z0, z1, y, mat="dark_oak", fill="spruce_planks", moss=True):
    """roof over x0..x1 / z0..z1 with 1-block eaves, ridge along x; gable triangles filled. returns ridge y"""
    for x in range(x0, x1 + 1):                                   # top plate: closes the gap between wall top and the first roof row
        for zz in (z0, z1): t.set(x, y, zz, worn(r, M(fill)))
    k = 0
    while True:
        za, zb = z0 - 1 + k, z1 + 1 - k
        if za > zb: break
        for x in range(x0 - 1, x1 + 2):
            if za == zb: slab(t, x, y + k, za, mat)
            else: stairs(t, x, y + k, za, mat, "south"); stairs(t, x, y + k, zb, mat, "north")
        if k >= 1:
            for x in (x0, x1):
                for zz in range(za, zb + 1): t.set(x, y + k - 1, zz, worn(r, M(fill)))
        if zb - za <= 1: break
        k += 1
    if moss:
        for _ in range(3):
            if r.random() < .5: t.set(r.randint(x0, x1), y + 1, r.choice([z0 - 1, z1 + 1]), M("moss_carpet"))
    return y + k

def gable_z(t, r, x0, x1, z0, z1, y, mat="dark_oak", fill="spruce_planks", moss=True):
    """same as gable() but ridge along z (slopes face east/west)"""
    for z in range(z0, z1 + 1):
        for xx in (x0, x1): t.set(xx, y, z, worn(r, M(fill)))
    k = 0
    while True:
        xa, xb = x0 - 1 + k, x1 + 1 - k
        if xa > xb: break
        for z in range(z0 - 1, z1 + 2):
            if xa == xb: slab(t, xa, y + k, z, mat)
            else: stairs(t, xa, y + k, z, mat, "east"); stairs(t, xb, y + k, z, mat, "west")
        if k >= 1:
            for z in (z0, z1):
                for xx in range(xa, xb + 1): t.set(xx, y + k - 1, z, worn(r, M(fill)))
        if xb - xa <= 1: break
        k += 1
    if moss:
        for _ in range(3):
            if r.random() < .5: t.set(r.choice([x0 - 1, x1 + 1]), y + 1, r.randint(z0, z1), M("moss_carpet"))
    return y + k

CONNECT = ("_fence", "_pane", "iron_bars", "_wall")
def anchor_chains(t):
    """user feedback 8-7: hanging chains must reach the ceiling/roof - extend every vertical chain upward until it meets a block."""
    for (x, y, z), (name, props, nbt) in list(t.b.items()):
        if name != M("chain") or dict(props).get("axis", "y") != "y": continue
        if t.b.get((x, y + 1, z), ("",))[0] == M("chain"): continue                 # not the top of the column
        yy = y + 1; path = []
        while yy < t.sy and t.b.get((x, yy, z), (M("air"),))[0] in (M("air"), "", M("cobweb")):
            path.append(yy); yy += 1
        if yy < t.sy and path:                                    # found something to hang from
            for p in path: t.set(x, p, z, M("chain"), {"axis": "y", "waterlogged": "false"})
PASSABLE = (M("air"), "", M("cobweb"), M("chain"))
def lift_lanterns(t):
    """user rule (8-8): hanging lanterns must clear a 2-block-tall player: lantern y >= floor + 3 (floor = first block below).
    Too low -> moved up (the chain is rebuilt by anchor_chains); no room under the ceiling -> hang it from the ceiling block itself if that clears,
    otherwise the lantern is turned into a standing lantern on the floor against nothing is avoided: we drop it (rare)."""
    for (x, y, z), (name, props, nbt) in list(t.b.items()):
        if name != M("lantern") or dict(props).get("hanging") != "true": continue
        f = y - 1
        while f >= 0 and t.b.get((x, f, z), ("",))[0] in PASSABLE: f -= 1
        need = f + 3
        if y >= need: continue
        c = y + 1                                                  # first solid above (the ceiling / roof)
        while c < t.sy and t.b.get((x, c, z), ("",))[0] in PASSABLE: c += 1
        for yy in range(y, c): t.set(x, yy, z, M("air"))            # clear old lantern + chain
        if c < t.sy and c - 1 >= need:                            # lowest head-clear spot; anchor_chains then fills the chain up to the ceiling
            t.set(x, need, z, M("lantern"), {"hanging": "true", "waterlogged": "false"})
            if need + 1 < c: t.set(x, need + 1, z, M("chain"), {"axis": "y", "waterlogged": "false"})
def fix_connections(t):
    lift_lanterns(t)
    anchor_chains(t)
    """set north/south/east/west (+up for walls) on fences, panes, bars, walls from their neighbours (template-local)."""
    for (x, y, z), (name, props, nbt) in list(t.b.items()):
        if not any(name.endswith(c) or c == "iron_bars" and name.endswith(c) for c in CONNECT) or name.endswith("fence_gate"): continue
        is_wall = name.endswith("_wall")
        p = {}
        for d, (dx, dz) in H4.items():
            nb = t.b.get((x + dx, y, z + dz), ("",))[0]
            con = bool(nb) and (full(nb) or any(nb.endswith(c) for c in CONNECT) or (name.endswith("_fence") and nb.endswith("_fence_gate")))
            if name.endswith("_fence") and nb.endswith("_wall"): con = False
            p[d] = ("low" if con else "none") if is_wall else ("true" if con else "false")
        p["waterlogged"] = "false"
        if is_wall: p["up"] = "true" if sum(v != "none" for k, v in p.items() if k in H4) != 2 else "false"
        t.set(x, y, z, name, p, nbt)

def register(name, pool, elements, biomes, adaptation="beard_box", size=1, radius=40, heightmap="WORLD_SURFACE_WG"):
    """pool elements [(loc, weight)] -> template_pool + structure json (keeps existing structure_set)."""
    w(OUT / f"worldgen/template_pool/{pool}.json", {"fallback": "minecraft:empty", "elements": [
        {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}
        for loc, wt in elements]})
    if biomes is not None:
        w(OUT / f"tags/worldgen/biome/has_structure/{name}.json", {"replace": False, "values": biomes})
    w(OUT / f"worldgen/structure/{name}.json", {
        "type": "minecraft:jigsaw", "biomes": f"#dying_world:has_structure/{name}", "max_distance_from_center": radius, "size": size,
        "project_start_to_heightmap": heightmap, "spawn_overrides": {}, "start_height": {"absolute": 0}, "start_pool": f"dying_world:{pool}",
        "step": "surface_structures", "terrain_adaptation": adaptation, "use_expansion_hack": False})

def opt(tag): return {"id": tag, "required": False}

# 9-17: fluid pipe connection states (the props index lists only 'true' because R&R uses a multipart blockstate; real values are true/false per side).
PIPE_BLOCKS = ("rustandrebar:rusted_fluid_pipe",)
PIPE_DEVICES = ("rustandrebar:rusted_mechanical_pump", "rustandrebar:rusted_drum", "rustandrebar:rusted_tank", "rustandrebar:rusted_inline_pump")
D6 = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0)}
OPP6 = {"north": "south", "south": "north", "west": "east", "east": "west", "up": "down", "down": "up"}
def connect_pipes(t):
    """set each pipe's 6 sides from its neighbours: pipe/device -> true; a pipe with one link continues straight through; a lone pipe is vertical"""
    n_fixed = 0
    for (x, y, z), (name, props, nbt) in list(t.b.items()):
        if name not in PIPE_BLOCKS: continue
        con = {d: t.b.get((x + dx, y + dy, z + dz), ("",))[0] in PIPE_BLOCKS + PIPE_DEVICES for d, (dx, dy, dz) in D6.items()}
        k = sum(con.values())
        if k == 0: con["up"] = con["down"] = True
        elif k == 1: con[OPP6[next(d for d, v in con.items() if v)]] = True
        p = dict(props) if not isinstance(props, dict) else dict(props)
        p.update({d: "true" if v else "false" for d, v in con.items()})
        t.b[(x, y, z)] = (name, tuple(sorted(p.items())) if not isinstance(props, dict) else p, nbt); n_fixed += 1
    return n_fixed
