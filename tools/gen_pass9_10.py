#!/usr/bin/env python3
"""
gen_pass9_10.py - pass 9-10: ADDITIVE mob drops via NeoForge global loot modifiers (neoforge:add_table) - nothing replaced, so other datapacks/mods that
change these mobs' loot keep working. Player kills only; Looting raises the chance (random_chance_with_enchanted_bonus). Safe to re-run.
- piglin / piglin brute: occasional gold (nuggets, rarely an ingot) + rare snout armor trim template (for vanilla-minded players).
  User rule: only bastion loot NOT already in scavenger structures -> a scan showed the scavenger stronghold tables already contain every bastion item
  (incl. the netherite upgrade template), so nothing else is added. Brutes ~3-4x the piglin chance.
- drowned: heart of the sea 0.5% (Looting +0.25%/level) - the conduit had no source after buried treasure was disabled.
Files: data/neoforge/loot_modifiers/global_loot_modifiers.json (replace:false, merges with other packs), data/dying_world/loot_modifiers/*.json,
data/dying_world/loot_table/entities/*.json.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pass4_2a import w, OUT

def chance(base, per):
    return {"condition": "minecraft:random_chance_with_enchanted_bonus", "enchantment": "minecraft:looting", "unenchanted_chance": base,
            "enchanted_chance": {"type": "minecraft:linear", "base": base + per, "per_level_above_first": per}}
def pool(entry, base, per, count=None):
    e = {"type": "minecraft:item", "name": entry}
    if count: e["functions"] = [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": count[0], "max": count[1]}}]
    return {"rolls": 1, "entries": [e], "conditions": [chance(base, per)]}

TABLES = {
    "piglin_extra": [pool("minecraft:gold_nugget", .10, .03, (2, 6)), pool("minecraft:gold_ingot", .02, .01), pool("minecraft:snout_armor_trim_smithing_template", .004, .002)],
    "piglin_brute_extra": [pool("minecraft:gold_nugget", .30, .05, (3, 9)), pool("minecraft:gold_ingot", .08, .02, (1, 2)), pool("minecraft:snout_armor_trim_smithing_template", .015, .005)],
    "drowned_extra": [pool("minecraft:heart_of_the_sea", .005, .0025)],
}
MODS = {"piglin_extra": "minecraft:entities/piglin", "piglin_brute_extra": "minecraft:entities/piglin_brute", "drowned_extra": "minecraft:entities/drowned"}
for name, pools in TABLES.items():
    w(OUT / f"loot_table/entities/{name}.json", {"type": "minecraft:entity", "pools": pools})
    w(OUT / f"loot_modifiers/{name}.json", {"type": "neoforge:add_table",
      "conditions": [{"condition": "neoforge:loot_table_id", "loot_table_id": MODS[name]}, {"condition": "minecraft:killed_by_player"}],
      "table": f"dying_world:entities/{name}"})
w(OUT.parent / "neoforge/loot_modifiers/global_loot_modifiers.json", {"replace": False, "entries": [f"dying_world:{n}" for n in TABLES]})
print(f"9-10: {len(TABLES)} additive loot modifiers (piglin, piglin brute, drowned)")
