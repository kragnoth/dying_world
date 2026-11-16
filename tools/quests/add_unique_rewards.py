#!/usr/bin/env python3
"""
add_unique_rewards.py - pass 9-43: the Incursion quests hand out the Guild uniques (see tools/gen_pass9_43.py).
Adds one command reward per quest; skips a quest that already has it. Usage: python3 -I add_unique_rewards.py <config/ftbquests/quests>
"""
import hashlib, re, sys
from pathlib import Path
Q = Path(sys.argv[1]); CH = Q / "chapters/6e5c1a7d0b9f4a21.snbt"
def nid(key):
    h = int(hashlib.sha1(("gh-occult/" + key).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF
    return f"{h:016X}"
REWARDS = {"inc/foundry": "gales_bank_shovel", "inc/listening": "brandts_waxed_hood", "inc/far": "marshs_field_boots",
           "inc/opened": "penitents_lamp"}
s = CH.read_text()
for key, uid in REWARDS.items():
    qid, rid = nid(key), nid(key + "/unique")
    if rid in s: continue
    m = re.search(r'\n(\t\t\t)id: "%s"\n\t\t\trewards: \[' % qid, s); assert m, key
    block = ('\n\t\t\t\t{\n\t\t\t\t\tcommand: "/hallmarked generate for {p} 1 unique=%s"\n\t\t\t\t\tid: "%s"\n'
             '\t\t\t\t\tpermission_level: 2\n\t\t\t\t\tsilent: true\n\t\t\t\t\ttype: "command"\n\t\t\t\t}') % (uid, rid)
    s = s[:m.end()] + block + s[m.end():]
CH.write_text(s)
LANG = Q / "lang/en_us.snbt"; l = LANG.read_text()
NOTE = {"inc/foundry": "Gale's banking shovel is yours now. Strike it at an assay anvil to read it.",
        "inc/listening": "Brandt's waxed hood is yours now. Strike it at an assay anvil to read it.",
        "inc/far": "Marsh's field boots are yours now. Strike them at an assay anvil to read them.",
        "inc/opened": "The hermit's lamp is yours now. Strike it at an assay anvil to read it."}
for key, line in NOTE.items():
    pat = re.compile(r'(\tquest\.%s\.quest_desc: \[.*)\]\n' % nid(key))
    m = pat.search(l); assert m, key
    if line in m.group(1): continue
    l = l[:m.start()] + m.group(1) + ', "%s"]\n' % line + l[m.end():]
LANG.write_text(l)
print("unique rewards added")
