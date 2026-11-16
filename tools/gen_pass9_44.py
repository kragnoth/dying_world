#!/usr/bin/env python3
"""
gen_pass9_44.py - pass 9-44: THE HOLLOW, the finale arena (the Guild's first gate; "every record points back to the Hollow").
Run after gen_pass9_12 (registers palettes); safe to re-run.
  structure/station/hollow/: marker (surface hut + mast, sign), shaft_1..2 (scaffold shafts), arena (33x18x33 hall: pillar ring,
      tinted-glass 'mirrors', candlelit dais with the ALTAR = reinforced deepslate, unobtainable in survival).
  worldgen: structure dying_world:the_hollow, set the_hollow (concentric rings, distance 40 / spread 3 / count 6: far out, a handful
      per world), tag dying_world:the_hollow, loot table dying_world:map/the_hollow (the Seal quest hands it out via /loot give).
  data/dying_world/mobrules/the_hollow.json: the Mob Rules rule for the boss (mobrules:doppelganger tagged gh_hollow).
The trigger + reward live in modpack kubejs (server_scripts/progression/60_the_hollow.js): right-click the altar with a Gearwright's Seal
inside the_hollow -> /mobrules doppelganger <player> <pos> gh_hollow; its death tags the owner + killer gh_hollow_defeated (quest stage).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import L as NL
import gen_pass9_11 as K
import gen_pass9_12  # noqa: F401  (palettes)
import gen_pass9_34 as H
from gen_pass9_11 import P, pe, salt
from gen_pass4_2a import M, R, w, OUT

SITE = "hollow"; K.PAL_OF[SITE] = "ow"
D = OUT / f"structure/station/{SITE}"; POOL = f"dying_world:station/{SITE}"
NS = "dying_world"; BIOMES = "#dying_world:has_structure/scavenger_outpost_any"

def sign_nbt(*lines):
    side = lambda ls: (10, {"messages": NL(8, [json.dumps({"text": t}) for t in ls]), "color": (8, "black"), "has_glowing_text": (1, 0)})
    return {"id": M("sign"), "front_text": side(lines), "back_text": side(("", "", "", "")), "is_waxed": (1, 1)}

def marker():
    F = 3
    p = P(SITE, "marker", 9, 14, 9, 71)
    for x in range(9):
        for z in range(9):
            for y in range(F): p.blk(x, y, z, "base")
            p.blk(x, F, z, "floor"); p.blk(x, F + 5, z, "ceil")
            for y in range(F + 1, F + 5):
                if x in (0, 8) or z in (0, 8):
                    corner = x in (0, 8) and z in (0, 8)
                    p.blk(x, y, z, "pillar" if corner else "base" if y == F + 1 else "trim" if y == F + 4 else "wall")
                else: p.b(x, y, z, M("air"))
            for y in range(F + 6, 14): p.b(x, y, z, M("air"))
    for y in range(1, F + 1): p.b(4, y, 4, *H.SCAF_B)
    for y in (F + 1, F + 2): p.b(4, y, 8, M("air"))
    p.b(4, 0, 4, M("jigsaw"), {"orientation": "down_north"}, H.jig_nbt(H.DOWN, H.UP, f"{POOL}/shaft_1"))
    for x, z in ((3, 3), (5, 3), (3, 5), (5, 5), (3, 4), (5, 4), (4, 3)): p.b(x, F + 1, z, M("chain"), {"axis": "y", "waterlogged": "false"})
    p.b(4, F + 4, 2, M("soul_lantern"), {"hanging": "true", "waterlogged": "false"})
    p.b(2, F + 2, 7, M("spruce_wall_sign"), {"facing": "north", "waterlogged": "false"},
        sign_nbt("GEARWRIGHTS", "THE HOLLOW", "First gate.", "SEALED BY ORDER."))
    for y in range(F + 6, 13): p.b(4, y, 4, M("iron_bars"))
    p.b(4, 13, 4, M("soul_lantern"), {"hanging": "false", "waterlogged": "false"})
    return p

def arena():
    X = Z = 33; Y = 18; C = 16
    p = P(SITE, "arena", X, Y, Z, 72); p.shell()
    for x in range(1, X - 1):                                                   # floor: worn rings round the dais
        for z in range(1, Z - 1):
            d = max(abs(x - C), abs(z - C))
            if d in (6, 11): p.b(x, 0, z, M("polished_deepslate"))
            elif d < 6 and p.r.random() < .12: p.b(x, 0, z, M("cracked_deepslate_tiles"))
    for x, z in ((6, 6), (26, 6), (6, 26), (26, 26), (4, C), (28, C), (C, 28)):  # pillar ring (north gap = the stair)
        for y in range(1, Y - 1): p.blk(x, y, z, "pillar")
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p.b(x + dx, Y - 2, z + dz, M("soul_lantern"), {"hanging": "true", "waterlogged": "false"})
    for face in ("e", "w", "s"):                                                # the mirrors: tinted glass set into three walls
        for k in range(-2, 3):
            for y in range(3, 8):
                if face == "s": p.b(C + k, y, Z - 1, M("tinted_glass"))
                else: p.b(0 if face == "w" else X - 1, y, C + k, M("tinted_glass"))
    for x in range(C - 2, C + 3):                                               # dais + altar
        for z in range(C - 2, C + 3): p.b(x, 1, z, M("polished_deepslate"))
    p.b(C, 2, C, M("reinforced_deepslate"))
    for x, z in ((C - 2, C - 2), (C + 2, C - 2), (C - 2, C + 2), (C + 2, C + 2)):
        p.b(x, 2, z, M("candle"), {"candles": "4", "lit": "true", "waterlogged": "false"})
    for x, z in ((C - 1, C + 3), (C + 3, C), (C - 3, C - 1), (C + 1, C - 3)): p.b(x, 1, z, M("crying_obsidian"))
    for x, z in ((1, 1), (X - 2, 1), (1, Z - 2), (X - 2, Z - 2), (2, 1), (1, 2)): p.b(x, Y - 2, z, M("cobweb"))
    for y in range(1, Y - 1): p.b(C, y, 2, *H.SCAF_B)                            # the way down from the marker
    p.b(C, Y - 1, 2, M("jigsaw"), {"orientation": "up_north"}, H.jig_nbt(H.UP, H.DOWN, "minecraft:empty"))
    p.b(C + 1, 2, 1, M("spruce_wall_sign"), {"facing": "south", "waterlogged": "false"},
        sign_nbt("Do not bring", "the seal down", "unless you mean", "to finish it."))
    for x, z in ((C - 6, 2), (C + 6, 2), (2, C - 6), (X - 3, C + 6)): p.light(x, Y - 2, z)
    return p

def main():
    assert (OUT / "structure/station/proving/hub.nbt").exists(), "run gen_pass9_12 first"
    D.mkdir(parents=True, exist_ok=True)
    H.SITE = SITE                                                               # reuse 9-34's shaft piece for this site
    tp = OUT / f"worldgen/template_pool/station/{SITE}"
    w(tp / "marker.json", {"fallback": "minecraft:empty", "elements": [pe(marker().save(D), 1)]})
    w(tp / "shaft_1.json", {"fallback": "minecraft:empty", "elements": [pe(H.shaft(1, f"{POOL}/shaft_2").save(D), 1)]})
    w(tp / "shaft_2.json", {"fallback": "minecraft:empty", "elements": [pe(H.shaft(2, f"{POOL}/arena").save(D), 1)]})
    w(tp / "arena.json", {"fallback": "minecraft:empty", "elements": [pe(arena().save(D), 1)]})
    w(OUT / "worldgen/structure/the_hollow.json", {
        "type": "minecraft:jigsaw", "biomes": BIOMES, "start_pool": f"{POOL}/marker", "size": 4, "max_distance_from_center": 80,
        "start_height": {"absolute": -3}, "project_start_to_heightmap": "WORLD_SURFACE_WG", "terrain_adaptation": "none",
        "step": "strongholds", "use_expansion_hack": False,
        "spawn_overrides": {"monster": {"bounding_box": "full", "spawns": []}}})
    w(OUT / "worldgen/structure_set/the_hollow.json", {
        "structures": [{"structure": f"{NS}:the_hollow", "weight": 1}],
        "placement": {"type": "minecraft:concentric_rings", "distance": 40, "spread": 3, "count": 6, "preferred_biomes": BIOMES,
                      "salt": salt(f"{NS}:the_hollow")}})
    w(OUT / "tags/worldgen/structure/the_hollow.json", {"values": [f"{NS}:the_hollow"]})
    w(OUT / "loot_table/map/the_hollow.json", {"type": "minecraft:chest", "pools": [{"rolls": 1, "entries": [
        {"type": "minecraft:item", "name": "minecraft:map", "functions": [
            {"function": "minecraft:exploration_map", "destination": f"{NS}:the_hollow", "decoration": "minecraft:red_x",
             "zoom": 2, "search_radius": 100, "skip_existing_chunks": False},
            {"function": "minecraft:set_name", "target": "item_name", "name": {"text": "Guild Register: The Hollow"}}]}]}]})
    w(OUT / "mobrules/the_hollow.json", {
        "_comment": "pass 9-44: the Hollow's copy of whoever brought the seal down (spawned by kubejs 60_the_hollow.js)",
        "priority": 100, "stop": True,
        "conditions": {"mobs": "mobrules:doppelganger", "has_tags": ["gh_hollow"]},
        "attributes": {"max_health": {"set": 300}, "knockback_resistance": {"set": 0.6}, "follow_range": {"set": 64},
                       "movement_speed": {"multiply": 1.15}},
        "heal": True,
        "combat": {"damage_dealt": [{"multiply": 1.5}], "regen": {"amount": 1, "interval": 40}, "fire_immune": True,
                   "on_hit": {"effects": [{"effect": "minecraft:darkness", "duration": 60, "chance": 0.25}]}},
        "abilities": [
            {"type": "blink", "cooldown": 160, "windup": 10},
            {"type": "leap", "cooldown": 100, "range": [4, 12], "windup": 8},
            {"type": "pull", "cooldown": 200, "health_below": 0.6, "windup": 15},
            {"type": "shield", "cooldown": 400, "health_below": 0.4, "duration": 60},
            {"type": "summon", "cooldown": 600, "health_below": 0.3, "mobs": [{"mob": "incision:skeletoncultist", "count": 2}],
             "message": "Those who stayed answer it."}],
        "boss_bar": {"color": "purple", "style": "notched_10", "range": 48, "darken_sky": True}})
    print("9-44: the_hollow (marker, 2 shafts, arena), ring set, map table, Mob Rules boss rule")

if __name__ == "__main__":
    main()
