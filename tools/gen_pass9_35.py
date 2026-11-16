#!/usr/bin/env python3
"""
gen_pass9_35.py - pass 9-35: UNDERGROUND SITES GROW PROPERLY (user: a proving grounds spawned as the hub + a few side rooms; progression needs the full site).
Run AFTER gen_pass9_12 and gen_pass9_34 (patches 9-12's hub NBTs + pools), before 9_16. Safe to re-run (only rewrites pool fields and copies).
CAUSE: all three hub doorways drew from one mixed 'wings' pool where 12 of 27 weight leads on; rooms are dead ends, so most sites stopped after ring 1.
FIX (pool wiring, no new buildings), for sunken / proving / sculk:
  hub doorways -> a SPINE corridor (copy of corridor_9 / corridor_15 whose far end opens the next pool), never a room;
    proving: west spine ends in the VAULT ROOM, east spine in the BREEZE TUNNEL (guaranteed specials; fallback = cap if it can't fit),
             north spine -> junctions;  sunken / sculk: all three spines -> junctions.
  junctions pool = tee / cross / corner (+ a short corridor) whose ends open the old mixed 'wings' pool (rooms + more corridors).
  jigsaw size +2 (sunken/sculk 6 -> 8, proving 10 -> 12) for the two extra rings.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbtrw
from gen_pass9_11 import pe
from gen_pass4_2a import w, OUT

SITES = {"sunken": "sunken_research_lab", "proving": "proving_grounds"}   # 9-36: sculk is rebuilt as the dig camp

def jig_pools(s):
    return [(p, pr, nb) for p, (n, pr, nb) in s.b.items() if n == "minecraft:jigsaw"]

def set_pool(s, pos, pool):
    n, pr, nb = s.b[pos]; d = dict(nb[1]); d["pool"] = (8, pool); s.b[pos] = (n, pr, (10, d))

def copy_with_pool(d, src, dst, pool):
    s = nbtrw.Struct((d / f"{src}.nbt").read_bytes())
    for pos, pr, nb in jig_pools(s):
        if nb[1]["name"][1] == "dying_world:station": set_pool(s, pos, pool)
    (d / f"{dst}.nbt").write_bytes(s.bytes())

def main():
    for site, name in SITES.items():
        d = OUT / f"structure/station/{site}"; base = f"dying_world:station/{site}"; tp = OUT / f"worldgen/template_pool/station/{site}"
        for f in ("hub", "corridor_9", "corridor_15", "tee", "cross", "corner", "cap"): assert (d / f"{f}.nbt").exists(), (site, f)
        # junction ring: the junction pieces already open the mixed 'wings' pool
        w(tp / "junctions.json", {"fallback": f"{base}/caps", "elements": [pe(f"{base}/tee", 3), pe(f"{base}/cross", 2), pe(f"{base}/corner", 2), pe(f"{base}/corridor_9", 1)]})
        spines = {"main": f"{base}/junctions"}
        if site == "proving":
            assert (d / "vault_room.nbt").exists() and (d / "breeze_tunnel.nbt").exists()
            w(tp / "vault_end.json", {"fallback": f"{base}/caps", "elements": [pe(f"{base}/vault_room", 1)]})
            w(tp / "breeze_end.json", {"fallback": f"{base}/caps", "elements": [pe(f"{base}/breeze_tunnel", 1)]})
            spines.update(vault=f"{base}/vault_end", breeze=f"{base}/breeze_end")
        for key, nxt in spines.items():
            for L in (9, 15): copy_with_pool(d, f"corridor_{L}", f"spine_{key}_{L}", nxt)
            w(tp / f"spine_{key}.json", {"fallback": f"{base}/caps", "elements": [pe(f"{base}/spine_{key}_9", 1), pe(f"{base}/spine_{key}_15", 1)]})
        # hub doorways (orientation in the hub's own frame): west / north / east
        face = {"west_up": "vault" if site == "proving" else "main", "north_up": "main", "east_up": "breeze" if site == "proving" else "main"}
        s = nbtrw.Struct((d / "hub.nbt").read_bytes()); done = 0
        for pos, pr, nb in jig_pools(s):
            if nb[1]["name"][1] == "dying_world:station" and pr.get("orientation") in face:
                set_pool(s, pos, f"{base}/spine_{face[pr['orientation']]}"); done += 1
        assert done == 3, (site, done)
        (d / "hub.nbt").write_bytes(s.bytes())
        sp = OUT / f"worldgen/structure/{name}.json"; j = json.loads(sp.read_text())
        j["size"] = 12 if site == "proving" else 8; w(sp, j)
    print("9-35: hub -> spine corridors -> junction ring -> wings for sunken / proving / sculk (proving: guaranteed vault room + breeze tunnel)")

if __name__ == "__main__":
    main()
