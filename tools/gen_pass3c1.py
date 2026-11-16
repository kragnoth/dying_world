#!/usr/bin/env python3
"""gen_pass3c1.py - pass 3c: survivor villages (40% lived-in / 60% worn-down), vanilla-based, per biome.
Usage: gen_pass3c1.py [plains taiga ...]   (default: plains)

Mechanism (per biome B):
 1. OVERRIDE `minecraft:village/B/houses` pool (street NBTs hard-code that pool id). Every house appears twice:
      lived  = original NBT, weight*2, light weathering (minecraft:mossify_10_percent)
      worn   = COPY of the NBT under dying_world:village/B/houses_worn/<name>, weight*3, processor dying_world:village_worn
    -> 2:3 weights = 40% lived / 60% worn.
 2. Worn NBT copies have the villagers jigsaw pool (minecraft:village/B/villagers) changed to minecraft:empty, so NO villager spawns there.
    (Processors cannot do this: jigsaws are expanded before processors run.)
 3. dying_world:village_worn processor list is REPLACE-ONLY (no air): beds -> moss carpet, job blocks -> mossy cobblestone,
    cobble/stone bricks -> mossy/cracked.
 4. dying_world:village_B structure (copy of vanilla, own biome tag starting as the vanilla tag) + shared set dying_world:survivor_villages (40/12).
Per-biome PROFILES: default = 1 lived + 1 worn variant (plains, taiga: output unchanged). desert = 1 lived + 3 worn variants
(weathered / scorched / tarred) sharing the same villager-free NBT copies; weights keep the overall 40/60 split (6 : 4+3+2).
Reads reference/*.zip. Safe to re-run."""
import gzip, json, re, sys, zipfile, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
WG = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip")
NBT = zipfile.ZipFile(ROOT / "reference/structures_nbt.zip")
OUT = ROOT / "datapack/data"
ALL = ["plains", "desert", "savanna", "snowy", "taiga"]
biomes = sys.argv[1:] or ["plains"]
LIVED_W, WORN_W = 2, 3
DEFAULT_PROFILE = {"lived": ("minecraft:mossify_10_percent", 2), "worn": [("dying_world:village_worn", 3)]}
PROFILES = {"desert": {"lived": ("dying_world:desert_lived", 6),
                       "worn": [("dying_world:desert_weathered", 4), ("dying_world:desert_scorched", 3), ("dying_world:desert_tarred", 2)]}}

def rj(name): return json.loads(re.sub(r"\r", "", WG.read(name).decode("utf-8")))
def w(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, indent=2) + "\n")

# ---- worn processor list (replace-only) ----
def rule(inp, out, p=None):
    ip = {"predicate_type": "minecraft:block_match", "block": inp} if p is None else \
         {"predicate_type": "minecraft:random_block_match", "block": inp, "probability": p}
    return {"input_predicate": ip, "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": out}}
colors = "white orange magenta light_blue yellow lime pink gray light_gray cyan purple blue brown green red black".split()
jobs = "composter barrel blast_furnace smoker cartography_table fletching_table grindstone lectern loom smithing_table stonecutter brewing_stand cauldron water_cauldron lava_cauldron powder_snow_cauldron".split()
rules = [rule(f"minecraft:{c}_bed", "minecraft:moss_carpet") for c in colors]
rules += [rule(f"minecraft:{j}", "minecraft:mossy_cobblestone") for j in jobs]
rules += [rule("minecraft:cobblestone", "minecraft:mossy_cobblestone", 0.4),
          rule("minecraft:stone_bricks", "minecraft:mossy_stone_bricks", 0.25),
          rule("minecraft:stone_bricks", "minecraft:cracked_stone_bricks", 0.25)]
w(OUT / "dying_world/worldgen/processor_list/village_worn.json",
  {"processors": [{"processor_type": "minecraft:rule", "rules": rules}]})

# ---- desert processor lists (replace-only; block_match/random_block_match keep Name only -> never used on stairs/slabs/logs) ----
def plist(name, rules): w(OUT / f"dying_world/worldgen/processor_list/{name}.json", {"processors": [{"processor_type": "minecraft:rule", "rules": rules}]})
terra = [f"minecraft:{c}_terracotta" for c in "white orange magenta light_blue yellow lime pink light_gray cyan purple blue brown green red".split()]
crops = [rule(f"minecraft:{c}", "minecraft:dead_bush") for c in ("wheat", "carrots", "potatoes")]
jobs_to = lambda out: [rule(f"minecraft:{j}", out) for j in jobs]
beds_to = lambda out: [rule(f"minecraft:{c}_bed", out) for c in colors]
# lived: only light sun-wear
plist("desert_lived", [rule("minecraft:smooth_sandstone", "minecraft:sandstone", 0.08), rule("minecraft:cut_sandstone", "minecraft:sandstone", 0.08)])
# weathered: sun-bleached, cracked, abandoned look
plist("desert_weathered", beds_to("minecraft:brown_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    rule("minecraft:smooth_sandstone", "minecraft:sandstone", 0.30), rule("minecraft:cut_sandstone", "minecraft:sandstone", 0.30),
    rule("minecraft:bookshelf", "minecraft:cobweb", 0.40), rule("minecraft:grass_block", "minecraft:coarse_dirt", 0.60)] +
    [rule(t, "minecraft:terracotta", 0.55) for t in terra])
# scorched: fire-damaged, soot-black
plist("desert_scorched", beds_to("minecraft:black_carpet") + jobs_to("minecraft:blackstone") + crops + [
    rule("minecraft:smooth_sandstone", "minecraft:black_terracotta", 0.18), rule("minecraft:smooth_sandstone", "minecraft:gray_terracotta", 0.22),
    rule("minecraft:cut_sandstone", "minecraft:black_terracotta", 0.15),
    rule("minecraft:birch_planks", "minecraft:dark_oak_planks", 0.50), rule("minecraft:jungle_planks", "minecraft:dark_oak_planks", 0.50),
    rule("minecraft:hay_block", "minecraft:coal_block", 0.60), rule("minecraft:bookshelf", "minecraft:cobweb", 0.50)] +
    [rule(t, "minecraft:black_terracotta", 0.35) for t in terra])
# tarred: tar/oil seeping in (real tarbound / immersivepetroleum blocks)
plist("desert_tarred", beds_to("minecraft:black_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    rule("minecraft:birch_planks", "tarbound:tar_soaked_planks", 0.50), rule("minecraft:jungle_planks", "tarbound:tar_soaked_planks", 0.50),
    rule("minecraft:sand", "immersivepetroleum:asphalt", 0.12),
    rule("minecraft:smooth_sandstone", "minecraft:sandstone", 0.15), rule("minecraft:bookshelf", "minecraft:cobweb", 0.40)])

def nbt_worn(data, biome):
    old = f"minecraft:village/{biome}/villagers".encode()
    a = len(old).to_bytes(2, "big") + old
    b = len(b"minecraft:empty").to_bytes(2, "big") + b"minecraft:empty"
    return data.replace(a, b), data.count(a)

set_members = []
for B in biomes:
    pool = rj(f"data/minecraft/worldgen/template_pool/village/{B}/houses.json")
    new, removed = [], 0
    for e in pool["elements"]:
        el = e["element"]
        if el["element_type"] != "minecraft:single_pool_element" or el.get("processors") != "minecraft:empty":
            new.append(e); print("  kept unchanged:", el.get("location", el["element_type"])); continue
        name = el["location"].split("/houses/")[-1]
        prof = PROFILES.get(B, DEFAULT_PROFILE)
        new.append({"weight": e["weight"] * prof["lived"][1],
                    "element": {**el, "processors": prof["lived"][0]}})
        raw = gzip.decompress(NBT.read(f"data/minecraft/structure/village/{B}/houses/{name}.nbt"))
        mod, n = nbt_worn(raw, B); removed += n
        dst = OUT / f"dying_world/structure/village/{B}/houses_worn/{name}.nbt"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(gzip.compress(mod, mtime=0))
        for proc, mult in prof["worn"]:
            new.append({"weight": e["weight"] * mult,
                        "element": {**el, "location": f"dying_world:village/{B}/houses_worn/{name}",
                                    "processors": proc}})
    pool["elements"] = new
    w(OUT / f"minecraft/worldgen/template_pool/village/{B}/houses.json", pool)
    s = rj(f"data/minecraft/worldgen/structure/village_{B}.json")
    orig = s["biomes"]; s["biomes"] = f"#dying_world:has_structure/village_{B}"
    w(OUT / f"dying_world/worldgen/structure/village_{B}.json", s)
    w(OUT / f"dying_world/tags/worldgen/biome/has_structure/village_{B}.json", {"replace": False, "values": [orig]})
    set_members.append({"structure": f"dying_world:village_{B}", "weight": 1})
    print(f"{B}: {len(pool['elements'])} house entries, {removed} villager jigsaws removed from worn copies")

# set lists ALL biomes done so far (re-run with the full list to regenerate the whole set)
existing = OUT / "dying_world/worldgen/structure_set/survivor_villages.json"
have = {m["structure"] for m in set_members}
if existing.exists():
    for m in json.loads(existing.read_text())["structures"]:
        if m["structure"] not in have: set_members.append(m)
w(existing, {"structures": set_members, "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 12,
   "salt": zlib.crc32(b"dying_world:survivor_villages") % 2000000000}})
