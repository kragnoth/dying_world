#!/usr/bin/env python3
"""
gen_pass9_25.py - pass 9-25: the user's CUSTOM CREATE MILLS restored + style-cleaned (user: 'I custom built those, safe to use; make sure they fit our style,
clean if not; re-add the lost structures'). Run after 9_21 (pool weights) and before 8_9 (lantern rule, now also over gearwrights NBTs) and build. Safe to re-run.
Source: reference_custom/<fam>__windmill[_abandoned].nbt (+ desert__watermill) = the user's originals (1.21.1, Create windmill bearing/sails/millstone; desert water
wheel), recovered from reference/structures_nbt.zip (the lived versions were lost from the kubejs data during the 8-x splits).
Style check: materials already match our families (plains oak/dark oak/mossy cobble, taiga spruce/podzol/andesite, snowy spruce/diorite, savanna acacia/terracotta/
packed mud, desert sandstone). Cleaning:
  - desert watermill: jungle wood -> spruce (our desert wood), all three variants.
  - ABANDONED variants: structural blocks the old process deleted are put back as WORN versions of the lived block (cobble -> mossy, stone bricks -> mossy/cracked,
    logs/planks -> stripped, panes kept, ~half the shutters) - user rule 'worn, not missing'. Torn sails, missing crops and half the lanterns stay (cloth/crops/decay).
  - lanterns: gen_pass8_9 head-clearance rule.
Placement (the user's lithostitched modifiers in kubejs_base/data/gearwrights/lithostitched/worldgen_modifier, kept):
  - lived mills -> minecraft:village/<fam>/houses, weight 1 -> 20 (our pools were re-weighted x4 in 9-21; 1 would be ~0.07% per plot).
  - abandoned mills -> retargeted from vanilla zombie-village pools (unused) to dying_world:<fam>/ruined_houses (abandoned villages/hamlets/ruins), weight 8.
  Burnt variants not used yet (candidates for the burnt landmarks).
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from buildkit import WEAR
from gen_pass4_2a import M, w

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "reference_custom"; DST = ROOT / "datapack/data/gearwrights/structure/village"
MODS = ROOT / "kubejs_base/data/gearwrights/lithostitched/worldgen_modifier"
MILLS = {"plains": "windmill", "taiga": "windmill", "snowy": "windmill", "savanna": "windmill", "desert": "watermill"}
SKIP = ("sail", "wheat", "carrots", "potatoes", "beetroots", "lantern", "torch", "carpet", "potted", "flower", "dead_bush", "short_grass", "fern", "water", "door")

def jungle_to_spruce(s):
    for p, (n, pr, nb) in list(s.b.items()):
        if "jungle" in n: s.b[p] = (n.replace("jungle", "spruce"), pr, nb)

def worn_name(r, n):
    if n in WEAR:
        acc, q = 0, r.random()
        for alt, ch in WEAR[n]:
            acc += ch * 1.8
            if q < acc: return alt
        return n
    k = n.split(":")[1]
    if k.endswith("_log") and not k.startswith("stripped_"): return f"minecraft:stripped_{k}"
    if k.endswith("_planks") and r.random() < .4: return f"minecraft:stripped_{k.replace('_planks', '_wood')}"
    return n

def restore(live, ab, r):
    n_fix = 0
    for p, (n, pr, nb) in live.b.items():
        if n in ("minecraft:air", "minecraft:structure_void", "minecraft:jigsaw") or n.startswith("create:"): continue
        cur = ab.b.get(p, ("minecraft:air",))[0]
        if cur not in ("minecraft:air",): continue
        k = n.split(":")[1]
        if any(x in k for x in SKIP): continue
        if "trapdoor" in k and r.random() < .5: continue
        ab.b[p] = (worn_name(r, n), dict(pr), None); n_fix += 1
    return n_fix

def main():
    out = []
    for fam, mill in MILLS.items():
        live = nbtrw.Struct((SRC / f"{fam}__{mill}.nbt").read_bytes())
        ab = nbtrw.Struct((SRC / f"{fam}__{mill}_abandoned.nbt").read_bytes())
        burnt = nbtrw.Struct((SRC / f"{fam}__{mill}_burnt.nbt").read_bytes())
        if fam == "desert":
            for s in (live, ab, burnt): jungle_to_spruce(s)
        fixed = restore(live, ab, random.Random(zlib.crc32(fam.encode())))
        (DST / fam).mkdir(parents=True, exist_ok=True)
        for s, suf in ((live, ""), (ab, "_abandoned"), (burnt, "_burnt")): (DST / fam / f"{mill}{suf}.nbt").write_bytes(s.bytes())
        for zombie in (False, True):
            mp = MODS / f"create_{mill}_{fam}{'_zombie' if zombie else ''}.json"; j = json.loads(mp.read_text())
            if zombie: j["template_pools"] = f"dying_world:{fam}/ruined_houses"
            for e in j["elements"]: e["weight"] = 8 if zombie else 20
            w(mp, j)
        out.append(f"{fam} {mill}: {fixed} worn blocks restored in the abandoned version")
    print("9-25:", "; ".join(out))

if __name__ == "__main__":
    main()
