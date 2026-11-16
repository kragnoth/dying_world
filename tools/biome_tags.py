"""Resolve biome tags from reference/worldgen_reference.zip (all namespaces, duplicates across mods merged)."""
import json, re, zipfile
from functools import lru_cache
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
WG = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip")
_by = {}
for zi in WG.infolist():
    m = re.match(r"data/([^/]+)/tags/worldgen/biome/(.+)\.json$", zi.filename)
    if m: _by.setdefault(f"{m.group(1)}:{m.group(2)}", []).append(zi)
ALL_BIOMES = sorted({f"{m.group(1)}:{m.group(2)}" for n in WG.namelist() if (m := re.match(r"data/([^/]+)/worldgen/biome/(.+)\.json$", n))})
@lru_cache(None)
def resolve(tag):
    out = set()
    for zi in _by.get(tag, []):
        d = json.loads(re.sub(r"\r", "", WG.read(zi).decode("utf-8")))
        for v in d.get("values", []):
            v = v["id"] if isinstance(v, dict) else v
            out |= resolve(v[1:]) if v.startswith("#") else {v}
    return frozenset(out)
