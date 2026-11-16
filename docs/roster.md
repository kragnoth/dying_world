# Structure roster - DRAFT v1 (pass 3a). Built from my defaults. **SEE docs/user_decisions.md - it overrides this table where they differ.**

Distances are in CHUNKS (16 blocks): spacing 48 = ~768 blocks between attempts. All our sets are far sparser than the
originals. `ID` = proposed id under `dying_world:`. Verdict: KEEP (reuse as-is), RETHEME (reuse + later processors/blocks),
OPT (optional, user decides), DROP (stays disabled).

## Mechanism (decided so 3b is cheap)
Each curated structure = 3 tiny files in our namespace: (1) `worldgen/structure/<id>.json` copy of the original with
`biomes` -> `#dying_world:has_structure/<id>` (start_pool etc. still point at the mod's own pools, no big copies);
(2) `tags/worldgen/biome/has_structure/<id>.json` which at first just includes the original biome tag
(`"#mod:has_structure/x"`) so behaviour is identical, narrow later; (3) `worldgen/structure_set/<id>.json` with our own
salt/spacing. Retheming later = our own template_pool / processor_list copies. Mod structure may use extra
mod-specific fields: copy them verbatim.

## Progression (done / placeholder)
| slot | source | status |
|---|---|---|
| Stronghold / end portal | vanilla stronghold | DONE placeholder `dying_world:strongholds` (retheme later: buried facility) |
| Nether fortress / blaze | vanilla fortress | DONE placeholder `dying_world:nether_fortress` (retheme: burnt-out foundry) |

## Life & settlement
| slot | proposed source | orig spacing | proposed | verdict |
|---|---|---|---|---|
| Survivor settlements (villagers!) | vanilla villages (5) + vsrevamped (cherry, swamp) + towns_and_towers towns (27 biome variants) | 34 / 34 / 51 | 64/20, one set per source or one mixed set | RETHEME - the key "life" structure; very rare |
| Abandoned villages / hamlets | gearwrights abandoned_villages, abandoned_hamlets (7 biome variants each) | 52 / 30 | 44/16 and 32/12 | KEEP/RETHEME - the common "dead" settlement; verify no live villagers in 3b |
| Lone homes | forsaken homes (9), abandoned_cabins, environmental log_cabins, autumnity maple_huts | 30/67/32/32 | 36/12 | KEEP (pick 1-2 sources, avoid duplicate cabin spam) |
| Wells / waypoints | forsaken wells (11) | 20 | 40/14 | KEEP |

## Ruins, industry, scavenger sites (core theme)
| slot | proposed source | orig | proposed | verdict |
|---|---|---|---|---|
| Burnt homestead / manor / watchtower | gearwrights burnt_* | 34/58/46 | 48/16, 80/28, 60/20 | KEEP - on theme |
| Collapsed minehead (surface mine entrance) | gearwrights collapsed_minehead | 40 | 48/16 | KEEP/RETHEME (industrial) |
| Ruined chapel | gearwrights ruined_chapel | 52 | 64/22 | KEEP (occult hook) |
| Small ruins (common filler) | gearwrights abandoned_ruins (7) | 13 | 24/8 | KEEP, keep dense-ish so world isn't empty |
| Watchtowers | watchtower_building abandoned (fresh = DROP) | 48/67 | 56/20 | KEEP abandoned only |
| Smithy / lighthouse | createnewbeg abandoned_smithy, lighthouse | 100 | 80/30 | KEEP (Create flavour) |
| Forges / vaults / tin monoliths | caverns_and_chasms (underground) | 16/32/96 | 40/14, 48/16, 96/32 | OPT - forges likely fit; check contents |
| Derelict conservatory | cultivar | 40 | 56/20 | KEEP ("derelict" fits a dying biosphere) |
| Mineshafts | vanilla mineshaft (+mesa) | 1/0 (everywhere!) | 20/6 | RETHEME - collapsed industrial tunnels |
| Road signs | supplementaries road_signs | 19 | 32/10 | KEEP - post-collapse connective tissue |
| Scavenger outposts | vanilla pillager_outposts + towns_and_towers towers (31 variants) | 32/48 | 56/18 | RETHEME - no pillager lore needed; OPT whether pillagers remain |

## Occult & tar (identity)
| slot | source | orig | proposed | verdict |
|---|---|---|---|---|
| Charnel crypt, drowned radio, researcher cabin, wayside shrine | tarbound (4) | 56/30/48/36 | 64/20, 40/14, 56/18, 40/14 | KEEP - theme anchors, first 3b batch |
| Witch tower, large temple | formationsoverworld rare | 50 | 72/24 | OPT (occult fits) |
| Small POIs (campsites, huts, spires...) | formationsoverworld uncommon (27) | 15 | 28/10 | OPT - good filler, check tone |
| Totems | windswept pine/snowy pine totems | 10/1 | 40/14 | OPT - occult-ish but far too dense originally |
| Weathered houses / frozen villages | windswept | 24-28 | 48/16 | OPT |

## Late-game / loot sites
| slot | source | verdict |
|---|---|---|
| Bastion remnant | vanilla (was paired with fortress) | OPT - piglin/gold economy; separate set if wanted |
| Ancient city | vanilla | OPT - rare deep site |
| Trial chambers | vanilla | OPT - keys/vault loot; rarest |
| Ruined portals | vanilla (7 variants) | OPT - "lost gateway" lore; gives obsidian/gold |
| End city | vanilla | OPT - elytra/ shulkers; far end only |
| Nether | formationsnether common/rare/ore_shards, hearths towers/spirals | OPT - nether flavour pass later |

## DROP (stay disabled)
desert pyramid, jungle temple, igloo, swamp hut, woodland mansion, ocean monument, ocean ruins, shipwrecks, buried treasure,
trail ruins, nether fossils (decide later), supplementaries galleons, formationsoverworld rafts & fresh_watchtower, towns_and_towers
mimic_desert/wreckage_ocean, formationsnether if nether is left bare, atmospheric (arid_gardens, kousa_sanctums - verify tone).

## Open questions for the user
1. Do villagers stay obtainable via living survivor settlements, or only via other means (Easy Villagers is installed)?
2. Pillager/illager lore: keep illager structures (retheme as scavenger gangs) or drop pillagers entirely?
3. Overworld-wide vs tied to dying biomes (`#c:is_wasteland`, Regions Unexplored ashen biomes) - or both (settlements everywhere,
   crypts/shrines only in blighted biomes)?
4. Nether/End: bare (just fortress + stronghold) or curated sets too?
5. Which OPT rows do you want?

## Proposed 3b first batch (5 sets, low risk)
tarbound x4 (single-structure each, identity setters) + one survivor-settlement set (vanilla villages, very rare).
Each pass ends with `/locate structure dying_world:<id>` and `/place structure` test steps.
