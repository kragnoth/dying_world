#!/usr/bin/env python3
"""
gen_pass9_21.py - pass 9-21: RARE HOUSE STYLES for the 5 village families (user: variants that add flavor when rarely spawned). Run after the family generators
(7_1 savanna, 9_1 plains, 9_4 taiga, 9_5 snowy/desert) and BEFORE 9_20 (dig spots stamp the new ruined houses too) and 9_19/9_22 (strongholds). Safe to re-run.
Every family gets 2 rare sub-styles (new gradient ramps; same builders/roster as the family, so every house type can appear in them):
  plains : brick (stone base -> bricks, stone-brick roof)              | mossy (mossy cobble/stone bricks, mossy-cobble roof)
  taiga  : darklodge (cobble -> dark oak planks -> vertical dark oak logs) | stave (mossy cobble -> spruce, spruce-log trim)
  snowy  : icehouse (packed/blue ice base, stone bricks -> spruce)     | deepslate (cobbled deepslate -> spruce, deepslate-tile roof)
  desert : redpueblo (red sandstone ramp)                              | bandadobe (mud bricks -> terracotta bands)
  savanna: redmud (mud bricks -> packed mud -> red terracotta, brick roof) | stonehacienda (cobble -> andesite, brick roof)
Weights: village houses pool x4 for the existing entries, each rare house = its roster weight (lived + ruined) -> ~9% of houses are rare;
ruined_houses (abandoned) x10 existing, rare = max(1, w//2) -> ~10%. Re-run safe: removes earlier rare entries/files first.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import savanna_kit as SK
from savanna_kit import B, RAMPS
import gen_pass7_1 as S
import gen_pass9_4 as T          # (module import sets taiga globals; reset below)
import gen_pass9_1 as P
from gen_pass4_2a import w, OUT

RAMPS.update({
    "r_brick": {"wall": ["cobblestone", "stone_bricks", "bricks", "bricks"], "base": ["cobblestone", "stone_bricks", "stone_bricks"], "floor": ["spruce_planks", "oak_planks", "oak_planks"],
                "trim": ["stripped_dark_oak_log"], "beam": ["dark_oak_log"], "roof": "stone_brick", "ridge": "stone_brick", "inner": ["bricks"], "ceil": "oak"},
    "r_mossy": {"wall": ["mossy_cobblestone", "mossy_cobblestone", "mossy_stone_bricks", "stone_bricks"], "base": ["mossy_cobblestone", "cobblestone", "mossy_cobblestone"],
                "floor": ["spruce_planks", "oak_planks", "oak_planks"], "trim": ["stripped_oak_log"], "beam": ["oak_log"], "roof": "mossy_cobblestone", "ridge": "mossy_stone_brick",
                "inner": ["stone_bricks"], "ceil": "oak"},
    "r_darklodge": {"wall": ["cobblestone", "dark_oak_planks", "dark_oak_log", "dark_oak_log"], "base": ["cobblestone", "cobblestone", "mossy_cobblestone"],
                    "floor": ["dark_oak_planks", "spruce_planks", "spruce_planks"], "trim": ["stripped_dark_oak_log"], "beam": ["dark_oak_log"], "roof": "dark_oak", "ridge": "dark_oak",
                    "inner": ["dark_oak_planks"], "ceil": "dark_oak"},
    "r_stave": {"wall": ["mossy_cobblestone", "mossy_cobblestone", "spruce_planks", "stripped_spruce_wood"], "base": ["mossy_cobblestone", "cobblestone", "mossy_cobblestone"],
                "floor": ["spruce_planks", "spruce_planks", "dark_oak_planks"], "trim": ["spruce_log"], "beam": ["spruce_log"], "roof": "spruce", "ridge": "spruce",
                "inner": ["spruce_planks"], "ceil": "spruce"},
    "r_icehouse": {"wall": ["packed_ice", "stone_bricks", "spruce_planks", "stripped_spruce_wood"], "base": ["packed_ice", "blue_ice", "packed_ice"],
                   "floor": ["spruce_planks", "spruce_planks", "birch_planks"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "spruce", "ridge": "spruce",
                   "inner": ["stone_bricks"], "ceil": "spruce"},
    "r_deepslate": {"wall": ["cobbled_deepslate", "deepslate_bricks", "spruce_planks", "stripped_spruce_wood"], "base": ["cobbled_deepslate", "cobbled_deepslate", "deepslate_bricks"],
                    "floor": ["spruce_planks", "dark_oak_planks", "spruce_planks"], "trim": ["stripped_dark_oak_log"], "beam": ["dark_oak_log"], "roof": "deepslate_tile", "ridge": "deepslate_tile",
                    "inner": ["deepslate_bricks"], "ceil": "spruce"},
    "r_redpueblo": {"wall": ["red_sandstone", "cut_red_sandstone", "smooth_red_sandstone", "smooth_red_sandstone"], "base": ["red_sandstone", "red_sandstone", "cut_red_sandstone"],
                    "floor": ["terracotta", "smooth_red_sandstone", "smooth_red_sandstone"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "smooth_red_sandstone",
                    "ridge": "smooth_red_sandstone", "inner": ["smooth_red_sandstone"], "ceil": "spruce"},
    "r_bandadobe": {"wall": ["mud_bricks", "packed_mud", "orange_terracotta", "terracotta"], "base": ["sandstone", "cut_sandstone", "mud_bricks"],
                    "floor": ["terracotta", "smooth_sandstone", "smooth_sandstone"], "trim": ["brown_terracotta"], "beam": ["spruce_log"], "roof": "smooth_sandstone",
                    "ridge": "smooth_sandstone", "inner": ["orange_terracotta"], "ceil": "spruce"},
    "r_redmud": {"wall": ["mud_bricks", "packed_mud", "terracotta", "red_terracotta"], "base": ["cobblestone", "mud_bricks", "mud_bricks"], "floor": ["brown_terracotta", "terracotta", "packed_mud"],
                 "trim": ["stripped_acacia_log"], "beam": ["acacia_log"], "roof": "brick", "ridge": "red_sandstone", "inner": ["packed_mud"], "ceil": "acacia"},
    "r_stonehacienda": {"wall": ["cobblestone", "stone_bricks", "andesite", "polished_andesite"], "base": ["cobblestone", "cobblestone", "stone_bricks"],
                        "floor": ["spruce_planks", "acacia_planks", "acacia_planks"], "trim": ["stripped_acacia_log"], "beam": ["acacia_log"], "roof": "brick", "ridge": "brick",
                        "inner": ["polished_andesite"], "ceil": "acacia"}})

FAM = {
    "plains": dict(wood="oak", steep=False, flat=False, ground=("dirt_path", "coarse_dirt", "grass_block", "coarse_dirt"), prefix="plains_", rare=("r_brick", "r_mossy"),
                   roster=P.ROSTER),
    "taiga": dict(wood="spruce", steep=True, flat=False, ground=("podzol", "coarse_dirt", "dirt_path", "grass_block"), prefix="taiga_", rare=("r_darklodge", "r_stave"),
                  roster=T.ROSTER),
    "snowy": dict(wood="spruce", steep=True, flat=False, ground=("snow_block", "coarse_dirt", "dirt_path", "snow_block"), prefix="snowy_", rare=("r_icehouse", "r_deepslate"),
                  roster=[(S.creole_cottage, 6), (S.dogtrot, 3), (S.limestone_cottage, 6), (S.casita, 2), (S.planter_house, 1), (T.longhouse, 2), (T.sawmill, 2),
                          (S.smokehouse, 2), (S.forge, 2), (S.schoolhouse, 2), (S.chapel, 1), (S.kitchen_garden, 1), (P.barn, 1)]),
    "desert": dict(wood="spruce", steep=False, flat=True, ground=("sand", "smooth_sandstone", "coarse_dirt", "sand"), prefix="desert_", rare=("r_redpueblo", "r_bandadobe"),
                   roster=[(S.creole_cottage, 5), (S.limestone_cottage, 5), (S.courtyard_house, 3), (S.casita, 3), (S.planter_house, 1),
                           (S.smokehouse, 2), (S.forge, 2), (S.schoolhouse, 2), (S.chapel, 1), (S.kitchen_garden, 2)]),
    "savanna": dict(wood="acacia", steep=False, flat=False, ground=("dirt_path", "coarse_dirt", "grass_block", "coarse_dirt"), prefix="", rare=("r_redmud", "r_stonehacienda"),
                    roster=S.ROSTER),
}
def el(loc, wt): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}

def main():
    out = []
    for fam, c in FAM.items():
        N = OUT / f"structure/{fam}"
        is_rare = lambda n: any(f"{st}_" in n for st in c["rare"])
        for old in N.glob("*.nbt"):
            if is_rare(old.name): old.unlink()
        hp = OUT.parent / f"minecraft/worldgen/template_pool/village/{fam}/houses.json"; hj = json.loads(hp.read_text())
        rp = OUT / f"worldgen/template_pool/{fam}/ruined_houses.json"; rj = json.loads(rp.read_text())
        base_h = [e for e in hj["elements"] if not is_rare(e["element"]["location"])]
        base_r = [e for e in rj["elements"] if not is_rare(e["element"]["location"])]
        # weight scaling is idempotent: remember the original weights in a side file
        meta = OUT.parent.parent.parent / f"tools/state/rare_meta_{fam}.json"; meta.parent.mkdir(exist_ok=True)   # NOT inside the datapack
        orig = json.loads(meta.read_text()) if meta.exists() else {"h": {e["element"]["location"]: e["weight"] for e in base_h}, "r": {e["element"]["location"]: e["weight"] for e in base_r}}
        meta.write_text(json.dumps(orig))
        for e in base_h: e["weight"] = orig["h"].get(e["element"]["location"], e["weight"]) * 4
        for e in base_r: e["weight"] = orig["r"].get(e["element"]["location"], e["weight"]) * 10
        rare_h, rare_r = [], []
        for style in c["rare"]:
            S.WOOD, S.STYLE_MAP, S.PREFIX, S.FAMILY = c["wood"], {"creole": style, "limestone": style, "hacienda": style}, f"{c['prefix']}{style}_", fam
            B.STEEP, B.FLAT, B.GROUND = c["steep"], c["flat"], c["ground"]
            for fn, wt in c["roster"]:
                for v in ("lived", "ruined"):
                    b = fn(1); t = b.finalize(v); (N / f"{b.name}_{v}.nbt").write_bytes(t.bytes())
                    rare_h.append(el(f"dying_world:{fam}/{b.name}_{v}", wt))
                    if v == "ruined": rare_r.append(el(f"dying_world:{fam}/{b.name}_{v}", max(1, wt // 2)))
        B.STEEP = B.FLAT = False; B.GROUND = ("dirt_path", "coarse_dirt", "grass_block", "coarse_dirt")
        hj["elements"] = base_h + rare_h; rj["elements"] = base_r + rare_r; w(hp, hj); w(rp, rj)
        sh = sum(e["weight"] for e in rare_h) / sum(e["weight"] for e in hj["elements"]); sr = sum(e["weight"] for e in rare_r) / sum(e["weight"] for e in rj["elements"])
        out.append(f"{fam}: {len(rare_h)} rare ({sh:.0%} of village houses, {sr:.0%} of ruins)")
    print("9-21:", "; ".join(out))

if __name__ == "__main__":
    main()
