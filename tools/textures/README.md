# Texture audit / restyle tools (pass 9-38)

1. `collect.py <instance minecraft dir> <kubejs/assets dir> <outdir>` - every ingot/nugget/dust item texture as it shows in game
   (priority: mod jars < resource packs in options.txt order < kubejs/assets < cultivar excalibur_style), written to outdir + index.json.
2. `analyze.py <outdir>` - alpha-mask shape vs the category consensus (IoU, area, bbox), report.json + contact sheets.
3. `restyle.py <outdir> <assets_out>` - recolours a style template onto every off-style texture: each template shade is mapped (by
   luminance rank) to the source texture's own colour at the same rank, so the material colour is kept and the shape/shading is the template's.
   Templates: Excalibur iron_ingot / iron_nugget, Neo Vitae iron_dust. Animated sources keep their frames.
Run with `python3 -I`.
