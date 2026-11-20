#!/usr/bin/env python3
"""gen_pass9_82.py - pass 9-82: structure audit fixes (terrain adaptation, waterlogging, wall lamps).

1. Overworld surface structures on beard_box -> beard_thin. beard_box clears each piece's whole box above its floor, so on a
   slope every house cut a square notch into the hill; beard_thin (vanilla villages, ATi) only clears near the floor and
   builds ground up underneath. Kept on beard_box: research gates/stations (Nether/End) and the sunken lab.
2. Surface structures with no terrain adaptation -> beard_thin: abandoned_ruin_swamp (fixed-length stilts floated on
   slopes), proving_grounds and the_hollow (headframe / marker stood exposed like the mineshaft did).
3. liquid_settings "ignore_waterlogging" on land jigsaw structures, so a fence/stair/slab placed into water doesn't fill.
   Kept on the default: swamp structures (stilts in water), the sunken lab, the lighthouse.
4. Wall lamps: a caged lamp saved facing "down" with air above it but a wall beside it is turned to face away from that
   wall (Hollow and proving-grounds shafts had them hanging from nothing).

Any terrain adaptation adds 12 to the reach; max_distance_from_center is capped at 116 where one is added.
Run after 9_78, before 8_9/build. Safe to re-run.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtrw import Struct
from gen_pass4_2a import OUT

KEEP_BOX = ("research_", "sunken")
TO_THIN = ("abandoned_ruin_swamp", "proving_grounds", "the_hollow")
KEEP_WATER = ("swamp", "sunken", "lighthouse")
AIR = {"minecraft:air", "minecraft:cave_air", "minecraft:structure_void"}
AWAY = {(1, 0): "west", (-1, 0): "east", (0, 1): "north", (0, -1): "south"}

def structures():
    n_thin = n_liq = 0
    for p in sorted((OUT / "worldgen/structure").rglob("*.json")):
        j = json.loads(p.read_text()); name = p.relative_to(OUT / "worldgen/structure").with_suffix("").as_posix()
        if j.get("type") != "minecraft:jigsaw": continue
        before = json.dumps(j)
        ta = j.get("terrain_adaptation", "none")
        if j.get("project_start_to_heightmap") and ((ta == "beard_box" and not name.startswith(KEEP_BOX)) or (ta == "none" and name in TO_THIN)):
            j["terrain_adaptation"] = "beard_thin"; n_thin += 1
        if j.get("terrain_adaptation", "none") != "none":
            md = j.get("max_distance_from_center", 80)
            if isinstance(md, int) and md > 116: j["max_distance_from_center"] = 116
        if j.get("project_start_to_heightmap") and not any(k in name for k in KEEP_WATER):
            if j.get("liquid_settings") != "ignore_waterlogging": n_liq += 1
            j["liquid_settings"] = "ignore_waterlogging"
        if json.dumps(j) != before: p.write_text(json.dumps(j, indent=2) + "\n")
    return n_thin, n_liq

def lamps():
    n = 0
    for f in sorted((OUT / "structure").rglob("*.nbt")):
        s = Struct(f.read_bytes()); changed = False
        for (x, y, z), (name, props, nbt) in list(s.b.items()):
            if not name.endswith("caged_lamp") or props.get("facing") != "down": continue
            if s.b.get((x, y + 1, z), ("minecraft:air",))[0] not in AIR: continue
            for (dx, dz), face in AWAY.items():
                if s.b.get((x + dx, y, z + dz), ("minecraft:air",))[0] not in AIR:
                    s.b[(x, y, z)] = (name, dict(props, facing=face), nbt); changed = True; n += 1
                    break
        if changed: f.write_bytes(s.bytes())
    return n

def main():
    t, l = structures(); n = lamps()
    print(f"9-82: {t} structures -> beard_thin, {l} -> ignore_waterlogging, {n} wall lamps turned")

if __name__ == "__main__":
    main()
