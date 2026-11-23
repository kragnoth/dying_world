# PROGRESS - Dying World / Gearwright's Hollow  (read this first)

Current state, open items, regen order and the pass log. The full history of passes 1 to 9-74 (every decision, with its
reasoning) is in `docs/progress_history.md`. Look things up there when you need them, but don't read the whole file.

## Working rules
- Kragnoth: efficient, direct answers; fish shell; don't launch the game headless unless asked; "can you X?" = brief
  feasibility answer. Use the handle Kragnoth in repos, commits and published files.
- One pass = one commit named after the pass. Add a `## Pass X-Y` entry at the end of this file.
  Say so when a pass DELETES files (unzipping over the top would leave them behind).
- Hand edits live in `user_overrides/data/`; never change only the generated copy.
- Keep `dying_world` and `gearwrights` namespaces separate. Run Python over extracted third-party files with `-I`.
- KubeJS (Rhino 2101): `let` not `const` inside loops/try blocks (`python3 -I tools/lint_kubejs.py`); avoid overloaded Java
  methods; `event.cancel()` last; `runCommandSilent` returns nothing (read results through Brigadier).

## Vision
A dying world: everything should feel like it belongs. Tar, oil, spirits, biomes worn out by over-used technology. Natural
structures are disabled; ours replace them under `dying_world`. The look is Wasteland Vision's job (client-side): the
Occult Foundry vision is forced on for everyone and is also the endgame's mark. Structures carry the real mechanics.

## Current state - 1.0.3 Alpha (2026-11-20)
- Minecraft 1.21.1, NeoForge 21.1.262, 252 CurseForge projects (`modpack/manifest.json`). Data pack format 48.
- Datapack: survivor/abandoned villages in our gradient style for all five families plus rare styles, landmarks, scavenger
  strongholds, research gates and stations (Overworld/Nether/End), the Nether foundry (replaces the fortress), proving
  grounds, sunken lab, sculk dig camp, the lore trail (journals + maps), mineshaft kit. Endgame: the Hollow (altar, doppelganger,
  Escapement chain, creative items; state in kskills_perks 1.2.0).
- Own mods in the pack: Wasteland Vision 0.24.4, kskills_perks 1.2.0, Mob Rules 0.7.1, Hallmarked, Tarbound, Rust & Rebar,
  Cog & Cultivar (its crop / mutation scaffold ships in kubejs/data since 9-85).
- Released files: `tools/export_server.py <version>` builds both the client zip and the server zip (self-installing,
  update-safe; mods download from `modpack/server/server-mods.txt`).
  CurseForge page: `modpack/CURSEFORGE_PAGE.html`; logo: `modpack/logo.png` (source in `tools/logo/`).

## Commands (fish)
```fish
python3 tools/build.py                       # validate + dist/kubejs_data.zip (the instance's kubejs/data)
python3 tools/export.py "<version>"          # client zip only (export_server.py runs this too)
python3 tools/export_server.py "<version>"   # client + server zips; checks server-mods.txt against manifest.json
python3 -I tools/lint_kubejs.py              # Rhino const check over modpack/overrides/kubejs
python3 tools/coherence_audit.py; python3 tools/theme_audit.py
python3 tools/build_release.py               # CurseForge-safe datapack (own/vanilla pieces only)
```
- Server files: `tools/export_server.py` (9-86) zips `modpack/server/*` (README version stamped) + the client export's
  `config/`, `defaultconfigs/`, `kubejs/`, and refuses if `server-mods.txt` and `manifest.json` disagree (by project/file
  ID, 9-87; client-only mods are listed by project ID in its `CLIENT_ONLY`). Regenerating
  `server-mods.txt` is still manual: CurseForge export (manifest + file names) minus the Excalibur resource packs and the
  client-only mods that crash a dedicated server (Create JEI Compat, Easy Auto Cycler, Sodium, Reese's Sodium Options,
  Saros Boosted Brightness, Freecam). Line format `sha1 url`; CDN url `edge.forgecdn.net/files/<id/1000>/<id%1000>/<file>`,
  check with `curl -sIL` (200 = right, 403 = wrong name).
- Never re-zip a CurseForge-app export: it drops `config/wastelandvision/.installed_examples` and sweeps in JourneyMap data,
  logs and caches.

## Regen order (full rebuild of `datapack/`)
Generators need `reference/*.zip` (`tools/make_reference.py`). Superseded, don't run: gen_pass3c1 (-> 3c4), gen_pass5_2 (-> 9_19).
```
1, 3b, 3b2, 3c4, 3c5, 4_1, 4_2a, 4_2b, 9_9, 4_2c, 4_2e, 4_2s, 4_3a, 5_1, 6_1,
8_2, 8_3, 8_4, 8_5, 8_6, 7_1, 7_2, 8_8, 8_11, 9_1, 9_2, 9_3, 9_4, 9_5, 9_6, 9_7, 9_8, 9_10,
9_11, 9_12, 9_34, 9_35, 9_36, 9_44, 9_13, 9_15, 9_18, 9_23, 9_21, 9_24, 9_29, 9_25, 9_27, 9_26, 9_28,
9_14, 9_20, 9_19, 9_22, 9_16, 9_33, 9_76, 9_78, 9_82, 9_83, 8_9, build, coherence_audit, theme_audit
```
- Independent of the structure chain (any order after the above): 9_43, 9_45 to 9_53 (uniques, skill tree, vision config,
  mobrules, sets, Hollow Sight).
- Quests (`tools/quests/`): gen_occult_quests, gen_pass9_43, add_unique_rewards, add_hollow_quests, add_escapement_quests.
- Reconstructed from the per-pass notes in the history. If a generator says otherwise in its docstring, the docstring wins.

## Open items
**Verify in game** (none of these could be checked on a headless server):
- Cog & Cultivar scaffold now loads (9-85): a world joins cleanly (plants / mutations are datapack registries: a bad entry
  stops world load); e.g. dropleaf, cattail, weak tau appear as Cultivar crops; mutations fire.
- Hollow endgame: boss skin/bow pose, first-kill set, Escapement cost scaling, Foundry Lens, Hollow/Lens Sight switching,
  Neo Vitae altar recipe, quest chapter ticking.
- WV 0.24.4 yucca fix (client crash on spruce fence posts).
- Proving grounds vault config (key item + loot table), vertical jigsaw chain + surface hut on slopes.
- 'A Terrible Fortress' advancement completing in the foundry; enchanted trade offers (hermit/tinker/plague scholar).
- End station over the void, foundry bridges, swamp stilt houses, density after the placement tiers.
- Lore: book rendering, maps' red X, location checks in landmark chests. Sculk dig camp cavern size and fit.
- Windows `start.bat` / `install.ps1` (only the Linux script has been run).
- Open-sky air -> void (9-83): no half-cut trees along village streets/plazas, no cube cut into hills by the headframe.
- Structure audit fixes (9-82): villages/cabins/ruins on hills without square notches cut behind them, swamp ruins,
  proving grounds headframe and Hollow marker sitting in the ground, Hollow/proving shaft lamps on the walls.
- Structure placement (9-78): wells set into slopes (no exposed shaft), no wells/mineshafts/outposts over the sea, mineshaft
  tunnels and container yards no longer hanging in the air under high headframes.
- Stilts (9-76/9-77): sculk dig camp and Nether research station buildings no longer floating; stilts look right over drops.

**To do**
- Delete the unused pool `dying_world:cabin/start` (9-82 audit).
- Scrambled journals revealed by Wasteland Vision (designed, not built).
- Excalibur-style textures for the Hollow items (placeholders now).
- kskills_perks: stale javadoc in HollowCommands (mentions runCommandSilent).
- Wasteland Vision idea: an `installExamples=false` config option, so packs don't need `.installed_examples`.
- Server: a tool to regenerate `server-mods.txt` from an export.
- Datapack: strip orphan namespaces of removed jars.

**Parked / open design calls**
- 4-2f mineshaft extras, 4-3b outpost tuning.
- Lighthouse white stripes; burnt mills as landmarks (yes/no).

**Known, harmless**
- Amendments logs "Couldn't load tag minecraft:mineable/pickaxe" on every dedicated-server boot, before Moonlight builds its pack.
- Rust & Rebar file 3.6.2.3 declares 3.6.2.2-beta in its mods.toml.

## Pass index (details in docs/progress_history.md)
| Passes | What |
| --- | --- |
| 1-2 | Natural structure sets and features disabled; namespace set up |
| 3a-3c | Survivor/abandoned villages from donor sets, biome tags incl. modded biomes |
| 4-x | Concrete pads, industrial mineshaft kit, container yards, scavenger outposts |
| 5-x, 6-1 | Scavenger stronghold (bastion replacement); floor guarantee |
| 7-x | Savanna rebuild (gradient palette engine), tipis and stilt palette removed |
| 8-x | Own smithy/lighthouse/cabin/watchtower/wells; one-zip install; third-party datapacks dropped |
| 9-1 to 9-7 | Our village families and streets for all biomes, abandoned ruins, coherence audit |
| 9-8 to 9-24 | Walkthrough fixes, mob drops, research gates/stations, monument/trial/ancient city replacements, Nether foundry, placement tiers, rare styles |
| 9-25 to 9-36 | Kragnoth's Create mills, theme pass, landmarks, loot baseline, lore trail, proving grounds, sculk dig camp |
| 9-37 to 9-43 | Modpack snapshot in the repo, textures, incursion alloys, Arcana quests, Guild uniques |
| 9-44 to 9-60 | The Hollow endgame: arena, boss, Hollowed node, vision lock/release, Escapement chain, kskills_perks takeover, KubeJS fixes |
| 9-61 to 9-74 | Server playtest, config trim, CurseForge page and logo, server files, 1.0.0 and 1.0.1 Alpha |

## Pass 9-75 (2026-11-17) - comment cleanup, PROGRESS rewritten
- KubeJS: pass-number and changelog comments removed from the Hollow/Escapement/alloy scripts (the Rhino explanations
  stay). Kragnoth's scripts: only stale provenance removed (old file paths, "from compat_report/tree_dump/cloche.zip",
  "--> Added" markers, analyzer notes), and `00_config.js` references now point to `startup_scripts/gh_progression_config.js`.
  Config comment: Embers (not in the pack) -> Neo Vitae / Tarbound. No code changes.
- PROGRESS.md moved verbatim to `docs/progress_history.md`; this file rewritten as current state + open items + one
  consolidated regen order. Status notes added to `docs/redo_list.md` (done) and `docs/wasteland_vision_notes.md` (stale).
- No files deleted (one moved).

## Pass 9-76 (2026-11-17) - footings: no more floating dig-camp buildings
- Cause: for rigid jigsaw children the beard's ground reference is the START piece's bottom + 1, not the child's own
  bottom. The dig camp's floors are 3 above the pit's bottom, so beard_box carved a 3-block band of air under every
  walkway and building; the fill below that only reaches ~12 blocks and never undoes carver caves. (Read from the 1.21.1
  Beardifier / JigsawPlacement bytecode.) A deeper template doesn't move the reference, so footings don't deepen the carving.
- NEW `tools/footing.py`: shifts a piece up and fills under its footprint (log posts at corners + every 4 along the edges,
  rubble elsewhere); marks the NBT (`DwFooting`) so re-runs skip it.
- `gen_pass9_36.py`: every dig-camp piece but the pit gets a 10-deep footing (spruce logs + deepslate/tuff rubble).
  Re-generated; each piece is block-for-block the same as before above the footing.
- NEW `tools/gen_pass9_76.py` (after 9_15/9_23, before build): the Nether research station's 8 buildings (normal +
  derelict) get the same, with stripped crimson stems (fireproof) and blackstone/basalt. Streets/causeways and the hall
  are untouched; the nether foundry keeps terrain_adaptation none (bridges by design).
- No files deleted. Only new chunks change. Untested in game; deeper boxes could block the odd building placement
  where a street drops a level.

## Pass 9-77 (2026-11-17) - stilts instead of plinths
- Kragnoth's screenshot: the 9-76 footing showed as a solid rubble storey under each building (the carved band is
  visible). Now mineshaft-style: only the log posts (corners + every 3 along the edges, 12 deep); the rest of the space
  under a piece is left out of the template, so rock stays rock and drops stay open under the stilts.
- `tools/footing.py`: posts only by default (`fill` optional); re-running strips an old footing first. gen_pass9_36
  (spruce logs) and gen_pass9_76 (stripped crimson stem) re-run.
- No files deleted.

## Pass 9-78 (2026-11-20) - structure placement: wells, mineshaft, beaches, Structure Essentials
- Kragnoth's report + screenshots: wells sitting on the surface/over the sea, a mineshaft on a coastal cliff with its
  container-yard hall hanging over the ocean, wild-tag structures on oceans.
- `modpack/overrides/config/structureessentials.json`: autoBiomeCompat OFF (Kragnoth's file). At strictness 0.75 it was
  adding "similar" biomes, coasts and oceans included, to every structure.
- NEW `tools/gen_pass9_78.py` (after 9_76, before 8_9/build; re-runnable):
  - beach/shore biomes removed from has_structure/concrete_pad_wild (wells/wild + outposts use it) and industrial_mineshaft
    (10 entries). Lighthouse, beached shipwreck and road signs keep them.
  - industrial mineshaft: collar -> 2 plain shaft segments (new pools mineshaft/shaft_upper_a, _b) -> normal shaft, so
    tunnels start >= ~50 below the head instead of ~23; size 14 -> 16; terrain_adaptation none -> beard_thin.
  - wells: split at ground level into wells/<style>_top (start: platform + roof) and <style>_shaft (jigsaw below);
    beard_thin, start_height -1 (platform one block into the ground). The old one-piece wells/<style>.nbt are still
    written by 8_6 and read by 9_78, but no pool uses them.
- No files deleted. Only new chunks change. Untested in game.

## Pass 9-79 (2026-11-20) - 1.0.3 Alpha release files
- `modpack/manifest.json` / `modlist.html` from Kragnoth's 1.0.3 Alpha export (same 252 files as 1.0.1, so
  `server-mods.txt` is unchanged); server README version bumped. His export's kubejs/data matched the 9-78 build; its
  scripts and quest files differed only in comments/formatting, so the repo copies were used.
- Built `Gearwrights_Hollow_1.0.3_Alpha.zip` (tools/export.py) and `_Server.zip` (modpack/server + config, defaultconfigs, kubejs).

## Pass 9-80 (2026-11-20) - fix: mineshaft reach broke the structure registry
- Headless test of 1.0.3: "Structure size including terrain adaptation must not exceed 128" for industrial_mineshaft -
  any terrain adaptation adds 12 to max_distance_from_center, and 9-78 gave the mineshaft beard_thin at reach 128, so the
  whole worldgen/structure registry failed to load (no world loads). gen_pass9_78 now caps it at 116. Both 1.0.3 zips rebuilt.
- Rule: with terrain_adaptation other than none, max_distance_from_center <= 116.
- Ocean-spawn scan started (16 ocean points, locate every overworld structure) but stopped at Kragnoth's request; he tests in game.

## Pass 9-81 (2026-11-20) - mineshaft headframe: girders/beams the right way round, lamps hung
- Kragnoth: the headframe lamps hung in mid-air and the girder/beam roles were swapped. Rust & Rebar's girder is the
  big H-section, the beam the small I-beam. gen_pass4_2s: top ring now girders (legs already were), the centre cross
  member a beam (`low=true`, flush with the block bottom, girder connectors at its ends), and the two lamps moved
  under it (x 5/11, z 8) instead of hanging from nothing at z 5/11.
- Only the two shaft_head NBTs changed (4_2s re-run, then 9_78 re-run; nothing else differs). No files deleted.

## Pass 9-82 (2026-11-20) - structure audit fixes
- Audit of all 79 structures against ATi / Integrated Villages / vanilla conventions (script: terrain adaptation, reach,
  explicit air, footprints, hanging lights, loot, salts, jigsaw refs). Fixed the cheap, high-value ones:
- NEW `tools/gen_pass9_82.py` (after 9_78, before 8_9/build; re-runnable):
  - 38 overworld surface structures beard_box -> beard_thin (villages, hamlets, cabins, ruins, smithies, chapel, cottages,
    lighthouse, scavenger strongholds, abandoned_ruin_swamp, proving_grounds, the_hollow). beard_box cleared each piece's
    whole box above its floor = square notches in hillsides. Research gates/stations and the sunken lab stay beard_box.
  - 62 land jigsaw structures get liquid_settings ignore_waterlogging (not swamp, sunken lab, lighthouse).
  - 7 caged lamps saved facing down under air beside a wall turned to face away from the wall (Hollow shafts 1/2,
    proving shafts 1/3).
- Not done (in Open items): structure_void for exterior air in the headframe/streets/town centres; dead pool cabin/start.
- No files deleted. Only new chunks change. Untested in game.

## Pass 9-83 (2026-11-20) - open-sky air -> structure void
- NEW `tools/gen_pass9_83.py` (after 9_82, before 8_9/build; re-runnable): in every street piece (villages, abandoned
  villages, scavenger strongholds), the town centres and the mineshaft headframes, air at y >= 2 with nothing above it in
  its column is dropped from the template (= structure void, the world keeps what's there). The ground layer and the one
  above stay air (clears trunks/plants off paths); air under roofs, the headframe ring and beams stays.
- 51,965 cells in 205 templates. Jigsaws untouched. No files deleted. Untested in game.

## Pass 9-84 (2026-11-23) - Quality Equipment -> Hallmarked
Quality Equipment is gone from the pack (Kragnoth deleted the modified jar); Hallmarked replaces it.
- Skill tree (`kskills` definitions.json): 4 skills had `"required_mods": ["quality_equipment"]`, so Pufferfish skipped them
  entirely; now `hallmarked` (and their "Requires:" line). 4 rewards used `quality_equipment:projectile_damage` /
  `damage_resistance`; now `hallmarked:...` (both registered by Hallmarked).
- Qualities: the 7 pack overrides (ascended, blessed, divine, exquisite, forsaken, impenetrable, mythic) moved from
  `kubejs_base/data/quality_equipment/qualities/` to `kubejs_base/data/hallmarked/qualities/` (same file names, so they
  override Hallmarked's own files directly): names `hallmarked.quality.*`, attributes `hallmarked:*`, `color_code` section
  codes -> Hallmarked's `color` names. Values unchanged.
- **Deletes files:** `kubejs/data/quality_equipment/` (the whole folder). Unzipping the new kubejs_data.zip over an old
  install leaves it behind: delete `kubejs/data/quality_equipment/` by hand (harmless if left, but it double-loads those 7
  qualities under the old names via Hallmarked's legacy mapping).
- No `quality_equipment` references remain in kubejs_base, user_overrides, datapack or modpack overrides.

## Pass 9-85 (2026-11-23) - kubejs_base cleanup; Cog & Cultivar scaffold actually loads
Checked every script (94 in tools/, KubeJS client/server/startup scripts, server files, docs): nothing references the folders
below. `kubejs_base/data` ships: build.py zips it into `dist/kubejs_data.zip`, export.py writes that as `overrides/kubejs/data`.
- **Cog & Cultivar scaffold never loaded:** `kubejs_base/data/cultivar_scaffold/` was the whole scaffolded datapack (its
  `pack.mcmeta` + `data/`) dropped into kubejs/data, so Minecraft read it as namespace `cultivar_scaffold` with paths starting
  `data/...`; Cultivar's plant / mutation datapack registries only read `data/<ns>/cultivar/plant|mutation/`. Cog & Cultivar's
  own PACKMAKERS.md says to copy the *contents* of `cultivar_scaffold/data/`. Moved those 46 files up into
  `kubejs_base/data/<ns>/` (atmospheric, autumnity, environmental, immersiveengineering, minecraft, minersdelight,
  mynethersdelight, neovitae, regions_unexplored, supplementaries, windswept): 23 plants + their mutations are new in game.
  Checked first: valid JSON, only fields Cultivar's own 55 plants / 37 mutations use (+ `neoforge:conditions`), every
  other-mod entry guarded by `mod_loaded` and all those mods are in the pack, no overwrites, no build conflicts.
  `mutation_plan.csv` (the scaffold's working sheet) -> `docs/cultivar_mutation_plan.csv`; inner `pack.mcmeta` removed.
- **Dead data removed (27 files):** `agritechevolved/` (7 planter recipes; mod not in the pack), `createliquidfuel/` (19 fuel
  compat files; mod not in the pack), `create_ultimate_factory/` (1 recipe disabler; mod not in the pack).
- Kept: `incontrol_port/` (3 Mob Rules rules; Mob Rules reads `mobrules/` from any namespace, so they're live).
  `datapack/` disable overrides for 8 structure mods no longer in the pack stay (harmless, protective; generator-made).
- **Deletes files:** `kubejs/data/cultivar_scaffold/`, `kubejs/data/agritechevolved/`, `kubejs/data/createliquidfuel/`,
  `kubejs/data/create_ultimate_factory/`. The README in kubejs_data.zip already says to replace kubejs/data rather than
  unzip over it; if unzipped over an old install, delete those four folders by hand.
- Plants / mutations are datapack registries: rejoin the world or restart the server (`/reload` won't do it).

## Pass 9-86 (2026-11-23, branch `cleanup`) - release pipeline check; server zip scripted
Kragnoth: test the client / server release scripts; further cleanup goes on branch `cleanup`, merged to main once verified.
- Ran: build.py, validate.py, export.py, lint_kubejs.py: OK. build_release.py, coherence_audit.py, theme_audit.py,
  provenance_audit.py need `reference/*.zip` (not in git; `tools/make_reference.py` from an instance): not runnable here.
- Client export checked: manifest 1.21.1 / NeoForge 21.1.262 / 252 files; overrides = config, defaultconfigs, kubejs (Cultivar
  files in place), options.txt, resourcepacks; `config/wastelandvision/.installed_examples` present.
- Server: server-mods.txt (234) = manifest (252) minus 6 client-only mods minus 12 CurseForge resource packs (11 Excalibur +
  Human Era); no stale versions. All 234 CDN URLs answer 200. NeoForge 21.1.262 in start.sh, install.ps1, README, manifest.
- **Deleted** 4 tracked JEI backups (`config/jei/client/{,default/}jei-client.ini.bak.{1,2}`; committed before .gitignore
  covered them); export.py now skips `*.bak.*` anyway.
- New `tools/export_server.py [version]`: runs export.py, then writes `dist/Gearwrights_Hollow_Server_<version>.zip` (was a
  manual zip); stops if server-mods.txt has versions not in the manifest or misses a mod that isn't client-only / a pack.
- Open: regenerating server-mods.txt itself (needs file names, which manifest.json doesn't have) stays manual.


## Pass 9-87 (2026-11-23, branch `cleanup`) - pack builder run-through
Ran every builder step in order: build.py, validate.py, export.py, export_server.py, lint_kubejs.py, build_release.py,
coherence_audit.py, theme_audit.py, provenance_audit.py (the reference/*.zip extractions are present in this workspace).
All run clean. Both 1.0.4 test zips checked: manifest 252 files / author Kragnoth, `.installed_examples` in both, no junk
(JourneyMap, logs, caches, .bak), start.sh 0755, README version stamped.
- `export_server.py`: the mod-list check compared COUNTS (missing == 6 + number of resource packs), so swapping one mod for
  another with the same count passed. Now by ID: `CLIENT_ONLY` names the 6 crash-on-server mods by project ID; resource packs
  = manifest projects modlist.html doesn't list; it stops on a stale file, an unexpected missing mod, or a client-only mod in
  the server list. Tested with a line removed (names the missing project).
- Stale entries for agritechevolved (removed in 9-85) dropped from `config/jade/sort-order.json` and both JEI
  `recipe-category-sort-order.ini` files.
- Audit reports (`docs/coherence_audit.md`, `theme_audit.md`, `provenance_audit.{md,json}`, `release_report.md`) were last
  generated many passes ago (still showed beard_box, pre-9-19 set names); regenerated.
- PROGRESS: commands take `<version>`; current state lists Cog & Cultivar and export_server.py.
- Still manual: regenerating server-mods.txt (manifest.json has no file names). No files deleted.

## Pass 9-88 (2026-11-23) - Kragnoth's latest skill tree; cleanup merged to main
- `kubejs_base/data/kskills/puffish_skills/`: Kragnoth's current files dropped in. config/category/experience unchanged;
  skills.json 456 -> 659 nodes (203 new: the inner ring, the arcs between disciplines and the seam/"h" crossings),
  79 moved; definitions.json +170 (384 total; `d_qe`/`d_qe_k` changed); connections 764 edges.
- Checked: valid JSON; every node's definition exists and every definition is used; every edge names real nodes; no two
  nodes share a position; everything is reachable from `awakening_1` except `hollowed_1`, `hollow_sight_1`,
  `lens_sight_1` (unlocked by kskills_perks, by design); every reward namespace is a mod in the pack (apothic_attributes,
  puffish_attributes, kskills_perks, caverns_and_chasms, lodestone, neovitae, ftbultimine, hallmarked, caelus); no
  `quality_equipment` left (9-84 holds).
- Branch `cleanup` (9-86 .. 9-88) fast-forwarded into `main`; work continues on main. No files deleted.
