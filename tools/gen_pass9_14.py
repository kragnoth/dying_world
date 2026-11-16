#!/usr/bin/env python3
"""
gen_pass9_14.py - pass 9-14: SCAVENGER STRONGHOLD streets fixed (user: 'scavenger fortress no longer spawns with buildings'). Run after 5_1/5_2 (and 9_3). Safe to re-run.
Cause: since 8-11 the stronghold house copies come only from the big plains donor houses (13-19 deep), but the stronghold still used copies of the vanilla
16x16 zombie streets, whose building-entrance jigsaws sit INSIDE the street box -> a house must fit in the leftover box space -> nothing fits, no houses.
Fix (same as the 9-3 village fix): own NARROW streets from the 9-3 generator (7 wide, entrances on the verge facing out -> houses use global free space),
worn scavenger palette, pools retargeted to the stronghold (streets/houses/decor), fallback = the barricade dead ends. Old vanilla street copies deleted.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_pass9_3 as G
from gen_pass4_2a import M, R, w, OUT

SH = "dying_world:scavenger_stronghold"
G.FAMILY = "scavenger_stronghold"
G.PAL = {"verge": ["coarse_dirt", "gravel"], "edge": ["gravel", "coarse_dirt", "dirt_path"], "inner": ["dirt_path", "cobblestone"],
         "centre": ["cobblestone", "mossy_cobblestone", "gravel", "dirt_path"], "fence": "spruce_fence", "hedge": None,
         "flowers": ["dead_bush", "short_grass", "fern"], "props": [("barrel", {"facing": "up", "open": "false"}), ("hay_block", {"axis": "y"}),
                                                                    ("cobblestone_wall", {"up": "true", "north": "none", "south": "none", "east": "none", "west": "none", "waterlogged": "false"})]}
G.street_j = lambda t, x, z, ori: G.jig(t, x, 1, z, ori, "minecraft:street", f"{SH}/streets")
G.plot_j = lambda t, x, z, ori: G.jig(t, x, 1, z, ori, "minecraft:building_entrance", f"{SH}/houses")
G.decor_j = lambda t, x, z: G.jig(t, x, 0, z, "up_north", "minecraft:bottom", f"{SH}/decor", M("coarse_dirt"), "rollable")
_props = G.verge_props
def verge_props(t, r, x, z, n):                     # scavenger junk on the verges: crates / drums / barbed wire between plots
    if n < -.4 and r.random() < .5:
        t.set(x, 1, z, r.choice([R("rusted_steel_crate"), R("weathered_wooden_crate"), R("rusted_drum"), R("barbed_wire")]))
    else: _props(t, r, x, z, n)
G.verge_props = verge_props

def main():
    N = OUT / "structure/scavenger_stronghold/streets"
    for old in N.glob("*.nbt"): old.unlink()
    N.mkdir(parents=True, exist_ok=True); els = []
    pieces = [("straight16_1", G.straight(16, 1), 5), ("straight16_2", G.straight(16, 2), 5), ("straight10_1", G.straight(10, 3), 3),
              ("cross_1", G.junction("cross", 1), 2), ("tee_1", G.junction("tee", 1), 3), ("tee_2", G.junction("tee", 2), 2),
              ("corner_1", G.junction("corner", 1), 3), ("end_1", G.junction("end", 1), 1)]
    for name, t, wt in pieces:
        (N / f"{name}.nbt").write_bytes(t.bytes())
        els.append({"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": f"{SH}/streets/{name}",
                    "processors": "minecraft:empty", "projection": "terrain_matching"}})
    w(OUT / "worldgen/template_pool/scavenger_stronghold/streets.json", {"fallback": f"{SH}/barricades", "elements": els})
    print(f"9-14: scavenger stronghold -> {len(els)} narrow streets (houses outside the street box)")

if __name__ == "__main__":
    main()
