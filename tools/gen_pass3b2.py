#!/usr/bin/env python3
"""gen_pass3b2.py - pass 3b-3 + 3b-4: multi-variant / remaining Tier A sets as dying_world:.
Per member structure: copy of original structure json (biomes -> own tag that starts as the original tag),
own tag file; per set: own structure_set (own salt/spacing, original frequency keys kept where listed). Reads reference/worldgen_reference.zip.
Road signs deliberately NOT registered (they point at #minecraft:village; revisit in 3c)."""
import json, re, zipfile, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
REF = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip")
OUT = ROOT / "datapack/data/dying_world"
V = ["plains", "taiga", "savanna", "desert", "snowy", "cherry", "swamp"]

def rd(name):
    t = REF.read(name).decode("utf-8")
    t = re.sub(r"^\s*//.*$", "", t, flags=re.M)          # createnewbeg files carry // comment lines
    return json.loads(t)
def w(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, indent=2) + "\n")

# set id: (spacing, separation, extra placement keys, [(src ns, src path, weight)])
SETS = {
 "abandoned_ruins":    (24, 8,  {"frequency": 0.55, "frequency_reduction_method": "default"}, [("gearwrights", f"abandoned_ruin_{v}", 1) for v in V]),
 "abandoned_hamlets":  (32, 12, {"frequency": 0.85, "frequency_reduction_method": "default"}, [("gearwrights", f"abandoned_hamlet_{v}", 1) for v in V]),
 "abandoned_villages": (44, 16, {}, [("gearwrights", f"abandoned_village_{v}", 1) for v in V]),
 "collapsed_minehead": (48, 16, {}, [("gearwrights", "collapsed_minehead", 1)]),
 "ruined_chapel":      (64, 22, {}, [("gearwrights", "ruined_chapel", 1)]),
 "abandoned_smithy":   (80, 30, {}, [("createnewbeg", "abandoned_smithy", 1)]),
 "lighthouse":         (80, 30, {}, [("createnewbeg", "lighthouse", 1)]),
 "shipwrecks":         (40, 12, {}, [("minecraft", "shipwreck", 1), ("minecraft", "shipwreck_beached", 1)]),
 "wells":              (40, 14, {"frequency": 0.6, "frequency_reduction_method": "default"}, None),  # members/weights read from forsaken set
}
wells = rd("data/forsaken/worldgen/structure_set/wells.json")
SETS["wells"] = SETS["wells"][:3] + ([(e["structure"].split(":")[0], e["structure"].split(":")[1], e["weight"]) for e in wells["structures"]],)

for sid, (sp, sep, extra, members) in SETS.items():
    ents = []
    for ns, path, wt in members:
        s = rd(f"data/{ns}/worldgen/structure/{path}.json")
        s.pop("values", None)                              # stray empty key in createnewbeg structures
        orig = s["biomes"]
        vals = [orig] if isinstance(orig, str) else [v if ":" in v else f"minecraft:{v}" for v in orig]
        s["biomes"] = f"#dying_world:has_structure/{path}"
        w(OUT / f"worldgen/structure/{path}.json", s)
        w(OUT / f"tags/worldgen/biome/has_structure/{path}.json", {"replace": False, "values": vals})
        ents.append({"structure": f"dying_world:{path}", "weight": wt})
    pl = {"type": "minecraft:random_spread", "spacing": sp, "separation": sep,
          "salt": zlib.crc32(f"dying_world:{sid}".encode()) % 2000000000}
    pl.update(extra)
    w(OUT / f"worldgen/structure_set/{sid}.json", {"structures": ents, "placement": pl})
    print(f"set {sid}: {len(ents)} structure(s), {sp}/{sep}")
