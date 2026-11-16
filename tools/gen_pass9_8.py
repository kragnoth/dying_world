#!/usr/bin/env python3
"""
gen_pass9_8.py - pass 9-8: gameplay-walkthrough fixes (see docs/gameplay_walkthrough.md). Post-edit after 9_7. Safe to re-run.
- #minecraft:village now also lists our 5 survivor villages (used by /locate, maps, some mods' 'near a village' checks).
- explorer-map / treasure-map tags pointed at structures that exist in this world (vanilla targets are all disabled):
  woodland explorer map -> scavenger stronghold (bastion loot, netherite template), ocean explorer map -> sunken research lab (9-12; was lighthouse),
  trial-chamber map -> proving grounds (9-12; was industrial mineshaft), buried-treasure map (shipwreck map chests, dolphins) -> beached shipwreck.
(Forge now also carries a fletching table + stonecutter so fletchers/masons exist in every family - change lives in gen_pass7_1.forge.)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pass4_2a import w, OUT
T = OUT.parent / "minecraft/tags/worldgen/structure"
w(T / "village.json", {"replace": False, "values": [f"dying_world:village_{f}" for f in ("plains", "taiga", "snowy", "desert", "savanna")]})
for tag, sid in (("on_woodland_explorer_maps", "dying_world:scavenger_stronghold"), ("on_ocean_explorer_maps", "dying_world:sunken_research_lab"),
                 ("on_trial_chambers_maps", "dying_world:proving_grounds"), ("on_treasure_maps", "dying_world:shipwreck_beached")):
    w(T / f"{tag}.json", {"replace": True, "values": [sid]})
print("9-8: #minecraft:village += our villages; 4 map tags retargeted")
