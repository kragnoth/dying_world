#!/usr/bin/env python3
"""
gen_pass9_51.py - pass 9-51: "what waits there is wearing their face" - the Hollow takes the herds.
USER: the heavier a player's Hollow, the more nearby friendly/neutral mobs spawn hostile. Weight = residue tier (from the tinker's
workshop on) + days held after the Hollow; release resets it; top chance 50%.
  datapack data/dying_world/mobrules/hollow_taken.json - mobs tagged gh_hollow_taken (by kubejs 85_hollow_taken.js) attack players,
      move a little faster, are named 'Taken <mob>' and sometimes drop Foundry Residue.
Safe to re-run.
"""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "datapack/data/dying_world/mobrules/hollow_taken.json"
RULE = {
    "_comment": "pass 9-51: friendly/neutral mobs the Hollow has taken (tagged by kubejs 85_hollow_taken.js near Hollow-heavy players)",
    "priority": 90, "stop": True,
    "conditions": {"has_tags": ["gh_hollow_taken"]},
    "behavior": {"hostile_to": ["minecraft:player"], "attack_damage": 3, "angry_on_spawn": True, "griefing": False},
    "attributes": {"movement_speed": {"multiply": 1.25}, "follow_range": {"set": 24}},
    "name": {"text": "Taken {mob}", "color": "dark_gray"},
    "loot": {"drops": [{"item": "gearwrights:foundry_residue", "count": 1, "chance": 0.15, "player_kill_only": True}]}}

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(RULE, indent=2) + "\n")
    print("9-51: hollow_taken rule")

if __name__ == "__main__":
    main()
