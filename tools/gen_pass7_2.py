#!/usr/bin/env python3
"""
gen_pass7_2.py - pass 7-2: abandoned SAVANNA ruins/hamlets/villages rebuilt from the new savanna houses (ruined variants). Run AFTER gen_pass7_1.py,
gen_pass3b2.py and gen_pass6_1.py. Safe to re-run.
- dying_world:abandoned_ruin_savanna   -> single ruined house (pool dying_world:savanna/ruined_houses), beard_box.
- dying_world:abandoned_hamlet_savanna / abandoned_village_savanna -> VANILLA savanna meeting points + vanilla streets (non-custom names) copied to
  structure/savanna/abandoned/ with jigsaw pools retargeted: houses -> ruined_houses, streets -> our abandoned streets, villagers/cats/golem -> empty
  (decor/terminators stay vanilla). Hamlet size 4, village size 6. gearwrights abandoned/savanna pieces are no longer used (=> archive).
- Survivor village: drops the user's custom 'savanna_teepee_crossing' town centre (all teepees go, user decision 7-0b) via an override of
  minecraft:village/savanna/town_centers (other custom centres kept).
"""
import gzip, json, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pass4_2a import w, OUT

ROOT = Path(__file__).resolve().parent.parent
NBTZ = zipfile.ZipFile(ROOT / "reference/structures_nbt.zip"); WG = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip")
SA = "dying_world:savanna/abandoned"
def lp(s): b = s.encode(); return len(b).to_bytes(2, "big") + b
RT = {"minecraft:village/savanna/houses": "dying_world:savanna/ruined_houses", "minecraft:village/savanna/zombie/houses": "dying_world:savanna/ruined_houses",
      "minecraft:village/savanna/streets": f"{SA}/streets", "minecraft:village/savanna/zombie/streets": f"{SA}/streets",
      "minecraft:village/savanna/villagers": "minecraft:empty", "minecraft:village/savanna/zombie/villagers": "minecraft:empty",
      "minecraft:village/common/cats": "minecraft:empty", "minecraft:village/common/iron_golem": "minecraft:empty",
      "minecraft:village/common/animals": "minecraft:empty", "minecraft:village/common/butcher_animals": "minecraft:empty"}

def copy(loc, sub):
    raw = gzip.decompress(NBTZ.read(f"data/minecraft/structure/{loc.split(':')[1]}.nbt"))
    for a, b in RT.items(): raw = raw.replace(lp(a), lp(b))
    name = loc.rsplit("/", 1)[1]; p = OUT / f"structure/savanna/abandoned/{sub}/{name}.nbt"; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(gzip.compress(raw, mtime=0)); return f"{SA}/{sub}/{name}"

def pe(loc, wt, proj): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": proj}}

def main():
    # vanilla savanna pools straight from the vanilla jar copy (reference keeps them under worldgen_reference? fall back to name scan)
    names = [n for n in NBTZ.namelist() if n.startswith("data/minecraft/structure/village/savanna/") and "/zombie/" not in n]
    streets = [n for n in names if "/streets/" in n and "/savanna_" not in n.rsplit("/", 1)[1]]
    centres = [n for n in names if "/town_centers/savanna_meeting_point_" in n]
    loc = lambda n: "minecraft:" + n[len("data/minecraft/structure/"):-4]
    s_el = [pe(copy(loc(n), "streets"), 2, "terrain_matching") for n in streets]
    c_el = [pe(copy(loc(n), "town_centers"), 1, "rigid") for n in centres]
    w(OUT / "worldgen/template_pool/savanna/abandoned/streets.json", {"fallback": "minecraft:village/savanna/terminators", "elements": s_el})
    w(OUT / "worldgen/template_pool/savanna/abandoned/town_centers.json", {"fallback": "minecraft:empty", "elements": c_el})
    for kind, size in (("hamlet", 4), ("village", 6)):
        p = OUT / f"worldgen/structure/abandoned_{kind}_savanna.json"; j = json.loads(p.read_text())
        j.update({"start_pool": f"{SA}/town_centers", "size": size, "terrain_adaptation": "beard_box"}); w(p, j)
    p = OUT / "worldgen/structure/abandoned_ruin_savanna.json"; j = json.loads(p.read_text())
    j.update({"start_pool": "dying_world:savanna/ruined_houses", "size": 1, "terrain_adaptation": "beard_box"}); j.pop("start_jigsaw_name", None); w(p, j)
    # survivor village: drop the teepee town centre
    src = ROOT / "datapack_imported/data/minecraft/worldgen/template_pool/village/savanna/town_centers.json"
    tc = json.loads(src.read_text()); tc["elements"] = [e for e in tc["elements"] if "teepee" not in json.dumps(e)]
    w(OUT.parent / "minecraft/worldgen/template_pool/village/savanna/town_centers.json", tc)
    print(f"7-2: abandoned savanna: {len(s_el)} streets + {len(c_el)} meeting points copied (retargeted); ruin/hamlet/village -> new ruined houses; teepee crossing dropped")

if __name__ == "__main__":
    main()
