#!/usr/bin/env python3
"""
gen_pass9_7.py - pass 9-7: coherence fixes from tools/coherence_audit.py (post-edit, run after 9_6; then 8_9, build, audit). Safe to re-run.
1. Biome gaps: land biomes that had NO settlement get one where it fits (optional entries, missing mods never break a tag):
   plains family (+ abandoned plains): cherry_grove, RU highland_fields, RU eucalyptus_forest; taiga family: RU blackwood_taiga, environmental pine_slopes,
   windswept_forest; abandoned plains only: RU ashen_woodland (burnt land); abandoned SWAMP (stilt houses) widened to wet biomes: mangrove_swamp,
   environmental marsh, RU bayou / old_growth_bayou / fen / marsh / fungal_fen. Deliberately empty (like vanilla): peaks, slopes, stony shore, mushroom
   fields, dark forest, jungles, hot springs.
2. Single abandoned buildings + tarbound sites get the survivor-village exclusion zone (3 chunks) so they never spawn inside a village.
3. Abandoned single buildings (cabin, smithy, watchtower, lighthouse) get the same light undead spawns as abandoned ruins (zombie / skeleton / zombie villager).
4. Survivor villages + scavenger stronghold -> beard_box (same no-floating rule as the abandoned settlements, 6-1).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pass4_2a import w, OUT

T = OUT / "tags/worldgen/biome/has_structure"
def add(tag, ids):
    p = T / f"{tag}.json"; j = json.loads(p.read_text())
    have = {v["id"] if isinstance(v, dict) else v for v in j["values"]}
    j["values"] += [{"id": i, "required": False} for i in ids if i not in have]; w(p, j)

PLAINS = ["minecraft:cherry_grove", "regions_unexplored:highland_fields", "regions_unexplored:eucalyptus_forest", "regions_unexplored:windswept_maple_forest",
          "regions_unexplored:wisteria_grove"]
TAIGA = ["regions_unexplored:blackwood_taiga", "environmental:pine_slopes", "regions_unexplored:pine_slopes", "minecraft:windswept_forest"]
SNOWY = ["windswept:snowy_pine_barrens"]
WET = ["minecraft:mangrove_swamp", "environmental:marsh", "regions_unexplored:bayou", "regions_unexplored:old_growth_bayou", "regions_unexplored:fen",
       "regions_unexplored:marsh", "regions_unexplored:fungal_fen"]
for k in ("village_plains", "abandoned_ruin_plains", "abandoned_hamlet_plains", "abandoned_village_plains"): add(k, PLAINS)
for k in ("abandoned_ruin_plains", "abandoned_hamlet_plains"): add(k, ["regions_unexplored:ashen_woodland"])
for k in ("village_taiga", "abandoned_ruin_taiga", "abandoned_hamlet_taiga", "abandoned_village_taiga"): add(k, TAIGA)
for k in ("abandoned_ruin_swamp", "abandoned_hamlet_swamp", "abandoned_village_swamp"): add(k, WET)
for k in ("village_snowy", "abandoned_ruin_snowy", "abandoned_hamlet_snowy", "abandoned_village_snowy"): add(k, SNOWY)

S = OUT / "worldgen/structure_set"
for s in ("abandoned_smithy", "abandoned_watchtower", "charnel_crypt", "drowned_radio", "researcher_cabin", "wayside_shrine"):
    p = S / f"{s}.json"; j = json.loads(p.read_text())
    j["placement"].setdefault("exclusion_zone", {"other_set": "dying_world:survivor_villages", "chunk_count": 3}); w(p, j)

UNDEAD = {"monster": {"bounding_box": "piece", "spawns": [
    {"type": "minecraft:zombie", "weight": 60, "minCount": 1, "maxCount": 2}, {"type": "minecraft:skeleton", "weight": 40, "minCount": 1, "maxCount": 2},
    {"type": "minecraft:zombie_villager", "weight": 20, "minCount": 1, "maxCount": 1}]}}
D = OUT / "worldgen/structure"
for s in ("abandoned_cabin", "abandoned_smithy", "abandoned_watchtower", "lighthouse"):
    p = D / f"{s}.json"; j = json.loads(p.read_text()); j["spawn_overrides"] = UNDEAD; w(p, j)
for s in ("village_plains", "village_taiga", "village_snowy", "village_desert", "village_savanna", "scavenger_stronghold"):
    p = D / f"{s}.json"; j = json.loads(p.read_text()); j["terrain_adaptation"] = "beard_box"; w(p, j)
print("9-7: biome gaps filled (plains/taiga/abandoned swamp), exclusion zones on 6 sets, undead on 4 single ruins, beard_box on survivor villages + stronghold")

# 5. cleanup: our processor lists / template pools that nothing references any more (left by 3c4 after the families were replaced)
import gzip, re
DATA = OUT.parent
blob = []
for p in DATA.rglob("*"):
    if p.is_file() and p.suffix == ".json": blob.append(p.read_text(errors="ignore"))
    elif p.is_file() and p.suffix == ".nbt": blob.append(gzip.decompress(p.read_bytes()).decode("latin1"))
blob = "\n".join(blob); removed = []
for kind in ("processor_list", "template_pool"):
    for p in sorted((OUT / f"worldgen/{kind}").rglob("*.json")):
        rid = "dying_world:" + str(p.relative_to(OUT / f"worldgen/{kind}"))[:-5]
        if rid not in blob.replace(f'"{rid}"', "", 0) or blob.count(rid) == 0: p.unlink(); removed.append(rid)
print(f"9-7 cleanup: removed {len(removed)} unreferenced processor lists/pools")
