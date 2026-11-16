"""village_biomes.py - assign every surface biome (vanilla + modded, from reference/) to AT MOST ONE village family.
Used by gen_pass3c4.py. Rules are tag-driven so modded biomes (Regions Unexplored, Atmospheric, Environmental, Windswept, Autumnity...) follow
automatically; re-run after the modlist changes (and refresh reference/)."""
import biome_tags as bt
R = bt.resolve
def T(*tags):
    s = set()
    for t in tags: s |= R(t)
    return s
ALL = set(bt.ALL_BIOMES)
KEEP_MOUNTAINISH = {"minecraft:meadow", "minecraft:cherry_grove", "minecraft:grove"}   # vanilla village-friendly despite mountain tags
WET = T("c:is_swamp", "minecraft:is_jungle", "c:is_tree/jungle", "minecraft:is_beach", "minecraft:is_river", "minecraft:is_ocean",
        "minecraft:is_deep_ocean", "c:is_shallow_ocean", "c:is_mushroom", "c:is_stony_shores")          # reserved for survivor bunkers / nothing
NOPE = T("minecraft:is_nether", "minecraft:is_end", "c:is_cave", "c:caves", "c:is_dead", "c:is_wasteland", "c:is_spooky", "c:is_dark_forest",
         "c:is_mountain/peak", "c:is_mountain/slope") | (T("minecraft:is_mountain", "minecraft:is_hill") - KEEP_MOUNTAINISH)
NOPE |= {b for b in ALL if any(k in b for k in ("cave", "deeps", "lush", "dripstone", "deep_dark", "void", "mushroom"))}
NOPE |= {"minecraft:dark_forest", "regions_unexplored:bamboo_forest"}   # dark forest = spooky; bamboo = jungle-like (wet)
EXCLUDED = (WET | NOPE) - KEEP_MOUNTAINISH
# vanilla biomes are missing from the neoforge c: tags (those live in the neoforge jar, not in reference/): seed them by hand
SEEDS = {"plains": {"minecraft:plains", "minecraft:sunflower_plains", "atmospheric:aspen_parkland", "windswept:lavender_fields"},
         "desert": {"minecraft:desert"}, "snowy": {"minecraft:snowy_plains", "minecraft:ice_spikes", "regions_unexplored:tundra"}}
snowy, forest = T("c:is_snowy", "c:is_icy", "c:is_cold", "c:is_snowy_plains"), T("minecraft:is_forest", "c:is_birch_forest", "c:is_flower_forest")
RULES = [  # first match wins -> families are disjoint
    ("taiga",   lambda b: b in R("minecraft:is_taiga") or (b in snowy and b in forest) or b == "minecraft:grove"),
    ("snowy",   lambda b: b in snowy),
    ("desert",  lambda b: b in T("c:is_desert", "minecraft:is_badlands", "c:is_sandy")),
    ("savanna", lambda b: b in T("minecraft:is_savanna", "c:is_tree/savanna")),
    ("plains",  lambda b: b in T("c:is_plains") or b in forest or b in KEEP_MOUNTAINISH),
]
def families():
    fam = {f: [] for f, _ in RULES}; unassigned = []
    for b in sorted(ALL):
        if b in EXCLUDED: continue
        for f, rule in RULES:
            if b in SEEDS.get(f, ()) or rule(b): fam[f].append(b); break
        else: unassigned.append(b)
    return fam, unassigned
if __name__ == "__main__":
    fam, un = families()
    for f, v in fam.items(): print(f, len(v), ", ".join(x.replace("minecraft:", "") for x in v))
    print("unassigned:", ", ".join(un))
