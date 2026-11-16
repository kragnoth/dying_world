#!/usr/bin/env python3
"""
gen_pass9_48.py - pass 9-48: datapack side of the Escapement chain.
  data/dying_world/mobrules/the_hollow_echo.json - the Echo: the copy a RELEASED player calls with a Seal while looking through the
      Foundry Lens (kubejs 60_the_hollow.js tags it gh_hollow_echo). Harder than the first fight; it pays residue + Hallmarked gear.
The items, recipes, residue drops and altar logic are modpack kubejs (startup hollow_items.js, progression 60/70/75); quests:
tools/quests/add_escapement_quests.py. Safe to re-run.
"""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "datapack/data/dying_world/mobrules/the_hollow_echo.json"

RULE = {
    "_comment": "pass 9-48: the Echo - a released player's repeat Hollow fight (lens on)",
    "priority": 101, "stop": True,
    "conditions": {"mobs": "mobrules:doppelganger", "has_tags": ["gh_hollow_echo"]},
    "attributes": {"max_health": {"set": 500}, "knockback_resistance": {"set": 0.8}, "follow_range": {"set": 64},
                   "movement_speed": {"multiply": 1.2}, "armor_toughness": {"add": 4}},
    "heal": True,
    "combat": {"damage_dealt": [{"multiply": 2.0}], "regen": {"amount": 2, "interval": 40}, "fire_immune": True,
               "on_hit": {"effects": [{"effect": "minecraft:darkness", "duration": 80, "chance": 0.35},
                                      {"effect": "minecraft:wither", "duration": 60, "chance": 0.2}]}},
    "abilities": [
        {"type": "blink", "cooldown": 120, "windup": 8},
        {"type": "leap", "cooldown": 80, "range": [4, 14], "windup": 6},
        {"type": "pull", "cooldown": 160, "health_below": 0.7, "windup": 12},
        {"type": "shield", "cooldown": 300, "health_below": 0.5, "duration": 80},
        {"type": "summon", "cooldown": 400, "health_below": 0.5, "mobs": [{"mob": "incision:skeletoncultist", "count": 3}],
         "message": "Those who stayed remember you."}],
    "boss_bar": {"color": "purple", "style": "notched_20", "range": 48, "darken_sky": True},
    "name": {"text": "Echo of the Hollow", "color": "dark_purple"}}

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(RULE, indent=2) + "\n")
    print("9-48: the_hollow_echo rule")

if __name__ == "__main__":
    main()
