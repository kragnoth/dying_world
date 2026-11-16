#!/usr/bin/env python3
"""
gen_pass9_49.py - pass 9-49: being locked in the Foundry is a real choice.
USER: release should cost some power; a Hallmarked 'Hollowed' set and uniques that drop while locked.
  datapack data/dying_world/sets/hollowed.json - 'Vestments of the Hollowed' (5 pieces, netherite-grade, never in chests or natural
      rolls: chance {} / no tables). Dropped only by kubejs 75_foundry_residue.js for LOCKED players (Hollowed, not escaped).
  datapack data/dying_world/uniques/{revenants_shroud,kiln_hook,hollow_bell}.json - uniques, chance {} (same rule: locked drops only).
  lang (kubejs/assets/dying_world/lang/en_us.json): set + piece + unique names and lore.
  skill tree (kubejs_base): Hollow Sight (locked) = 3 keystone perks + a stat line; NEW Lens Sight (released, lens on) = Arcane Ward + Hex
      only, no stats. kubejs 60_the_hollow.js switches between them.
Safe to re-run.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "datapack/data/dying_world"
LANG = ROOT / "modpack/overrides/kubejs/assets/dying_world/lang/en_us.json"
TREE = ROOT / "kubejs_base/data/kskills/puffish_skills/categories/skill_tree"

def mod(name, attr, op, v): return {"name": name, "attribute": attr, "operation": op, "value": v}
TRIM = {"pattern": "minecraft:eye", "material": "minecraft:amethyst"}
SET = {
    "name": "hallmarked.set.hollowed", "color": "dark_purple", "chance": {},
    "pieces": [
        {"key": "cowl", "item": "minecraft:leather_helmet", "base_stats": {"armor": 3, "toughness": 3, "knockback_resistance": 0.1},
         "durability": 407, "dye": "#1c1626", "trim": TRIM, "fire_resistant": True,
         "modifiers": [mod("hollowed_cowl_resist", "lodestone:magic_resistance", "addition", 1)]},
        {"key": "vestment", "item": "minecraft:chainmail_chestplate", "base_stats": {"armor": 8, "toughness": 3, "knockback_resistance": 0.1},
         "durability": 592, "trim": TRIM, "fire_resistant": True,
         "modifiers": [mod("hollowed_vestment_health", "minecraft:generic.max_health", "addition", 4)]},
        {"key": "greaves", "item": "minecraft:iron_leggings", "base_stats": {"armor": 6, "toughness": 3, "knockback_resistance": 0.1},
         "durability": 555, "trim": TRIM, "fire_resistant": True,
         "modifiers": [mod("hollowed_greaves_speed", "minecraft:generic.movement_speed", "multiply_total", 0.03)]},
        {"key": "treads", "item": "minecraft:leather_boots", "base_stats": {"armor": 3, "toughness": 3, "knockback_resistance": 0.1},
         "durability": 481, "dye": "#1c1626", "trim": TRIM, "fire_resistant": True,
         "modifiers": [mod("hollowed_treads_fall", "minecraft:generic.safe_fall_distance", "addition", 2)]},
        {"key": "censer", "item": "hallmarked:emerald_amulet", "glint": True,
         "modifiers": [mod("hollowed_censer_luck", "minecraft:generic.luck", "addition", 1),
                       mod("hollowed_censer_magic", "lodestone:magic_damage", "addition", 1)]}],
    "bonuses": [
        {"pieces": 2, "modifiers": [mod("hollowed_2_magic", "caverns_and_chasms:magic_protection", "addition", 0.1)]},
        {"pieces": 3, "modifiers": [], "procs": [{"type": "leech", "chance": 0.2, "power": 0.15}]},
        {"pieces": 4, "modifiers": [mod("hollowed_4_health", "minecraft:generic.max_health", "addition", 4),
                                    mod("hollowed_4_damage", "minecraft:generic.attack_damage", "multiply_total", 0.08)],
         "effects": [{"effect": "minecraft:night_vision", "amplifier": 0}]},
        {"pieces": 5, "modifiers": [mod("hollowed_5_resist", "hallmarked:damage_resistance", "multiply_total", 0.05)],
         "procs": [{"type": "reaper", "chance": 1.0, "power": 4}, {"type": "bleed", "chance": 0.2, "power": 1.5, "duration": 80}]}]}
SET_NAMES = {"": "Vestments of the Hollowed", "cowl": "Hollowed Cowl", "vestment": "Hollowed Vestment", "greaves": "Hollowed Greaves",
             "treads": "Hollowed Treads", "censer": "Hollowed Censer"}

UNIQUES = {
    "revenants_shroud": ("minecraft:leather_chestplate", "chestplate", [
        mod("shroud_armor", "minecraft:generic.armor", "addition", 4), mod("shroud_tough", "minecraft:generic.armor_toughness", "addition", 2),
        mod("shroud_health", "minecraft:generic.max_health", "addition", 6)],
        "The Revenant's Shroud", "It stayed. It wore this the whole time."),
    "kiln_hook": ("minecraft:iron_sword", "tool", [
        mod("kiln_hook_damage", "minecraft:generic.attack_damage", "multiply_total", 0.15),
        mod("kiln_hook_reach", "minecraft:player.entity_interaction_range", "addition", 0.75),
        mod("kiln_hook_burn", "minecraft:generic.burning_time", "multiply_base", -0.5)],
        "The Kiln Hook", "Pulled the clinker from the Guild's first kiln, and other things after."),
    "hollow_bell": ("hallmarked:emerald_amulet", "bauble", [
        mod("hollow_bell_luck", "minecraft:generic.luck", "addition", 1.5),
        mod("hollow_bell_resist", "hallmarked:damage_resistance", "multiply_total", 0.05),
        mod("hollow_bell_magic", "lodestone:magic_damage", "addition", 2)],
        "The Hollow Bell", "It rang once, when the first gate opened. It is ringing now."),
}

def w(p, o): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")

def tree():
    dp = TREE / "definitions.json"; d = json.loads(dp.read_text())
    perk = lambda p: {"type": "kskills_perks:perk", "data": {"perk": p, "level": 1}}
    attr = lambda a, v: {"type": "puffish_skills:attribute", "data": {"attribute": a, "value": v, "operation": "add"}}
    hs = d["x_hollow_sight"]
    hs["rewards"] = [perk("soul_siphon"), perk("arcane_ward"), perk("hex"),
                     attr("minecraft:generic.armor", 2), attr("minecraft:generic.attack_damage", 1), attr("minecraft:generic.max_health", 4)]
    hs["description"] = ["", {"text": "✦ Soul Siphon, Arcane Ward and Hex, wherever your path ran\n", "color": "light_purple"},
                         {"text": "+2 Armor\n", "color": "green"}, {"text": "+1 Attack Damage\n", "color": "green"},
                         {"text": "+4 Max Health\n", "color": "green"},
                         {"text": "Only while the Foundry holds you (locked in its vision)", "color": "gray"}]
    d["x_lens_sight"] = {
        "title": {"text": "Lens Sight", "color": "dark_purple", "bold": True},
        "description": ["", {"text": "✦ Arcane Ward and Hex\n", "color": "light_purple"},
                        {"text": "Only while you look through the Foundry Lens", "color": "gray"}],
        "icon": {"type": "item", "data": {"item": "minecraft:spyglass"}},
        "frame": {"type": "advancement", "data": {"frame": "goal"}}, "size": 1.0, "cost": 0,
        "rewards": [perk("arcane_ward"), perk("hex")],
        "extra_description": ["", {"text": "What you let go of, you only borrow back.\n", "color": "dark_gray", "italic": True},
                              {"text": "Capstone • Released players, lens on", "color": "dark_aqua"}],
        "required_mods": ["kskills_perks", "caverns_and_chasms", "lodestone"]}
    dp.write_text(json.dumps(d, indent="\t", ensure_ascii=False) + "\n")
    sp = TREE / "skills.json"; s = json.loads(sp.read_text())
    s["lens_sight_1"] = {"x": -800, "y": 356, "definition": "x_lens_sight"}
    sp.write_text(json.dumps(s, indent="\t", ensure_ascii=False) + "\n")

def main():
    w(DATA / "sets/hollowed.json", SET)
    lang = json.loads(LANG.read_text()) if LANG.exists() else {}
    for k, v in SET_NAMES.items(): lang["hallmarked.set.hollowed" + ("." + k if k else "")] = v
    for uid, (base, section, mods, name, lore) in UNIQUES.items():
        key = f"hallmarked.unique.{uid}"
        w(DATA / f"uniques/{uid}.json", {"name": key, "lore": key + ".lore", "items": {"item": base}, "chance": {}, section: {"modifiers": mods}})
        lang[key] = name; lang[key + ".lore"] = lore
    w(LANG, dict(sorted(lang.items())))
    tree()
    print("9-49: Hollowed set, 3 locked-only uniques, Hollow Sight (full) / Lens Sight (reduced)")

if __name__ == "__main__":
    main()
