# Wasteland Vision notes (from user's config/wastelandvision/ zip, mod v0.23.1)

> Status (9-75): written for WV 0.23.1. Now only the Occult Foundry vision ships, forced on for everyone (9-47, 9-63); `.installed_examples` must list occult_foundry, soot_and_tar, thermal_print.

Client-side "hallucination layer". Real world/server/hitboxes/drops/light are unchanged; the player only SEES
different blocks, plants, item icons/names, sky, fog, colour grade. Installed visions (folders in
`config/wastelandvision/visions/`): `soot_and_tar` (soot/creosote/tar mud, ash particles, smog shader),
`occult_foundry` (ghosts, bell/whisper ambience, smoke columns, sky omens, tar pools, brass thorns),
`thermal_print` (post-shader only). Toggle H, cycle J. Lock on server-side with
`defaultconfigs/wastelandvision-server.toml` (forceVision=true, forcedVision="..."). Which vision is active by
default is in `config/wastelandvision-client.toml` (not provided).

## What matters for structure design
- Rules match by block id / `#tag` / namespace / `full_cube` ONLY. No biome or structure awareness. So the vision
  restyles our structures' blocks exactly like natural ones. Do not rely on it for per-structure looks.
- "Blight" (dead patches) and "haunt" (ghost groves) are world-space 2D noise (percent of world, scale in blocks),
  independent of biome and of structures. Ghost mobs are client-only undead from the pack. We cannot place
  ghosts via structures and should not try. Structures and ghost groves overlap randomly.
- Stand-ins are registered blocks: client and server must ship the same `config/wastelandvision/` folder
  (otherwise registry mismatch on join). Only matters when distributing the pack.
- Vision hazards system marks dangerous stand-ins, so tar/oil that is genuinely dangerous stays readable.
- It ships `#c:is_wasteland` biome tag (only `regions_unexplored:ashen_woodland`). Possible hook for our own
  structure biome tags later; not used yet.
- `config/wastelandvision/mappings-<vision>.txt` (generated) lists every remapped block and the rule that caught it.
  Ask the user for it when choosing blocks for structures, to avoid picking blocks the vision hides/replaces.

## Rule of thumb
Vision = how it looks. Structures = what is really there (real tar/oil blocks, loot, mechanics, layout).
