# PROGRESS - Dying World worldgen project  (READ THIS FIRST in any new chat)

Handoff file. Chats are separate and files may be lost, so this zip is the source of truth.
At the end of every pass: update this file, bump the pass log, re-zip, hand back.

## Working rules (from the user)
- Be efficient; use just enough info. Passes must be small (fit well inside one context window).
- Always finish a pass with a usable zip + updated PROGRESS.md. Split work into sub-passes rather than risk a cut-off.
- Don't read huge files. Use `docs/structure_inventory.md` / `.json` instead of re-opening packwork.zip.
- User re-uploads: (a) this project zip, and (b) packwork.zip only if a pass needs raw mod files.
- Uploading a zip does not cost tokens by itself; only what gets read does.

## Vision
Dying world: everything should feel like it belongs. Ghostly zones, tar, oil, biomes weakened by
over-use of technology. Natural structures are all disabled; we curate our own (re-using mod
structure pieces where useful) under our own namespace, with decay/tar/oil theming.

## Environment
- Minecraft 1.21.1, NeoForge, Prism Launcher on CachyOS. Data pack format 48.
- `tools/packwork.py` scrapes all jars (+ vanilla) into packwork.zip (+ `_packwork_sources.md` report).
- Pack has KubeJS, Lithostitched, Cristel Lib, Biolith, Regions Unexplored, Create stack, Tarbound, etc.
- Own namespace: **`dying_world` (PROVISIONAL - user may rename; only used from pass 2 on).**

## Pass log
| pass | status | summary |
|---|---|---|
| 1 | DONE | Disabled all 69 structure sets (19 namespaces). Inventory + docs generated. |
| 2 | DONE | User verified /locate clean. Removed feature-based structures; added Wasteland Vision notes; stronghold + nether fortress placeholders restored under `dying_world:`. See `docs/pass2_decisions.md`. |
| 3a | DONE | `docs/roster.md` draft + user answered questions -> `docs/user_decisions.md` (AUTHORITATIVE vision; read it). |
| 3a+ | DONE | Q1-Q3 answered (see `docs/user_decisions.md` 'pass 3b prep'): settlements 40/12, rare pillager outposts + undead guards, mundane=overworld-wide / occult=original tags. |
| 3b-1 | DONE, TESTED OK (all 5 /locate worked) | tarbound x4 + abandoned_cabin registered as `dying_world:` (structure+biome tag+set each). `tools/gen_pass3b.py`. Test steps in `docs/INSTALL.md`. |
| 3b-2 | DONE (untested) | burnt_homestead 48/16, burnt_manor 80/28, burnt_watchtower 60/20, abandoned_watchtower 56/20 as `dying_world:` (same generator, `tools/gen_pass3b.py`). |
| 3b-3 | DONE (untested) | gearwrights abandoned_ruins 24/8, hamlets 32/12, villages 44/16 (7 biome variants each, original frequency kept for ruins .55 / hamlets .85). |
| 3b-4 | DONE (untested) | collapsed_minehead 48/16, ruined_chapel 64/22, abandoned_smithy 80/30, lighthouse 80/30, shipwrecks 40/12 (2 variants), forsaken wells 40/14 freq .6 (11 variants). Road signs DEFERRED to 3c. |
| 3b-2/3/4 | TESTED OK | user: all locates work. |
| 3c-1 | DONE, TESTED OK (user: looked good) | Survivor villages, PLAINS only: `dying_world:village_plains` in set `dying_world:survivor_villages` (40/12). Mechanism in `tools/gen_pass3c1.py` docstring. |
| 3c-2 | DONE, TESTED OK (user: looked good): TAIGA | `tools/gen_pass3c1.py taiga` (23 houses x2). User chose taiga as next most common type. |
| 3c-3 | DONE (untested): DESERT, REDONE with variants | `python3 tools/gen_pass3c1.py plains taiga desert`. 24 houses; 1 lived + 3 worn variants (96 pool entries). See 'Pass 3c-3b'. |
| 3c-4 | DONE, TESTED OK (user: looked good) | ALL five survivor villages in one run: `python3 tools/gen_pass3c4.py` (supersedes gen_pass3c1.py). Savanna + snowy added; widened biome tags; mod houses mixed in (hodgepodge) per family. See 'Pass 3c-4'. |
| 3c-4b | DONE, TESTED OK | Tag-driven biome families incl. MODDED biomes for all village tags + abandoned ruin/hamlet/village tags (`tools/village_biomes.py`, used by gen_pass3c4.py). See 'Pass 3c-4b'. |
| 3c-5 | DONE (untested) | Village exclusion zones re-added + road signs registered (`tools/gen_pass3c5.py`). See 'Pass 3c-5'. |
| 3c-5 | (user: continued without reporting test results; treat as untested) | |
| 4-1 | DONE (untested) | Concrete pads + broken lean-tos (ruined-portal replacement): `python3 tools/gen_pass4_1.py`. See 'Pass 4-1 result'. |
| 4-1b | DONE, TESTED OK (user: concrete pads are good) | CORRECTION: pads redone with RUST AND REBAR concrete (user meant R&R `rebar_concrete` w/ visible rebar, not vanilla concrete). Same generator, re-run. See 'Pass 4-1b'. |
| 4-2a | DONE (untested) | Industrial mineshaft core kit (replaces vanilla mineshafts): `python3 tools/gen_pass4_2a.py`. Tunnels + door alcoves + 1 storage room type. See 'Pass 4-2a'. |
| 4-2b | DONE, TESTED OK (user: mineshaft generates, 'rest looks good'; lamps fixed in 4-2b-lights) | 7 new room pieces (workshop, office, fuel store, rare stash cell) + 4 loot tables: `python3 tools/gen_pass4_2b.py` (run after gen_pass4_2a.py). See 'Pass 4-2b'. |
| 4-2b-lights | DONE (untested) | Lamp mix changed (see 'Pass 4-2b-lights'). NOTE: this was a MISREAD of the user's 'the other two... right states' (they meant girders/beams); harmless, kept unless the user wants the old all-caged-lamp look back. |
| 4-2c | DONE (untested) | Container yard halls: `python3 tools/gen_pass4_2c.py` (run after 2a and 2b). See 'Pass 4-2c'. |
| 4-2c-girders | DONE (untested) | Girder/beam connection states + no more floating pieces (see 'Pass 4-2c-girders'). |
| 4-1c | DONE (untested) | Pad chest loot now includes ruined-portal loot (see 'Pass 4-1c'). |
| 4-2c2 | DONE (untested) | Yard-hall containers now SOLID + decorative (user screenshots); branch pieces never build over open air ('no float'). See 'Pass 4-2c2'. |
| 4-2s | DONE (untested) | CENTRAL SHAFT surface->down (head, collar, 8 segments, caps) feeding the tunnel/hall/room network: `python3 tools/gen_pass4_2s.py` (run LAST). See 'Pass 4-2s'. |
| 4-2s2 | DONE (untested) | Shaft ladders -> `rusted_rung_ladder` (no cage); branch levels get a full grate floor except the ladder cell. See 'Pass 4-2s2'. |
| 4-2c3 | DONE (untested) | Containers 3x3 ends + 4-7 wall columns, cave-proof boxes layer; undead-only spawn_overrides on the mineshaft. See 'Pass 4-2c3'. |
| 4-2c3 | TESTED OK (user: containers 'perfection', undead spawns 'awesome') | |
| 4-2e | DONE (untested) | Flooded + tar-pit tunnel variants: `python3 tools/gen_pass4_2e.py`. See 'Pass 4-2e'. |
| 4-2f | PARKED (user: mineshafts good for now, may add later) | Ideas: shaft water sump, railings, always-lit ladder lamps, flooded/tar corners+tees. |
| bunkers | DROPPED (user) | Wet-biome R&R survivor bunkers: overkill now that mineshafts are fleshed out. |
| 4-3a | DONE (untested) | Scavenger outposts: `python3 tools/gen_pass4_3a.py`. See 'Pass 4-3a'. |
| 4-3a-lights | DONE (untested) | Floodlights fixed (see 'Pass 4-3a-lights'). User: abandoned outposts look good otherwise; checking the other variants. |
| 4-3a | TESTED OK | User: abandoned look good; pillagers + zombies spawn as intended (within the pack's Mob Rules limits). Floodlight fix 4-3a2 not yet reported. |
| 4-3b | OPTIONAL | Tune outposts from feedback; optional: more camp layouts, raider banner/flag, biome-matched accents. Then pass 5 (scavenger stronghold / sculk site). |
| 5-1 | DONE (untested) | Scavenger stronghold base: keep + zombie-village streets + barricades + scavenger decor + placed immune piglins + bastion loot: `python3 tools/gen_pass5_1.py`. See 'Pass 5-1'. |
| 5-2 | DONE (untested) | Fortified houses + floor repair + piglins in every house and more in the streets: `python3 tools/gen_pass5_1.py && python3 tools/gen_pass5_2.py`. See 'Pass 5-2'. |
| 5-3 | TODO NEXT (after test) | Tune stronghold from feedback; then sculk ruin site. |
| 6-1 | DONE (untested) | Gearwrights abandoned ruins/hamlets/villages -> terrain_adaptation beard_box (no floating floors on eroded hillsides): `python3 tools/gen_pass6_1.py` (run after 3b2/3c4). See 'Pass 6-1'. |
| 7-0 | DONE | Savanna rebuild plan: furniture catalogue, redo list, style board (docs only). See 'Pass 7-0'. |
| 7-0b | DONE (notes only) | USER: remove ALL tipis/teepees in every set; checklist in `docs/redo_list.md` ('TIPI / TEEPEE REMOVAL'); work set by set later. |
| 7-0c | DONE (docs only, no game files changed) | Outlier scan over all village houses: `python3 tools/outlier_scan.py` -> `docs/building_outliers.md` (group-level + single-house outliers). User will comment on it; the 7-0 open question about 'clashy Mediterranean' sets stays open until then. |
| 7-0d | DONE (docs only) | USER: stilt/pole houses disliked -> whole palette marked for removal in all villages. `tools/stilt_scan.py` -> `docs/stilt_houses.md`; checklist in `docs/redo_list.md` ('STILT / POLE HOUSES'). Savanna base set (7 stilt of 18) + gearwrights abandoned savanna marked. CORRECTED 7-0d2: swamp stilt houses are KEPT (they fit); only colour-panel stilt palettes go. |
| 8-0 | DONE (tools + docs; no game files changed) | USER DIRECTION: release on CurseForge WITHOUT third-party permissions -> remove every structure that pulls 100% from mods, replace with our own over the passes; also cut the mod count. Built the provenance audit + policy-driven RELEASE build. See 'Pass 8-0'. |
| 7-1 | TODO NEXT (user: the new savanna style REPLACES the abandoned savanna variants; first own-built batch)| Furniture library + palette + ONE test cottage (base/lived/ruined) as a savanna `dying_world` house; then 7-2.. the first batch (~10 buildings). Waiting on user answers in 'Pass 7-0'. |
| 5-4 | TODO | Sculk ruin site (ancient-city eq.): reuse the 5-1 village base (retargeted streets) + sculk replace processor + loot. |
| 4-2d | DROPPED (user) | Catwalk halls: not needed, the central shaft already links levels. |
| 4-2d (old) | superseded (after user tests 4-2c2/4-2s; catwalk halls can also hang off the shaft), WAIT for user's feedback on container halls + girders/beams first | Multi-floor catwalk halls (rusted_catwalk / caged ladders / createdeco catwalks), then 4-2e flooded/tar/deep variants + stairs + spawner room. |
| 4-2 (old, superseded) | |  Next small build from 'Pass 4 candidates' (suggest: scavenger outposts OR wet-biome bunkers; ask user). |
| 3b (orig) | superseded by 3b-1/2 | Tier A re-register: gearwrights burnt_*/abandoned_*, abandoned_cabins, abandoned watchtower, shipwrecks, road signs (+tarbound). Mechanism in roster.md. |
| 4 | TODO | New builds: concrete pads+lean-tos, industrial tunnels (mineshaft replacement), scavenger outposts. |
| 5 | TODO | Scavenger stronghold (bastion eq.), sculk ruin site (ancient city eq.), biome palette processors. |
| 4+ | TODO | Build curated structures in `dying_world` namespace, a few at a time. |

## Pass 1 - what was done
- Every `worldgen/structure_set/*.json` in vanilla + mods is overridden at its ORIGINAL id with
  `"structures": []` and a plain vanilla `random_spread` placement (no mod codec dependencies).
  Empty sets cannot spawn anything. Result: `datapack/` and `dist/dying_world_datapack.zip`.
- Checked: no Lithostitched `add_structure_set_entries` modifiers exist, so nothing re-adds entries.
  Lithostitched only adds template-pool elements (harmless with sets empty).
- Two createnewbeg set files contain `//` comments (invalid strict JSON). Irrelevant: we overwrite them.
- `tools/gen_pass1.py --packwork packwork.zip` regenerates everything; `--check` reports drift
  (new/removed sets after mod changes).

## INSTALL / TEST (untested by me - confirm in pass 2)
- Important: `gearwrights` and `vsrevamped` sets (10 files) come from the pack's own **`kubejs/data`**
  folder, and KubeJS data loads on top of world datapacks. So install by copying the contents of
  `datapack/data/` into `<instance>/minecraft/kubejs/data/` (overwrites those 10 files, adds the rest).
  Alternative: world datapacks folder, but then kubejs's 10 sets may still win. Check for `kubejs/data/gearwrights`.
- Restart the game/server (worldgen registries don't fully reload with /reload).
- Only NEW chunks are affected. Test in a fresh world or far from explored area.
- Verify: `/locate structure #minecraft:village` (and a few modded ones) should report none found.
  Run `/datapack list` to see loaded packs.

## Known consequences (decisions needed in pass 2/3)
- Stronghold gone -> Eye of Ender useless -> **no end portal**. Nether fortress gone -> **no blaze rods**
  (Create/IE progression may need them). Bastions gone -> piglin/ancient debris loot access unchanged,
  but bastion loot gone. Ancient city/trial chamber loot gone (trial keys, ominous things).
  Ruined portals, buried treasure (maps), shipwrecks gone. Villages gone -> no natural villagers;
  cartographer maps for structures will fail gracefully.
- => Pass 3 must pick a **progression-critical shortlist** to restore first: nether fortress (blaze),
  stronghold/end portal, something for villagers, maybe bastion.
- Feature-based "structures" are NOT touched yet: see `docs/feature_structure_candidates.md`
  (ant hills, realmrpg underground chambers) + vanilla biome features (monster rooms, fossils, desert wells,
  geodes). Pass 2: disable with `neoforge:none` override (modded) / `neoforge:remove_features` (vanilla).

## Curation approach (planned)
Reuse existing mod structure pieces by registering NEW structure/template_pool/structure_set files under
`dying_world:` that point at the original template pools / nbt, plus our own processor lists (decay, tar,
oil staining, cracked/rusted blocks) and our own biome tags (`#dying_world:has_structure/...`).
Authoring brand new .nbt is possible via script, but reuse + processors is far cheaper per pass.
Candidates worth reusing by theme (from inventory): tarbound (4 sets), forsaken, gearwrights abandoned_*/burnt_*,
abandoned_cabins, watchtower_building (abandoned), formations*, windswept ruins, caverns_and_chasms.

## File map
- `datapack/` datapack source (pass1 overrides + `dying_world` namespace files). `dist/dying_world_datapack.zip` installable.
- `tools/validate.py`, `tools/build.py` (validate+zip), `tools/gen_pass1.py` (regenerates ONLY structure_set overrides; safe for later files).
- `docs/wasteland_vision_notes.md`, `docs/pass2_decisions.md`.
- `docs/structure_inventory.md|json` all sets/structures/biome tags per namespace (reference; replaces packwork lookups).
- `docs/disabled_structure_sets.txt` ids disabled. `docs/feature_structure_candidates.md` pass-2 list.
- `tools/gen_pass1.py`, `tools/packwork.py`.

## Design decisions log (from user conversations)
- Agreed with plan so far: reuse+retheme mod structures, sparse/rare, restore vanilla milestones in reskinned form
  (blaze source, end portal, villagers), biomes as separate workstream that structures hook into via own biome tags.
- **Ghost zones are NOT a structure/worldgen concern.** Mod `wastelandvision` (0.23.1, by Kragnoth) is a CLIENT-SIDE
  hallucination layer: world is normal, player sees a dying/occult version (ghost overlays on trees/areas that can't be
  interacted with, retextured blocks). Default vision "Soot & Tar" (soot stone, creosote timber, tar mud, falling ash).
  Visions are data-driven in `config/wastelandvision/` (NOT in packwork.zip; not yet seen). Toggle key H.
  It ships tag `#c:is_wasteland` (currently only `regions_unexplored:ashen_woodland`).
- Therefore two layers: Wasteland Vision = cosmetic look (client). Our structures/processors = real mechanics only
  (actual tar/oil blocks, rusted palette relevant to Create, loot, chest contents). Don't spend processors on pure cosmetics.
- Idea (unconfirmed): use `#c:is_wasteland` as one of our structure biome tags.
- Assumed split pending user confirmation: vision = how it looks; structures = what is actually there.

## Status after pass 2
- Namespace `dying_world` CONFIRMED. /locate verified clean after kubejs/data install. Nether/End access must remain.
- Wasteland Vision config received and summarised in `docs/wasteland_vision_notes.md` (client-only, block-id/tag rules,
  not structure-aware; ghost groves = world-space noise). Look-vs-mechanics split: treated as agreed.
- Theming deferred by user: "changing base structures with themed ones sounds ok, decide theming later".
- Install: copy contents of `datapack/` `data/` into `kubejs/data/` (as before), restart. Test: `/locate structure
  dying_world:...` not needed; use `/locate structure minecraft:stronghold` and `minecraft:fortress` (should now be found),
  and check monster rooms/desert wells are gone in new chunks.

## Next (proposed pass 3, small, needs user input)
1. User decides which other base structures return as themed versions, and priority: villages (villagers), bastions,
   ancient city, trial chambers, ruined portals, outposts, mansions, monuments, shipwrecks, mineshafts, etc.
   Default proposal: villages + nether fortress/stronghold first, everything else optional/rare.
2. Possibly ask user for `config/wastelandvision/mappings-<vision>.txt` to avoid blocks the vision hides.
3. Then Tier-A pass: for each chosen structure, a `dying_world:` set (own salt/spacing, optional own biome tag).
   Theming (processors, tar/oil blocks, loot) is a later pass.

## Self-contained reference - you should NOT need packwork.zip for design/curation (rebuild: `tools/make_reference.py`)
`reference/` (~29 MB). Read selectively: `unzip -p reference/<zip> <path>`, `unzip -l ... | grep`, `grep` the .md. Never dump whole.
- `blocks_index.md|json` - 8,890 block ids across 71 namespaces (with display names where they differ). USE THIS FIRST for
  palette choices (e.g. rustandrebar 130 blocks: rusted corrugated metal, container walls/doors, chain-link, barbed wire,
  bund walls, concrete-encased pipes, burning barrel, breeze blocks; tarbound 17; minecraft 1286 incl. all concrete;
  createdeco 389; immersiveengineering 390; immersivepetroleum 27).
- `worldgen_reference.zip` (3.9 MB) - all `data/*/worldgen/*` (biomes, configured/placed features, structure, structure_set
  [ORIGINAL pre-override], template_pool, processor_list, noise), all `data/*/tags`, neoforge biome_modifiers,
  lithostitched modifiers, damage types, enchantments.
- `structures_nbt.zip` (14 MB) - all 5,544 structure .nbt files. `nbt_index.txt` = their paths. (Delete the zip if size matters.)
- `loot_and_recipes.zip` (11 MB) - all loot tables (incl. chests/ blocks/ entities/) + all recipes.
- `lang_en_us.zip` - display names per mod.
- NOT included: textures, models, sounds, advancements, other assets. If ever needed, ask the user for a slice or to run
  `tools/packwork.py --textures`. Also not included: user's `config/wastelandvision/mappings-<vision>.txt` (ask if needed).
- Other docs: `docs/structure_inventory.json|md`, `docs/wasteland_vision_notes.md`, `docs/pass2_decisions.md`.
- Note: reference reflects the modlist at time of generation. If mods change, user re-runs packwork.py and
  `tools/make_reference.py` + `tools/gen_pass1.py --check`.

## READ FIRST: `docs/user_decisions.md` holds the user's vision answers (villages 40/60 lived/worn, replace-only decay,
portal->concrete pads, mineshaft->industrial tunnels, outposts->scavenger, bastion/ancient city overworld equivalents, biome-tied palettes, Rust and Rebar usage).

## Pass 3a result
- `docs/roster.md` = draft roster (slots, source, proposed chunk spacing, verdict KEEP/RETHEME/OPT/DROP) + the 3-file
  mechanism per curated structure (copy structure json w/ own biome tag that initially includes the original tag; own set w/ salt+spacing).
- User asked to "go on" without answering the open questions, so defaults stand until they steer. Re-read roster.md 'Open questions'.
- Next: 3b first batch (tarbound x4 + villages), then wasteland-vision `mappings-*.txt` before any block retheming.

## Pass 3a+ result (2026-11-14)
- Decisions recorded in `docs/user_decisions.md` (section 'Answers recorded in pass 3b prep'). `docs/mod_list.md` added.
- Standing rule (user): hand back zips NAMED WITH A PROGRESS MARKER, `dying_world_project_<pass>.zip` (e.g. `_3b-1`, `_3b-2`), so each stage can be backed up. Inner folder stays `dying_world/`. Keep progress in the zip as we go; update this file + re-zip at the end of EVERY reply that changes anything. User has limited tokens: one small step at a time, easiest first.
- NEXT (3b, first small step): generate tarbound x4 + abandoned_cabins sets under `dying_world:` (3-file mechanism in roster.md), run tools/validate.py + tools/build.py, then install/test steps. Remaining 3b rows follow in separate small steps.

## Pass 3b-1 result (2026-11-14)
- New: `datapack/data/dying_world/{worldgen/structure,worldgen/structure_set,tags/worldgen/biome/has_structure}/<id>.json` for charnel_crypt(64/20),
  drowned_radio(40/14), researcher_cabin(56/18), wayside_shrine(40/14), abandoned_cabin(36/12). Salts = crc32 of id. regular_cabin NOT registered (stays disabled).
- Tarbound wrappers are `tarbound:dry_land` and still point at `tarbound:*_layout` (inner structure keeps its original biome tag; harmless, our tag is the one that matters).
- Own biome tags start as copies of the originals (identical behaviour); narrow later. Original `exclusion_zone: minecraft:villages` DROPPED (that set is empty);
  re-add against our own settlement set in 3c.
- validate.py now cross-checks dying_world sets (structure file, biome tag, spacing>separation). Install/cleanup/test: `docs/INSTALL.md` (brief, no commands - user preference).
- NEXT: user runs the test; then 3b-2. Unresolved: tarbound biome tags only cover plains/forest/taiga/swamp (user may want wider later).

## Pass 3b-2 result (2026-11-14)
- 3b-1 user test: all five `/locate structure dying_world:*` worked.
- Added to BATCH in `tools/gen_pass3b.py`: burnt_homestead/manor/watchtower (gearwrights; biomes = original gearwrights tags, spawn_overrides kept: zombie + zombie_villager)
  and abandoned_watchtower (watchtower_building; inline biomes plains/birch_forest/forest/flower_forest/taiga -> own tag). fresh_watchtower stays disabled.
- Test ids: dying_world:burnt_homestead, burnt_manor, burnt_watchtower, abandoned_watchtower. Install per `docs/INSTALL.md`.
- Reminder: burnt_* zombie_villager spawn_overrides are mob spawns, not villagers living there; fine for tone.

## Pass 3b-3 + 3b-4 result (2026-11-14)
- `tools/gen_pass3b2.py` (multi-variant aware): per member structure = copy w/ own biome tag (starts = original tag); per set = own salt/spacing.
  Now 20 structure_set files under `dying_world:` (2 progression placeholders + 18 curated sets incl. 3b-1/3b-2).
- createnewbeg files had `//` comments + a stray `values` key: stripped in our copies. Forsaken wells original frequency was 0.0025 (near-never); set to 0.6 with 40/14 (TUNE after test).
- Shipwrecks re-registered per user decision (roster had them DROP; user_decisions.md overrides). Vanilla shipwreck structures use original vanilla biome tags.
- NOT registered on purpose: forsaken homes (cabin spam; abandoned_cabin already covers lone homes), regular_cabin, fresh_watchtower, road signs (their destinations tag is `#minecraft:village`, nothing to point at until 3c).
- Dropped all `exclusion_zone` entries (they referenced the now-empty vanilla villages set).
- Test ids (new): abandoned_ruin_plains, abandoned_hamlet_taiga, abandoned_village_snowy, collapsed_minehead, ruined_chapel, abandoned_smithy, lighthouse, shipwreck, shipwreck_beached, wells/rustic/oak.

## Pass 3c-1 result (2026-11-14)
- Design: houses pool OVERRIDE `minecraft:village/plains/houses` (street NBTs hard-code that id; kubejs/data wins). 22 houses x2: lived (vanilla NBT, mossify_10_percent, weight x2)
  and worn (copy in `dying_world:village/plains/houses_worn/*`, processor `dying_world:village_worn`, weight x3) => 40/60.
- Worn NBT copies have the villagers jigsaw pool set to `minecraft:empty` (22 jigsaws changed; verified with nbtlib) => no villagers spawn in worn houses.
  Lived houses keep villagers, beds and job blocks. Processors can't do this (jigsaws expand before processors).
- `village_worn` = replace-only: 16 bed colors -> moss_carpet; composter/barrel/blast furnace/smoker/cartography/fletching/grindstone/lectern/loom/smithing/stonecutter/
  brewing stand/cauldrons -> mossy_cobblestone; cobblestone 40% -> mossy; stone_bricks 25% mossy + ~19% cracked. No air, no holes.
- Side effect: any other structure using vanilla pool `minecraft:village/plains/houses` also gets the 40/60 mix (vanilla villages are disabled, so normally only ours).
- Not changed: streets, decor, town centers, farms' crops, trees (vanilla). Structure copy keeps vanilla fields verbatim (size etc.).
- Only plains biomes spawn villages until 3c-2. Original village exclusion zones not re-added yet.
- Test: `/locate structure dying_world:village_plains` (plains/sunflower plains/meadow per vanilla tag); `/place structure dying_world:village_plains` in a flat test area;
  walk in: ~40% houses should have beds/workstations + a villager, others moss carpet + mossy cobblestone, no villagers.

## Pass 3c-2 result (2026-11-14)
- User: plains test looked good; keep current worn logic unchanged (extra replacements discussed - farms->dead bush, ground wear, tar-soaked planks, wool/hay/bookshelf swaps -
  are OPTIONAL IDEAS only, not applied; revisit later if wanted).
- Taiga added with the same mechanism: 23 house entries x2, 13 villager jigsaws removed in worn copies (verified none left), set `survivor_villages` now = plains + taiga (40/12).
- Test: `/locate structure dying_world:village_taiga` (vanilla taiga village biomes), walk in, expect the same 40/60 mix.

## Pass 3c-3 result (2026-11-14)
- Taiga tested OK. Desert added, same mechanism: 24 houses x2, 12 villager jigsaws removed in worn copies (verified none left in all 24). `survivor_villages` = plains + taiga + desert (40/12).
- NOTE: re-run the generator with ALL finished biomes (plains taiga desert ...) to be safe; the set file merges anyway.
- Desert caveat: desert houses are mostly sandstone, so `village_worn` (cobble/stone-brick/bed/job-block rules) changes less visibly than in plains/taiga: expect mostly moss carpet beds + mossy cobblestone workstations, little wall decay. Optional later: sandstone -> cracked/ash-stained variants (not applied; wait for user feedback).
- Test: `/locate structure dying_world:village_desert`, `/place structure dying_world:village_desert`, walk in.

## Pass 3c-3b result (2026-11-14) - desert redone with variants
- User asked for more desert house variants. Generator now has per-biome PROFILES (plains/taiga output verified byte-identical; only desert changed).
- Desert = 1 lived + 3 worn variants, all worn variants share the same villager-free NBT copies (only the processor differs). Weights 6:4:3:2 -> lived 40%, weathered 26.7%, scorched 20%, tarred 13.3%.
  - `dying_world:desert_lived`: 8% smooth/cut sandstone -> sandstone (replaces moss, which looked wrong in desert).
  - `desert_weathered` (sun-bleached): beds -> brown carpet, job blocks -> cobblestone, crops -> dead bush, 30% sandstone roughening, 40% bookshelf -> cobweb, 60% grass -> coarse dirt, 55% colored terracotta -> plain.
  - `desert_scorched` (fire): beds -> black carpet, job blocks -> blackstone, crops -> dead bush, smooth sandstone ~18% black / ~22% gray terracotta, 15% cut sandstone black, birch/jungle planks 50% -> dark oak, 60% hay -> coal block, 35% colored terracotta -> black, bookshelf 50% -> cobweb.
  - `desert_tarred` (tar/oil): beds -> black carpet, job blocks -> cobblestone, crops -> dead bush, birch/jungle planks 50% -> `tarbound:tar_soaked_planks`, 12% sand -> `immersivepetroleum:asphalt`, 15% sandstone roughening, bookshelf cobwebs.
- All replace-only (no air, no stairs/slabs/logs touched, so no lost block states). Tune percentages after testing; same variant pattern can be reused for snowy/savanna.
- Test: `/locate structure dying_world:village_desert`, `/place structure dying_world:village_desert`, walk several houses: expect clean-ish lived, bleached, black-scorched, and tar-planked ones, no villagers in worn ones.

## Pass 3c-4 result (2026-11-14) - lean village plan, all in one run
- User direction: NOT many village types; lived-in world. Keep 5 base types (plains taiga desert savanna snowy), widen their biomes, get variety from MIXED HOUSES (hodgepodge within a material family). No new village types. Wet biomes (swamp, jungle, beach, mangrove) get NO village this pass: user plans survivor RUST-AND-REBAR BUNKERS there (on gravel/coarse sand, reinforced wet soil, 'away from the blight') -> goes in pass 4.
- `tools/gen_pass3c4.py` regenerates everything village-related (safe to re-run). It replaces gen_pass3c1.py (keep for history; do not run both).
- Biomes (own tag = original vanilla tag + extras, disjoint): plains +forest, birch_forest, old_growth_birch_forest, flower_forest, cherry_grove; taiga +snowy_taiga, grove; desert +badlands, wooded_badlands, eroded_badlands; savanna +windswept_savanna; snowy +ice_spikes. (Modded biomes, e.g. Regions Unexplored, are NOT added yet.)
- Donor houses (accepted only if they have a minecraft:building_entrance jigsaw + all jigsaw pools exist; full list in `docs/pass3c4_mix_report.md`): plains <- kaisyn forest_ruins(30)/birch_romanian(18)/vsrevamped cherry(20); taiga <- snowy_taiga_viking(19)/old_growth_polish(19); desert <- badlands_pueblo(27)/wooded_badlands_tipi(12); snowy <- windswept frozen(26); savanna: none (ramshackled has no compatible houses). Each donor village gets an equal share; donors ~29% of the house pool. Donor processors are combined with ours (`dying_world:mix/*`) so street/path conversion keeps working. Frozen donors use windswept blocks (holly planks etc.).
- Worn houses: ALL jigsaws whose pool contains 'villager' are set to minecraft:empty (also in donor copies). Lived donors keep their villager jigsaws (pueblo/viking donors point at vanilla taiga villager pool: fine).
- Worn looks per family: plains/taiga `village_worn` (moss); desert/savanna/snowy each have lived + weathered/scorched/tarred lists (weights 6:4:3:2 = 40% lived / 60% worn). Tarred uses tarbound:tar_soaked_planks and immersivepetroleum:asphalt.
- Skipped on purpose: sunflower_plains_farm, meadow_swiss, japanese flower forest, grove outpost, snowy slopes inn, mushroom/ocean/piglin villages, all T&T 'exclusives' (culture clutter). savanna: vanilla pool entry `savanna_medium_house` has no nbt in vanilla; left out.
- Test: `/locate structure dying_world:village_savanna` and `village_snowy`; `/place structure` each of the five and walk: expect a mix of base + donor house styles, ~40% lived. Also check forest/birch/badlands/cherry grove now find a village: `/locate structure dying_world:village_plains` from a forest.

## Pass 3c-4b result (2026-11-14) - village biome tags incl. modded biomes
- User: add tags to all village pools efficiently. Done tag-driven: `tools/biome_tags.py` resolves biome tags from reference/ (all namespaces merged), `tools/village_biomes.py` assigns each surface biome to AT MOST ONE family (first match: taiga, snowy, desert, savanna, plains), so families are disjoint (86 biomes). Re-run `gen_pass3c4.py` after modlist changes (refresh reference/ first).
- Tags are now EXPLICIT lists of optional entries (`{"id":..., "required": false}`): a removed mod / missing biome cannot break the tag. `dying_world:has_structure/village_<B>` no longer references the vanilla village tags.
- Same lists also added to gearwrights `abandoned_{ruin,hamlet,village}_<B>` tags (original tag kept; cherry_grove excluded for plains so the cherry variant keeps it). Swamp/cherry abandoned variants untouched. If gen_pass3b2.py is ever re-run, run gen_pass3c4.py after it.
- Included modded biomes (RU, Atmospheric, Environmental, Windswept, Autumnity): e.g. plains <- RU forests/grasslands/orchard/magnolia/etc, atmospheric laurel forest/grimwoods, environmental blossom woods; taiga <- boreal/pine/redwoods + pine barrens; snowy <- tundra/frozen tundra/spires/cold forests; desert <- dunes/scrubland/joshua/saguaro/outback; savanna <- baobab/dry bushland/steppe/flowering savanna.
- Excluded on purpose: wet (swamp, jungle/rainforest, beach, river, ocean, mushroom) = future bunkers; caves, nether/end, mountains/peaks/hills (except meadow, cherry grove, grove), dark forest, bamboo forest, ashen woodland (wasteland). Full lists + unassigned leftovers: `docs/pass3c4_mix_report.md`.
- Note: reference/ contains biome ids newer than MC 1.21.1 (minecraft:pale_garden, dappled_forest, sulfur_caves). Harmless here because tag entries are optional; if the pack really is a newer MC than 1.21.1, tell me so pack_format/other assumptions can be rechecked.
- Test: `/locate structure dying_world:village_plains` from RU forest / grassland; `village_desert` in an Atmospheric dune; `village_snowy` in frozen tundra; check no villages in swamp/jungle/beach.

## Pass 3c-5 result (2026-11-14)
- 3c-4 / 3c-4b tested by user: looked good.
- `tools/gen_pass3c5.py` (safe to re-run; run AFTER gen_pass3b/3b2/3c4 since it edits their set files):
  - exclusion_zone re-added against `dying_world:survivor_villages` with the ORIGINAL chunk counts: abandoned_cabin 4, abandoned_hamlets 6, abandoned_ruins 3, abandoned_villages 8, burnt_homestead/manor/watchtower 6, collapsed_minehead 6, ruined_chapel 6, wells 3. (Not applied to sets whose originals had none, e.g. tarbound, lighthouse, smithy, shipwrecks.)
  - Road signs: `dying_world:road_sign` structure (copy of supplementaries:road_sign, min_y 40/max_y 105), set `dying_world:road_signs` 32/10 with exclusion 6 chunks from survivor villages (original was 19/10 vs villages 10), biome tag = all 136 non-ocean/river/cave/nether/end biomes (optional entries; the mod's own config flag condition is bypassed).
  - `supplementaries:road_sign_destinations` structure tag OVERRIDDEN (replace:true) -> only the 5 survivor village structures (originally #minecraft:village + a long list of other mods' structures). Optional later: add abandoned_village_* as destinations.
- Test: `/locate structure dying_world:road_sign`; find a sign in the world and check it points to a village and its text is sensible (destination names may show raw ids like `dying_world:village_plains` - report what the sign says); confirm an abandoned hamlet/ruin is not generated right next to a survivor village.

## Pass 4 candidates (from user_decisions.md; pick ONE per step, easiest first)
1. (DONE in 4-1, untested) Concrete pads + broken lean-tos (portal replacement): chest with obsidian/bricks/etc + mid-tier loot.
2. Survivor bunkers in WET biomes (swamp/jungle/beach etc.): Rust and Rebar, on gravel/coarse sand + reinforced wet soil; 'away from the blight' (user idea, 2026-11-14).
3. Industrial tunnels (mineshaft replacement, Rust and Rebar heavy).
4. Scavenger outposts (pillager outpost replacement; per-biome-group guards, rare pillager variant).
Needs new .nbt (script-built) or reuse + processors; check docs/user_decisions.md + `reference/blocks_index.md` (rustandrebar 130 blocks) first.

## Pass 4-1 result (2026-11-14) - concrete pads + broken lean-tos
- `tools/gen_pass4_1.py` (safe to re-run; has its own tiny NBT writer, no deps beyond biome_tags/village_biomes). Replaces ruined portals.
- 14 script-built NBTs `structure/concrete_pad/<wood>_<n>.nbt` (9x5x9): y0 = cracked concrete pad flush with ground (gray/light gray concrete, stone, andesite, cobble/mossy, ragged edges);
  lean-to on one side (back wall with gaps, corner posts, snapped front posts, sloping plank/slab roof ~27% missing, cobwebs), chest (loot `dying_world:chests/concrete_pad`),
  barrel (80%, `concrete_pad_scraps`), unlit campfire, fallen post, rubble. Layout rng is seeded per wood+variant; jigsaw rotates them randomly.
- Wood by biome group (disjoint tags, optional entries): temperate=village 'plains' family (oak x3 + birch x2), cold=taiga+snowy (spruce x3), arid=desert+savanna (acacia x3),
  wild=ALL other land biomes incl. swamp/jungle/mountains/dark forest (dark_oak x3; TUNE later, e.g. jungle/mangrove wood). Counts: 37/28/21/50 biomes.
- Registered: `dying_world:concrete_pad_{temperate,cold,arid,wild}` (minecraft:jigsaw, 1 piece, beard_thin, WORLD_SURFACE_WG), set `dying_world:concrete_pads` 44/16, 3 chunks from survivor villages.
- Loot: `loot_table/chests/concrete_pad.json` = building pool (obsidian 3-8 w4, bricks, stone bricks, deepslate bricks, glass, iron bars, terracotta, smooth stone, rare crying obsidian/iron block) +
  mid pool (iron/gold/copper ingots, coal, redstone, lapis, gunpowder, worn iron tools via set_damage, rare golden apple/diamond) + food/torches. Vanilla ids only on purpose (no enchant functions yet).
  Optional later: add Rust and Rebar / other modded items (verify ids in `reference/blocks_index.md` first).
- Assumption to verify in game: NBT y0 layer lands flush with the ground (vanilla groundLevelDelta). If the pad floats 1 block high or sinks, shift the pad to y0/lean-to y+1 or add a foundation layer.
- Test: `/locate structure dying_world:concrete_pad_temperate` (also _cold/_arid/_wild; 44 chunks spacing so may need travel), `/place structure dying_world:concrete_pad_temperate` on flat ground:
  expect a cracked concrete pad flush with ground, lean-to on one side, chest with obsidian/bricks/etc, no holes in terrain. Check log for `dying_world` / `concrete_pad` errors (bad loot item ids, nbt).

## Pass 4-1b correction (2026-11-14)
- USER CORRECTION: 'concrete' in 'concrete pad' meant Rust and Rebar concrete with visible rebar + other cool R&R blocks (vanilla concrete is flat/boring). My 4-1 wrongly used vanilla concrete
  ('R&R reserved for industrial zones' was a misreading). RULE: pads and other 'concrete'/industrial bits use R&R blocks; villages/shacks stay mostly vanilla.
- Fixed in `tools/gen_pass4_1.py` (re-run; same file names, so it overwrites the 14 NBTs): pad floor = `rustandrebar:rebar_concrete` ~42% + `weathered_concrete` ~46% + `tread_plate`/`hazard_plating` patches;
  ragged edges (weathered/rebar concrete, coarse dirt, mossy cobble, andesite) with `rebar_bundle` sticking out; lean-to back wall/roof = `corrugated_rusted_metal` (+slabs) and `riveted_rusted_plating`, biome-wood posts/planks kept (wood stays biome-matched);
  `burning_barrel` camp, salvage (`weathered_concrete_slab`, `rebar_bundle`, crates, pallet, `rusted_drum`, `tar_leaking_drum`, `gas_cylinders`). Chest/barrel/vanilla loot kept; chest loot now also has R&R building mats
  (rebar_concrete, weathered_concrete, firebrick, sooty_brick, rusted_plating, rebar_bundle, hazard_plating, salvaged_steel_block). All 20 R&R ids verified against `reference/blocks_index.json`.
- Block states of R&R blocks are default (only slab `type` set); orientation-dependent R&R blocks (stairs, railings, doors) deliberately avoided. Unverified in game: how `burning_barrel` / `tar_leaking_drum` behave when placed by worldgen (fire/drips?). Report if odd.
- Same install/test as 4-1 (copy `data/` into kubejs/data; `/place structure dying_world:concrete_pad_temperate`). Wasteland Vision may restyle these blocks client-side.

## Pass 4-2a (2026-11-14) - industrial mineshaft core kit
- USER ANSWERS: R&R crates are PURELY DECORATIVE (loot goes in barrels); Create TRACKS (not rails) in tunnels, so profile is big; mineshafts must be SPRAWLING but spawn efficiently (no cascading chunk generation); R&R jar provided (`rustandrebar-3_6_2_2-beta.jar`).
- New reference (small): `reference/rustandrebar_blockstate_props.json` (every R&R block -> its blockstate properties/values from the jar) and `reference/create_family_blockstate_props.json`
  (create/createdeco/aeronautics/simulated/createpropulsion track/catwalk/girder/scaffold/ladder/pipe/etc). USE THESE before placing any block with states.
  Facts: R&R `rusted_*` blocks have `paint` (16 colors) + `coat` (fresh/weathered); ladders `caged_rusted_ladder`/`rusted_rung_ladder` have facing+waterlogged; `rusted_catwalk`/`rusted_grate` paint+coat;
  `rusted_railing`/`guardrail` facing+paint+coat; container walls (red/blue/green/bare `_container_wall`) have NO props; container doors (`*_container_doors`) have facing + bottom/top flags (multipart: not yet understood, check models before using);
  `rusted_tank` is multi-block (kind ground/tower/large_tower + x,y,z); `create:track` shape: xo/zo straight, an/as/ae/aw slopes, tn/ts/te/tw, cr_*, turn, waterlogged.
- `tools/nbtw.py` = shared tiny structure-NBT writer (Tpl). `tools/gen_pass4_1.py` still has its own copy (fine).
- Design (jigsaw, procedural like vanilla): `dying_world:industrial_mineshaft` start pool `dying_world:mineshaft/start` (hub 13x13). Tunnel shell 9x8, interior 7 wide x 6 high (Create train clearance).
  Connectors name/target `dying_world:tunnel`, jigsaw cell at local y=3 at face centre; room doors `dying_world:room_door` at y=2. ALL jigsaw final_state = air. `tunnels` pool fallback = `caps` (dead ends).
  Pieces (2 variants each, NBT in `structure/mineshaft/`): straight_track (create:track zo on centre lane), straight_plain, straight_door (13 wide, side alcoves 3x4x2 -> rooms), corner, tee, hub, cap (dead-end stash with barrels/crates);
  rooms: storage_closet_1..3 (11x6x9: barrels w/ loot `dying_world:chests/mineshaft_storage`, R&R crates decor). `rooms` pool has empty element weight 3 (about half of alcoves get a room).
  Materials: rebar_concrete/weathered_concrete/sooty_brick/rusted_plating walls, hazard_plating + tread_plate floor accents, `rusted_girder` posts + `rusted_beam` ceiling ribs, `caged_lamp` (lit=false) + 12% flickering `fluorescent_batten`.
  Tracks only on straight_track and one straight_door variant; corners/tees/hubs have plain floor (Create tracks can't curve in static NBT) -> tracks 'end' at junctions = ripped-up rails.
- EFFICIENCY choices (answering 'no cascading chunk generation'): structure `size` 10; `max_distance_from_center` 112 (<8 chunks so starts are found within vanilla's reference radius); NO heightmap projection (fixed start Y uniform -48..16);
  `terrain_adaptation none`; step `underground_structures`; closed shells (no holes into caves/water; interior explicit air carves rock); rare random_spread spacing 30 / separation 10 / frequency 0.6; pieces are big so piece count stays low.
  Biome tag = 136 land biomes + lush/dripstone caves (start Y is underground, 3D biome decides). Tune spacing/frequency after test.
- Unverified in game: orientation of `caged_lamp`/`fluorescent_batten` (facing=down used), flickering battens staying lit, create:track rotation + whether train graph registers, jigsaw door alcove/room alignment, whether pieces ever overlap awkwardly, performance feel while flying/exploring.
- Test: `/locate structure dying_world:industrial_mineshaft` (rare; may need travel; creative flight helps). Or `/place structure dying_world:industrial_mineshaft ~ ~ ~` (start Y comes from the structure's -48..16 range, so tp underground/dig down to look).
  Check: tunnel network branches, caps at ends, rooms off alcoves with barrels, tracks, no flooding, and report chunk-gen hitching + log lines mentioning `dying_world` / `mineshaft` / `jigsaw` / `rustandrebar`.
- Next sub-passes: 4-2b more storage rooms (loot tuning), 4-2c container yard hall (3x3x9 containers; need container door model check), 4-2d multi-floor catwalk halls (rusted_catwalk/rung ladders + createdeco catwalks), 4-2e flooded/tar/deep variants + stairs + spawner room.

## Pass 4-2b (2026-11-14) - more mineshaft rooms + loot tuning
- Project zip resumed from `dying_world_project_4-2a-industrial-mineshaft-kit.zip`; R&R jar re-uploaded but NOT needed for 4-2b (props already in `reference/rustandrebar_blockstate_props.json`). Needed again for 4-2c container door models.
- `tools/gen_pass4_2b.py` (imports helpers from gen_pass4_2a.py; keep both). Rooms keep the 11x6x9 closet footprint + door jigsaw at (5,2,0) so alcoves need no change.
  New pieces (structure/mineshaft/): workshop_1/2 (anvil, grindstone, blast furnace, crafting table, loot barrels), office_1/2 (bookshelves, lectern, gray bunk bed, cobwebs, loot barrels),
  fuel_store_1/2 (R&R gas cylinders, tar-leaking drums, unlit burning barrel, oil puddles, high-voltage sign, loot barrels), stash_cell_1 (rare; rebar-heavy; chest + barrels).
- `rooms.json` now: 3 closets + 2 workshop + 2 office + 2 fuel + 1 stash, each weight 1, empty weight 10 (about half of alcoves stay empty, same as before).
- New loot tables (`loot_table/chests/`): mineshaft_workshop (ingots/chain/worn tools+iron armor), mineshaft_office (paper/books/maps/compass/clock), mineshaft_fuel (coal/charcoal/gunpowder/fire charges, rare lava bucket),
  mineshaft_stash (best: diamonds, emerald, gold, ender pearls, enchanted book, rare golden apple). `mineshaft_storage` unchanged.
- Unverified in game: bed head/foot orientation, anvil/grindstone/lectern facing against the back wall, R&R sign_* facing on a wall-adjacent block, gas_cylinders/tar_leaking_drum facing, whether `oil_puddle` places cleanly on the floor.
- Test: same as 4-2a (`/locate structure dying_world:industrial_mineshaft`, `/place structure ...`); look into door alcoves for the new rooms; report odd orientations + log lines mentioning dying_world/mineshaft.

## Pass 4-2b-lights (2026-11-14)
- User feedback: after installing, mineshafts generated (3 screenshots: track tunnel, girders, sooty-brick ceiling patches, lit fluorescent battens). Caged lamps were all OFF (we placed lit=false) and the user said the lights can support the other
  two types "with the right states".
- Verified in the R&R jar (blockstates): `caged_lamp` has facing + lit (separate on/off models), `hanging_bulb` has lit only, `fluorescent_batten` has axis/facing/lit/flickering/dark (dark=true uses the off model).
- `lamp()` in `tools/gen_pass4_2a.py` (shared by 4-2b rooms) now: 12% flickering batten (lit), 23% hanging_bulb lit=true, rest caged_lamp facing down with ~60% lit (40% stay dead for atmosphere).
  Still ONE `r.random()` call so layouts are unchanged. Re-run order: gen_pass4_2a.py then gen_pass4_2b.py (2b overwrites rooms.json). Counts in all pieces: 17 caged lit, 5 caged off, 7 bulbs, 4 battens.
- Tune: change the `.12 / .35 / .6` constants in lamp(). Unknown: whether R&R lamps reset `lit` on first tick (e.g. need redstone) - report if lamps look off in-game.

## Pass 4-2c (2026-11-14) - container yard halls
- Container facts read from the R&R jar (blockstates + models): `*_container_wall` (red/blue/green/bare) = full block, NO props, each of 6 faces randomly plain/patch/hole skin;
  `*_container_doors` = full block with the door panel + protruding lock bars on the `facing` side, flags `bottom`/`top` add latch hardware (use bottom on the lowest block row, top on the highest). R&R ships NO container structures.
- `tools/gen_pass4_2c.py`: `yard_hall_1/2` (31x12x31, interior 29x10x29), 4 tunnel connectors (7x6 openings, jigsaw y=3, same as hub), 2 cross aisles (7 wide), 4 quadrants 11x11.
  Containers are 4x4x10 (hollow 2x2x8, walkable), door end faces the wall, rear end of the bottom container is open (2x2) toward an aisle, top layer sealed, 1-3 loot barrels near the door end
  (tables: storage 45 / workshop 20 / fuel 15 / office 10 / stash 10 weights), 35% a lit hanging bulb inside. Hall 1 has a Create track down the middle of the N-S aisle; hall 2 none. Girders at aisle corners, ceiling beams, lamps via lamp().
  Both halls added to `tunnels.json` pool (weight 1 each; pool now 14 entries). Hall 1: 8 containers/9 barrels, hall 2: 12 containers/11 barrels (seeds fixed).
- Unverified in game: door `facing` direction after jigsaw rotation, whether the bottom/top latch flags look right on the 4-high door face, hole-skin faces (cutout) letting light/rock show, hall overlap/spacing in the network, aisle clearance for trains, chunk-gen cost of big halls.
- Tune: hall weight (tunnels.json), container count/stack probabilities in hall(), loot weights in LOOT.

## Pass 4-2c-girders (2026-11-14) - no more floating girders/beams
- User feedback: generated girders/beams 'float'; R&R girders/beams can connect, 'you just need the right states'; sub girders should connect into the main I-beam.
- Cause: jigsaw/template placement does not recompute neighbour-dependent blockstates (flags without UPDATE_NEIGHBORS), so connection states must be IN the NBT.
- Jar facts (blockstates + models): `rusted_girder` axis x/y/z, turned, neg/pos in {girder, column, flange} (x/z axes only); `rusted_beam` axis, low, neg/pos in {girder, column, beam_high, beam_low} (x/z only);
  paint/coat exist (16 colors, fresh/weathered; we leave defaults). Connected ends draw extensions into the neighbour cell (column/girder ~7/16, flange = thin plate, beam_low/high = taper).
  `reference/rustandrebar_blockstate_props.json` does NOT list these multipart blocks correctly (shows None) - read the jar blockstates instead.
- New `tools/rr_connect.py` (`connect(t)`, applied to every piece before saving in gen_pass4_2a/2b/2c). Rules: beam/girder end meeting a vertical girder -> `column`; sub girder (or perpendicular girder) butting into a main beam -> `flange`;
  beam end into a girder -> `girder`; beam to beam only if `low` differs. Continuous same-kind runs get no state (to avoid overlapping end plates). Counts now: beam ends 33+33 column, girder ends 27+27 flange.
- Geometry changes so everything touches: tunnel ribs = full-height posts (y1..6) with the main beam running BETWEEN the posts (x=2..w-3, ends connect as column) + sub girders along the ceiling centre between consecutive ribs (butt into the beams, flange).
  Yard halls = 4 full-height columns (floor to ceiling) at the aisle crossings, main beams split by the columns, sub girders wall->main beam in all 4 quadrants (both directions) + a cross girder over the aisle centre; centre lamp moved to y=9 under it.
- Unverified in game: whether my reading of the state names matches the mod's own logic (flange vs girder vs column), any z-fighting where extensions overlap, and whether a connected end looks right on beams. If it looks wrong, tweak the three rule lines in rr_connect.py.

## Pass 4-1c (2026-11-14) - ruined-portal loot in the concrete pad chest
- User: lean-to/pad chest should hold appropriate NETHER PORTAL chest loot (pads replace ruined portals); also asked for netherrack + magma blocks. Pads themselves tested OK; user was NOT concerned about lamp state.
- `tools/gen_pass4_1.py` loot(): `concrete_pad.json` gets a new 2nd pool (rolls 3-5) = vanilla `chests/ruined_portal` entries copied VERBATIM from reference (obsidian, flint, iron nugget, flint and steel, fire charge, golden apple, gold nuggets, golden tools/armor with `enchant_randomly #minecraft:on_random_loot`, glistering melon, golden horse armor, light weighted plate, golden carrot, clock, gold ingot, rare bell / enchanted golden apple / gold block) + `netherrack` (w30, 6-16) + `magma_block` (w18, 2-6).
  Existing building pool (2-3 rolls), mid pool and food pool unchanged, so the chest is now richer than vanilla ruined portals (tune: reduce portal rolls or the mid pool if too generous).
- `concrete_pad_scraps.json` (barrel) gets a small extra pool (0-1 rolls): flint, fire charge, netherrack, magma block, gold nuggets.
- Only these two loot files changed (NBTs byte-identical). Re-run `python3 tools/gen_pass4_1.py` if needed.

## USER DECISIONS for 4-2d (2026-11-14)
- Use Rust and Rebar catwalks (`rusted_catwalk`, `rusted_grate`) + `caged_rusted_ladder` (jar blockstates: ladders facing+waterlogged; catwalk paint+coat). Create Deco catwalks NOT wanted for now.
- Waiting for the user's test feedback on 4-2c yard halls and 4-2c-girders before starting 4-2d (fix connection rules in `tools/rr_connect.py` first if the user reports problems).

## Pass 4-2c2 (2026-11-14) - solid containers + no floating branches
- USER FEEDBACK (2 screenshots + 2nd log): yard-hall containers were hollow with an open rear (screenshot 1); user wanted them SOLID, purely decorative, nothing inside, like screenshot 2 (R&R Rust-Red Container Wall with the door-end hardware visible).
  `tools/gen_pass4_2c.py` container(): all blocks R&R container wall, one end face = `*_container_doors` (facing outward, bottom/top latch flags); door end faces the aisle 70% / the wall 30%; stacks of 1-2 kept.
  Loot barrels are no longer inside containers: `end_barrels()` puts 0-2 on the aisle side next to container ends (hall 1: 9 containers/5 barrels, hall 2: 10/6; seeds shifted).
- NO FLOATING: vanilla jigsaw cannot skip a branch based on the world (pool selection never looks at terrain). Instead every branch piece (tunnels, caps, rooms, halls) uses processor `dying_world:mineshaft_no_float`
  = `minecraft:protected_blocks` with block tag `#dying_world:mineshaft_open` (air, cave_air, void_air; file `tags/block/mineshaft_open.json`): the piece never overwrites air that is already in the world, so inside a cavern the part over open air is NOT built
  (collapsed gap, tunnel opens into the cavern) and only parts embedded in rock remain. Water/lava are not protected (shell stays sealed). Shaft pieces are not protected (they cross caverns as a tube).
  Alternative if gaps look bad: structure `terrain_adaptation: encapsulate` (1.21) fills terrain around pieces instead (costlier). Tune the tag to add/remove protected blocks.
- Second log (user): the long blank-sky stall ended by itself after generating; no `dying_world` errors anywhere. Repeating `Block-attached entity at invalid position` errors (x~270-365, y -60..-51, z~20-50, worker threads) are NOT ours (our mineshaft/pad NBTs contain no entities; mineshaft was at -256,-464); probably another mod's structure (neovitae dungeon?). Slowness = heavy new-chunk generation in this pack (205 s startup).

## Pass 4-2s (2026-11-14) - central shaft
- USER ASK: central shaft from surface to bedrock that branches off to the halls and rooms.
- `tools/gen_pass4_2s.py` (run after 2a, 2b, 2c; overrides start pool, structure json, set). Pieces `structure/mineshaft/shaft_*.nbt`:
  head_1/2 (23x15x17: concrete platform with 9x9 shaft opening, curb ring, 4-leg girder headframe with beams/cross girder + pulley, control shed with 2 loot barrels (workshop/office), crates, windows, clutter),
  collar (15x10x15 solid block under the head so it sits in the ground), 7 segment variants (11x16x11, interior 9x9, caged ladder on the NORTH wall, corner girders, wall lamps; branch variants have 1-3 openings E/S/W with a rusted_grate landing + tunnel connector),
  caps 16/8/4 (sump floor, 2-3 loot barrels/crates, oil puddles; fallback of the `shaft` pool).
  Pools: `start` (heads), `shaft_collar`, `shaft` (segments weights plain 3+3, S 2, E 1, W 1, EW 2, ESW 1; fallback `shaft_caps`).
- Vertical connection = jigsaw `dying_world:shaft`, orientation up_north/down_north, joint aligned (keeps one rotation for the whole shaft => continuous ladder). Branch landings: tunnel floor level = segment y 5 (connector jigsaw at y 8).
- Structure: start_height 0 + project_start_to_heightmap WORLD_SURFACE_WG (head at the surface), step surface_structures, size 14, max_distance_from_center 128, terrain_adaptation none. Set 32/10 frequency .5, exclusion 4 chunks from survivor villages. Old random hub start removed (hubs stay in the `tunnels` pool).
- LIMIT: vanilla jigsaw box is +-max_distance (128) around the start piece in every axis => shaft reaches surface-128 (bedrock only where the surface is <= ~64; elsewhere it ends in natural rock above bedrock).
- Unverified in game: head sits correctly on slopes/hills (collar fills below), jigsaw vertical alignment + ladder continuity, grate landings meeting tunnels, tunnels attaching to shaft openings (J=Y0+3=8), how big the network gets (size 14 / radius 128: check chunk-gen time), caps/fallback at the bottom, whether the `dimension` allows pieces below -64 (they would be clipped).
- Test: `/locate structure dying_world:industrial_mineshaft`, tp to the surface there (head building), or `/place structure dying_world:industrial_mineshaft ~ ~ ~` on flat ground; climb down the ladder, look for side openings with grate landings; report odd alignment + log lines mentioning dying_world/mineshaft/jigsaw/protected_blocks.

## Pass 4-2s2 (2026-11-14) - workable shaft ladder + landings
- USER FEEDBACK: caged ladder had no good exit. Now `rusted_rung_ladder` (facing south = rungs on the north wall; jar model checked; in #minecraft:climbable) in segments, caps, collar, head.
- Branch segments (any opening): y=Y0 is a full `rusted_grate` floor over the 9x9 interior, only the ladder cell (5,Y0,1) open; two `rusted_beam` (axis x) supports under it at z=3/7. Old partial grate strips/beams removed. Plain segments unchanged (open drop).
- Suggestions offered to the user (NOT applied, waiting for picks): water sump in the bottom cap, rest landings on plain segments, railings at landing edges/openings, depth signs, top exit tidy-up, optional second ladder.

## Pass 4-2c3 (2026-11-14) - container spec fix + undead spawns
- USER FEEDBACK: girders/beams look good now; shaft worked well and 4-2s2 ladder/landing changes were great; containers were too big (4x4x10) and some were 'eaten' by caverns (no-float processor skipped blocks over cave air).
  User dropped 4-2d catwalk halls (shaft already links levels); priority = best bang for buck: 4-2e variants next.
- `tools/gen_pass4_2c.py`: container = 3 wide x 3 high, BOTH ends = 3x3 `*_container_doors` (facing outward, bottom/top flags), 4-7 wall columns between (length 6-9), one colour, stacked 1-2 (45%).
  Rows of up to 3 per quadrant (4 apart). Containers + loot barrels are in `yard_hall_N_boxes.nbt`; pool entry is a `minecraft:list_pool_element` [hall shell w/ mineshaft_no_float, boxes w/ minecraft:empty]
  (jigsaws come from the first element). Over a cavern the shell may still have gaps but containers are always whole (may sit over a gap).
- `tools/gen_pass4_2s.py` SPAWNS -> structure `spawn_overrides.monster` (bounding_box piece): zombie 100 (2-4), skeleton 80 (1-3), zombie_villager 25 (1-2), drowned 15 (water only).
  No creepers/spiders/endermen inside pieces. Husk/stray left out (need sky). Lighthouse Horrors divers could be added later if their spawn rules allow natural spawning (ids not checked).
- Re-run order for the mineshaft: gen_pass4_2a -> 4_2b -> 4_2c -> 4_2s (done for this build).
- Test: `/place structure dying_world:industrial_mineshaft`, find a yard hall: containers 3x3 with door faces both ends, no missing chunks; at night/in dark tunnels only zombies/skeletons/zombie villagers should spawn.

## Pass 4-2e (2026-11-14) - flooded + tar tunnel variants
- `tools/gen_pass4_2e.py`. MINESHAFT RE-RUN ORDER NOW: gen_pass4_2a -> 4_2b -> 4_2c -> 4_2e -> 4_2s.
- 4 new straight tunnels (9x15, N/S connectors, built from box_piece then LIFTED 3 layers: floor y3, jigsaws y6, jigsaw alignment keeps floors level). Pit z3..11 x2..6 below the floor, 1-block ledges along both walls (rib posts on ledges), fluid surface flush with the floor => sealed, cannot spill into neighbours.
  - flooded_1/2: water 4 deep (gravel/concrete pit floor, 3 sunken crates), walls ~15% mossy cobblestone, no track. Drowned spawn here via the 4-2c3 spawn_overrides.
  - tarred_1/2: `tarbound:tar` (fluid, level 0) 3 deep; walls ~35% `tarbound:tar_soaked_planks`; one ledge side ~40% broken (tar instead of ledge), other side intact; oil puddles/tar-leaking drums on ledges.
- Added to `tunnels` pool weight 1 each (pool 18 entries, variants ~4/22 of the weight). Processor mineshaft_no_float (in a cavern a pit wall over open air could be skipped -> small spill risk; report if seen).
- Unverified: whether worldgen-placed tar/water source blocks stay static (they should, sealed), tar's effect on players/mobs (Tarbound's own behaviour), drowned actually spawning (needs darkness + depth).
- Test: `/place structure dying_world:industrial_mineshaft` a few times / explore; look for water- and tar-filled tunnel stretches with ledges.

## Pass 4-3a (2026-11-14) - scavenger outposts
- USER: mineshafts done for now (4-2e accepted without test notes); survivor bunkers DROPPED; next = scavenger outposts.
- `tools/gen_pass4_3a.py` (safe to re-run). 3 camps `structure/scavenger_outpost/camp_{1,2,3}.nbt` (17x14x17, y0 partial ground patch like the pads, rest natural ground; air cleared y1..3 inside the ring):
  scrap perimeter at 1/15 (runs of corrugated rusted metal / one-colour container wall / chain_link_fence with connection states / gaps), barbed_wire tops, south entrance x6..10;
  watchtower x9..13 z2..6 (4 girder legs y1..12, corrugated north panel + rusted_rung_ladder (facing south) to a y9 grate/tread platform, y10 parapet w/ gaps, loot chest, 2 sodium floodlights (1 lit), patchy slab roof y13);
  2 west lean-tos (corrugated back wall x2, slab roof y4, girder posts) with loot barrels; lit burning_barrel + pallets; ~10 scrap piles; danger/no-entry signs at the entrance.
- Mostly R&R (industrial-site rule) => ONE camp pool for all biomes. Structures (same pool): `scavenger_outpost_{temperate,cold,arid,wild}` (biomes = concrete_pad group tags) weight 4 with undead spawn_overrides
  (temperate/wild zombie+skeleton+zombie_villager, cold stray+zombie+skeleton, arid husk+skeleton; bounding_box full), `scavenger_outpost_abandoned` (any land, no overrides) weight 6,
  `scavenger_outpost_raiders` (any land, pillager override like vanilla outposts) weight 1 => ~36% guarded / 55% abandoned / 9% raiders. New tag `has_structure/scavenger_outpost_any` = the 4 group tags.
  Set `dying_world:scavenger_outposts` 40/14, exclusion 6 chunks from survivor villages.
- Loot: `chests/scavenger_outpost` (tower chest: worn crossbow/bow/weapons/chainmail + arrows; iron/gold/gunpowder/tnt/emerald, rare pearl/golden apple/diamond; R&R building mats; food), `chests/scavenger_scraps` (barrels).
- Note: undead guards only spawn in the dark (night) on the surface, like any monster; pillagers spawn in daylight. Husks/strays need sky (fine on the surface).
- Unverified: ladder/floodlight/gas-cylinder/sign orientations after rotation, chain-link look, y0 flush with ground on slopes (beard_thin), barbed_wire behaviour.
- Test: `/locate structure dying_world:scavenger_outpost_temperate` (also _cold/_arid/_wild/_abandoned/_raiders), `/place structure dying_world:scavenger_outpost_raiders` (pillagers should start spawning); climb the tower, check chest + barrels.

## Pass 4-3a-lights (2026-11-14)
- USER FEEDBACK (2 screenshots): sodium floodlights floated inside the tower platform (mounted on nothing). Abandoned outposts otherwise look good.
- Jar facts: `sodium_floodlight` = facing (6 dirs) + lit only. Model (facing=north): mount plate at z=15-16 (SOUTH side), lens points NORTH tilted down 22.5 deg => `facing` = where it points; it attaches to the block on the OPPOSITE side.
  up = floor mount (points up), down = ceiling mount. Use: outside walls facing away from the wall, or on floors with facing=up.
- `tools/gen_pass4_3a.py`: 3 floodlights now hang off the OUTSIDE of the y9 platform edge, each mounted on a tread_plate edge block: east (lit), south over the yard (lit), west (off). Re-run done.

## Pass 5-1 (2026-11-14) - scavenger stronghold (bastion replacement), base
- USER DECISIONS: stronghold = ABANDONED VILLAGE with scavenger material built on top; R&R as accents only (NOT the main build). Guards = PIGLINS immune to zombification,
  gear leather/chainmail/iron/gold; NO KubeJS (=> placed entities, no respawn). Chests = bastion-level loot; at least 1 smithing template must ALWAYS spawn.
- `tools/gen_pass5_1.py` (run after gen_pass3c4.py). `tools/nbtw.py` gained entity support (`Tpl.entity(x,y,z,typed_nbt)`, tags B/F/D); older outputs byte-identical.
- Start = KEEP (`structure/scavenger_stronghold/keep_{1,2}.nbt`, 17x16x17): ruined cobble/stone-brick ground floor + oak log/plank upper floor, breaches patched with corrugated metal, oak/corrugated slab roof w/ barbed wire + stone-brick wall rim,
  3-wide doorways on 4 sides, ladder to the roof, 4 floodlights mounted on the outside walls (mount block forced solid), treasure corner behind a scrap barricade with gold blocks.
  Chests: treasure (`chests/scavenger_stronghold_treasure` = vanilla bastion_treasure VERBATIM -> has a rolls-1 pool with netherite_upgrade_smithing_template => GUARANTEED, keep is the start piece so always present; generator asserts it),
  upper floor chest `_other`; barrels `_other`/`_bridge`/`_stable`. other/bridge/stable = vanilla bastion tables + an extra overworld building-material pool (stone bricks, bricks, deepslate bricks, planks, logs, glass, bars, lanterns, chain, some R&R). They also roll netherite upgrade/snout templates at vanilla odds.
  Courtyard fence (oak fence/cobble wall/chain-link/corrugated, barbed wire) with street mouths open. 4 street jigsaws (minecraft:street, y1 edge centres).
- Streets = vanilla PLAINS ZOMBIE streets copied to `structure/scavenger_stronghold/streets/` with jigsaw pools byte-retargeted (103 jigsaws): our streets/houses/decor; cats/iron golem/villagers -> minecraft:empty. Street processors kept (street_plains).
  Pool fallback = `barricades` (3 NBTs: planks/cobble/corrugated/logs/crates/drums 2-3 high across the dead end, barbed wire, 35% with a gap; jigsaw minecraft:street east_up, terrain_matching).
  Houses pool = the 22 worn plains houses from our village override (villagers already stripped). Decor = vanilla zombie decor + camp (lit burning barrel, 70% a piglin) / scrap pile / floodlight post / loot cache (50% a piglin).
- Piglins: `IsImmuneToZombification` 1b, `PersistenceRequired` 1b, armour slots 60% (brutes 85%) random leather/chainmail/iron/gold, golden sword/crossbow (brutes golden axe). Keep: 2 brutes in the treasure corner + 6 piglins (house, upper floor, courtyard, roof).
  Vanilla finalizeSpawn(STRUCTURE) may still put gold armour in a slot (10%/slot) and brutes always get a golden axe. Piglins attack players without gold armour and barter gold ingots (vanilla behaviour).
- Structure `dying_world:scavenger_stronghold` (jigsaw size 6, radius 80, beard_thin, any land biome via `has_structure/scavenger_outpost_any`, no spawn_overrides). Set `scavenger_strongholds` 48/16, 8 chunks from survivor villages.
  Plains (oak/cobble) look everywhere for now; biome palettes later.
- Unverified: keep orientation of ladder/floodlights, piglins actually staying unzombified + gear as expected, street/keep jigsaw alignment, barricade orientation at dead ends, size of the sprawl.
- Test: `/locate structure dying_world:scavenger_stronghold`, `/place structure dying_world:scavenger_stronghold`; wait >15 s near piglins (must not zombify); open the treasure chest (netherite upgrade template); walk the streets to dead-end barricades.

## Pass 5-2 (2026-11-14) - fortified houses, floor guarantee, piglins everywhere
- USER: do fortified houses; floors must NOT spawn completely gone in the abandoned houses; piglins should spawn throughout the ENTIRE village.
  (Our worn processors never remove blocks; the vanilla house NBTs have intact floors. Floor repair added anyway as a guarantee - if the user still sees missing floors, ask where/which structure, e.g. gearwrights abandoned villages are a different structure.)
- New `tools/nbtrw.py`: typed NBT read/write round-trip (verified byte-identical on all 22 worn houses) + `Struct` view (blocks dict, entities, size; `entity()`), used to EDIT existing NBTs.
- `tools/gen_pass5_2.py` (run AFTER gen_pass5_1.py; overwrites `scavenger_stronghold/houses.json`): per worn plains house 2 copies in `structure/scavenger_stronghold/houses/<name>_{plain,fort}.nbt`, weights 40%/60% of the original, original processors kept.
  - both: floor level = lowest y with many floor-type blocks that are ROOFED (covered); every enclosed + roofed air cell on it gets the dominant floor block (187 cells repaired across 11 houses; open pens not filled). Farm animals/fish removed (frames/paintings/armour stands kept).
    Piglins on free interior floor cells (plain 1-2, fort 2-3; farms/fisher 1 on the lowest standable cell). 101 piglins over the 44 copies, every copy has >=1.
  - fort: ~15% roof-top blocks -> corrugated rusted metal (stairs keep facing/half/shape, slabs keep type), ~50% glass panes -> spruce planks, LOOKOUT on the highest roof point (3x3 spruce/corrugated platform, fence corner posts down to the roof, fence/barbed-wire rail with gaps,
    sodium floodlight on the platform edge pointing outward, crossbow piglin; template height grows if needed), 3-5 scrap props outside the walls incl. 1 loot barrel (bridge/other/scraps). Village materials stay dominant (R&R 12-74 blocks per house).
- `gen_pass5_1.py` decor: camp + cache always hold a piglin, scrap piles 50%, NEW `guard` decor (2 piglins behind a low scrap barrier, weight 3). Streets carry ~5 decor jigsaws each, so piglins spread along all streets.
- Unverified: lookout placement on odd roofs (church/library), fence posts look (unconnected), floodlight edge facing, piglin count feel / lag (persistent entities), repaired floors matching the house style.
- Test: `/place structure dying_world:scavenger_stronghold`; walk all streets: piglins in houses + at street camps/guard posts; fortified houses with lookouts; floors intact.

## Pass 6-1 (2026-11-14) - no floating abandoned houses
- User first asked for a 'worn not 30-years-abandoned' pass over all structures, then (after seeing that gearwrights abandoned houses are ruins by design: walls mostly gone, ~600 NBTs, nothing to repair)
  NARROWED it to: just fix their floors so they don't FLOAT. Landmarks (burnt_*, collapsed_minehead, ruined_chapel) stay AS-IS, no changes (user decision).
- Likely cause of 'missing floors': houses spawning over a partly eroded hillside; `beard_thin` only smooths a little, leaving overhangs / gaps under foundations.
- `tools/gen_pass6_1.py`: all 21 `dying_world:abandoned_{ruin,hamlet,village}_*` structures -> `terrain_adaptation: beard_box` (terrain filled under every piece). Post-edit; re-run after gen_pass3b2.py/gen_pass3c4.py.
  (abandoned_cabin + abandoned_watchtower already used beard_box.) Survivor villages/stronghold unchanged (beard_thin) - switch them too if the user sees floating there.
- Test: find an abandoned hamlet/village on a slope (`/locate structure dying_world:abandoned_hamlet_plains` etc.): houses should sit on filled ground, no hanging floors. Note: only NEW chunks.

## Pass 7-0 (2026-11-14) - savanna rebuild plan (docs only)
- USER REQUEST: remove the savanna houses (clashy) and replace with our own rich 1800s hot-climate US/European style, BDubs build quality, walkable + functional; study ALL houses' furniture and reuse the language; base untarnished + matching lived/ruined variants.
  User confirmed the roster in `docs/style_board_savanna.md` (vanilla-fit slots: small x3, medium x2, big, butcher, toolsmith, library, temple, 2 farms; later shepherd/weaponsmith/armorer/mason/tannery/cartographer; teepees dropped).
  Added: redo ANY building that uses the teepee style or the other ugly non-vanilla 'Mediterranean' buildings.
- FINDING: user's kubejs data replaces ALL vanilla village house sets (plains/taiga/desert/snowy/savanna) with custom 18-26 house sets and replaces the `minecraft:village/<family>/houses` pools. Our survivor villages copied from those. The savanna set = acacia log+slab shells with coloured terracotta panels + 3 white-wool teepees.
  (Correction to my earlier note: those kubejs `minecraft/` village files DO affect us - they are our donor/base houses; vanilla-named savanna houses in the merged data are unused.) See `docs/redo_list.md`.
- New tools/docs: `tools/furniture_scan.py` (regenerates `docs/furniture_catalog.md`, `furniture_patterns.json`, `house_palettes.md`), `docs/furniture_notes.md` (how furniture is built + the library for new houses), `docs/redo_list.md`, `docs/style_board_savanna.md`.
- Key furniture facts: table = fence+pressure plate, chairs = bottom stairs beside it, chest solo/on trapdoor plinth, bed pair (+foot chest), job block solo against a wall with a standing cell, wall torch/lantern/chain-lantern, potted plants, bookshelf stacks.
- OPEN QUESTIONS for the user: (1) ANSWERED: remove ALL tipis/teepees everywhere (see 7-0b); (2) which OTHER sets are the 'clashy Mediterranean' ones (desert `badlands_pueblo` 27? plains/taiga/desert/snowy custom sets?) - not touched until told. (3) palette proposal OK (3 blended sub-styles)? (4) tile roofs: brick stairs (red clay) OK?
- Next: 7-1 = reusable furniture + palette functions in a generator (`tools/gen_pass7_1.py`) + ONE test cottage with base, lived-in, ruined variants and the savanna pool hook so it can be `/place`d; judge quality before scaling (script-built BDubs approximations).

- USER CORRECTION (after 7-0): BDubs style = GRADIENTS based on lighting, not random multi-block noise. Rules saved in `docs/style_board_savanna.md` ('BDubs rules (CORRECTED...)'): block ramps (dark/rough -> light/clean) positioned by height + exposure, one step darker in shade (eaves, recesses, corners),
  noise only as clustered secondary breakup, ruin variants = same ramp shifted with direction (moss from ground, cracks mid, soot near chimneys). 7-1 generator must compute a per-block shade score (height + ambient-occlusion-like neighbour check) and map it to the ramp.

## Pass 7-0b (2026-11-15) - tipi/teepee removal decision (notes only, no game files changed)
- USER: 'get rid of all tipis in all [sets]; we will work over each set'. Known locations: savanna custom `savanna_teepee1-3` (+ our worn copies), desert donor `kaisyn:wooded_badlands_tipi` (15 NBTs / 12 accepted houses),
  gearwrights abandoned savanna ruins (14 tipi/teepee-named NBTs). Full checklist + method in `docs/redo_list.md`. Nothing regenerated yet; installed datapack still contains them.
- Still open from 7-0: which other sets are the 'clashy Mediterranean' ones; palette/tile-roof OK. Next: user works through sets with me; 7-1 (furniture library + test cottage with gradient/shade-score palette) when ready.

## Pass 7-0c (2026-11-15) - outlier scan (docs only)
- User: not sure which sets are 'clashy Mediterranean'; asked for a pass over all buildings with outlier NAMES so they can comment. `tools/outlier_scan.py` scans every distinct house in our village pools (kubejs base set + accepted donors; worn copies ignored) -> `docs/building_outliers.md`.
- Palette = structural-block shares (ground/plants/furniture/glass ignored); modded wood counted as wood. Findings (distance from the family base set; >0.4 = different):
  plains: forest_ruins (all cobblestone ruins, 0.75), birch_forest_romanian (deepslate + coloured concrete 20-37%, 0.50), cherry (deepslate, pagoda/large builds, 0.45); taiga: viking + old_growth_polish (~0.39, mostly plain wood);
  desert: wooded_badlands_tipi (wool 55%, 0.87) = TEEPEES, pueblo set matches the desert base palette (0.08); savanna base: 20% coloured terracotta/wool/concrete, 3 teepees; snowy: windswept:frozen (40% modded-wood blocks, 0.40).
  Single houses: base `plains_church` 11x28x18, `plains_library` 23x17x19, `taiga_church` 9x30x17, `snowy_stave_church` 15x27x26, `snowy_longhouse` 11x10x30 (very large); `taiga_mason` + `plains_mason` coloured concrete; desert smallhouse3-7 + toolsmith coloured terracotta ~20-30%;
  `snowy_taiga_temple_1` all stone; `cherry_farm_1` 9x15x10 other/stone; `birch_forest_small_farm_1` all deepslate.
- NOT in our pools (so not outliers here): kaisyn mediterranean/iberian/tudor/etc. exclusives, piglin, mushroom, nilotic - they only appear in `docs/house_palettes.md`. If 'Mediterranean' means one of those, tell me where you saw them (maybe from another mod's villages).
- Nothing regenerated; installed datapack unchanged.

## Pass 7-0d (2026-11-15) - stilt houses marked (docs only)
- USER: 'I don't like the savanna colour panel houses that are on poles at all. If it has poles bringing the floor up off the ground, mark that whole palette in all of the villages for removal.' Term = STILT houses (pile dwellings / palafitte).
- `tools/stilt_scan.py`: per template, ground blocks ignored, first floor layer (>=50% filled) at y>=2 with sparse layers (median <25%) and >=4 pole blocks below it; farms skipped. Savanna base: 7 of 18 stilt (armorer, big_house, butcher, cartographer, library, shepherd, medium_house2);
  gearwrights abandoned: savanna 16/53, swamp 25/63, snowy 1/73. Everything else 0 (plains/taiga/desert/snowy bases, pueblo, tipi, cherry, birch_romanian, forest_ruins, viking, polish, frozen).
- Marked in `docs/redo_list.md`: whole savanna base palette (incl. its non-stilt tannery/mason/toolsmith/weaponsmith/temple/farms + teepees), `dying_world:abandoned_{ruin,hamlet,village}_savanna` and `_swamp`. Nothing removed or regenerated yet.
- Open: user to confirm the swamp abandoned sets go too (stilts there are common, 25/63), and what replaces the abandoned savanna/swamp variants (new style or simply no structure in those biomes).

## Pass 7-0d2 (2026-11-15) - swamp stilts kept
- USER: swamp stilt houses are fine (they look proper on stilts); the dislike is the multi-colour-panel stilt houses in the savanna 'and other places'. Scan found that palette only in the savanna base set and gearwrights abandoned savanna sets.
- `docs/redo_list.md` updated: `dying_world:abandoned_{ruin,hamlet,village}_swamp` stay untouched. Still marked: whole savanna base set + `dying_world:abandoned_{ruin,hamlet,village}_savanna`. Docs only; no game files changed.
- Open: replacement for the abandoned savanna variants (new savanna style via 7-1+, or none). Other coloured-panel houses without poles (desert smallhouse3-7/toolsmith, taiga/plains masons, birch_romanian concrete) are NOT marked; user may comment later.

## Pass 8-0 (2026-11-15) - provenance audit + release build (docs/tools only)
- USER DIRECTION: (1) the NEW savanna style (7-1+) replaces `dying_world:abandoned_{ruin,hamlet,village}_savanna` (answers the 7-0d2 open question) - abandoned savanna = ruined variants of the new houses; (2) a pass will remove every structure that pulls 100% from mods and replace them with our own over the passes, so the final release needs no permissions from other authors; (3) bring the mod count down where possible.
- NEW `tools/provenance_audit.py` -> `docs/provenance_audit.md` + `.json`: for each of our structure sets, walks structure -> pools -> NBT pieces (-> jigsaw pools) and classes every piece OWN / VANILLA / KUBEJS:<ns> / MOD:<jar> (derived copies inherit their source: worn copies of base houses = KUBEJS:village_houses, mix_worn = donor mod). Also: structure TYPES implemented by mods, third-party pools/processors, mod blocks placed, loot/biome/mob namespaces, per-mod dependency matrix.
  Key result: CLEAN already = concrete_pads, industrial_mineshafts, scavenger_outposts (blocks: R&R/Create/tarbound), scavenger_strongholds (vanilla pieces), shipwrecks, strongholds, nether_fortress. 100% THIRD-PARTY = all gearwrights sets (abandoned ruins/hamlets/villages, burnt_*, ruined_chapel, collapsed_minehead: 2277 pieces), wells (forsaken, 792), abandoned_cabin, abandoned_watchtower, abandoned_smithy + lighthouse (createnewbeg), tarbound x4 (structure type), road_signs (supplementaries). MIXED = survivor_villages (base houses = kubejs custom sets 222, kaisyn donors 252, brutos 41, windswept 55, vanilla streets/centres).
- NEW `tools/release_policy.json` + `tools/build_release.py` -> `dist/release/dying_world_release_datapack.zip` + `docs/release_report.md`: copies the datapack, strips third-party pool elements (donor houses, unconfirmed base houses, mix processors), recomputes every structure's closure, drops structures/sets that still need third-party pieces/pools/processors/types (or have no houses left), copies only needed files + the empty overrides that disable natural sets, removes dangling exclusion zones, scans for third-party namespaces. Result with the default policy: 7 sets kept, 51 structures dropped (listed as a REBUILD QUEUE, fewest pieces first), 478 KB, scan CLEAN. Report also lists the mods the release needs (hard: rustandrebar, create (tracks), tarbound blocks; soft: biome ids) and the mods you could drop (formationsnether, formationsoverworld, forsaken, hearths, towns_and_towers, abandoned_cabins, watchtower_building, createnewbeg: 0 lang content = probably structure-only).
- HOW the user brings things back: add to `confirmed_mine` (tokens `gearwrights`, `village_houses`, `brutos`, `vsrevamped`, `kubejs`) ONLY what the user made / has permission for, or to `permission_granted` (jar-name substrings). Re-run `python3 tools/provenance_audit.py && python3 tools/build_release.py`.
- OPEN QUESTIONS for the user: (a) which kubejs-provided data is YOURS vs downloaded (gearwrights sets, vsrevamped/brutos, the custom village house sets replacing `minecraft:village/*/houses`)? Treated as third-party until answered. (b) wells (forsaken, 11 variants/792 pieces) and road signs (supplementaries structure type) and the 4 tarbound structures: rebuild, ask permission, or drop? (c) Vanilla-derived pieces (scavenger stronghold from bastion/village NBT, vanilla streets/centres) are kept in the release - OK, or should the stronghold also be rebuilt from scratch? (d) the mineshaft hard-needs create tracks (74 blocks) and tarbound (tar blocks 414): swap for vanilla rails / own blocks to drop Create/Tarbound from the requirements?
- Suggested order for own replacements (smallest first): abandoned_smithy + lighthouse (7 pieces), abandoned_cabin (7), burnt_* (23 each) and ruined_chapel, collapsed_minehead (19), abandoned_watchtower (23), tarbound-type small ruins (charnel crypt, radio, researcher cabin, shrine), wells, then the savanna abandoned sets via the new savanna houses, then the other abandoned ruins/hamlets/villages and finally the village house sets.

## Pass 8-1 (2026-11-15) - structures split out of kubejs/data
- USER: 8-0 may have read 'remove all structures' too literally - the user only wanted buildings MARKED so the ones they don't own can be pulled and replaced later (e.g. gearwrights abandoned buildings with our own structures + sets).
  CHECKED: 8-0 did NOT change the working datapack (7-0d2 and 8-0 `datapack/` are identical); it only added the audit tools and the separate RELEASE zip (`dist/release/`, 51 structures dropped). Ignore the release zip until the user asks for it.
- USER REQUEST: two zips so structures and the rest of kubejs/data are cleanly separated: (1) our build with ALL datapack structures it uses, (2) their data.zip stripped of every structure; unused structure files -> a third ARCHIVE zip (user's choice), nothing deleted.
- NEW `tools/split_data.py <user_data_dir> <out_dir>` (input = folder containing `data/` from the user's kubejs/data upload). Closure walk from every dying_world structure + set: structure json -> pools -> NBT jigsaw pools (length-prefixed NBT strings) -> processors -> biome tags.
  Outputs (copies kept in `dist/split/`):
  1. `dying_world_structures_datapack.zip` (5.8 MB): our 704-file build + 1182 structure files moved from kubejs/data (gearwrights abandoned/landmark NBTs+pools+processors+tags, the custom `minecraft:village/*` house sets, brutos/vsrevamped pieces) + `PROVENANCE.md`
     (per structure: NBT pieces by source OWN / KUBEJS-DATA:<ns>, plus EXTERNAL pools/tags/types still loaded from mod jars: abandoned_cabins, watchtower_building, createnewbeg, forsaken wells, tarbound types, supplementaries road signs, kaisyn/windswept donor houses).
  2. `data_without_structures.zip`: 1026 files (recipes, tags, biomes, noise, loot, mobrules ...), 0 structure-category files. Our own 704 files removed from it (the structures zip carries the current build).
  3. `unused_structures_archive.zip`: 194 structure files nothing of ours uses (brutos 77, minecraft 67 incl. the 5 `minecraft/worldgen/structure/village_*.json` overrides + 7 has_structure tags, gearwrights 43 (26 original structure jsons, 14 NBTs, 3 pools), vsrevamped 4, autumnity 2, environmental 1) + ARCHIVE.md.
  Every one of the 3106 input files lands in exactly one bucket (asserted). Structure categories = structure/, worldgen/{structure,structure_set,template_pool,processor_list}/, tags/worldgen/{structure,biome/has_structure}/.
  STAYS in data: 11 loot tables used by moved pieces (gearwrights chests/abandoned/* + landmark/*, vsrevamped village_library) -> install BOTH zips.
- Install: kubejs/data = contents of data_without_structures + the structures datapack (as loose `data/` files, or the zip itself if KubeJS 2101 loads zips - unverified). Same game as before.
- Next (user's plan): use PROVENANCE.md to pick the not-owned structures (gearwrights abandoned sets first) and replace them with our own structures + sets.

## Pass 8-2 (2026-11-15) - own abandoned smithy (first replacement) + structures zip built from the project
- USER: 'move onto the next stage' (no answer yet on which kubejs-data sets are theirs -> still treated as not-owned; smithy is a mod-jar structure anyway).
  Agreed order (suggested, user went ahead): smithy -> lighthouse (both createnewbeg) -> abandoned_cabin -> abandoned_watchtower -> wells; then savanna (7-1), gearwrights sets, road signs.
- PROJECT CHANGE: the 1182 structure files moved out of the user's kubejs/data in 8-1 now live in `datapack_imported/data/` (source of truth; the user no longer needs to re-upload data).
  `tools/build.py` now also writes `dist/dying_world_structures_datapack.zip` (= datapack/ + datapack_imported/ files still referenced, + PROVENANCE.md) and `dist/unused_structures_archive.zip` (imported files that became unused after a replacement). This is the zip to install.
  `tools/split_data.py` gained `structures_only` (used by build.py); the 8-1 split mode is unchanged.
- `tools/gen_pass8_2.py`: 2 script-built variants in `structure/smithy/`: smithy_1 forge house 11x11x9 (stone-brick plinth + spruce frame/plank walls, dark-oak gable roof, blast furnace + furnace under a brick/cobble chimney through the roof, open work bay under a lean-to with chipped anvil/smithing table/grindstone, quench cauldron, coal block, chest + loot barrel, lanterns, vines);
  smithy_2 open forge 9x10x9 (timber pavilion, cobble half-walls, central brick hearth + chimney, storeroom with door + chest, damaged anvil). Wear = mossy/cracked/stripped swaps + moss carpet, NO missing parts. R&R accents: rusted drum, rebar bundle.
  Pool `dying_world:smithy/start` (3:2). Loot `chests/smithy` = vanilla weaponsmith+toolsmith+armorer pools + iron/coal/chain/R&R scrap.
  Structure `dying_world:abandoned_smithy` (same id + set 80/30) -> own pool, beard_box; biome tag now = `#dying_world:has_structure/scavenger_outpost_any` (any land) instead of createnewbeg's tag. createnewbeg no longer needed by it (lighthouse still uses it).
- Test: `/place structure dying_world:abandoned_smithy` (a few times for both variants), check roof/chimney, stairs facing, chest + barrel loot.

## Pass 8-3 (2026-11-15) - own lighthouse
- USER: 'work through until the savanna pass is done' -> passes 8-3..8-6 + 7-1 run back-to-back without check-ins; each logged here.
- NEW `tools/buildkit.py`: shared helpers for replacement builds (rng, replace-only `worn()` with a gradient factor k, chest/stairs/slab/door/bed/table/chair/lantern/pot,
  `gable()` (ridge along x) / `gable_z()`, `fix_connections()` (fence/pane/bars/wall states from template neighbours), `register()` (pool + structure json + biome tag; keeps the existing set), `opt()`).
  Chair rule: `chair(facing)` = side of the BACK (point it away from the table).
- `tools/gen_pass8_3.py`: 2 variants `structure/lighthouse/lighthouse_{1,2}.nbt` (16x32x11): octagonal tower r3, stone-brick base -> white terracotta with 2 red bands, wear heavier near the ground,
  inside ladder (north wall) + 3 plank landings, gallery at y22 with iron-bar rail, glass lantern room (dark-oak frame) with centre column: glowstone + 4 LIT sodium floodlights pointing out, weathered copper cap + lightning rod;
  keeper's cottage east (cobble/spruce, gable roof, bed, table + chairs, smoker, chest + loot barrel, doors, passage into the tower).
  Loot `chests/lighthouse`. Structure `dying_world:lighthouse` (same set 80/30) -> own pool, beard_box, biomes: #minecraft:is_beach + stony_shore + snowy_beach (createnewbeg tag dropped).
  => createnewbeg is no longer used by any of our structures (smithy + lighthouse both own).
- Test: `/place structure dying_world:lighthouse` on a beach; climb, check lantern room + floodlights, cottage door/passage.

## Pass 8-4 (2026-11-15) - own abandoned cabin
- `tools/gen_pass8_4.py`: 3 worn log cabins `structure/cabin/cabin_{spruce,oak,dark_oak}.nbt` (13x11x11): horizontal log walls + upright corner logs on a cobble footing, gable roof, cobble chimney + fireplace (unlit campfire) on the east gable,
  porch (posts, slab roof, bench, loot barrel), bed, chest, table + 2 chairs, hides (carpet), crafting table, hanging lantern, windows; spruce adds a lean-to woodshed, oak a loft (ladder, hay). Vines on the north wall.
  Pool `dying_world:cabin/start` (3:2:1). Loot `chests/cabin` (hunter). Structure `dying_world:abandoned_cabin` (same set) -> own pool, beard_box; biomes = old list + old-growth taigas + dark forest.
  => abandoned_cabins mod no longer used by our structures (its natural sets stay disabled while installed; can be removed from the pack).

## Pass 8-5 (2026-11-15) - own abandoned watchtower
- `tools/gen_pass8_5.py`: `structure/watchtower/timber_1.nbt` (9x19x9: cobble/stone-brick ground storey with door/chest/barrel, 4 spruce log legs, plank backing + ladder, fence cross-rails, lookout platform y11 with rail,
  unlit signal campfire, chest, bell under a plank ceiling, gable roof) and `stone_1.nbt` (9x18x9: square keep tower with wear gradient, inside ladder + 2 landings (bed on the first), arrow-slit bars, crenellations, roofed wooden lookout, 2 chests, campfire).
  Pool `dying_world:watchtower/start` (3:2). Loot `chests/watchtower`. Structure `dying_world:abandoned_watchtower` (same set) -> own pool, beard_box; biomes = old list + meadow + windswept forest.
  => watchtower_building mod no longer used by our structures.

## Pass 8-6 (2026-11-15) - own wells (forsaken replaced)
- `tools/gen_pass8_6.py`: 5 worn wells `structure/wells/{temperate,cold,arid,wild,washhouse}.nbt`, each a real 3x3 water shaft (template starts 6 underground: structure start_height -6; water y1..3 sealed by shaft walls).
  temperate cobble/oak gable canopy + crank beam/chain/lantern; cold stone brick/spruce; arid smooth sandstone rim, cut-sandstone pillars, slab canopy; wild mud brick/mangrove + vines; washhouse = temperate well + open oak shed with 2 cauldron troughs, bench, scraps barrel.
  Structures `dying_world:wells/<style>` (biomes = concrete_pad_<group> tags; washhouse temperate), set `dying_world:wells` members replaced (2 each, washhouse 1), placement/frequency/exclusion kept.
  The 11 forsaken-based structure jsons + `has_structure/wells/*` tags were DELETED. => forsaken no longer used by our structures.
- REGEN ORDER (important): older generators rewrite registrations. Full rebuild order: gen_pass1 .. 3b2 .. 3c4 .. 3c5 .. 4_x .. 5_1 5_2 .. 6_1 .. THEN 8_2 8_3 8_4 8_5 8_6 (and later 7_1) LAST, then build.py.
  (3b2 rewrites abandoned_cabin/watchtower/smithy/lighthouse/wells; re-run the 8_x generators after it.)

## USER (2026-11-15, during 8-x): Brutos and vsrevamped were downloaded DATAPACKS (not the user's), and so is anything built from them (our worn copies etc.).
=> treat `brutos`, `vsrevamped` (+ derived worn/mix copies) as THIRD-PARTY in provenance/release; queue them for replacement like the mod donors.
   Still unanswered: gearwrights sets + the custom `minecraft:village/*` house sets (kubejs) - yours or downloaded?

## Pass 7-1 (2026-11-15) - NEW SAVANNA HOUSES (gradient palette engine)
- NEW `tools/savanna_kit.py`: buildings are drawn with ROLE cells (wall/base/floor/trim/beam/inner/roof/roof_slab) and finalized per variant.
  Wall score = position in its wall band (dark/rough base -> light/clean top) + smooth clustered VALUE NOISE (+-.13, scale 3) - shade (.2 when something solid is above the outward face: eaves, porches, balconies);
  floors darker next to walls (AO); base course = mid-ramp + clustered breakup. Ramps per sub-style: hacienda (cobble -> stone brick -> smooth sandstone -> white terracotta stucco, brick tile roof, red sandstone ridge),
  creole (stripped birch -> birch planks -> white terracotta, dark-oak shingles), limestone (cobble -> stone brick -> sandstone -> cut -> smooth sandstone, andesite base/quoins, spruce roof). Acacia = trim/posts/beams everywhere.
  RUINED = same ramp shifted darker from the ground up (-.45*(1-h) -.1) + swaps (stucco -> light gray, sandstone -> plain, bricks -> cracked/mossy), brick roof partly mossy stone brick, beds -> carpets, job blocks -> cobble, plants -> dead bush, crops -> dead bush/grass, half the standing lanterns gone, cobwebs in upper corners. Nothing missing.
  Variants: base (no villager jigsaw, reference), lived (minecraft:bottom villager jigsaw -> minecraft:village/savanna/villagers), ruined (no villagers). Every building: minecraft:building_entrance jigsaw at the door on the front row (south, y1).
- `tools/gen_pass7_1.py` (run AFTER gen_pass3c4.py): 12 buildings x 3 variants in `structure/savanna/<name>_{base,lived,ruined}.nbt`:
  creole_cottage 9x9 (porch), dogtrot 11x9 (2 pens + breezeway, smoker), limestone_cottage 10x9 (chimney/fireplace, bookshelves), casita 12x11 (hacienda, tile veranda with acacia arches, 2 rooms),
  courtyard_house 13x12 (U-plan around a court, gate, loom), planter_house 15x12 (2 storeys, porch + balcony, parlour sofa, 2x3 dining table, kitchen, 2 bedrooms + study with cartography table, ladder),
  smokehouse 9x12 (butcher: smoker, meat hooks, chimney), forge 13x10 (toolsmith: open-sided, grindstone, blast furnace chimney, anvil), schoolhouse 12x13 (library: lectern, bookshelf wall, desks, blackboard),
  chapel 17x20 (cleric: brewing stand altar, pews, bell tower with bell + ladder), kitchen_garden 15x8 (walled crops + water channel, pergola, composter), orchard 12x12 (6 small acacia trees, melon/pumpkin rows, composter).
  `minecraft:village/savanna/houses` (survivor village) = 24 entries (lived weight*4, ruined weight*6 = 40/60). Old savanna worn copies (`structure/village/savanna/`) deleted; the user's custom savanna house set (incl. stilt/colour-panel houses + 3 teepees) is no longer used (-> unused archive).
  Chest loot = vanilla village tables (savanna house, butcher, toolsmith, cartographer, temple).
- Pass 7-2 `tools/gen_pass7_2.py` (run after 7_1, 3b2, 6_1): abandoned_ruin_savanna -> single ruined house (pool `dying_world:savanna/ruined_houses`); abandoned_hamlet/village_savanna -> VANILLA savanna meeting points (4) + vanilla streets (27, non-custom, non-zombie)
  copied to `structure/savanna/abandoned/` with pools retargeted (houses -> ruined_houses, streets -> ours, villagers/cats/golem/animals -> empty); size 4/6, beard_box. Gearwrights abandoned savanna pieces no longer used.
  Survivor village town centres: override of `minecraft:village/savanna/town_centers` without the custom `savanna_teepee_crossing` (teepee rule).
- Build: 772 own files; 118 imported files became unused -> `dist/unused_structures_archive.zip`.
- Not yet checked in game: everything above. Things to look at: door/entrance alignment with streets, interior walkability (beds/job blocks reachable), shutter orientation, the gradient look, ruined variants, chapel tower/nave overlap, orchard leaves (persistent).
- REGEN ORDER: ... 6_1, 8_2..8_6, 7_1, 7_2, build.

## Pass 8-7 (2026-11-15) - one-zip install
- USER: wants ONE zip per test: unzip, take its data/ folder, move it in as a fresh kubejs/data. No layering (layering leaves stale files).
- Project now holds `kubejs_base/data/` = the user's NON-structure kubejs data (1026 files, from 8-1's data_without_structures). `tools/build.py` additionally writes
  `dist/kubejs_data.zip` = data/ (kubejs_base + structures datapack: ours + still-used imported files; conflicts abort the build) + PROVENANCE.md + README.txt. THIS is the deliverable from now on (2863 files).
- If the user edits their own non-structure data (recipes, tags, mobrules...), they must send it so kubejs_base is updated, otherwise the next build overwrites their edits.

## Pass 8-8 (2026-11-15) - first in-game feedback round (10 screenshots)
- USER FEEDBACK: watchtower looks good. Lighthouse: cottage chain+lantern floated at chest height (not reaching the roof), floating lantern on the 3rd floor (-> put on a lootless barrel), gallery railing wonky -> widen the walkway.
  atmospheric:village_scrubland still findable via /locate #minecraft:village. Savanna houses: same floating lanterns; roof open without a ceiling; slab table tops too thick (use pressure plates). Abandoned cabin roof: gap where porch roof meets the main roof.
- FIXES (generators re-run in order 8_2..8_6, 7_1, 7_2, then build):
  - `buildkit.anchor_chains()` (called from fix_connections, so every builder): every vertical chain column is extended UP until it meets a block. Verified: 0 chains / hanging lanterns with air above across all our script-built NBTs.
  - Roof gap: `buildkit.gable/gable_z`, smithy's local gable and `savanna_kit.B.gable` now place a TOP PLATE row on both long walls at roof level (was an open slit between wall top and first roof row -> the cabin porch/roof hole + 'open roof').
  - Savanna: `B.gable(ceiling=True)` adds a flat plank-slab (top) ceiling under every roof (acacia/birch/spruce by sub-style) with an acacia beam ring; chapel nave (vaulted) and open forge keep no ceiling. New role `ceil`.
  - Tables: schoolhouse desks + planter dining table = fence + pressure plate (no slabs).
  - Lighthouse: 3rd-floor lantern stands on a lootless barrel; gallery is now a SQUARE platform radius 5 (2-wide walkway around the tower) with a straight iron-bar rail.
  - NEW `tools/gen_pass8_8.py`: code-registered structures killed by emptying their biome tag (replace:true, []). First entry: atmospheric:village_scrubland. Add more ids to KILL if /locate finds others (candidates seen in reference: towns_and_towers village tags (sets already disabled), waystones (kept)).
- REGEN ORDER now ends: ... 8_2 8_3 8_4 8_5 8_6 7_1 7_2 8_8, build.

## Pass 8-9 (2026-11-15) - lantern head clearance
- USER RULE: hanging lanterns must be high enough that a 2-block-tall player never hits them: lantern y >= floor + 3.
- `buildkit.lift_lanterns()` (runs inside fix_connections before anchor_chains): script-built structures (8-x, savanna) move low lanterns up under the ceiling. Verified 0 violations in them.
- NEW `tools/gen_pass8_9.py` (run LAST, after 3c4/5_2/7_1 which rewrite the house copies): same rule over EVERY dying_world NBT incl. worn/mix village copies + stronghold house copies.
  Fix order: lift under the ceiling (7) -> if the room is only 2 high: wall torch on an adjacent block at head height or a standing torch on the floor (torches have no collision) (85) -> else removed (41, e.g. lanterns over tables/fences).
  88 files changed. NOTE: the LIVED village houses are the original kubejs/vanilla/donor NBTs (not ours) and are untouched.
- REGEN ORDER now ends: ... 8_2 8_3 8_4 8_5 8_6 7_1 7_2 8_8 8_9, build.

## Pass 8-10 (2026-11-15) - last tipi removed
- `tools/gen_pass3c4.py`: desert donor `kaisyn:wooded_badlands_tipi` removed (desert donors = badlands_pueblo only). Its 11 worn copies deleted.
  Re-ran the village chain: 3c4 -> 3c5 -> 7_1 -> 7_2 -> 8_9, then build. Diff check: only the desert house pool changed semantically + 11 tipi files gone; the other ~180 'changed' NBTs are byte-level only (same blocks).
- `kubejs_data.zip` now contains 0 files named tipi/teepee (the custom savanna teepees + teepee crossing were already unused -> archive). Lantern rule: 0 violations.
- Tipi checklist in docs/redo_list.md: DONE everywhere (savanna set, teepee town centre, desert donor, gearwrights abandoned savanna = replaced in 7-2).

## Pass 8-11 (2026-11-15) - Brutos + vsrevamped dropped entirely
- USER: drop EVERYTHING Brutos and vsrevamped, incl. buildings built on them; rebuild step by step afterwards.
- `tools/gen_pass3c4.py`: plains donor 'cherry' (brutos:village/cherry/houses, vsrevamped loot) removed. NEW `tools/gen_pass8_11.py` (run after 3c4): deletes our worn cherry copies, the vsrevamped
  structure-set disable overrides, brutos/vsrevamped files in datapack_imported/ and kubejs_base/ (5 vsrevamped loot tables of the user's data). `docs/disabled_structure_sets.txt` no longer lists the 2 vsrevamped sets (67 now).
- FINDING: the user's custom plains/taiga/snowy STREET pieces (`minecraft:village/<fam>/streets/<fam>_crossroad_1` etc.) use vsrevamped processors (`vsrevamped:<fam>_streets`) => they are vsrevamped content.
  8_11 overrides `minecraft:village/{plains,taiga,snowy}/streets` with the VANILLA street pieces (16/16/17, vanilla processors street_plains / street_snowy_or_taiga, legacy elements, terrain_matching). Desert/savanna streets had no vsrevamped refs (unchanged).
  OPEN QUESTION for the user: are the custom village HOUSE sets / town centres (minecraft:village/*/houses ...) also from vsrevamped? Their pools have no vsrevamped refs, but they came with the same street set. If yes -> drop them too (villages would then need our own houses per family).
- BUG FIXED in `tools/split_data.py`: the closure now starts from EVERY structure-category file of ours (pools we override can be reachable only through vanilla jar NBTs, e.g. snowy houses via vanilla streets). Without it the snowy custom houses would have been left out of the zip.
- Result: 0 brutos/vsrevamped files or references in kubejs_data.zip; structures zip 743 own + 991 imported; 162 imported files unused -> archive.
- REGEN ORDER: ... 3c4, 3c5, ..., 8_2..8_6, 7_1, 7_2, 8_8, 8_11, 8_9, build.

## Pass 8-12 (2026-11-15) - lighthouse roof + gearwrights provenance check
- USER: lighthouse railing is great; the copper cap was wonky (layers floating). Wanted: tall steep DEEPSLATE slope with a deepslate wall finial on top, NO copper.
  `tools/gen_pass8_3.py` `roof()`: 3 tiers of deepslate tile stairs (radius 3/2/1) each with 2 layers of deepslate tiles inside (2:1 steep profile), corner stairs with outer shapes (vanilla rule),
  apex tile + 2 deepslate tile walls; lantern-room top ring now polished deepslate; lightning rod removed; template height 36.
- GEARWRIGHTS CHECK (user: 'look at the naming for our own modpack name; if not obvious, scrap and rebuild with our own'):
  - kubejs_base/data/gearwrights (worldgen tweaks: ore budget biome modifiers, tree placed features per mod, lithostitched windmill/watermill modifiers, loot tables) = pack-specific => clearly the user's own pack config.
  - datapack_imported/data/gearwrights/structure (abandoned ruins/hamlets/villages + landmarks, 838 NBTs) is NOT clean: names are systematic derivatives `<source house>_a / _b / _burnt` of other sets
    (e.g. cherry_armorer_a/_b/_burnt = Brutos/vsrevamped cherry houses, cherry_crossroad_1_a = cherry streets), mixed DataVersions 3218 (1.19.3), 3463/3465 (1.20.1), 3955 (1.21.1), 4189 (1.21.4) => pieces gathered from several third-party sources and batch-processed.
  => Recommendation given: treat gearwrights STRUCTURES as third-party-derived -> scrap + rebuild with our own (same route as savanna: ruined variants of our new houses on vanilla streets). Waiting for the user's go.

## Pass 9-1 (2026-11-15) - OUR PLAINS-FAMILY HOUSES (most common family)
- USER: 'work on next pass for fleshing out our own buildings in most common biome' -> plains family (plains + forests/birch/flower forest/cherry grove ... via village_biomes.py).
- `tools/gen_pass7_1.py` builders parameterized (module globals WOOD, STYLE_MAP, PREFIX, FAMILY + `mkB()`); savanna output unchanged except ruined floors now also swap spruce/oak planks -> stripped wood.
  `savanna_kit`: B.family drives the villager pool (minecraft:village/<family>/villagers) and default chest loot (village_<family>_house). New ramps: farmhouse (spruce -> oak -> birch planks -> white terracotta whitewash, dark-oak roof),
  timber (stone brick -> mud brick -> white plaster, dark-oak frame, spruce roof), fieldstone (cobble -> stone -> stone brick -> polished andesite, oak roof). RUIN_SWAP gained oak/spruce planks, stone, polished andesite, mud bricks.
- NEW `tools/gen_pass9_1.py` (run after 3c4 + 7_1; then 8_9, build): 13 buildings x base/lived/ruined in `structure/plains/plains_<name>_<variant>.nbt` = the 12 savanna builders re-skinned in oak
  (creole->farmhouse, limestone->fieldstone, hacienda->timber) + NEW `barn` (shepherd: 13x17 frame barn, hay loft + ladder, stalls, loom, open gates).
  `minecraft:village/plains/houses` = ONLY ours (26 entries, lived 40 / ruined 60). Our old plains worn + kaisyn mix copies deleted; the custom plains house set + kaisyn plains donors are no longer used (-> archive).
  `dying_world:plains/ruined_houses` written for a later abandoned-plains rebuild (not hooked; waiting for the user's go on scrapping gearwrights structures).
- village_plains now: OWN houses + vanilla streets + the user's custom town centres/terminators (KUBEJS-DATA minecraft 9).
- Test: `/place template dying_world:plains/plains_<name>_lived|_ruined` (names: creole_cottage dogtrot limestone_cottage casita planter_house courtyard_house smokehouse forge schoolhouse chapel kitchen_garden orchard barn); `/locate structure dying_world:village_plains`.
- REGEN ORDER: ... 7_1, 7_2, 9_1, 8_8, 8_11, 8_9, build.  (8_11 must stay after 3c4; 9_1 after 3c4 too.)

## Pass 9-2 (2026-11-15) - denser plains/taiga/snowy villages
- USER PLAYTEST: plains village spawned with ~1 large building + 2 Create mill buildings (gearwrights lithostitched modifiers - intended). Savanna/desert normal size.
- CAUSE: 8-11 swapped plains/taiga/snowy to VANILLA streets: ~2.4 house plots per piece (plains: 16 pieces/39 plots, avg area 186) vs dropped vsrevamped streets ~3.9 (9/35, area 77) and savanna custom ~7.8 (8/62).
  Same jigsaw size budget => far fewer houses; our big buildings eat the few plots.
- USER CHOSE fixes 1 + 3: NEW `tools/gen_pass9_2.py` (post-edit after 3c4): village_plains/taiga/snowy jigsaw size 3 -> 6, max_distance_from_center 65 -> 80 (= vanilla village values; our survivor villages were all size 3 / 65 - savanna/desert stay 3 because their custom streets are dense).
  `gen_pass9_1.py` ROSTER weights: cottages 6/4/6, casita 3, planter/courtyard/chapel/barn 1, others unchanged.
- Not done (option 2/4 for later): weight vanilla streets by house plots, or our own compact street sets per family.
- Test: `/place structure dying_world:village_plains` several times (also village_taiga, village_snowy): count houses vs before.
- REGEN ORDER: ... 7_1, 7_2, 9_1, 9_2, 8_8, 8_11, 8_9, build.

## BACKLOG (user, 2026-11-15): FANCY STREETS per biome family in the BDubs gradient style
- Own compact street sets per family (replaces vanilla streets; also fixes village density = option 4 of 9-2): path gradients (coarse dirt/gravel/packed mud edges -> dirt path/cobble/stone-brick centre, worn toward the edges),
  curbs + drainage, lamp posts (head-clearance rule), fences/hedges/planters, benches, wells/market stalls at crossroads, signposts; dense house plots (>=3 per piece) with jigsaws matching vanilla conventions
  (minecraft:street / building_entrance / bottom-decor). Plan: style board per family -> plains first -> others. Not started.

## Pass 9-3 (2026-11-15) - cherry builds removed + OUR PLAINS STREETS (gradient)
- USER: plains test PASSED (9-1/9-2). 'Not a fan of the cherry builds at all' -> remove all.
- NEW `tools/gen_pass9_3.py` (run after 3b2/3c4/6_1/9_1):
  (a) dying_world:abandoned_{ruin,hamlet,village}_cherry deleted (structure + biome tag) and removed from the abandoned sets. A scan of every shipped NBT found cherry-built pieces ONLY in gearwrights abandoned/cherry (78 files -> now unused -> archive).
  (b) plains street set `structure/plains/streets/*` (8 pieces): straight16 x2 (2 plots/side), straight10 (1 plot/side), cross, tee x2, corner, end (cul-de-sac + trough).
      KEY DESIGN: pieces are NARROW (7 wide: 5 road + 1 verge each side); house-entrance jigsaws sit on the verge facing out, so houses are placed OUTSIDE the street bounding box (global free space).
      Vanilla 16x16 street boxes only accept houses that fit inside the box (=> our big buildings failed). Gradient road: verge grass/coarse dirt + flowers/hedges/hay/barrels -> gravel/coarse dirt -> dirt path -> centre dirt path with clustered cobble/stone-brick/mossy paving (value noise).
      Lamp posts = oak fence x3 + standing lantern on top (head-clear). Street jigsaws on the centre line, y1, aligned; decor jigsaws -> minecraft:village/plains/decor. Junction road arms reach every street side.
      `minecraft:village/plains/streets` = ours only (terrain_matching), fallback = the user's plains terminators.
- BACKLOG item 'fancy streets' started: plains done; other families later (same generator pattern, family palettes).
- TESTED OK (user: "plains looks perfect"). Test was: `/place structure dying_world:village_plains` x3-4: density, big buildings now spawning, roads continuous through junctions, lamp posts, verge props; `/locate structure dying_world:abandoned_village_cherry` should fail (unknown).
- REGEN ORDER: ... 7_1, 7_2, 9_1, 9_2, 9_3, 8_8, 8_11, 8_9, build.

## Pass 9-4 (2026-11-15) - OUR TAIGA FAMILY (houses + streets)
- USER: plains TESTED OK ('plains looks perfect'); go ahead with taiga.
- `gen_pass9_3.py` street generator parameterized (module globals FAMILY + PAL palette; `write_streets()`); plains output identical except 1 prop cell (hay -> barrel, RNG order).
- `savanna_kit`: taiga ramps logcabin / stonetimber / heavystone (+ RUIN_SWAP dark-oak planks, andesite); `B.STEEP` class switch -> `_steep()` 2:1 gable (full roof block + stairs per row, gable ends closed incl. the course between rows), +8 template headroom.
- NEW `tools/gen_pass9_4.py` (after 3c4, 7_1, 9_1, 9_3, 8_11): 14 taiga buildings x base/lived/ruined in `structure/taiga/` (spruce re-skin of the builders, steep roofs) + NEW longhouse (9x17 Nordic hall, hearth strip + campfire, 4 long tables/benches, 4 beds, smoker)
  and sawmill (open shed, stonecutter = mason job, saw bench logs, log stacks, grindstone). Pools `minecraft:village/taiga/houses` (28 entries, 40/60) + `minecraft:village/taiga/streets` (8 pieces, taiga palette: podzol verges, ferns/berries, rooted dirt/gravel, cobble/mossy/spruce-plank centre, spruce lamp posts) = ours only.
  Our old taiga worn/mix copies deleted (kaisyn viking/polish donors + custom taiga houses now unused -> archive). `dying_world:taiga/ruined_houses` for later.
- Lantern lift changed (buildkit + 8_9): a too-low lantern now hangs at the LOWEST head-clear height (floor+3) with the chain up to the ceiling (was: right under the ceiling -> vaulted rooms got lanterns 10 blocks up). Our builds: 0 too low, 0 > floor+5.
- Test: `/place template dying_world:taiga/taiga_<name>_lived|_ruined` (creole_cottage dogtrot limestone_cottage casita planter_house longhouse sawmill smokehouse forge schoolhouse chapel kitchen_garden orchard barn); `/place structure dying_world:village_taiga` x3 (move ~300 between).
- REGEN ORDER (authoritative): 1 .. 3c4 3c5 .. 4_x .. 5_1 5_2 .. 6_1, 8_2 8_3 8_4 8_5 8_6, 7_1 7_2, 8_8, 8_11 (vanilla streets for taiga/snowy), 9_1 9_2 9_3 9_4, 8_9, build.

## Pass 9-5 (2026-11-15) - OUR SNOWY + DESERT families, SAVANNA streets (user: 'do 1-4 quickly, I test all at once')
- NEW `tools/gen_pass9_5.py` (after 9_4): `build_family()` helper (wood, style map, prefix, steep/flat roofs, per-family yard ground) + `streets(fam, palette)`.
  - snowy: spruce, STEEP roofs, ramps chalet / frost (packed-ice base course, polished diorite top) / stonetimber; 13 buildings (taiga roster incl. longhouse + sawmill), snow-block yards; streets: snow/coarse verges, gravel/packed-ice edges, cobble/stone-brick/gravel centre, spruce lamps + hedges, ferns/berries, log stacks.
  - desert: spruce trim, FLAT roofs with parapets (`B.FLAT`), ramps adobe (mud brick -> packed mud -> smooth sandstone -> whitewash) / sandstone (chiseled trim) / hacienda; 10 buildings (no barn/orchard/longhouse), sand yards;
    streets: sand verges, sandstone/gravel edges, smooth/cut sandstone centre, sandstone-wall lamp posts, no hedges, dead bushes, decorated pots/barrels/hay.
  - savanna: houses unchanged; NEW streets (grass/coarse verges, packed mud edges, mud-brick/packed-mud centre, acacia lamps + hedges, decorated pots).
  - village_desert / village_savanna -> size 6 / radius 80 (all five survivor villages now 6/80). Windswept frozen + pueblo donors and the custom snowy/desert houses + all custom street sets are unused now (-> archive).
- savanna_kit: ramps chalet/frost/adobe/sandstone; `full_of()` maps roof families to full blocks (was '<fam>_planks' only); RUIN_ROOF for sandstone families; `B.FLAT`, `B.GROUND` (per-family yard ground).
- FIX: `porch_posts()` default wood was frozen to acacia at def time -> plains/taiga porches had acacia posts; now the family wood (re-ran 7_1, 9_1, 9_4, 9_5).
- All five survivor village families now = OUR houses + OUR streets (+ the user's custom town centres/terminators).
- REGEN ORDER: ... 8_8, 8_11, 9_1 9_2 9_3 9_4 9_5, 8_9, build.
- NEXT (user): test everything at once, then the ABANDONED villages/hamlets phase (ruined_houses pools exist for all five families).

## Pass 9-6 (2026-11-15) - ABANDONED ruins/hamlets/villages = our ruined houses on our worn streets
- USER: all five survivor village families TESTED OK ('all the villages look good'). Next = abandoned phase.
- `gen_pass9_3.py`: `ABANDONED` switch -> street jigsaws -> dying_world:<fam>/abandoned/streets, plots -> dying_world:<fam>/ruined_houses, no decor jigsaws, lamp posts = unlit 1-2 high stubs;
  writes `structure/<fam>/abandoned/streets/*` + pools `<fam>/abandoned/{streets,town_centers}` (start = 'plaza': overgrown crossroads with a dry cauldron trough).
- NEW `tools/gen_pass9_6.py` (after 9_5 and 7_2): worn palettes per family (more verge/coarse ground, mossy cobble/gravel centre, grass/ferns/dead bushes, cracked pots, mossy rubble props);
  abandoned_ruin_<fam> -> single house from <fam>/ruined_houses; abandoned_hamlet_<fam> size 4 / abandoned_village_<fam> size 6 -> <fam>/abandoned/town_centers; radius 80, beard_box (tags/spawns/sets unchanged).
  Families: plains, taiga, snowy, desert, savanna (7-2's vanilla-street copies for savanna deleted). SWAMP keeps the gearwrights stilt set (user liked it).
- Result: gearwrights abandoned pieces for those 5 families unused -> archive (868 imported files now unused); only swamp + landmarks (burnt_*, chapel, minehead) still use gearwrights structures.
- Test: `/place structure dying_world:abandoned_village_<fam>` / `_hamlet_` / `_ruin_` for plains taiga snowy desert savanna (move ~300 between).
- REGEN ORDER: ... 9_1 9_2 9_3 9_4 9_5 9_6, 8_9, build.

## Pass 9-7 (2026-11-15) - whole-pack COHERENCE audit + fixes
- USER: 'compare all structures against each other to make sure the whole modpack is coherent, then fix gaps in logic'.
- NEW `tools/coherence_audit.py` -> `docs/coherence_audit.md` (reads dist/kubejs_data.zip = what the game loads): every set (spacing/sep/freq/exclusion/salt clashes/members exist),
  every structure (in a set? start pool exists, biome count, terrain adaptation, size/radius, monster spawns), biome coverage (land biomes with no survivor/abandoned settlement, overlapping village families),
  loot tables referenced by our chests/barrels exist, other namespaces referenced. Structural issues found: 0 (sets, pools, loot all consistent).
- LOGIC GAPS fixed by NEW `tools/gen_pass9_7.py` (post-edit after 9_6):
  1. biome gaps: plains family += cherry_grove (now settled by OUR plains houses - the cherry *builds* stay gone), RU highland_fields / eucalyptus_forest / windswept_maple_forest / wisteria_grove;
     taiga += RU blackwood_taiga + pine_slopes, environmental pine_slopes, windswept_forest; snowy += windswept snowy_pine_barrens; abandoned plains ruin/hamlet += RU ashen_woodland;
     abandoned SWAMP stilt set widened from swamp only to mangrove_swamp, environmental marsh, RU bayou/old_growth_bayou/fen/marsh/fungal_fen. (49 -> 31 land biomes without settlements.)
     Deliberately left empty (like vanilla): peaks/slopes/cliffs/mountains, stony shore, mushroom fields, dark forest, jungles/rainforests/tropics (wet-hot: earlier user decision, bunkers dropped), hot springs.
  2. exclusion zone (3 chunks from survivor villages) added to abandoned_smithy, abandoned_watchtower and the 4 tarbound sites (they could spawn inside villages).
  3. abandoned cabin/smithy/watchtower/lighthouse get the same light undead spawns as abandoned ruins (zombie/skeleton/zombie villager) - they had none.
  4. survivor villages + scavenger stronghold -> beard_box (same no-floating rule as abandoned settlements since 6-1; they were beard_thin).
  5. cleanup: 28 processor lists left by 3c4 for the replaced house sets (savanna/desert/snowy lived/weathered/scorched/tarred + mix/*) deleted (unreferenced).
- Kept on purpose: `_base` house variants (unreferenced reference/test templates for /place template), neoforge biome modifier (auto-loaded).
- REGEN ORDER: ... 9_1 .. 9_6, 9_7, 8_9, build, coherence_audit.

## Pass 9-8 (2026-11-15) - gameplay walkthrough ('step through the world, find where gameplay fails')
- NEW `docs/gameplay_walkthrough.md`: survival run checked against all our structures + the 21 disabled vanilla sets + pass-2 feature removals.
- FIXED: (a) fletcher + mason had no job site outside taiga/snowy -> `gen_pass7_1.forge()` gains a fletching table + stonecutter (all families regenerated: 7_1 9_1 9_4 9_5 9_6, 8_9);
  (b) NEW `tools/gen_pass9_8.py`: `#minecraft:village` += our 5 survivor villages; explorer/treasure map tags retargeted to existing structures
  (woodland -> scavenger_stronghold, ocean -> lighthouse, trial chambers -> industrial_mineshaft, buried treasure/dolphins -> shipwreck_beached) - vanilla targets are disabled, so cartographer map trades vanished and shipwreck map chests gave blank maps.
- OPEN DECISIONS for the user (see the doc): end cities disabled => ELYTRA + SHULKER shells unobtainable (biggest gap); monuments (sponge), trial chambers (mace, breeze), ancient cities (echo shards, swift sneak),
  mansions/outposts (allays), ocean/trail ruins + pyramids (sniffer eggs, sherds), buried treasure (heart of the sea); no overworld mob spawners (monster rooms removed, mineshaft spawner room deferred).
- REGEN ORDER: ... 9_6, 9_7, 9_8, 8_9, build, coherence_audit.

## USER DECISIONS after 9-8 walkthrough (2026-11-15)
1. END/NETHER gaps -> our own INCURSION STRUCTURES: research buildings mixing MEDIEVAL ALCHEMIST + DIESELPUNK INDUSTRIAL research station, on EITHER END of a portal
   (overworld <-> End, overworld <-> Nether), with appropriate items on each side (elytra/shulker shells etc. on the End side). They EXPAND into jigsaw mini-villages
   (feel of a nether fortress / end city). Not started; feasibility notes given to the user (datapack can't pair two structures across dimensions exactly; see reply).
2. Monuments / trial chambers / ancient cities -> BUILD OUR REPLACEMENTS (sculk ruin site 5-4 + loot placement for sponge, mace/heavy core, breeze rods, echo shards, swift sneak ...).
3. Mob spawners -> MINESHAFT SPAWNER ROOM (zombie / skeleton / spider) in the industrial mineshaft.

## USER ANSWERS for the incursion stations (2026-11-15)
- End portal in the overworld gate hall must still REQUIRE EYES OF ENDER (frame with empty eye slots, vanilla style).
- ONE GUARANTEED ELYTRA per End station ('end city').
- Datapack-only portals OK: near-vanilla parity - 'you can get in, but you might need to work to get back out' (nether portals link by vanilla rules; end portal blocks go to the End platform / back to spawn).

## Pass 9-9 (2026-11-15) - mineshaft spawner rooms
- NEW `tools/gen_pass9_9.py` (after 4_2b): `structure/mineshaft/spawner_{zombie,skeleton,spider}.nbt` (11x6x9 room shell, same door jigsaw): rebar-heavy cell, mob spawner on a mossy plinth (vanilla defaults),
  cobwebs, bone blocks + skull, dead floodlight, danger sign, chest with `dying_world:chests/mineshaft_dungeon` (= vanilla simple_dungeon: saddles, name tags, music discs, golden apples - no other source since monster rooms were removed).
  Unlit so spawners run. Added weight 1 each to `dying_world:mineshaft/rooms` (~3 in 23 door alcoves).
- `tools/nbtw.py`: block-entity nbt values may now be typed tuples (needed for SpawnData compound); string values unchanged.
- Test: `/place structure dying_world:industrial_mineshaft` and explore door alcoves, or `/place template dying_world:mineshaft/spawner_zombie`; check spawner mob + chest loot.
- REGEN ORDER: ... 4_2a 4_2b 9_9 4_2c 4_2e 4_2s ... (9_9 right after 4_2b).
- NEXT: incursion stations (style board first: overworld gate hall village -> nether outposts -> End stations), then monument/trial/ancient-city replacements.

## USER DECISIONS (2026-11-15) - mob loot + station invasions
- Bastion loot -> piglin/brute DROPS, ADDITIVE (not replacing loot tables) so other datapacks/mods still work; only bastion items NOT already in scavenger structures; occasional gold OK; snout trim = my judgement; no ancient debris.
- Heart of the sea = rare drowned drop (0.5% ok), player kill only, Looting increases rates.
- Nether research station invasions: OVERWORLD side spawns ZOMBIFIED PIGLINS ONLY (no piglins/brutes - they'd zombify anyway); NETHER side spawns ZOMBIES + SKELETONS (husks dropped: they need sky).

## Pass 9-10 (2026-11-15) - additive mob drops (NeoForge global loot modifiers)
- NEW `tools/gen_pass9_10.py`: `data/neoforge/loot_modifiers/global_loot_modifiers.json` (replace:false) + `dying_world:loot_modifiers/{piglin_extra,piglin_brute_extra,drowned_extra}` (type neoforge:add_table,
  conditions neoforge:loot_table_id + minecraft:killed_by_player) -> `dying_world:entities/*` tables with per-pool `random_chance_with_enchanted_bonus` (Looting).
  piglin: gold nuggets 10% (2-6), gold ingot 2%, snout trim 0.4%; brute: nuggets 30% (3-9), ingot 8%, snout 1.5%; drowned: heart of the sea 0.5% (+0.25%/Looting level).
  Scan: every bastion item is already in the scavenger stronghold tables (copies of all 4 bastion chests) -> no other bastion items added (netherite template stays a stronghold item).
- The user's own kubejs `minecraft:entities/piglin_brute` override is untouched (modifiers stack on top).
- Test: kill piglins/brutes/drowned with/without Looting (many kills, e.g. /summon + /kill won't count - must be player kills).

## Pass 9-11 (2026-11-15) - INCURSION RESEARCH STATIONS (user: 'fill in the remaining holes')
- NEW `tools/gen_pass9_11.py`: station kit (class P: shell/openings/jigsaws/lights/windows, palettes ow/nether/end) -> jigsaw mini-complexes, size 6 / radius 64, beard_box.
  Hub 17x13x17 (start, open south entrance, 3 jigsaw faces) -> wings pool: corridor_9 (w4), corridor_15 (w3), tee, cross, corner, rooms lab/engine/archive/quarters/store (w2 each);
  fallback caps. Connector `dying_world:station` (y1, face centre, 5x5 openings). Pieces: structure/station/<site>/*.nbt, pools worldgen/template_pool/station/<site>/{hub,wings,caps}.
  - research_gate_end (overworld land): 12 END PORTAL FRAMES facing in, NO eyes; endermen spawn_override (pearls for the eyes; my addition - drop if unwanted).
  - research_gate_nether (overworld land): LIT nether portal, netherrack/nylium/magma creeping over the floor; spawn_override ZOMBIFIED PIGLINS only.
  - research_nether (nether, y 36-72, carved): complete UNLIT portal frame + flint&steel chest; moss/dirt creeping; spawn_override ZOMBIES + SKELETONS (kept dim: nether raw light <=7).
  - research_end (end_highlands): GUARANTEED ELYTRA = hub plinth chest `research_end_elytra` (end_city_treasure + an elytra pool, rolls 1); 4 persistent shulkers (shells);
    store = end_city_treasure (spire trim). Note: WORLD_SURFACE_WG projection - a start over a void column would sit at y0 (rare in highlands).
  - Sets: dying_world:research_gates (both gates, 48/18, 6 chunks from survivor villages), research_nether_stations (28/10, 3 from dying_world:nether_fortress),
    research_end_stations (20/11 triangular). Loot: chests/research_<site>_<room> (+ research_nether_portal).
- Caged persistent ALLAY specimen in the lab of both overworld gates (9-13 item, built here).

## Pass 9-12 (2026-11-15) - monument / trial chamber / ancient city REPLACEMENTS (same kit; run after 9_11)
- NEW `tools/gen_pass9_12.py` (palettes sea/proving/sculk; `fill` = water for the sunken site; windows/pipes flags):
  - dying_world:sunken_research_lab (deep oceans, OCEAN_FLOOR_WG, water-filled prismarine + blue plating): 1 persistent ELDER GUARDIAN in the hub (wet sponge, tide trim 20%),
    guardian spawn_override (prismarine), wet sponge blocks, chests = underwater_ruin_big + sponge/prismarine pool (+ tide trim 1/6 in stores). Set 32/5 triangular.
  - dying_world:proving_grounds (underground -40..-16, encapsulate, tuff/copper/rusted plating): BREEZE SPAWNER wind-tunnel room (w3) (breeze rods, wind charges),
    vault_room (w2) + hub: VAULT blocks with config nbt (normal: chests/trial_chambers/reward + trial_key; ominous: reward_ominous + ominous_trial_key -> heavy core/mace,
    flow/bolt trims). Keys: supply chests (vanilla trial_chambers/supply + key pool), breeze chest (1-2 keys, 50% ominous key). Set 34/12.
  - dying_world:sculk_research_site (deep_dark, y -45..-30): deepslate station overgrown by sculk (sculkify: veins/sensors/shriekers can_summon=true), reinforced-deepslate gate +
    catalyst in the hub; chests = vanilla ancient_city (quarters = ancient_city_ice_box): echo shards, swift sneak, ward/silence trims, disc 5 fragments. Set 24/8.
- UNVERIFIED in game: vault `config` nbt (VaultConfig codec: loot_table + key_item) - if vaults show the default trial-key reward it still works, only the ominous path differs.
- 9-8 map tags retargeted: ocean explorer map -> sunken_research_lab, trial-chamber map -> proving_grounds.

## Pass 9-13 (2026-11-15) - last walkthrough holes
- NEW `tools/gen_pass9_13.py` (run after 4_3a, 5_1, 9_11, 9_12): DIG SITES dig_site_arid (concrete_pad_arid biomes) / dig_site_temp (concrete_pad_temperate), set dying_world:dig_sites 40/14:
  terraced 3-deep pit (walkable steps) with suspicious sand/gravel -> vanilla archaeology tables (arid: desert_pyramid + ocean_ruin_warm = SNIFFER EGGS; temp: trail_ruins common/rare
  = sherds, RELIC disc, wayfinder/raiser/shaper/host trims + ocean_ruin_cold), tent, survey scaffold, lantern posts; camp chest = guaranteed BRUSH; finds barrel = desert_pyramid
  (DUNE trim) / jungle_temple (WILD trim) chest loot. start_height -4 (pit below ground).
- Trims: SENTRY -> scavenger_outpost chest pool (25%), VEX -> scavenger_stronghold_treasure pool (15%) (pools tagged dw_marker, re-run safe).
- Walkthrough gaps now all covered: elytra/shulkers/spire (End station), sponge/tide/prismarine (sunken lab), mace/breeze/wind charge/keys/flow/bolt (proving grounds),
  echo shards/swift sneak/ward/silence/disc 5 (sculk site), sniffer eggs/sherds/relic/dune/wild/trail trims (dig sites), allays (gate labs), sentry/vex (scavenger loot),
  heart of the sea (drowned, 9-10), spawners (mineshaft, 9-9). Jungle/mountain/dark-forest biomes still have no settlements (deliberate).
- REGEN ORDER (tail): ... 9_6, 9_7, 9_8, 8_9, 9_9 (after 4_2b), 9_10, 9_11, 9_12, 9_13, build, coherence_audit.
- TEST (one at a time, move 500+ blocks between): `/place structure dying_world:research_gate_end` (fill 12 eyes -> portal), `research_gate_nether` (portal lit, zombified piglins),
  in the nether `/place structure dying_world:research_nether`, in the End highlands `research_end` (hub chest = elytra, shulkers), `sunken_research_lab` in a deep ocean,
  `proving_grounds` underground (vault + key, breeze spawner), `sculk_research_site` in deep dark, `dig_site_arid` / `dig_site_temp` (brush the suspicious blocks).

## Pass 9-14 (2026-11-15) - scavenger stronghold buildings back
- USER: 'scavenger fortress no longer spawns with buildings'. CAUSE: since 8-11 (donors = big plains houses only) the stronghold house copies are 13-19 deep, but the
  stronghold still used copies of the vanilla 16x16 zombie streets: their entrance jigsaws sit inside the street box, so a house must fit in the leftover box -> nothing fit.
- NEW `tools/gen_pass9_14.py` (after 5_1/5_2/9_3): stronghold streets = the 9-3 NARROW street generator (houses placed outside the street box), worn palette (coarse dirt/gravel/
  cobble), scavenger junk on the verges (crates/drums/barbed wire), lamp posts; jigsaws -> scavenger_stronghold/{streets,houses,decor}; fallback barricades. Old vanilla copies deleted.
- REGEN ORDER: ... 5_1, 5_2, ..., 9_3, 9_14 (any time after those), ... build.
- Test: `/place structure dying_world:scavenger_stronghold` 2-3 times (move 500+ blocks): houses (plain + fortified) along the streets, piglins, barricade dead ends.

## Pass 9-15 (2026-11-15) - research stations REBUILT AS VILLAGES
- USER on 9-11: stations looked like above-ground mineshafts, entrance went straight to the portal, Rust & Rebar was the main material - not what was asked
  (central research building + smaller buildings like a village, fortress/end-city feel, R&R as flavor). Agreed redesign, user: 'go ahead'.
- NEW `tools/gen_pass9_15.py` (run after 9_11, which still provides loot tables, biome tags, sets; 9_15 deletes 9_11's corridor pieces for the 4 stations and
  rewrites their pools + start pool). Uses savanna_kit B (gradient engine) with new RAMPS alch_ow / alch_nether / alch_end and the 9-3 narrow street generator.
  - START = research hall 25x27x25: alchemist keep (stone base -> plaster/brick, timber frame, gable roof, NE tower with ladder + top floor, R&R chimney stack).
    South 3x3 archway -> ENTRY HALL (brewing benches + cauldrons, bookshelves, long table with candles + lectern, R&R distillery/pipes, lab + archive chests)
    -> partition wall doorway -> INNER SANCTUM at the back with the portal (gate_end frames / gate_nether lit portal / nether unlit frame + flint&steel chest /
    end elytra plinth + 4 shulkers) + store chest. Street jigsaws on all 4 sides.
  - streets: per-side palette; overworld stone-paved with herb verges + rare R&R junk; nether = rigid nether-brick causeways with fence railings + soul lanterns;
    end = purpur walkways with iron-bar railings. Dead ends = wall_end (wall + gate + post lanterns).
  - outbuildings (pool buildings): workshop (brewing; ALLAY cage in the overworld gates), apothecary + herb garden (berries/flowers | nether wart on soul sand |
    chorus flowers on end stone), library tower (taller in the End), quarters, storehouse, BOILER HOUSE (the dieselpunk one: furnaces, pump, gas, pipes, R&R smokestack),
    watch post. R&R share of all station blocks ~1.2% (flavor only).
  - structure: size 5, radius 64, beard_box; nether start y 40-70. Spawns/sets/loot unchanged from 9-11.
- REGEN ORDER (tail): ... 9_11, 9_12, 9_13, 9_15, 9_14, build, coherence_audit.
- TEST: `/place structure dying_world:research_gate_end` (and gate_nether; nether one in the nether; end one in the End highlands): hall in the middle, walk in
  through the entry hall to the sanctum, streets with outbuildings around, wall ends.

## Pass 9-15b (2026-11-15) - stations smaller, fuller, dimension palettes, End return portal
- USER on 9-15: 'too tall and too empty', 'palette should borrow from their representative dimension, not stark white', couldn't find the portal in the End station
  (there was none - only the elytra plinth).
- `tools/gen_pass9_15.py` rewritten: hall 21x19 footprint (was 25x25), 5-high walls (was 8), ridge y14, tower 15 (End 19) -> 20/24 tall (was 33); entry hall furnished
  (brewing benches + cauldrons, bookshelves + chiseled shelves, lectern, two work tables, carpet runner, distillery, 3 lanterns); sanctum with pillars + 2 lanterns.
  Outbuildings 4-high walls (10 tall, library 14/17): workshop (brewing, cauldron, crafting, smithing, anvil; allay cage in gates), SPECIMEN GARDEN (potting shed +
  chorus on end stone for gate_end/end, nether wart on soul sand for gate_nether/nether), library (2 floors), quarters (4 beds + nightstands + rug), storehouse, boiler, watch post.
- Per-SITE ramps: st_gate_end (deepslate + end stone bricks, purpur trim, obsidian beams, deepslate-tile roof, purpur ridge), st_gate_nether (stone/deepslate base ->
  nether brick/red nether brick, crimson timber, nether-brick roof), st_nether (blackstone/basalt -> nether bricks), st_end (obsidian base -> end stone bricks -> purpur, purpur roof).
  No white terracotta any more. Street palettes per site (deepslate/end-stone paving; blackstone/nether brick paving with crimson/warped roots; nether causeways; End walkways).
- END station sanctum: 12 EMPTY end portal frames (fill with eyes -> portal back to the overworld), elytra chest on an obsidian plinth beside it, 4 shulkers.
- structure: size 4 (was 5), radius 56.

## Pass 9-16 (2026-11-15) - overlap fix: placement tiers
- USER: overlaps between villages and smaller structures (and inside the End station). CAUSE: 25 independent surface structure sets; vanilla never keeps different
  sets apart, the only guard was a 3-8 chunk exclusion from survivor villages (village pieces reach 5 chunks). Nothing kept abandoned villages/hamlets/stronghold/gates/
  outposts/cabins/wells... apart from each other.
- NEW `tools/gen_pass9_16.py` (run LAST before build): `dying_world:settlements` 22/11 (5 survivor villages w12, 6 abandoned villages w8, 6 hamlets w12, stronghold w40,
  2 research gates w20) and `dying_world:landmarks` 11/5 with exclusion 7 chunks from settlements (36 small/medium surface structures, weights ~ old densities).
  One structure per grid cell per set; biome misses fall through to the next weighted pick. proving_grounds + sculk_research_site exclude industrial_mineshafts (8),
  sunken lab excludes shipwrecks (4), road_signs + industrial_mineshafts exclude settlements. 23 old set files deleted.
- Expect slightly fewer settlements (~75%) and landmarks (~70%) than before; tune spacing in 9_16 if the world feels empty.
- Placement only affects NEW chunks: test in a new world (or far-out chunks).
- REGEN ORDER (tail): ... 9_11, 9_12, 9_13, 9_15, 9_14, 9_16, build, coherence_audit.

## Pass 9-17 (2026-11-15) - fluid pipe states
- USER screenshot: pipes spawned with wrong states. CAUSE: reference/rustandrebar_blockstate_props.json lists only 'true' for rusted_fluid_pipe sides (multipart blockstate),
  so 9-11/9-12/9-15 set all six sides true (stubs everywhere). Real values are true/false.
- NEW `buildkit.connect_pipes(t)`: each pipe side = true toward another pipe or a pump/drum/tank/inline pump; one link -> continues straight through; lone pipe -> vertical.
  Applied in gen_pass9_11 P.save (also covers 9-12 sunken/proving/sculk) and gen_pass9_15 (hall + outbuildings). Result: straight runs, corners and tees only.
- NOTE for future passes: any R&R block whose props index shows a single value per side is multipart -> compute states, never copy the index.
- REGEN ORDER (tail): ... 9_11, 9_12, 9_13, 9_15, 9_14, 9_16, build.

## Pass 9-18 (2026-11-15) - NETHER FORTRESS REMOVED, roles replaced (user: 'do 1 and 2')
- Fortress-only items before: blaze rods (rare chest only), wither skeletons (none), rib trim (none). Nether wart already covered (gardens, chests).
- NEW `tools/gen_pass9_18.py` (after 9_15, before 9_16):
  (1) nether research station: BLAZE CONTAINMENT building (buildings pool w3: iron-bar cage, blaze spawner on magma, desk, chest research_nether_containment =
      vanilla nether_bridge + rib pool); station spawns now zombie 3 / skeleton 3 / WITHER SKELETON 2; rib pool (15%) in research_nether_store.
  (2) NEW dying_world:nether_foundry (set nether_foundries 26/9, nether biomes, start y 36-60, terrain none, rigid, size 6 / radius 80): dieselpunk foundry on
      BRIDGES - every piece has its deck at local y12 on nether-brick columns, empty space = structure_void (terrain kept), walkway air (tunnels through netherrack).
      Pieces: hall (start: blast furnaces, lava cauldrons, anvil, smithing table, R&R pump/pipes/drums/cogwheel, 2 chests), bridge13 (w5), bridge7 (w3), cross (w2),
      tee (w2), BLAZE KILN (w3, blaze spawner on a fenced plinth), BARRACKS (w2, dark room), WART TERRACE (w1), caps. spawn_overrides = vanilla fortress mix
      (blaze 10, wither skeleton 8, zombified piglin 5, magma cube 3, skeleton 2). Chests dying_world:chests/foundry = nether_bridge + rib pool.
  Fortress off: dying_world:nether_fortress set deleted; research_nether_stations exclusion -> nether_foundries (4);
  `data/minecraft/advancement/nether/find_fortress.json` override: 'A Terrible Fortress' completes in the foundry (UNVERIFIED format - check the advancement in game).
- TEST (nether): `/place structure dying_world:nether_foundry` (bridges, kiln spawner, blazes/wither skeletons spawning), `/place structure dying_world:research_nether`
  (containment building), `/locate structure minecraft:fortress` should find nothing in new chunks; walk into a foundry -> advancement.

## Pass 9-19 (2026-11-15) - scavenger buildings audit: stronghold houses rebuilt from OUR houses
- USER: make sure scavenger buildings don't still reference mod structures (rs/brutos) - rebuild from our sources.
- AUDIT: outposts (all 6) = script-built (4-3a), blocks minecraft + rustandrebar only, no foreign pools. Stronghold keep/streets/barricades/decor = script-built.
  PROBLEM: the 44 stronghold houses were copies of the old worn plains houses = the kubejs custom plains house set (third-party since 8-0), and the houses pool fell
  back to the kubejs plains terminators.
- NEW `tools/gen_pass9_19.py`: 26 houses = our 13 ruined plains houses (9-1/9-6) x plain/fort through gen_pass5_2.build() (immune piglins, fort layer: corrugated roof
  patches, boarded windows, rooftop lookout + floodlight + crossbow piglin, scrap + loot barrel). Floor level forced to y0 (5-2's detector skips y0 and would have filled
  the walking layer). Fallback minecraft:empty. Old copies deleted.
- Remaining non-own refs in scavenger structures: only vanilla (plains_lamp_1 decor + zombie_plains processor). Whole-pack pool scan: no kaisyn/brutos/vsrevamped/
  gearwrights refs anywhere. Survivor villages still use the kubejs-provided OVERRIDES of vanilla-named minecraft:village/{plains,desert,savanna}/terminators and the
  savanna town centers (vanilla ids, contents from the user's kubejs data) - candidates for the next replacement pass.
- REGEN ORDER: 5_2 is SUPERSEDED (its source dir structure/village/plains/houses_worn no longer exists) - run 9_19 instead (after 5_1, 9_1, 9_6, 9_14).
  Tail: ... 9_11, 9_12, 9_13, 9_15, 9_18, 9_14, 9_19, 9_16, build, coherence_audit.

## Pass 9-20 (2026-11-15) - archaeology + sniffers; last kubejs village pieces replaced
- USER: can we still get sniffers? build better suspicious-sand rewards into fitting structures (the vanilla ones are off); remove the last kubejs bits referencing rs/brutos.
- Sniffers before: only via vanilla ocean_ruin_warm table on 1 in 4 blocks of arid dig sites (rare). Now: eggs in OUR tables on land and sea.
- NEW `tools/gen_pass9_20.py` (after family gens 9_1/9_3/9_4/9_5/9_6 + 9_12 + 9_13; BEFORE 9_19):
  (A) loot_table/archaeology/{ruins_common (sherds ~1/3, emeralds, nuggets, seeds, candles, copper, rebar, name tag, sniffer egg ~2%), ruins_rare (wayfinder/raiser/
      shaper/host/dune/wild trims, relic disc, sniffer egg ~9%, burn/danger/heartbreak/howl sherds, diamonds, enchanted book, golden apple), desert_dig (desert sherds,
      tnt/gunpowder, dune trim, sniffer egg ~5%), seabed (ocean sherds, sniffer egg ~15%, prismarine, nautilus)}.
  (B) suspicious blocks (supported cells, not next to jigsaws, re-run safe): every RUINED house of the 5 families (3 in the open yard ground; desert sand/desert_dig,
      others gravel ruins_common 85% / ruins_rare 15%), every abandoned street piece (2), wells (2 silt cells at the shaft bottom, under water), sunken lab hub
      (5 seabed sand beds), dig sites switched to our tables (arid: desert_dig/ruins_rare/seabed; temp: ruins_common/ruins_rare/seabed). Stronghold houses inherit (9-19).
      Totals: ruins_common 285, desert_dig 68, ruins_rare 67, seabed 13 (template cells).
  (C) survivor villages no longer use ANY kubejs village content: start pool dying_world:<fam>/town_centers (17x17 plaza: roofed well, BELL, 2 market stalls,
      benches, 4 lamp posts, 2 villager + 1 golem jigsaws, 4 street exits; family paving), streets/houses fallback dying_world:<fam>/street_ends (fence + gate),
      and our content written into minecraft:village/<fam>/{villagers (family-type unemployed, babies, nitwit), decor (lamp, hay/barrel stack, planter, bench, crates)};
      golem = dying_world:village_iron_golem. The old savanna town_centers override deleted.
  (D) datapack_imported purged of every file mentioning brutos/vsrevamped/repurposed (5 *_library house NBTs with vsrevamped loot, 3 old street pools).
- VERIFIED: install zip has 0 brutos/vsrevamped/repurposed/kaisyn references and ships 0 data/minecraft/structure NBTs (all village pieces are ours).
- REGEN ORDER (tail): ... 9_11, 9_12, 9_13, 9_15, 9_18, 9_14, 9_20, 9_19, 9_16, build, coherence_audit.
- TEST: /place structure dying_world:village_plains (new plaza with bell + stalls, gated street ends, villagers), abandoned_village_* / abandoned_ruin_* (brush the
  gravel in yards and streets), a well (brush the shaft bottom), dig_site_temp/arid, sunken_research_lab hub beds -> sniffer eggs.

## USER DECISIONS (2026-11-15) - variants audit
- Build: rare house styles (all 5 families), biome strongholds, derelict station + foundry variants. Not now: single-structure biome variants (lighthouse/cabin/smithy/watchtower).
- Rebuild ALL 6 gearwrights-derived sets as ours (swamp abandoned set + 5 landmarks). (Correction to 9-19: its 'no gearwrights refs' scan only covered our own pools.)

## Pass 9-21 - rare house styles  (`tools/gen_pass9_21.py`, after family gens, before 9_20)
- 2 rare ramps per family, full roster, lived + ruined: plains r_brick / r_mossy, taiga r_darklodge / r_stave, snowy r_icehouse / r_deepslate, desert r_redpueblo /
  r_bandadobe, savanna r_redmud / r_stonehacienda. ~9% of village houses, 8-10% of ruins (existing weights x4 / x10; originals kept in tools/state/rare_meta_<fam>.json,
  NOT in the datapack - a .json inside worldgen/ would be loaded as a pool).
## Pass 9-22 - biome scavenger strongholds  (`tools/gen_pass9_22.py`, after 9_20/9_14/9_19, before 9_16)
- scavenger_stronghold_<fam> x5: same keep/streets/barricades/decor (copied, jigsaw pools retargeted to scavenger_stronghold/<fam>/*), houses = that family's ruined
  houses (incl. rare styles + dig spots) through 5_2.build; street ground tinted per family; biomes = village_<fam> tag. Generic stronghold kept (other biomes).
  Settlements: generic w10 + 5 x w6. Woodland explorer map tag += the 5.
## Pass 9-23 - derelict variants  (gen_pass9_15 main now builds ("", lived) and ("_derelict", ruined); `tools/gen_pass9_23.py` after 9_15/9_18)
- research_<site>_derelict x4: ruined finish (wear, beds->carpet, half the standing lanterns, cobwebs), unlit street post stubs, undead spawns (gate_end zombie/skeleton/
  enderman; gate_nether zombie/skeleton/zombified piglin; nether zombie/skeleton/wither skeleton; end none). Portals/elytra kept. Gates in settlements w4 each;
  nether/end station sets 4:1. 9_18 also adds the blaze containment to the derelict nether station.
- nether_foundry_derelict: furnaces out, lava cauldrons empty, half the soul lanterns gone, cracked bricks, cobwebs; wither skeleton 12 / skeleton 4 / blaze 3 /
  magma 2. nether_foundries 4:1.
## Pass 9-24 - gearwrights structures rebuilt as ours  (`tools/gen_pass9_24.py`, after 9_21, before 9_16)
- SWAMP abandoned ruin/hamlet/village: 14 stilt houses (7 builders x swampwood/swampstone ramps, ruined) raised 3 on mangrove-log posts (yard -> plank deck, only posts
  touch the marsh), ladder from the street; boardwalk street set (mangrove/spruce planks, mud verges); terrain_adaptation none.
- LANDMARKS: burnt_homestead (dogtrot/creole/barn), burnt_manor (schoolhouse/courtyard), burnt_watchtower (tower) in a 'burnt' ramp + scorch pass; ruined_chapel
  (chapel, r_mossy, ruined); collapsed_minehead (fieldstone shed, timber headframe, R&R winding wheel, rails, caved-in shaft). structure/landmarks/*, pools landmarks/<name>.
- VERIFIED: install zip ships 0 gearwrights structure/pool files.
## Mob Rules fix (2026-11-15) - zombified piglins at the nether gate
- CAUSE: kubejs/data/incontrol_port/mobrules/no_surface_hostiles.json blocked every natural hostile spawn at Y>=57 (except pillager/enderman) in EVERY dimension;
  zombified piglins are hostile (Zombie -> Enemy). It also blocked nether spawns at Y>=57 (foundry blazes/wither skeletons, nether station, ghasts).
- FIX (in kubejs_base, ships in kubejs_data.zip): + "dimensions": "minecraft:overworld", + "none_of": [{"structures": [research_gate_nether(+_derelict),
  research_gate_end(+_derelict)]}] (Mob Rules Conditions: dimensions / structures / none_of, verified in github.com/kragnoth/mobrules Conditions.java).
- Still blocked on purpose (unchanged): undead from abandoned settlement/landmark spawn_overrides at Y>=57. To allow them too, use "structures": "dying_world:*".
- REGEN ORDER (tail): ... 9_11, 9_12, 9_13, 9_15 (live + derelict), 9_18, 9_23, 9_21, 9_24, 9_14, 9_20, 9_19, 9_22, 9_16, build, coherence_audit.

## Pass 9-25 (2026-11-15) - the user's CUSTOM CREATE MILLS restored + style-cleaned
- USER: the Create windmills/watermill are custom built by the user (safe to use); check style, clean if needed; re-add these lost structures in the next release.
- FOUND: kubejs_base/data/gearwrights/lithostitched/worldgen_modifier/create_*.json (user's) still shipped, but the 5 LIVED NBTs (gearwrights:village/<fam>/windmill,
  desert/watermill) were missing from the data (lost in the 8-x splits; the 7-2 project zip lacks them too) -> recovered from reference/structures_nbt.zip into
  `reference_custom/` (+ abandoned/burnt). Abandoned modifiers targeted vanilla zombie-village pools our villages never use.
- NEW `tools/gen_pass9_25.py`: desert jungle wood -> spruce; abandoned versions get the deleted structural blocks back as WORN versions of the lived block
  (plains 44, taiga 43, snowy 22, savanna 39, desert 11; torn sails/crops/half the lanterns stay); NBTs written to datapack/data/gearwrights/structure/village/<fam>/.
  Modifiers (kubejs_base): lived weight 1 -> 20 (pools were x4 in 9-21), abandoned retargeted to dying_world:<fam>/ruined_houses at 8. Burnt versions shipped but unused.
- gen_pass8_9 (lantern rule) now also covers datapack/data/gearwrights/structure (1 lifted, 4 -> torch, 1 removed).
- REGEN ORDER (tail): ... 9_21, 9_24, 9_14, 9_20, 9_19, 9_22, 9_25, 9_16, 8_9, build, coherence_audit.
- TEST: /place structure dying_world:village_plains (several; a windmill should show up in roughly 1 in 4 villages), abandoned_village_* for the worn mills.

## Pass 9-26 (2026-11-15) - FULL THEME PASS over every shipped structure
- USER: full thematic pass on all structures; sent the mods list + tarbound-0.67.0-alpha.jar.
- NEW `tools/theme_audit.py` -> `docs/theme_audit.md`: per structure, follows start pool -> pools -> jigsaw pools in NBTs (+ lithostitched additions, Tarbound
  dry_land layouts read from the jar extracted to /home/claude/tarbound_jar) and scores R&R share, stark-white share, banned materials (cherry, bamboo, coloured
  concrete, bright wool), low hanging lanterns, lights in abandoned sites, loot-table existence (datapack/imported/kubejs_base/jar), block namespaces, DataVersion,
  missing templates. RESULT after fixes: every structure passes; only code-built shipwrecks (vanilla) and road signs (Supplementaries) not scored.
- FINDINGS FIXED (`tools/gen_pass9_26.py`, after 9_21/9_24/9_25, before 9_19/9_22): ABANDONED = DARK - 363 lights out in 205 ruined/abandoned NBTs (ruined houses
  of all families incl. rare + swamp, abandoned Create mills): hanging lanterns removed (chain stays), standing lanterns/torches removed, campfires out. They broke
  our 9-8 rule and suppressed the undead spawns. Scavenger strongholds inherit dark houses (lookout floodlights remain).
  Savanna plaza stall wool lime -> brown (gen_pass9_20 WOOL).
- CHECKED OK: Tarbound structures (charnel crypt = bone/deepslate/blackstone + candles/votive racks; researcher/trapper/burned cabins; drowned radio; wayside
  shrine) fit; their own sets are disabled, ours place them. Every block namespace in shipped NBTs is minecraft/rustandrebar/create/tarbound (all in the mods list).
  Every mod structure set in the reference is disabled (vsrevamped sets are from the removed datapack, not installed). Industrial sites (mineshaft, outposts,
  pads, proving grounds) are R&R-heavy by design; stations/strongholds 1-3% R&R.
- OPEN (subjective, user to decide): lighthouse = 17% white terracotta in red/white stripes (classic look, previously approved) vs our no-stark-white rule.
- REGEN ORDER (tail): ... 9_21, 9_24, 9_25, 9_26, 9_14, 9_20, 9_19, 9_22, 9_16, 8_9, build, coherence_audit, theme_audit.

## Pass 9-27 (2026-11-15) - Create mills re-skinned in our gradient style (user screenshot of an abandoned windmill)
- USER: abandoned windmill = random checkerboard block mix + cobwebs all over the outside; 'redo the ruin phase, rebuild to match our tone'.
- NEW `tools/gen_pass9_27.py` (after 9_25, before 9_26 + 8_9): keeps the user's geometry + all create:* machinery; converts every building block to a savanna_kit
  ROLE (stone/plank full -> wall with ONE gradient band foot->70% height, y0 decks + open-topped interior blocks -> floor, logs -> trim, wooden stairs/slabs ->
  roof/roof_slab, props kept) and finishes with per-family mill ramps (no white; plains cobble->stone bricks->spruce->oak + dark oak roof, taiga mossy->spruce,
  snowy cobble->spruce, savanna cobble->packed mud->acacia, desert sandstone->smooth sandstone). LIVED = finalize('lived'); ABANDONED = finalize('ruined') from the
  same lived source (worn/mossy, nothing missing, only interior-corner cobwebs) + 60% of the sails torn, glue entity removed; dark via 9_26.
  The old checkerboard abandoned NBTs (reference_custom/*_abandoned) are no longer used; burnt versions still unused.
- REGEN ORDER (tail): ... 9_25, 9_27, 9_26, 9_14, 9_20, 9_19, 9_22, 9_16, 8_9, build, coherence_audit, theme_audit.

## Pass 9-28 (2026-11-15) - biome-matched single structures (best bang only)
- USER: lighthouse red/white stays (it's a lighthouse). Fix single designs where it pays off, don't overdo it.
- NEW `tools/gen_pass9_28.py` (after 8_2/8_4, before 9_16): abandoned_smithy now temperate/cold/wild only + NEW abandoned_smithy_arid (material swap of the same
  2 builds: cobble/bricks -> sandstone family, yard -> sand, vines/moss -> dead bush/none; spruce timber kept) in the arid biomes.
  abandoned_cabin was a RANDOM pick of oak/spruce/dark oak in any of its biomes -> abandoned_cabin (spruce: taigas incl. snowy), abandoned_cabin_oak (forest/birch/
  flower forest), abandoned_cabin_dark_oak (dark forest). Watchtower left as is (its biomes are all similar).
- 9_16 landmarks: cabin 8 / cabin_oak 5 / cabin_dark_oak 2, smithy 2 / smithy_arid 1 (a comment typo briefly dropped 4 landmarks - fixed; landmarks set = 39).
- REGEN ORDER: 9_28 any time after 8_2/8_4 and before 9_16.

## Pass 9-29 (2026-11-15) - 4 landmarks out, 3 survivor landmarks with master characters in
- USER: abandoned watchtower, burnt homestead, burnt manor, burnt watchtower don't fit the flow -> remove; replace with fitting buildings, maybe a villager/zombie
  with flavor, e.g. a master-level villager with rare trades.
- NEW `tools/gen_pass9_29.py` (after 9_24 + 8_5, before 9_16): deletes the 4 (structure json, biome tag, pools, NBTs incl. structure/watchtower) and builds:
  hermit_cottage (creole cottage, fieldstone, lit; temperate+cold) - 'Old Hermit' master CLERIC: 12em->2 ender pearls (6), 10em->4 XP bottles (6), 24em+book->Mending (1),
    28em->totem (1), 30em->heart of the sea (1).
  tinker_workshop (forge, r_brick, rusted drums; any land) - 'Tinker' master TOOLSMITH: 32em+diamond->netherite upgrade template (1), 26em->diamond pickaxe Eff IV/Unb III (1),
    14em->coast trim (1), 18em->wild trim (1), 6em->name tag (3), 4em->8 rebar bundles (6).
  plague_house (dogtrot, fieldstone, RUINED, windows boarded, doors -> planks/bars, unlit, undead spawns; temperate+wild) - 'Quarantined Scholar' ZOMBIE VILLAGER
    master LIBRARIAN in the sealed west pen: cure (weakness + golden apple) to trade 20em+book->Mending, 22em+book->Protection IV, 18em+book->Unbreaking III (2),
    6em->name tag (3), 12em->2 golden apples (2).
  Characters: PersistenceRequired, Xp 250, VillagerData level 5, fixed Offers (1.21 MerchantOffer NBT), CustomName. Hermit/tinker built 'base' (no extra villager jigsaw).
- Landmarks set: watchtower 6 / homestead 9 / manor 3 / burnt watchtower 6 -> hermit 8 / tinker 6 / plague 8 (38 structures).
- UNVERIFIED in game: enchanted items via 'components' in Offers NBT (book stored_enchantments, pickaxe enchantments) - check the trade screens.
- REGEN ORDER (tail): ... 9_24, 9_29 (after 8_5 too), ..., 9_16, 8_9, build.

## Pass 9-30 (2026-11-15) - user's loot re-tune adopted as the baseline (RC 1 sync)
- USER sent their live kubejs/data after fixing chest loot rates "and a few other things". Diff vs our last kubejs_data.zip: ONLY 35 dying_world chest loot
  tables changed (fixed roll counts instead of ranges, lower maxima, some `minecraft:empty` entries) - concrete_pad*, digsite_*, mineshaft_*, research_* (all stations),
  scavenger_outpost/scraps, scavenger_stronghold_* (4), smithy. No files added or removed. (Other edits were outside kubejs/data.)
- NEW layer `user_overrides/data/` (+ README): the user's hand edits; `tools/build.py` copies it over datapack/ BEFORE validation, so generator re-runs can't undo them.
  RULE: to change one of those files, edit the user_overrides copy and log it here.
- Rebuilt: dist/kubejs_data.zip is byte-identical to the user's uploaded data folder (diff -rq clean).
- Pack state: 13 structure-only jars removed by the user (watchtowers, abandoned_cabins, createnewbeg, formations x3, strayed-fates-forsaken, t_and_t+cristellib, hearths,
  lootintegrations_yungs+YungsApi, lootintegrations_dnt); their disabled structure_set overrides are now orphans (harmless). Logs: clean load, 0 KubeJS errors,
  no dying_world/gearwrights errors. Excalibur Create addon stock_link/stock_ticker fix shipped as a separate resource pack (GH_Excalibur_Create_Fix.zip).
- NEXT: in-game verification sweep of the UNVERIFIED list (below), then optional cleanup pass 9-31 (strip orphan namespaces of removed jars).
  Unverified: vault config nbt (proving grounds), find_fortress advancement in the foundry, enchanted trade Offers (hermit/tinker/plague scholar),
  End station over the void, foundry bridges, swamp stilt houses, density after the set tiers. Open design call: burnt mills as landmarks (yes/no).

## Pass 9-31 (2026-11-15) - research gates get stronghold-style ring placement
- USER: tested 3 (hermit/tinker/plague trades) = WORKS. Nether research gates spawned way too close to spawn and too often; same for the End gates -> treat them like
  old-school strongholds (rings).
- gen_pass9_16.py: the 4 gate structures left the settlements set (they were 48 of ~240 weight = 1 in 5 settlements!) -> NEW set `dying_world:research_gates`,
  minecraft:concentric_rings distance 20 / spread 4 / count 32, preferred_biomes #dying_world:has_structure/scavenger_outpost_any, weights nether 5 / end 5 /
  each derelict 1. Rings: 1st ~880-1680 blocks (4 gates), 2nd ~2800, 3rd ~4700, 4th ~6600. A ring spot can roll either type (no guarantee of both in ring 1).
- Overlaps: settlements exclude research_gates (8 chunks); gate structures now step `strongholds` (after surface_structures), so a landmark landing on a gate gets
  overwritten by the gate. (Landmarks can only hold one exclusion zone - settlements.)
- The in-dimension stations (research_nether_stations / research_end_stations sets) are unchanged.
- Tuning knobs if needed: GATE_RINGS in gen_pass9_16.py (distance = how far, count = how many, spread = how many in ring 1).

## Pass 9-32 (2026-11-15) - FTB Quests structure tasks retargeted (found while drafting the endgame framework)
- Wilds & Ruins + Into the Depths had structure tasks that can never complete: #gearwrights:abandoned_settlements / #gearwrights:landmarks (tags gone),
  gearwrights:ruined_chapel / collapsed_minehead (now dying_world:), gearwrights:burnt_watchtower (removed in 9-29), minecraft:trial_chambers / fortress /
  bastion_remnant (sets disabled).
- gen_pass9_16.py now also writes dying_world structure TAGS: abandoned_settlements (18), landmarks (21: every landmark except ruins, wells, outposts),
  scavenger_strongholds (6), nether_foundries (2), research_gates (4).
- Quests (outside this project, shipped as GH_quest_structure_fix.zip = config/ftbquests chapters 10e207a2a56a7ab6 + 6a3d5b7fcab349ba + lang/en_us.snbt):
  Gone Quiet -> #dying_world:abandoned_settlements; Landmarks + Pathfinder -> #dying_world:landmarks; Ruined Chapel / Collapsed Minehead -> dying_world ids;
  Burnt Watchtower -> 'The Plague House' (dying_world:plague_house); Trial by Chamber -> 'Proving Grounds'; Pathfinder trial task -> proving_grounds;
  Fortress of Fire -> 'The Foundry' (#dying_world:nether_foundries); Piglin Gold -> 'Scavenger Hold' (#dying_world:scavenger_strongholds). Texts rewritten to match.
  The Stronghold quest is fine (dying_world:strongholds set still places minecraft:stronghold).
- RULE: when a structure is renamed/removed, grep config/ftbquests for its id/tag.

## Pass 9-33 (2026-11-15) - lore: journals + map trail (endgame framework, phase 1)
- USER: "build in the lore and flavor into the sites through journals/etc." Story defaults = the framework doc's first options (Gearwrights opened the gates;
  the 'draught' drawn through them bleeds the world: tar = 'the black', spirits = 'lodgers'; dry records that go wrong). First Gate 'at the Hollow' foreshadowed only.
- NEW `tools/gen_pass9_33.py` (after 9_16, before 8_9/build): 16 written books + 5 exploration maps, delivered ONLY by NeoForge GLMs (neoforge:add_table ->
  dying_world:lore/<site>), so the user's hand-tuned chest tables (user_overrides) stay untouched. Registered in neoforge global_loot_modifiers (lore_* entries
  rebuilt on every run).
  Archives (guaranteed book): gate Below/Beyond registers (+60% map -> proving grounds), proving ledger (+60% map -> sunken lab or sculk site),
  Station Below day book (+map -> foundry), Far Station observations, Listening Post transcript, Tidewell log.
  Chance books: foundry orders 35% per foundry chest, survey stake notes 40% (concrete pads), scavenger's tally 60% (stronghold 'other' chests).
  Landmarks on vanilla village tables via any_of(loot_table_id) + location_check structure: hermit (account + map -> nearest research gate = trail entry),
  plague house (quarantine notes), tinker (apprentice's notebook), ruined chapel (50% unfinished sermon); abandoned settlements 12% per chest: an unsent letter
  or a parish closure notice.
- Maps are same-dimension only (exploration_map can't cross portals). New tags dying_world:map/proving_grounds, map/far_labs. search_radius 100.
- Ties to the Occult Foundry vision on purpose: the horizon smoke ('it is not our smoke'), the midnight bell, pale groves, weakened blazes (Tarbound).
- UNVERIFIED in game: book rendering (written_book_content via set_components), the maps' locate (red X), location_check firing in landmark chests.
- 9-33 FIX (user log): all 15 lore tables failed to parse - written_book_content PAGES must be JSON-text STRINGS (flat codec), not component objects.
  Pages now json.dumps({"text": ...}). Title {"raw": ...} and the GLMs parsed fine.

## Pass 9-34 (2026-11-15) - proving grounds surface marker; lore reaches every proving/sunken site
- USER: the proving-grounds map led to an X over plain ground (site is buried at -40..-16); found no lore there.
- Lore cause: the archive is an OPTIONAL wing room (weight 2 of 27 per slot), so most proving grounds had no archive chest. Same risk for the sunken lab.
- NEW `tools/gen_pass9_34.py` (after 9_12, before 9_16): proving grounds now START AT THE SURFACE: 'headframe' = small Guild hut (tuff/copper palette,
  3-course foundation, start_height -3 on WORLD_SURFACE_WG) with an iron-bar mast + lantern above the roof (the marker), wall sign 'GEARWRIGHTS / PROVING
  GROUNDS / Crews only. / Keys by requisition.', winch, and the ARCHIVE chest (-> Proving Ledger + 60% far-labs map, guaranteed now). Floor centre = a
  scaffolding shaft: shaft_1..3 (5x16x5, scaffolding column, jigsaws shaft_down/shaft_up, final_state scaffolding) -> 9-12's hub, patched with an UP jigsaw
  at (8,12,13) + scaffolding (8,1..11,13). Hub floor ~ surface - 67. Jigsaw size 6 -> 10, max_distance 64 -> 80, terrain encapsulate -> NONE
  (encapsulate/bury would dome the hut under terrain; beard would carve caverns round the rooms; the rooms are closed shells anyway).
- 9-33: sunken lore now on archive OR lab chests (the sunken hub always has a lab chest). Sculk hub already holds its archive chest; gate/Nether/End halls too.
- REGEN ORDER: ... 9_12, 9_34, ..., 9_16, 9_33, 8_9, build. (9_12 rewrites the hub + proving json -> 9_34 must follow it.)
- UNVERIFIED in game: vertical jigsaw chain (up_north/down_north, aligned), hut on slopes, sign text.

## Pass 9-35 (2026-11-15) - underground sites grow properly + proving grounds stops landing in villages
- USER: a proving grounds was just the hub + a few side rooms (progression blocker); an abandoned village had spawned on the proving-grounds X.
- NEW `tools/gen_pass9_35.py` (after 9_12 + 9_34, before 9_16) for sunken / proving / sculk: hub doorways -> SPINE corridors (copies of corridor_9/15:
  spine_<key>_<len>.nbt, far end opens the next pool) -> JUNCTIONS pool (tee 3 / cross 2 / corner 2 / corridor_9 1, ends open the old mixed wings).
  Proving: west spine ends in the VAULT ROOM, east spine in the BREEZE TUNNEL (guaranteed unless they can't fit -> cap), north -> junctions.
  Jigsaw size: sunken/sculk 6 -> 8, proving 10 -> 12.
- 9_16: proving_grounds + industrial_mineshaft now share ONE set `dying_world:deep_sites` (random_spread 26/10, exclusion 6 chunks from settlements):
  both are surface-started and big underground, one per cell keeps them apart. Old sets proving_grounds.json + industrial_mineshafts.json are DELETED
  (user must delete them from kubejs/data too - unzip-over-top would leave them placing a second copy). Sculk site now excludes deep_sites (8).
- REGEN ORDER: ... 9_12, 9_34, 9_35, ..., 9_16, 9_33, 8_9, build.

## Pass 9-36 (2026-11-15) - sculk research site rebuilt as an abandoned DIG CAMP in an open cavern
- USER: the sculk site read as a 'weird sci-fi horror show'; wanted abandoned research buildings + mining shacks + sculk, a site built up over time then
  abandoned. Choices: OPEN CAVERN, a FEW VEINS at the edges, keep the HALF-BURIED ANCIENT GATE.
- NEW `tools/gen_pass9_36.py` (after 9_12 + 9_35, before 9_16): deletes 9-12's structure/station/sculk + its pools; writes structure/sculk_camp/ (22 pieces) +
  template_pool/sculk_camp/. terrain beard_box (cavern carved round every piece, like the ancient city), size 7, start pool sculk_camp/pit.
  pit (27x16x27): 15x15 excavation 4 deep, cut stairs (south), scaffolding towers, rim rails, dead caged lamps on fence posts, plank paths to 4 exits,
  gate = reinforced-deepslate frame half-buried in a sculk/deepslate mound + catalyst, Guild survey desk (NE rim: ARCHIVE chest = guaranteed Listening
  Post Transcript, lectern, calibrated sculk sensor, crate, barrel).
  walk_inner / walk_outer = timber-framed mine tracks (posts + cap beams every 5, boardwalk, rail); 11 / 17 / fork (fork's east side = another track);
  outer ring peters out into old caved-in mine drifts; side jigsaws -> bld_inner / bld_outer.
  Buildings (camp: planks + corrugated tin; Guild: stone brick/cobbled deepslate + weathered copper roof): shack 4, bunkhouse 3 (bunks, a skull),
  cook shack 2 (open lean-to, cold campfire), tool shed 3, Listening Post 1 (calibrated sensor, overturned table, honeycomb 'wax', archive chest),
  lab 1 (caged sculk catalyst specimen, brewing stand), mine-drift entrance 2. Loot = the old research_sculk_* tables.
  SCULK GRADIENT by ring: pit heavy (40% blocks -> sculk, veins, sensors, shriekers CAN summon), inner some (12%, veins, odd sensor), outer veins only.
- 9_35 no longer touches sculk. REGEN ORDER: ... 9_12, 9_34, 9_35, 9_36, ..., 9_16, 9_33, 8_9, build.
- Deleted from the build: data/dying_world/structure/station/sculk/ + worldgen/template_pool/station/sculk/ (user should delete them too; harmless if left).
- UNVERIFIED in game: cavern size from beard_box (carves ~12 above each floor), walkway/building fit, dead caged lamps (lit=false) look.

## Pass 9-37 (2026-11-15) - repo: modpack snapshot (RC 3)
- USER: moved the project to git (github.com/kragnoth/dying_world, main) and asked for the kubejs + config folders in it too, to retrieve major stuff.
- NEW `modpack/` = the CurseForge export 'Gearwright's Hollow RC 3' 1.0.0 (252 mods, NeoForge 21.1.262): manifest.json, modlist.html, overrides/
  (config, defaultconfigs, options.txt, icon.png, resourcepacks/HollowDead.zip, kubejs client/server/startup scripts, kubejs assets + config).
  overrides/kubejs/data is NOT stored: RC 3's kubejs/data was byte-identical to our build (diff -rq clean). usernamecache.json left out.
- The RC 3 export already contains everything up to pass 9-36 (quest structure fix, lore, sculk camp ...).

## Pass 9-38 (2026-11-15) - metal item textures brought in line (modpack assets, not the datapack)
- USER: ingots -> Excalibur style; dusts -> match Neo Vitae's flat piles; nuggets -> Excalibur nugget style (experience nuggets excluded).
- Audit (tools/textures/collect.py + analyze.py) over the textures that actually win in game: 51 ingots / 49 nuggets / 35 dusts.
- tools/textures/restyle.py recoloured the style template onto 70 textures, written to modpack/overrides/kubejs/assets/ (kubejs File Resource Pack
  sits above every resource pack, so these win): 25 ingots (IE 11, Ender IO Evolution 9, createdeco, createcasing chorium, createpropulsion platinum,
  enderio combustive metal, neovitae hellforged + demonite trim), 23 nuggets (IE 12, Ender IO Evolution 9, createdeco 2, propulsion platinum),
  22 dusts (IE 16, immersivepetroleum petcoke, arkaneworx zinc, glowstone, waystones warp dust, neovitae corrupted dust).
- Skipped: titanium:* (library textures, no items), create:copper_ingot (no such item), experience nuggets, neovitae corrupted_tiny_dust (tiny on
  purpose), cultivar:sulfur_dust (cultivar's excalibur_style pack loads ABOVE kubejs assets - change it in Cog & Cultivar itself).

## Pass 9-39 (2026-11-15) - dusts re-done richer
- USER: some restyled dusts lost a lot vs the original Neo Vitae look (straight colour transfer).
- Cause: the 9-38 template (neovitae iron_dust) has only 7 shades and rank-mapping collapsed sources to them; Neo Vitae's richest dust (copper) has 12
  shades in two hue groups (body + speckles). tools/textures/rich_dust.py redoes the 22 dusts on that template with continuous ramp interpolation:
  every output now has 12 distinct colours with accent speckles. Ingots/nuggets unchanged.

## Pass 9-40 (2026-11-15) - four dusts fixed after the v1/v2 review
- USER: keep v2 (rich dusts), fix the four weak ones. rich_dust.py FIX table: zinc trim=.25 (outline pixels dropped from the source colours, no black
  rim), wood + sulfur mono (speckles = darker shade of their own colour, no green cast), glowstone mono + contrast .75 (calmer, keeps its highlights).

## Pass 9-41 (2026-11-15) - Create's discontinued alloys get recipes + uses (modpack kubejs, not the datapack)
- USER: give the discontinued Create ingots still in game recipes and uses that fit the lore and progression.
- Found: create:chromatic_compound, create:shadow_steel, create:refined_radiance (+ create:shadow_steel_casing / refined_radiance_casing) are
  registered but have NO recipe; they only drop as rare loot (create_drops.js / loot bridge), and their only use was Create Encased's cosmetic
  sheets (#c:ingots/shadow_steel, #c:ingots/refined_radiance -> sheets -> encased machine variants).
- NEW modpack/overrides/kubejs/server_scripts/progression/50_incursion_alloys.js (switch incursionAlloys in gh_progression_config.js):
  chromatic compound = superheated mixing 3 powdered obsidian + polished rose quartz + glowstone + 250 mB tarbound:tar ('draught condensate');
  shadow steel = mixing compound + echo shard + 2 popped chorus fruit (the Beyond: End + deep dark / sculk camp);
  refined radiance = superheated mixing compound + 2 glowstone + tarbound:weakened_soul (the Below).
  Uses: hallmarked:gearwrights_seal (smith's stamp + shadow steel + refined radiance, beside nether star / dragon egg), Create's creative-only
  handheld worldshaper (mechanical crafting: 2 radiance, precision mechanism, brass, brass casing, 2 shadow steel), Create's two casings
  (item application on brass casing). Recipe ids gearwrights:incursion/*.
- NEW client_scripts/incursion_alloys_tooltips.js: one lore line each (ItemEvents.modifyTooltips).
- Not used (no way to get it): tarbound:essence_of_the_void. UNVERIFIED in game: all recipes (JEI), tooltip event name on KubeJS 2101.7.2.
- 9-41 follow-up (USER): worldshaper recipe DROPPED - Create's Handheld Worldshaper doesn't consume blocks, so a survival recipe = infinite
  blocks. Uses left: Gearwrights' Seal + the two casings (+ Encased sheets). User will pick more uses later.

## Pass 9-42 (2026-11-16) - Arcana questlines fleshed out on the world's lore (modpack quests)
- USER: read FTB Quests (1.21.1/main), Neo Vitae (1.21.1), NeoForge + MC sources; build on the existing questlines to flesh out the arcane/occult side
  using the lore built into the world. Mid-task: look at the Incision nether mod (flesh biome) and work it in if it fits.
- NEW tools/quests/gen_occult_quests.py (+ snbt.py): one-shot editor for modpack/overrides/config/ftbquests/quests (refuses a second run; ids are
  deterministic sha1 'gh-occult/<key>' with the top bit cleared). Text-level inserts keep the existing files' formatting.
  * NEW chapter 'The Incursion' (Arcana, order 2, 19 quests): Smoke on the Horizon -> The Penitent (hermit), Quarantine, The Apprentice ->
    The Gatehouse (#research_gates) -> Requisitions (proving) -> The Tidewell / The Listening Post; Station Below (#nether_stations) -> The Foundry
    (#nether_foundries) / The Wound Below (biome incision:eroded_yard) -> Those Who Stayed (3 skeleton cultists), Burial Knife; Far Station
    (#end_stations); Draught Condensate -> Steeped in the Beyond / Fired from Below -> The Guild's Own Mark (Gearwright's Seal) -> What They Opened
    (capstone: skill point, title, big table).
  * Tar and Spirits +14: weakened soul (Black Tar now also depends on it), scorched spawner, feeding the lodgers, work order, shade, ossuary, broadcast
    mast, transient antenna, sixteen candles, bottled void, and Tarbound's 4 landmarks (its own advancements).
  * Blood and Ritual +14: Scriptura Vitae, throwing dagger, blood lantern, Sigil of Holding, Green Grove, first ritual, A Crack in the Veil
    (Breaching the Edge = 'you are cutting a gate'), demonite, bloodstone x4, Magus / Dominus / Divinus orbs, crystal cluster (sculk from the dig camp),
    Aspectum Omnia. Advancement tasks use Neo Vitae's / Tarbound's own advancements (ritual activation has no item).
  * 'Beyond the Veil' description now names the third thread (The Incursion).
- Datapack: gen_pass9_16 adds structure tags dying_world:nether_stations / end_stations (live + derelict) for the quests.
- Incision: fits as 'the wound Below' (MCreator mod, injects its Eroded Yard biome into the Nether noise itself; skeleton cultists, seers, burial
  knife). Its jokey names were re-voiced in modpack/overrides/kubejs/assets/incision/lang/en_us.json (advancements, whoopie cushion -> Gas Bladder,
  voomoo doll -> Effigy).
- UNVERIFIED in game: quest book loads the new chapter; advancement/biome/kill tasks tick.

## Pass 9-43 - Guild uniques + tallow candles
- `tools/gen_pass9_43.py`: four Hallmarked uniques in `data/dying_world/uniques/` (`chance {}` = never roll naturally): Gale's Banking Shovel, Brandt's Waxed Hood, Marsh's Field Boots, The Penitent's Lamp (emerald amulet). Names/lore in `kubejs/assets/dying_world/lang/en_us.json`.
- `tools/quests/add_unique_rewards.py`: Incursion quests foundry/listening/far/opened give them via `/hallmarked generate for {p} 1 unique=<id>` (arrive Unappraised). Idempotent.
- `tarbound:candle_wax` += `incision:tallow` (optional).
- No deletions. Unverified in game.
- REGEN: after gen_occult_quests: gen_pass9_43, add_unique_rewards.

## Pass 9-44 (2026-11-16) - The Hollow: finale arena + doppelganger boss
- USER: endgame = feels like unlocking a max-tier perk, not creative items (a multi-stage creative recipe ingredient is OK). Finale may be a
  boss only if it's a clone of the player (skin + Hallmarked gear that doesn't drop) with Mob Rules bonuses, from a building + spawn point + trigger.
- Mob Rules 0.7.0 (kragnoth/mobrules): NEW `mobrules:doppelganger` (player skin incl. slim arms, copies of the player's equipped gear at drop
  chance 0, melee or bow) + `/mobrules doppelganger <player> [pos] [tag]`. The pack needs Mob Rules 0.7.0.
- `tools/gen_pass9_44.py`: structure `dying_world:the_hollow` (marker hut + mast -> 2 scaffold shafts -> 33x18x33 arena: pillar ring,
  tinted-glass mirrors, candlelit dais, ALTAR = reinforced deepslate). Set the_hollow: concentric rings distance 40 / spread 3 / count 6.
  Tag + loot table `dying_world:map/the_hollow`. Mob Rules rule `data/dying_world/mobrules/the_hollow.json` (gh_hollow tag: 300 hp, x1.5 damage,
  regen, blink/leap/pull/shield, summons 2 skeleton cultists under 30%, purple boss bar).
- modpack kubejs `server_scripts/progression/60_the_hollow.js`: Seal on the altar inside the_hollow -> doppelganger tagged gh_hollow on the
  far side of the dais (seal spent; one at a time within 64). Death -> owner + killer get stage `gh_hollow_defeated` (entity tag + KubeJS stage).
  `kubejs/assets/mobrules/lang`: "<player>'s Hollow".
- `tools/quests/add_hollow_quests.py` (idempotent): Seal quest also gives the map (`/loot give`); What They Opened: checkmark -> gamestage task.
- No deletions. UNVERIFIED in game: everything (skin render, bow pose, ring placement, structure check from KubeJS, stage task).
- REGEN: gen_pass9_44 after 9_12 (and 9_34); quests: add_hollow_quests after add_unique_rewards.

## Pass 9-45 (2026-11-16) - 'Hollowed': the endgame perk node
- USER: the end game should feel like unlocking a max-tier perk.
- `tools/gen_pass9_45.py` edits the skill tree in kubejs_base/data/kskills (the user's tree; identical to his 2026-11-16 upload):
  definition x_hollowed + skill hollowed_1 at (-800, 228), off the Occult rim. No connections, cost 0: it can't be bought and costs no points.
  Grants all three Occult keystone perks (soul_siphon, arcane_ward, hex) whatever path was taken, +4 max health, +1 luck, +10% magic
  protection, +2 lodestone magic damage, +5% cooldown reduction. required_mods as the occult keystones.
- kubejs 60_the_hollow.js: the doppelganger's death runs `/puffish_skills skills unlock <player> kskills:skill_tree hollowed_1` for owner +
  killer; on login it re-unlocks it for anyone tagged gh_hollow_defeated (a respec locks every node).
- Not done (offered): a 'Hollow Mark' item for a multi-stage creative recipe.
- No deletions. UNVERIFIED in game.

## Pass 9-46 (2026-11-16) - the Occult Foundry vision becomes the Hollow's mark
- USER decisions: before the Hollow the world is normal; killing your copy locks you into occult_foundry; the Escapement (later) frees you;
  after that the vision is a toggle that needs an item (Foundry Lens); harsher spawns while locked; Hollowed's perks only work in the vision;
  repeatable Escapements; late journals scrambled, revealed in the vision (book-screen/lang approach); vision items must be data-driven
  (the mod is for any pack).
- NEW Wasteland Vision 0.24.0/0.24.1 (kragnoth/Wasteland-Vision): clients report their vision, players carry tag wv_<vision>;
  /wastelandvision lock|unlock|status (saved per player); vision.json "key_item" + "items" (JSON-declared items, "key": true);
  reveal/<lang>.json = keys that read differently while the vision is on. NEW Mob Rules 0.7.1: spawner "players" has_tags/lacks_tags.
- `tools/gen_pass9_46.py`: wastelandvision-server.toml forceVision=false (config/ + NEW defaultconfigs/ copy, so new worlds get it);
  client startActive=false; occult_foundry/vision.json "items": foundry_lens (head, key, rare) + texture in the vision folder's assets;
  datapack mobrules/foundry_haunting.json (skeleton cultist spawner, dark overworld spots, only around players tagged wv_occult_foundry +
  gh_hollow_defeated and not gh_escaped); skill tree: x_hollowed keeps the stats, the 3 perks move to x_hollow_sight / hollow_sight_1.
- kubejs 60_the_hollow.js: the kill locks owner + killer into occult_foundry; escapeFoundry(player) (tag gh_escaped, unlock, give the lens)
  is ready for the Escapement pass; Hollow Sight is unlocked/locked once a second when the wv_occult_foundry tag changes.
- EXISTING WORLDS: edit <world>/serverconfig/wastelandvision-server.toml (forceVision = false) by hand.
- No deletions. UNVERIFIED in game.

## Pass 9-47 (2026-11-16) - the vision path, final
- USER: start in the vision (locked on until the Hollow); killing the doppelganger keeps it always on; the Escapement (creative-recipe
  item) turns it off and gives the lens to see into it again (for more crafting items).
- `tools/gen_pass9_47.py`: forceVision = true / forcedVision = occult_foundry (config + defaultconfigs), startActive = true (reverses 9-46).
- Wasteland Vision 0.24.3: `/wastelandvision release <players>` frees a player even under forceVision (0.24.2 dropped the built-in lens:
  the mod hardcodes no items). kubejs escapeFoundry() now uses release (+ gh_escaped tag + Foundry Lens).
- No deletions. Existing worlds: <world>/serverconfig/wastelandvision-server.toml keeps whatever it had (forceVision = true is right).

## Pass 9-48 (2026-11-16) - Foundry Residue, the Escapement chain, creative items
- USER decisions: residue starts at the tinker's workshop / research gate and ramps with progress; creative items tier 1 = creative motor
  (+ gear motor swap), creative fluid tank (+ fluid vessel swap), creative blaze cake, creative physics staff, Eternal Creative Power,
  IE Creative Accumulator; tier 2 = creative crate, creative bookshelf, Neo Vitae creative activation crystal, Ender IO creative
  batch/stack upgrades; thrusters left out; Create Encased's creative casing gets a cheap railway-casing-level recipe (cosmetic only);
  released players get Distilled Residue + repeat Hollow fights (Echo).
- modpack kubejs: startup hollow_items.js (gearwrights: foundry_residue, distilled_residue, incomplete/unwound/bled/wound_movement,
  escapement; placeholder textures from tools/textures/hollow_items.py - redo in Excalibur style), gh_progression_config hollowEndgame;
  client hollow_items_tooltips.js; server 70_escapement.js (sequenced assembly -> Neo Vitae altar T4 50k LP -> spout 500 mB essence of the
  void; creative recipes = mechanical crafting with one Escapement; creative activation crystal = altar T5 100k LP from an Escapement;
  swaps; creative casing = brass casing + amethyst shard, replaces createcasing's chorium recipe); 75_foundry_residue.js (tiers from
  gh_residue_<n> tags, only while tagged wv_occult_foundry; deepslate + undead; revenants 1-2 at tier 5; distilled for gh_escaped);
  60_the_hollow.js: altar takes a Wound Movement -> Escapement (first: releases you; after: also costs 4 Distilled Residue), a released
  player with the lens on calls an Echo (gh_hollow_echo: 12 residue, 4-6 distilled, /hallmarked generate 2); first copy drops 8 residue;
  Hollowed adds gh_residue_5. FIX: 50_incursion_alloys.js tar ingredient type fluid_stack -> neoforge:single (Create 6 format).
- `tools/gen_pass9_48.py`: datapack mobrules/the_hollow_echo.json (500 hp, x2 damage, wither on hit, tighter abilities, 3 cultists).
- `tools/quests/add_escapement_quests.py`: residue tier tag rewards on 7 Incursion quests; NEW quests 'What the Foundry Leaves' and
  'The Escapement' (item tasks, consume_items false).
- No deletions. UNVERIFIED in game: everything; esp. Neo Vitae ara_vitae_recipe via event.custom, KubeJS popItem / clear-count, ids.

## Pass 9-49 (2026-11-16) - staying locked is a real choice
- USER: release should cost some power; a Hallmarked 'Hollowed' set and uniques that drop while locked.
- `tools/gen_pass9_49.py`: datapack sets/hollowed.json ('Vestments of the Hollowed': cowl, vestment, greaves, treads, censer; netherite-grade,
  2/3/4/5-piece bonuses incl. leech, night vision, reaper + bleed; chance {} and no tables = never natural) + uniques revenants_shroud,
  kiln_hook, hollow_bell (chance {}); names/lore in kubejs/assets/dying_world/lang. Skill tree: Hollow Sight (locked) = 3 perks + 2 armor,
  1 attack damage, 4 max health; NEW Lens Sight / lens_sight_1 (released, lens on) = Arcane Ward + Hex only.
- kubejs 60_the_hollow.js: sight switching (locked -> Hollow Sight, released + lens -> Lens Sight, else none); the first kill gives the
  summoner a Hollowed set piece. 75_foundry_residue.js: locked tier-5 players killing Foundry Revenants: 4% set piece, 2% one of the
  three uniques (via /hallmarked sets give + generate unique=).
- No deletions. UNVERIFIED in game.

## Pass 9-50 (2026-11-16) - locked vs released balanced (no Hallmarked changes)
- USER: do all three (gear tied to being locked, rising Escapement cost, reversible release) without touching Hallmarked; the Hollowed set
  should only come from the first doppelganger kill, which is what locks you.
- kubejs 60_the_hollow.js: the first kill gives the whole Hollowed set (its only source; 9-49's revenant set drops removed from
  75_foundry_residue.js - revenants still give the 3 uniques, 2%, locked players only). Escapement n made after release costs
  min(32, 4n) Distilled Residue (count in player persistent data gh_escapements_made). Offering an Escapement at the altar re-locks
  you (relockFoundry); releasing again costs a Wound Movement and gives no Escapement (only the first release does: tag gh_first_escape),
  so cycling can't dodge the Distilled cost. The lens is only given if you don't already carry one.
- NEW kubejs 80_hollowed_gear.js: for released players, Hollowed set armor + Revenant's Shroud move from armor slots to the inventory,
  Hollowed Censer / Hollow Bell out of Curios slots, and holding the Kiln Hook gives Weakness II (Hallmarked components hallmarked:set_piece
  / hallmarked:unique read via the registry; Curios via CuriosApi, guarded).
- No deletions. UNVERIFIED in game.

## Pass 9-51 (2026-11-16) - the Hollow takes the herds
- USER: the heavier a player's Hollow, the more nearby friendly/neutral mobs spawn hostile; weight = residue tier + time held, release
  resets it; cap 50%.
- NEW kubejs 85_hollow_taken.js: each mob is judged once on spawn (tag gh_hollow_seen); 'creature'-category, not baby/named/tamed, within
  48 blocks of a player -> chance = tier base (t1 2%, t2 5%, t3 8%, t4 12%, Hollowed 15%) + 3% per day held, capped 50%; released = 0.
  60_the_hollow.js keeps the held clock (persistent gh_hollow_held_since: set when Hollowed or re-held, cleared on release).
- `tools/gen_pass9_51.py`: datapack mobrules/hollow_taken.json (gh_hollow_taken: hostile to players, 3 damage, angry on spawn,
  x1.25 speed, 'Taken <mob>', 15% Foundry Residue on player kills).
- No deletions. UNVERIFIED in game.

## Pass 9-52 (2026-11-16) - server robustness for the Hollow scripts
- Counters moved from KubeJS player persistentData (not certain to survive death) to vanilla scoreboard objectives, created on server
  load: gh_held_day (overworld day held + 1, 0 = not held), gh_escapements (Escapements made after release). Tags already survive
  death (PlayerList.respawn copies them).
- 85_hollow_taken.js: weights cached per player every 100 ticks (no command per spawn); only 'creature' mobs get the gh_hollow_seen
  tag (was every living entity).
- NOTE: anyone who tested 9-50/9-51 keeps stale gh_escapements_made / gh_hollow_held_since in KubeJS data; harmless, unused now.

## Pass 9-53 (2026-11-16) - kskills_perks takes over the sight switching
- kskills_perks now in git (kragnoth/kskills-perks): 1.0.1 source verified identical to the pack's jar; NEW 1.1.0 adds while_tags /
  unless_tags on kskills_perks:perk and a new kskills_perks:attribute reward (tag-conditional attribute modifiers). PACK NEEDS 1.1.0.
- `tools/gen_pass9_53.py`: Hollow Sight rewards = 3 perks + armor/attack/health while wv_occult_foundry unless gh_escaped; Lens Sight =
  Arcane Ward + Hex while wv_occult_foundry and gh_escaped.
- kubejs 60_the_hollow.js: the per-second node swapping is gone; grantCapstone unlocks hollowed_1, hollow_sight_1 and lens_sight_1
  together (and on login). Leftover tags gh_hollow_sight / gh_lens_sight from testing are harmless.
- No deletions. UNVERIFIED in game.

## Pass 9-54 (2026-11-16) - the Hollow moves into kskills_perks 1.2.0
- USER: move the rest into kskills_perks (it is a Gearwright's Hollow-only mod).
- kskills_perks 1.2.0 (kragnoth/kskills-perks): per-player Hollow state (tier, held/released, held day, escapements) saved on the player,
  mirrored to gh_hollow_defeated / gh_escaped / gh_residue_1..n; /kskills hollow status|defeat|hold|release|tier|escapements|reset;
  residue + distilled drops, revenant drops, locked-only uniques, taken spawns (tags gh_hollow_taken for the Mob Rules rule), Hollowed
  gear going cold (Curios by reflection), HUD meter; [hollow] section in kskills_perks-common.toml. Imports the 9-51/9-52 scoreboards
  and tags on first login. PACK NEEDS kskills_perks 1.2.0.
- DELETED kubejs server_scripts/progression/75_foundry_residue.js, 80_hollowed_gear.js, 85_hollow_taken.js (now in the mod).
- 60_the_hollow.js keeps only the altar, the boss and pack items; state goes through /kskills hollow (defeat, hold, release,
  escapements). Scoreboard objectives gh_held_day / gh_escapements are no longer used (left in old worlds, harmless).
- Quests still add gh_residue_<n> tags; the mod takes them in. UNVERIFIED in game.

## Pass 9-55 (2026-11-16) - one-command CurseForge export
- NEW `tools/export.py [version]` -> dist/Gearwrights_Hollow_<version>.zip: manifest.json + modlist.html at the root (from modpack/),
  overrides = modpack/overrides with kubejs/data from a fresh build.py run; repo notes left out. Reproduces the hand-built RC 4.2 zip.
- modpack/ snapshot updated to RC4: manifest.json, modlist.html, options.txt and three client configs from the RC4.1 export.
- To change mods: export from CurseForge, copy its manifest.json + modlist.html into modpack/, commit.

## Pass 9-56 (2026-11-16) - creative bookshelf recipe removed
- RC 4.2 log: create_enchantment_industry:creative_bookshelf is a block with no item ("Unknown registry key ... item"), so the 70_escapement.js
  mechanical-crafting recipe failed. Removed. Otherwise the log was clean for the pack's scripts: kskills_perks 1.2.0 loaded both reward
  types, the kskills tree loaded, Hallmarked loaded 13 uniques.

## Pass 9-57 (2026-11-16) - altar check made robust
- USER: right-clicking the altar with a Seal did nothing (silent). The only silent exits were the hand/item checks and the structure lookup.
- 60_the_hollow.js: the altar is also recognised by its shape (reinforced deepslate with candles on the four diagonals two blocks out);
  the structure lookup is wrapped and logs to logs/kubejs/server.log if it throws; holding a Seal / Wound Movement / Escapement on reinforced
  deepslate that isn't the altar now says so instead of doing nothing.

## Pass 9-58 (2026-11-16) - the altar's real bug
- KubeJS server.log: insideHollow threw on every click - Rhino can't choose between Registry.get(ResourceKey) and get(ResourceLocation).
  Now registryOrThrow(...).getOrThrow(HOLLOW_KEY) (single overload). The rest of the session's logs were clean for the pack's scripts.

## Pass 9-59 (2026-11-16) - the altar's second bug: event.cancel() exits immediately
- Checked against KubeJS 2101 source (kube-mods/kubejs@2101, KubeEvent.cancel: "Execution will be stopped immediately", throws EventExit).
  60_the_hollow.js called event.cancel() before doing anything, so every valid click stopped right there (hidden until 9-58 fixed the
  crash before it). The handler is now handleAltar(event) returning whether the click was the altar's; the wrapper cancels last.
- Rule for this repo's KubeJS: event.cancel() / event.success() etc. only as the final statement.

## Pass 9-60 (2026-11-16) - command results in KubeJS 2101
- RC test log: summoning works. Bugs: no Hollowed set / "Hollowed" message on the first kill, "The next one will want NaN", lens likely
  not given. Cause (KubeJS 2101 source, MinecraftServerKJS): server.runCommandSilent returns void, so every result I read was undefined.
- 60_the_hollow.js: cmdResult(server, command) runs the command through Brigadier (getCommands().getDispatcher().execute) and returns
  its number (0 on CommandSyntaxException, other failures logged as warnings). Used for /kskills hollow, the altar-busy check, the
  Distilled Residue count (was free), the doppelganger summon check, and the lens check.
- Testers: a player who already killed their copy under the bug is already 'defeated', so they never got the set; give it with
  /hallmarked sets give hollowed <cowl|vestment|greaves|treads|censer> (or /kskills hollow reset <player> and fight again).

## Pass 9-61 (2026-11-17) - headless server playtest; insideHollow fixed for real
- Booted a dedicated server (NeoForge 21.1.262) from the review instance's jars, swapped to kskills_perks 1.2.0 / mobrules 0.7.1 /
  wastelandvision 0.24.3, RC4-dropped jars removed, client-only jars set aside, plus a fresh tools/export.py build. Not covered:
  12 RC4 CurseForge projects absent from the review copy (no CurseForge API access to fetch them).
- Clean: every pack loader (KubeJS 0 script errors, 39 Mob Rules rules, 7+6 uniques, 15 sets, kskills tree, FTB Quests).
  Every quest item/fluid/entity/structure/biome/dimension/advancement reference resolves; all quest commands target valid
  ids (uniques, map loot table, skill category). Every Escapement-chain and creative recipe loads; the only non-Escapement
  creative producers are Create Encased's cosmetic casings (intended) and Ender IO's own Eternal Creative Power recipe, which needs
  enderio:creative_power - nothing makes that, so the gate holds.
- Live checks: the_hollow generates (/place and natural) with the altar on the candle diagonals; cmdResult returns real
  Brigadier numbers (0 on failure); the altar-busy execute check is dimension-scoped.
- BUG (mine): insideHollow never worked. (1) Rhino 2101 throws "redeclaration of var" for a `const` inside a try block on
  EVERY call (and in a loop body on the 2nd iteration) - now `let`. (2) Behind it, getStructureWithPieceAt has 4 overloads Rhino
  can't pick between - now getStructureAt + structureHasPieceAt (one overload each). Verified: natural Hollow inside=true.
  In play the altar still worked because the candle-shape check passes first.
- tools/lint_kubejs.py: flags `const` in try blocks / loop bodies; the pack is clean.
- Harmless: "Couldn't load tag minecraft:mineable/pickaxe" (#amendments:wall_lanterns) is logged on every dedicated-server boot
  before Moonlight generates Amendments' pack; the tags work at boot (tested from a fresh start).

## Pass 9-62 (2026-11-17) - configs after the mod update test
- Kragnoth updated all mods (20 patch/minor bumps) in a test instance; log clean apart from harmless warnings (Kotlin for Forge
  5.13 vs Fragmentum's bundled copy, Snow Under Trees' compat hook for an absent mod).
- Updated shipped configs from that instance: supplementaries-common (new [tools.orichalcum]), sophisticatedstorage-common
  (comment), waystones-common (fixVanillaTeleportBug removed upstream), kskills_perks-common (adds the 1.2.0 [hollow] section;
  was the 1.0.1 file). No pack values were reset. Quest chapters and ftbchunks-client differed only in formatting - left as is.
- DELETED (runtime output, regenerated on launch): config/wastelandvision/.generated/ (43 files),
  config/wastelandvision/mappings-occult_foundry.txt, config/jei/world/, config/jei/*.bak.1. Gitignored.

## Pass 9-63 (2026-11-17) - config trim; only the Occult Foundry vision ships
- Wasteland Vision: ships only visions/occult_foundry. config/wastelandvision/.installed_examples lists all three bundled
  examples, so WV's first-launch install (VisionManager.installDefaults: each example is offered once) skips soot_and_tar and
  thermal_print. Verified on a fresh server: only occult_foundry installed. README.md dropped (WV rewrites it every launch).
- DELETED 497 config files (730 -> 234):
  - orphans (189): configs of mods not in the pack, e.g. AE2 + addons, Apotheosis family, Artifacts, In Control, Powah,
    Just Dire Things, Modular Routers, Cristel Lib / Towns and Towers / vanilla_structures, Abnormals mods not shipped,
    Petrolpark, Storage Hub, Summoning Rituals. Owner = declared [[mods]] ids of every pack jar (nested too) + files a pack
    mod regenerates on an empty-config boot.
  - orphan sub-files (59): attributefix/{ars_nouveau,petrolpark,runiclib}, spark/tmp*.
  - default (225): identical (parsed TOML/JSON; normalised otherwise) to what the mod writes on an empty-config dedicated-server
    boot. Files also in defaultconfigs/ excluded (NeoForge seeds config from there, so that comparison is invalid).
  - client default (15): every key matches its "# Default:" comment. Client configs without Default comments were kept.
  - Kept although "default": create_enchantment_industry-server.toml (CEI's mechanicalGrindstoneFluidCapacity default 1000
    is outside its own range >5000, so a fresh file is "corrected" with a warning every install).
- Trimmed config boots clean on the test server (no new warnings vs the full config).
- Existing instances keep the deleted files when a zip is unzipped over them; harmless (defaults/orphans).

## Pass 9-64 (2026-11-17) - CurseForge project page
- modpack/CURSEFORGE_PAGE.md: project description (Markdown) for the CurseForge upload. Facts from the repo: 15 chapters /
  266 quests in four groups, structure list, mod list. Does not claim the Excalibur packs (not shipped in the export).

## Pass 9-65 (2026-11-17) - CurseForge logo
- modpack/logo.svg (source) + logo.png (800x800): brass cog, the face in the violet hollow, tar off the lowest teeth.
  Re-render: rsvg-convert -w 800 -h 800 modpack/logo.svg -o modpack/logo.png

## Pass 9-66 (2026-11-17) - logo = the pack icon, scaled
- Kragnoth prefers the original pixel-art icon (overrides/icon.png) over the 9-65 vector logo and a procedural pixel redraw.
  modpack/logo.png is now that icon scaled 16x (1024x1024, nearest neighbour). DELETED modpack/logo.svg.

## Pass 9-67 (2026-11-17) - new logo: water wheel and votive skull
- modpack/logo.png (1024x1024 = 64x64 pixel art x16): wooden water wheel in the Occult Foundry haze (palette from
  occult_foundry vision.json: fog #5c6270, water #24363a, soul fire), soul-light ring behind it, a blocky skull on a stone
  plinth with a soul-flame candle, fog bank in front of the wheel foot. Source: tools/logo_wheel.py
  (python3 tools/logo_wheel.py modpack/logo.png 16).

## Pass 9-68 (2026-11-17) - logo rendered from in-game models
- modpack/logo.png (1024x1024) now rendered like the Skill Perks logo: Create large water wheel from its OBJ model
  (spruce), vanilla skull block with soul-lit eye sockets and a lit candle + soul-fire flame, blurred Occult Foundry haze
  (fog #5c6270, soul glow, pines and foundry stacks), cobblestone pixel title, deepslate bar, gold subtitle
  "THE WORLD ENDED SLOWLY", bevelled frame. Source: tools/logo/ (README lists the textures to extract).
- DELETED tools/logo_wheel.py (9-67 pixel-art version).

## Pass 9-69 (2026-11-17) - plainer CurseForge page
- modpack/CURSEFORGE_PAGE.md rewritten short and plain at Kragnoth's request (no hype, no spoilers).

## Pass 9-70 (2026-11-17) - CurseForge page as HTML
- modpack/CURSEFORGE_PAGE.html replaces the .md (DELETED): inline-styled (brass headings, soul-teal accents) so the
  formatting survives copy-paste into the WYSIWYG editor; Copy button copies it as rich text.
