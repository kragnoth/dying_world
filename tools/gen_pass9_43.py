#!/usr/bin/env python3
"""
gen_pass9_43.py - pass 9-43: Hallmarked UNIQUES for the Incursion trail + Incision tallow as Tarbound candle wax.
Run any time after the datapack exists (no reference zips needed). Safe to re-run.
  data/dying_world/uniques/*.json  - four hand-written Hallmarked uniques tied to the journals. chance {} = they never roll from
      loot or mobs; the Incursion quests hand them out with `/hallmarked generate for {p} 1 unique=<id>` (they arrive Unappraised,
      like any found unique: strike them at the Assay Anvil). Names use the 'hallmarked.unique.<id>' key so the short id resolves.
      Lang lines live in modpack/overrides/kubejs/assets/dying_world/lang/en_us.json (written by this script too).
  data/tarbound/tags/item/candle_wax.json - adds incision:tallow (optional entry) so the flesh biome's tallow makes candles
      for feeding the lodgers.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "datapack/data"
LANG = ROOT / "modpack/overrides/kubejs/assets/dying_world/lang/en_us.json"

def mod(name, attr, op, v): return {"name": name, "attribute": attr, "operation": op, "value": v}
UNIQUES = {
    "gales_bank_shovel": ("minecraft:iron_shovel", "tool", [
        mod("gale_dig", "minecraft:player.block_break_speed", "multiply_total", 0.2),
        mod("gale_burn", "minecraft:generic.burning_time", "multiply_base", -0.4)],
        "Gale's Banking Shovel", "Foreman Gale banked every kiln with it rather than double the draught."),
    "brandts_waxed_hood": ("minecraft:leather_helmet", "helmet", [
        mod("brandt_armor", "minecraft:generic.armor", "addition", 2),
        mod("brandt_sneak", "minecraft:player.sneaking_speed", "addition", 0.3)],
        "Brandt's Waxed Hood", "Speak quietly. Wear wax. Do not drop tools."),
    "marshs_field_boots": ("minecraft:iron_boots", "boots", [
        mod("marsh_fall", "minecraft:generic.safe_fall_distance", "addition", 4),
        mod("marsh_land", "minecraft:generic.fall_damage_multiplier", "multiply_total", -0.25),
        mod("marsh_speed", "minecraft:generic.movement_speed", "multiply_total", 0.03)],
        "Marsh's Field Boots", "She walked the island edges in these and never once looked down."),
    "penitents_lamp": ("hallmarked:emerald_amulet", "bauble", [
        mod("penitent_luck", "minecraft:generic.luck", "addition", 1.5),
        mod("penitent_health", "minecraft:generic.max_health", "addition", 2),
        mod("penitent_resist", "hallmarked:damage_resistance", "multiply_total", 0.04)],
        "The Penitent's Lamp", "He kept a light on for anyone who came asking. You came asking."),
}

def w(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(obj, indent=2) + "\n")

def main():
    lang = json.loads(LANG.read_text()) if LANG.exists() else {}
    for uid, (base, section, mods, name, lore) in UNIQUES.items():
        key = f"hallmarked.unique.{uid}"
        w(OUT / f"dying_world/uniques/{uid}.json", {"name": key, "lore": key + ".lore", "items": {"item": base}, "chance": {},
                                                   section: {"modifiers": mods}})
        lang[key] = name; lang[key + ".lore"] = lore
    w(LANG, dict(sorted(lang.items())))
    w(OUT / "tarbound/tags/item/candle_wax.json", {"replace": False, "values": [{"id": "incision:tallow", "required": False}]})
    print(f"9-43: {len(UNIQUES)} uniques, candle_wax += incision:tallow")

if __name__ == "__main__":
    main()
