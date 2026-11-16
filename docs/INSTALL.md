# INSTALL / CLEANUP (user wants a brief plain rundown, NO shell commands)

Why kubejs/data: the pack's own `kubejs/data` loads on top of world datapacks, so ours must go there to win.

## Install
1. Optional: copy your current `kubejs/data` folder somewhere as a backup.
2. Open `dist/dying_world_datapack.zip` (inside the project zip).
3. Copy the contents of its `data` folder into `kubejs/data`, overwriting existing files. Skip `pack.mcmeta`.
4. Fully restart the game (/reload is not enough for worldgen).

## 3c note
The pack now also contains `data/minecraft/worldgen/template_pool/village/<biome>/houses.json` overrides (plains, taiga, desert) - it goes into kubejs/data like everything else.

## Cleanup
Nothing to delete: passes only add or overwrite files. Only if you also installed it as a world datapack, remove that copy.

## Test (fresh world or unexplored chunks only)
- `/locate structure dying_world:<id>` for: abandoned_cabin, wayside_shrine, researcher_cabin, charnel_crypt, drowned_radio (swamp),
  burnt_homestead, burnt_manor, burnt_watchtower, abandoned_watchtower (3b-2),
  abandoned_ruin_plains, abandoned_hamlet_taiga, abandoned_village_snowy, collapsed_minehead, ruined_chapel, shipwreck, shipwreck_beached,
  wells/rustic/oak (3b-3/4; smithy + lighthouse are 80 chunks apart, so `abandoned_smithy` / `lighthouse` may need a long search). All of the above already passed. 3c-1 passed. 3c-2 passed. 3c-3 (desert, now with 4 house looks) new: `/locate structure dying_world:village_desert`; method as before: `/place structure dying_world:village_taiga` and `/place structure dying_world:village_plains` and walk the village (see PROGRESS.md 3c-1/3c-2).
- `#minecraft:village` must find nothing; `minecraft:stronghold` and `minecraft:fortress` must still be found.
- Check logs/latest.log for lines mentioning `dying_world`. Report failed locates + those log lines.

## 3c-4 note
Villages now come from one generator run: new files under `data/dying_world/{structure/village,worldgen/processor_list/mix,...}` plus overrides of `data/minecraft/worldgen/template_pool/village/{plains,taiga,desert,savanna,snowy}/houses.json`. Install as before (into kubejs/data), restart.
Test (3c-4): `/locate structure dying_world:village_savanna`, `dying_world:village_snowy`; `/place structure dying_world:village_<type>` for all five and walk through; check forest / birch / badlands / ice spikes / cherry grove now get a village. Report failed locates + log lines mentioning `dying_world`, `kaisyn`, `windswept` or `brutos`.

## 3c-4b note
Village biome tags now include modded biomes (explicit optional lists). Same install. Extra tests: `/locate structure dying_world:village_plains` while standing in a Regions Unexplored forest/grassland; `dying_world:village_desert` in an Atmospheric dune; no villages should appear in swamp/jungle/beach.

## 3c-5 note
Also adds `data/supplementaries/tags/worldgen/structure/road_sign_destinations.json` (override) - goes into kubejs/data like the rest. Tests: `/locate structure dying_world:road_sign`; read a road sign; check abandoned hamlets/ruins keep their distance from survivor villages.

## 4-1 note
New: concrete pads (4 structures, `dying_world:concrete_pad_{temperate,cold,arid,wild}`), their loot tables (`data/dying_world/loot_table/chests/`) and 14 NBTs (`data/dying_world/structure/concrete_pad/`). Same install (into kubejs/data, restart).
Test: `/locate structure dying_world:concrete_pad_temperate` (and cold/arid/wild), `/place structure dying_world:concrete_pad_temperate` on flat ground, open the chest. Report failed locates, floating/sunken pad, and log lines mentioning `dying_world` or `concrete_pad`.

## 4-1b note
Pads now use Rust and Rebar blocks (`rebar_concrete`, corrugated rusted metal, crates...). Reinstall the datapack the same way (it overwrites the 14 pad NBTs + chest loot table); restart.

## 4-2a note
Industrial mineshafts: `dying_world:industrial_mineshaft` (set `industrial_mineshafts`), 17 NBTs in `data/dying_world/structure/mineshaft/`, pools in `worldgen/template_pool/mineshaft/`, loot `chests/mineshaft_storage`. Same install (kubejs/data), restart. Test: `/locate structure dying_world:industrial_mineshaft` or `/place structure dying_world:industrial_mineshaft` then dig/tp underground. Report: layout/connection problems, lighting, tracks, hitching, and log lines mentioning `dying_world`, `mineshaft`, `jigsaw`.

## 4-2b note
Adds 7 room NBTs + 4 loot tables and overwrites `worldgen/template_pool/mineshaft/rooms.json`. Same install: copy `data` contents from `dist/dying_world_datapack.zip` into `kubejs/data`, overwrite, restart. Test as 4-2a; open door alcoves to see workshop/office/fuel/stash rooms.

## 4-2b-lights note
Overwrites the mineshaft NBT pieces (lamp states only; layouts unchanged). Same install: copy `data` contents from `dist/dying_world_datapack.zip` into `kubejs/data`, overwrite, restart. Already-generated mineshaft chunks keep old lamps; explore new chunks (or /place a new one) to see the change.

## 4-2c note
Adds `yard_hall_1/2.nbt` and overwrites `worldgen/template_pool/mineshaft/tunnels.json`. Same install (copy `data` contents of `dist/dying_world_datapack.zip` into `kubejs/data`, overwrite, restart). Test in NEW mineshaft chunks: look for a large hall with stacked shipping containers; walk into a container through its open rear end.

## 4-2c-girders note
Overwrites all mineshaft NBT pieces (girder/beam connection states + new ceiling girders; halls too). Same install (copy `data` contents of `dist/dying_world_datapack.zip` into `kubejs/data`, overwrite, restart). Look at new chunks only: ceiling beams should meet the posts, and thin sub girders should run into the main beams.

## 4-2c2 / 4-2s note
New folders in `data/dying_world/`: `tags/block/` (mineshaft_open tag) and processor `mineshaft_no_float`. Same install (copy `data/` into kubejs/data, restart). The mineshaft now has a surface head: test with `/locate structure dying_world:industrial_mineshaft`.

## Release build (8-0)
`python3 tools/provenance_audit.py && python3 tools/build_release.py` -> `dist/release/dying_world_release_datapack.zip` (only own/vanilla/confirmed content) + `docs/release_report.md`. Policy: `tools/release_policy.json`. The normal private build is still `python3 tools/build.py`.
