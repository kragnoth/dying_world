#!/usr/bin/env python3
"""gen_pass3c5.py - pass 3c-5: (1) re-add village exclusion zones against dying_world:survivor_villages (original chunk counts),
(2) register road signs as dying_world:road_signs pointing at survivor villages. Safe to re-run.
Run after gen_pass3b/3b2/3c4 (it edits their set files in place)."""
import json, re, sys, zipfile, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import biome_tags as bt
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "datapack/data"
WG = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip")
def rj(n): return json.loads(re.sub(r"\r", "", WG.read(n).decode("utf-8")))
def w(p, o): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o, indent=2) + "\n")
SETS = OUT / "dying_world/worldgen/structure_set"
SURV = "dying_world:survivor_villages"

# (1) exclusion zones, counts = originals (see roster / reference structure_set files)
EXCL = {"abandoned_cabin": 4, "abandoned_hamlets": 6, "abandoned_ruins": 3, "abandoned_villages": 8, "burnt_homestead": 6, "burnt_manor": 6,
        "burnt_watchtower": 6, "collapsed_minehead": 6, "ruined_chapel": 6, "wells": 3}
for name, n in EXCL.items():
    f = SETS / f"{name}.json"; d = json.loads(f.read_text())
    d["placement"]["exclusion_zone"] = {"other_set": SURV, "chunk_count": n}; w(f, d)
    print(f"exclusion: {name} keeps {n} chunks away from survivor villages")

# (2) road signs
s = rj("data/supplementaries/worldgen/structure/road_sign.json")
s["biomes"] = "#dying_world:has_structure/road_sign"
w(OUT / "dying_world/worldgen/structure/road_sign.json", s)
R = bt.resolve
skip = R("minecraft:is_ocean") | R("minecraft:is_deep_ocean") | R("c:is_shallow_ocean") | R("minecraft:is_river") | R("minecraft:is_nether") | R("minecraft:is_end") | \
       R("c:is_cave") | R("c:caves") | R("c:is_mushroom") | {b for b in bt.ALL_BIOMES if any(k in b for k in ("cave", "deeps", "dripstone", "deep_dark", "void", "marker"))}
land = [b for b in bt.ALL_BIOMES if b not in skip]
w(OUT / "dying_world/tags/worldgen/biome/has_structure/road_sign.json", {"replace": False, "values": [{"id": b, "required": False} for b in land]})
w(SETS / "road_signs.json", {"structures": [{"structure": "dying_world:road_sign", "weight": 1}],
   "placement": {"type": "minecraft:random_spread", "spacing": 32, "separation": 10, "salt": zlib.crc32(b"dying_world:road_signs") % 2000000000,
                 "exclusion_zone": {"other_set": SURV, "chunk_count": 6}}})
# destinations: replace supplementaries' tag (originally #minecraft:village + mod structures) with our survivor villages
w(OUT / "supplementaries/tags/worldgen/structure/road_sign_destinations.json",
  {"replace": True, "values": [f"dying_world:village_{b}" for b in ("plains", "taiga", "desert", "savanna", "snowy")]})
print(f"road_signs: 32/10, {len(land)} land biomes, destinations = 5 survivor village structures")
