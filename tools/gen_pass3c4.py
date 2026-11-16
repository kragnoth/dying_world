#!/usr/bin/env python3
"""gen_pass3c4.py - pass 3c-4: ALL survivor villages (plains taiga desert savanna snowy) in one run. Supersedes gen_pass3c1.py.
Usage: gen_pass3c4.py            (always regenerates all five; safe to re-run)

Per biome B (house pool OVERRIDE of minecraft:village/B/houses):
  base houses : lived (original NBT) + worn variants (villager-free NBT copy under dying_world:village/B/houses_worn/<n>), 40/60 split.
  donor houses: hand-picked houses from mod villages in the same MATERIAL FAMILY are appended (DONORS below), ~DONOR_SHARE of the pool.
    A donor is accepted only if: its NBT has a jigsaw named minecraft:building_entrance, every jigsaw pool it references exists
    (or is minecraft:empty), and its processor list can be read. Everything rejected is listed in docs/pass3c4_mix_report.md.
    Donor processors are COMBINED with ours (dying_world:mix/*) so street/path conversions keep working.
  worn copies get every jigsaw whose pool contains 'villager' set to minecraft:empty (no villagers in worn houses).
Biome tags: dying_world:has_structure/village_B = explicit optional biome list from tools/village_biomes.py (tag-driven, vanilla + modded, disjoint across families).
Also widens the gearwrights abandoned_{ruin,hamlet,village}_B tags with the same lists: run gen_pass3b2.py BEFORE this script if you ever regenerate it.
Wet biomes (swamp/jungle/beach/mangrove) intentionally get NO village (reserved for survivor bunkers later)."""
import gzip, json, re, sys, zipfile, zlib, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtmini, village_biomes
ROOT = Path(__file__).resolve().parent.parent
WG = zipfile.ZipFile(ROOT / "reference/worldgen_reference.zip")
NBT = zipfile.ZipFile(ROOT / "reference/structures_nbt.zip")
WGN, NBTN = set(WG.namelist()), set(NBT.namelist())
OUT = ROOT / "datapack/data"
BIOMES = ["plains", "taiga", "desert", "savanna", "snowy"]
DONOR_SHARE = 0.40            # donor houses ~ 40% of base weight sum (=> ~29% of the pool)

DONORS = {  # family base -> list of (label, template_pool id of donor 'houses' pool)
    "plains": [("forest_ruins", "kaisyn:village/forest_ruins/houses"), ("birch_romanian", "kaisyn:village/birch_forest_romanian/houses"),
               ],   # brutos/vsrevamped cherry REMOVED (user 8-11: third-party datapacks, dropped entirely)
    "taiga":  [("snowy_taiga_viking", "kaisyn:village/snowy_taiga_viking/houses"), ("old_growth_polish", "kaisyn:village/old_growth_taiga_polish/houses")],
    "desert": [("badlands_pueblo", "kaisyn:village/badlands_pueblo/houses")],   # wooded_badlands_tipi REMOVED (user: no tipis anywhere, 7-0b / 8-10)
    "savanna": [],   # savanna_plateau_ramshackled has no entrance-compatible house pool (checked)
    "snowy":  [("frozen", "windswept:village/frozen/houses")],
}
FAMILY_BIOMES, UNASSIGNED = village_biomes.families()   # tag-driven, vanilla + modded, disjoint (tools/village_biomes.py)
opt = lambda ids: [{"id": i, "required": False} for i in ids]   # optional entries: a missing/removed mod biome can never break the tag

def rj(name): return json.loads(re.sub(r"\r", "", WG.read(name).decode("utf-8")))
def w(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, indent=2) + "\n")

# ---------------- rules ----------------
def rule(inp, out, p=None):
    ip = {"predicate_type": "minecraft:block_match", "block": inp} if p is None else \
         {"predicate_type": "minecraft:random_block_match", "block": inp, "probability": p}
    return {"input_predicate": ip, "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": out}}
PROC = {}   # our processor lists: id -> list of processors (so donors can be combined)
def plist(name, rules):
    PROC[f"dying_world:{name}"] = [{"processor_type": "minecraft:rule", "rules": rules}]
    w(OUT / f"dying_world/worldgen/processor_list/{name}.json", {"processors": PROC[f"dying_world:{name}"]})
colors = "white orange magenta light_blue yellow lime pink gray light_gray cyan purple blue brown green red black".split()
jobs = "composter barrel blast_furnace smoker cartography_table fletching_table grindstone lectern loom smithing_table stonecutter brewing_stand cauldron water_cauldron lava_cauldron powder_snow_cauldron".split()
beds_to = lambda out: [rule(f"minecraft:{c}_bed", out) for c in colors]
jobs_to = lambda out: [rule(f"minecraft:{j}", out) for j in jobs]
crops = [rule(f"minecraft:{c}", "minecraft:dead_bush") for c in ("wheat", "carrots", "potatoes")]
terra = [f"minecraft:{c}_terracotta" for c in "white orange magenta light_blue yellow lime pink light_gray cyan purple blue brown green red".split()]
M = lambda i, o, p=None: rule(f"minecraft:{i}", f"minecraft:{o}", p)

# plains / taiga (unchanged from pass 3c-1)
plist("village_worn", beds_to("minecraft:moss_carpet") + jobs_to("minecraft:mossy_cobblestone") +
      [rule("minecraft:cobblestone", "minecraft:mossy_cobblestone", 0.4), rule("minecraft:stone_bricks", "minecraft:mossy_stone_bricks", 0.25),
       rule("minecraft:stone_bricks", "minecraft:cracked_stone_bricks", 0.25)])
# desert (pass 3c-3b)
plist("desert_lived", [M("smooth_sandstone", "sandstone", .08), M("cut_sandstone", "sandstone", .08)])
plist("desert_weathered", beds_to("minecraft:brown_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    M("smooth_sandstone", "sandstone", .30), M("cut_sandstone", "sandstone", .30), M("bookshelf", "cobweb", .40), M("grass_block", "coarse_dirt", .60)] +
    [rule(t, "minecraft:terracotta", .55) for t in terra])
plist("desert_scorched", beds_to("minecraft:black_carpet") + jobs_to("minecraft:blackstone") + crops + [
    M("smooth_sandstone", "black_terracotta", .18), M("smooth_sandstone", "gray_terracotta", .22), M("cut_sandstone", "black_terracotta", .15),
    M("birch_planks", "dark_oak_planks", .5), M("jungle_planks", "dark_oak_planks", .5), M("hay_block", "coal_block", .6), M("bookshelf", "cobweb", .5)] +
    [rule(t, "minecraft:black_terracotta", .35) for t in terra])
plist("desert_tarred", beds_to("minecraft:black_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    rule("minecraft:birch_planks", "tarbound:tar_soaked_planks", .5), rule("minecraft:jungle_planks", "tarbound:tar_soaked_planks", .5),
    rule("minecraft:sand", "immersivepetroleum:asphalt", .12), M("smooth_sandstone", "sandstone", .15), M("bookshelf", "cobweb", .4)])
# savanna (acacia)
plist("savanna_lived", [M("cobblestone", "mossy_cobblestone", .2)])
plist("savanna_weathered", beds_to("minecraft:brown_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    M("cobblestone", "mossy_cobblestone", .4), M("bookshelf", "cobweb", .4), M("grass_block", "coarse_dirt", .5), M("smooth_stone", "stone", .3)] +
    [rule(t, "minecraft:terracotta", .5) for t in terra])
plist("savanna_scorched", beds_to("minecraft:black_carpet") + jobs_to("minecraft:blackstone") + crops + [
    M("acacia_planks", "dark_oak_planks", .35), M("hay_block", "coal_block", .6), M("white_wool", "black_wool", .5), M("grass_block", "coarse_dirt", .4),
    M("bookshelf", "cobweb", .5)] + [rule(t, "minecraft:black_terracotta", .35) for t in terra])
plist("savanna_tarred", beds_to("minecraft:black_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    rule("minecraft:acacia_planks", "tarbound:tar_soaked_planks", .5), M("dirt", "coarse_dirt", .15),
    rule("minecraft:smooth_stone", "immersivepetroleum:asphalt", .2), M("bookshelf", "cobweb", .4)])
# snowy (spruce / snow)
plist("snowy_lived", [M("cobblestone", "mossy_cobblestone", .15), M("stone_bricks", "cracked_stone_bricks", .1)])
plist("snowy_weathered", beds_to("minecraft:gray_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    M("spruce_planks", "dark_oak_planks", .25), rule("windswept:holly_planks", "minecraft:dark_oak_planks", .25), M("cobblestone", "mossy_cobblestone", .4), M("stone_bricks", "cracked_stone_bricks", .3),
    M("bookshelf", "cobweb", .4)])
plist("snowy_scorched", beds_to("minecraft:black_carpet") + jobs_to("minecraft:blackstone") + crops + [
    M("spruce_planks", "dark_oak_planks", .35), rule("windswept:holly_planks", "minecraft:dark_oak_planks", .35), M("hay_block", "coal_block", .6), M("snow_block", "tuff", .25), M("bookshelf", "cobweb", .5),
    M("stone_bricks", "cracked_stone_bricks", .3)])
plist("snowy_tarred", beds_to("minecraft:black_carpet") + jobs_to("minecraft:cobblestone") + crops + [
    rule("minecraft:spruce_planks", "tarbound:tar_soaked_planks", .5), rule("windswept:holly_planks", "tarbound:tar_soaked_planks", .5), rule("minecraft:snow_block", "immersivepetroleum:asphalt", .12),
    M("stone_bricks", "cracked_stone_bricks", .3), M("bookshelf", "cobweb", .4)])

DEFAULT = {"lived": ("minecraft:mossify_10_percent", 2), "worn": [("dying_world:village_worn", 3)]}
def prof(b): return {"lived": (f"dying_world:{b}_lived", 6), "worn": [(f"dying_world:{b}_weathered", 4), (f"dying_world:{b}_scorched", 3), (f"dying_world:{b}_tarred", 2)]}
PROFILES = {"desert": prof("desert"), "savanna": prof("savanna"), "snowy": prof("snowy")}

# ---------------- helpers ----------------
def nbt_path(loc): ns, p = loc.split(":"); return f"data/{ns}/structure/{p}.nbt"
def pool_exists(pid): ns, p = pid.split(":"); return f"data/{ns}/worldgen/template_pool/{p}.json" in WGN
def jigsaws(raw):
    f = nbtmini.parse(raw); pal = [p["Name"] for p in f["palette"]]; out = []
    for b in f["blocks"]:
        if pal[b["state"]] == "minecraft:jigsaw":
            n = b.get("nbt", {}); out.append((n.get("name"), n.get("pool"), n.get("joint")))
    return out, {p for p in pal}
def strip_villagers(raw, pools):
    n = 0
    for pool in {p for p in pools if p and "villager" in p}:
        old = pool.encode(); a = len(old).to_bytes(2, "big") + old
        b = len(b"minecraft:empty").to_bytes(2, "big") + b"minecraft:empty"
        n += raw.count(a); raw = raw.replace(a, b)
    return raw, n
def proc_list(spec):
    """processors spec of a pool element -> list of processor dicts, or None if unreadable"""
    if isinstance(spec, dict): return spec.get("processors", [])
    if spec == "minecraft:empty": return []
    ns, p = spec.split(":"); n = f"data/{ns}/worldgen/processor_list/{p}.json"
    if n not in WGN: return None
    d = rj(n); return d["processors"] if isinstance(d, dict) else d
def is_plain(spec): return spec == "minecraft:empty" or (isinstance(spec, str) and spec.startswith("minecraft:mossify_")) or spec == {"processors": []}
def combined(donor_spec, ours_id):
    """donor processors first (e.g. street/path conversion), then ours. Returns processor_list id."""
    if is_plain(donor_spec): return ours_id
    base = proc_list(donor_spec)
    if ours_id.startswith("minecraft:"):
        ours = proc_list(ours_id)
    else: ours = PROC[ours_id]
    key = hashlib.md5(json.dumps(donor_spec, sort_keys=True).encode()).hexdigest()[:8]
    nid = f"dying_world:mix/{ours_id.split(':')[1]}__{key}"
    w(OUT / f"dying_world/worldgen/processor_list/mix/{ours_id.split(':')[1]}__{key}.json", {"processors": base + ours})
    return nid

report = ["# Pass 3c-4 mix report (generated by tools/gen_pass3c4.py)\n"]
set_members = []
for B in BIOMES:
    pr = PROFILES.get(B, DEFAULT)
    pool = rj(f"data/minecraft/worldgen/template_pool/village/{B}/houses.json")
    base, removed, base_sum, kept, skipped = [], 0, 0, 0, []
    for e in pool["elements"]:
        el = e["element"]
        if el["element_type"] != "minecraft:single_pool_element" or el.get("processors") != "minecraft:empty":
            base.append(e); kept += 1; continue
        name = el["location"].split("/houses/")[-1]
        if f"data/minecraft/structure/village/{B}/houses/{name}.nbt" not in NBTN:   # vanilla pool lists a house with no nbt (skipped by the game too)
            skipped.append(name); continue
        base_sum += e["weight"]
        base.append({"weight": e["weight"] * pr["lived"][1], "element": {**el, "processors": pr["lived"][0]}})
        raw = gzip.decompress(NBT.read(f"data/minecraft/structure/village/{B}/houses/{name}.nbt"))
        js, _ = jigsaws(raw); mod, n = strip_villagers(raw, [j[1] for j in js]); removed += n
        dst = OUT / f"dying_world/structure/village/{B}/houses_worn/{name}.nbt"
        dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(gzip.compress(mod, mtime=0))
        for proc, mult in pr["worn"]:
            base.append({"weight": e["weight"] * mult, "element": {**el, "location": f"dying_world:village/{B}/houses_worn/{name}", "processors": proc}})
    # ---- donors ----
    acc, rej = [], []
    for label, dpool in DONORS[B]:
        if not pool_exists(dpool): rej.append((label, "-", "donor pool not found in reference")); continue
        dp = rj(f"data/{dpool.split(':')[0]}/worldgen/template_pool/{dpool.split(':')[1]}.json")
        for e in dp["elements"]:
            el = e["element"]
            if el.get("element_type") == "minecraft:empty_pool_element": continue
            if el.get("element_type") not in ("minecraft:single_pool_element", "minecraft:legacy_single_pool_element") or "location" not in el:
                rej.append((label, el.get("element_type"), "not a single nbt element")); continue
            loc = el["location"]; np_ = nbt_path(loc)
            if np_ not in NBTN: rej.append((label, loc, "nbt missing")); continue
            raw = gzip.decompress(NBT.read(np_)); js, pal = jigsaws(raw)
            if not any(j[0] == "minecraft:building_entrance" for j in js): rej.append((label, loc, "no building_entrance jigsaw")); continue
            bad = [j[1] for j in js if j[1] and j[1] != "minecraft:empty" and not pool_exists(j[1]) and "villager" not in j[1]]
            if bad: rej.append((label, loc, f"jigsaw pool missing: {bad[0]}")); continue
            if proc_list(el.get("processors", "minecraft:empty")) is None: rej.append((label, loc, "processor list unreadable")); continue
            acc.append((label, e, raw, js, pal))
    # each donor village gets an EQUAL share of the donor weight (so a village with big weights, e.g. cherry, cannot dominate)
    labels = sorted({a[0] for a in acc}); tgt = DONOR_SHARE * base_sum / max(1, len(labels))
    lsum = {l: sum(a[1]["weight"] for a in acc if a[0] == l) for l in labels}
    d_total = 0
    for label, e, raw, js, pal in acc:
        el = e["element"]; loc = el["location"]; dw = max(1, round(e["weight"] * tgt / lsum[label])); d_total += dw
        spec = el.get("processors", "minecraft:empty")
        lived_p = combined(spec, pr["lived"][0])
        base.append({"weight": dw * pr["lived"][1], "element": {**el, "processors": lived_p}})
        mod, n = strip_villagers(raw, [j[1] for j in js]); removed += n
        ns, pth = loc.split(":"); nm = pth.split("/")[-1]
        wl = f"dying_world:village/{B}/mix_worn/{label}/{nm}"
        dst = OUT / f"dying_world/structure/village/{B}/mix_worn/{label}/{nm}.nbt"
        dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(gzip.compress(mod, mtime=0))
        for proc, mult in pr["worn"]:
            base.append({"weight": dw * mult, "element": {**el, "location": wl, "processors": combined(spec, proc)}})
    pool["elements"] = base
    w(OUT / f"minecraft/worldgen/template_pool/village/{B}/houses.json", pool)
    s = rj(f"data/minecraft/worldgen/structure/village_{B}.json")
    s["biomes"] = f"#dying_world:has_structure/village_{B}"
    w(OUT / f"dying_world/worldgen/structure/village_{B}.json", s)
    w(OUT / f"dying_world/tags/worldgen/biome/has_structure/village_{B}.json", {"replace": False, "values": opt(FAMILY_BIOMES[B])})
    # abandoned ruins/hamlets/villages (gearwrights): keep their original tag, add the same family biomes (cherry_grove stays with the cherry variant)
    for kind in ("ruin", "hamlet", "village"):
        tp = OUT / f"dying_world/tags/worldgen/biome/has_structure/abandoned_{kind}_{B}.json"
        if not tp.exists(): continue
        orig = [v for v in json.loads(tp.read_text())["values"] if isinstance(v, str) and v.startswith("#")][:1]
        ex = [x for x in FAMILY_BIOMES[B] if x != "minecraft:cherry_grove"]
        w(tp, {"replace": False, "values": orig + opt(ex)})
    set_members.append({"structure": f"dying_world:village_{B}", "weight": 1})
    share = 100 * d_total / (base_sum + d_total) if acc else 0
    print(f"{B}: {len(base)} pool entries | base houses weight {base_sum}, donors accepted {len(acc)} (weight {d_total}, {share:.0f}% of pool) rejected {len(rej)} | villager jigsaws stripped {removed}")
    if skipped: report.append(f"\n(note {B}: vanilla pool entries with no nbt, left out: {', '.join(skipped)})")
    report.append(f"\n## {B}\n- base weight {base_sum}; donor houses accepted {len(acc)}, donor weight {d_total} (~{share:.0f}% of houses)\n- biomes ({len(FAMILY_BIOMES[B])}): {', '.join(x.replace('minecraft:', '') for x in FAMILY_BIOMES[B])}")
    by = {}
    for a in acc: by.setdefault(a[0], []).append(a[1]["element"]["location"].split("/")[-1])
    for lab, v in by.items(): report.append(f"- accepted {lab}: {len(v)} houses")
    for lab, loc, why in rej: report.append(f"- REJECTED {lab} `{loc.split('/')[-1]}`: {why}")
    if not DONORS[B]: report.append("- no donors (savanna_plateau_ramshackled houses have no entrance jigsaw compatible with vanilla streets)")
w(OUT / "dying_world/worldgen/structure_set/survivor_villages.json",
  {"structures": set_members, "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 12,
   "salt": zlib.crc32(b"dying_world:survivor_villages") % 2000000000}})
report.append("\n## no village (excluded or unmatched)\n- wet/ocean/river/beach/mushroom/cave/mountain/spooky biomes are excluded on purpose (wet ones reserved for survivor bunkers).\n- tag-matched but unassigned (check if wanted): " + ", ".join(UNASSIGNED))
(ROOT / "docs/pass3c4_mix_report.md").write_text("\n".join(report) + "\n")
