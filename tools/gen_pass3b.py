#!/usr/bin/env python3
"""gen_pass3b.py - pass 3b batch 1: re-register tarbound x4 + abandoned_cabin as dying_world: structures.
Per structure (3 files, see docs/roster.md): copy of the original structure json (biomes -> own tag),
own biome tag (initially = original tags), own structure_set (own salt/spacing, no exclusion_zone yet).
Reads originals from reference/worldgen_reference.zip. Safe to re-run (overwrites only these files)."""
import json, zipfile, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
REF = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip")
OUT = ROOT / "datapack/data/dying_world"

# id: (source ns, source structure file, tag source, (spacing, separation))
BATCH = {
    "charnel_crypt":    ("tarbound", "charnel_crypt",    "tag", (64, 20)),
    "drowned_radio":    ("tarbound", "drowned_radio",    "tag", (40, 14)),
    "researcher_cabin": ("tarbound", "researcher_cabin", "tag", (56, 18)),
    "wayside_shrine":   ("tarbound", "wayside_shrine",   "tag", (40, 14)),
    "abandoned_cabin":  ("abandoned_cabins", "abandoned_cabin", "inline", (36, 12)),
    # 3b-2
    "burnt_homestead":  ("gearwrights", "burnt_homestead", "tag", (48, 16)),
    "burnt_manor":      ("gearwrights", "burnt_manor",     "tag", (80, 28)),
    "burnt_watchtower": ("gearwrights", "burnt_watchtower","tag", (60, 20)),
    "abandoned_watchtower": ("watchtower_building", "abandoned_watchtower", "inline", (56, 20)),
}

def w(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")

for sid, (ns, src, tagmode, (sp, sep)) in BATCH.items():
    s = json.loads(REF.read(f"data/{ns}/worldgen/structure/{src}.json"))
    own_tag = f"dying_world:has_structure/{sid}"
    if tagmode == "tag":
        vals = [s["biomes"]]                      # e.g. "#tarbound:has_charnel_crypt" - same behaviour as original
    else:
        vals = list(s["biomes"]) if isinstance(s["biomes"], list) else [s["biomes"]]
        vals = [v if ":" in v or v.startswith("#") else f"minecraft:{v}" for v in vals]
    s["biomes"] = "#" + own_tag
    w(OUT / f"worldgen/structure/{sid}.json", s)
    w(OUT / f"tags/worldgen/biome/has_structure/{sid}.json", {"replace": False, "values": vals})
    w(OUT / f"worldgen/structure_set/{sid}.json", {
        "structures": [{"structure": f"dying_world:{sid}", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": sp, "separation": sep,
                      "salt": zlib.crc32(f"dying_world:{sid}".encode()) % 2000000000}})
    print("wrote", sid, sp, sep)
