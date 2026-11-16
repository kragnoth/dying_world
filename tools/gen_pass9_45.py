#!/usr/bin/env python3
"""
gen_pass9_45.py - pass 9-45: the endgame reward is a max-tier perk node, 'Hollowed'.
Edits the user's skill tree in kubejs_base/data/kskills/puffish_skills (the user's kubejs data).
  definition x_hollowed + skill hollowed_1, off the Occult rim (x -800). NO connections and cost 0: players can't buy it and it costs no
  points; kubejs 60_the_hollow.js unlocks it (/puffish_skills skills unlock) when your copy dies in the Hollow, and re-unlocks it on login
  for anyone tagged gh_hollow_defeated (so a respec can't take it away).
  It grants all three Occult keystone perks (Soul Siphon, Arcane Ward, Hex) whatever path you walked, plus a stat line.
Safe to re-run (replaces its own entries).
"""
import json
from pathlib import Path
T = Path(__file__).resolve().parent.parent / "kubejs_base/data/kskills/puffish_skills/categories/skill_tree"

def txt(t, color, **kw): return dict({"text": t, "color": color}, **kw)
def attr(a, v): return {"type": "puffish_skills:attribute", "data": {"attribute": a, "value": v, "operation": "add"}}
def perk(p): return {"type": "kskills_perks:perk", "data": {"perk": p, "level": 1}}

HOLLOWED = {
    "title": txt("Hollowed", "dark_purple", bold=True),
    "description": ["",
        txt("✦ Soul Siphon, Arcane Ward and Hex, wherever your path ran\n", "light_purple"),
        txt("+4 Max Health\n", "green"), txt("+1 Luck\n", "green"), txt("+10% Magic Protection\n", "green"),
        txt("+2 Magic Damage (Lodestone)\n", "green"), txt("+5% Cooldown Reduction", "green")],
    "icon": {"type": "item", "data": {"item": "minecraft:reinforced_deepslate"}},
    "frame": {"type": "advancement", "data": {"frame": "challenge"}},
    "size": 1.5, "cost": 0,
    "rewards": [perk("soul_siphon"), perk("arcane_ward"), perk("hex"),
                attr("minecraft:generic.max_health", 4), attr("minecraft:generic.luck", 1),
                attr("caverns_and_chasms:magic_protection", 0.1), attr("lodestone:magic_damage", 2),
                attr("apothic_attributes:cooldown_reduction", 0.05)],
    "extra_description": ["",
        txt("It wore your face. Now you wear what it kept.\n", "dark_gray", italic=True),
        txt("Capstone • Cannot be learned\n", "dark_aqua"),
        txt("Earned by putting down what waits in the Hollow", "dark_purple")],
    "required_mods": ["kskills_perks", "neovitae", "caverns_and_chasms", "lodestone", "apothic_attributes"],
}

def edit(name, fn):
    p = T / name; d = json.loads(p.read_text()); fn(d)
    p.write_text(json.dumps(d, indent="\t", ensure_ascii=False) + "\n")

def main():
    edit("definitions.json", lambda d: d.__setitem__("x_hollowed", HOLLOWED))
    edit("skills.json", lambda d: d.__setitem__("hollowed_1", {"x": -800, "y": 228, "definition": "x_hollowed"}))
    print("9-45: Hollowed capstone (x_hollowed / hollowed_1)")

if __name__ == "__main__":
    main()
