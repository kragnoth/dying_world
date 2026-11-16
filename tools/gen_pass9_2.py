#!/usr/bin/env python3
"""
gen_pass9_2.py - pass 9-2: denser villages on VANILLA streets (plains/taiga/snowy since 8-11). Post-edit, run after gen_pass3c4.py. Safe to re-run.
Vanilla street pieces carry ~2.4 house plots each (the dropped vsrevamped streets ~3.9, savanna custom ~7.8), so size 6 left villages thin.
-> jigsaw size 3 -> 6 and max_distance_from_center 65 -> 80 (vanilla village values) for dying_world:village_{plains,taiga,snowy}. (Plains pool weights rebalanced in gen_pass9_1.py.)
"""
import json
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "datapack/data/dying_world/worldgen/structure"
for fam in ("plains", "taiga", "snowy"):
    p = D / f"village_{fam}.json"; j = json.loads(p.read_text())
    j["size"], j["max_distance_from_center"] = 6, 80   # = vanilla village values (ours were 3 / 65)
    p.write_text(json.dumps(j, indent=2) + "\n")
print("9-2: village_plains/taiga/snowy -> size 6, radius 80")
