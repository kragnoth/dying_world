#!/usr/bin/env python3
"""
gen_pass8_11.py - pass 8-11: drop EVERYTHING from the third-party datapacks Brutos + vsrevamped (user decision), incl. what we built on them.
Run after gen_pass3c4.py (which no longer has the cherry donor). Deletes: our worn cherry copies + their mix processor lists, the vsrevamped
structure-set disable overrides (the datapack itself is gone from the instance), and the brutos/vsrevamped files kept in datapack_imported/ and
kubejs_base/ (user's kubejs data). They stay recoverable from the 8-1 uploads/archive if ever needed. Safe to re-run.
"""
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
gone = []
for p in [ROOT / "datapack/data/dying_world/structure/village/plains/mix_worn/cherry", ROOT / "datapack/data/vsrevamped",
          ROOT / "datapack_imported/data/brutos", ROOT / "datapack_imported/data/vsrevamped", ROOT / "kubejs_base/data/brutos", ROOT / "kubejs_base/data/vsrevamped"]:
    if p.exists(): shutil.rmtree(p); gone.append(str(p.relative_to(ROOT)))
for p in (ROOT / "datapack/data/dying_world/worldgen/processor_list").rglob("*.json"):
    if "cherry" in p.name or "brutos" in p.read_text() or "vsrevamped" in p.read_text(): p.unlink(); gone.append(str(p.relative_to(ROOT)))
# the user's custom plains/taiga/snowy STREET sets use vsrevamped processors (= vsrevamped content) -> survivor villages get VANILLA streets
import json, zipfile, sys
sys.path.insert(0, str(ROOT / "tools")); from gen_pass4_2a import w
NBTZ = zipfile.ZipFile(ROOT / "reference/structures_nbt.zip")
PROC = {"plains": "minecraft:street_plains", "taiga": "minecraft:street_snowy_or_taiga", "snowy": "minecraft:street_snowy_or_taiga"}
for fam, proc in PROC.items():
    els = []
    for n in sorted(NBTZ.namelist()):
        pre = f"data/minecraft/structure/village/{fam}/streets/"
        if not n.startswith(pre) or "/" in n[len(pre):]: continue
        name = n[len(pre):-4]
        if name.startswith(fam + "_"): continue                              # custom (vsrevamped) pieces
        wt = 4 if name.startswith("straight") else 3 if name.startswith("turn") else 2
        els.append({"weight": wt, "element": {"element_type": "minecraft:legacy_single_pool_element", "location": f"minecraft:village/{fam}/streets/{name}",
                    "processors": proc, "projection": "terrain_matching"}})
    w(ROOT / f"datapack/data/minecraft/worldgen/template_pool/village/{fam}/streets.json", {"fallback": f"minecraft:village/{fam}/terminators", "elements": els})
    gone.append(f"{fam} streets -> {len(els)} vanilla pieces (custom vsrevamped streets dropped)")
print("8-11 removed:", *gone, sep="\n  ")
