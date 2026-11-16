#!/usr/bin/env python3
"""
gen_pass9_16.py - pass 9-16: NO MORE OVERLAPPING STRUCTURES (user: 'go through our structures and see why we are getting overlaps with the villages and
smaller structures'). Run LAST before build (after every pass that writes structure sets). Safe to re-run.
CAUSE: 25 independent surface structure sets. Different sets never avoid each other in vanilla placement; the only guard was an exclusion zone of 3-8 chunks
against survivor villages (whose pieces reach 5 chunks = radius 80). So abandoned villages/hamlets, the stronghold, research gates, outposts, cabins, wells ...
could all land on or inside each other (and inside villages when the zone was smaller than the village).
FIX = placement tiers (one structure per grid cell inside a set; weights pick the structure, biome misses fall through to the next pick):
  dying_world:settlements (22/11): survivor villages, abandoned villages, abandoned hamlets, scavenger stronghold, both research gates (big jigsaw towns;
        separation 11 chunks = 176 blocks > 2 x radius 80, so they can't touch). Weights ~ the old per-set densities.
  dying_world:landmarks (11/5, exclusion 7 chunks from settlements): every small/medium surface structure (ruins, cabin, smithy, watchtowers, burnt sites,
        chapel, crypt, minehead, concrete pads, dig sites, researcher cabin, shrine, wells, scavenger outposts, lighthouse, drowned radio).
  underground: proving grounds + sculk site keep their sets but avoid the industrial mineshaft (8 chunks); sunken lab avoids shipwrecks (4).
  road signs: exclusion now against settlements. Nether station vs fortress unchanged; End station alone.
Old per-structure set files are deleted (the structures themselves are untouched).
"""
import json, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pass4_2a import w, OUT

S = OUT / "worldgen/structure_set"
def salt(n): return zlib.crc32(n.encode()) % 2000000000
FAM = ("plains", "taiga", "savanna", "desert", "snowy")
SETTLE = [(f"village_{f}", 12) for f in FAM] + [(f"abandoned_village_{f}", 8) for f in FAM + ("swamp",)] + \
         [(f"abandoned_hamlet_{f}", 12) for f in FAM + ("swamp",)] + [("scavenger_stronghold", 10)] + [(f"scavenger_stronghold_{f}", 6) for f in FAM]   # 9-22 biome strongholds
OLD_SETTLE = ("survivor_villages", "abandoned_villages", "abandoned_hamlets", "scavenger_strongholds")
# 9-31: research gates moved OUT of settlements into their own stronghold-style CONCENTRIC RINGS set (user: too close to spawn, too frequent).
#   rings around 0,0: ring 0 = 4*D chunks (+-1.25*D), ring n adds 6*D. D=20 -> first ring ~880-1680 blocks, 2nd ~2800, 3rd ~4700, 4th ~6600.
#   COUNT 32 positions in total (first ring SPREAD 4); weights pick nether/end/derelict per position. Biome-preferred like vanilla strongholds.
#   Overlap guards: settlements exclude the gate rings (8 chunks); gates generate in the 'strongholds' step (after surface_structures) so a landmark
#   that lands on a gate is overwritten by it, never the other way round (the end portal room stays intact).
GATES = [("research_gate_nether", 5), ("research_gate_end", 5), ("research_gate_nether_derelict", 1), ("research_gate_end_derelict", 1)]
GATE_RINGS = {"distance": 20, "spread": 4, "count": 32}
# 9-28: cabin split oak/spruce/dark oak by biome, smithy + arid smithy
LAND = [(f"abandoned_ruin_{f}", 3) for f in FAM + ("swamp",)] + [
    ("abandoned_cabin", 8), ("abandoned_cabin_oak", 5), ("abandoned_cabin_dark_oak", 2), ("abandoned_smithy", 2), ("abandoned_smithy_arid", 1), ("hermit_cottage", 8), ("tinker_workshop", 6), ("plague_house", 8),
    ("ruined_chapel", 5), ("charnel_crypt", 5), ("collapsed_minehead", 9), ("concrete_pad_temperate", 3), ("concrete_pad_cold", 3), ("concrete_pad_arid", 3),
    ("concrete_pad_wild", 3), ("dig_site_arid", 6), ("dig_site_temp", 6), ("researcher_cabin", 6), ("wayside_shrine", 12),
    ("wells/temperate", 2), ("wells/cold", 2), ("wells/arid", 2), ("wells/wild", 2), ("wells/washhouse", 1),
    ("scavenger_outpost_temperate", 2), ("scavenger_outpost_cold", 2), ("scavenger_outpost_arid", 2), ("scavenger_outpost_wild", 2),
    ("scavenger_outpost_abandoned", 3), ("scavenger_outpost_raiders", 1), ("lighthouse", 3), ("drowned_radio", 12)]
OLD_LAND = ("abandoned_ruins", "abandoned_cabin", "abandoned_smithy", "abandoned_watchtower", "burnt_homestead", "burnt_manor", "burnt_watchtower",
            "ruined_chapel", "charnel_crypt", "collapsed_minehead", "concrete_pads", "dig_sites", "researcher_cabin", "wayside_shrine", "wells",
            "scavenger_outposts", "lighthouse", "drowned_radio")

def main():
    # the structures must exist (a missing id in a set breaks world loading)
    for n, _ in SETTLE + LAND:
        assert (OUT / f"worldgen/structure/{n}.json").exists(), n
    # find the namespace each landmark currently lives in (tarbound ids are ours under dying_world? check the old sets)
    for old in OLD_SETTLE + OLD_LAND:
        p = S / f"{old}.json"
        if p.exists(): p.unlink()
    for n, _ in GATES:
        assert (OUT / f"worldgen/structure/{n}.json").exists(), n
        p = OUT / f"worldgen/structure/{n}.json"; j = json.loads(p.read_text()); j["step"] = "strongholds"; w(p, j)
    w(S / "research_gates.json", {"structures": [{"structure": f"dying_world:{n}", "weight": wt} for n, wt in GATES],
        "placement": {"type": "minecraft:concentric_rings", **GATE_RINGS, "preferred_biomes": "#dying_world:has_structure/scavenger_outpost_any",
                      "salt": salt("dying_world:research_gates")}})
    w(S / "settlements.json", {"structures": [{"structure": f"dying_world:{n}", "weight": wt} for n, wt in SETTLE],
        "placement": {"type": "minecraft:random_spread", "spacing": 22, "separation": 11, "salt": salt("dying_world:settlements"),
                      "exclusion_zone": {"other_set": "dying_world:research_gates", "chunk_count": 8}}})
    w(S / "landmarks.json", {"structures": [{"structure": f"dying_world:{n}", "weight": wt} for n, wt in LAND],
        "placement": {"type": "minecraft:random_spread", "spacing": 11, "separation": 5, "salt": salt("dying_world:landmarks"),
                      "exclusion_zone": {"other_set": "dying_world:settlements", "chunk_count": 7}}})
    # 9-35: proving grounds now has a SURFACE hut (9-34) and landed inside an abandoned village -> it shares ONE set with the industrial mineshaft
    #   (both surface-started, both big underground; one per grid cell keeps them apart) and that set avoids settlements.
    for old in ("proving_grounds", "industrial_mineshafts"):
        p = S / f"{old}.json"
        if p.exists(): p.unlink()
    for n in ("proving_grounds", "industrial_mineshaft"): assert (OUT / f"worldgen/structure/{n}.json").exists(), n
    w(S / "deep_sites.json", {"structures": [{"structure": "dying_world:industrial_mineshaft", "weight": 1}, {"structure": "dying_world:proving_grounds", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 26, "separation": 10, "salt": salt("dying_world:deep_sites"),
                      "exclusion_zone": {"other_set": "dying_world:settlements", "chunk_count": 6}}})
    for name, other, n in (("sculk_research_site", "deep_sites", 8),
                           ("sunken_research_lab", "shipwrecks", 4), ("road_signs", "settlements", 6)):
        p = S / f"{name}.json"; j = json.loads(p.read_text())
        j["placement"]["exclusion_zone"] = {"other_set": f"dying_world:{other}", "chunk_count": n}; w(p, j)
    # any other set still pointing at a deleted set
    gone = {f"dying_world:{o}" for o in OLD_SETTLE + OLD_LAND}
    for p in S.glob("*.json"):   # 9-35: anything still avoiding the two merged sets avoids deep_sites
        j = json.loads(p.read_text()); ez = j["placement"].get("exclusion_zone")
        if ez and ez["other_set"] in ("dying_world:proving_grounds", "dying_world:industrial_mineshafts"): ez["other_set"] = "dying_world:deep_sites"; w(p, j)
    for p in S.glob("*.json"):
        j = json.loads(p.read_text()); ez = j["placement"].get("exclusion_zone")
        if ez and ez["other_set"] in gone: j["placement"]["exclusion_zone"]["other_set"] = "dying_world:settlements"; w(p, j)
    # 9-32: structure TAGS for FTB Quests structure tasks (the old #gearwrights:* tags and gearwrights:/vanilla ids no longer generate)
    T = OUT / "tags/worldgen/structure"
    tags = {
        "abandoned_settlements": [n for n, _ in SETTLE if n.startswith(("abandoned_village_", "abandoned_hamlet_"))]
                                 + [n for n, _ in LAND if n.startswith("abandoned_ruin_")],
        "landmarks": [n for n, _ in LAND if not n.startswith(("abandoned_ruin_", "wells/", "scavenger_outpost_"))],
        "scavenger_strongholds": [n for n, _ in SETTLE if n.startswith("scavenger_stronghold")],
        "nether_foundries": ["nether_foundry", "nether_foundry_derelict"],
        "research_gates": [n for n, _ in GATES],
        "nether_stations": ["research_nether", "research_nether_derelict"],   # 9-42: Incursion quest chapter
        "end_stations": ["research_end", "research_end_derelict"],
    }
    for name, ids in tags.items():
        for n in ids: assert (OUT / f"worldgen/structure/{n}.json").exists(), n
        w(T / f"{name}.json", {"replace": False, "values": [f"dying_world:{n}" for n in ids]})
    print(f"9-16: settlements set ({len(SETTLE)} structures), landmarks set ({len(LAND)}), {len(OLD_SETTLE) + len(OLD_LAND)} old sets removed")

if __name__ == "__main__":
    main()
