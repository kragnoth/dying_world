#!/usr/bin/env python3
"""
add_escapement_quests.py - pass 9-48: the Incursion chapter carries the Foundry Residue ramp and the Escapement.
  Residue tier tags (gh_residue_<n>, read by kubejs 75_foundry_residue.js) as silent command rewards:
    1 The Apprentice; 2 The Gatehouse; 3 Requisitions / The Tidewell / The Listening Post; 4 Station Below / Far Station
    (5 = Hollowed, set by the Hollow script).
  NEW quests: 'What the Foundry Leaves' (first Foundry Residue, after The Apprentice) and 'The Escapement' (after What They Opened).
Idempotent. Usage: python3 -I add_escapement_quests.py <config/ftbquests/quests>
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import snbt
from snbt import Num

Q = Path(sys.argv[1]); CH = Q / "chapters/6e5c1a7d0b9f4a21.snbt"; LANG = Q / "lang/en_us.snbt"
def nid(key): return f"{int(hashlib.sha1(('gh-occult/' + key).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF:016X}"
def d(v): return Num(float(v), "d")
def esc(s): return snbt.q(s)
BIG = Num(0x2CC2AA7605FDDBAC, "L")

TIERS = {"inc/apprentice": 1, "inc/gatehouse": 2, "inc/proving": 3, "inc/tidewell": 3, "inc/listening": 3, "inc/below": 4, "inc/far": 4}

NEW = [
    ("inc/residue", 2.5, 2.75, "gearwrights:foundry_residue", "gearwrights:foundry_residue", [nid("inc/apprentice")],
     [{"id": nid("inc/residue/xp"), "type": "xp", "xp": 60}],
     "What the Foundry Leaves", "Foundry Residue",
     ["Grit that should not be there: in the deepslate, in the ash of things that should have stayed dead. Only those who see the Foundry find it.",
      "Keep it. The Guild's ledgers count it by the ounce, and the further down their trail you go, the more of it you will find."]),
    ("inc/escapement", 18, 0, "gearwrights:escapement", "gearwrights:escapement", [nid("inc/opened")],
     [{"id": nid("inc/escapement/xp"), "type": "xp", "xp": 400}, {"id": nid("inc/escapement/table"), "table_id": BIG, "type": "random"}],
     "The Escapement", "The world runs on without asking",
     ["Build a movement from residue, shadow steel and refined radiance; bleed it on an altar; wind it with the void; set it on the Hollow's altar.",
      "The first one lets you go. After that the Foundry is behind a lens, and every Escapement it gives you costs Distilled Residue gathered through it.",
      "An Escapement sits at the heart of every creative machine the Guild ever built."]),
]

def main():
    s = CH.read_text()
    for key, tier in TIERS.items():
        qid, rid = nid(key), nid(f"{key}/residue_tier")
        if rid in s: continue
        m = re.search(r'\n\t\t\tid: "%s"\n\t\t\trewards: \[' % qid, s); assert m, key
        s = s[:m.end()] + ('\n\t\t\t\t{\n\t\t\t\t\tcommand: "/tag {p} add gh_residue_%d"\n\t\t\t\t\tid: "%s"\n'
                           '\t\t\t\t\tpermission_level: 2\n\t\t\t\t\tsilent: true\n\t\t\t\t\ttype: "command"\n\t\t\t\t}') % (tier, rid) + s[m.end():]
    lines = []
    for key, x, y, icon, it, deps, rewards, ttl, sub, desc in NEW:
        if f'id: "{nid(key)}"' in s: continue
        qd = {"dependencies": deps, "icon": {"id": icon}, "id": nid(key), "rewards": rewards,
              "tasks": [{"consume_items": False, "id": nid(key + "/task"), "item": {"count": 1, "id": it}, "type": "item"}], "x": d(x), "y": d(y)}
        m = list(re.finditer(r"\n\t\t\}\n\t\]\n", s)); assert m
        cut = m[-1].start() + len("\n\t\t}")
        s = s[:cut] + "\n\t\t" + snbt.dump(qd, 2) + s[cut:]
        lines += [f'\tquest.{nid(key)}.title: {esc(ttl)}', f'\tquest.{nid(key)}.quest_subtitle: {esc(sub)}',
                  f'\tquest.{nid(key)}.quest_desc: [' + ", ".join(esc(x) for x in desc) + "]"]
    CH.write_text(s)
    if lines:
        lang = LANG.read_text().rstrip(); assert lang.endswith("}")
        LANG.write_text(lang[:-1].rstrip("\n") + "\n" + "\n".join(lines) + "\n}\n")
    print("escapement quests applied")

if __name__ == "__main__":
    main()
