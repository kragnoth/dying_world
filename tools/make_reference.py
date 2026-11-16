#!/usr/bin/env python3
"""
make_reference.py --packwork packwork.zip
Builds reference/ so future chats never need the huge packwork.zip for design work:
  worldgen_reference.zip  all data/*/worldgen (biomes, features, structures, sets, pools, processors, noise...),
                          all data tags, neoforge biome modifiers, lithostitched modifiers, damage types, enchantments
  structures_nbt.zip      all structure .nbt files (13 MB; delete if size matters, keep nbt_index.txt)
  loot_and_recipes.zip    all loot tables + recipes
  lang_en_us.zip          en_us lang per mod (block/item display names)
  blocks_index.json|md    block ids per namespace (from blockstates) + display names
  nbt_index.txt           paths of structure nbt files
Not included: textures/models/sounds/advancements (assets are huge; ask user for a slice if ever needed).
"""
import argparse, json, re, zipfile, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("--packwork", required=True); a = ap.parse_args()
src = zipfile.ZipFile(a.packwork); names = src.namelist()
out = ROOT / "reference"; out.mkdir(exist_ok=True)

def bundle(fname, pred):
    sel = [n for n in names if pred(n)]
    with zipfile.ZipFile(out / fname, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sel: z.writestr(n, src.read(n))
    print(f"{fname:26}{len(sel):7} files {(out / fname).stat().st_size / 1e6:6.1f} MB")
    return sel

D = lambda n: n.startswith("data/")
bundle("worldgen_reference.zip", lambda n: D(n) and re.match(
    r"data/[^/]+/(worldgen|tags|neoforge|lithostitched|damage_type|enchantment|painting_variant)/", n) is not None)
nbt = bundle("structures_nbt.zip", lambda n: D(n) and re.match(r"data/[^/]+/structures?/.+\.nbt$", n))
(out / "nbt_index.txt").write_text("\n".join(sorted(nbt)) + "\n")
bundle("loot_and_recipes.zip", lambda n: D(n) and re.match(r"data/[^/]+/(loot_tables?|recipes?)/", n) is not None)
bundle("lang_en_us.zip", lambda n: re.match(r"assets/[^/]+/lang/en_us\.json$", n) is not None)

# blocks index
blocks = collections.defaultdict(set)
for n in names:
    m = re.match(r"assets/([^/]+)/blockstates/(.+)\.json$", n)
    if m: blocks[m.group(1)].add(m.group(2))
lang = {}
for n in names:
    if re.match(r"assets/[^/]+/lang/en_us\.json$", n):
        try: lang.update(json.loads(src.read(n).decode("utf-8-sig", "replace")))
        except Exception: pass
idx = {ns: sorted(b) for ns, b in sorted(blocks.items())}
(out / "blocks_index.json").write_text(json.dumps(idx))
L = ["# Block ids per namespace (from blockstates; grep this, don't read it all)", "",
     "Format: `namespace (count)` then ids; `id=Name` shown only when en_us name differs from the id.", ""]
for ns, bs in idx.items():
    L.append(f"## {ns} ({len(bs)})")
    items = []
    for b in bs:
        nm = lang.get(f"block.{ns}.{b.replace('/', '.')}")
        pretty = b.replace("_", " ").title()
        items.append(b if not nm or nm.lower() == pretty.lower() else f"{b}={nm}")
    L.append(", ".join(items)); L.append("")
(out / "blocks_index.md").write_text("\n".join(L))
print(f"blocks_index: {sum(len(v) for v in idx.values())} blocks in {len(idx)} namespaces")
