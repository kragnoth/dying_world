#!/usr/bin/env python3
"""
gen_pass6_1.py - pass 6-1: stop gearwrights abandoned ruins/hamlets/villages from FLOATING over eroded hillsides.
Sets terrain_adaptation = beard_box on every dying_world:abandoned_{ruin,hamlet,village}_* structure (fills terrain under each piece).
Post-edit: run AFTER gen_pass3b2.py / gen_pass3c4.py (they rewrite these files). Safe to re-run. No other changes (user: landmarks stay as-is).
"""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "datapack/data/dying_world/worldgen/structure"
n = 0
for p in sorted(D.glob("abandoned_*.json")):
    if not any(k in p.name for k in ("abandoned_ruin_", "abandoned_hamlet_", "abandoned_village_")): continue
    j = json.loads(p.read_text())
    if j.get("terrain_adaptation") != "beard_box":
        j["terrain_adaptation"] = "beard_box"; p.write_text(json.dumps(j, indent=2) + "\n"); n += 1
print(f"6-1: beard_box set on {n} abandoned ruin/hamlet/village structures")
