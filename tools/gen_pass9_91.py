#!/usr/bin/env python3
"""gen_pass9_91.py - pass 9-91: building templates hold their own air, and village houses get a foundation plinth.

Run after gen_pass9_83.py, before 8_9 / build. Safe to re-run.

1. Interior air. Building templates left their rooms and attics as structure void, so when a house is set into a slope
   (or the beardifier's thin carve doesn't reach the attic) the hillside stays inside it. Every void cell at y >= 1 with
   a block below AND above it in its column (rooms, attics, under eaves) becomes explicit air.
2. No holes in the ground. Explicit air at y = 0 (the ground layer) digs into the ground under/next to the building
   (the snowy burnt windmill, the village decor pieces): dropped back to void.
3. Plinth. Houses placed as children of village / stronghold streets get PLINTH layers of foundation under their y = 0
   footprint (stone on the outside ring, soil inside), so on slopes and over cave openings they stand on masonry instead
   of floating over gaps. The template shifts up with its jigsaws, so a house attaches exactly where it did and the
   beardifier's ground reference (street surface) doesn't move. Templates that are also a structure's start piece (the
   *_ruined houses double as abandoned_ruin starts) get no plinth: a start would be lifted by it.
"""
import glob, json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from nbtrw import Struct

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "datapack/data"
AIR = {"minecraft:air", "minecraft:cave_air"}
VOID = "minecraft:structure_void"
PLINTH = 4
MARK = "DwPlinth"

# building templates (rooms/roofs); streets, mines, wells, pits, stations and other designed-underground pieces are left alone
SKIP_DIRS = ("mineshaft/", "wells/", "sculk_camp/", "station/", "foundry", "digsite/", "concrete_pad/", "/streets/",
             "/village/", "scavenger_stronghold/decor/")
STONE = {"desert": [("minecraft:sandstone", 6), ("minecraft:smooth_sandstone", 2), ("minecraft:cut_sandstone", 2)],
         "snowy": [("minecraft:cobblestone", 6), ("minecraft:stone", 3), ("minecraft:mossy_cobblestone", 1)],
         None: [("minecraft:cobblestone", 7), ("minecraft:mossy_cobblestone", 3)]}
SOIL = {"desert": [("minecraft:sandstone", 1)], None: [("minecraft:dirt", 8), ("minecraft:coarse_dirt", 2)]}


def tid(path):
    rel = Path(path).relative_to(DATA).as_posix()            # ns/structure/a/b.nbt
    ns, _, rest = rel.partition("/structure/")
    return f"{ns}:{rest[:-4]}"


def pool_locations(pool_files):
    out = set()
    for f in pool_files:
        for e in json.loads(Path(f).read_text()).get("elements", []):
            loc = e["element"].get("location")
            if loc: out.add(loc)
    return out


def pool_files_for(pool_id):
    ns, _, p = pool_id.partition(":")
    return [f for base in (DATA, ROOT / "kubejs_base/data") for f in glob.glob(f"{base}/{ns}/worldgen/template_pool/{p}.json")]


def plinth_targets():
    house_pools = [f for f in glob.glob(f"{DATA}/minecraft/worldgen/template_pool/village/*/houses.json")]
    house_pools += glob.glob(f"{DATA}/dying_world/worldgen/template_pool/scavenger_stronghold/**/houses.json", recursive=True)
    locs = pool_locations(house_pools)
    # Lithostitched additions to the vanilla house pools (gearwrights windmills / watermill)
    for f in glob.glob(f"{ROOT}/kubejs_base/data/*/lithostitched/worldgen_modifier/*.json"):
        j = json.loads(Path(f).read_text())
        if "village/" in str(j.get("template_pools", "")) and "houses" in str(j.get("template_pools", "")):
            locs |= {e["element"].get("location") for e in j.get("elements", []) if e["element"].get("location")}
    starts = set()
    for f in glob.glob(f"{DATA}/*/worldgen/structure/**/*.json", recursive=True):
        sp = json.loads(Path(f).read_text()).get("start_pool")
        if sp: starts |= {l for pf in pool_files_for(sp) for l in pool_locations([pf])}
    return locs - starts, locs & starts


def biome_of(t):
    for b in ("desert", "snowy", "savanna", "taiga", "plains", "swamp"):
        if f"/{b}/" in "/" + t.split(":", 1)[1] + "/" or t.split(":", 1)[1].startswith(b + "/"):
            return b
    return None


def pick(r, opts):
    x = r.random() * sum(w for _, w in opts)
    for n, w in opts:
        x -= w
        if x < 0: return n
    return opts[-1][0]


def strip_plinth(s):
    root = s.tree[1]
    if MARK in root:
        d = root.pop(MARK)[1]
        s.b = {(x, y - d, z): v for (x, y, z), v in s.b.items() if y >= d}
        for e in s.ents:
            e["pos"][1][1][1] -= d; e["blockPos"][1][1][1] -= d
        s.size[1] -= d


def fix_air(s):
    solid = lambda v: v is not None and v[0] not in AIR and v[0] != VOID
    cols = {}
    for (x, y, z), v in s.b.items():
        if solid(v): cols.setdefault((x, z), []).append(y)
    added = removed = 0
    for (x, z), ys in cols.items():
        lo, hi = min(ys), max(ys)
        for y in range(max(lo + 1, 1), hi):
            if (x, y, z) not in s.b:
                s.b[(x, y, z)] = ("minecraft:air", {}, None); added += 1
    for (x, y, z) in [p for p, v in s.b.items() if p[1] == 0 and v[0] in AIR]:
        del s.b[(x, y, z)]; removed += 1
    return added, removed


def add_plinth(s, t, seed):
    foot = {(x, z) for (x, y, z), v in s.b.items() if y == 0 and v[0] not in AIR and v[0] != VOID}
    if not foot: return 0
    s.b = {(x, y + PLINTH, z): v for (x, y, z), v in s.b.items()}
    for e in s.ents:
        e["pos"][1][1][1] += PLINTH; e["blockPos"][1][1][1] += PLINTH
    s.size[1] += PLINTH
    b = biome_of(t); r = random.Random(f"{t}:{seed}")
    stone, soil = STONE.get(b, STONE[None]), SOIL.get(b, SOIL[None])
    for x, z in foot:
        edge = any(n not in foot for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)))
        for y in range(PLINTH):
            s.set(x, y, z, pick(r, stone if edge else soil))
    s.tree[1][MARK] = (3, PLINTH)
    return len(foot) * PLINTH


def main():
    plinth, skipped = plinth_targets()
    files = sorted(glob.glob(f"{DATA}/*/structure/**/*.nbt", recursive=True))
    tot_a = tot_r = tot_p = n = 0
    for f in files:
        t = tid(f); rel = t.split(":", 1)[1] + "/"
        if any(d in "/" + rel for d in SKIP_DIRS) and t not in plinth and "/village/decor_" not in "/" + rel:
            continue
        s = Struct(Path(f).read_bytes())
        strip_plinth(s)
        a, r = fix_air(s)
        p = add_plinth(s, t, 0) if t in plinth else 0
        if a or r or p or MARK in s.tree[1]:
            Path(f).write_bytes(s.bytes()); n += 1
        tot_a += a; tot_r += r; tot_p += p
    print(f"9-91: {n} templates written; +{tot_a} interior air, -{tot_r} ground-level air, {tot_p} plinth blocks "
          f"({len(plinth)} houses with plinth, {len(skipped)} start-pool houses without)")


if __name__ == "__main__":
    main()
