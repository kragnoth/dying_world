#!/usr/bin/env python3
"""
gen_occult_quests.py - pass 9-42: the Arcana questlines fleshed out on the world's lore.
Edits modpack/overrides/config/ftbquests/quests in place (run once; refuses to run twice):
  - NEW chapter 'The Incursion' (Arcana group): the Gearwrights' trail through the research sites (structure tasks), the three
    characters, the Eroded Yard (Incision's flesh biome = the wound Below), the incursion alloys (chromatic compound -> shadow steel / refined radiance -> Gearwrights' Seal), a capstone.
  - Tar and Spirits: + weakened souls, scorched spawners, feeding the lodgers, orders, shade, ossuary, broadcast mast,
    transient antenna, sixteen candles, bottled void, and the four Tarbound landmarks (Tarbound's own advancements).
  - Blood and Ritual: + Scriptura Vitae, throwing dagger, blood lantern, two sigils, first ritual, Breaching the Edge
    ('you are opening a gate'), demonite, bloodstone (Tier III), Magus / Dominus / Divinus orbs, crystal cluster (sculk), aspects.
  - 'Beyond the Veil' description names the new chapter; 'Black Tar' now also follows the weakened-soul quest.
Lore = the defaults set in the endgame framework: the Gearwrights opened the gates; the draught drawn through them bleeds the
world; tar is 'the black', spirits are 'lodgers'; the first gate was cut at the Hollow. Text avoids literal '&' (FTB format char).
Usage: python3 -I gen_occult_quests.py <path to config/ftbquests/quests>
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import snbt
from snbt import Num

Q = Path(sys.argv[1]); LANG = Q / "lang/en_us.snbt"
def nid(key):
    h = int(hashlib.sha1(("gh-occult/" + key).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF
    return f"{h:016X}"
def d(v): return Num(float(v), "d")

# reward helpers
TAR_TABLE, BLOOD_TABLE, BIG_TABLE = Num(0x69C10E45500045A4, "L"), Num(0x6030087D3CF462D8, "L"), Num(0x2CC2AA7605FDDBAC, "L")
def xp(k, n): return {"id": nid(k + "/xp"), "type": "xp", "xp": n}
def table(k, t): return {"id": nid(k + "/table"), "table_id": t, "type": "random"}
def cmd(k, c, i=0): return {"command": c, "id": nid(f"{k}/cmd{i}"), "permission_level": 2, "silent": True, "type": "command"}
def point(k): return cmd(k, "/puffish_skills points add {p} kskills:skill_tree 1", 9)
def title(k, text, color): return cmd(k, '/title {p} title {"text": "%s", "color": "%s", "italic": false}' % (text, color), 1)
# task helpers
def item(k, i, n=1):
    t = {"id": nid(k + "/task/" + i), "item": {"count": 1, "id": i}, "type": "item"}
    if n > 1: t["count"] = Num(n, "L")
    return t
def struct(k, s): return {"id": nid(k + "/task/" + s), "structure": s, "type": "structure"}
def adv(k, a): return {"advancement": a, "criterion": "", "id": nid(k + "/task/" + a), "type": "advancement"}
def check(k): return {"id": nid(k + "/task"), "type": "checkmark"}

QUESTS = {}   # chapter file -> [(key, quest dict, title, subtitle, [desc lines])]
def quest(ch, key, x, y, icon, tasks, rewards, deps, ttl, sub, desc, shape=None, size=None):
    qd = {"dependencies": deps, "icon": {"id": icon}, "id": nid(key), "rewards": rewards, "tasks": tasks, "x": d(x), "y": d(y)}
    if shape: qd["shape"] = shape
    if size: qd["size"] = d(size)
    QUESTS.setdefault(ch, []).append((key, qd, ttl, sub, desc)); return nid(key)

# existing quest ids we hang on
VEIL, BLACK_TAR, SCRYING, WEAK_BLAZE, RELIQUARY, STEWARD, ANTENNA = ("0BCCE13FE16F5EFD", "1C4C5E5A4D91FB07", "05C1A55100CFBB38",
    "3E961021C0E5BA63", "59CF596AC2C13B60", "111DF059A82E0716", "679E22B36236EB13")
ARA, TIER1, HELLFIRE, PETTY, ELEMENTAL, ACTIVATION, VENEFICUS, SENT_SWORD = ("676BFBF2B0FA5E96", "33E5B1351885CBCE", "14499DB1DC5AABD0",
    "1210AF3C76111BF1", "00A027F0F6E654B9", "6DE4A25BC52F5DCB", "57BA6B8AE5057DBC", "1043FBC3EE5F85BB")
FOUNDRY_Q = "35B1CCDBAD614213"   # Into the Depths: The Foundry

# ============================================================== The Incursion (new chapter)
INC = "incursion"
k = "inc/smoke"; i_smoke = quest(INC, k, 0, 0, "minecraft:bell", [check(k)], [xp(k, 50)], [VEIL],
    "Smoke on the Horizon", "What the Gearwrights opened",
    ["Columns of smoke rise beyond the hills and are gone by the time you get there. A bell tolls at midnight with no one to ring it. The groves grow pale.",
     "None of it is natural. Somebody kept records of what they did here, and the records are still lying in the ruins."], "hexagon", 1.5)
k = "inc/penitent"; i_pen = quest(INC, k, 2, -0.875, "minecraft:lantern", [struct(k, "dying_world:hermit_cottage")], [xp(k, 80)], [i_smoke],
    "The Penitent", "A light left on",
    ["An old man keeps a lamp burning in a cottage far from any road. He was chaplain to the Gearwrights, and he blessed the first gate when they cut it.",
     "His account is in the chest, and so is a map to the nearest gatehouse. He trades, if you are polite."])
k = "inc/gatehouse"; i_gate = quest(INC, k, 4, 0, "minecraft:reinforced_deepslate", [struct(k, "#dying_world:research_gates")],
    [xp(k, 120), table(k, TAR_TABLE)], [i_smoke],
    "The Gatehouse", "Registers, Below and Beyond",
    ["The Guild built gatehouses in the wilds: a hall, a sanctum, and a frame that opens onto the Nether or the End.",
     "Read the register in the archive. Every one of them ends the same way: the gate does not close as fast as it opens."])
k = "inc/quarantine"; quest(INC, k, 2, 0.875, "minecraft:golden_apple", [struct(k, "dying_world:plague_house")], [xp(k, 80)], [i_smoke],
    "Quarantine", "Nailed shut",
    ["The Guild's archivist copied every register that came off the gatehouses. The black got into the ink, then into him.",
     "He is still lucid most days. A weakness potion and a golden apple would cure him, and he kept what he could of the archive."])
k = "inc/apprentice"; quest(INC, k, 2, 1.75, "minecraft:anvil", [struct(k, "dying_world:tinker_workshop")], [xp(k, 80)], [i_smoke],
    "The Apprentice", "Mends anything but frames",
    ["A tinker poured rebar for three gatehouses and saw one whole frame drawn up by the masters at the Hollow.",
     "He will fix your tools. He will not build a gate, for any price."])
k = "inc/proving"; i_prov = quest(INC, k, 6, -1.75, "minecraft:trial_key", [struct(k, "dying_world:proving_grounds")], [xp(k, 120)], [i_gate],
    "Requisitions", "The proving grounds",
    ["Every suit, hood and wind-engine bound for the far stations was tested under a Guild hut first. Follow the mast.",
     "The sergeant there is still holding his post. His ledger has the supply routes to the far laboratories."])
k = "inc/tidewell"; i_tide = quest(INC, k, 8, -2.625, "minecraft:prismarine_bricks", [struct(k, "dying_world:sunken_research_lab")],
    [xp(k, 150), table(k, TAR_TABLE)], [i_prov],
    "The Tidewell", "Cooling halls under the sea",
    ["The sea cooled the draught lines from the gatehouses. Then the water in the halls went dark, and the keeper flooded them herself.",
     "Mind the great one. It woke for a reason."])
k = "inc/listening"; i_listen = quest(INC, k, 8, -0.875, "minecraft:calibrated_sculk_sensor", [struct(k, "dying_world:sculk_research_site")],
    [xp(k, 150), table(k, TAR_TABLE)], [i_prov],
    "The Listening Post", "Wear wax. Do not drop tools.",
    ["Deep in the dark the Guild dug down to an older gate, and set the growth to listen to their own.",
     "The growth hums at the frames' pitch even with every gate shut. Read the transcript in the survey desk, and do not ring the bell."])
k = "inc/below"; i_below = quest(INC, k, 6, 0.875, "minecraft:crying_obsidian", [struct(k, "#dying_world:nether_stations")],
    [xp(k, 150)], [i_gate],
    "Station Below", "Harrow's day book",
    ["The draught Below is not heat, though it comes with heat. It is closer to will.",
     "Master Harrow went through to find out why the gates would not close. Her day book is in the station's archive, with a route to the foundry."])
k = "inc/foundry"; i_found = quest(INC, k, 8, 0.875, "minecraft:blast_furnace", [struct(k, "#dying_world:nether_foundries")],
    [xp(k, 150), table(k, TAR_TABLE)], [i_below],
    "The Foundry", "It is not our smoke",
    ["Every measure of draught was fired here before it went up. The caged blazes went dim feeding it.",
     "Foreman Gale banked the kilns rather than double the draught. Find his orders; one line explains the smoke you keep seeing."])
k = "inc/far"; i_far = quest(INC, k, 8, 2.625, "minecraft:elytra", [struct(k, "#dying_world:end_stations")],
    [xp(k, 200), table(k, BIG_TABLE)], [i_gate],
    "Far Station", "We are being drawn on",
    ["Doctor Marsh watched the void under the islands and wrote to the Guild four times.",
     "Each measure of draught sent home carried passengers. The clerks called them lodgers. They are still riding the cold back into the world."])
# the Eroded Yard (Incision mod): the wound Below
def kill(k, e, n): return {"entity": e, "id": nid(k + "/task/" + e), "type": "kill", "value": Num(n, "L")}
k = "inc/wound"; i_wound = quest(INC, k, 6, 2.625, "incision:carrion", [{"biome": "incision:eroded_yard", "id": nid(k + "/task"), "type": "biome"}],
    [xp(k, 120)], [i_below],
    "The Wound Below", "The Eroded Yard",
    ["In places the Nether has grown flesh: carrion, clotted stone, eyes in the walls. As if the draught tore a wound Below and it healed wrong.",
     "Harrow's day book stops short of saying where her crew went."])
k = "inc/stayed"; quest(INC, k, 5, 3.5, "minecraft:skeleton_skull", [kill(k, "incision:skeletoncultist", 3)], [xp(k, 120), table(k, TAR_TABLE)], [i_wound],
    "Those Who Stayed", "Skeleton cultists",
    ["Skeletons keep vigil in the yard with candles in their hands. They tend the wound like something sacred.",
     "Some of the Guild's crews never came back up. Put three of the vigil to rest."])
k = "inc/knife"; quest(INC, k, 7, 3.5, "incision:burial_knife", [item(k, "incision:burial_knife")], [xp(k, 100)], [i_wound],
    "Burial Knife", "Seer fangs on a stick",
    ["The seers that drift through the yard leave vile fangs behind. Two on a stick make a knife for cutting away what the yard grows."])
# the incursion alloys (see server_scripts/progression/50_incursion_alloys.js)
k = "inc/condensate"; i_chrom = quest(INC, k, 10, 0, "create:chromatic_compound", [item(k, "create:chromatic_compound")],
    [xp(k, 200)], [i_found, BLACK_TAR],
    "Draught Condensate", "Chromatic Compound",
    ["The Guild bottled what came through. Superheat three powdered obsidian, a polished rose quartz and glowstone with a measure of tar in a mixer.",
     "It is the closest thing to the draught you can hold in your hand."])
k = "inc/shadow"; i_shadow = quest(INC, k, 12, -0.875, "create:shadow_steel", [item(k, "create:shadow_steel")], [xp(k, 200)], [i_chrom],
    "Steeped in the Beyond", "Shadow Steel",
    ["Mix the compound with an echo shard and two popped chorus fruit. The listening post and the far station each gave you half of it.",
     "It never quite warms in the hand."])
k = "inc/radiance"; i_rad = quest(INC, k, 12, 0.875, "create:refined_radiance", [item(k, "create:refined_radiance")], [xp(k, 200)], [i_chrom],
    "Fired from Below", "Refined Radiance",
    ["Superheat the compound with two glowstone and a weakened soul, a spark of what the foundry burned out of its blazes.",
     "Brighter than it has any right to be."])
k = "inc/seal"; i_seal = quest(INC, k, 14, 0, "hallmarked:gearwrights_seal", [item(k, "hallmarked:gearwrights_seal")],
    [xp(k, 250), table(k, BIG_TABLE)], [i_shadow, i_rad],
    "The Guild's Own Mark", "Gearwright's Seal",
    ["A smith's stamp, shadow steel and refined radiance make the Guild's seal without a nether star or a dragon egg.",
     "The Gearwrights marked their best work with it. Now you can mark yours."])
k = "inc/opened"; quest(INC, k, 16, 0, "minecraft:end_portal_frame", [check(k)],
    [xp(k, 300), point(k), title(k, "What They Opened", "dark_purple"), table(k, BIG_TABLE)],
    [i_tide, i_listen, i_far, i_seal],
    "What They Opened", "Every register ends the same way",
    ["Gatehouses, a station Below, a station Beyond, a foundry to feed them, a post to listen and a well to cool them. Each one built to fix the last.",
     "Every record points back to the Hollow, where the first gate was cut. Whatever is still open there, the Gearwrights never closed it."],
    "octagon", 1.5)

# ============================================================== Tar and Spirits additions
TS = "629bfe84ad23c816"
k = "tar/soul"; t_soul = quest(TS, k, -2, 0, "tarbound:weakened_soul", [item(k, "tarbound:weakened_soul")], [xp(k, 30)], [VEIL],
    "A Weakened Soul", "Scraped out of soul sand",
    ["Strike flint and steel against soul sand and a dim spark of soul comes loose. A bucket and a soul make a bucket of tar.",
     "The Guild called it the black. It leaked through their gates long before anyone thought to bottle it."])
k = "tar/scorched"; quest(TS, k, 6, 1.75, "minecraft:spawner", [adv(k, "tarbound:scorched_spawner")], [xp(k, 80)], [WEAK_BLAZE],
    "Scorched Earth", "Dimmed on purpose",
    ["Scorch a blaze spawner with flint and steel and it only gives up weakened blazes.",
     "The foundry did this to its caged stock for years. Foreman Gale's orders say it plainly."])
k = "tar/feed"; t_feed = quest(TS, k, 6, -1.75, "minecraft:candle", [adv(k, "tarbound:feed_radio")], [xp(k, 60)], [SCRYING],
    "Feeding Time", "Lodgers are hungry",
    ["The spirits in your tar are the same lodgers that rode the draught home. Feed them a candle or a soul and they work for you.",
     "Keep them fed. The registers do not say what they do when they are not."])
k = "tar/order"; t_order = quest(TS, k, 10, -2.625, "tarbound:spirit_contract", [adv(k, "tarbound:first_order")], [xp(k, 100)], [RELIQUARY],
    "Work Order", "Something to make",
    ["Order an item from the radio and let a bound spirit make it.", "The Guild ran whole workshops this way, near the end."])
k = "tar/shade"; quest(TS, k, 12, -2.625, "tarbound:shade", [adv(k, "tarbound:shade")], [xp(k, 120)], [t_order],
    "Someone's Watching", "A shade over your orders",
    ["A shade holds the parts of a long order so nothing else takes them. Feed it votive skulls to raise its rank.",
     "It watches the work. Try not to wonder what else it watches."])
k = "tar/ossuary"; quest(TS, k, 14, -0.875, "tarbound:ossuary", [adv(k, "tarbound:ossuary")], [xp(k, 120)], [STEWARD],
    "Bone Library", "Every contract in one place",
    ["An ossuary keeps every reliquary's contracts on one radio, to hand out and take back.",
     "The archivist kept the Guild's contracts like this, until the ink went dark."])
k = "tar/mast"; t_mast = quest(TS, k, 14, 0.875, "tarbound:tar_antenna", [adv(k, "tarbound:cell_tower")], [xp(k, 120)], [ANTENNA],
    "Can You Hear Me Now?", "A broadcast mast",
    ["Stack an antenna three pieces tall. The tar carries further than it should.",
     "The drowned radio sets along the coast were the Guild's. Some of them are still listening."])
k = "tar/transient"; quest(TS, k, 16, 0.875, "tarbound:transient_antenna", [adv(k, "tarbound:transient_antenna")], [xp(k, 150)], [t_mast],
    "Here and Not", "Transient Antenna", ["An antenna that is only partly in the world. The lodgers find it comfortable."])
k = "tar/candles"; quest(TS, k, 10, 2.625, "minecraft:candle", [adv(k, "tarbound:sixteen_candles")], [xp(k, 100), table(k, TAR_TABLE)], [RELIQUARY],
    "Sixteen Candles", "A well-kept reliquary", ["Light sixteen candles around one reliquary. The wayside shrines did this for spirits nobody remembered binding."])
k = "tar/void"; quest(TS, k, 2, -1.75, "tarbound:essence_of_the_void_bucket", [adv(k, "tarbound:essence")], [xp(k, 150)], [BLACK_TAR],
    "Bottled Void", "Essence of the Void",
    ["Fill a bucket with essence of the void.", "Doctor Marsh wrote that the void beneath the islands is not empty. This is what she meant."])
lore_sites = [("tar/cabin", -1, "tarbound:researcher_cabin", "minecraft:spruce_door", "Someone Was Here", "A researcher's cabin",
               "A cabin in the woods, left in a hurry. Whoever lived here was studying the tar before the Guild was."),
              ("tar/shrine", 1, "tarbound:wayside_shrine", "minecraft:candle", "A Coin for the Box", "A wayside shrine",
               "A reliquary still minds a dead furnace by the road. Leave it something."),
              ("tar/radio", 3, "tarbound:drowned_radio", "minecraft:note_block", "Dead Air", "A drowned radio",
               "A radio set the tar swallowed. It was tuned to a Guild frequency."),
              ("tar/crypt", 5, "tarbound:charnel_crypt", "minecraft:skeleton_skull", "The Sexton's Count", "A charnel crypt",
               "Climb down into a charnel crypt. The sexton counted every bone. The count is off by one.")]
for k, x, a, icon, ttl, sub, line in lore_sites:
    quest(TS, k, x, 3.5, icon, [adv(k, a)], [xp(k, 60)], [BLACK_TAR], ttl, sub, [line])

# ============================================================== Blood and Ritual additions
BR = "003226919cf36109"
k = "blood/scriptura"; quest(BR, k, 0, -1.75, "neovitae:guide_book", [item(k, "neovitae:guide_book")], [xp(k, 20)], [VEIL],
    "Scriptura Vitae", "Read first", ["The guidebook to everything below. Keep it on you; this chapter only marks the road."])
k = "blood/dagger"; quest(BR, k, 8, 3.5, "neovitae:throwing_dagger", [adv(k, "neovitae:neovitae/throwing_dagger")], [xp(k, 60)], [HELLFIRE],
    "Throwing Daggers", "Soul snare",
    ["A dagger that marks what it hits. Kill a marked creature and it gives up raw spiritus, before you ever hold a sentient sword."])
k = "blood/lantern"; quest(BR, k, 10, 3.5, "neovitae:blood_lantern", [item(k, "neovitae:blood_lantern")], [xp(k, 80)], [TIER1],
    "Blood Lantern", "A light left on",
    ["A soul lantern reforged in the altar. It wards sixteen blocks against wandering spawns.",
     "The hermit keeps one burning. Now you know why nothing troubles him."])
k = "blood/holding"; quest(BR, k, 12, -2.625, "neovitae:sigil_holding", [item(k, "neovitae:sigil_holding")], [xp(k, 100)], [ELEMENTAL],
    "Sigil of Holding", "Nine sigils in one hand", ["Carries up to nine other sigils. Cycle them with a hotkey."])
k = "blood/grove"; quest(BR, k, 14, -2.625, "neovitae:sigil_green_grove", [item(k, "neovitae:sigil_green_grove")], [xp(k, 100)], [ELEMENTAL],
    "Sigil of the Green Grove", "Life, paid in blood",
    ["The pale groves are what the draught does to growing things. This sigil is what blood does instead."])
k = "blood/first_ritual"; b_rit = quest(BR, k, 14, -1.75, "neovitae:master_ritual_stone", [adv(k, "neovitae:neovitae/first_ritual")],
    [xp(k, 150)], [ACTIVATION],
    "Ritual Awakening", "Your first rite", ["Inscribe the stones, set a crystal to the master stone, and pay the cost. The Ritual Diviner shows each layout."])
k = "blood/breach"; b_breach = quest(BR, k, 16, -2.625, "neovitae:dungeon_eye", [adv(k, "neovitae:neovitae/edge_of_hidden_realm")],
    [xp(k, 250), title(k, "A Crack in the Veil", "dark_red"), table(k, BLOOD_TABLE)], [b_rit, VENEFICUS],
    "A Crack in the Veil", "Breaching the Edge of Demon Realm",
    ["A Tier II rite that opens a way into the Demon Realm, once.",
     "Understand what you are doing. You are cutting a gate, the way the Gearwrights did. Every one of their registers ends with the gate not closing as fast as it opened. Yours, at least, is paid for in your own blood."],
    "diamond", 1.25)
k = "blood/demonite"; quest(BR, k, 18, -3.5, "neovitae:raw_demonite", [adv(k, "neovitae:neovitae/demonite")], [xp(k, 150)], [b_breach],
    "Forged in the Pit", "Raw demonite", ["Dig a sliver of demonite out of the Endless Realm. It smelts into hellforged metal."])
k = "blood/bloodstone"; b_stone = quest(BR, k, 18, -1.75, "neovitae:bloodstone_brick", [item(k, "neovitae:bloodstone_brick", 4)],
    [xp(k, 200)], [b_breach],
    "Bloodstone", "Tier III capstones",
    ["Tau grows in the Demon Realm. Saturated tau and the sanguine reverter in an athanor give weak blood shards, and shards make bloodstone.",
     "Four bricks cap the corners of a Tier III altar: 28 more runes, a ring lower, at radius five."])
k = "blood/magus"; b_magus = quest(BR, k, 20, -0.875, "neovitae:blood_orb_master", [item(k, "neovitae:blood_orb_master")],
    [xp(k, 250), point(k)], [b_stone, VENEFICUS],
    "Magus Orb", "Tier Three", ["A weak blood shard in a Tier III altar. Your network deepens again."])
k = "blood/dominus"; b_dom = quest(BR, k, 22, 0, "neovitae:blood_orb_archmage",
    [item(k, "neovitae:hellforged_block", 4), item(k, "neovitae:blood_orb_archmage")], [xp(k, 300), table(k, BLOOD_TABLE)], [b_magus],
    "Dominus Orb", "Tier Four",
    ["Hellforged blocks cap a Tier IV altar, 48 runes further out at radius eight. A hellforged block in the basin becomes the Dominus orb."])
k = "blood/cluster"; b_cl = quest(BR, k, 22, -1.75, "neovitae:crystal_cluster", [item(k, "neovitae:crystal_cluster", 4)], [xp(k, 300)], [b_dom],
    "Crystal Cluster", "Sculk and a star",
    ["Forged from sculk, a Tabula Aetherea, a weak blood shard and a nether star. Four crown a Tier V altar.",
     "The sculk is easiest got from the Guild's dig in the deep dark. They were listening to it; you are going to build on it."])
k = "blood/divinus"; quest(BR, k, 24, -0.875, "neovitae:blood_orb_transcendent", [item(k, "neovitae:blood_orb_transcendent")],
    [xp(k, 500), point(k), title(k, "Divinus", "dark_red"), table(k, BIG_TABLE)], [b_cl],
    "Divinus Orb", "Tier Five",
    ["A crystal cluster in a Tier V altar: 172 runes in five rings.",
     "The Guild drew its power through a gate and never paid for it. You have paid for every drop of yours."], "octagon", 1.4)
k = "blood/aspects"; quest(BR, k, 12, 3.5, "neovitae:raw_spiritus_crystal", [adv(k, "neovitae:neovitae/aspectum_omnia")], [xp(k, 150)], [PETTY],
    "Aspectum Omnia", "Four aspects of spiritus",
    ["Transmute a raw cluster into each of the four aspects: invictus, nihilum, ruina and vindicta."])

CHAPTER_NEW = {"default_hide_dependency_lines": False, "default_quest_shape": "", "filename": "6e5c1a7d0b9f4a21", "group": "1C6C41D6798C3267",
               "icon": {"id": "minecraft:end_portal_frame"}, "id": "6E5C1A7D0B9F4A21", "images": [], "order_index": 2, "quest_links": [], "quests": []}

def esc(s):
    assert "&" not in re.sub(r"&[0-9a-fk-or]", "", s), s
    return snbt.q(s)

def main():
    lang = LANG.read_text()
    if nid("inc/smoke") in lang: sys.exit("already applied")
    ids = set(re.findall(r'id: "([0-9A-F]{16})"', "".join(p.read_text() for p in (Q / "chapters").glob("*.snbt"))))
    new = [qd["id"] for qs in QUESTS.values() for _, qd, *_ in qs]
    assert len(new) == len(set(new)) and not (set(new) & ids), "id clash"
    lines = []
    # new chapter
    ch = dict(CHAPTER_NEW); ch["quests"] = [qd for _, qd, *_ in QUESTS[INC]]
    (Q / "chapters" / "6e5c1a7d0b9f4a21.snbt").write_text(snbt.dump(ch) + "\n")
    lines += [f'\tchapter.6E5C1A7D0B9F4A21.title: {esc("The Incursion")}', f'\tchapter.6E5C1A7D0B9F4A21.chapter_subtitle: [{esc("The Gearwrights records")}]']
    # existing chapters: insert quest blocks before the closing of quests: [ ... ]
    for f in (TS, BR):
        p = Q / "chapters" / f"{f}.snbt"; s = p.read_text()
        blocks = "\n".join("\t\t" + snbt.dump(qd, 2) for _, qd, *_ in QUESTS[f])
        m = list(re.finditer(r"\n\t\t\}\n\t\]\n", s)); assert m, f
        cut = m[-1].start() + len("\n\t\t}")
        s = s[:cut] + "\n" + blocks + s[cut:]
        if f == TS:   # Black Tar also follows the new weakened-soul quest
            s, n = re.subn(r'dependencies: \["0BCCE13FE16F5EFD"\]\n(\t+icon: \{\n\t+id: "tarbound:tar_bucket")', 'dependencies: ["0BCCE13FE16F5EFD", "%s"]\n\\1' % nid("tar/soul"), s)
            assert n == 1
        p.write_text(s)
    for qs in QUESTS.values():
        for _, qd, ttl, sub, desc in qs:
            lines.append(f'\tquest.{qd["id"]}.title: {esc(ttl)}')
            if sub: lines.append(f'\tquest.{qd["id"]}.quest_subtitle: {esc(sub)}')
            lines.append(f'\tquest.{qd["id"]}.quest_desc: [' + ", ".join(esc(x) for x in desc) + "]")
    old = '\tquest.0BCCE13FE16F5EFD.quest_desc: ["&5Some power isn\'t forged. It\'s bargained for.&r", "Two arts wait in this group: &4blood&r and ritual here, and &8tar&r and spirits in &8Tar and Spirits&r."]'
    assert old in lang
    lang = lang.replace(old, '\tquest.0BCCE13FE16F5EFD.quest_desc: ["&5Some power isn\'t forged. It\'s bargained for.&r", "Three threads wait in this group: &4blood&r and ritual here, &8tar&r and spirits in &8Tar and Spirits&r, and the Guild\'s own records in &5The Incursion&r: what the Gearwrights opened, and what came through."]')
    lang = lang.rstrip()
    assert lang.endswith("}")
    LANG.write_text(lang[:-1].rstrip("\n") + "\n" + "\n".join(lines) + "\n}\n")
    print({c: len(v) for c, v in QUESTS.items()}, "quests added")

if __name__ == "__main__":
    main()
