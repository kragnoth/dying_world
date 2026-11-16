#!/usr/bin/env python3
"""
gen_pass9_26.py - pass 9-26: theme-audit fixes (tools/theme_audit.py -> docs/theme_audit.md). Run after 9_21, 9_24, 9_25 (they write the ruined/abandoned
NBTs) and BEFORE 9_19/9_22 (stronghold copies). Safe to re-run.
- ABANDONED = DARK (our own design rule from 9-8: abandoned settlements unlit + undead): every ruined house (5 families incl. rare styles, swamp stilts) and the
  abandoned Create mills lose their lights - hanging lanterns removed (the chain stays as a broken lamp), standing lanterns/torches removed, campfires out.
  (They kept their lanterns from the ruined finish; 55-77 lit lanterns per abandoned village type also suppressed the undead spawns.)
"""
import glob, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
ROOT = Path(__file__).resolve().parent.parent
LIGHTS = ("minecraft:lantern", "minecraft:soul_lantern", "minecraft:torch", "minecraft:wall_torch", "minecraft:soul_torch", "minecraft:soul_wall_torch")
def main():
    files = glob.glob(str(ROOT / "datapack/data/dying_world/structure/*/*_ruined.nbt")) + glob.glob(str(ROOT / "datapack/data/gearwrights/structure/village/*/*_abandoned.nbt"))
    n = 0
    for f in files:
        s = nbtrw.Struct(Path(f).read_bytes()); ch = False
        for p, (b, pr, nb) in list(s.b.items()):
            if b in LIGHTS: s.b[p] = ("minecraft:air", {}, None); n += 1; ch = True
            elif b.endswith("campfire") and pr.get("lit") == "true": s.b[p] = (b, dict(pr, lit="false"), nb); n += 1; ch = True
        if ch: Path(f).write_bytes(s.bytes())
    print(f"9-26: {n} lights put out in {len(files)} ruined/abandoned NBTs")
if __name__ == "__main__":
    main()
