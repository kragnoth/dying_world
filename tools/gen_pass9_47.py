#!/usr/bin/env python3
"""
gen_pass9_47.py - pass 9-47: USER's vision path: everyone STARTS locked in occult_foundry (forceVision back on), killing your copy in
the Hollow keeps it on, the Escapement (creative-recipe item) releases you (/wastelandvision release, Wasteland Vision 0.24.3) and gives
the Foundry Lens, which is then needed to see it again. Reverses 9-46's forceVision=false / startActive=false. Safe to re-run.
"""
import re
from pathlib import Path
CFG = Path(__file__).resolve().parent.parent / "modpack/overrides"

def toml_set(p, key, val):
    s = p.read_text(); n = re.subn(rf"(?m)^{key} = .*$", f"{key} = {val}", s); assert n[1] == 1, (p, key); p.write_text(n[0])

for p in (CFG / "config/wastelandvision-server.toml", CFG / "defaultconfigs/wastelandvision-server.toml"):
    toml_set(p, "forceVision", "true"); toml_set(p, "forcedVision", '"occult_foundry"')
toml_set(CFG / "config/wastelandvision-client.toml", "startActive", "true")
print("9-47: forceVision on (occult_foundry), startActive on")
