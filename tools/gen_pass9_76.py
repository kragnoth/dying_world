#!/usr/bin/env python3
"""gen_pass9_76.py - pass 9-76: footings for the Nether research station's buildings (normal + derelict).
Each building NBT stands on 12-deep stilts of stripped crimson
stem (fireproof), so it can't hang over a Nether drop. See tools/footing.py. The dig camp gets its footing in gen_pass9_36.
Run after gen_pass9_15 / 9_23 (which write these NBTs), any time before build. Safe to re-run (an old footing is replaced)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from footing import add_footing
from gen_pass4_2a import OUT

BUILDINGS = ("workshop", "garden", "library", "quarters", "storehouse", "boiler", "watchpost", "containment")

def main():
    n = 0
    for site in ("nether", "nether_derelict"):
        for b in BUILDINGS:
            f = OUT / f"structure/station/{site}/{b}.nbt"
            if f.exists() and add_footing(f, 12, "minecraft:stripped_crimson_stem"): n += 1
    print(f"9-76: stilts on {n} Nether station buildings")

if __name__ == "__main__":
    main()
