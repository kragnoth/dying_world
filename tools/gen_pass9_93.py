#!/usr/bin/env python3
"""gen_pass9_93.py - pass 9-93: no explicit structure_void blocks in templates. Run after 9_92; safe to re-run.

Structure placement only skips structure voids when *saving* a template; an explicit minecraft:structure_void entry is
placed in the world as a real (invisible, targetable, vein-mineable) block. 9-18 filled the Nether foundry pieces with
them. Every such cell is removed, i.e. left out of the file: the world's block stays.
"""
import glob, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from nbtrw import Struct
ROOT = Path(__file__).resolve().parent.parent
n = files = 0
for f in sorted(glob.glob(f"{ROOT}/datapack/data/*/structure/**/*.nbt", recursive=True)):
    s = Struct(Path(f).read_bytes())
    v = [p for p, b in s.b.items() if b[0] == "minecraft:structure_void"]
    if v:
        for p in v: del s.b[p]
        Path(f).write_bytes(s.bytes()); n += len(v); files += 1
print(f"9-93: removed {n} structure_void blocks from {files} templates")
