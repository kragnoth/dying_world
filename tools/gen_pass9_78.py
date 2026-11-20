#!/usr/bin/env python3
"""gen_pass9_78.py - pass 9-78: structure placement fixes (wells, industrial mineshaft, beaches).

1. Beaches out: beach / shore biomes are removed from has_structure/concrete_pad_wild (wells/wild uses it) and
   has_structure/industrial_mineshaft. A start on a beach sits at the water's edge, so the piece hangs over the sea.
2. Industrial mineshaft: tunnels could branch ~23 blocks under the headframe, so on high ground (cliffs, mountains) the
   tunnel network and container-yard halls ran out over lower ground and hung in the air. The collar now leads into two
   plain shaft segments (pools mineshaft/shaft_upper_a, _b; no branches) before the normal shaft pool, so tunnels start at
   least ~50 blocks under the head. size 14 -> 16 to keep the network's reach; max_distance_from_center 128 -> 116 (with
   terrain adaptation the limit is reach + 12 <= 128). terrain_adaptation none -> beard_thin, so
   ground is built up under the headframe on slopes instead of leaving the collar standing in the open.
3. Wells: each well was one template from the shaft floor up, with beard_box, which carves the whole box above the shaft
   floor - on a slope the shaft stood in the open. Each well is now split at ground level into <style>_top (the start
   piece: platform and roof) and <style>_shaft (hanging below by a jigsaw), with beard_thin and start_height -1. The beard's
   ground level is the start piece's bottom + 1 (see tools/footing.py), so ground is now built up to the platform and
   filled around the shaft, and the platform sits one block into the ground.

Reads gen_pass8_6's wells/<style>.nbt and gen_pass4_2a's mineshaft pieces; safe to re-run. Run after 9_76, before 8_9/build.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtrw import Struct
from gen_pass4_2a import OUT

DW = "dying_world"
BEACHY = ("beach", "shore")

def rj(p): return json.loads(p.read_text())
def wj(p, j): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(j, indent=2) + "\n")

def single_pool(loc):
    return {"fallback": "minecraft:empty", "elements": [{"weight": 1, "element": {
        "element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}]}

def jig(name, pool, final="minecraft:air"):
    return {"id": (8, "minecraft:jigsaw"), "name": (8, name), "target": (8, name), "pool": (8, pool),
            "final_state": (8, final), "joint": (8, "aligned")}

# ---- 1. beaches ----------------------------------------------------------------------------------------------------
def beaches():
    n = 0
    for t in ("concrete_pad_wild", "industrial_mineshaft"):
        p = OUT / f"tags/worldgen/biome/has_structure/{t}.json"; j = rj(p)
        keep = [v for v in j["values"] if not any(k in (v["id"] if isinstance(v, dict) else v) for k in BEACHY)]
        n += len(j["values"]) - len(keep); j["values"] = keep; wj(p, j)
    return n

# ---- 2. mineshaft ---------------------------------------------------------------------------------------------------
def mineshaft():
    sd = OUT / "structure/mineshaft"; pd = OUT / "worldgen/template_pool/mineshaft"
    src = {p.stem: p for p in sd.rglob("*.nbt")}
    rel = lambda name: src[name].relative_to(OUT / "structure").with_suffix("").as_posix()
    collar = Struct(src["shaft_collar_1"].read_bytes())
    for k, (n, props, nbt) in collar.b.items():
        if n == "minecraft:jigsaw" and props.get("orientation", "").startswith("down"):
            nbt[1]["pool"] = (8, f"{DW}:mineshaft/shaft_upper_a")
    src["shaft_collar_1"].write_bytes(collar.bytes())
    for stage, nxt in (("a", "shaft_upper_b"), ("b", "shaft")):
        locs = []
        for plain in ("shaft_plain_1", "shaft_plain_2"):
            s = Struct(src[plain].read_bytes())
            for k, (n, props, nbt) in s.b.items():
                if n == "minecraft:jigsaw" and props.get("orientation", "").startswith("down"):
                    nbt[1]["pool"] = (8, f"{DW}:mineshaft/{nxt}")
            out = src[plain].with_name(f"shaft_upper_{stage}{plain[-1]}.nbt"); out.write_bytes(s.bytes())
            locs.append(f"{DW}:" + out.relative_to(OUT / "structure").with_suffix("").as_posix())
        pool = single_pool(locs[0]); pool["fallback"] = f"{DW}:mineshaft/shaft_caps"
        pool["elements"].append({"weight": 1, "element": dict(pool["elements"][0]["element"], location=locs[1])})
        wj(pd / f"shaft_upper_{stage}.json", pool)
    p = OUT / "worldgen/structure/industrial_mineshaft.json"; j = rj(p)
    # any terrain adaptation adds 12 to the reach, and Minecraft refuses max_distance_from_center + 12 > 128
    j["size"] = 16; j["terrain_adaptation"] = "beard_thin"; j["max_distance_from_center"] = min(j["max_distance_from_center"], 116); wj(p, j)

# ---- 3. wells -------------------------------------------------------------------------------------------------------
G = 6   # gen_pass8_6 DEPTH: shaft y0..5, ground/platform layer y6

def crop(s, y0, y1):
    c = Struct(s.raw)
    c.b = {(x, y - y0, z): v for (x, y, z), v in s.b.items() if y0 <= y < y1}
    c.ents = []; c.size = [s.size[0], y1 - y0, s.size[2]]
    return c

def wells():
    wd = OUT / "structure/wells"
    for style in ("arid", "cold", "temperate", "washhouse", "wild"):
        s = Struct((wd / f"{style}.nbt").read_bytes()); s.raw = (wd / f"{style}.nbt").read_bytes()
        xs = [k[0] for k in s.b if k[1] == 0]; zs = [k[2] for k in s.b if k[1] == 0]
        cx, cz = (min(xs) + max(xs)) // 2, (min(zs) + max(zs)) // 2
        top, shaft = crop(s, G, s.size[1]), crop(s, 0, G)
        top.set(cx, 0, cz, "minecraft:jigsaw", {"orientation": "down_north"}, (10, jig(f"{DW}:well_shaft", f"{DW}:wells/{style}_shaft")))
        shaft.set(cx, G - 1, cz, "minecraft:jigsaw", {"orientation": "up_north"}, (10, jig(f"{DW}:well_shaft", "minecraft:empty")))
        (wd / f"{style}_top.nbt").write_bytes(top.bytes()); (wd / f"{style}_shaft.nbt").write_bytes(shaft.bytes())
        wj(OUT / f"worldgen/template_pool/wells/{style}.json", single_pool(f"{DW}:wells/{style}_top"))
        wj(OUT / f"worldgen/template_pool/wells/{style}_shaft.json", single_pool(f"{DW}:wells/{style}_shaft"))
        p = OUT / f"worldgen/structure/wells/{style}.json"; j = rj(p)
        j.update(size=2, start_height={"absolute": -1}, terrain_adaptation="beard_thin"); wj(p, j)

def main():
    n = beaches(); mineshaft(); wells()
    print(f"9-78: {n} beach/shore biomes removed; mineshaft shaft_upper a/b + beard_thin; 5 wells split top/shaft + beard_thin")

if __name__ == "__main__":
    main()
