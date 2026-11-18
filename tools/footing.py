"""footing.py - give a jigsaw piece a built-in footing so it can't hang in the air (pass 9-76).

add_footing(path, depth, post, fill, seed): shifts every block and entity of the NBT up by `depth` and fills the space
under the piece's footprint (cells of its bottom layer that aren't air): log posts at the footprint's corners and every
4 cells along its edges, rubble (`fill`, weighted list) everywhere else. Jigsaw blocks move with the rest, so connections
stay aligned. Inside solid ground the footing just replaces rock; over a drop it reads as shoring.

Why it's needed: for rigid jigsaw children the beardifier's ground reference is the START piece's bottom + 1 (child
groundLevelDelta = parent delta - child y offset), not the child's own bottom. beard_box carves everything above that
reference, so pieces whose floor sits higher than it (the dig camp: floors 3 above the pit's bottom) get carved air
under them, and the fill below only reaches ~12 blocks and never undoes carver caves. Making the box deeper doesn't move
the reference, so the footing doesn't deepen the carving.

Idempotent: the NBT root gets "DwFooting" (ignored by Minecraft); a file that has it is skipped.
"""
import random
from pathlib import Path
from nbtrw import Struct

AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:structure_void"}

def _pick(r, opts):
    tot = sum(w for _, w in opts); x = r.random() * tot
    for n, w in opts:
        x -= w
        if x < 0: return n
    return opts[-1][0]

def add_footing(path, depth, post, fill, seed=0):
    path = Path(path); s = Struct(path.read_bytes()); root = s.tree[1]
    if "DwFooting" in root: return False
    foot = {(x, z) for (x, y, z), (n, _, _) in s.b.items() if y == 0 and n not in AIRS}
    if not foot: return False
    s.b = {(x, y + depth, z): v for (x, y, z), v in s.b.items()}
    for e in s.ents:
        p = e["pos"][1][1]; p[1] = p[1] + depth
        bp = e["blockPos"][1][1]; bp[1] = bp[1] + depth
    xs = [x for x, _ in foot]; zs = [z for _, z in foot]; x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    r = random.Random(f"{path.name}:{seed}")
    for x, z in foot:
        ex, ez = x in (x0, x1), z in (z0, z1)
        is_post = (ex and ez) or (ex and (z - z0) % 4 == 0) or (ez and (x - x0) % 4 == 0)
        for y in range(depth):
            if is_post: s.set(x, y, z, post, {"axis": "y"})
            else: s.set(x, y, z, _pick(r, fill))
    s.size[1] += depth
    root["DwFooting"] = (3, depth)
    path.write_bytes(s.bytes())
    return True
