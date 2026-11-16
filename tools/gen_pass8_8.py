#!/usr/bin/env python3
"""
gen_pass8_8.py - pass 8-8: overrides for natural structures that are registered in MOD CODE (no structure_set file we could disable in pass 1).
Kills them by emptying their biome tag (replace:true, values:[]) -> they can never pick a biome.
- atmospheric:village_scrubland (user found one via /locate #minecraft:village)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pass4_2a import w, OUT
KILL = ["atmospheric:village_scrubland"]
for sid in KILL:
    ns, p = sid.split(":")
    w(OUT.parent / f"{ns}/tags/worldgen/biome/has_structure/{p}.json", {"replace": True, "values": []})
print(f"8-8: emptied biome tags for {len(KILL)} code-registered structures: {', '.join(KILL)}")
