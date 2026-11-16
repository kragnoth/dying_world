#!/usr/bin/env python3
"""validate.py - sanity-check the datapack. Optional: --packwork X.zip checks referenced features exist."""
import argparse, json, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).resolve().parent.parent
errs = []
dp = ROOT / "datapack"
ap = argparse.ArgumentParser(); ap.add_argument("--packwork"); a = ap.parse_args()
names = set(zipfile.ZipFile(a.packwork).namelist()) if a.packwork else None

mc = dp / "pack.mcmeta"
try:
    assert json.loads(mc.read_text())["pack"]["pack_format"] == 48
except Exception as e:
    errs.append(f"pack.mcmeta bad: {e}")

n_sets = 0
for f in sorted(dp.rglob("*.json")):
    rel = f.relative_to(dp).as_posix()
    try:
        j = json.loads(f.read_text())
    except Exception as e:
        errs.append(f"{rel}: invalid JSON ({e})"); continue
    if "/worldgen/structure_set/" in rel and rel.startswith("data/"):
        n_sets += 1
        if j.get("structures") != []:
            errs.append(f"{rel}: structure set not empty (use dying_world: namespace for real sets)") \
                if rel.split("/")[1] != "dying_world" else None
    if "/neoforge/biome_modifier/" in rel:
        if "type" not in j: errs.append(f"{rel}: no type")
        if names is not None and j.get("type") == "neoforge:remove_features":
            for fid in j.get("features", []):
                ns, _, p = fid.partition(":")
                if f"data/{ns}/worldgen/placed_feature/{p}.json" not in names:
                    errs.append(f"{rel}: placed feature not found in packwork: {fid}")

# cross-check dying_world sets: structure file + biome tag must exist in this pack
for f in sorted((dp / "data/dying_world/worldgen/structure_set").glob("*.json")):
    j = json.loads(f.read_text())
    for e in j.get("structures", []):
        ns, _, sid = e["structure"].partition(":")
        sf = dp / f"data/{ns}/worldgen/structure/{sid}.json"
        if ns == "dying_world":
            if not sf.exists(): errs.append(f"{f.name}: missing structure {e['structure']}")
            else:
                b = json.loads(sf.read_text()).get("biomes", "")
                if isinstance(b, str) and b.startswith("#dying_world:"):
                    t = dp / f"data/dying_world/tags/worldgen/biome/{b.split(':',1)[1]}.json"
                    if not t.exists(): errs.append(f"{sf.name}: missing biome tag {b}")
    pl = j.get("placement", {})
    if pl.get("spacing", 1) <= pl.get("separation", 0): errs.append(f"{f.name}: spacing must be > separation")

listed = (ROOT / "docs/disabled_structure_sets.txt").read_text().split()
for sid in listed:
    ns, _, p = sid.partition(":")
    if not (dp / f"data/{ns}/worldgen/structure_set/{p}.json").exists():
        errs.append(f"missing override for {sid}")

print(f"checked datapack: {n_sets} structure_set files, {len(listed)} listed")
print("OK" if not errs else "\n".join(errs))
sys.exit(1 if errs else 0)
