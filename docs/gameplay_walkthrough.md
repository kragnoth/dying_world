# Gameplay walkthrough (pass 9-8) - where the dying world can fail or falter

Method: a full survival run checked against every structure we ship (coherence_audit.md), the 21 vanilla sets disabled in pass 1, the feature removals of pass 2
and vanilla's item/progression sources. ✅ = works, 🔧 = fixed in 9-8, ❗ = gap that needs a decision.

## 1. Spawn and early game
- ✅ Shelter/food/tools: survivor villages in all 5 families (40/12 spacing, size 6) with 40% lived houses, crops, beds; wells (water), cabins, watchtowers, smithy loot.
- ✅ Villagers: lived houses spawn villagers; jobs present in every family: farmer (composter), butcher (smoker), librarian (lectern), cleric (brewing stand), shepherd (loom),
  weaponsmith (grindstone), armorer (blast furnace), toolsmith (smithing table), cartographer (cartography table, planter house), fisherman (barrels), leatherworker (water cauldrons).
  🔧 fletcher and mason were MISSING everywhere except taiga/snowy sawmills -> the forge now has a fletching table + stonecutter in every family.
- ✅ Zombie-villager cures: abandoned settlements spawn zombie villagers (light undead spawns), so villages can be repopulated.
- ❗ No mob spawners in the overworld: monster rooms were removed in pass 2 and the industrial mineshaft has no spawner rooms (deferred 4-2e 'spawner room').
  Early XP farms (zombie/skeleton spawner) are impossible; dungeon-chest loot (saddles, name tags, music discs) only via other chests/fishing/trading.
- 🔧 `/locate #minecraft:village` and anything else using the village tag now finds our survivor villages (it only listed disabled vanilla/mod villages).

## 2. Exploration loop
- ✅ Loot ladder: abandoned ruins/hamlets/villages (undead, basic loot) -> concrete pads (ruined-portal gold loot) -> scavenger outposts (gear, crossbows) -> industrial mineshafts (deep loot, flooded/tar hazards)
  -> scavenger stronghold (bastion loot, guaranteed netherite upgrade template, immune piglins).
- ✅ Road signs point to survivor villages.
- 🔧 Explorer/treasure maps all pointed at DISABLED structures (mansion, monument, trial chambers, buried treasure): cartographer map trades silently disappeared and shipwreck map chests
  gave blank maps. Retargeted: woodland map -> scavenger stronghold, ocean map -> lighthouse, trial-chamber map -> industrial mineshaft, treasure map/dolphins -> beached shipwreck.
- ❗ Heart of the sea (conduit) only came from buried treasure (disabled): unobtainable.

## 3. Nether
- ✅ Nether fortress restored (blaze rods for eyes of ender, wither skeletons, rib trim). Piglins + bartering in nether wastes/crimson.
- ✅ Netherite: ancient debris is ore (not structure); upgrade template guaranteed in the scavenger stronghold treasure chest.
- ❗ No bastions/nether fossils (disabled): snout trim only via stronghold chests (bastion copy), bastion-only loot otherwise covered.

## 4. Stronghold and the End
- ✅ Strongholds restored (concentric rings, eye of ender tag fine) -> End portal works.
- ❗ END CITIES are disabled: **elytra and shulker shells (shulker boxes) are unobtainable**, plus spire trim and end-city loot. This is the biggest progression gap.

## 5. Items/features with NO source any more (vanilla structure-only)
| lost structure | what disappears |
|---|---|
| end cities | elytra, shulker shells/boxes, spire trim |
| ocean monuments | sponges, elder guardian, tide trim (prismarine only via guardians -> none) |
| trial chambers | mace/heavy core, breeze rods/wind charges, trial keys, ominous vaults, flow/bolt trims |
| ancient cities | echo shards (recovery compass), swift sneak, ward/silence trims, disc 5 |
| woodland mansions / pillager outposts (vanilla) | allays (cages), vex trim, sentry trim (totems still drop from raid evokers) |
| ocean ruins / trail ruins / desert pyramids | sniffer eggs, archaeology sherds, relic disc, dune/host/raiser/shaper/wayfinder trims |
| buried treasure | heart of the sea / conduit |
| jungle temples / igloos / swamp huts | wild trim; igloo basements; witch-hut farms |

## 6. Coherence of feel
- ✅ Survivor villages lit + living vs abandoned settlements unlit + undead: clear contrast, same houses (lived vs ruined variants) -> reads as one world.
- ✅ No floating structures (beard_box on all settlements), lantern head clearance everywhere, no tipis/cherry/coloured panels.
- ❗ Jungles/rainforests/tropics, mountains, dark forest, mushroom fields have no settlements (deliberate) - jungle is the largest empty biome group.

## Decisions needed (❗)
1. End cities: re-enable vanilla end cities (simplest, End is outside the dying-world theme) OR put elytra/shulker shells into our own structure loot?
2. Ocean monuments / trial chambers / ancient cities: re-enable as-is, or build replacements (5-4 sculk site = ancient-city replacement already planned), or accept the losses?
3. Mob spawners: add a spawner room to the industrial mineshaft (zombie/skeleton/spider), as planned in 4-2e?
4. Sniffer eggs / sherds / heart of the sea / allays: add to specific loot tables (e.g. lighthouse, shipwreck, stronghold) or accept?

## Update 9-11..9-13 (2026-11-15): every ❗ above now has a source
End station (elytra guaranteed, shulkers, spire) · sunken research lab (elder guardian, sponge, tide, prismarine) · proving grounds (breeze spawner, vaults, keys, mace via heavy core, flow/bolt)
· sculk research site (ancient-city loot) · dig sites (sniffer eggs, sherds, relic, dune/wild/trail trims) · allay specimens (overworld gate labs) · sentry/vex trims (scavenger loot)
· heart of the sea (drowned drop, 9-10) · spawners (mineshaft, 9-9). Remaining by design: no settlements in jungle/mountain/dark-forest/mushroom biomes.
