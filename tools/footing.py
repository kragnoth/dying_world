"""footing.py - give a jigsaw piece built-in stilts / a footing so it can't hang in the air (pass 9-76).

add_footing(path, depth, post, fill=None, seed=0, every=3): shifts every block and entity of the NBT up by `depth` and
puts log posts under the footprint's corners and every `every` cells along its edges (mineshaft-style stilts). The rest
of the space under the piece is left out of the template, so whatever the world has there stays: rock stays rock, a drop
stays open under the stilts. `fill` (weighted list) fills those cells instead, for a solid plinth. Jigsaw blocks move
with the rest, so connections stay aligned.

Why it's needed: for rigid jigsaw children the beardifier's ground reference is the START piece's bottom + 1 (child
groundLevelDelta = parent delta - child y offset), not the child's own bottom. beard_box carves everything above that
reference, so pieces whose floor sits higher than it (the dig camp: floors 3 above the pit's bottom) get carved air
under them, and the fill below only reaches ~12 blocks and never undoes carver caves. Making the box deeper doesn't move
the reference, so the footing doesn't deepen the carving.

The NBT root gets "DwFooting" = depth (ignored by Minecraft). A file that already has one is first stripped back to the
piece itself, so re-running with other settings replaces the old footing instead of stacking a second one.
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

def _shift(s, dy):
    s.b = {(x, y + dy, z): v for (x, y, z), v in s.b.items()}
    for e in s.ents:
        p = e["pos"][1][1]; p[1] = p[1] + dy
        bp = e["blockPos"][1][1]; bp[1] = bp[1] + dy
    s.size[1] += dy

def add_footing(path, depth, post, fill=None, seed=0, every=3):
    path = Path(path); s = Struct(path.read_bytes()); root = s.tree[1]
    if "DwFooting" in root:                                   # strip the old footing first
        old = root.pop("DwFooting")[1]
        s.b = {k: v for k, v in s.b.items() if k[1] >= old}
        _shift(s, -old)
    foot = {(x, z) for (x, y, z), (n, _, _) in s.b.items() if y == 0 and n not in AIRS}
    if not foot: return False
    _shift(s, depth)
    xs = [x for x, _ in foot]; zs = [z for _, z in foot]; x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    r = random.Random(f"{path.name}:{seed}")
    for x, z in foot:
        ex, ez = x in (x0, x1), z in (z0, z1)
        is_post = (ex and ez) or (ex and (z - z0) % every == 0) or (ez and (x - x0) % every == 0)
        for y in range(depth):
            if is_post: s.set(x, y, z, post, {"axis": "y"})
            elif fill: s.set(x, y, z, _pick(r, fill))
    root["DwFooting"] = (3, depth)
    path.write_bytes(s.bytes())
    return True
