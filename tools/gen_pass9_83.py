#!/usr/bin/env python3
"""gen_pass9_83.py - pass 9-83: open-sky air -> structure void in surface templates.

Explicit air in a template deletes whatever the world has there; structure void (a cell left out of the template) keeps it.
The village street pieces, town centres and the mineshaft headframe saved their whole box as air, so they cut trees in
half (the canopy of a tree already grown from a neighbouring chunk) and, for the 23x15x17 headframe, a cube out of
hillsides. Rule: an air cell at y >= KEEP (default 2: the ground layer and the one above it stay air, which still clears
trunks and plants off the path/pad) with no block anywhere above it in its column becomes void. Air under a roof, a ring
girder or a beam is kept, so interiors stay clear.

Templates: every */streets/*.nbt (villages, abandoned villages, scavenger strongholds), */village/town_center.nbt,
mineshaft/shaft_head_*.nbt. Run after 9_82, before 8_9/build. Safe to re-run (nothing left to change).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtrw import Struct
from gen_pass4_2a import OUT

AIR = {"minecraft:air", "minecraft:cave_air"}
KEEP = 2

def voidify(f, keep=KEEP):
    s = Struct(f.read_bytes()); X, Y, Z = s.size; n = 0
    for x in range(X):
        for z in range(Z):
            for y in range(Y - 1, keep - 1, -1):              # top down until the first real block
                v = s.b.get((x, y, z))
                if v is None: continue                          # already void
                if v[0] not in AIR: break
                del s.b[(x, y, z)]; n += 1
    if n: f.write_bytes(s.bytes())
    return n

def main():
    base = OUT / "structure"
    files = sorted(set(base.rglob("streets/*.nbt")) | set(base.rglob("village/town_center.nbt")) | set(base.glob("mineshaft/shaft_head_*.nbt")))
    total = sum(voidify(f) for f in files)
    print(f"9-83: {total} open-sky air cells -> void in {len(files)} templates")

if __name__ == "__main__":
    main()
