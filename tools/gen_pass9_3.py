#!/usr/bin/env python3
"""
gen_pass9_3.py - pass 9-3: (a) cherry builds removed, (b) OUR PLAINS STREET SET (gradient 'BDubs' streets). Run after 3b2/3c4/6_1/9_1. Safe to re-run.

(a) user: 'not a fan of the cherry builds at all' -> dying_world:abandoned_{ruin,hamlet,village}_cherry deleted (structure + biome tag) and removed
    from their sets. (Only cherry-built NBTs we shipped were gearwrights abandoned/cherry.)
(b) Street pieces are NARROW (path 5 + 1 verge each side = 7 wide): house entrance jigsaws sit on the verge facing out, so houses are placed
    OUTSIDE the street's bounding box (global free space) - big houses fit, villages get dense. (Vanilla 16x16 street boxes only allow houses that
    fit inside the box, which is why our large buildings rarely spawned.)
    Gradient across the road: verge grass/coarse dirt + flowers -> gravel/coarse dirt edges -> dirt path -> centre dirt path with clustered
    cobble/stone-brick paving (value noise). Lamp posts (fence + lantern on top, head-clear), hedges (persistent oak leaves), hay/barrels, decor jigsaws
    (minecraft:village/plains/decor). Pieces: straight16 (2 plots/side), straight10 (1 plot/side), cross (4 streets), tee (3 streets + plot),
    corner (2 streets + 2 plots), end (cul-de-sac: 1 street + 3 plots). Street jigsaws on the centre line, y1, aligned (vanilla convention).
    Pool minecraft:village/plains/streets = ours only, terrain_matching, fallback minecraft:village/plains/terminators.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from buildkit import M, rng, fix_connections
from savanna_kit import vnoise
from gen_pass4_2a import w, OUT

# 9-4: family palette + pools are module globals so other families reuse the generator (set PAL/FAMILY, call straight()/junction())
FAMILY = "plains"
PAL = {"verge": ["grass_block", "coarse_dirt"], "edge": ["gravel", "coarse_dirt", "dirt_path"], "inner": ["dirt_path", "cobblestone"],
       "centre": ["cobblestone", "stone_bricks", "mossy_cobblestone", "dirt_path"], "fence": "oak_fence", "hedge": "oak_leaves",
       "flowers": ["poppy", "dandelion", "cornflower", "oxeye_daisy"], "props": [("hay_block", {"axis": "y"}), ("barrel", {"facing": "up", "open": "false"})]}
DEC = "minecraft:village/plains/decor"
def jig(t, x, y, z, ori, name, pool, final="minecraft:structure_void", joint="aligned"):
    t.set(x, y, z, M("jigsaw"), {"orientation": ori}, {"id": M("jigsaw"), "name": name, "target": name, "pool": pool, "final_state": final, "joint": joint})
ABANDONED = False   # 9-6: abandoned variant -> own pools (ruined houses only, no decor/villagers), unlit lamp posts
def street_j(t, x, z, ori): jig(t, x, 1, z, ori, "minecraft:street", f"dying_world:{FAMILY}/abandoned/streets" if ABANDONED else f"minecraft:village/{FAMILY}/streets")
def plot_j(t, x, z, ori): jig(t, x, 1, z, ori, "minecraft:building_entrance", f"dying_world:{FAMILY}/ruined_houses" if ABANDONED else f"minecraft:village/{FAMILY}/houses")
def decor_j(t, x, z):
    if ABANDONED: return
    jig(t, x, 0, z, "up_north", "minecraft:bottom", f"minecraft:village/{FAMILY}/decor", M(PAL["verge"][0]), "rollable")

def surface(t, r, seed, cells):
    """cells: {(x,z): d} with d = distance from the road centre line (0 centre .. 3 verge). Gradient + clustered paving."""
    for (x, z), d in cells.items():
        n = vnoise(x, 0, z, seed, 2.5)
        v, e, i, c = PAL["verge"], PAL["edge"], PAL["inner"], PAL["centre"]
        if d >= 3: b = M(v[0] if n > -.3 else v[1])
        elif d == 2: b = M(e[0] if n > .2 else e[1] if n > -.3 else e[2])
        elif d == 1: b = M(i[0] if n < .35 else i[1])
        else: b = M(c[0] if n > .1 else c[1] if n > -.1 else c[2] if n > -.3 else c[3])
        t.set(x, 0, z, b)
        for y in (1, 2, 3, 4): t.set(x, y, z, M("air")) if (x, y, z) not in t.b else None
def lamp(t, x, z):
    if ABANDONED:                                                 # leaning, unlit: 1-2 high post stub
        for y in range(1, 1 + (x + z) % 2 + 1): t.set(x, y, z, M(PAL["fence"]))
        return
    for y in (1, 2, 3): t.set(x, y, z, M(PAL["fence"]))
    t.set(x, 4, z, M("lantern"), {"hanging": "false", "waterlogged": "false"})        # standing on the post top: above head height
def verge_props(t, r, x, z, n):
    if n > .45 and PAL["hedge"]: t.set(x, 1, z, M(PAL["hedge"]), {"distance": "1", "persistent": "true", "waterlogged": "false"})
    elif n > .3:
        f = r.choice(PAL["flowers"]); t.set(x, 1, z, M(f), {"age": "3"} if f == "sweet_berry_bush" else None)
    elif n < -.55:
        b, pr = r.choice(PAL["props"]); t.set(x, 1, z, M(b), pr)

def straight(L, seed):
    r = rng("pst" + str(L), seed); t = Tpl(7, 5, L)
    surface(t, r, seed, {(x, z): abs(x - 3) for x in range(7) for z in range(L)})
    street_j(t, 3, 0, "north_up"); street_j(t, 3, L - 1, "south_up")
    plots = [L // 4, 3 * L // 4] if L >= 14 else [L // 2]
    for z in plots: plot_j(t, 0, z, "west_up"); plot_j(t, 6, z, "east_up")
    for z in range(2, L - 2):                                     # verge furniture between plots
        if all(abs(z - p) > 2 for p in plots):
            for x in (0, 6): verge_props(t, r, x, z, vnoise(x, 0, z, seed + 9, 2))
    lamp(t, 0, 1) if seed % 2 else lamp(t, 6, 1)
    if L >= 14: lamp(t, 6 if seed % 2 else 0, L // 2)
    decor_j(t, 0, L - 2); decor_j(t, 6, 2)
    fix_connections(t); return t

def junction(kind, seed):
    """7x7 square: kind cross / tee / corner / end. Sides: N,E,S,W -> street or plot."""
    r = rng("pjn" + kind, seed); t = Tpl(7, 5, 7)
    sides = {"cross": "SSSS", "tee": "SSSP", "corner": "SSPP", "end": "SPPP"}[kind]    # order N, E, S, W (N is always a street)
    st = dict(zip("NESW", sides))
    def dist(x, z):                                               # road arms run out to every street side; plaza in the middle
        c = [max(abs(x - 3), abs(z - 3)) - 1]
        if (st["N"] == "S" and z <= 3) or (st["S"] == "S" and z >= 3): c.append(abs(x - 3))
        if (st["E"] == "S" and x >= 3) or (st["W"] == "S" and x <= 3): c.append(abs(z - 3))
        return max(0, min(3, min(c)))
    surface(t, r, seed, {(x, z): dist(x, z) for x in range(7) for z in range(7)})
    spots = {"N": (3, 0, "north_up"), "E": (6, 3, "east_up"), "S": (3, 6, "south_up"), "W": (0, 3, "west_up")}
    for side, k in zip("NESW", sides):
        x, z, ori = spots[side]
        (street_j if k == "S" else plot_j)(t, x, z, ori)
    corners = [(0, 0), (6, 0), (0, 6), (6, 6)]
    for i, (x, z) in enumerate(corners):
        if kind == "cross" and i == seed % 4: lamp(t, x, z)
        elif kind != "cross" and i == 0: lamp(t, x, z)
        else: verge_props(t, r, x, z, vnoise(x, 0, z, seed + 3, 1.5))
    if kind == "end":                                             # little turning circle: a well-trough in the middle
        t.set(3, 1, 3, M("water_cauldron"), {"level": "3"})
    fix_connections(t); return t

def main():
    # (a) cherry builds out
    S = OUT / "worldgen/structure"; T = OUT / "tags/worldgen/biome/has_structure"; gone = []
    for k in ("ruin", "hamlet", "village"):
        for p in (S / f"abandoned_{k}_cherry.json", T / f"abandoned_{k}_cherry.json"):
            if p.exists(): p.unlink(); gone.append(p.name)
        sp = OUT / f"worldgen/structure_set/abandoned_{k}s.json"
        if sp.exists():
            j = json.loads(sp.read_text()); j["structures"] = [e for e in j["structures"] if "cherry" not in e["structure"]]; w(sp, j)
    write_streets()
    print(f"9-3: cherry removed ({', '.join(gone)}); plains streets written")

def write_streets():
    sub = "abandoned/streets" if ABANDONED else "streets"
    N = OUT / f"structure/{FAMILY}/{sub}"; N.mkdir(parents=True, exist_ok=True); els = []
    pieces = [("straight16_1", straight(16, 1), 5), ("straight16_2", straight(16, 2), 5), ("straight10_1", straight(10, 1), 3),
              ("cross_1", junction("cross", 1), 2), ("tee_1", junction("tee", 1), 3), ("tee_2", junction("tee", 2), 2),
              ("corner_1", junction("corner", 1), 3), ("end_1", junction("end", 1), 1)]
    for name, t, wt in pieces:
        (N / f"{name}.nbt").write_bytes(t.bytes())
        els.append({"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:{FAMILY}/{sub}/{name}",
                    "processors": "minecraft:empty", "projection": "terrain_matching"}})
    if ABANDONED:
        w(OUT / f"worldgen/template_pool/{FAMILY}/abandoned/streets.json", {"fallback": "minecraft:empty", "elements": els})
        t = junction("cross", 7)                                  # start piece: overgrown crossroads with a dry trough
        t.set(3, 1, 3, M("cauldron")); (N / "plaza.nbt").write_bytes(t.bytes())
        w(OUT / f"worldgen/template_pool/{FAMILY}/abandoned/town_centers.json", {"fallback": "minecraft:empty", "elements": [
            {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": f"dying_world:{FAMILY}/{sub}/plaza",
             "processors": "minecraft:empty", "projection": "terrain_matching"}}]})
    else:
        w(OUT.parent / f"minecraft/worldgen/template_pool/village/{FAMILY}/streets.json", {"fallback": f"minecraft:village/{FAMILY}/terminators", "elements": els})
    return len(pieces)

if __name__ == "__main__":
    main()
