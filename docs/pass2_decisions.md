# Pass 2 decisions (reversible)

Feature-based structures (not structure sets), audit from packwork biome JSONs:
- vanilla `monster_room`, `monster_room_deep` (163 biomes each), `desert_well` (4): REMOVED.
- realmrpg_skeletons `underground_chambers`, `deep_underground_chambers`: REMOVED.
- KEPT: vanilla fossils (17 biomes), ice spikes/patches, blue ice, basalt columns, delta, end spike/gateway
  (terrain/natural, suit the theme); naturalist ant hills (ecology); the ~30 other realmrpg_skeletons placed
  features (loose skeletons, thematic for a dying world).
- Method: one NeoForge `remove_features` biome modifier `dying_world:remove_feature_structures`
  (runs in the REMOVE phase, after all add_features). Edit its `features` list to restore/remove more.

Progression placeholders (vanilla structures, our own sets, TO BE RETHEMED later):
- `dying_world:strongholds` - vanilla stronghold, vanilla ring placement (end portal reachable via Eye of Ender).
- `dying_world:nether_fortress` - vanilla fortress only (no bastions), spacing 30 / separation 10, own salt.
These reference vanilla structure ids directly, so no copied files. Later passes swap the `structure` entries
for themed versions in the `dying_world:` namespace.
Deferred: villages, bastions, ancient cities, trial chambers, ruined portals, etc.

User confirmed: namespace `dying_world`; `/locate` showed no stray structures after kubejs/data install;
dimension access (Nether/End) must remain; structure theming decided later.
