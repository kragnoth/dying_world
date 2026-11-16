# Feature-based structure candidates (NOT disabled in pass 1)

Biome modifiers that add features in the *_structures steps. These are not structure sets, so
pass 1 does not touch them. Decide per item in pass 2 (disable with a `neoforge:none` override of
the same biome_modifier path, or keep). Vanilla also has feature-based things (monster rooms,
fossils, desert wells, geodes, etc.) which live in biome JSON - handle with a `neoforge:remove_features`
biome modifier in pass 2.

| biome_modifier | features | step |
|---|---|---|
| naturalist/add_ant_hills.json | naturalist:ant_hill_small, naturalist:ant_hill_big | surface_structures |
| realmrpg_skeletons/deep_underground_chambers_biome_modifier.json | realmrpg_skeletons:deep_underground_chambers | underground_structures |
| realmrpg_skeletons/underground_chambers_biome_modifier.json | realmrpg_skeletons:underground_chambers | underground_structures |
