#!/usr/bin/env python3
"""build.py - validate, then zip datapack/ -> dist/dying_world_datapack.zip"""
import subprocess, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
# 9-30: the user's hand edits (user_overrides/data) always win over generator output -> copied into datapack/ before validation
import shutil
_uo = ROOT / "user_overrides/data"
if _uo.is_dir():
    for f in sorted(_uo.rglob("*")):
        if f.is_file():
            d = ROOT / "datapack/data" / f.relative_to(_uo); d.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(f, d)
if subprocess.call([sys.executable, str(ROOT / "tools/validate.py")] + sys.argv[1:]):
    sys.exit("validation failed")
out = ROOT / "dist/dying_world_datapack.zip"; out.parent.mkdir(exist_ok=True)
for old in out.parent.glob("*.zip"): old.unlink()   # (dist/split, dist/release subfolders untouched)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted((ROOT / "datapack").rglob("*")):
        if f.is_file(): z.write(f, f.relative_to(ROOT / "datapack").as_posix())
print("built", out)
# 8-2: full structures datapack = our build + structure files imported from the user's kubejs/data (datapack_imported/, see PROGRESS 8-1)
if (ROOT / "datapack_imported/data").is_dir():
    sys.path.insert(0, str(ROOT / "tools")); import split_data
    split_data.main(str(ROOT / "datapack_imported"), str(ROOT / "dist"), structures_only=True)
    print("built", ROOT / "dist/dying_world_structures_datapack.zip")

# 8-7: ONE zip for testing = the whole kubejs/data folder: kubejs_base/data (user's non-structure data, from 8-1) + the structures datapack
base = ROOT / "kubejs_base/data"; sz = ROOT / "dist/dying_world_structures_datapack.zip"
if base.is_dir() and sz.exists():
    out = ROOT / "dist/kubejs_data.zip"; seen = set()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z, zipfile.ZipFile(sz) as s:
        for n in s.namelist():
            if n.startswith("data/"): z.writestr(n, s.read(n)); seen.add(n)
        for f in sorted(base.rglob("*")):
            if f.is_file():
                n = "data/" + f.relative_to(base).as_posix()
                if n in seen: sys.exit(f"conflict between kubejs_base and structures: {n}")
                z.write(f, n)
        z.writestr("PROVENANCE.md", s.read("PROVENANCE.md"))
        z.writestr("README.txt", "Replace kubejs/data with the data/ folder from this zip (move the old one away first). Nothing else needed.\n")
    print("built", out)
