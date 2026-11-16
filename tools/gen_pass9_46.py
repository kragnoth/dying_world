#!/usr/bin/env python3
"""
gen_pass9_46.py - pass 9-46: the Occult Foundry vision becomes the Hollow's mark (needs Wasteland Vision 0.24.1, Mob Rules 0.7.1).
USER: before the Hollow the world looks normal; killing your copy locks you into occult_foundry; the (later) Escapement frees you,
then the vision is a toggle that needs the Foundry Lens. While locked: harsher spawns. Hollowed's perks only work in the vision.
  modpack config: wastelandvision-server.toml forceVision=false (config/ and defaultconfigs/); wastelandvision-client.toml startActive=false.
  occult_foundry/vision.json: "items": foundry_lens (head slot, key, rare) + its texture in the vision folder's assets.
  datapack: data/dying_world/mobrules/foundry_haunting.json - a spawner around players tagged wv_occult_foundry + gh_hollow_defeated
      and NOT gh_escaped: skeleton cultists in the dark (overworld).
  kubejs_base skill tree: x_hollowed keeps the stat line; the three perks move to x_hollow_sight / hollow_sight_1 (cost 0, unconnected),
      which kubejs 60_the_hollow.js unlocks while the player is in the vision and locks when they leave it.
Safe to re-run.
"""
import json, re
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "modpack/overrides/config"
VISION = CFG / "wastelandvision/visions/occult_foundry"
TREE = ROOT / "kubejs_base/data/kskills/puffish_skills/categories/skill_tree"
RULE = ROOT / "datapack/data/dying_world/mobrules/foundry_haunting.json"

def toml_set(p, key, val):
    s = p.read_text(); n = re.subn(rf"(?m)^{key} = .*$", f"{key} = {val}", s); assert n[1] == 1, key; p.write_text(n[0])

def lens_png(path):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); px = im.load()
    O = (40, 24, 14, 255); B = [(110, 70, 30, 255), (164, 112, 46, 255), (214, 166, 82, 255)]
    G = [(30, 66, 60, 235), (44, 112, 96, 225), (120, 214, 180, 210)]               # soul-fire glass
    cx, cy, r = 9.5, 6.5, 5.2
    for y in range(16):
        for x in range(16):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** .5; t = (x - cx) + (y - cy)
            if d <= r - 1.6: px[x, y] = G[2] if t < -3 else G[1] if t < 1.5 else G[0]
            elif d <= r - .6: px[x, y] = B[2] if t < -1 else B[1] if t < 2 else B[0]
            elif d <= r + .3: px[x, y] = O
    for x, y in ((7, 4), (8, 3)): px[x, y] = (236, 255, 246, 255)
    for x, y in ((9, 6), (10, 7)): px[x, y] = (70, 160, 130, 255)                    # a mote in the glass
    for i, (x, y) in enumerate(((5, 10), (4, 11), (4, 12), (3, 13), (2, 14), (2, 15))): px[x, y] = B[1] if i % 2 == 0 else O
    path.parent.mkdir(parents=True, exist_ok=True); im.save(path)

def main():
    toml_set(CFG / "wastelandvision-server.toml", "forceVision", "false")
    toml_set(CFG / "wastelandvision-client.toml", "startActive", "false")

    vj = VISION / "vision.json"; v = json.loads(vj.read_text())
    v["items"] = {"foundry_lens": {"name": "Foundry Lens", "slot": "head", "key": True, "rarity": "rare",
                                   "texture": "wastelandvision:item/occult_foundry/foundry_lens"}}
    vj.write_text(json.dumps(v, indent=2, ensure_ascii=False) + "\n")
    lens_png(VISION / "assets/wastelandvision/textures/item/occult_foundry/foundry_lens.png")

    RULE.parent.mkdir(parents=True, exist_ok=True)
    RULE.write_text(json.dumps({
        "_comment": "pass 9-46: while a player is locked in the Occult Foundry (Hollowed, not yet escaped), those who stayed follow them",
        "conditions": {"mobs": "incision:skeletoncultist", "dimensions": "minecraft:overworld", "light": {"max": 7}},
        "spawner": {"mob": "incision:skeletoncultist", "interval": 400, "attempts": 3, "chance": 0.6,
                    "distance": {"min": 20, "max": 48}, "group": [1, 2], "max_nearby": {"count": 6, "radius": 48},
                    "players": {"has_tags": ["wv_occult_foundry", "gh_hollow_defeated"], "lacks_tags": ["gh_escaped"]}},
        "name": "Foundry Revenant"}, indent=2) + "\n")

    dp = TREE / "definitions.json"; d = json.loads(dp.read_text())
    h = d["x_hollowed"]
    perks = [r for r in h["rewards"] if r["type"] == "kskills_perks:perk"]
    if perks:
        h["rewards"] = [r for r in h["rewards"] if r["type"] != "kskills_perks:perk"]
        h["description"] = [x for x in h["description"] if not (isinstance(x, dict) and "Soul Siphon" in x.get("text", ""))]
        h["description"].insert(1, {"text": "✦ In the Foundry: Soul Siphon, Arcane Ward and Hex (see Hollow Sight)\n", "color": "light_purple"})
    d["x_hollow_sight"] = {
        "title": {"text": "Hollow Sight", "color": "dark_purple", "bold": True},
        "description": ["", {"text": "✦ Soul Siphon, Arcane Ward and Hex, wherever your path ran\n", "color": "light_purple"},
                        {"text": "Only while you see the Occult Foundry", "color": "gray"}],
        "icon": {"type": "item", "data": {"item": "minecraft:ender_eye"}},
        "frame": {"type": "advancement", "data": {"frame": "challenge"}},
        "size": 1.25, "cost": 0,
        "rewards": [{"type": "kskills_perks:perk", "data": {"perk": p, "level": 1}} for p in ("soul_siphon", "arcane_ward", "hex")],
        "extra_description": ["", {"text": "The Foundry lends you what it took from them.\n", "color": "dark_gray", "italic": True},
                              {"text": "Capstone • Opens and closes with the vision", "color": "dark_aqua"}],
        "required_mods": ["kskills_perks", "neovitae", "caverns_and_chasms", "lodestone"]}
    dp.write_text(json.dumps(d, indent="\t", ensure_ascii=False) + "\n")
    sp = TREE / "skills.json"; s = json.loads(sp.read_text())
    s["hollow_sight_1"] = {"x": -800, "y": 296, "definition": "x_hollow_sight"}
    sp.write_text(json.dumps(s, indent="\t", ensure_ascii=False) + "\n")
    print("9-46: vision configs, Foundry Lens, foundry_haunting spawner, Hollow Sight node")

if __name__ == "__main__":
    main()
