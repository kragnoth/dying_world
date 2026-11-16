# Furniture notes (pass 7-0) - how the existing houses furnish themselves, and the library the new savanna houses will use
Source: `tools/furniture_scan.py` over 1,056 village house NBTs (vanilla + the user's kubejs custom set + donor mods), 18.6k clusters. Raw tables: `furniture_catalog.md`. Palettes: `house_palettes.md`.

## What the existing houses actually do (interior clusters; counts = clusters / houses)
- BED: always a 2-block bed against a wall (267). Variant: chest at the foot end (32). No nightstands/rugs in vanilla-style houses.
- TABLE: `fence` + `pressure_plate` on top = 1x1 table (13 clusters / 12 houses). With CHAIRS: stairs (bottom) on 1-2 sides of the table (23/18 and 12/9). Extras seen: lantern on a second fence post beside it, wall_torch above, wall signs as chair backs (4).
- SEATS: single `stairs` (bottom) as a chair (219 / 81 houses); open/closed `trapdoors` mostly act as window shutters but 3 trapdoors in a row (top half) make a counter/bench (30).
- STORAGE: lone `chest` against a wall is near universal (240 / 210 houses); chest standing on a top-half trapdoor "plinth" (13+10); double chests; `decorated_pot` (21); barrels in pairs.
- WORKSTATIONS: one job block placed solo against a wall with a free standing cell in front (blast_furnace 26, barrel 23, smoker 22, crafting_table 22, brewing_stand 20, fletching 15, grindstone 13, plus loom/lectern/cartography/smithing/stonecutter/composter/cauldron). Villagers need the job block REACHABLE (a standing cell + path); keep that in every house with a job.
- SHELVES: bookshelf stacks 1-3 high (libraries use 3x3 walls with stairs/trapdoor trim, lantern on top, lectern in front).
- LIGHT: wall_torch (673) and lantern (465) dominate; lanterns stand on blocks/fence posts or hang from `chain` (22); campfire hearth (73); candles (27); standing torch (33). Windows = glass panes with trapdoor shutters.
- PLANTS: flower_pot / potted plants (cactus 25, saplings, fern, orchid, lily of the valley).
- Outside: lamp posts (fence + lantern), hay/barrels/crates near job buildings, animal pens, farms.
- Density: vanilla-style houses are SPARSE (a bed, a table, a chest, a light). The new houses should be noticeably richer but still read as the same furniture language so villagers/players recognise it.

## Furniture library for the new savanna houses (all built from vanilla blocks; each is a small function in the generator)
Core (matches the existing language): bed (+ foot chest), 1x1 table + 1-2 stair chairs, stair chair/stool, chest, decorated pot, wall torch, lantern on fence post, chain lantern, flower pots, bookshelf stack, job block + free standing cell.
Rich additions (BDubs-style, not in the current houses):
- dining table 2x3 (slab top on fence legs) with 4-6 stair chairs and sign/trapdoor chair backs; candle/flower-pot centrepiece
- sideboard / dresser (stairs or slabs top + barrel or trapdoor doors, lantern/pot on top); wardrobe (barrels/chests + trapdoors)
- kitchen run: furnace/smoker/barrels under a slab counter, cauldron wash basin, hanging pots (flower pots on chains)
- hearth/fireplace: stone brick surround + campfire/furnace + chimney flue, mantel slab with candles
- sofa/armchair: stairs + trapdoor/sign backs and arms; rugs from carpets; low coffee table (slab on fence)
- chandelier: chain + lantern/candle ring; porch bench (stairs/slabs); shutters (trapdoors); curtains (open trapdoors + banner/carpet)
- desk (slab + barrel + book/lectern), globe/map (item frame/painting when entities are used), potted plants everywhere
Rules: every room gets 2-4 functional pieces; keep a clear 1-wide walking path; ceiling >= 3 high; beds/job blocks never boxed in; lights in every room; lived-in versions keep beds+job blocks, ruined versions swap them (see style board).
