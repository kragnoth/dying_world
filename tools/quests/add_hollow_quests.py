#!/usr/bin/env python3
"""
add_hollow_quests.py - pass 9-44: the Incursion finale goes through the Hollow.
  The Guild's Own Mark (Seal) also hands out the map to the Hollow (/loot give ... dying_world:map/the_hollow).
  What They Opened: checkmark -> gamestage task 'gh_hollow_defeated' (set by kubejs 60_the_hollow.js when your copy dies).
Idempotent. Usage: python3 -I add_hollow_quests.py <config/ftbquests/quests>
"""
import hashlib, re, sys
from pathlib import Path
Q = Path(sys.argv[1]); CH = Q / "chapters/6e5c1a7d0b9f4a21.snbt"; LANG = Q / "lang/en_us.snbt"
def nid(key):
    return f"{int(hashlib.sha1(('gh-occult/' + key).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF:016X}"

s = CH.read_text()
seal, opened = nid("inc/seal"), nid("inc/opened")
rid = nid("inc/seal/hollow_map")
if rid not in s:
    m = re.search(r'\n\t\t\tid: "%s"\n\t\t\trewards: \[' % seal, s); assert m
    s = s[:m.end()] + ('\n\t\t\t\t{\n\t\t\t\t\tcommand: "/loot give {p} loot dying_world:map/the_hollow"\n\t\t\t\t\tid: "%s"\n'
                       '\t\t\t\t\tpermission_level: 2\n\t\t\t\t\tsilent: true\n\t\t\t\t\ttype: "command"\n\t\t\t\t}') % rid + s[m.end():]
tid = nid("inc/opened/task")
old = '\t\t\t\t{\n\t\t\t\t\tid: "%s"\n\t\t\t\t\ttype: "checkmark"\n\t\t\t\t}' % tid
if old in s:
    s = s.replace(old, '\t\t\t\t{\n\t\t\t\t\tid: "%s"\n\t\t\t\t\tstage: "gh_hollow_defeated"\n\t\t\t\t\ttype: "gamestage"\n\t\t\t\t}' % tid)
assert 'stage: "gh_hollow_defeated"' in s, "finale task not found"
CH.write_text(s)

l = LANG.read_text()
ADD = {seal: "The seal fits one lock the Guild never sold. The register with it marks the way to the Hollow.",
       opened: "Take a seal down to the dais in the Hollow and set it on the altar. What comes up is wearing your face, and your gear."}
for q, line in ADD.items():
    m = re.search(r'(\tquest\.%s\.quest_desc: \[.*)\]\n' % q, l); assert m, q
    if line not in m.group(1): l = l[:m.start()] + m.group(1) + ', "%s"]\n' % line + l[m.end():]
l = l.replace('\tquest.%s.title: "What They Opened"\n' % opened,
              '\tquest.%s.title: "What They Opened"\n\ttask.%s.title: "Put down what waits in the Hollow"\n' % (opened, tid)) \
    if 'task.%s.title' % tid not in l else l
LANG.write_text(l)
print("hollow quests applied")
