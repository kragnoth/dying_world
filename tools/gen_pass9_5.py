#!/usr/bin/env python3
"""
gen_pass9_5.py - pass 9-5: OUR SNOWY + DESERT families (houses + streets) and SAVANNA STREETS. Run after 9_4 (same position in the regen order); then 8_9, build.
- snowy: spruce, STEEP roofs, sub-styles chalet (stone brick -> spruce -> stripped spruce, dark-oak roof) / frost (cobble -> stone brick -> polished diorite,
  packed-ice base course, spruce roof) / stonetimber; roster like taiga incl. longhouse + sawmill. Windswept frozen donors + custom snowy houses no longer used.
- desert: spruce trim, FLAT roofs with parapets (B.FLAT), sub-styles adobe (mud brick -> packed mud -> smooth sandstone -> whitewash) / sandstone
  (sandstone -> cut -> smooth, chiseled trim) / hacienda (mission chapel, casita). Pueblo donors + custom desert houses no longer used.
- savanna: houses unchanged (7-1); streets = our generator with a savanna palette (custom savanna streets dropped).
Every family: houses pool lived 40 / ruined 60, streets = 8 narrow gradient pieces, dying_world:<family>/ruined_houses for the abandoned phase.
Also: village_desert + village_savanna -> jigsaw size 6 / radius 80 (like plains/taiga/snowy; our streets are dense now).
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_pass7_1 as S, gen_pass9_1 as P, gen_pass9_3 as ST, gen_pass9_4 as T
from savanna_kit import B
from gen_pass4_2a import w, OUT

GROUNDS = {"snowy": ("snow_block", "coarse_dirt", "dirt_path", "snow_block"), "desert": ("sand", "smooth_sandstone", "coarse_dirt", "sand")}
def build_family(fam, wood, style_map, prefix, steep, flat, roster):
    S.WOOD, S.STYLE_MAP, S.PREFIX, S.FAMILY = wood, style_map, prefix, fam
    B.STEEP, B.FLAT = steep, flat; B.GROUND = GROUNDS.get(fam, B.GROUND)
    N = OUT / f"structure/{fam}"; N.mkdir(parents=True, exist_ok=True)
    els, ruined = [], []
    for fn, wt in roster:
        for v in ("base", "lived", "ruined"):
            b = fn(1); t = b.finalize(v); (N / f"{b.name}_{v}.nbt").write_bytes(t.bytes())
            if v != "base":
                els.append({"weight": wt * (4 if v == "lived" else 6), "element": {"element_type": "minecraft:single_pool_element",
                            "location": f"dying_world:{fam}/{b.name}_{v}", "processors": "minecraft:empty", "projection": "rigid"}})
        ruined.append({"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:{fam}/{b.name}_ruined",
                       "processors": "minecraft:empty", "projection": "rigid"}})
    w(OUT.parent / f"minecraft/worldgen/template_pool/village/{fam}/houses.json", {"fallback": f"minecraft:village/{fam}/terminators", "elements": els})
    w(OUT / f"worldgen/template_pool/{fam}/ruined_houses.json", {"fallback": "minecraft:empty", "elements": ruined})
    old = OUT / f"structure/village/{fam}"
    if old.exists(): shutil.rmtree(old)
    B.STEEP = B.FLAT = False; B.GROUND = ("dirt_path", "coarse_dirt", "grass_block", "coarse_dirt")
    return len(els)

def streets(fam, pal):
    ST.FAMILY, ST.PAL = fam, pal
    return ST.write_streets()

POT = ("decorated_pot", {"facing": "north", "cracked": "false", "waterlogged": "false"})
def main():
    out = []
    # snowy
    n = build_family("snowy", "spruce", {"creole": "chalet", "limestone": "frost", "hacienda": "stonetimber"}, "snowy_", True, False,
                     [(S.creole_cottage, 6), (S.dogtrot, 3), (S.limestone_cottage, 6), (S.casita, 2), (S.planter_house, 1), (T.longhouse, 2), (T.sawmill, 2),
                      (S.smokehouse, 2), (S.forge, 2), (S.schoolhouse, 2), (S.chapel, 1), (S.kitchen_garden, 1), (P.barn, 1)])
    k = streets("snowy", {"verge": ["snow_block", "coarse_dirt"], "edge": ["gravel", "coarse_dirt", "packed_ice"], "inner": ["dirt_path", "cobblestone"],
                          "centre": ["cobblestone", "stone_bricks", "gravel", "dirt_path"], "fence": "spruce_fence", "hedge": "spruce_leaves",
                          "flowers": ["fern", "sweet_berry_bush", "fern", "fern"], "props": [("spruce_log", {"axis": "x"}), ("barrel", {"facing": "up", "open": "false"})]})
    out.append(f"snowy {n} house entries / {k} streets")
    # desert
    n = build_family("desert", "spruce", {"creole": "adobe", "limestone": "sandstone", "hacienda": "hacienda"}, "desert_", False, True,
                     [(S.creole_cottage, 5), (S.limestone_cottage, 5), (S.courtyard_house, 3), (S.casita, 3), (S.planter_house, 1),
                      (S.smokehouse, 2), (S.forge, 2), (S.schoolhouse, 2), (S.chapel, 1), (S.kitchen_garden, 2)])
    k = streets("desert", {"verge": ["sand", "smooth_sandstone"], "edge": ["sandstone", "gravel", "coarse_dirt"], "inner": ["dirt_path", "smooth_sandstone"],
                           "centre": ["smooth_sandstone", "cut_sandstone", "sandstone", "dirt_path"], "fence": "sandstone_wall", "hedge": None,
                           "flowers": ["dead_bush", "dead_bush", "short_grass", "dead_bush"], "props": [POT, ("barrel", {"facing": "up", "open": "false"}), ("hay_block", {"axis": "y"})]})
    out.append(f"desert {n} house entries / {k} streets")
    # savanna streets only
    k = streets("savanna", {"verge": ["grass_block", "coarse_dirt"], "edge": ["coarse_dirt", "packed_mud", "gravel"], "inner": ["dirt_path", "packed_mud"],
                            "centre": ["mud_bricks", "packed_mud", "cobblestone", "dirt_path"], "fence": "acacia_fence", "hedge": "acacia_leaves",
                            "flowers": ["short_grass", "dead_bush", "short_grass", "orange_tulip"], "props": [POT, ("hay_block", {"axis": "y"}), ("barrel", {"facing": "up", "open": "false"})]})
    out.append(f"savanna {k} streets")
    S.WOOD, S.STYLE_MAP, S.PREFIX, S.FAMILY = "acacia", {}, "", "savanna"
    D = OUT / "worldgen/structure"
    for fam in ("desert", "savanna"):
        p = D / f"village_{fam}.json"; j = json.loads(p.read_text()); j["size"], j["max_distance_from_center"] = 6, 80; w(p, j)
    print("9-5:", "; ".join(out), "; desert/savanna villages size 6 / radius 80")

if __name__ == "__main__":
    main()
