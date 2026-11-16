#!/usr/bin/env python3
"""
packwork.py - collect every data/asset file from a Minecraft modpack into one zip.

Place this in the instance's `minecraft` folder (the one containing `mods/`,
`config/`, etc.) and run:

    python3 packwork.py                # -> packwork.zip
    python3 packwork.py --textures     # also include png/ogg/etc.
    python3 packwork.py --mc-jar /path/to/minecraft-1.21.1-client.jar

What gets scanned (in override order, later wins):
  1. The vanilla Minecraft client jar (found via Prism's mmc-pack.json)
  2. Every .jar in mods/ (recursively), including jar-in-jar nested jars
  3. Extra pack locations: kubejs/, datapacks/, resourcepacks/, global_packs/,
     config/openloader/, config/paxi/, saves/*/datapacks/

What gets extracted:
  - everything under data/   (recipes, loot tables, structures .nbt, worldgen,
                              tags, advancements, functions, ...)
  - text-ish files under assets/ (models, blockstates, lang, ...)
  - with --textures: binary assets too (png, ogg, ...)
  - mod metadata files (mods.toml, fabric.mod.json, ...) under _sources/<jar>/

Tag files (data/*/tags/**.json) are merged across sources instead of overwritten.
A _packwork_report.json is written into the zip with sources, counts and overrides.
A human-readable _packwork_sources.md is written too: which jars were extracted,
which ones ship data for other mods' namespaces (built-in compat), compat-looking
folders, and a namespace -> provider index.
"""

import argparse
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

TEXT_ASSET_EXT = {
    ".json", ".mcmeta", ".lang", ".txt", ".properties", ".toml", ".cfg",
    ".fsh", ".vsh", ".glsl", ".csv", ".xml", ".yml", ".yaml", ".md",
}
BINARY_ASSET_EXT = {
    ".png", ".ogg", ".wav", ".mp3", ".ttf", ".otf", ".bin", ".nbt",
    ".bbmodel", ".obj", ".mtl", ".gif", ".jpg", ".jpeg", ".ttc",
}
META_FILES = {
    "fabric.mod.json", "quilt.mod.json", "mcmod.info", "pack.mcmeta",
    "META-INF/mods.toml", "META-INF/neoforge.mods.toml",
}
TAG_RE = re.compile(r"^data/[^/]+/tags/.+\.json$")
MAX_NEST = 3

# generated pack.mcmeta values for 1.21.1
PACK_FORMAT_DATA = 48
PACK_FORMAT_RESOURCE = 34

CATEGORIES = {
    "recipes": re.compile(r"^data/[^/]+/recipes?/.+\.json$"),
    "loot tables": re.compile(r"^data/[^/]+/loot_tables?/.+\.json$"),
    "structures (nbt)": re.compile(r"^data/[^/]+/structures?/.+\.(nbt|snbt)$"),
    "tags": TAG_RE,
    "worldgen": re.compile(r"^data/[^/]+/worldgen/.+"),
    "advancements": re.compile(r"^data/[^/]+/advancements?/.+"),
    "functions": re.compile(r"^data/[^/]+/functions?/.+"),
    "models": re.compile(r"^assets/[^/]+/models/.+"),
    "blockstates": re.compile(r"^assets/[^/]+/blockstates/.+"),
    "lang": re.compile(r"^assets/[^/]+/lang/.+"),
    "textures": re.compile(r"^assets/[^/]+/textures/.+"),
}


class Collector:
    def __init__(self, textures: bool, include_assets: bool):
        self.textures = textures
        self.include_assets = include_assets
        self.files = {}                      # zip path -> bytes
        self.owners = defaultdict(list)      # zip path -> [source labels]
        self.meta = {}                       # zip path -> bytes
        self.sources = []                    # (label, files_taken)
        self.source_files = defaultdict(list)    # label -> [zip paths it provided]
        self.meta_by_label = defaultdict(dict)   # label -> {meta filename: bytes}
        self.roles = {}                          # label -> vanilla|mod|nested|extra

    # ---- filtering -------------------------------------------------------
    def wanted(self, name: str) -> bool:
        if ".." in name.split("/") or name.startswith("/"):
            return False
        if name.startswith("data/"):
            return True
        if name.startswith("assets/") and self.include_assets:
            ext = Path(name).suffix.lower()
            if ext in TEXT_ASSET_EXT:
                return True
            if self.textures and ext in BINARY_ASSET_EXT:
                return True
        return False

    # ---- adding ----------------------------------------------------------
    def add(self, name: str, data: bytes, label: str):
        self.source_files[label].append(name)
        if name in self.files:
            self.owners[name].append(label)
            if TAG_RE.match(name):
                merged = merge_tags(self.files[name], data)
                if merged is not None:
                    self.files[name] = merged
                    return
            self.files[name] = data  # last wins
        else:
            self.files[name] = data
            self.owners[name].append(label)

    def ingest(self, entries, label: str, depth: int = 0):
        taken = 0
        for name, reader in entries:
            if name.endswith("/"):
                continue
            if self.wanted(name):
                try:
                    self.add(name, reader(), label)
                    taken += 1
                except Exception as e:  # corrupt entry
                    print(f"  ! {label}: could not read {name}: {e}", file=sys.stderr)
            elif name in META_FILES:
                content = reader()
                self.meta[f"_sources/{label}/{name}"] = content
                self.meta_by_label[label][name] = content
            elif (depth < MAX_NEST and name.startswith("META-INF/")
                  and name.lower().endswith(".jar")):
                try:
                    nested = zipfile.ZipFile(io.BytesIO(reader()))
                    nlabel = f"{label}!{Path(name).name}"
                    self.roles[nlabel] = "nested"
                    taken += self.ingest(zip_entries(nested), nlabel, depth + 1)
                except Exception as e:
                    print(f"  ! {label}: bad nested jar {name}: {e}", file=sys.stderr)
        self.sources.append((label, taken))
        return taken


def merge_tags(old: bytes, new: bytes):
    """Merge two tag JSONs; honours 'replace': true. Returns None on parse failure."""
    try:
        a, b = json.loads(old), json.loads(new)
        if b.get("replace"):
            return new
        seen, values = set(), []
        for v in list(a.get("values", [])) + list(b.get("values", [])):
            key = json.dumps(v, sort_keys=True)
            if key not in seen:
                seen.add(key)
                values.append(v)
        out = dict(a)
        out["values"] = values
        return json.dumps(out, indent=2).encode()
    except Exception:
        return None


def zip_entries(zf: zipfile.ZipFile):
    for info in zf.infolist():
        if not info.is_dir():
            yield info.filename, (lambda i=info: zf.read(i))


def dir_entries(root: Path):
    for p in root.rglob("*"):
        if p.is_file():
            yield p.relative_to(root).as_posix(), (lambda q=p: q.read_bytes())


# ---- source report (markdown) ------------------------------------------------

SHARED_NS = {"minecraft", "c", "forge", "neoforge", "fabric", "common", "conventions"}
COMPAT_WORDS = {"compat", "compatibility", "integration", "integrations", "mod_compat", "modcompat"}


def extract_ids(meta: dict) -> set:
    """Pull mod ids out of fabric/quilt/forge/neoforge metadata files."""
    ids = set()
    for name, data in meta.items():
        text = data.decode("utf-8", "replace")
        if name == "fabric.mod.json":
            try:
                j = json.loads(text, strict=False)
                ids.add(j["id"])
                for p in j.get("provides", []):
                    ids.add(p if isinstance(p, str) else p.get("id"))
            except Exception:
                m = re.search(r'"id"\s*:\s*"([^"]+)"', text)
                if m:
                    ids.add(m.group(1))
        elif name == "quilt.mod.json":
            try:
                ids.add(json.loads(text, strict=False)["quilt_loader"]["id"])
            except Exception:
                pass
        elif name.endswith("mods.toml"):
            ids.update(re.findall(r'^\s*modId\s*=\s*["\']([^"\']+)["\']', text, re.M))
        elif name == "mcmod.info":
            ids.update(re.findall(r'"modid"\s*:\s*"([^"]+)"', text, re.I))
    ids.discard(None)
    return ids


def split_path(name: str):
    parts = name.split("/")
    ns = parts[1] if len(parts) > 2 else None
    kind = parts[2] if len(parts) > 3 else ""
    return ns, kind


def build_markdown(col: Collector, version, overrides: dict) -> str:
    ids_by_label = {l: extract_ids(m) for l, m in col.meta_by_label.items()}
    for l, role in col.roles.items():
        if role == "vanilla":
            ids_by_label[l] = {"minecraft"}
    all_ids = set().union(*ids_by_label.values()) if ids_by_label else set()
    taken = dict(col.sources)

    ns_index = defaultdict(Counter)                   # ns -> label -> count
    foreign = defaultdict(lambda: defaultdict(list))  # label -> ns -> [paths]
    shared = defaultdict(Counter)                     # label -> ns -> count
    compat = defaultdict(Counter)                     # label -> folder prefix -> count

    for label, paths in col.source_files.items():
        own = ids_by_label.get(label, set())
        role = col.roles.get(label, "mod")
        for p in paths:
            ns, _ = split_path(p)
            if ns is None:
                continue
            ns_index[ns][label] += 1
            if role not in ("mod", "nested") or not own:
                continue
            if ns in own:
                parts = p.split("/")
                others = all_ids - own
                for i in range(3, len(parts) - 1):  # directory segments only
                    seg = parts[i].lower()
                    if (seg in COMPAT_WORDS or seg.startswith("compat")
                            or (len(seg) >= 3 and seg in others)):
                        compat[label]["/".join(parts[:i + 1]) + "/"] += 1
                        break
            elif ns in SHARED_NS:
                shared[label][ns] += 1
            else:
                foreign[label][ns].append(p)

    def title(label):
        ids = sorted(ids_by_label.get(label, ()))
        return f"{label} (`{', '.join(ids)}`)" if ids else label

    L = []
    w = L.append
    w("# packwork source report")
    w("")
    w(f"- Generated: {datetime.now():%Y-%m-%d %H:%M}")
    w(f"- Minecraft version: {version or 'unknown'}")
    w(f"- Total files in zip: {len(col.files)}")
    w(f"- Sources scanned: {len(col.sources)} "
      f"({sum(1 for _, n in col.sources if n)} contributed files)")
    w("")
    w("## How to use this")
    w("")
    w("A mod jar sometimes ships data meant for *another* mod (built-in compat). "
      "Sections 2 and 3 flag those so you can ignore those folders if you are "
      "supplying the compat yourself. Section 2 = a jar providing a namespace that "
      "is not its own. Section 3 = folders inside a jar's own namespace whose names "
      "look like compat (`compat/`, `integration/`, or another loaded mod's id). "
      "These are heuristics: check the sample paths before ignoring anything.")
    w("")

    # 1. extracted sources
    w("## 1. Extracted sources")
    w("")
    w("| Source | Role | Files taken |")
    w("|---|---|---|")
    for label, n in col.sources:
        if n:
            w(f"| {title(label)} | {col.roles.get(label, 'mod')} | {n} |")
    empty = [l for l, n in col.sources if not n]
    if empty:
        w("")
        w(f"Scanned, but contained no data/asset files ({len(empty)}): "
          + ", ".join(sorted(empty)))
    w("")

    # 2. foreign namespace
    w("## 2. Jars shipping data for another mod's namespace (likely built-in compat)")
    w("")
    if not foreign:
        w("None detected.")
    for label in sorted(foreign):
        w(f"### {title(label)}")
        for ns in sorted(foreign[label]):
            paths = foreign[label][ns]
            kinds = Counter(split_path(p)[1] or "(root)" for p in paths)
            kind_txt = ", ".join(f"`{k}` x{c}" for k, c in kinds.most_common())
            w(f"- `{ns}`: {len(paths)} files ({kind_txt})")
            for s in sorted(paths)[:3]:
                w(f"  - e.g. `{s}`")
        w("")

    # 3. compat folders in own namespace
    w("## 3. Compat-looking folders inside a mod's own namespace")
    w("")
    if not compat:
        w("None detected.")
    for label in sorted(compat):
        w(f"### {title(label)}")
        for prefix, c in sorted(compat[label].items()):
            w(f"- `{prefix}`: {c} files")
        w("")

    # 4. shared namespaces
    w("## 4. Contributions to shared namespaces (minecraft, c, forge, ...)")
    w("")
    w("Usually legitimate (tags, loot injection, etc.), listed for completeness.")
    w("")
    if shared:
        w("| Source | Namespace | Files |")
        w("|---|---|---|")
        for label in sorted(shared):
            for ns, c in sorted(shared[label].items()):
                w(f"| {title(label)} | `{ns}` | {c} |")
    else:
        w("None detected.")
    w("")

    # 5. overrides
    w("## 5. Paths provided by more than one source")
    w("")
    w("Order is load order; the last source wins (tag files are merged instead).")
    w("")
    items = sorted(overrides.items())
    for path, owners in items[:300]:
        tag = " (merged)" if TAG_RE.match(path) else ""
        w(f"- `{path}`{tag}: " + " -> ".join(owners))
    if len(items) > 300:
        w(f"- ... and {len(items) - 300} more (full list in `_packwork_report.json`)")
    if not items:
        w("None.")
    w("")

    # 6. namespace index
    w("## 6. Namespace -> providing sources")
    w("")
    for ns in sorted(ns_index):
        provs = ", ".join(f"{l} ({c})" for l, c in ns_index[ns].most_common())
        w(f"- `{ns}`: {provs}")
    w("")
    return "\n".join(L)


# ---- locating things -------------------------------------------------------

def find_mc_version(base: Path):
    for cand in (base.parent / "mmc-pack.json", base / "mmc-pack.json"):
        if cand.exists():
            try:
                for comp in json.loads(cand.read_text())["components"]:
                    if comp.get("uid") == "net.minecraft":
                        return comp.get("version")
            except Exception:
                pass
    return None


def find_mc_jar(base: Path, version):
    data_dirs = []
    # <data>/instances/<name>/minecraft  ->  <data>
    if len(base.resolve().parents) >= 3:
        data_dirs.append(base.resolve().parents[2])
    home = Path.home()
    data_dirs += [
        home / ".local/share/PrismLauncher",
        home / ".var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher",
        home / ".minecraft",
    ]
    for d in data_dirs:
        if not d.exists():
            continue
        if version:
            for rel in (
                f"libraries/com/mojang/minecraft/{version}/minecraft-{version}-client.jar",
                f"versions/{version}/{version}.jar",
            ):
                if (d / rel).exists():
                    return d / rel
        # fallback: any minecraft client jar in libraries
        lib = d / "libraries/com/mojang/minecraft"
        if lib.exists():
            hits = sorted(lib.rglob("minecraft-*-client.jar"))
            if version:
                hits = [h for h in hits if version in h.as_posix()] or hits
            if hits:
                return hits[-1]
    return None


def extra_sources(base: Path):
    """Yield (label, kind, path) for datapack/resourcepack-like locations."""
    roots = [
        "kubejs", "datapacks", "resourcepacks", "global_packs/required_data",
        "global_packs/required_resources", "config/openloader/data",
        "config/openloader/resources", "config/paxi/datapacks",
        "config/paxi/resourcepacks",
    ]
    paths = [base / r for r in roots]
    paths += list(base.glob("saves/*/datapacks"))
    for p in paths:
        if not p.is_dir():
            continue
        rel = p.relative_to(base).as_posix()
        if (p / "data").is_dir() or (p / "assets").is_dir():
            yield rel, "dir", p
        for child in sorted(p.iterdir()):
            if child.is_dir() and ((child / "data").is_dir() or (child / "assets").is_dir()):
                yield f"{rel}/{child.name}", "dir", child
            elif child.is_file() and child.suffix.lower() == ".zip":
                yield f"{rel}/{child.name}", "zip", child


def ingest_path(col: Collector, label: str, kind: str, path: Path):
    try:
        if kind == "dir":
            col.ingest(dir_entries(path), label)
        else:
            with zipfile.ZipFile(path) as zf:
                col.ingest(zip_entries(zf), label)
    except zipfile.BadZipFile:
        print(f"  ! skipping bad archive: {path}", file=sys.stderr)


# ---- main ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", default="packwork.zip")
    ap.add_argument("--base", default=None, help="instance minecraft folder (default: folder containing this script)")
    ap.add_argument("--mc-jar", default=None, help="path to the vanilla client jar")
    ap.add_argument("--no-vanilla", action="store_true", help="skip the Minecraft jar")
    ap.add_argument("--no-extras", action="store_true", help="skip kubejs/datapacks/resourcepacks/etc.")
    ap.add_argument("--textures", action="store_true", help="include binary assets (png, ogg, ...)")
    ap.add_argument("--data-only", action="store_true", help="only data/, skip assets/")
    args = ap.parse_args()

    base = Path(args.base).resolve() if args.base else Path(__file__).resolve().parent
    out = Path(args.output)
    if not out.is_absolute():
        out = base / out

    version = find_mc_version(base)
    print(f"Instance folder : {base}")
    print(f"Minecraft ver   : {version or 'unknown'}")

    col = Collector(textures=args.textures, include_assets=not args.data_only)

    # 1. vanilla
    if not args.no_vanilla:
        jar = Path(args.mc_jar) if args.mc_jar else find_mc_jar(base, version)
        if jar and jar.exists():
            print(f"Vanilla jar     : {jar}")
            vlabel = f"minecraft-{version or 'vanilla'}"
            col.roles[vlabel] = "vanilla"
            ingest_path(col, vlabel, "zip", jar)
        else:
            print("! Could not find the Minecraft jar. Use --mc-jar /path/to/client.jar", file=sys.stderr)

    # 2. mods
    mods_dir = base / "mods"
    jars = sorted(mods_dir.rglob("*.jar")) if mods_dir.is_dir() else []
    print(f"Mod jars found  : {len(jars)}")
    for i, jar in enumerate(jars, 1):
        print(f"  [{i}/{len(jars)}] {jar.name}", end="\r", flush=True)
        col.roles[jar.stem] = "mod"
        ingest_path(col, jar.stem, "zip", jar)
    if jars:
        print()

    # 3. extras
    if not args.no_extras:
        for label, kind, path in extra_sources(base):
            print(f"Extra source    : {label}")
            col.roles[label] = "extra"
            ingest_path(col, label, kind, path)

    if not col.files:
        sys.exit("Nothing extracted - is this the right folder?")

    # stats
    counts = Counter()
    for name in col.files:
        for cat, rx in CATEGORIES.items():
            if rx.match(name):
                counts[cat] += 1
    overrides = {n: o for n, o in col.owners.items() if len(o) > 1}

    report = {
        "minecraft_version": version,
        "total_files": len(col.files),
        "categories": dict(counts),
        "sources": [{"name": n, "files": c} for n, c in col.sources],
        "overridden_or_merged": {n: o for n, o in sorted(overrides.items())},
    }

    # write
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        pack = {"pack": {"pack_format": PACK_FORMAT_DATA,
                         "description": "packwork - merged modpack data/assets"}}
        if not args.data_only:
            pack["pack"]["supported_formats"] = [min(PACK_FORMAT_DATA, PACK_FORMAT_RESOURCE),
                                                 max(PACK_FORMAT_DATA, PACK_FORMAT_RESOURCE)]
        zf.writestr("pack.mcmeta", json.dumps(pack, indent=2))
        for name in sorted(col.files):
            if name == "pack.mcmeta":
                continue
            zf.writestr(name, col.files[name])
        for name in sorted(col.meta):
            zf.writestr(name, col.meta[name])
        zf.writestr("_packwork_report.json", json.dumps(report, indent=2))
        zf.writestr("_packwork_sources.md", build_markdown(col, version, overrides))

    size = out.stat().st_size / (1024 * 1024)
    print(f"\nWrote {out}  ({size:.1f} MiB, {len(col.files)} files)")
    for cat, n in counts.most_common():
        print(f"  {cat:<18} {n}")
    print(f"  paths provided by >1 source: {len(overrides)} (see _packwork_report.json)")


if __name__ == "__main__":
    main()
