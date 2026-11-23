#!/usr/bin/env python3
"""
export.py - build a CurseForge-importable modpack zip from the repo.
  python3 tools/export.py [version]     ->  dist/Gearwrights_Hollow_<version>.zip
Layout: manifest.json + modlist.html at the root (from modpack/), overrides/ = modpack/overrides with kubejs/data replaced by a fresh
tools/build.py run. Repo notes (PROVENANCE.md, README.txt) are left out. The manifest's mod list is whatever modpack/manifest.json
says: update it by copying in the manifest.json from a CurseForge export after changing mods.
"""
import json, subprocess, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "modpack"
SKIP = {"kubejs/PROVENANCE.md", "kubejs/README.txt"}

def main():
    subprocess.run([sys.executable, str(ROOT / "tools/build.py")], check=True)
    manifest = json.loads((PACK / "manifest.json").read_text())
    version = sys.argv[1] if len(sys.argv) > 1 else manifest.get("version", "dev")
    manifest["version"] = version
    out = ROOT / "dist" / f"Gearwrights_Hollow_{version.replace(' ', '_')}.zip"
    out.parent.mkdir(exist_ok=True)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        z.write(PACK / "modlist.html", "modlist.html")
        for f in sorted((PACK / "overrides").rglob("*")):
            rel = f.relative_to(PACK / "overrides").as_posix()
            if f.is_dir() or rel in SKIP or rel.startswith("kubejs/data/") or ".bak." in f.name:   # (9-86: JEI backups)
                continue
            z.write(f, "overrides/" + rel); n += 1
        with zipfile.ZipFile(ROOT / "dist/kubejs_data.zip") as data:
            for info in data.infolist():
                if not info.is_dir() and info.filename.startswith("data/"):
                    z.writestr("overrides/kubejs/" + info.filename, data.read(info)); n += 1
    print(f"wrote {out} ({n} override files, version {version})")

if __name__ == "__main__":
    main()
