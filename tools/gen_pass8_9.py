#!/usr/bin/env python3
"""
gen_pass8_9.py - pass 8-9: head-clearance rule for HANGING LANTERNS in every dying_world NBT (incl. worn/mix/stronghold copies of
village houses). Run LAST before build (after 3c4, 5_2, 7_1 ... which rewrite those copies). Safe to re-run.
User rule: a 2-block-tall player must not hit a lantern -> hanging lantern y >= floor + 3 (floor = first non-air block below).
Too low -> lantern moved up under the ceiling (chain refilled above it); if the ceiling is too low for that, it becomes a wall torch on an
adjacent solid block at head height or a standing torch on the floor (torches have no collision), else removed. Script-built structures already obey this via buildkit.
"""
import glob, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from buildkit import H4, full
ROOT = Path(__file__).resolve().parent.parent
PASS = ("minecraft:air", "", "minecraft:cobweb", "minecraft:chain", "minecraft:cave_air", "minecraft:structure_void")
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
stats = {"files": 0, "lifted": 0, "torch": 0, "removed": 0}
for f in glob.glob(str(ROOT / "datapack/data/dying_world/structure/**/*.nbt"), recursive=True) + glob.glob(str(ROOT / "datapack/data/gearwrights/structure/**/*.nbt"), recursive=True):   # 9-25: + the custom Create mills
    s = nbtrw.Struct(Path(f).read_bytes()); changed = False
    for (x, y, z), (n, p, nbt) in list(s.b.items()):
        if n != "minecraft:lantern" or p.get("hanging") != "true": continue
        fl = y - 1
        while fl >= 0 and s.b.get((x, fl, z), ("",))[0] in PASS: fl -= 1
        if fl < 0 or y >= fl + 3: continue                              # no floor in the template (outside / overhang) or already fine
        c = y + 1
        while c < s.size[1] and s.b.get((x, c, z), ("",))[0] in PASS: c += 1
        for yy in range(y, c): s.set(x, yy, z, "minecraft:air")
        changed = True
        if c < s.size[1] and c - 1 >= fl + 3:
            s.set(x, fl + 3, z, "minecraft:lantern", {"hanging": "true", "waterlogged": "false"})
            for yy in range(fl + 4, c): s.set(x, yy, z, "minecraft:chain", {"axis": "y", "waterlogged": "false"})
            stats["lifted"] += 1; continue
        ty = fl + 2
        for d, (dx, dz) in H4.items():
            if full(s.b.get((x + dx, ty, z + dz), ("",))[0]) and s.b.get((x, ty, z), ("",))[0] in PASS:
                s.set(x, ty, z, "minecraft:wall_torch", {"facing": OPP[d]}); stats["torch"] += 1; break
        else:
            if s.b.get((x, fl + 1, z), ("",))[0] in PASS and full(s.b.get((x, fl, z), ("",))[0]):
                s.set(x, fl + 1, z, "minecraft:torch"); stats["torch"] += 1     # standing torch on the floor (no collision, keeps the light)
            else: stats["removed"] += 1
    if changed: Path(f).write_bytes(s.bytes()); stats["files"] += 1
print("8-9 lanterns:", stats)
