#!/usr/bin/env python3
"""
gen_pass4_2e.py - pass 4-2e: FLOODED and TAR-SOAKED tunnel variants for the industrial mineshaft.
Run order: gen_pass4_2a -> 4_2b -> 4_2c -> 4_2e -> 4_2s (2e appends to the tunnels pool that 2a rewrites).

Both are 9x15 straight tunnels (same N/S connectors as straight_plain) built 3 layers TALLER at the bottom:
the normal tunnel sits on y=3 (jigsaws at y=6; jigsaw alignment keeps floors level with neighbours) and a PIT is dug
below the floor over z=3..11, x=2..6, leaving 1-block ledges along both walls (rib posts stand on the ledges).
Fluid surface is flush with the floor (y=3), so the pit is sealed on all sides and cannot spill into other tunnels.
- flooded_1/2: water 4 deep (y0 pit floor, y1-3 water) -> drowned spawn here by themselves (spawn_overrides from 4-2s).
  Walls ~15% mossy cobblestone, more dead lamps feel (same lamp() mix), no track (ripped out), a few sunken crates.
- tarred_1/2: tarbound:tar (fluid, level 0) 3 deep (y1 pit floor, y2-3 tar). Walls ~35% tarbound:tar_soaked_planks,
  ledge on ONE side broken (~40% of its cells missing => tar), the other side intact; oil puddles + tar-leaking drums on the ledges.
Processor: mineshaft_no_float as for every branch piece (in a cavern, pit walls over open air are skipped; small spill risk there).
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from rr_connect import connect
from gen_pass4_2a import M, R, H, box_piece, wall, w, elem, OUT, CRATES

DY, PZ0, PZ1, PX0, PX1 = 3, 3, 11, 2, 6
T = lambda n: "tarbound:" + n

def lifted(base):
    t = Tpl(base.sx, base.sy + DY, base.sz)
    for (x, y, z), v in base.b.items(): t.b[(x, y + DY, z)] = v
    return t

def variant(kind, seed):
    r = random.Random(zlib.crc32(kind.encode()) + seed)
    ribs = (2, 7, 12) if seed == 1 else (4, 10)
    base = box_piece(9, 15, "NS", seed + 40, f"{kind}_tunnel", ribs=ribs)
    t = lifted(base)
    fluid, pit_floor = (M("water"), 0) if kind == "flooded" else (T("tar"), 1)
    for z in range(PZ0 - 1, PZ1 + 2):                 # pit box: walls + floor + fluid
        for x in range(PX0 - 1, PX1 + 2):
            for y in range(0, DY + 1):
                edge = x in (PX0 - 1, PX1 + 1) or z in (PZ0 - 1, PZ1 + 1)
                if edge:
                    if y < DY: t.set(x, y, z, wall(r))
                elif y < pit_floor: t.set(x, y, z, wall(r))
                elif y == pit_floor: t.set(x, y, z, R("weathered_concrete") if r.random() < .55 else M("gravel"))
                else: t.set(x, y, z, fluid, {"level": "0"})
        for x in (0, 8):                              # outer wall below the ledges (seals the broken tar ledge)
            for y in range(0, DY): t.set(x, y, z, wall(r))
    for (x, y, z), (name, props, nbt) in list(t.b.items()):   # anything that was standing in the pit area at floor+1 (clutter) is dropped
        if PX0 <= x <= PX1 and PZ0 <= z <= PZ1 and y == DY + 1 and name not in (M("air"),): t.set(x, y, z, M("air"))
    for (x, y, z), (name, props, nbt) in list(t.b.items()):   # wall retheme
        if y <= DY or not (x in (0, 8) or y == t.sy - 1): continue
        if kind == "flooded" and r.random() < .15: t.set(x, y, z, M("mossy_cobblestone"))
        if kind == "tarred" and r.random() < .35: t.set(x, y, z, T("tar_soaked_planks"))
    if kind == "flooded":
        for _ in range(3):                            # sunken crates on the pit floor
            t.set(r.randint(PX0, PX1), 1, r.randint(PZ0, PZ1), r.choice(CRATES))
    else:
        broken = 1 if seed == 1 else 7                # one ledge side broken
        posts = {z for z in ribs}
        for z in range(PZ0, PZ1 + 1):
            if z not in posts and r.random() < .4:
                for y in range(pit_floor + 1, DY + 1): t.set(broken, y, z, T("tar"), {"level": "0"})
                t.set(broken, pit_floor, z, wall(r))
                t.set(broken, DY + 1, z, M("air"))
        for _ in range(5):
            x, z = r.choice((1, 7)), r.randint(2, 12)
            if t.b.get((x, DY, z), ("",))[0] != T("tar") and t.b.get((x, DY + 1, z), (M("air"),))[0] == M("air"):
                t.set(x, DY + 1, z, R("oil_puddle") if r.random() < .7 else R("tar_leaking_drum"))
    return t

def main():
    N = OUT / "structure/mineshaft"; kit = {}
    for s in (1, 2):
        kit[f"flooded_{s}"] = variant("flooded", s)
        kit[f"tarred_{s}"] = variant("tarred", s)
    for n, t in kit.items(): connect(t); (N / f"{n}.nbt").write_bytes(t.bytes())
    p = OUT / "worldgen/template_pool/mineshaft/tunnels.json"; j = json.loads(p.read_text())
    j["elements"] = [e for e in j["elements"] if not any(k in json.dumps(e) for k in ("flooded_", "tarred_"))] + [elem(n, 1) for n in kit]
    w(p, j)
    print(f"4-2e: {len(kit)} variant tunnels ({', '.join(kit)}), tunnels pool now {len(j['elements'])} entries")

if __name__ == "__main__":
    main()
