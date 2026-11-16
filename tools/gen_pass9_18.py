#!/usr/bin/env python3
"""
gen_pass9_18.py - pass 9-18: NETHER FORTRESS REMOVED, its roles replaced (user: 'do 1 and 2'). Run after 9_15, before 9_16. Safe to re-run.
(1) NETHER RESEARCH STATION gains a BLAZE CONTAINMENT building (buildings pool, w3): nether-brick block house, iron-bar cage round a BLAZE SPAWNER on magma,
    observation desk, chest = vanilla nether_bridge loot + RIB trim pool. Station spawns += WITHER SKELETONS (zombie 3 / skeleton 3 / wither skeleton 2).
    Rib trim pool also in the station store chests.
(2) NEW dying_world:nether_foundry - dieselpunk foundry outpost on BRIDGES (fortress feel): rigid jigsaw, terrain_adaptation none, start y 48-72.
    Every piece has its walking deck at local y12 with nether-brick support columns down to y0; empty space = structure_void (terrain kept), the walkway
    space above decks = air (bridges tunnel through netherrack like fortress corridors). Connector dying_world:foundry (y13, face centre).
    Pieces: foundry hall (start: blast furnaces, lava cauldrons, anvil, R&R pumps/pipes/drums/cogwheels, store chest), bridge 13 (w5), bridge 7 (w3),
    cross + tee platforms, BLAZE KILN (open platform, blaze spawner in a fence cage), BARRACKS (dark nether-brick room, chest), WART TERRACE (soul sand +
    nether wart), railing caps (fallback). spawn_overrides = vanilla fortress mix (blaze 10, wither skeleton 8, zombified piglin 5, magma cube 3, skeleton 2).
    Chests = vanilla nether_bridge + rib trim pool (15%). Set dying_world:nether_foundries 26/9.
Fortress off: dying_world:nether_fortress set deleted (minecraft:nether_complexes was already empty); nether station exclusion -> foundries;
'A Terrible Fortress' advancement (minecraft:nether/find_fortress) now completes in the foundry.
"""
import json, sys, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbtw import Tpl
from buildkit import M, R, rng, fix_connections, connect_pipes, chest as kchest
from gen_pass4_2a import w, item, OUT
import gen_pass9_15 as S
from gen_pass9_11 import ZIP

J = "dying_world:foundry"; FP = "dying_world:foundry"
VOID = M("structure_void")
PIPE = {d: "true" for d in ("north", "east", "south", "west", "up", "down")}
RIB = {"rolls": 1, "entries": [item("rib_armor_trim_smithing_template", 3), {"type": "minecraft:empty", "weight": 17}]}

def nb(r):
    p = r.random()
    return M("nether_bricks") if p < .7 else M("cracked_nether_bricks") if p < .85 else M("red_nether_bricks") if p < .95 else M("chiseled_nether_bricks")

# ---------------- (1) station additions ----------------
def containment():
    b = S.mk("nether", "containment", 9, 13, 10, 8); b.ground(S.GROUND["nether"])
    S.box(b, 0, 8, 0, 8, 6, door_x=4, windows=False)
    b.gable(0, 8, 0, 8, 7, axis="x", over=0)
    for x in range(2, 7):                                          # cage x2..6 z1..5, spawner on magma in the middle
        for z in range(1, 6):
            for y in range(1, 6):
                if x in (2, 6) or z in (1, 5): b.set(x, y, z, M("iron_bars"))
                else: b.set(x, y, z, M("air"))
    b.set(4, 1, 3, M("magma_block"))
    b.set(4, 2, 3, M("spawner"), None, {"id": M("mob_spawner"), "SpawnData": (10, {"entity": (10, {"id": (8, "minecraft:blaze")})})})
    b.set(1, 1, 7, M("crimson_slab"), {"type": "top", "waterlogged": "false"}); b.set(1, 2, 7, M("lectern"), {"facing": "east", "has_book": "false", "powered": "false"})
    b.set(7, 1, 7, M("chest"), {"facing": "west", "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": "dying_world:chests/research_nether_containment"})
    b.set(7, 1, 6, R("sign_danger"), {"facing": "west"}); b.set(1, 1, 6, M("cauldron"))
    S.front(b, 8, 4)
    t = b.finalize("lived"); fix_connections(t); return t

def station():
    d = OUT / "structure/station/nether"; (d / "containment.nbt").write_bytes(containment().bytes())
    for suf in ("", "_derelict"):                                  # 9-23: the derelict nether station gets it too
        p = OUT / f"worldgen/template_pool/station/nether{suf}/buildings.json"
        if not p.exists(): continue
        if suf: (OUT / "structure/station/nether_derelict").mkdir(parents=True, exist_ok=True); (OUT / "structure/station/nether_derelict/containment.nbt").write_bytes((d / "containment.nbt").read_bytes())
        j = json.loads(p.read_text())
        j["elements"] = [e for e in j["elements"] if "containment" not in e["element"]["location"]] + [S.pe(f"dying_world:station/nether{suf}/containment", 3)]
        w(p, j)
    sp = OUT / "worldgen/structure/research_nether.json"; j = json.loads(sp.read_text())
    j["spawn_overrides"] = {"monster": {"bounding_box": "piece", "spawns": [
        {"type": "minecraft:zombie", "weight": 3, "minCount": 2, "maxCount": 4}, {"type": "minecraft:skeleton", "weight": 3, "minCount": 1, "maxCount": 3},
        {"type": "minecraft:wither_skeleton", "weight": 2, "minCount": 1, "maxCount": 2}]}}
    w(sp, j)
    nbr = json.loads(ZIP.read("data/minecraft/loot_table/chests/nether_bridge.json")); nbr.pop("random_sequence", None); nbr["pools"].append(RIB)
    w(OUT / "loot_table/chests/research_nether_containment.json", nbr)
    w(OUT / "loot_table/chests/foundry.json", nbr)
    lp = OUT / "loot_table/chests/research_nether_store.json"; j = json.loads(lp.read_text())
    j["pools"] = [q for q in j["pools"] if "rib_armor" not in json.dumps(q)] + [RIB]; w(lp, j)

# ---------------- (2) foundry outpost on bridges ----------------
DECK = 12
class F:
    def __init__(s, name, sx, sz, h=6):
        s.name, s.t, s.r = name, Tpl(sx, DECK + h + 1, sz), rng("foundry/" + name)
        s.sx, s.sz = sx, sz
        for x in range(sx):
            for z in range(sz):
                for y in range(DECK + h + 1): s.t.set(x, y, z, VOID)
    def b(s, x, y, z, n, p=None, nbt=None): s.t.set(x, y, z, n, p, nbt)
    def deck(s, x0, x1, z0, z1, rail=True, head=3):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                s.b(x, DECK, z, nb(s.r) if s.r.random() < .85 else R("tread_plate"))
                for y in range(DECK + 1, DECK + 1 + head): s.b(x, y, z, M("air"))
                if rail and (x in (x0, x1) or z in (z0, z1)): s.b(x, DECK + 1, z, M("nether_brick_fence"))
    def column(s, x, z):
        for y in range(0, DECK): s.b(x, y, z, nb(s.r))
    def jig(s, face, pool=True):
        x, z, f = {"n": (s.sx // 2, 0, "north"), "s": (s.sx // 2, s.sz - 1, "south"), "w": (0, s.sz // 2, "west"), "e": (s.sx - 1, s.sz // 2, "east")}[face]
        for d in (-1, 0, 1):                                       # open the railing at the connection
            xx, zz = (x + d, z) if face in "ns" else (x, z + d)
            s.b(xx, DECK + 1, zz, M("air"))
        s.b(x, DECK + 1, z, M("jigsaw"), {"orientation": f + "_up"}, {"id": M("jigsaw"), "name": J, "target": J,
            "pool": f"{FP}/wings" if pool else "minecraft:empty", "final_state": M("air"), "joint": "aligned"})
    def lamp(s, x, z):
        for y in (1, 2): s.b(x, DECK + y, z, M("nether_brick_fence"))
        s.b(x, DECK + 3, z, M("soul_lantern"), {"hanging": "false", "waterlogged": "false"})
    def done(s): fix_connections(s.t); connect_pipes(s.t); return s.t

def bridge(L, name):
    f = F(name, 5, L); f.deck(0, 4, 0, L - 1)
    for z in range(0, L, 6):
        f.column(0, z); f.column(4, z)
    f.lamp(0, L // 2) if L > 8 else None
    f.jig("n"); f.jig("s"); return f.done()

def platform(name, faces, size=9):
    f = F(name, size, size); f.deck(0, size - 1, 0, size - 1)
    for x, z in ((0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1), (size // 2, size // 2)): f.column(x, z)
    f.lamp(1, 1); f.lamp(size - 2, size - 2)
    for c in faces: f.jig(c)
    return f.done()

def hall():
    f = F("hall", 15, 15, 9); r = f.r; f.deck(0, 14, 0, 14, rail=False, head=7)
    for x in (0, 7, 14):
        for z in (0, 7, 14): f.column(x, z)
    for x in range(15):                                            # walls (nether brick, red-brick band, R&R plating patches), roof
        for z in range(15):
            edge = x in (0, 14) or z in (0, 14)
            for y in range(DECK + 1, DECK + 8):
                if edge: f.b(x, y, z, M("red_nether_bricks") if y == DECK + 4 else R("red_oxide_plating") if r.random() < .08 else nb(r))
            f.b(x, DECK + 8, z, M("nether_brick_slab") if not edge else nb(r), {"type": "bottom", "waterlogged": "false"} if not edge else None)
    for c in "nswe":
        x, z = {"n": (7, 0), "s": (7, 14), "w": (0, 7), "e": (14, 7)}[c]
        for d in (-1, 0, 1):
            for y in range(DECK + 1, DECK + 4):
                f.b(x + d if c in "ns" else x, y, z if c in "ns" else z + d, M("air"))
        f.jig(c)
    for x in (3, 4):                                               # furnace line + lava pots
        f.b(x, DECK + 1, 2, M("blast_furnace"), {"facing": "south", "lit": "true"})
    f.b(5, DECK + 1, 2, M("lava_cauldron")); f.b(9, DECK + 1, 2, M("lava_cauldron")); f.b(10, DECK + 1, 2, M("blast_furnace"), {"facing": "south", "lit": "true"})
    f.b(11, DECK + 1, 2, M("anvil"), {"facing": "east"}); f.b(2, DECK + 1, 12, M("smithing_table"))
    for y in range(DECK + 1, DECK + 7): f.b(7, y, 2, R("rusted_fluid_pipe"), PIPE)
    for x in range(3, 12): f.b(x, DECK + 7, 2, R("rusted_fluid_pipe"), PIPE)
    f.b(6, DECK + 1, 2, R("rusted_mechanical_pump"), {"facing": "up"}); f.b(8, DECK + 1, 2, R("rusted_encased_cogwheel"), {"axis": "x", "top_shaft": "true", "bottom_shaft": "true"})
    f.b(12, DECK + 1, 12, R("rusted_drum"), {"axis": "y"}); f.b(12, DECK + 2, 12, R("rusted_drum"), {"axis": "y"}); f.b(11, DECK + 1, 12, R("gas_cylinders"), {"count": "4", "facing": "west"})
    kchest(f.t, 12, DECK + 1, 10, "west", "foundry"); kchest(f.t, 2, DECK + 1, 10, "east", "foundry")
    for x, z in ((4, 7), (10, 7)):
        f.b(x, DECK + 7, z, M("chain"), {"axis": "y", "waterlogged": "false"}); f.b(x, DECK + 6, z, M("soul_lantern"), {"hanging": "true", "waterlogged": "false"})
    return f.done()

def kiln():
    f = F("kiln", 11, 11); f.deck(0, 10, 0, 10)
    for x, z in ((0, 0), (10, 0), (0, 10), (10, 10), (5, 5)): f.column(x, z)
    for x in range(3, 8):                                          # raised plinth + open fence cage (fortress blaze platform)
        for z in range(3, 8):
            f.b(x, DECK + 1, z, nb(f.r))
            if x in (3, 7) or z in (3, 7):
                if (x + z) % 2: f.b(x, DECK + 2, z, M("nether_brick_fence"))
    f.b(5, DECK + 2, 5, M("spawner"), None, {"id": M("mob_spawner"), "SpawnData": (10, {"entity": (10, {"id": (8, "minecraft:blaze")})})})
    f.b(5, DECK + 1, 3, M("nether_brick_stairs"), {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"})
    kchest(f.t, 9, DECK + 1, 9, "west", "foundry"); f.jig("n", pool=False)
    return f.done()

def barracks():
    f = F("barracks", 9, 9, 6); r = f.r; f.deck(0, 8, 0, 8, rail=False, head=4)
    for x, z in ((0, 0), (8, 0), (0, 8), (8, 8)): f.column(x, z)
    for x in range(9):
        for z in range(9):
            edge = x in (0, 8) or z in (0, 8)
            for y in range(DECK + 1, DECK + 5):
                if edge: f.b(x, y, z, nb(r))
            f.b(x, DECK + 5, z, nb(r))
    for d in (-1, 0, 1):
        for y in (1, 2, 3): f.b(4 + d, DECK + y, 0, M("air"))
    f.jig("n", pool=False)
    for x in (2, 6): f.b(x, DECK + 1, 6, M("nether_brick_slab"), {"type": "bottom", "waterlogged": "false"})
    kchest(f.t, 7, DECK + 1, 7, "west", "foundry"); f.b(1, DECK + 1, 7, M("wither_skeleton_skull"), {"rotation": "6", "powered": "false"})
    return f.done()

def terrace():
    f = F("terrace", 9, 9); f.deck(0, 8, 0, 8)
    for x, z in ((0, 0), (8, 0), (0, 8), (8, 8)): f.column(x, z)
    for x in range(2, 7):
        for z in range(3, 8):
            f.b(x, DECK, z, M("soul_sand")); f.b(x, DECK + 1, z, M("nether_wart"), {"age": str(f.r.randint(1, 3))})
    for x in range(1, 8): f.b(x, DECK + 1, 2, M("nether_brick_stairs"), {"facing": "south", "half": "bottom", "shape": "straight", "waterlogged": "false"}) if x in (1, 7) else None
    f.jig("n", pool=False); return f.done()

def cap():
    f = F("cap", 5, 1)
    for x in range(5): f.b(x, DECK, 0, nb(f.r)); f.b(x, DECK + 1, 0, M("nether_brick_fence"))
    f.b(2, DECK + 1, 0, M("jigsaw"), {"orientation": "north_up"}, {"id": M("jigsaw"), "name": J, "target": J, "pool": "minecraft:empty",
                                                                 "final_state": M("nether_brick_fence"), "joint": "aligned"})
    return f.done()

def pe(loc, wt): return {"weight": wt, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}
def foundry():
    d = OUT / "structure/foundry"; d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.nbt"): old.unlink()
    pieces = {"hall": hall(), "bridge13": bridge(13, "bridge13"), "bridge7": bridge(7, "bridge7"), "cross": platform("cross", "nswe"),
              "tee": platform("tee", "nwe"), "kiln": kiln(), "barracks": barracks(), "terrace": terrace(), "cap": cap()}
    for n, t in pieces.items(): (d / f"{n}.nbt").write_bytes(t.bytes())
    L = lambda n: f"{FP}/{n}"
    w(OUT / "worldgen/template_pool/foundry/start.json", {"fallback": "minecraft:empty", "elements": [pe(L("hall"), 1)]})
    w(OUT / "worldgen/template_pool/foundry/wings.json", {"fallback": f"{FP}/caps", "elements": [
        pe(L("bridge13"), 5), pe(L("bridge7"), 3), pe(L("cross"), 2), pe(L("tee"), 2), pe(L("kiln"), 3), pe(L("barracks"), 2), pe(L("terrace"), 1)]})
    w(OUT / "worldgen/template_pool/foundry/caps.json", {"fallback": "minecraft:empty", "elements": [pe(L("cap"), 1)]})
    w(OUT / "tags/worldgen/biome/has_structure/nether_foundry.json", {"replace": False, "values": ["#minecraft:is_nether"]})
    w(OUT / "worldgen/structure/nether_foundry.json", {"type": "minecraft:jigsaw", "biomes": "#dying_world:has_structure/nether_foundry", "max_distance_from_center": 80,
        "size": 6, "spawn_overrides": {"monster": {"bounding_box": "piece", "spawns": [
            {"type": "minecraft:blaze", "weight": 10, "minCount": 2, "maxCount": 3}, {"type": "minecraft:zombified_piglin", "weight": 5, "minCount": 4, "maxCount": 4},
            {"type": "minecraft:wither_skeleton", "weight": 8, "minCount": 5, "maxCount": 5}, {"type": "minecraft:skeleton", "weight": 2, "minCount": 5, "maxCount": 5},
            {"type": "minecraft:magma_cube", "weight": 3, "minCount": 4, "maxCount": 4}]}},
        "start_height": {"type": "minecraft:uniform", "min_inclusive": {"absolute": 36}, "max_inclusive": {"absolute": 60}},
        "start_pool": f"{FP}/start", "step": "underground_decoration", "terrain_adaptation": "none", "use_expansion_hack": False})
    w(OUT / "worldgen/structure_set/nether_foundries.json", {"structures": [{"structure": "dying_world:nether_foundry", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 26, "separation": 9, "salt": zlib.crc32(b"dying_world:nether_foundries") % 2000000000}})
    return len(pieces)

def fortress_off():
    p = OUT / "worldgen/structure_set/nether_fortress.json"
    if p.exists(): p.unlink()
    sp = OUT / "worldgen/structure_set/research_nether_stations.json"; j = json.loads(sp.read_text())
    j["placement"]["exclusion_zone"] = {"other_set": "dying_world:nether_foundries", "chunk_count": 4}; w(sp, j)
    w(OUT.parent / "minecraft/advancement/nether/find_fortress.json", {
        "parent": "minecraft:nether/root",
        "criteria": {"fortress": {"trigger": "minecraft:location", "conditions": {"player": [{"condition": "minecraft:entity_properties", "entity": "this",
                     "predicate": {"location": {"structures": "dying_world:nether_foundry"}}}]}}},
        "display": {"icon": {"id": "minecraft:nether_bricks", "count": 1}, "title": {"translate": "advancements.nether.find_fortress.title"},
                    "description": {"translate": "advancements.nether.find_fortress.description"}},
        "requirements": [["fortress"]], "sends_telemetry_event": True})

def main():
    station(); n = foundry(); fortress_off()
    print(f"9-18: nether station + blaze containment + wither skeletons; nether_foundry ({n} pieces); fortress set removed; find_fortress -> foundry")

if __name__ == "__main__":
    main()
