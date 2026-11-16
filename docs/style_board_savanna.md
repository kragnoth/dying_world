# Savanna style board (pass 7-0) - PROPOSAL for the replacement houses
Goal: rich 1800s hot-dry/seasonal architecture (US + European), BDubs build principles, walkable + functional, fits vanilla village footprints/entrances. Own namespace pools; streets/well/lamp posts/pens stay vanilla.

## Three blended sub-styles (vanilla blocks only; acacia stays the village identity wood for beams/trim)
| style | walls | roof | trim/ornament | used for |
|---|---|---|---|---|
| Spanish-colonial adobe/hacienda | white_terracotta stucco, smooth_sandstone, stone_bricks base | brick_stairs/slabs (clay tile) + red_sandstone ridge | acacia log beams + corbels, dark_oak trapdoor shutters, iron_bars grilles, arched porches (stairs), terracotta pot planters | medium house, big house, mission chapel, library |
| Southern raised-porch frame (dogtrot/Creole) | birch/stripped birch siding + white_terracotta panels, cobblestone/stone-brick piers | spruce/dark_oak stairs shingles, steep with overhang | acacia fence columns, veranda + railings, trapdoor shutters, porch swing/bench | small houses, big house, shepherd barn |
| Texas limestone farmhouse | sandstone/cut_sandstone + andesite quoins, stone-brick chimney | spruce stairs/slabs (tin look: cut_copper only if wanted) | acacia lintels, small deep windows, porch posts | small houses, butcher/smokehouse, smithy, mason |
BDubs rules (CORRECTED by user: the style is GRADIENTS driven by lighting, not random noise):
- Every wall/roof/floor surface is a RAMP of 3-5 related blocks ordered dark/rough -> light/clean (e.g. mossy cobble -> cracked stone brick -> stone brick -> sandstone -> white stucco). Position on the ramp comes from a smooth function, not a coin flip per block.
- Vertical gradient: heavy/dark base course, lighter mid wall, lightest cornice/upper storey. Blend bands at their borders with light dithering (2-3 block patches), never single random dots across a wall.
- Light/shadow logic (fake ambient occlusion): surfaces in shade (under eaves/porches, inside recesses, interior corners, shaded side) shift ONE step darker; exposed/sun-facing one step lighter. Computed from neighbouring blocks in the generator.
- Random noise only as secondary breakup: <= ~15-20% inside a band, clustered, never the main structure.
- Plus: nothing flat (recess windows 1, trim rows, corner posts/quoins, cornice), 2-layer roofs with overhang + dormers/chimneys, a light source in every room (warm lanterns; interior lighting also reads as a gradient: pools of light, darker corners), props outside (barrels, planters, benches, vines).
- Ruined variants reuse the SAME ramp logic: decay = shift the ramp darker/rougher with a direction (moss/dirt rising from the ground, cracks mid-wall, soot near chimneys/ridge), not uniform random replacement.

## Roster (vanilla slots -> our buildings). First batch ~10
| slot | building | size class (x,z) | job block / function |
|---|---|---|---|
| small house x3 | Creole cottage, dogtrot, limestone cottage | 7-9 x 7-9 | beds |
| medium house x2 | hacienda casita w/ veranda | ~11x12 | beds |
| big house | planter's house, 2 storeys, balcony | ~14x10 | beds |
| butcher | limestone smokehouse + chimney | ~8x13 | smoker |
| toolsmith | open-sided forge | ~13x11 | grindstone |
| library | mission schoolhouse/reading room | ~12x13 | lectern |
| temple | adobe mission chapel + bell tower | ~17x20 | bell/brewing stand |
| large farm x2 | walled kitchen garden/orchard, pergola, cistern | ~14x7, 11x12 | composter, crops |
| later | shepherd barn+corral 17x9; weaponsmith 5x6; armorer 13x13; mason 11x9; tannery 9x8; cartographer 8x10 | | |
Each building needs a `minecraft:building_entrance` jigsaw (pool `minecraft:village/savanna/...` replaced by ours) so vanilla-style streets connect, same y alignment as the old houses.

## Variants (user rule: 40% lived-in, 60% worn; never holes)
1. BASE untarnished (our reference version, no villagers' job/beds issues).
2. LIVED-IN = base with beds + job blocks + villagers spawn (40%).
3. RUINED (60%), style-appropriate and replace-only (moss/lower stage): stucco white_terracotta -> light_gray_terracotta/cracked; stone_bricks -> cracked/mossy; sandstone -> cut/ chiselled weathering;
   clay-tile roof bricks -> mossy cobble/stone brick stairs; wood -> stripped/moss trim; beds -> carpets, job blocks -> cobblestone-style rubble; props tipped/cobwebbed; savanna 'weathered / scorched / tarred' lists as now.
   Because we GENERATE the NBTs, worn variants are made by script with property-preserving block mapping (stairs/slabs/walls keep facing/half/type), not by processor.
