#!/usr/bin/env python3
"""gen_pass9_92.py - pass 9-92: gentler terrain + villages kept off steep biomes. Run after 9_91; safe to re-run.

1. Terrain. The old terrain-overhaul fragments in kubejs_base (factor/offset/jaggedness/erosion splines, rescaled noises)
   are deleted by this pass's commit; the overworld is vanilla 1.21.1 again, then softened by wrapping vanilla's own
   density functions (copies in tools/state/vanilla_1_21_1, Mojang's 1.21.1 data):
     offset     : height above sea level x HEIGHT (below sea level untouched, so oceans keep their depth)
     factor     : x FACTOR (3D noise matters less: fewer cliffs and overhangs)
     jaggedness : x JAGGED (peak spikes)
   Vanilla structure kept (flat_cache > cache_2d > ...) so old-chunk blending still works.
2. Villages. The flattest-looking biomes stay; steep / mountain-side biomes are dropped from the village, abandoned
   village and hamlet biome tags (and the minecraft:has_structure/village_* tags they include).
"""
import glob, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
VAN = ROOT / "tools/state/vanilla_1_21_1"
OUT = ROOT / "datapack/data/minecraft/worldgen/density_function/overworld"
HEIGHT, FACTOR, JAGGED = 0.70, 1.30, 0.35
SEA = 0.5037500262260437          # vanilla offset's constant: offset = -SEA is sea level (y ~ 63)

HILLY = {"minecraft:meadow", "minecraft:cherry_grove", "minecraft:grove", "minecraft:windswept_forest",
         "minecraft:savanna_plateau", "minecraft:windswept_savanna", "minecraft:eroded_badlands", "minecraft:wooded_badlands",
         "minecraft:snowy_slopes", "regions_unexplored:mauve_hills", "regions_unexplored:rocky_meadow",
         "regions_unexplored:highland_fields", "regions_unexplored:windswept_maple_forest", "regions_unexplored:pine_slopes",
         "regions_unexplored:spires", "environmental:pine_slopes", "atmospheric:rocky_dunes"}


def inner(name):                   # the part inside flat_cache > cache_2d
    j = json.loads((VAN / f"{name}.json").read_text())
    assert j["type"] == "minecraft:flat_cache" and j["argument"]["type"] == "minecraft:cache_2d"
    return j["argument"]["argument"]


def wrap(fn):
    return {"type": "minecraft:flat_cache", "argument": {"type": "minecraft:cache_2d", "argument": fn}}


def mul(a, b): return {"type": "minecraft:mul", "argument1": a, "argument2": b}
def add(a, b): return {"type": "minecraft:add", "argument1": a, "argument2": b}


def terrain():
    x = add(SEA, inner("offset"))                         # height above sea level (in offset units)
    offset = add(-SEA, add(mul(HEIGHT, {"type": "minecraft:max", "argument1": x, "argument2": 0.0}),
                           {"type": "minecraft:min", "argument1": x, "argument2": 0.0}))
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("offset", offset), ("factor", mul(FACTOR, inner("factor"))), ("jaggedness", mul(JAGGED, inner("jaggedness")))):
        (OUT / f"{name}.json").write_text(json.dumps(wrap(fn), separators=(",", ":")))


def tags():
    files = glob.glob(f"{ROOT}/datapack/data/dying_world/tags/worldgen/biome/has_structure/*.json")
    files = [f for f in files if Path(f).stem.startswith(("village_", "abandoned_village_", "abandoned_hamlet_"))]
    files += glob.glob(f"{ROOT}/datapack_imported/data/minecraft/tags/worldgen/biome/has_structure/village_*.json")
    dropped = 0
    for f in files:
        j = json.loads(Path(f).read_text())
        keep = [v for v in j["values"] if (v if isinstance(v, str) else v.get("id")) not in HILLY]
        if len(keep) != len(j["values"]):
            dropped += len(j["values"]) - len(keep); j["values"] = keep
            Path(f).write_text(json.dumps(j, indent=2) + "\n")
    return dropped


if __name__ == "__main__":
    terrain()
    print(f"9-92: terrain wrapped (height x{HEIGHT}, factor x{FACTOR}, jaggedness x{JAGGED}); {tags()} hilly biome entries dropped")
