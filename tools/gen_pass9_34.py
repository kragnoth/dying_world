#!/usr/bin/env python3
"""
gen_pass9_34.py - pass 9-34: PROVING GROUNDS get a SURFACE MARKER (user: the map's X sat over solid ground, nothing to find).
Run AFTER gen_pass9_12 (it rewrites the hub + structure json every run) and before 9_16. Safe to re-run (re-applies on 9_12's fresh hub).

New layout: the structure now STARTS at the surface (project to WORLD_SURFACE_WG):
  headframe (9x11x9): a small tuff/copper Guild hut with a lit mast above the roof (seen from a distance), a wall sign, and the ARCHIVE chest
                      (research_proving_archive -> the Proving Ledger journal via the 9-33 lore modifier is now guaranteed); floor centre = shaft.
  shaft_1..3 (5x16x5 each): a scaffolding shaft straight down (3 copies differ only in which pool their bottom jigsaw opens).
  hub (9-12's piece) + an UP jigsaw in its ceiling (8,12,13) and a scaffolding column down to the floor -> wings as before.
Jigsaw size 4 -> 10 (hub moved from depth 0 to depth 4).
Terrain: encapsulate -> none (encapsulate/bury dome the hut under terrain, beard carves caverns round the rooms); the hut stands on a
3-course foundation (start_height -3) and every underground piece is a closed shell anyway.
Depths: hub floor = surface - 67 (inside max_distance_from_center 80).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from nbtw import L as NL
import gen_pass9_11 as K
import gen_pass9_12  # noqa: F401  (registers the proving palette in K.PAL)
from gen_pass9_11 import P, pe, chest
from gen_pass4_2a import M, R, w, OUT

SITE = "proving"; D = OUT / f"structure/station/{SITE}"; POOL = f"dying_world:station/{SITE}"
UP, DOWN = "dying_world:shaft_up", "dying_world:shaft_down"
SCAF = "minecraft:scaffolding[bottom=false,distance=0,waterlogged=false]"
SCAF_B = (M("scaffolding"), {"bottom": "false", "distance": "0", "waterlogged": "false"})

def jig_nbt(name, target, pool):
    return {"id": M("jigsaw"), "name": name, "target": target, "pool": pool, "final_state": SCAF, "joint": "aligned"}

def headframe():
    F = 3                                                                       # foundation depth: the hut floor sits at surface level, the
    p = P(SITE, "headframe", 9, 14, 9, 41)                                      # 3 courses below cover slopes (terrain adaptation is 'none')
    for x in range(9):
        for z in range(9):
            for y in range(F): p.blk(x, y, z, "base")
            p.blk(x, F, z, "floor"); p.blk(x, F + 5, z, "ceil")
            for y in range(F + 1, F + 5):
                if x in (0, 8) or z in (0, 8):
                    corner = x in (0, 8) and z in (0, 8)
                    p.blk(x, y, z, "pillar" if corner else "base" if y == F + 1 else "trim" if y == F + 4 else "wall")
                else: p.b(x, y, z, M("air"))
            for y in range(F + 6, 14): p.b(x, y, z, M("air"))
    for y in range(1, F + 1): p.b(4, y, 4, *SCAF_B)                            # shaft through the foundation, up to the floor
    for y in (F + 1, F + 2): p.b(4, y, 8, M("air"))                             # doorway, south
    for x, z in ((0, 4), (8, 4), (4, 0)): p.b(x, F + 3, z, M("weathered_copper_grate"))   # vents
    p.b(4, 0, 4, M("jigsaw"), {"orientation": "down_north"}, jig_nbt(DOWN, UP, f"{POOL}/shaft_1"))
    for x, z in ((3, 3), (5, 3), (3, 5), (5, 5), (3, 4), (5, 4), (4, 3)): p.b(x, F + 1, z, R("rusted_grate"))   # railing, open to the door side
    p.b(1, F + 1, 6, R("rusted_encased_cogwheel"), {"axis": "x", "top_shaft": "true", "bottom_shaft": "true"})   # winch
    chest(p.t, 1, F + 1, 1, "south", "research_proving_archive")
    p.b(7, F + 1, 1, M("barrel"), {"facing": "up", "open": "false"})
    p.b(4, F + 4, 2, M("lantern"), {"hanging": "true", "waterlogged": "false"})
    sign = lambda *lines: (10, {"messages": NL(8, [json.dumps({"text": t}) for t in lines]), "color": (8, "black"), "has_glowing_text": (1, 0)})
    p.b(2, F + 2, 7, M("spruce_wall_sign"), {"facing": "north", "waterlogged": "false"},
        {"id": M("sign"), "front_text": sign("GEARWRIGHTS", "PROVING GROUNDS", "Crews only.", "Keys by requisition."),
         "back_text": sign("", "", "", ""), "is_waxed": (1, 1)})
    for y in range(F + 6, 13): p.b(4, y, 4, M("iron_bars"))                    # mast + lamp: the marker you see from a distance
    p.b(4, 13, 4, M("lantern"), {"hanging": "false", "waterlogged": "false"})
    return p

def shaft(k, nxt):
    p = P(SITE, f"shaft_{k}", 5, 16, 5, 50 + k); p.shell()
    for y in range(1, 15): p.b(2, y, 2, *SCAF_B)
    p.b(2, 15, 2, M("jigsaw"), {"orientation": "up_north"}, jig_nbt(UP, DOWN, "minecraft:empty"))
    p.b(2, 0, 2, M("jigsaw"), {"orientation": "down_north"}, jig_nbt(DOWN, UP, nxt))
    p.light(1, 13, 1); p.light(3, 6, 3)
    return p

def patch_hub():
    path = D / "hub.nbt"; s = nbtrw.Struct(path.read_bytes())
    assert s.size == [17, 13, 17], s.size
    for y in range(1, 12): s.set(8, y, 13, *SCAF_B)
    s.set(8, 12, 13, M("jigsaw"), {"orientation": "up_north"}, (10, {k: (8, v) for k, v in jig_nbt(UP, DOWN, "minecraft:empty").items()}))
    path.write_bytes(s.bytes())

def main():
    assert (D / "hub.nbt").exists(), "run gen_pass9_12 first"
    patch_hub()
    w(OUT / f"worldgen/template_pool/station/{SITE}/headframe.json", {"fallback": "minecraft:empty", "elements": [pe(headframe().save(D), 1)]})
    for k in (1, 2, 3):
        nxt = f"{POOL}/shaft_{k + 1}" if k < 3 else f"{POOL}/hub"
        w(OUT / f"worldgen/template_pool/station/{SITE}/shaft_{k}.json", {"fallback": "minecraft:empty", "elements": [pe(shaft(k, nxt).save(D), 1)]})
    sp = OUT / "worldgen/structure/proving_grounds.json"; j = json.loads(sp.read_text())
    j.update({"start_pool": f"{POOL}/headframe", "start_height": {"absolute": -3}, "project_start_to_heightmap": "WORLD_SURFACE_WG",
              "terrain_adaptation": "none", "size": 10, "max_distance_from_center": 80, "step": "surface_structures"})
    w(sp, j)
    print("9-34: proving grounds start at the surface (headframe + 3 shaft pieces), hub patched")

if __name__ == "__main__":
    main()
