#!/usr/bin/env python3
"""
gen_pass9_19.py - pass 9-19: SCAVENGER STRONGHOLD HOUSES FROM OUR OWN BUILDINGS (user: make sure the scavenger buildings no longer reference mod/third-party
structures; rebuild from our new sources). Run after 5_1, 5_2, 9_1, 9_6, 9_14. Safe to re-run.
Before: the 44 stronghold houses were plain/fortified copies of the old worn plains houses = the kubejs custom plains house set (third-party since the 8-0 audit),
and the houses pool fell back to the user's kubejs plains terminators.
Now: source = OUR 9-1 plains houses, RUINED variants (worn, floors intact, villager jigsaws stripped; pool dying_world:plains/ruined_houses gives names + weights),
run through gen_pass5_2.build() (floor level forced to y0: our floors are at y0 and intact) (floor repair, immune piglins, FORT layer: corrugated roof patches, boarded windows, rooftop lookout with floodlight +
crossbow piglin, scrap + loot barrel outside). plain 40% / fort 60% of each house's weight. Fallback = minecraft:empty. Old copies deleted.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_pass5_2 as F
from gen_pass4_2a import w, OUT
from gen_pass5_1 import SH

def main():
    F.SRC = OUT / "structure/plains"
    F.FLOORISH = F.FLOORISH + ("wood", "terracotta", "sandstone", "mud", "tile", "deepslate", "andesite", "dirt", "path", "gravel", "brick")
    F.floor_level = lambda s: 0          # our houses have their floor at y0 (5-2's detector skips y0 and would fill the walking layer); ruined floors are intact
    for old in F.DST.glob("*.nbt"): old.unlink()
    F.DST.mkdir(parents=True, exist_ok=True)
    src = json.loads((OUT / "worldgen/template_pool/plains/ruined_houses.json").read_text())["elements"]
    els, rep = [], {}
    for e in src:
        name = e["element"]["location"].rsplit("/", 1)[1]
        for fort, share in ((False, .4), (True, .6)):
            s, n = F.build(name, fort, 1); tag = "fort" if fort else "plain"
            (F.DST / f"{name}_{tag}.nbt").write_bytes(s.bytes()); rep[name] = n
            els.append({"weight": max(1, round(e["weight"] * share)), "element": {"element_type": "minecraft:single_pool_element",
                        "location": f"{SH}/houses/{name}_{tag}", "processors": "minecraft:empty", "projection": "rigid"}})
    w(OUT / "worldgen/template_pool/scavenger_stronghold/houses.json", {"fallback": "minecraft:empty", "elements": els})
    print(f"9-19: {len(els)} stronghold houses from our {len(src)} ruined plains houses (plain + fort); floors repaired {sum(rep.values())}")

if __name__ == "__main__":
    main()
