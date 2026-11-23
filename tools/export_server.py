#!/usr/bin/env python3
"""
export_server.py - build the dedicated-server zip (9-86; was assembled by hand).
  python3 tools/export_server.py [version]   ->  dist/Gearwrights_Hollow_<version>.zip            (client, via export.py)
                                                 dist/Gearwrights_Hollow_Server_<version>.zip     (server)
Server zip = modpack/server/* (start.sh, start.bat, install.ps1, server-mods.txt, README.txt with the version stamped in)
+ config/, defaultconfigs/ and kubejs/ taken from the client export just built, so both always match.
Mods are not in the zip: start.sh / start.bat download server-mods.txt from CurseForge and check each SHA-1.
server-mods.txt itself is still edited by hand after a mod change (see PROGRESS "Commands"); this script checks it against
modpack/manifest.json by project/file ID and stops if an entry isn't in the manifest (stale version), a mod is missing that
isn't in CLIENT_ONLY, or a CLIENT_ONLY mod was added (resource packs = manifest projects modlist.html doesn't list).
"""
import json, re, subprocess, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "modpack"
SERVER = PACK / "server"
# CurseForge project IDs of the mods that crash a dedicated server (left out of server-mods.txt on purpose)
CLIENT_ONLY = {1422344: "Create JEI Compat", 1242344: "Easy Auto Cycler", 394468: "Sodium",
               511319: "Reese's Sodium Options", 1371053: "Saros Boosted Brightness", 557076: "Freecam",
               854213: "Colorful Hearts"}   # Colorful Hearts: client-side HUD only, nothing for a server to load
FROM_CLIENT = ("config/", "defaultconfigs/", "kubejs/")


def check_mod_list():
    """server-mods.txt must equal manifest.json minus CLIENT_ONLY minus resource packs. Resource packs are the manifest
    projects that modlist.html (which lists mods only) doesn't name. Checked by project and file ID, not by count."""
    man = {f["fileID"]: f["projectID"] for f in json.loads((PACK / "manifest.json").read_text())["files"]}
    srv = set()
    for line in (SERVER / "server-mods.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        a, b = re.search(r"/files/(\d+)/(\d+)/", line.split()[1]).groups()
        srv.add(int(a) * 1000 + int(b))
    stale = srv - set(man)
    if stale:
        sys.exit(f"server-mods.txt has {len(stale)} file(s) not in manifest.json (outdated versions?): {sorted(stale)}")
    mods = {int(p) for p in re.findall(r"curseforge\.com/projects/(\d+)", (PACK / "modlist.html").read_text())}
    missing = {man[f] for f in set(man) - srv}
    packs = {p for p in man.values() if p not in mods}
    unexpected = missing - set(CLIENT_ONLY) - packs
    if unexpected:
        sys.exit(f"{len(unexpected)} mod(s) in manifest.json are missing from server-mods.txt (projects {sorted(unexpected)}): "
                 "add them, or to CLIENT_ONLY if they crash a dedicated server")
    shipped = set(CLIENT_ONLY) & {man[f] for f in srv}
    if shipped:
        sys.exit(f"client-only mod(s) {[CLIENT_ONLY[p] for p in shipped]} are in server-mods.txt: they crash a dedicated server")
    print(f"server-mods.txt: {len(srv)} mods, matches manifest.json ({len(missing & set(CLIENT_ONLY))} client-only + "
          f"{len(packs)} resource packs left out)")


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else json.loads((PACK / "manifest.json").read_text()).get("version", "dev")
    check_mod_list()
    subprocess.run([sys.executable, str(ROOT / "tools/export.py"), version], check=True)
    tag = version.replace(" ", "_")
    client = ROOT / "dist" / f"Gearwrights_Hollow_{tag}.zip"
    out = ROOT / "dist" / f"Gearwrights_Hollow_Server_{tag}.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z, zipfile.ZipFile(client) as c:
        for f in sorted(SERVER.iterdir()):
            if not f.is_file():
                continue
            if f.name == "README.txt":
                text = re.sub(r"\(\d[^)]*\)", f"({version})", f.read_text(), count=1)   # "server files (1.0.3 Alpha)"
                z.writestr(f.name, text)
            else:
                info = zipfile.ZipInfo(f.name)
                info.external_attr = (0o755 if f.suffix == ".sh" else 0o644) << 16   # start.sh stays executable
                z.writestr(info, f.read_bytes(), zipfile.ZIP_DEFLATED)
            n += 1
        for info in c.infolist():
            rel = info.filename[len("overrides/"):] if info.filename.startswith("overrides/") else None
            # mods/: jars that aren't on CurseForge ship in overrides/mods (9-89); the start scripts only remove jars they
            # installed themselves, so these stay put
            if rel and not info.is_dir() and (rel.startswith(FROM_CLIENT) or (rel.startswith("mods/") and rel.endswith(".jar"))):
                z.writestr(rel, c.read(info)); n += 1
    print(f"wrote {out} ({n} files, version {version})")


if __name__ == "__main__":
    main()
