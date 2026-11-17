#!/usr/bin/env python3
"""
gen_pass9_53.py - pass 9-53: Hollow Sight / Lens Sight use kskills_perks 1.1.0's tag conditions instead of KubeJS swapping nodes.
Both nodes are unlocked once (when Hollowed) and stay unlocked; their rewards switch themselves on and off:
  Hollow Sight: 3 Occult keystone perks + 2 armor, 1 attack damage, 4 max health  while wv_occult_foundry, unless gh_escaped
  Lens Sight:   Arcane Ward + Hex                                                 while wv_occult_foundry and gh_escaped
Needs kskills_perks 1.1.0+. Safe to re-run.
"""
import json
from pathlib import Path
TREE = Path(__file__).resolve().parent.parent / "kubejs_base/data/kskills/puffish_skills/categories/skill_tree"
HELD = {"while_tags": "wv_occult_foundry", "unless_tags": "gh_escaped"}
LENS = {"while_tags": ["wv_occult_foundry", "gh_escaped"]}

def perk(p, cond): return {"type": "kskills_perks:perk", "data": dict({"perk": p, "level": 1}, **cond)}
def attr(a, v, cond): return {"type": "kskills_perks:attribute", "data": dict({"attribute": a, "value": v, "operation": "add"}, **cond)}

def main():
    dp = TREE / "definitions.json"; d = json.loads(dp.read_text())
    d["x_hollow_sight"]["rewards"] = [perk("soul_siphon", HELD), perk("arcane_ward", HELD), perk("hex", HELD),
        attr("minecraft:generic.armor", 2, HELD), attr("minecraft:generic.attack_damage", 1, HELD),
        attr("minecraft:generic.max_health", 4, HELD)]
    d["x_lens_sight"]["rewards"] = [perk("arcane_ward", LENS), perk("hex", LENS)]
    for k in ("x_hollow_sight", "x_lens_sight"):
        mods = d[k].setdefault("required_mods", [])
        if "kskills_perks" not in mods: mods.insert(0, "kskills_perks")
    dp.write_text(json.dumps(d, indent="\t", ensure_ascii=False) + "\n")
    print("9-53: sight nodes now tag-conditional")

if __name__ == "__main__":
    main()
