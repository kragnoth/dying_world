#!/usr/bin/env python3
"""
gen_pass9_6.py - pass 9-6: ABANDONED ruins/hamlets/villages rebuilt from OUR ruined houses + overgrown versions of OUR streets
(plains, taiga, snowy, desert, savanna). Swamp stays the gearwrights stilt set (user liked it, 7-0d2). Run after 9_5 (and after 7_2); then 8_9, build.
- streets: gen_pass9_3 generator with ABANDONED=True and a worn palette per family (more verge/coarse ground, mossy/gravel centre, unlit post stubs,
  no decor jigsaws); pools dying_world:<fam>/abandoned/{streets,town_centers}; start piece = overgrown crossroads 'plaza' with a dry trough.
- structures: abandoned_ruin_<fam> -> single ruined house (dying_world:<fam>/ruined_houses); abandoned_hamlet_<fam> (size 4) / abandoned_village_<fam> (size 6)
  -> dying_world:<fam>/abandoned/town_centers; radius 80; beard_box. Biome tags, spawn_overrides and sets unchanged.
- savanna: the 7-2 vanilla-street copies (structure/savanna/abandoned) are deleted and replaced by the same scheme.
=> gearwrights abandoned plains/taiga/snowy/desert/savanna pieces become unused (-> archive); only swamp + landmarks still use gearwrights.
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_pass9_3 as ST
from gen_pass4_2a import w, OUT

WORN = {
    "plains": {"verge": ["grass_block", "coarse_dirt"], "edge": ["coarse_dirt", "grass_block", "gravel"], "inner": ["coarse_dirt", "dirt_path"],
               "centre": ["mossy_cobblestone", "gravel", "cobblestone", "coarse_dirt"], "fence": "oak_fence", "hedge": "oak_leaves",
               "flowers": ["short_grass", "tall_grass", "poppy", "short_grass"], "props": [("hay_block", {"axis": "y"}), ("mossy_cobblestone", {})]},
    "taiga": {"verge": ["podzol", "coarse_dirt"], "edge": ["coarse_dirt", "podzol", "gravel"], "inner": ["coarse_dirt", "dirt_path"],
              "centre": ["mossy_cobblestone", "gravel", "cobblestone", "rooted_dirt"], "fence": "spruce_fence", "hedge": "spruce_leaves",
              "flowers": ["fern", "large_fern", "sweet_berry_bush", "fern"], "props": [("spruce_log", {"axis": "z"}), ("mossy_cobblestone", {})]},
    "snowy": {"verge": ["snow_block", "coarse_dirt"], "edge": ["snow_block", "gravel", "coarse_dirt"], "inner": ["gravel", "dirt_path"],
              "centre": ["gravel", "mossy_cobblestone", "cobblestone", "snow_block"], "fence": "spruce_fence", "hedge": "spruce_leaves",
              "flowers": ["fern", "fern", "sweet_berry_bush", "fern"], "props": [("spruce_log", {"axis": "x"}), ("packed_ice", {})]},
    "desert": {"verge": ["sand", "sand"], "edge": ["sand", "sandstone", "coarse_dirt"], "inner": ["sand", "smooth_sandstone"],
               "centre": ["sandstone", "sand", "cut_sandstone", "coarse_dirt"], "fence": "sandstone_wall", "hedge": None,
               "flowers": ["dead_bush", "dead_bush", "dead_bush", "short_grass"], "props": [("sandstone", {}), ("decorated_pot", {"facing": "north", "cracked": "true", "waterlogged": "false"})]},
    "savanna": {"verge": ["grass_block", "coarse_dirt"], "edge": ["coarse_dirt", "grass_block", "packed_mud"], "inner": ["coarse_dirt", "packed_mud"],
                "centre": ["packed_mud", "mossy_cobblestone", "coarse_dirt", "mud_bricks"], "fence": "acacia_fence", "hedge": "acacia_leaves",
                "flowers": ["short_grass", "dead_bush", "tall_grass", "short_grass"], "props": [("hay_block", {"axis": "y"}), ("decorated_pot", {"facing": "north", "cracked": "true", "waterlogged": "false"})]},
}

def main():
    old = OUT / "structure/savanna/abandoned"
    if old.exists(): shutil.rmtree(old)
    for p in (OUT / "worldgen/template_pool/savanna/abandoned").glob("*.json"): p.unlink()
    ST.ABANDONED = True; out = []
    for fam, pal in WORN.items():
        ST.FAMILY, ST.PAL = fam, pal
        n = ST.write_streets()
        for kind, size, pool in (("ruin", 1, f"dying_world:{fam}/ruined_houses"), ("hamlet", 4, f"dying_world:{fam}/abandoned/town_centers"),
                                 ("village", 6, f"dying_world:{fam}/abandoned/town_centers")):
            p = OUT / f"worldgen/structure/abandoned_{kind}_{fam}.json"; j = json.loads(p.read_text())
            j.update({"start_pool": pool, "size": size, "max_distance_from_center": 80, "terrain_adaptation": "beard_box"}); j.pop("start_jigsaw_name", None)
            w(p, j)
        out.append(f"{fam}: {n} worn streets + plaza")
    ST.ABANDONED = False
    print("9-6:", "; ".join(out))

if __name__ == "__main__":
    main()
