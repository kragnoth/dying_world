# Pack logo (pass 9-68)

`logo.py` renders `modpack/logo.png` (1024x1024): Create's large water wheel (its real OBJ model, spruce textures) and a
votive skull (vanilla skull block + candle + soul-fire particle) over a blurred Occult Foundry haze, with a cobblestone pixel
title. `render.py` is the tiny orthographic renderer it uses (nearest-sampled textures, z-buffer, Minecraft-style face shading).

Textures are not in git (Mojang/Create assets). Extract them first into the folders `logo.py` names (`V`, `CR`, `OBJ`):
the 1.21.1 client jar (`assets/minecraft/textures/...`: entity/skeleton/skeleton.png, block/candle_lit.png,
particle/soul_fire_flame.png, block/spruce_log.png, block/spruce_planks.png, block/spruce_log_top.png,
block/cobblestone.png, block/polished_deepslate.png) and the Create jar (`assets/create/textures/block/axis*.png`,
`waterwheel_metal.png`, `assets/create/models/block/large_water_wheel/waterwheel_large.obj`).
