#!/usr/bin/env python3
"""
gen_pass5_2.py - pass 5-2: FORTIFIED HOUSES for the scavenger stronghold (run AFTER gen_pass5_1.py; overwrites its houses pool). Safe to re-run.

For each of the 22 worn plains houses (our villager-free copies in structure/village/plains/houses_worn/) two stronghold copies are written
to structure/scavenger_stronghold/houses/<name>_{plain,fort}.nbt (edited with tools/nbtrw.py, tag types preserved):
- BOTH: FLOOR REPAIR (user: floors must never be completely gone): floor level = most common y of floor-type blocks with air above;
  every enclosed cell on that level that is air/missing gets the house's dominant floor block. Farm animals/fish removed (item frames,
  paintings, armour stands kept). Piglins placed on free interior floor cells (plain 1-2, fort 2-3; farms 1 in the field).
- FORT only (scavenger layer on top, village materials stay dominant): ~15% of roof-top blocks swapped for corrugated rusted metal
  (stairs -> corrugated stairs with the same facing/half/shape, slabs -> corrugated slab, full -> corrugated block); ~50% glass panes
  boarded with spruce planks; a LOOKOUT on the highest roof point (3x3 plank platform on fence posts, fence rail with gaps, barbed wire,
  sodium floodlight mounted on the platform edge pointing outward, crossbow piglin); scrap outside the walls (crates/drums + 1 loot barrel).
Pool: plain weight = 40% and fort = 60% of the house's original weight (processors kept from our village override).
"""
import json, random, sys, zlib
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from gen_pass4_2a import M, R, w, OUT, CRATES
from gen_pass5_1 import piglin, SH

SRC = OUT / "structure/village/plains/houses_worn"; DST = OUT / "structure/scavenger_stronghold/houses"
FLOORISH = ("planks", "cobblestone", "stone_bricks", "polished_andesite", "smooth_stone", "stone")
ANIMALS = {"minecraft:sheep", "minecraft:pig", "minecraft:cow", "minecraft:horse", "minecraft:cod", "minecraft:salmon", "minecraft:chicken"}
AIRS = (M("air"), M("cave_air"))

def air(s, p): return p not in s.b or s.b[p][0] in AIRS
def solid(s, p): return p in s.b and s.b[p][0] not in AIRS and "jigsaw" not in s.b[p][0] and "water" not in s.b[p][0]

def covered(s, x, y, z): return any(solid(s, (x, yy, z)) for yy in range(y + 2, s.size[1]))
def free(s, p): return air(s, p) or any(k in s.b[p][0] for k in ("carpet", "pressure_plate", "wheat", "carrots", "potatoes", "beetroots", "short_grass"))

def floor_level(s):
    """lowest y with a substantial number of floor-type blocks that have something solid ABOVE them (roof) => ground floor, not the roof"""
    c = Counter()
    for (x, y, z), (n, _, _) in s.b.items():
        if y >= 1 and any(k in n for k in FLOORISH) and covered(s, x, y, z): c[y] += 1
    if not c: return None
    best = max(c.values()); return min(y for y, v in c.items() if v >= .4 * best)

def enclosed(s, x, y, z):
    sx, _, sz = s.size
    def hit(dx, dz):
        X, Z = x + dx, z + dz
        while 0 <= X < sx and 0 <= Z < sz:
            if solid(s, (X, y, Z)) or solid(s, (X, y + 1, Z)): return True
            X += dx; Z += dz
        return False
    return all(hit(dx, dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))

def barrel(s, x, y, z, table):
    s.set(x, y, z, M("barrel"), {"facing": "up", "open": "false"}, (10, {"id": (8, M("barrel")), "LootTable": (8, f"dying_world:chests/{table}")}))

def build(name, fort, seed):
    r = random.Random(zlib.crc32(f"{name}{fort}".encode()) + seed)
    s = nbtrw.Struct((SRC / f"{name}.nbt").read_bytes()); sx, sy, sz = s.size
    s.ents = [e for e in s.ents if e["nbt"][1]["id"][1] not in ANIMALS]
    yf = floor_level(s); farm = "farm" in name; repaired = 0; spots = []
    if yf is not None and not farm:
        dom = Counter(n for (x, y, z), (n, _, _) in s.b.items() if y == yf and any(k in n for k in FLOORISH)).most_common(1)[0][0]
        for x in range(sx):
            for z in range(sz):
                if air(s, (x, yf, z)) and air(s, (x, yf + 1, z)) and covered(s, x, yf, z) and enclosed(s, x, yf + 1, z):
                    s.set(x, yf, z, dom); repaired += 1
        for x in range(sx):
            for z in range(sz):
                if solid(s, (x, yf, z)) and free(s, (x, yf + 1, z)) and air(s, (x, yf + 2, z)) and enclosed(s, x, yf + 1, z): spots.append((x, yf + 1, z))
    if not spots:                                     # farms / fisher: lowest standable cell anywhere (field, jetty)
        for y in range(0, 4):
            spots = [(x, y + 1, z) for x in range(1, sx - 1) for z in range(1, sz - 1)
                     if solid(s, (x, y, z)) and free(s, (x, y + 1, z)) and air(s, (x, y + 2, z))]
            if spots: break
    n_pig = (r.randint(2, 3) if fort else r.randint(1, 2)) if not farm else 1
    for (x, y, z) in r.sample(spots, min(n_pig, len(spots))): piglin(s, r, x, y, z)
    if fort and not farm and yf is not None:
        # roof patches + boarded windows
        tops = {}
        for (x, y, z), (n, _, _) in s.b.items():
            if n not in AIRS and y > yf + 2 and air(s, (x, y + 1, z)) and y >= tops.get((x, z), (-1,))[0]: tops[(x, z)] = (y, n)
        for (x, z), (y, n) in tops.items():
            if r.random() >= .15: continue
            props = s.b[(x, y, z)][1]
            if n.endswith("_stairs"): s.set(x, y, z, R("corrugated_rusted_metal_stairs"), {k: props[k] for k in ("facing", "half", "shape") if k in props})
            elif n.endswith("_slab"): s.set(x, y, z, R("corrugated_rusted_metal_slab"), {"type": props.get("type", "bottom")})
            elif any(k in n for k in ("planks", "log", "cobblestone", "bricks")): s.set(x, y, z, R("corrugated_rusted_metal"))
        for p, (n, _, _) in list(s.b.items()):
            if n == M("glass_pane") and r.random() < .5: s.set(*p, M("spruce_planks"))
        # lookout on the highest roof point (keep 1 block margin so the floodlight fits inside the template)
        cand = [(y, x, z) for (x, z), (y, n) in tops.items() if 2 <= x <= sx - 3 and 2 <= z <= sz - 3]
        if cand:
            ty, cx, cz = max(cand); yp = ty + 1
            need = yp + 3
            if need >= sy: s.size[1] = sy = need + 1
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    X, Z = cx + dx, cz + dz
                    if air(s, (X, yp, Z)): s.set(X, yp, Z, M("spruce_planks") if r.random() < .8 else R("corrugated_rusted_metal"))
                    y = yp - 1
                    while y > yf and air(s, (X, y, Z)) and (dx, dz) != (0, 0) and abs(dx) == abs(dz): s.set(X, y, Z, M("spruce_fence")); y -= 1
                    edge = (dx, dz) != (0, 0)
                    if edge and r.random() < .6: s.set(X, yp + 1, Z, M("spruce_fence") if r.random() < .75 else R("barbed_wire"))
            f, (lx, lz) = r.choice([("east", (cx + 2, cz)), ("west", (cx - 2, cz)), ("north", (cx, cz - 2)), ("south", (cx, cz + 2))])
            if air(s, (lx, yp, lz)): s.set(lx, yp, lz, R("sodium_floodlight"), {"facing": f, "lit": "true" if r.random() < .6 else "false"})
            s.entity(cx + .5, yp + 1, cz + .5, {"id": (8, "minecraft:piglin"), "IsImmuneToZombification": (1, 1), "PersistenceRequired": (1, 1),
                     "HandItems": (9, (10, [{"id": (8, "minecraft:crossbow"), "count": (3, 1)}, {}])), "HandDropChances": (9, (5, [.085, .085]))})
            # fence connections are neighbour-dependent: a lone post is fine; rails left unconnected (posts look like a broken rail)
        # scrap outside the walls
        out = [(x, z) for x in range(sx) for z in range(sz) if solid(s, (x, 0, z)) and air(s, (x, 1, z)) and not enclosed(s, x, 1, z)
               and not any(solid(s, (x + dx, 1, z + dz)) and "door" in s.b[(x + dx, 1, z + dz)][0] for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        r.shuffle(out)
        for i, (x, z) in enumerate(out[:r.randint(3, 5)]):
            if i == 0: barrel(s, x, 1, z, r.choice(["scavenger_stronghold_bridge", "scavenger_stronghold_other", "scavenger_scraps"]))
            else: s.set(x, 1, z, r.choice(CRATES + [R("rusted_drum")]), {"axis": "y"} if False else None)
    return s, repaired

def main():
    DST.mkdir(parents=True, exist_ok=True)
    hj = json.loads((Path(__file__).resolve().parent.parent / "datapack/data/minecraft/worldgen/template_pool/village/plains/houses.json").read_text())
    src = [e for e in hj["elements"] if "houses_worn" in json.dumps(e)]
    els, rep = [], {}
    for e in src:
        name = e["element"]["location"].rsplit("/", 1)[1]
        for fort, share in ((False, .4), (True, .6)):
            s, n = build(name, fort, 1); tag = "fort" if fort else "plain"
            (DST / f"{name}_{tag}.nbt").write_bytes(s.bytes()); rep[name] = n
            el = json.loads(json.dumps(e)); el["element"]["location"] = f"{SH}/houses/{name}_{tag}"; el["weight"] = max(1, round(e["weight"] * share))
            els.append(el)
    w(OUT / "worldgen/template_pool/scavenger_stronghold/houses.json", {"fallback": "minecraft:village/plains/terminators", "elements": els})
    print(f"5-2: {len(els)} stronghold house copies ({len(src)} houses x plain/fort); floor cells repaired: {sum(rep.values())} ({ {k: v for k, v in rep.items() if v} })")

if __name__ == "__main__":
    main()
