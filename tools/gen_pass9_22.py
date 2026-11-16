#!/usr/bin/env python3
"""
gen_pass9_22.py - pass 9-22: BIOME SCAVENGER STRONGHOLDS (user: variants). Run after 9_21 + 9_20 + 9_14 + 9_19 (needs the stronghold streets/keeps and the
families' ruined houses incl. rare styles + dig spots); before 9_16 (which puts them in the settlements set). Safe to re-run.
dying_world:scavenger_stronghold_<fam> for plains/taiga/snowy/desert/savanna: same keep, narrow streets, barricades and decor as the generic stronghold, but the
houses are that family's RUINED houses (incl. its rare styles) through gen_pass5_2.build (immune piglins, plain/fort 40/60, rooftop lookouts, scrap) and the
street ground is re-tinted (desert sand/sandstone, snowy snow, taiga podzol, savanna packed mud). Biomes = the family's village biome tag.
The generic scavenger_stronghold (plains houses, any land) stays for every other biome. Woodland explorer maps also point at the 5 new ones.
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
import gen_pass5_2 as F
from gen_pass4_2a import M, w, OUT
from gen_pass5_1 import SH

FAMS = ("plains", "taiga", "snowy", "desert", "savanna")
TINT = {"desert": {"coarse_dirt": ("sand", 1), "gravel": ("sandstone", .5), "mossy_cobblestone": ("sandstone", 1), "cobblestone": ("cut_sandstone", .6), "dirt_path": ("smooth_sandstone", .4)},
        "snowy": {"coarse_dirt": ("snow_block", .5), "gravel": ("snow_block", .3)}, "taiga": {"coarse_dirt": ("podzol", .5)},
        "savanna": {"cobblestone": ("packed_mud", .5), "gravel": ("coarse_dirt", .4)}, "plains": {}}

def copy_nbt(src, dst, fam, r):
    s = nbtrw.Struct(src.read_bytes())
    for p, (n, props, nbt) in list(s.b.items()):
        if n == M("jigsaw") and nbt:
            d = dict(nbt[1]); pool = d["pool"][1]
            for k in ("streets", "houses"):
                if pool == f"{SH}/{k}": d["pool"] = (8, f"{SH}/{fam}/{k}")
            s.b[p] = (n, props, (10, d))
        elif p[1] == 0 and n.split(":")[1] in TINT[fam]:
            b, ch = TINT[fam][n.split(":")[1]]
            if r.random() < ch: s.b[p] = (M(b), {}, None)
    dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(s.bytes())

def main():
    F.FLOORISH = F.FLOORISH + ("wood", "terracotta", "sandstone", "mud", "tile", "deepslate", "andesite", "dirt", "path", "gravel", "brick", "ice")
    F.floor_level = lambda s: 0
    base = OUT / "structure/scavenger_stronghold"; gen = json.loads((OUT / "worldgen/structure/scavenger_stronghold.json").read_text()); out = []
    for fam in FAMS:
        r = random.Random(zlib.crc32(fam.encode())); D = base / fam
        if D.exists():
            for old in D.rglob("*.nbt"): old.unlink()
        for f in (base / "streets").glob("*.nbt"): copy_nbt(f, D / "streets" / f.name, fam, r)
        for f in base.glob("keep_*.nbt"): copy_nbt(f, D / f.name, fam, r)
        F.SRC = OUT / f"structure/{fam}"; (D / "houses").mkdir(parents=True, exist_ok=True); els = []
        for e in json.loads((OUT / f"worldgen/template_pool/{fam}/ruined_houses.json").read_text())["elements"]:
            name = e["element"]["location"].rsplit("/", 1)[1]
            for fort, share in ((False, .4), (True, .6)):
                s, _ = F.build(name, fort, 1); tag = "fort" if fort else "plain"
                (D / "houses" / f"{name}_{tag}.nbt").write_bytes(s.bytes())
                els.append({"weight": max(1, round(e["weight"] * share)), "element": {"element_type": "minecraft:single_pool_element",
                            "location": f"{SH}/{fam}/houses/{name}_{tag}", "processors": "minecraft:empty", "projection": "rigid"}})
        P = OUT / f"worldgen/template_pool/scavenger_stronghold/{fam}"
        st = json.loads((OUT / "worldgen/template_pool/scavenger_stronghold/streets.json").read_text())
        for e in st["elements"]: e["element"]["location"] = e["element"]["location"].replace(f"{SH}/streets/", f"{SH}/{fam}/streets/")
        w(P / "streets.json", st)
        w(P / "houses.json", {"fallback": "minecraft:empty", "elements": els})
        kp = json.loads((OUT / "worldgen/template_pool/scavenger_stronghold/keep.json").read_text())
        for e in kp["elements"]: e["element"]["location"] = e["element"]["location"].replace(f"{SH}/keep_", f"{SH}/{fam}/keep_")
        w(P / "keep.json", kp)
        j = dict(gen); j["biomes"] = f"#dying_world:has_structure/village_{fam}"; j["start_pool"] = f"{SH}/{fam}/keep"
        w(OUT / f"worldgen/structure/scavenger_stronghold_{fam}.json", j)
        out.append(f"{fam} {len(els)} houses")
    tp = OUT.parent / "minecraft/tags/worldgen/structure/on_woodland_explorer_maps.json"
    if tp.exists():
        j = json.loads(tp.read_text()); vals = [v for v in j["values"] if "scavenger_stronghold_" not in str(v)]
        j["values"] = vals + [f"dying_world:scavenger_stronghold_{f}" for f in FAMS]; w(tp, j)
    print("9-22: biome strongholds:", "; ".join(out))

if __name__ == "__main__":
    main()
