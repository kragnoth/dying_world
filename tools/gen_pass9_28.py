#!/usr/bin/env python3
"""
gen_pass9_28.py - pass 9-28: biome-matched single structures, best bang for the buck only (user: 'don't overdo it'). Run after 8_2/8_4, before 9_16. Safe to re-run.
- abandoned_smithy: one spruce/cobble design spawned in every land biome. Now: original in temperate/cold/wild biomes; NEW abandoned_smithy_arid = material swap
  of the same two builds (cobble/stone bricks -> sandstone family, mossy -> plain sandstone, yard dirt/gravel -> sand, vines/moss -> dead bush/none; spruce
  timber kept = our desert family wood) in the arid biomes (deserts, badlands, savanna, dunes, scrubland).
- abandoned_cabin: its oak / spruce / dark oak builds were picked at RANDOM in any of its 8 biomes. Now one structure per wood, biome-matched:
  oak = forest/birch/flower forest, spruce = the taigas incl. snowy, dark oak = dark forest. Landmark weights split from the old entries.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from gen_pass4_2a import w, OUT
SWAP = {"cobblestone": "sandstone", "mossy_cobblestone": "sandstone", "stone_bricks": "cut_sandstone", "mossy_stone_bricks": "cut_sandstone",
        "cracked_stone_bricks": "cut_sandstone", "bricks": "smooth_sandstone", "coarse_dirt": "sand", "gravel": "sandstone", "dirt_path": "smooth_sandstone",
        "grass_block": "sand", "dirt": "sand", "vine": "air", "moss_carpet": "air", "cobblestone_wall": "sandstone_wall", "mossy_cobblestone_wall": "sandstone_wall",
        "stone_brick_stairs": "sandstone_stairs", "stone_brick_slab": "sandstone_slab", "cobblestone_stairs": "sandstone_stairs", "cobblestone_slab": "sandstone_slab",
        "mossy_cobblestone_stairs": "sandstone_stairs", "mossy_stone_brick_stairs": "sandstone_stairs", "short_grass": "dead_bush", "fern": "dead_bush"}
T = OUT / "tags/worldgen/biome/has_structure"
def tag(name, values): w(T / f"{name}.json", {"replace": False, "values": values})
def struct(src, dst, pool, biomes):
    j = json.loads((OUT / f"worldgen/structure/{src}.json").read_text()); j["start_pool"] = pool; j["biomes"] = f"#dying_world:has_structure/{dst}"
    w(OUT / f"worldgen/structure/{dst}.json", j)
def el(loc, wt): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}

def smithy():
    els = []
    for n, wt in (("smithy_1", 3), ("smithy_2", 2)):
        s = nbtrw.Struct((OUT / f"structure/smithy/{n}.nbt").read_bytes())
        for p, (b, pr, nb) in list(s.b.items()):
            k = b.split(":")[1]
            if b.startswith("minecraft:") and k in SWAP:
                nk = SWAP[k]; keep = {kk: v for kk, v in pr.items() if kk in ("facing", "half", "shape", "type", "waterlogged", "up", "north", "south", "east", "west")}
                s.b[p] = ("minecraft:" + nk, keep if nk.endswith(("stairs", "slab", "wall")) else {}, None)
        (OUT / f"structure/smithy/{n}_arid.nbt").write_bytes(s.bytes()); els.append(el(f"dying_world:smithy/{n}_arid", wt))
    w(OUT / "worldgen/template_pool/smithy/start_arid.json", {"fallback": "minecraft:empty", "elements": els})
    tag("abandoned_smithy", ["#dying_world:has_structure/concrete_pad_temperate", "#dying_world:has_structure/concrete_pad_cold", "#dying_world:has_structure/concrete_pad_wild"])
    tag("abandoned_smithy_arid", ["#dying_world:has_structure/concrete_pad_arid"])
    struct("abandoned_smithy", "abandoned_smithy_arid", "dying_world:smithy/start_arid", None)

CABIN = {"oak": ["minecraft:forest", "minecraft:birch_forest", "minecraft:flower_forest"],
         "spruce": ["minecraft:taiga", "minecraft:snowy_taiga", "minecraft:old_growth_spruce_taiga", "minecraft:old_growth_pine_taiga"],
         "dark_oak": ["minecraft:dark_forest"]}
def cabin():
    for wood, biomes in CABIN.items():
        w(OUT / f"worldgen/template_pool/cabin/start_{wood}.json", {"fallback": "minecraft:empty", "elements": [el(f"dying_world:cabin/cabin_{wood}", 1)]})
        name = "abandoned_cabin" if wood == "spruce" else f"abandoned_cabin_{wood}"
        tag(name, biomes)
        if name != "abandoned_cabin": struct("abandoned_cabin", name, f"dying_world:cabin/start_{wood}", None)
    j = json.loads((OUT / "worldgen/structure/abandoned_cabin.json").read_text()); j["start_pool"] = "dying_world:cabin/start_spruce"; w(OUT / "worldgen/structure/abandoned_cabin.json", j)

def main():
    smithy(); cabin(); print("9-28: smithy + arid smithy; cabin split into oak / spruce / dark oak by biome")

if __name__ == "__main__":
    main()
