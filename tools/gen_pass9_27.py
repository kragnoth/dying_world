#!/usr/bin/env python3
"""
gen_pass9_27.py - pass 9-27: the user's Create mills RE-SKINNED in our gradient style (user screenshot: abandoned windmill = random checkerboard mix +
cobwebs all over the outside; 'redo the ruin phase, rebuild to match our tone'). Run after 9_25 (modifiers/placement) and before 9_26 + 8_9. Safe to re-run.
Keeps the user's exact geometry + Create machinery (windmill bearing, sails, frames, shafts, gearbox, millstone; desert water wheel). Every building block is
converted to a savanna_kit ROLE and finished by the same engine as our village houses:
  stone/plank full blocks -> 'wall' (one band over the whole height: rough stone at the foot -> planks up the tower = smooth gradient, no checkerboard),
  plank/stone with open air above at floor level -> 'floor', logs -> 'trim' (axis kept), wooden stairs -> 'roof' (facing/half/shape kept), wooden slabs ->
  'roof_slab'; ground, glass, doors, trapdoors, fences, crops, containers, ladders, stone stairs and all create:* blocks stay as built.
  Per-family mill ramps (no white): plains cobble->stone bricks->spruce->oak, dark oak roof | taiga cobble->mossy->spruce->stripped spruce |
  snowy cobble->stone bricks->spruce | savanna cobble->packed mud->acacia, acacia roof | desert sandstone->cut->smooth sandstone, sandstone roof.
LIVED = finalize('lived'). ABANDONED = finalize('ruined') from the SAME lived source (our ruin rule: worn/mossy/cracked, nothing missing, a few INTERIOR cobwebs,
  beds/jobs/pots decayed) + 60% of the sails torn away (glue entity removed) + dark (9_26 runs after). The old abandoned NBTs (checkerboard) are no longer used.
"""
import random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from savanna_kit import B, RAMPS
from gen_pass4_2a import M

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "reference_custom"; DST = ROOT / "datapack/data/gearwrights/structure/village"
MILLS = {"plains": "windmill", "taiga": "windmill", "snowy": "windmill", "savanna": "windmill", "desert": "watermill"}
RAMPS.update({
    "mill_plains": {"wall": ["cobblestone", "stone_bricks", "spruce_planks", "oak_planks"], "base": ["cobblestone", "mossy_cobblestone", "stone_bricks"],
                    "floor": ["spruce_planks", "oak_planks", "oak_planks"], "trim": ["oak_log"], "beam": ["oak_log"], "roof": "dark_oak", "ridge": "dark_oak", "inner": ["oak_planks"], "ceil": "oak"},
    "mill_taiga": {"wall": ["cobblestone", "mossy_cobblestone", "spruce_planks", "stripped_spruce_wood"], "base": ["cobblestone", "mossy_cobblestone", "cobblestone"],
                   "floor": ["spruce_planks", "dark_oak_planks", "spruce_planks"], "trim": ["spruce_log"], "beam": ["spruce_log"], "roof": "dark_oak", "ridge": "dark_oak", "inner": ["spruce_planks"], "ceil": "spruce"},
    "mill_snowy": {"wall": ["cobblestone", "stone_bricks", "spruce_planks", "stripped_spruce_wood"], "base": ["cobblestone", "stone_bricks", "cobblestone"],
                   "floor": ["spruce_planks", "spruce_planks", "dark_oak_planks"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "spruce", "ridge": "spruce", "inner": ["spruce_planks"], "ceil": "spruce"},
    "mill_savanna": {"wall": ["cobblestone", "packed_mud", "acacia_planks", "stripped_acacia_wood"], "base": ["cobblestone", "packed_mud", "mud_bricks"],
                     "floor": ["acacia_planks", "spruce_planks", "acacia_planks"], "trim": ["acacia_log"], "beam": ["acacia_log"], "roof": "acacia", "ridge": "acacia", "inner": ["acacia_planks"], "ceil": "acacia"},
    "mill_desert": {"wall": ["sandstone", "cut_sandstone", "smooth_sandstone", "smooth_sandstone"], "base": ["sandstone", "cut_sandstone", "sandstone"],
                    "floor": ["spruce_planks", "smooth_sandstone", "spruce_planks"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "smooth_sandstone",
                    "ridge": "cut_sandstone", "inner": ["smooth_sandstone"], "ceil": "spruce"}})
STONE = ("cobblestone", "stone_bricks", "andesite", "sandstone", "terracotta", "packed_mud", "mud_bricks", "diorite", "deepslate", "stone")
WOODS = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove")
GROUND = ("grass_block", "dirt", "coarse_dirt", "podzol", "farmland", "sand", "snow_block", "dirt_path", "gravel", "rooted_dirt")

def is_wood(k): return any(k.startswith(w + "_") or k.startswith("stripped_" + w + "_") for w in WOODS)
def convert(fam, s, seed):
    sx, sy, sz = s.size; b = B(f"mill_{fam}", f"mill_{fam}", sx, sy, sz, seed); b.t.b.clear()
    solid = lambda p: s.b.get(p, ("minecraft:air",))[0] not in ("minecraft:air", "minecraft:cave_air")
    top = max((y for (x, y, z), v in s.b.items() if v[0] not in ("minecraft:air",) and not v[0].startswith("create:")), default=sy - 1)
    for (x, y, z), (n, pr, nb) in s.b.items():
        ns, k = n.split(":")
        if fam == "desert" and "jungle" in k: n = n.replace("jungle", "spruce"); k = k.replace("jungle", "spruce")
        props = dict(pr)
        if isinstance(nb, tuple): nb = nb[1]          # nbtrw typed compound -> nbtw dict of typed values
        if ns != "minecraft" or nb or y == 0 and any(g in k for g in GROUND):
            b.t.b[(x, y, z)] = (n, tuple(sorted(props.items())), nb); continue
        full = not any(t in k for t in ("stairs", "slab", "fence", "pane", "door", "trapdoor", "wall", "ladder", "lantern", "chain", "carpet", "sign", "button", "plate", "torch", "leaves"))
        if k.endswith(("_log", "_wood")) and not k.endswith("planks") and ("log" in k or "wood" in k) and "stripped" not in k:
            b.role(x, y, z, "trim", {"axis": props.get("axis", "y")}); continue
        if full and (any(st in k for st in STONE) or k.endswith("_planks") or k.startswith("stripped_")):
            if y == 0: b.role(x, y, z, "floor")
            elif not solid((x, y + 1, z)) and solid((x - 1, y, z)) + solid((x + 1, y, z)) + solid((x, y, z - 1)) + solid((x, y, z + 1)) >= 3 and y < top - 2:
                b.role(x, y, z, "floor")
            else: b.role(x, y, z, "wall", band=(1, max(4, int(top * .7))))   # tower reaches the timber end of the ramp before the eaves
            continue
        if k.endswith("_stairs") and is_wood(k): b.role(x, y, z, "roof", {kk: props[kk] for kk in ("facing", "half", "shape") if kk in props}); continue
        if k.endswith("_slab") and is_wood(k): b.role(x, y, z, "roof_slab", {"type": props.get("type", "bottom")}); continue
        b.t.b[(x, y, z)] = (n, tuple(sorted(props.items())), nb)
    return b

def main():
    out = []
    for fam, mill in MILLS.items():
        src = nbtrw.Struct((SRC / f"{fam}__{mill}.nbt").read_bytes())
        for variant, suf in (("lived", ""), ("ruined", "_abandoned")):
            b = convert(fam, src, 3); t = b.finalize(variant)
            if variant == "ruined":
                r = random.Random(zlib.crc32(fam.encode()))
                for p, (n, pr, nb) in list(t.b.items()):
                    if n.endswith("_sail") and r.random() < .6: t.b[p] = (M("air"), (), None)
                t.ents = []
            else:
                t.ents = list(src.ents)
            (DST / fam / f"{mill}{suf}.nbt").write_bytes(t.bytes())
        out.append(f"{fam} {mill}")
    print("9-27: re-skinned (lived + ruined):", ", ".join(out))

if __name__ == "__main__":
    main()
