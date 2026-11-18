# Redo list (pass 7-0): buildings to replace with our own style

> Status (9-75): done. Tipis/teepees removed (8-10), savanna rebuilt in our gradient style (7-1, 9-5), abandoned savanna = ruined variants of it (9-6). Kept for history.

User decision: redo every building that uses the TEEPEE style or the other clashy, non-vanilla "Mediterranean" buildings.

## TIPI / TEEPEE REMOVAL - USER DECISION (supersedes the questions below)
Get rid of ALL tipis/teepees everywhere. We will work over each set one by one later (no files changed yet; this is the checklist):
- savanna custom houses `savanna_teepee1/2/3` (kubejs `minecraft/structure/village/savanna/houses`, pool `minecraft:village/savanna/houses`; also our worn copies in `datapack/data/dying_world/structure/village/savanna/houses_worn/`) -> drop from the pool (replaced by the new savanna roster).
- desert donor `kaisyn:wooded_badlands_tipi` (15 NBTs, 12 accepted houses mixed into our desert villages) -> remove the donor from `tools/gen_pass3c4.py` (desert donors) and regenerate.
- Gearwrights abandoned savanna ruins: 14 NBTs with tipi/teepee names (`gearwrights/structure/abandoned/savanna/...`) -> remove from those pools (check `grep -i -E "tipi|teepee|tepee" reference/nbt_index.txt`).
- Any other set found later: grep the NBT index / pool element names for tipi|teepee|tepee|wigwam.
Method when working each set: remove the pool entries (weights re-balanced), regenerate (`gen_pass3c4.py`, `gen_pass3b2/3c4`, `gen_pass6_1.py` order), re-run `tools/validate.py`.

## STILT / POLE HOUSES - USER DECISION (pass 7-0d, corrected 7-0d2): remove the MULTI-COLOUR-PANEL stilt palette wherever it appears
User dislikes the savanna multi-colour-panel houses on poles (acacia + coloured terracotta/wool panels, floor lifted off the ground). Stilts themselves are fine where they fit: SWAMP stilt houses are KEPT (look proper there). Rule: a stilt palette with coloured panels is removed everywhere. Scan: `python3 tools/stilt_scan.py` -> `docs/stilt_houses.md`.
- savanna custom set (palette: acacia + coloured terracotta/wool panels): stilt houses `savanna_armorer, savanna_big_house, savanna_butcher, savanna_cartographer, savanna_library, savanna_shepherd, savanna_medium_house2`;
  same palette, NOT on poles but marked too: `savanna_tannery, savanna_mason, savanna_toolsmith, savanna_weaponsmith, savanna_temple, savanna_farm1/2` (+ the 3 teepees). => whole savanna base set goes (already planned in 7-0: new roster).
- gearwrights abandoned SAVANNA ruins/hamlets/villages: 16 of 53 NBTs are stilt houses (same palette) -> mark `dying_world:abandoned_{ruin,hamlet,village}_savanna` for removal / rebuild with the new savanna style.
- gearwrights abandoned SWAMP ruins/hamlets/villages: 25 of 63 NBTs are stilt houses but they are wood/swamp-style and FIT -> KEEP, nothing to do (user decision 7-0d2).
- one stray: gearwrights `snowy_small_house_2_a` (1 of 73 snowy NBTs) - single house, not a palette; mention only.
- NOT stilt (scan, 0 hits): all other base sets, pueblo, tipi huts, cherry, birch_romanian, forest_ruins, viking, polish, frozen. Farms are skipped by the scan (flat plots).
- Nothing removed yet; this is the checklist. Removal method: drop the structures from the sets (gen_pass3b2/3c4/6_1 order) or replace with the new styles in 7-1+.

## Evidence (from the scan of reference NBTs)
- The user's KubeJS data (`kubejs/data/minecraft/structure/village/*/houses` + pool `minecraft:village/<family>/houses`) REPLACES the vanilla house sets of all five families with a custom 18-26 house set each
  (plains_armorer..., taiga_..., desert_..., snowy_..., savanna_...). Vanilla-named files (`savanna_small_house_1..8`, `_medium_house_1/2`, `_butchers_shop_1/2` ...) exist in the merged data but the pool does NOT use them.
- Our survivor villages (`tools/gen_pass3c4.py`) build their savanna house pool from that custom set (18 houses, weights, worn copies in `datapack/data/dying_world/structure/village/savanna/houses_worn/`).
- The savanna custom set is what reads as clashy: acacia log + acacia slab shell, flat roofs, large PANELS OF COLOURED TERRACOTTA (lime, yellow, light blue, orange, white, green) and 3 teepees of white wool with a blue/red/orange accent.

## Savanna custom houses currently in our pool (ALL to be replaced; size = x,y,z with template height)
armorer 13x16x13 | big_house 14x14x10 | butcher 8x14x13 | cartographer 8x16x10 | farm1 11x11x12 | farm2 14x11x7 | fisher 11x8x16 | library 12x17x13 | mason 11x14x9 |
medium_house2 11x13x12 | shepherd 17x14x9 | tannery 9x14x8 | teepee1/2/3 9x14x9 | temple 17x16x20 | toolsmith 13x14x11 | weaponsmith 5x11x6  (+ unused medium_house1 15x13x8, small_farm 6x7x9)
Replacement roster and footprints: see `docs/style_board_savanna.md`. Teepees and fisher (no water in savanna) are dropped, not replaced.

## Other families - needs the user's confirmation
- Desert donor `kaisyn:wooded_badlands_tipi`: REMOVE (see user decision above).
- Desert donor `kaisyn:badlands_pueblo` (27 houses), plus the plains/taiga/desert/snowy custom sets (22-26 houses each) and the other donors: NOT touched until the user says which are 'clashy Mediterranean'.
- Gearwrights abandoned savanna ruins (72 NBTs) are separate (ruined by design) and untouched.


## 2026-11-15 update
- `dying_world:abandoned_{ruin,hamlet,village}_savanna` will be REPLACED by ruined variants of the new savanna houses (7-1+), not by gearwrights pieces. Everything else third-party is tracked in `docs/release_report.md` (rebuild queue).

## 2026-11-15 (pass 7-1/7-2) DONE
- savanna custom set (coloured panels, stilts, 3 teepees) replaced by 12 new buildings (lived/ruined); teepee town centre dropped; abandoned savanna sets rebuilt from ruined new houses + vanilla streets.
- Still open from the tipi list: desert donor `kaisyn:wooded_badlands_tipi` (remove from gen_pass3c4 desert donors).

## 2026-11-15 (8-10): tipi removal COMPLETE - desert donor kaisyn:wooded_badlands_tipi dropped from gen_pass3c4.py.
