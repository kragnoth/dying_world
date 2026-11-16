#!/usr/bin/env python3
"""
gen_pass9_9.py - pass 9-9: MINESHAFT SPAWNER ROOMS (user decision after the 9-8 walkthrough: overworld XP farms were impossible - monster rooms removed in pass 2).
Run after gen_pass4_2b.py (appends to dying_world:mineshaft/rooms). Safe to re-run.
3 rooms (11x6x9, same door jigsaw as every mineshaft room): spawner_zombie / spawner_skeleton / spawner_spider. Rebar-heavy cell, mob spawner on a mossy plinth
in the middle (vanilla spawner defaults), cobwebs, bones/skull clutter, dead floodlight, one chest with the VANILLA DUNGEON loot (chests/mineshaft_dungeon = copy of
chests/simple_dungeon: saddles, name tags, music discs, golden apples ... which also had no source any more). Unlit, so the spawner works.
Weight 1 each in the rooms pool (~3 in 23 door alcoves).
"""
import json, random, sys, zipfile, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import S as NS
from gen_pass4_2a import M, R, w, elem, OUT
from gen_pass4_2b import shell

ROOT = Path(__file__).resolve().parent.parent
LOOTZ = zipfile.ZipFile(ROOT / "reference/loot_and_recipes.zip")

def room(mob, seed):
    t, r = shell(seed, "spawner_" + mob, rebar=True)
    t.set(5, 1, 5, M("mossy_cobblestone"))
    t.set(5, 2, 5, M("spawner"), None, {"id": M("mob_spawner"), "SpawnData": (10, {"entity": (10, {"id": NS(M(mob))})})})
    for (x, z) in ((1, 1), (9, 1), (1, 7), (9, 7), (2, 7), (8, 1)):
        t.set(x, 4 if (x + z) % 2 else 1, z, M("cobweb"))
    for (x, z) in ((3, 6), (7, 3), (2, 4)): t.set(x, 1, z, M("bone_block"), {"axis": r.choice("xyz")}) if r.random() < .6 else None
    t.set(7, 1, 6, M("skeleton_skull"), {"rotation": str(r.randint(0, 15)), "powered": "false"})
    t.set(9, 1, 6, M("chest"), {"facing": "west", "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": "dying_world:chests/mineshaft_dungeon"})
    t.set(9, 3, 4, R("sodium_floodlight"), {"facing": "west", "lit": "false"})        # mounted on the east wall, dead
    t.set(1, 2, 2, R("sign_danger"), {"facing": "east"}) if r.random() < .7 else None
    return t

def main():
    N = OUT / "structure/mineshaft"; names = []
    for i, mob in enumerate(("zombie", "skeleton", "spider")):
        (N / f"spawner_{mob}.nbt").write_bytes(room(mob, i + 1).bytes()); names.append(f"spawner_{mob}")
    p = OUT / "worldgen/template_pool/mineshaft/rooms.json"; j = json.loads(p.read_text())
    j["elements"] = [e for e in j["elements"] if "spawner_" not in json.dumps(e)]
    j["elements"][-1:-1] = [elem(n, 1) for n in names]                      # before the empty element
    w(p, j)
    lt = json.loads(LOOTZ.read("data/minecraft/loot_table/chests/simple_dungeon.json")); lt.pop("random_sequence", None)
    w(OUT / "loot_table/chests/mineshaft_dungeon.json", lt)
    print(f"9-9: {len(names)} spawner rooms added to mineshaft rooms pool; loot chests/mineshaft_dungeon = vanilla simple_dungeon")

if __name__ == "__main__":
    main()
