#!/usr/bin/env python3
"""
split_data.py - pass 8-1: cleanly separate STRUCTURES from the user's kubejs/data.

usage: python3 tools/split_data.py <user_data_dir (contains data/)> <out_dir>
Writes 3 zips to out_dir:
  1. dying_world_structures_datapack.zip  = our build (datapack/) + every structure file from the user's data that OUR structures
     use (closure walk: structure -> pools -> NBT jigsaw pools -> processors -> biome tags), + disabled structure-set overrides,
     + PROVENANCE.md (per structure: where each piece comes from: OWN / KUBEJS-DATA:<ns> / EXTERNAL (vanilla or mod jar)).
  2. data_without_structures.zip         = user's data/ minus every structure-category file and minus our namespace/overrides.
  3. unused_structures_archive.zip       = structure-category files from the user's data that nothing of ours uses (nothing lost).
Structure categories: structure/ (NBT), worldgen/{structure,structure_set,template_pool,processor_list}/, tags/worldgen/{structure,biome/has_structure}/.
Loot tables, placed features etc. stay in data (reported if a moved piece points at them).
"""
import gzip, io, json, os, re, sys, zipfile
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OURS = ROOT / "datapack/data"
CATS = ("structure/", "worldgen/structure/", "worldgen/structure_set/", "worldgen/template_pool/", "worldgen/processor_list/",
        "tags/worldgen/structure/", "tags/worldgen/biome/has_structure/")
IDRE = re.compile(r"^#?[a-z0-9_.-]+:[a-z0-9_./-]+$")
KINDS = [("worldgen/template_pool", ".json"), ("worldgen/processor_list", ".json"), ("structure", ".nbt"),
         ("worldgen/structure", ".json"), ("tags/worldgen/biome", ".json"), ("worldgen/placed_feature", ".json"), ("loot_table", ".json")]

def files(base):
    return {str(Path(d, f).relative_to(base)).replace(os.sep, "/") for d, _, fs in os.walk(base) for f in fs}

def is_struct(rel):
    s = rel.split("/", 1)[1] if "/" in rel else ""
    return any(s.startswith(c) for c in CATS)

def main(user, out, structures_only=False):
    UD = Path(user) / "data"; out = Path(out); out.mkdir(parents=True, exist_ok=True)
    ours, theirs = files(OURS), files(UD)
    def where(rel): return "OURS" if rel in ours else "DATA" if rel in theirs else None
    def read(rel): return ((OURS if rel in ours else UD) / rel).read_bytes()
    def cand(i):
        tag = i.startswith("#"); ns, p = i.lstrip("#").split(":", 1)
        for k, ext in KINDS:
            if tag != (k.startswith("tags")): continue
            rel = f"{ns}/{k}/{p}{ext}"
            if where(rel): yield rel
    def strings(o, key=None):
        if isinstance(o, str): yield (key, o)
        elif isinstance(o, dict):
            for k, v in o.items(): yield from strings(v, k)
        elif isinstance(o, list):
            for v in o: yield from strings(v, key)
    def nbt_refs(raw):
        d = gzip.decompress(raw); out = set()
        for m in re.finditer(rb"[#a-z0-9_.-]+:[a-z0-9_./-]+", d):     # NBT strings are length-prefixed: trust the prefix
            b, e = m.start(), m.end()
            for st in range(b, min(b + 3, e)):
                if st >= 2 and int.from_bytes(d[st - 2:st], "big") == e - st:
                    s = d[st:e].decode()
                    if IDRE.match(s): out.add(s)
                    break
        return out
    # ---- closure from every OUR structure + structure set
    # 8-11: walk from EVERY structure-category file of ours (not only structures): pools we override (e.g. minecraft:village/snowy/houses) can be
    # reachable only through vanilla jar NBTs (vanilla streets) that this walk cannot open.
    start = [r for r in ours if is_struct(r) and (r.endswith(".json") or r.endswith(".nbt"))]
    seen, stack, owner, edges = set(), list(start), {}, defaultdict(set)
    external = defaultdict(set); loot_refs = set(); feat_refs = set()
    for r in start: owner[r] = r
    while stack:
        rel = stack.pop()
        if rel in seen: continue
        seen.add(rel)
        raw = read(rel)
        if rel.endswith(".nbt"): refs = {(None, i) for i in nbt_refs(raw)}
        else: refs = {(k, v) for k, v in strings(json.loads(raw)) if IDRE.match(v)}
        for key, i in refs:
            hits = list(cand(i))
            if not hits:
                pathlike = "/" in i or i.startswith("#") or key in ("start_pool", "location", "structure", "pool", "fallback", "processors")
                if pathlike and i != "minecraft:empty" and ":chests/" not in i and "/chests/" not in i:
                    external[i].add(owner.get(rel, rel))                # NBT: only path-like ids (pools), not block names
                continue
            for h in hits:
                if "/loot_table/" in h: loot_refs.add(h); continue
                if "/placed_feature/" in h: feat_refs.add(h); continue
                edges[rel].add(h)
                if h not in seen: owner.setdefault(h, owner.get(rel, rel)); stack.append(h)
    used = {r for r in seen if r in theirs and r not in ours and is_struct(r)}
    # disabled structure-set overrides in data that are not ours (keep the 'off' switch with the structures)
    disables, archive = set(), set()
    for r in theirs:
        if r in ours or r in used or not is_struct(r) or r.startswith("dying_world/"): continue
        if "/worldgen/structure_set/" in r:
            try:
                j = json.loads((UD / r).read_bytes())
                if not j.get("structures"): disables.add(r); continue
            except Exception: pass
        archive.add(r)
    stale_ours = {r for r in theirs if r.startswith("dying_world/") and r not in ours}
    archive |= {r for r in stale_ours if is_struct(r)}
    removed_dup = {r for r in theirs if r in ours}                     # our files (current build wins)
    keep_data = {r for r in theirs if not is_struct(r) and r not in ours and not r.startswith("dying_world/")}
    stale_nonstruct = {r for r in stale_ours if not is_struct(r)}
    # ---- zip 1
    z1 = out / "dying_world_structures_datapack.zip"
    with zipfile.ZipFile(z1, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT / "datapack/pack.mcmeta", "pack.mcmeta")
        for r in sorted(ours): z.write(OURS / r, "data/" + r)
        for r in sorted(used | disables): z.write(UD / r, "data/" + r)
        z.writestr("PROVENANCE.md", provenance(ours, used, disables, start, edges, external))
    if structures_only:                                           # build mode: input = datapack_imported (only the moved files)
        with zipfile.ZipFile(out / "unused_structures_archive.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for r in sorted(archive): z.write(UD / r, "data/" + r)
        print(f"structures zip: {len(ours)} own + {len(used)} imported files; {len(archive)} imported files no longer used -> archive")
        return
    with zipfile.ZipFile(out / "data_without_structures.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for r in sorted(keep_data | stale_nonstruct): z.write(UD / r, "data/" + r)
    with zipfile.ZipFile(out / "unused_structures_archive.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for r in sorted(archive): z.write(UD / r, "data/" + r)
        z.writestr("ARCHIVE.md", "# Unused structure files from kubejs/data (pass 8-1)\nNothing in the dying_world build references these. Kept so nothing is lost.\n\n"
                   + "\n".join(f"- {k}: {v}" for k, v in Counter(r.split('/')[0] + ' ' + cat(r) for r in archive).most_common()) + "\n")
    # sanity: every user data file accounted for exactly once
    acc = used | disables | archive | removed_dup | keep_data | stale_nonstruct
    assert acc == theirs, (len(acc), len(theirs), list(theirs - acc)[:5])
    rep = {"user_files": len(theirs), "ours_in_build": len(ours), "moved_into_structures_zip": len(used), "disabled_set_overrides_moved": len(disables),
           "archived": len(archive), "removed_as_our_files": len(removed_dup), "stale_ours_nonstructure_kept_in_data": len(stale_nonstruct),
           "kept_in_data": len(keep_data), "external_ids": len(external), "loot_tables_used_by_structures_in_data": sorted(r for r in loot_refs if r in theirs and r not in ours)[:999],
           "placed_features_used_in_data": sorted(r for r in feat_refs if r in theirs)}
    (out / "split_report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if not isinstance(v, list)}, indent=1))
    print("loot tables in data used by structures:", len(rep["loot_tables_used_by_structures_in_data"]), "| placed features:", len(rep["placed_features_used_in_data"]))

def cat(r):
    s = r.split("/", 1)[1]
    for c in CATS:
        if s.startswith(c): return c.rstrip("/")
    return "other"

def provenance(ours, used, disables, start, edges, external):
    ext = defaultdict(set)
    for i, ows in external.items():
        for o in ows: ext[o].add(i)
    L = ["# PROVENANCE - dying_world structures datapack (pass 8-1)", "",
         "Every structure in this zip and where its NBT pieces come from (per structure, full jigsaw closure). Nothing removed; use this to pick what to replace with our own builds.",
         "- OWN = dying_world namespace (script-built, or our generators' copies such as worn village houses - see PROGRESS.md / docs/provenance_audit.md for their sources).",
         "- KUBEJS-DATA:<ns> = moved here from kubejs/data (gearwrights, brutos, vsrevamped, the custom minecraft:village house sets...). Mark which are yours.",
         "- EXTERNAL = pools/tags/types loaded from a mod jar or vanilla at runtime (not in this zip; that mod must stay installed while the structure is used).", "",
         "| structure | NBT pieces by source | external pools/tags/types |", "|---|---|---|"]
    for st in sorted(r for r in start if "/worldgen/structure/" in r and r.startswith("dying_world/")):
        seen, stack, cnt, ex = set(), [st], Counter(), set(ext.get(st, ()))
        while stack:
            r = stack.pop()
            if r in seen: continue
            seen.add(r); ex |= ext.get(r, set()); stack += list(edges.get(r, ()))
            if r.endswith(".nbt"): cnt["OWN" if r.startswith("dying_world/") else ("KUBEJS-DATA:" + r.split("/")[0]) if r in used else ("BUILD:" + r.split("/")[0])] += 1
        p = ", ".join(f"{k} {v}" for k, v in cnt.most_common()) or "-"
        e = sorted(ex)
        L.append(f"| `{st.split('/worldgen/structure/')[1][:-5]}` | {p} | {', '.join(e[:5])}{f' (+{len(e) - 5})' if len(e) > 5 else ''} |")
    L += ["", f"Moved from kubejs/data: {len(used)} files; disabled structure-set overrides moved: {len(disables)}.",
          "Loot tables / placed features stay in data_without_structures (some pieces point at them; install both zips)."]
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
