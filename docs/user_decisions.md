# USER DECISIONS (authoritative; supersede verdicts in roster.md where they differ)  - recorded after pass 3a

## Villages (survivor settlements)
- Mix of two building kinds in ONE settlement: ~40% LIVED-IN (beds, workstations, villagers spawn) and ~60% WORN DOWN
  (no beds, no workstations - villagers no longer live there).
- Decay rule: partial decay by REPLACING blocks with moss/lower-stage variants (mossy cobble, cracked bricks, etc).
  NEVER holes/removed blocks: the world "has a hard time completely decaying because the ghostly part remembers the shape".
  => processors are replace-only (no air replacement). Derelict variants swap beds/job blocks for non-functional filler.
- Re-use existing mod village builds where sensible (vanilla, vsrevamped, towns_and_towers, gearwrights abandoned villages).

## Replacements for vanilla structures
| vanilla | replacement |
|---|---|
| ruined portals | NO ruined portals. Instead: CONCRETE PADS with broken-down LEAN-TOS, a chest with obsidian/bricks/etc + random mid-tier loot (new build) |
| mineshafts | INDUSTRIAL TUNNELS (Rust and Rebar heavy) |
| pillager outposts | SCAVENGER OUTPOSTS |
| bastion | overworld equivalent of scavenging piglins: SCAVENGER stronghold with more OVERWORLD building-material loot |
| ancient city | overworld SCULK-styled site, same building style as the shacks/villages; NO warden/trigger (warden doesn't fit); its loot goes in chests |
| trial chambers, woodland mansions, ocean monuments | DROP (useless) |
| shipwrecks | KEEP (re-register, can stay) |
Nether fortress / stronghold placeholders already done (nether + end access must remain).

## General
- Re-use mod builds where intelligent; write new builds where nothing fits.
- Tone anchors the user likes most: BURNT and ABANDONED sites (gearwrights burnt_*, abandoned_*), ABANDONED CABINS, ABANDONED WATCHTOWERS.
- Structures TIED TO BIOMES so wood/palettes match (no oak in a spruce biome). Efficient method if possible:
  one structure + per-biome-group processor_list swapping wood/stone palette (instead of one structure copy per biome);
  mod builds that already ship per-biome variants (gearwrights 7, towns_and_towers 27, forsaken) keep their own biome tags.
- Density: rare and sparse by default.
- Rust and Rebar: used HEAVILY in the more industrialized zones (industrial tunnels, scavenger sites, concrete pads);
  mostly normal VANILLA materials in sparse villages / abandoned shacks.
- Not yet answered (defaults stand): tarbound sets (treated as occult anchors), overworld-wide vs dying-biome-only (user wants
  biome-tied palettes; `#c:is_wasteland` hook still optional), optional formations*/windswept rows.

## Revised pass plan
- 3b (Tier A, cheap): re-register as `dying_world:` sets with own spacing/salt + biome tag (initially includes original tag):
  gearwrights burnt_* + abandoned_ruins/hamlets/villages, abandoned_cabins, watchtower_building abandoned_watchtower,
  shipwrecks, supplementaries road_signs (+ tarbound x4 unless user objects).
- 3c (design): survivor villages - read vanilla/vsrevamped/towns_and_towers village pools in reference/worldgen_reference.zip,
  design lived-in (40%) vs worn-down (60%) pool split + replace-only decay processor_list + bed/workstation stripping.
- 4: new builds - concrete pads + lean-tos, industrial tunnels (replaces mineshafts), scavenger outposts.
- 5: scavenger stronghold (bastion eq.), sculk ruin site (ancient-city eq.), biome palette processor lists.
- Before block retheming: ask user for `config/wastelandvision/mappings-<vision>.txt`.

## Answers recorded in pass 3b prep (2026-11-14)
- Q1 VILLAGERS: survivor settlements are THE villager source (Easy Villagers / zombie cure = flavor only). Findable, playable, not brutal;
  themed sandbox, not a grindfest. Settlement placement = **spacing 40 / separation 12** (working value; tune after in-world test).
- Q2 SCAVENGER OUTPOSTS: pillagers only in a RARE variant. Normal outposts guarded by skeleton/zombie/husk/drowned (+stray) variants, per biome group
  via structure spawn_overrides. Candidate modded variants: variantsandventures gelid/thicket (zombie-like), murk/verdant (skeleton-like) - UNVERIFIED
  biome rules (custom mob_spawns modifier); vanilla-only table works without them. Vanilla pillager patrols/raids are separate (not changed unless asked).
  Mostly-empty vs occupied mix not finalised: default = mostly abandoned camps + some guarded.
- Q3 PLACEMENT (user delegated to Claude's best choice): practical/mundane structures (settlements, cabins, watchtowers, concrete pads,
  industrial tunnels, scavenger sites, shipwrecks) overworld-wide with biome-matched palettes. Occult anchors (tarbound x4, later sculk site) keep
  their ORIGINAL biome tags (own tag starts as a copy), optionally + `#c:is_wasteland`. Reason: `#c:is_wasteland` currently holds only
  regions_unexplored:ashen_woodland, so restricting to it alone would make them near-nonexistent.
- Still unanswered, defaults stand: Q4 nether/end (bare), Q5 optional formations*/windswept rows (leave off), Q6 tarbound x4 in 3b (yes).
- Mod list: see `docs/mod_list.md`. packwork.zip received 2026-11-14 (403 sources scanned).

- CLARIFICATION (pass 4-1b): 'concrete pads' = Rust and Rebar concrete (visible rebar) + other R&R blocks, NOT vanilla concrete. Use R&R blocks for any concrete/industrial element; keep vanilla for villages/shacks.

- (2026-11-15) REMOVE ALL tipis/teepees from every village/ruin set (savanna custom houses, desert donor wooded_badlands_tipi, gearwrights abandoned savanna). Set-by-set work later; checklist in `docs/redo_list.md`.

- (2026-11-15) The NEW savanna style (pass 7-1+) replaces the gearwrights abandoned savanna variants (`abandoned_{ruin,hamlet,village}_savanna`): abandoned = ruined variants of the new houses.
- (2026-11-15) RELEASE GOAL: publish on CurseForge without needing permission from other authors -> a pass removes every structure that pulls 100% from mods and replaces it with our own (tracked by tools/provenance_audit.py + build_release.py). Also reduce the mod count where possible.

## 2026-11-15 (after pass 9-8): incursion structures, replacements, spawners
- End/Nether gaps: own INCURSION research stations (medieval alchemist x dieselpunk industrial) at both ends of portals (overworld<->End, overworld<->Nether), items fitting each side, expanding as jigsaw mini-villages like fortress/end city.
- Monument / trial chamber / ancient city items: our replacement structures (sculk ruin site etc.).
- Spawners: spawner room in the industrial mineshaft.
