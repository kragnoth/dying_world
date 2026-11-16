#!/usr/bin/env python3
"""
furniture_scan.py - pass 7-0. Scan every village house NBT in reference/structures_nbt.zip and catalogue how FURNITURE is built.
  python3 tools/furniture_scan.py            -> docs/furniture_catalog.md + docs/furniture_patterns.json + docs/house_palettes.md
Method: furniture blocks (fences, trapdoors, plates, carpets, lights, job blocks, containers, beds...) are grouped into small 6-connected clusters;
free-standing stairs/slabs (air above) join a cluster when touching it. Each cluster is reduced to a rotation/mirror-invariant pattern with wood
names -> W_ and colours -> C_, then counted across houses. Categories: bed, workstation, shelf, storage, table, seat, light, plant, decor, other.
"""
import collections, gzip, io, json, re, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtmini

ROOT = Path(__file__).resolve().parent.parent
WOOD = re.compile(r"^(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|bamboo|crimson|warped|pale_oak)_")
COL = re.compile(r"^(white|orange|magenta|light_blue|yellow|lime|pink|gray|light_gray|cyan|purple|blue|brown|green|red|black)_")
JOBS = {"smoker", "blast_furnace", "cartography_table", "fletching_table", "smithing_table", "grindstone", "stonecutter", "loom", "brewing_stand",
        "cauldron", "composter", "lectern", "barrel", "furnace", "crafting_table", "anvil", "enchanting_table", "bell"}
SEED = re.compile(r"(fence$|fence_gate$|trapdoor$|pressure_plate$|_button$|sign$|carpet$|lantern$|torch$|candle|flower_pot|^potted_|barrel$|chest$|bed$|bookshelf|"
                  r"campfire$|cake$|jukebox|banner$|decorated_pot|^chain$|end_rod|skull$|head$|^hay_block$)")
SKIP_DIR = ("/streets/", "/terminators/", "/villagers/", "/animals/", "/cats/", "iron_golem", "/town_centers/")


def norm(name, props):
    n = name.split(":", 1)[1] if name.startswith("minecraft:") else name
    n = WOOD.sub("W_", n); n = COL.sub("C_", n)
    if n.endswith("_stairs"): n += ":" + props.get("half", "bottom")
    elif n.endswith("_slab"): n += ":" + props.get("type", "bottom")
    elif n.endswith("_trapdoor"): n += ":" + props.get("half", "bottom") + (":open" if props.get("open") == "true" else "")
    elif n.endswith("_bed") or n == "C_bed": n = "C_bed"
    return n


def base(n): return n.split(":")[0]


def canon(cells):
    best = None
    pts = list(cells)
    for mirror in (False, True):
        for rot in range(4):
            q = []
            for (x, y, z, n) in pts:
                if mirror: x = -x
                for _ in range(rot): x, z = z, -x
                q.append((x, y, z, n))
            mx, my, mz = min(a[0] for a in q), min(a[1] for a in q), min(a[2] for a in q)
            sig = tuple(sorted((n, x - mx, y - my, z - mz) for x, y, z, n in q))
            if best is None or sig < best: best = sig
    return best


def classify(names):
    b = {base(n) for n in names}
    has = lambda *ks: any(any(k in x for x in b) for k in ks)
    if has("_bed", "C_bed"): return "bed"
    if any(x in JOBS for x in b) and not (b <= {"barrel"} and len(names) > 1): return "workstation"
    if has("bookshelf"): return "shelf"
    if has("barrel", "chest", "decorated_pot"): return "storage"
    if has("fence") and has("pressure_plate", "_slab", "carpet", "trapdoor", "_button", "stairs"): return "table"
    if has("stairs", "trapdoor", "sign", "_slab"): return "seat"
    if has("lantern", "torch", "candle", "campfire", "end_rod", "chain"): return "light"
    if has("flower_pot", "potted_"): return "plant"
    if has("banner", "cake", "jukebox", "skull", "head", "hay_block"): return "decor"
    return "other"


def scan_house(data):
    d = nbtmini.parse(gzip.decompress(data))
    pal = d["palette"]
    meta = [(p["Name"], p.get("Properties", {})) for p in pal]
    B = {}
    for b in d["blocks"]:
        n, pr = meta[b["state"]]
        if n in ("minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:structure_void", "minecraft:jigsaw"): continue
        B[tuple(b["pos"])] = (n, pr)
    seeds = {p for p, (n, pr) in B.items() if SEED.search(n.split(":")[-1]) or n.split(":")[-1] in JOBS}
    # free-standing stairs/slabs (air above, floor below, >=2 open horizontal sides) or touching a seed with air above
    extra = set()
    for p, (n, pr) in B.items():
        s = n.split(":")[-1]
        if not (s.endswith("_stairs") or s.endswith("_slab")): continue
        x, y, z = p
        if (x, y + 1, z) in B or (x, y - 1, z) not in B: continue
        free = sum((x + dx, y, z + dz) not in B for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        touch = any((x + dx, y + dy, z + dz) in seeds for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)))
        if free >= 2 or touch: extra.add(p)
    cells = seeds | extra
    seen, comps = set(), []
    for p in cells:
        if p in seen: continue
        comp, st = [], [p]; seen.add(p)
        while st:
            c = st.pop(); comp.append(c); x, y, z = c
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in cells and q not in seen: seen.add(q); st.append(q)
        comps.append(comp)
    NOSOLID = ("leaves", "glass", "pane", "door", "fence", "sign", "torch", "lantern", "carpet", "plate", "button", "ladder", "vine", "chain", "banner", "flower", "pot", "bed")
    solid = {p for p, (n, pr) in B.items() if p not in cells and not any(k in n for k in NOSOLID)}
    colmax = {}
    for (x, y, z) in solid: colmax[(x, z)] = max(colmax.get((x, z), -1), y)

    def interior(p):
        x, y, z = p
        if colmax.get((x, z), -1) <= y: return False
        walls = 0
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if any((x + k * dx, yy, z + k * dz) in solid for k in range(1, 13) for yy in (y, y + 1)): walls += 1
        return walls >= 3
    out = []
    for comp in comps:
        if len(comp) > 10: continue
        items = [(x, y, z, norm(*B[(x, y, z)])) for x, y, z in comp]
        names = [i[3] for i in items]
        low = min(comp, key=lambda c: c[1])
        out.append((classify(names), canon(items), interior(low)))
    pal_count = collections.Counter(norm(*B[p]).split(":")[0] for p in B if p not in cells)
    return out, pal_count, len(B)


def main():
    zref = zipfile.ZipFile(ROOT / "reference/structures_nbt.zip")
    files = [n for n in zref.namelist() if n.endswith(".nbt") and re.search(r"/structures?/.*village", n) and not any(s in n for s in SKIP_DIR)]
    pats = collections.defaultdict(lambda: {"count": 0, "houses": set(), "ex": []})
    fam_pal = collections.defaultdict(collections.Counter); fam_clusters = collections.defaultdict(collections.Counter)
    fam_houses = collections.Counter(); bad = 0; total_clusters = 0
    for n in files:
        parts = n.split("/")                      # data/<ns>/structure/<...>
        fam = parts[1] + "/" + "/".join(parts[4:6]) if len(parts) > 6 else parts[1]
        try: cl, pc, nb = scan_house(zref.read(n))
        except Exception as e:
            bad += 1; continue
        fam_houses[fam] += 1; fam_pal[fam].update(pc)
        for cat, sig, inside in cl:
            total_clusters += 1; fam_clusters[fam][cat if inside else 'outdoor'] += 1
            e = pats[(cat if inside else 'outdoor', sig)]; e["count"] += 1; e["houses"].add(n)
            if len(e["ex"]) < 2 and n not in e["ex"]: e["ex"].append(n)
    docs = ROOT / "docs"
    # ---- catalog
    L = ["# Furniture catalogue (generated by tools/furniture_scan.py, pass 7-0)", "",
         f"Scanned {len(files) - bad} village NBTs ({bad} unreadable) from {len(fam_houses)} groups; {total_clusters} furniture clusters; {len(pats)} distinct patterns.",
         "Pattern notation: `token@(dx,dy,dz)` relative to the cluster's min corner after rotation/mirror normalisation; `W_`=any wood, `C_`=any colour, `:bottom/:top` = half/type, `:open` trapdoor open.",
         "Use this to pick the pieces the new savanna houses should reuse (the most common ones are what players already read as furniture).", ""]
    bycat = collections.defaultdict(list)
    for (cat, sig), e in pats.items(): bycat[cat].append((e["count"], len(e["houses"]), sig, e["ex"]))
    for cat in ("bed", "table", "seat", "storage", "workstation", "shelf", "light", "plant", "decor", "other", "outdoor"):
        rows = sorted(bycat[cat], key=lambda r: -r[0])
        L += [f"## {cat if cat != 'outdoor' else 'outdoor (all categories, not under a roof)'} ({sum(r[0] for r in rows)} clusters, {len(rows)} patterns) - top 14", "", "| n | houses | pattern | example |", "|---|---|---|---|"]
        for cnt, nh, sig, ex in rows[:14]:
            txt = " + ".join(f"{n}@({x},{y},{z})" for n, x, y, z in sig)
            L.append(f"| {cnt} | {nh} | {txt} | {ex[0].split('/structure')[-1][:60]} |")
        L.append("")
    (docs / "furniture_catalog.md").write_text("\n".join(L) + "\n")
    # ---- raw
    (docs / "furniture_patterns.json").write_text(json.dumps([{"cat": c, "n": e["count"], "houses": len(e["houses"]), "pattern": [list(t) for t in sig]}
                                                              for (c, sig), e in sorted(pats.items(), key=lambda kv: -kv[1]["count"])][:600]))
    # ---- palettes per group
    P = ["# House palettes per village group (structural blocks only, top 14, generated)", "",
         "| group | houses | furniture clusters/house | top structural blocks |", "|---|---|---|---|"]
    for fam in sorted(fam_houses):
        tops = ", ".join(f"{b} {c}" for b, c in fam_pal[fam].most_common(14))
        P.append(f"| {fam} | {fam_houses[fam]} | {sum(fam_clusters[fam].values()) / fam_houses[fam]:.1f} | {tops} |")
    (docs / "house_palettes.md").write_text("\n".join(P) + "\n")
    print(f"houses {len(files) - bad}, clusters {total_clusters}, patterns {len(pats)}")
    for cat in ("bed", "table", "seat", "storage", "light", "shelf"):
        r = sorted(bycat[cat], key=lambda t: -t[0])[:2]
        for cnt, nh, sig, ex in r: print(cat, cnt, " + ".join(f"{n}@({x},{y},{z})" for n, x, y, z in sig)[:150])


if __name__ == "__main__":
    main()
