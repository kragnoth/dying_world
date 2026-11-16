#!/usr/bin/env python3
"""
gen_pass9_29.py - pass 9-29: four landmarks REMOVED (abandoned_watchtower, burnt_homestead, burnt_manor, burnt_watchtower - user: 'don't fit the flow anymore')
and replaced by three SURVIVOR landmarks, each with one master-level (level 5) character with fixed rare trades. Run after 9_24 + 8_5, before 9_16. Safe to re-run.
  hermit_cottage   : lit fieldstone cottage (temperate + cold biomes), 'Old Hermit' = master CLERIC: ender pearls, Mending book, totem, heart of the sea, XP bottles.
  tinker_workshop  : brick forge (any land), 'Tinker' = master TOOLSMITH: netherite upgrade template, enchanted diamond pickaxe, coast/wild trims, name tags, rebar.
  plague_house     : boarded-up, unlit ruined dogtrot (temperate + wild), a ZOMBIE VILLAGER master LIBRARIAN locked inside - cure him (weakness + golden apple)
                     and he keeps his trades: Mending / Protection IV / Unbreaking III books, name tags, golden apples.
Characters: PersistenceRequired, Xp 250 (level 5 never loses its profession), fixed Offers (vanilla 1.21 MerchantOffer NBT), limited uses (most 1-3).
"""
import json, random, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import S as NS, I as NI, B as NB, F as NF, L as NL
from savanna_kit import B
import gen_pass7_1 as S
import gen_pass9_21          # registers r_brick
from gen_pass4_2a import M, w, OUT

GONE = ("abandoned_watchtower", "burnt_homestead", "burnt_manor", "burnt_watchtower")
def item(i, n=1, comp=None):
    d = {"id": NS(f"minecraft:{i}" if ":" not in i else i), "count": NI(n)}
    if comp: d["components"] = (10, comp)
    return (10, d)
def book(ench, lvl): return item("enchanted_book", 1, {"minecraft:stored_enchantments": (10, {"levels": (10, {f"minecraft:{ench}": NI(lvl)})})})
def offer(buy, sell, uses, buyB=None, xp=30):
    o = {"buy": buy, "sell": sell, "uses": NI(0), "maxUses": NI(uses), "rewardExp": NB(1), "xp": NI(xp), "priceMultiplier": NF(.05), "specialPrice": NI(0), "demand": NI(0)}
    if buyB: o["buyB"] = buyB
    return o
EM = lambda n: item("emerald", n)
TRADES = {
    "hermit": [offer(EM(12), item("ender_pearl", 2), 6), offer(EM(10), item("experience_bottle", 4), 6), offer(EM(24), book("mending", 1), 1, item("book")),
               offer(EM(28), item("totem_of_undying"), 1), offer(EM(30), item("heart_of_the_sea"), 1)],
    "tinker": [offer(EM(32), item("netherite_upgrade_smithing_template"), 1, item("diamond")),
               offer(EM(26), item("diamond_pickaxe", 1, {"minecraft:enchantments": (10, {"levels": (10, {"minecraft:efficiency": NI(4), "minecraft:unbreaking": NI(3)})})}), 1),
               offer(EM(14), item("coast_armor_trim_smithing_template"), 1), offer(EM(18), item("wild_armor_trim_smithing_template"), 1),
               offer(EM(6), item("name_tag"), 3), offer(EM(4), item("rustandrebar:rebar_bundle", 8), 6)],
    "plague": [offer(EM(20), book("mending", 1), 1, item("book")), offer(EM(22), book("protection", 4), 1, item("book")),
               offer(EM(18), book("unbreaking", 3), 2, item("book")), offer(EM(6), item("name_tag"), 3), offer(EM(12), item("golden_apple", 2), 2)],
}
def character(kind, entity, prof, name, biome="plains"):
    return {"id": NS(f"minecraft:{entity}"), "PersistenceRequired": NB(1), "Xp": NI(250), "CustomName": NS(json.dumps(name)),
            "VillagerData": (10, {"type": NS(f"minecraft:{biome}"), "profession": NS(f"minecraft:{prof}"), "level": NI(5)}),
            "Offers": (10, {"Recipes": NL(10, [o for o in TRADES[kind]])})}

def free_cell(t, r, xs=None, zs=None):
    cells = []
    for (x, y, z), (n, _, _) in t.b.items():
        if y != 1 or n != M("air") or (xs and x not in xs) or (zs and z not in zs): continue
        if t.b.get((x, 2, z), ("",))[0] != M("air"): continue
        below = t.b.get((x, 0, z), ("",))[0]
        if below in ("", M("air")) or "jigsaw" in below: continue
        if not any(t.b.get((x, yy, z), ("",))[0] not in ("", M("air")) for yy in range(3, t.sy)): continue    # under a roof
        cells.append((x, z))
    r.shuffle(cells); return cells[0]

def setfam(wood, smap, prefix):
    S.WOOD, S.STYLE_MAP, S.PREFIX, S.FAMILY = wood, smap, prefix, "plains"
    B.STEEP = B.FLAT = False; B.GROUND = ("dirt_path", "coarse_dirt", "grass_block", "coarse_dirt")

def build():
    D = OUT / "structure/landmarks"; D.mkdir(parents=True, exist_ok=True); r = random.Random(29)
    setfam("spruce", {"creole": "fieldstone", "limestone": "fieldstone", "hacienda": "fieldstone"}, "hermit_")
    t = S.creole_cottage(1).finalize("base"); x, z = free_cell(t, r, xs=range(2, 7), zs=range(2, 6))      # base = lived look without the villager jigsaw (one hermit only)
    t.entity(x + .5, 1, z + .5, character("hermit", "villager", "cleric", "Old Hermit"))
    (D / "hermit_cottage.nbt").write_bytes(t.bytes())
    setfam("dark_oak", {"creole": "r_brick", "limestone": "r_brick", "hacienda": "r_brick"}, "tinker_")
    t = S.forge(1).finalize("base"); x, z = free_cell(t, r)
    t.entity(x + .5, 1, z + .5, character("tinker", "villager", "toolsmith", "Tinker"))
    for p, (n, pr, nb) in list(t.b.items()):                                  # a little dieselpunk flavor on the forge
        if n == M("barrel") and r.random() < .5: t.b[p] = ("rustandrebar:rusted_drum", (("axis", "y"),), None)
    (D / "tinker_workshop.nbt").write_bytes(t.bytes())
    setfam("oak", {"creole": "fieldstone", "limestone": "fieldstone", "hacienda": "fieldstone"}, "plague_")   # (farmhouse tops out in white plaster)
    t = S.dogtrot(1).finalize("ruined")
    for p, (n, pr, nb) in list(t.b.items()):                                  # boarded up and dark
        if n in (M("glass_pane"),): t.b[p] = (M("oak_planks"), (), None)
        elif n.endswith("_door"): t.b[p] = (M("iron_bars") if dict(pr).get("half") == "upper" else M("oak_planks"), (), None)
        elif n in (M("lantern"), M("torch"), M("wall_torch")): t.b[p] = (M("air"), (), None)
    x, z = free_cell(t, r, xs=(2, 3))                                       # inside the sealed west pen, not the breezeway
    t.entity(x + .5, 1, z + .5, dict(character("plague", "zombie_villager", "librarian", "Quarantined Scholar"), CanBreakDoors=NB(0)))
    t.set(x, 1, z - 1 if z > 1 else z + 1, M("cobweb")) if t.b.get((x, 1, z - 1), ("",))[0] == M("air") else None
    (D / "plague_house.nbt").write_bytes(t.bytes())

def el(loc): return {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}
def register():
    tmpl = json.loads((OUT / "worldgen/structure/ruined_chapel.json").read_text())
    for name, biomes, spawns in (("hermit_cottage", ["#dying_world:has_structure/concrete_pad_temperate", "#dying_world:has_structure/concrete_pad_cold"], {}),
                                 ("tinker_workshop", ["#dying_world:has_structure/scavenger_outpost_any"], {}),
                                 ("plague_house", ["#dying_world:has_structure/concrete_pad_temperate", "#dying_world:has_structure/concrete_pad_wild"], None)):
        w(OUT / f"worldgen/template_pool/landmarks/{name}.json", {"fallback": "minecraft:empty", "elements": [el(f"dying_world:landmarks/{name}")]})
        w(OUT / f"tags/worldgen/biome/has_structure/{name}.json", {"replace": False, "values": biomes})
        j = dict(tmpl); j.update({"biomes": f"#dying_world:has_structure/{name}", "start_pool": f"dying_world:landmarks/{name}", "size": 1, "max_distance_from_center": 32,
                                  "terrain_adaptation": "beard_box"})
        if spawns is not None: j["spawn_overrides"] = spawns
        w(OUT / f"worldgen/structure/{name}.json", j)

def remove():
    for n in GONE:
        for p in (OUT / f"worldgen/structure/{n}.json", OUT / f"tags/worldgen/biome/has_structure/{n}.json", OUT / f"worldgen/template_pool/landmarks/{n}.json"):
            if p.exists(): p.unlink()
        for p in (OUT / "structure/landmarks").glob(f"{n}_*.nbt"): p.unlink()
    for p in (OUT / "worldgen/template_pool/watchtower").glob("*.json"): p.unlink()
    for p in (OUT / "structure/watchtower").glob("*.nbt"): p.unlink()

def main():
    remove(); build(); register()
    print("9-29: removed", ", ".join(GONE), "-> hermit_cottage, tinker_workshop, plague_house (master characters with fixed rare trades)")

if __name__ == "__main__":
    main()
