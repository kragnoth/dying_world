import zipfile, re, io, json, sys, os
from pathlib import Path
from PIL import Image
INST = Path(sys.argv[1]); KJ = Path(sys.argv[2]); OUT = Path(sys.argv[3])
PAT = re.compile(r'^assets/([a-z0-9_.-]+)/textures/items?/(.+)\.png$')
def cat(name):
    n = name.split('/')[-1]
    if 'nugget' in n: return 'nugget'
    if 'ingot' in n: return 'ingot'
    if re.search(r'(^|_)dust($|_)', n) or n.endswith('dust') and 'industrial' not in n: return 'dust'
    return None
eff = {}; jar_ids = set(); srcs = []
mods = sorted((INST / 'mods').glob('*.jar'))
def scan_zip(zp, label, prefix='', register=False):
    try: z = zipfile.ZipFile(zp)
    except Exception: return
    for n in z.namelist():
        nn = n[len(prefix):] if prefix and n.startswith(prefix) else (None if prefix else n)
        if not nn: continue
        m = PAT.match(nn)
        if not m: continue
        c = cat(m.group(2))
        if not c: continue
        key = (m.group(1), m.group(2))
        if register: jar_ids.add(key)
        eff[key] = (label, c, z.read(n))
for j in mods: scan_zip(j, 'jar:' + j.name, register=True)
for rp in ["Excalibur_V26.3_01.zip","FarnersDelightExcaliburSupport_1.21.1.zip","Excalibur_Supplementaries_1.1_1.20.1.zip","MyNethersDelight_Excalibur_1.21.1_ver-2.2.zip",
           "Excalibur_Create-6 Addon_Forge_v2.32.zip","Excalibur-Vanilla-Backport-2.3.zip","Excalibur-Sophisticated-v1.2.1.zip","Excalibur-Jei-Support-1.6.zip",
           "Excalibur Waystones 1.1.zip","Excalibur Fallen Adventurers 1.3.zip","Excalibur Amendments 1.7.zip","HumanEraVillagersIllagers[3.91.6].zip","HollowDead.zip"]:
    scan_zip(INST / 'resourcepacks' / rp, 'rp:' + rp)
for p in KJ.rglob('*.png'):
    rel = 'assets/' + p.relative_to(KJ).as_posix(); m = PAT.match(rel)
    if m and cat(m.group(2)):
        key = (m.group(1), m.group(2)); eff[key] = ('kubejs/assets', cat(m.group(2)), p.read_bytes())
        if m.group(1) in ('kubejs', 'arkaneworx'): jar_ids.add(key)
for j in mods:
    if 'cultivar' in j.name.lower(): scan_zip(j, 'cultivar:excalibur_style', prefix='resourcepacks/excalibur_style/')
OUT.mkdir(parents=True, exist_ok=True); rows = []
for (ns, path), (src, c, data) in sorted(eff.items()):
    if (ns, path) not in jar_ids and ns != 'minecraft': continue
    fn = f"{ns}__{path.replace('/', '__')}.png"; (OUT / fn).write_bytes(data)
    rows.append({"id": f"{ns}:{path}", "cat": c, "src": src, "file": fn})
json.dump(rows, open(OUT / 'index.json', 'w'), indent=1)
print(len(rows), {c: sum(r['cat'] == c for r in rows) for c in ('ingot', 'nugget', 'dust')})
