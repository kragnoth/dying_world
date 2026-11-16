#!/usr/bin/env python3
"""
gen_pass9_33.py - pass 9-33: LORE. Journals (written books) + exploration maps in the research sites and story landmarks.
Run AFTER gen_pass9_16 (needs its structure tags), before 8_9/build. Safe to re-run.

Delivery = NeoForge global loot modifiers (neoforge:add_table), so the chest tables themselves (several are the user's hand-tuned
user_overrides copies) are never touched:
  - research archives / foundry / pads / scavenger keep: condition loot_table_id (+ random_chance where noted)
  - landmarks that use vanilla village tables: any_of(loot_table_id ...) + minecraft:location_check {structures: <the landmark>}
Exploration maps only link sites in the SAME dimension (a map can't point across a portal):
  hermit cottage -> nearest research gate; gate archives -> proving grounds; proving archive -> sunken lab / sculk site;
  Nether station archive -> foundry.
Story defaults (endgame framework 'aiming knobs', first options): the Gearwrights opened the gates; power drawn through them
('the draught') bleeds the world - tar ('the black') and spirits ('lodgers') are the leak; dry records that slowly go wrong.
The First Gate 'at the Hollow' is foreshadowed only (phase 2 builds it).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pass4_2a import w, OUT

NS = "dying_world"

# ------------------------------------------------------------------ the books: key -> (title, author, [pages])
BOOKS = {
 "gate_below": ("Gatehouse Register, Below", "A. Venn, Clerk", [
   "Gatehouse register, kept by order of the Guild.\n\nDraught drawn this week: forty measures. Heat in the sanctum within tolerance. Frames inspected, sound.",
   "Draught drawn: sixty measures. The fitters ask for gloves. The pipes are warm on the outside now, not only within.\n\nStaff note a sound in the pipes like talking. Recorded as pressure.",
   "Draught drawn: more than ordered. The gate does not close as fast as it opens.\n\nMaster Harrow has gone through to the station below to see why. Register to be kept until she returns.",
   "No draught drawn. No draught ordered.\n\nThe gate is open anyway.\n\nRegister closed. A.V."]),
 "gate_beyond": ("Gatehouse Register, Beyond", "M. Ashdown, Clerk", [
   "Gatehouse register, Beyond.\n\nTwelve frames set, twelve eyes seated. Draught from Beyond runs cold and clean, cleaner than Below. The Guild is pleased.",
   "The cold does not leave the sanctum when the gate is shut. Frost on the inside of the frames in summer.\n\nThree of the fitters report they have stopped dreaming. Recorded.",
   "Something came back through with the draught. Not a creature. A presence in the room, like being watched by someone politely.\n\nThe staff call them lodgers. I have asked them to stop.",
   "Doctor Marsh writes from the far station that we are not drawing power. We are being drawn on.\n\nThe Guild has asked me to stop recording her letters."]),
 "proving": ("Proving Ledger", "Sgt. R. Coyle", [
   "Proving ledger. All gear bound for the far stations is tried here first: suits, breathing hoods, the wind-engines.\n\nVault keys issued to passing crews only.",
   "Wind-engine trial: three crew winded, one lost a hand to the rotor. Passed for service.\n\nRequisitions from the Tidewell for sealed hoods. From the Listening Post: wax, for ears.",
   "Requisitions stopped in the spring. No crews come through.\n\nWe keep testing. The engines run whether anyone watches or not.",
   "Orders were to hold until relieved.\n\nNobody has come to relieve us. If you are reading this, you are the relief. The keys are in the vaults. Take them."]),
 "below": ("Station Below: Day Book", "Wright E. Harrow", [
   "Day book of the station below.\n\nThe draught here is not heat, though it comes with heat. It is closer to will. The furnaces burn hotter when the crew is angry.",
   "The gold-wearers traded with us for a season. Then they stopped trading and started watching the gate.\n\nSome have gone through it. We did not stop them. I am not sure we could.",
   "A black seep under the overworld frames. It does not burn and does not dry. It is coming through from our side.\n\nThe Guild calls it slag. It is not slag.",
   "The foundry is past the lava field. Every measure of draught is fired there before it goes up.\n\nIf the draught is the wound, the foundry is where we kept it open. Map enclosed."]),
 "foundry": ("Foundry Orders", "Foreman T. Gale", [
   "Foundry orders. Kilns fired on draught alone, no coal. Output: brass that does not tarnish and takes a spirit like a lamp takes a flame.\n\nBlaze stock kept in cages.",
   "The caged blazes are dimmer every month. The draught is feeding on them, or they on it. We call the spent ones weakened and sell them up top.",
   "The men up top say that in the Hollow you can see our smoke on the horizon, rising over the hills.\n\nIt is not our smoke. Our stacks vent here, into this sky.",
   "Order from the Guild: fire every kiln, double the draught.\n\nOrder refused. Kilns banked. If they want it done they can come down and do it.\n\nT. Gale"]),
 "far": ("Far Station: Observations", "Dr. I. Marsh", [
   "Observations from the far station.\n\nThe void beneath us is not empty. Lights move in it, slowly, as if looking. The shell-creatures guard the towers and ignore us entirely.",
   "The wing-harness works. A crewman glided the length of the island and back. The Guild wants a hundred.\n\nI want to know what the draught carries back with it.",
   "Each measure of draught we send home carries passengers. The clerks call them lodgers. They ride the cold back into the world and they stay.",
   "We are not drawing power. We are being drawn on.\n\nI have written this to the Guild four times. I will not write it a fifth. I.M."]),
 "listening": ("Listening Post Transcript", "Operator N. Brandt", [
   "Transcript, listening post.\n\nThe deep growth answers sound. Set beneath the gates, it hums at the same pitch as the frames when the draught runs.",
   "Something very large moves below the growth when the gates are open. The growth tells it where we are.\n\nOrders: speak quietly. Wear wax. Do not drop tools.",
   "The hum continues with every gate shut.\n\nThe hum continues with every gate shut.\n\nIt is not listening to the gates anymore.",
   "do not ring the bell\ndo not ring the bell\n\nit comes at the bell\n\n- N."]),
 "tidewell": ("Tidewell Log", "Keeper L. Moor", [
   "Tidewell log. The sea cools the draught lines from the gatehouses. The guardians tolerate us if we keep to the lit halls.",
   "Water in the cooling halls has gone dark. Not dirty. Dark, like the black seep from below, thinned out in brine.\n\nFish will not enter the halls.",
   "Order from the Guild: hold the Tidewell at any cost.\n\nThe cost was decided for us. The great one woke. The halls are flooded by my hand. Nothing more will be cooled here.",
   "If the gatehouses still run, they run hot. If they run hot, they leak.\n\nI am sorry for what the sea will carry. L.M."]),
 "hermit": ("A Penitent's Account", "the Hermit", [
   "I was chaplain to the Gearwrights. I blessed the First Gate when they cut it, at the Hollow, the valley the Guild is named for.\n\nI said the words. I believed them.",
   "The draught came up through the Hollow first. The smoke on the horizon, the bell at midnight, the pale groves. All of it started there.\n\nThe Guild knew within a year.",
   "They built more gates. Gatehouses in the wilds, a station Below, another Beyond. Each one to fix the last.\n\nI left. I keep a light on in case anyone comes asking.",
   "You are asking. The nearest gatehouse is marked on the map in this chest.\n\nRead their registers. Then decide what you think of men who keep records instead of stopping."]),
 "quarantine": ("Quarantine Notes", "Archivist P. Sallow", [
   "I kept the Guild's archive. Every register came across my desk.\n\nThe black gets into ink. Pages copied from the gatehouses darken by themselves, a little more every day.",
   "My hands have gone the colour of the pages. The village nailed the door shut and I do not blame them.\n\nI am still lucid most days.",
   "A golden apple and a draught of weakness would do it. The old cure. Nobody will bring me either.\n\nIf you do, I can trade you what I saved from the archive.",
   "The registers all end the same way. The gate does not close as fast as it opens.\n\nSomeone has to close the first one. P.S."]),
 "tinker": ("Apprentice's Notebook", "W. Tamsin", [
   "Apprenticed to the Gearwrights at fourteen. I poured rebar for three gatehouses and cut frames for a fourth.\n\nGood work, all of it. I was proud of it.",
   "The frames were drawn by the masters at the Hollow. Nobody below a master was allowed to see a whole one.\n\nI saw one. I wish I had not.",
   "I will mend anything you bring me. Tools, locks, engines.\n\nI will not build a frame. Not for silver, not for the Guild, not for you.\n\n- W.T."]),
 "chapel": ("Sermon, Unfinished", "unsigned", [
   "They call it draught, as if it were wind through a door.\n\nIt is a door. And we have propped it open to warm our hands at what stands on the other side.",
   "Each night the bell in the Hollow tolls twelve, and nobody rings it. Each night after, the dead walk a little longer.\n\nThe Guild says it is a fault in the clockwork.",
   "I will preach this on the morrow, whatever the Guild pays our"]),
 "pad": ("Survey Stake Notes", "Guild Survey, Site 14", [
   "Site fourteen. Foundation poured for a gatehouse: sound ground, two days from any town, water near.\n\nFrames due by autumn.",
   "Frames not delivered. Crew paid off. Foundation left to cure.\n\nThe Guild has stopped building new gatehouses. No reason given.\n\nSite abandoned."]),
 "scavenger": ("Scavenger's Tally", "the Keep", [
   "Tally of Guild crates taken: thirty-one. Good brass, rope, lamp oil, a crate of frame bolts we could not sell.\n\nThe gold-wearers came up through a gatehouse and stayed.",
   "They hold the keep and we hold the walls. They want gold and we want quiet. It works.\n\nNobody goes near the gatehouses after dark. Not them, not us."]),
 "letter_a": ("Letter, Unsent", "Edda", [
   "Dear Tom,\n\nThe Guild men came through again, hiring for the gatehouse up the valley. Good silver. Your father signed on.\n\nThe well water tastes of pennies since.",
   "He came home grey and quiet. The cows will not go to the north field.\n\nWe are leaving after the harvest, everyone is. Come find us at Aunt Bet's.\n\nEdda"]),
 "letter_b": ("Notice of Closure", "the Parish", [
   "By order of the parish, this village is closed.\n\nThe sickness from the gatehouse road has taken eleven. Those who remain will go south with the carts.",
   "Do not drink from the well. Do not stay after dark. Do not open the doors that are nailed shut.\n\nGod keep whoever reads this."]),
}

def book_entry(key, weight=1):
    title, author, pages = BOOKS[key]
    for p in pages: assert len(p) <= 280, (key, len(p))
    return {"type": "minecraft:item", "name": "minecraft:written_book", "weight": weight,
            "functions": [{"function": "minecraft:set_components", "components": {"minecraft:written_book_content": {
                "title": {"raw": title}, "author": author, "resolved": True,
                "pages": [json.dumps({"text": p}) for p in pages]}}}]}

def map_entry(tag, name, weight=1):
    return {"type": "minecraft:item", "name": "minecraft:map", "weight": weight, "functions": [
        {"function": "minecraft:exploration_map", "destination": f"{NS}:{tag}", "decoration": "minecraft:red_x",
         "zoom": 2, "search_radius": 100, "skip_existing_chunks": False},
        {"function": "minecraft:set_name", "target": "item_name", "name": {"text": name}}]}

def pool(entries, chance=None):
    p = {"rolls": 1, "entries": entries}
    if chance is not None: p["conditions"] = [{"condition": "minecraft:random_chance", "chance": chance}]
    return p

# map destination tags (exploration_map needs a structure TAG)
MAP_TAGS = {"map/proving_grounds": ["proving_grounds"], "map/far_labs": ["sunken_research_lab", "sculk_research_site"]}

# ------------------------------------------------------------------ what goes where: name -> (lore table pools, condition list)
def tid(t): return {"condition": "neoforge:loot_table_id", "loot_table_id": t}
def any_tid(*ts): return {"condition": "minecraft:any_of", "terms": [tid(t) for t in ts]}
def inside(structs): return {"condition": "minecraft:location_check", "predicate": {"structures": structs}}
C = f"{NS}:chests/"; V = "minecraft:chests/village/"
VILLAGE = [V + f"village_{k}" for k in ("plains_house", "taiga_house", "savanna_house", "snowy_house", "desert_house", "temple", "toolsmith", "cartographer")]

SITES = {
 # research archives (live + derelict share the tables)
 "gate_nether": ([pool([book_entry("gate_below")]), pool([map_entry("map/proving_grounds", "Requisition Route: Proving Grounds")], 0.6)],
                 [tid(C + "research_gate_nether_archive")]),
 "gate_end":    ([pool([book_entry("gate_beyond")]), pool([map_entry("map/proving_grounds", "Requisition Route: Proving Grounds")], 0.6)],
                 [tid(C + "research_gate_end_archive")]),
 "proving":     ([pool([book_entry("proving")]), pool([map_entry("map/far_labs", "Supply Route: Far Laboratories")], 0.6)],
                 [tid(C + "research_proving_archive")]),
 "nether":      ([pool([book_entry("below")]), pool([map_entry("nether_foundries", "Route to the Foundry")])],
                 [tid(C + "research_nether_archive")]),
 "end":         ([pool([book_entry("far")])], [tid(C + "research_end_archive")]),
 "sculk":       ([pool([book_entry("listening")])], [tid(C + "research_sculk_archive")]),
 "sunken":      ([pool([book_entry("tidewell")])], [any_tid(C + "research_sunken_archive", C + "research_sunken_lab")]),   # 9-34: archive rooms are optional; the hub has a lab chest
 # other sites with their own tables (chance: these tables fill several chests per site)
 "foundry":     ([pool([book_entry("foundry")], 0.35)], [tid(C + "foundry")]),
 "pad":         ([pool([book_entry("pad")], 0.4)], [tid(C + "concrete_pad")]),
 "scavenger":   ([pool([book_entry("scavenger")], 0.6)], [tid(C + "scavenger_stronghold_other")]),
 # landmarks on vanilla village tables -> only inside that structure
 "hermit":      ([pool([book_entry("hermit")]), pool([map_entry("research_gates", "The Hermit's Directions")])],
                 [any_tid(*VILLAGE), inside(f"{NS}:hermit_cottage")]),
 "plague":      ([pool([book_entry("quarantine")])], [any_tid(*VILLAGE), inside(f"{NS}:plague_house")]),
 "tinker":      ([pool([book_entry("tinker")])], [any_tid(*VILLAGE), inside(f"{NS}:tinker_workshop")]),
 "chapel":      ([pool([book_entry("chapel")], 0.5)], [any_tid(*VILLAGE), inside(f"{NS}:ruined_chapel")]),
 # the Quiet: abandoned settlements, now and then
 "quiet":       ([pool([book_entry("letter_a"), book_entry("letter_b")], 0.12)], [any_tid(*VILLAGE), inside(f"#{NS}:abandoned_settlements")]),
}

def main():
    tags = OUT / "tags/worldgen/structure"
    for name, ids in MAP_TAGS.items():
        for n in ids: assert (OUT / f"worldgen/structure/{n}.json").exists(), n
        w(tags / f"{name}.json", {"replace": False, "values": [f"{NS}:{n}" for n in ids]})
    for t in ("research_gates", "nether_foundries", "abandoned_settlements"):
        assert (tags / f"{t}.json").exists(), f"run gen_pass9_16 first ({t})"
    for c in ("research_gate_nether_archive", "research_gate_end_archive", "research_proving_archive", "research_nether_archive",
              "research_end_archive", "research_sculk_archive", "research_sunken_archive", "foundry", "concrete_pad", "scavenger_stronghold_other"):
        assert (OUT / f"loot_table/chests/{c}.json").exists(), c
    for s in ("hermit_cottage", "plague_house", "tinker_workshop", "ruined_chapel"):
        assert (OUT / f"worldgen/structure/{s}.json").exists(), s
    ids = []
    for name, (pools, conds) in SITES.items():
        w(OUT / f"loot_table/lore/{name}.json", {"type": "minecraft:chest", "pools": pools})
        w(OUT / f"loot_modifiers/lore_{name}.json", {"type": "neoforge:add_table", "conditions": conds, "table": f"{NS}:lore/{name}"})
        ids.append(f"{NS}:lore_{name}")
    reg = OUT.parent / "neoforge/loot_modifiers/global_loot_modifiers.json"
    j = json.loads(reg.read_text()); j["entries"] = [e for e in j["entries"] if not e.startswith(f"{NS}:lore_")] + ids; w(reg, j)
    print(f"9-33: {len(BOOKS)} books, {len(SITES)} lore modifiers, {len(MAP_TAGS)} map tags")

if __name__ == "__main__":
    main()
