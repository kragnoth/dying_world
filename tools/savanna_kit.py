"""
savanna_kit.py - pass 7-1: gradient ('BDubs') palette engine + building primitives for the new savanna houses.

Buildings are drawn with ROLE blocks ("role:<name>", props); finalize() turns every role cell into a real block:
  score = vertical position in its wall band (dark/rough base -> light/clean top) + smooth clustered noise (value noise, +-.12)
          - shade (overhang/porch/eave above the outward face, interior corner) - ruin shift (ruined variants: darker near the ground)
  block = ramp[style][role][round(score * (len-1))]
Stairs/slab roles keep their props (facing/half/shape/type). Ruined variants additionally get replace-only wear (moss/cracks) and
furniture swaps (beds -> carpet, job blocks -> rubble, potted plants -> dead bush, lanterns half kept, cobwebs) - never missing parts.
"""
import math
from nbtw import Tpl
from buildkit import M, R, H4, rng, worn, full, stairs, slab, door, bed, table, chair, lantern, hang_lantern, pot, fix_connections

# ---------------- ramps (dark/rough -> light/clean) ----------------
RAMPS = {
    "hacienda": {"wall": ["cobblestone", "stone_bricks", "smooth_sandstone", "white_terracotta", "white_terracotta"],
                 "base": ["cobblestone", "stone_bricks", "stone_bricks"], "floor": ["brown_terracotta", "terracotta", "terracotta", "smooth_sandstone"],
                 "trim": ["stripped_acacia_log"], "beam": ["acacia_log"], "roof": "brick", "ridge": "red_sandstone", "inner": ["smooth_sandstone", "white_terracotta"], "ceil": "acacia"},
    "creole":   {"wall": ["stripped_birch_wood", "birch_planks", "birch_planks", "white_terracotta"],
                 "base": ["cobblestone", "stone_bricks", "stone_bricks"], "floor": ["spruce_planks", "spruce_planks", "birch_planks"],
                 "trim": ["stripped_acacia_log"], "beam": ["acacia_log"], "roof": "dark_oak", "ridge": "dark_oak", "inner": ["birch_planks"], "ceil": "birch"},
    "limestone": {"wall": ["cobblestone", "stone_bricks", "sandstone", "cut_sandstone", "smooth_sandstone"],
                  "base": ["cobblestone", "andesite", "polished_andesite"], "floor": ["spruce_planks", "spruce_planks", "acacia_planks"],
                  "trim": ["polished_andesite"], "beam": ["acacia_log"], "roof": "spruce", "ridge": "spruce", "inner": ["cut_sandstone", "smooth_sandstone"], "ceil": "spruce"},
}
# 9-1 plains family sub-styles (temperate 1800s: clapboard farmhouse, Tudor timber frame, fieldstone cottage)
RAMPS.update({
    "farmhouse": {"wall": ["spruce_planks", "oak_planks", "birch_planks", "white_terracotta"], "base": ["cobblestone", "stone_bricks", "stone_bricks"],
                  "floor": ["spruce_planks", "oak_planks", "oak_planks"], "trim": ["stripped_oak_log"], "beam": ["oak_log"], "roof": "dark_oak", "ridge": "dark_oak",
                  "inner": ["oak_planks"], "ceil": "oak"},
    "timber":    {"wall": ["stone_bricks", "mud_bricks", "white_terracotta", "white_terracotta"], "base": ["cobblestone", "stone_bricks", "stone_bricks"],
                  "floor": ["spruce_planks", "spruce_planks", "oak_planks"], "trim": ["stripped_dark_oak_log"], "beam": ["dark_oak_log"], "roof": "spruce", "ridge": "spruce",
                  "inner": ["white_terracotta"], "ceil": "spruce"},
    "fieldstone": {"wall": ["cobblestone", "stone", "stone_bricks", "polished_andesite"], "base": ["cobblestone", "cobblestone", "stone_bricks"],
                   "floor": ["spruce_planks", "oak_planks", "oak_planks"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "oak", "ridge": "oak",
                   "inner": ["stone_bricks"], "ceil": "spruce"}})
# 9-4 taiga family sub-styles
RAMPS.update({
    "logcabin":   {"wall": ["dark_oak_planks", "spruce_planks", "stripped_spruce_wood", "stripped_spruce_wood"], "base": ["cobblestone", "cobblestone", "stone_bricks"],
                   "floor": ["dark_oak_planks", "spruce_planks", "spruce_planks"], "trim": ["spruce_log"], "beam": ["stripped_dark_oak_log"], "roof": "dark_oak", "ridge": "dark_oak",
                   "inner": ["spruce_planks"], "ceil": "spruce"},
    "stonetimber": {"wall": ["cobblestone", "stone_bricks", "spruce_planks", "stripped_spruce_wood"], "base": ["cobblestone", "cobblestone", "stone_bricks"],
                    "floor": ["spruce_planks", "spruce_planks", "dark_oak_planks"], "trim": ["dark_oak_log"], "beam": ["dark_oak_log"], "roof": "spruce", "ridge": "spruce",
                    "inner": ["spruce_planks"], "ceil": "dark_oak"},
    "heavystone": {"wall": ["cobblestone", "cobblestone", "stone_bricks", "andesite"], "base": ["cobblestone", "cobblestone", "stone"],
                   "floor": ["spruce_planks", "dark_oak_planks", "spruce_planks"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "dark_oak", "ridge": "dark_oak",
                   "inner": ["stone_bricks"], "ceil": "spruce"}})
# 9-5 snowy + desert sub-styles
RAMPS.update({
    "chalet": {"wall": ["stone_bricks", "spruce_planks", "stripped_spruce_wood", "stripped_spruce_wood"], "base": ["cobblestone", "stone_bricks", "stone_bricks"],
               "floor": ["spruce_planks", "spruce_planks", "dark_oak_planks"], "trim": ["stripped_dark_oak_log"], "beam": ["dark_oak_log"], "roof": "dark_oak", "ridge": "dark_oak",
               "inner": ["spruce_planks"], "ceil": "spruce"},
    "frost":  {"wall": ["cobblestone", "stone_bricks", "polished_diorite", "polished_diorite"], "base": ["cobblestone", "packed_ice", "stone_bricks"],
               "floor": ["spruce_planks", "spruce_planks", "birch_planks"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "spruce", "ridge": "spruce",
               "inner": ["stone_bricks"], "ceil": "spruce"},
    "adobe":  {"wall": ["mud_bricks", "packed_mud", "smooth_sandstone", "white_terracotta"], "base": ["sandstone", "cut_sandstone", "cut_sandstone"],
               "floor": ["terracotta", "smooth_sandstone", "smooth_sandstone"], "trim": ["stripped_spruce_log"], "beam": ["spruce_log"], "roof": "smooth_sandstone", "ridge": "smooth_sandstone",
               "inner": ["smooth_sandstone"], "ceil": "spruce"},
    "sandstone": {"wall": ["sandstone", "cut_sandstone", "smooth_sandstone", "smooth_sandstone"], "base": ["sandstone", "sandstone", "cut_sandstone"],
                  "floor": ["spruce_planks", "smooth_sandstone", "smooth_sandstone"], "trim": ["chiseled_sandstone"], "beam": ["stripped_spruce_log"], "roof": "sandstone", "ridge": "sandstone",
                  "inner": ["cut_sandstone"], "ceil": "spruce"}})
RUIN_SWAP = {"polished_diorite": "diorite", "packed_ice": "cobblestone", "packed_mud": "mud_bricks", "dark_oak_planks": "stripped_dark_oak_wood", "andesite": "cobblestone", "oak_planks": "stripped_oak_wood", "spruce_planks": "stripped_spruce_wood", "stone": "cobblestone", "polished_andesite": "andesite", "mud_bricks": "packed_mud","white_terracotta": "light_gray_terracotta", "smooth_sandstone": "sandstone", "cut_sandstone": "sandstone", "birch_planks": "stripped_birch_wood",
             "stone_bricks": "cracked_stone_bricks", "cobblestone": "mossy_cobblestone", "terracotta": "brown_terracotta", "acacia_planks": "stripped_acacia_wood"}
RUIN_ROOF = {"brick": "mossy_stone_brick", "dark_oak": "dark_oak", "spruce": "spruce", "smooth_sandstone": "sandstone", "sandstone": "sandstone"}
WOODS = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "bamboo", "crimson", "warped")
def full_of(fam): return fam + "_planks" if fam in WOODS else fam + "s" if fam.endswith(("brick", "tile")) else fam
JOBS = ("smoker", "grindstone", "lectern", "brewing_stand", "composter", "barrel_job", "blast_furnace", "fletching_table", "cartography_table", "loom", "stonecutter", "smithing_table")

def vnoise(x, y, z, seed, scale=3.0):
    """smooth value noise in [-1,1] (trilinear over a hashed lattice) -> clustered, not dotty"""
    def h(i, j, k):
        n = (i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (seed * 2654435761)
        n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
        return (n & 0xFFFF) / 32767.5 - 1
    fx, fy, fz = x / scale, y / scale, z / scale
    ix, iy, iz = math.floor(fx), math.floor(fy), math.floor(fz)
    tx, ty, tz = fx - ix, fy - iy, fz - iz
    s = lambda t: t * t * (3 - 2 * t)
    tx, ty, tz = s(tx), s(ty), s(tz)
    acc = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                wgt = (tx if dx else 1 - tx) * (ty if dy else 1 - ty) * (tz if dz else 1 - tz)
                acc += wgt * h(ix + dx, iy + dy, iz + dz)
    return acc

class B:
    """building canvas: Tpl + role cells + metadata"""
    def __init__(self, name, style, W, H, D, seed=1):
        self.t = Tpl(W, H + (8 if B.STEEP else 0), D); self.style, self.name, self.seed = style, name, seed   # steep roofs need headroom
        self.r = rng(name, seed); self.band = {}; self.family = "savanna"          # role cell -> (y_lo, y_hi) of its wall band
    def set(self, x, y, z, name, props=None, nbt=None): self.t.set(x, y, z, name, props, nbt)
    def role(self, x, y, z, role, props=None, band=None):
        self.t.set(x, y, z, "role:" + role, props)
        if band: self.band[(x, y, z)] = band
    def get(self, x, y, z): return self.t.b.get((x, y, z), ("",))[0]
    def clear(self, x0, x1, y0, y1, z0, z1):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1): self.set(x, y, z, M("air"))

    # ---------- primitives ----------
    GROUND = ("dirt_path", "coarse_dirt", "grass_block", "coarse_dirt")   # 9-5: per-family yard ground (desert sand, snowy snow ...)
    def ground(self, mat_choices=None):
        t = self.t; mat_choices = mat_choices or B.GROUND
        for x in range(t.sx):
            for z in range(t.sz):
                self.set(x, 0, z, M(self.r.choice(mat_choices)))
                for y in range(1, 4): self.set(x, y, z, M("air"))
    def walls(self, x0, x1, z0, z1, y0, y1, role="wall", corners="trim", base_h=1, floor=True):
        """hollow box: floor at y0 (role floor), walls y0+1..y1, corner posts; lowest base_h wall courses use role 'base'"""
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                edge = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
                if floor: self.role(x, y0, z, "base" if edge else "floor")
                for y in range(y0 + 1, y1 + 1):
                    if not edge: self.set(x, y, z, M("air")); continue
                    if corner and corners: self.role(x, y, z, corners, {"axis": "y"}); continue
                    self.role(x, y, z, "base" if y <= y0 + base_h else role, band=(y0 + 1, y1))
    def floor_layer(self, x0, x1, z0, z1, y, role="floor"):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1): self.role(x, y, z, role)
    FLAT = False                                                   # 9-5: desert - flat roof with parapet instead of a gable
    STEEP = False                                                  # 9-4: class-level switch; taiga sets it -> 2:1 roofs (snow)
    def gable(self, x0, x1, z0, z1, y, axis="x", over=1, ceiling=True):
        """roof role stairs; ridge along `axis`; gable ends filled with role wall (upper band = light).
        top plate (acacia beam) closes the wall-top gap; ceiling=True adds a flat plank-slab ceiling under the roof (8-7 feedback)."""
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1): self.role(x, y, z, "beam", {"axis": "x" if z in (z0, z1) and x not in (x0, x1) else "z" if x in (x0, x1) and z not in (z0, z1) else "y"})
                elif ceiling and self.get(x, y, z) in ("", M("air")): self.role(x, y, z, "ceil")
        if B.FLAT:
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    edge = x in (x0, x1) or z in (z0, z1)
                    if not edge: self.role(x, y, z, "wall", band=(y - 4, y))          # flat roof deck (light top of the ramp), also the ceiling
                    else:
                        self.role(x, y, z, "wall", band=(y - 4, y))
                        if (x + z) % 4: self.role(x, y + 1, z, "wall", band=(y - 4, y + 1))   # parapet with drainage gaps
            return y + 1
        if B.STEEP: return self._steep(x0, x1, z0, z1, y, axis, over)
        k = 0
        if axis == "x":
            while True:
                za, zb = z0 - over + k, z1 + over - k
                if za > zb: break
                for x in range(x0 - over, x1 + over + 1):
                    if za == zb: self.role(x, y + k, za, "roof_slab", {"type": "bottom"})
                    else:
                        self.role(x, y + k, za, "roof", {"facing": "south", "half": "bottom", "shape": "straight"})
                        self.role(x, y + k, zb, "roof", {"facing": "north", "half": "bottom", "shape": "straight"})
                if k >= over:
                    for x in (x0, x1):
                        for zz in range(za, zb + 1): self.role(x, y + k - 1, zz, "wall", band=(y - 3, y + k))
                if zb - za <= 1: break
                k += 1
        else:
            while True:
                xa, xb = x0 - over + k, x1 + over - k
                if xa > xb: break
                for z in range(z0 - over, z1 + over + 1):
                    if xa == xb: self.role(xa, y + k, z, "roof_slab", {"type": "bottom"})
                    else:
                        self.role(xa, y + k, z, "roof", {"facing": "east", "half": "bottom", "shape": "straight"})
                        self.role(xb, y + k, z, "roof", {"facing": "west", "half": "bottom", "shape": "straight"})
                if k >= over:
                    for z in (z0, z1):
                        for xx in range(xa, xb + 1): self.role(xx, y + k - 1, z, "wall", band=(y - 3, y + k))
                if xb - xa <= 1: break
                k += 1
        return y + k
    def _steep(self, x0, x1, z0, z1, y, axis, over):
        """2:1 gable: each roof row = full roof block + stairs on top; next row one in, two up. Gable ends filled with wall role."""
        sw = (lambda a, b: (a, b)) if axis == "x" else (lambda a, b: (b, a))           # (along, across) -> (x, z)
        a0, a1, c0, c1 = (x0, x1, z0, z1) if axis == "x" else (z0, z1, x0, x1)
        lo_f, hi_f = ("south", "north") if axis == "x" else ("east", "west")
        k = 0
        while True:
            ca, cb = c0 - over + k, c1 + over - k
            if ca > cb: break
            yy = y + 2 * k
            for a in range(a0 - over, a1 + over + 1):
                if ca == cb:
                    X, Z = sw(a, ca); self.role(X, yy, Z, "roof_full"); self.role(X, yy + 1, Z, "roof_slab", {"type": "bottom"})
                else:
                    for c, f in ((ca, lo_f), (cb, hi_f)):
                        X, Z = sw(a, c)
                        self.role(X, yy, Z, "roof_full"); self.role(X, yy + 1, Z, "roof", {"facing": f, "half": "bottom", "shape": "straight"})
            if k >= over:
                for a in (a0, a1):
                    for c in range(ca + 1, cb):
                        for dy in (-1, 0, 1):                        # -1 closes the course between this row and the one below
                            X, Z = sw(a, c)
                            if not self.get(X, yy + dy, Z).startswith("role:roof"): self.role(X, yy + dy, Z, "wall", band=(y - 3, yy + 2))
            if cb - ca <= 1: break
            k += 1
        return y + 2 * k + 1
    def shed_roof(self, x0, x1, z0, z1, y, down="south"):
        """single-pitch roof (porches, verandas) falling towards `down`"""
        rows = list(range(z0, z1 + 1)) if down in ("south", "north") else list(range(x0, x1 + 1))
        if down in ("north", "west"): rows = rows[::-1]
        for i, a in enumerate(rows):
            yy = y + (len(rows) - 1 - i) // 2
            half = "bottom" if (len(rows) - 1 - i) % 2 == 0 else "top"
            for b_ in (range(x0, x1 + 1) if down in ("south", "north") else range(z0, z1 + 1)):
                x, z = (b_, a) if down in ("south", "north") else (a, b_)
                self.role(x, y + (len(rows) - 1 - i) // 2 if False else yy, z, "roof_slab", {"type": half})
    def window(self, x, y, z, normal, shutters=True, tall=False):
        """glass pane in the wall + open trapdoor shutters on the outside either side"""
        for dy in ((0, 1) if tall else (0,)): self.set(x, y + dy, z, M("glass_pane"))
        if not shutters: return
        nx, nz = H4[normal]; side = [(1, 0), (-1, 0)] if nz else [(0, 1), (0, -1)]
        for sx, sz in side:
            for dy in ((0, 1) if tall else (0,)):
                p = (x + nx + sx, y + dy, z + nz + sz)
                if 0 <= p[0] < self.t.sx and 0 <= p[2] < self.t.sz and self.get(*p) in ("", M("air")):
                    self.set(*p, M("dark_oak_trapdoor"), {"facing": normal, "half": "bottom", "open": "true", "powered": "false", "waterlogged": "false"})
    def entrance(self, x, z, lived):
        """vanilla street hookup: building_entrance jigsaw at (x,1,z) on the front row (+ villager spawn jigsaw beside it when lived)"""
        self.set(x, 1, z, M("jigsaw"), {"orientation": "south_up"}, {"id": M("jigsaw"), "name": "minecraft:building_entrance", "target": "minecraft:building_entrance",
                 "pool": "minecraft:empty", "final_state": M("structure_void"), "joint": "aligned"})
        if lived:
            vx = x - 1 if x > 0 else x + 1
            self.set(vx, 0, z, M("jigsaw"), {"orientation": "up_north"}, {"id": M("jigsaw"), "name": "minecraft:bottom", "target": "minecraft:bottom",
                     "pool": f"minecraft:village/{self.family}/villagers", "final_state": M("dirt_path"), "joint": "rollable"})
    def chest(self, x, y, z, facing, table=None):
        table = table or f"minecraft:chests/village/village_{self.family}_house"
        self.set(x, y, z, M("chest"), {"facing": facing, "type": "single", "waterlogged": "false"}, {"id": M("chest"), "LootTable": table})
    def job(self, x, y, z, name, props=None):
        self.set(x, y, z, M(name), props); self.t.b[(x, y, z)] = (M(name), self.t.b[(x, y, z)][1], {"__job": "1"})

    # ---------- finalize ----------
    def finalize(self, variant):
        """variant: base | lived | ruined"""
        t, st, rs = self.t, RAMPS[self.style], self.seed * 7 + (3 if variant == "ruined" else 0)
        r = rng(self.name + variant, self.seed); ruined = variant == "ruined"
        def solid(p): n = t.b.get(p, ("",))[0]; return bool(n) and n != M("air") and n != M("structure_void")
        for (x, y, z), (name, props, nbt) in list(t.b.items()):
            if not name.startswith("role:"): continue
            role = name[5:]; props = dict(props)
            if role in ("roof", "roof_slab", "roof_full"):
                fam = st["roof"]
                if ruined and r.random() < .25 + .25 * (vnoise(x, y, z, rs) > .2): fam = RUIN_ROOF.get(fam, fam)
                if role == "roof": t.set(x, y, z, M(f"{fam}_stairs"), dict(props, waterlogged="false"))
                elif role == "roof_slab":
                    ridge = st["ridge"]
                    t.set(x, y, z, M(f"{ridge if props.get('type') == 'bottom' and ridge != fam else fam}_slab"), dict(props, waterlogged="false"))
                else: t.set(x, y, z, M(full_of(fam)))
                continue
            ramp = st.get(role, st["wall"])
            if role == "ceil":
                t.set(x, y, z, M(f"{st['ceil']}_slab"), {"type": "top", "waterlogged": "false"}); continue
            if role in ("trim", "beam"):
                b = ramp[0]
                if ruined and r.random() < .3: b = b.replace("stripped_", "") if "stripped_" in b else b
                t.set(x, y, z, M(b), {"axis": props.get("axis", "y")} if b.endswith(("_log", "_wood")) else None); continue
            lo, hi = self.band.get((x, y, z), (0, t.sy - 1))
            hrel = 0 if hi <= lo else (y - lo) / (hi - lo)
            score = .1 + .85 * hrel + .13 * vnoise(x, y, z, rs)
            if role == "base":                                    # base course: mid of its ramp, clustered breakup only
                score = .45 + .25 * vnoise(x, y, z, rs, 2.5)
            elif role == "floor":                                   # floors: darker towards the walls (ambient occlusion)
                walls_near = sum(solid((x + dx, y + 1, z + dz)) for dx, dz in H4.values())
                score = .75 - .22 * walls_near + .12 * vnoise(x, y, z, rs, 2.5)
            else:                                                 # shade: something solid above the outward face (eave, porch, balcony)
                for dx, dz in H4.values():
                    if not solid((x + dx, y, z + dz)) and any(solid((x + dx, y + k, z + dz)) for k in (1, 2, 3)): score -= .2; break
            if ruined: score -= .45 * (1 - hrel) + .1
            i = max(0, min(len(ramp) - 1, round(score * (len(ramp) - 1))))
            b = ramp[i]
            if ruined:
                if r.random() < .35 * (1.2 - hrel): b = RUIN_SWAP.get(b, b)
                b = worn(r, M(b), 1.5 - hrel)[len("minecraft:"):]
            t.set(x, y, z, M(b), {"axis": props.get("axis", "y")} if b.endswith(("_log", "_wood")) else None)
        if ruined: self._ruin_props(r)
        if variant == "base": self._strip_jigsaws()
        for p, (name, props, nbt) in list(t.b.items()):           # drop internal job markers
            if nbt and "__job" in nbt: t.b[p] = (name, props, None)
        fix_connections(t)
        return t
    def _strip_jigsaws(self):
        for p, (name, props, nbt) in list(self.t.b.items()):
            if name == M("jigsaw") and nbt and nbt.get("pool") != "minecraft:empty": self.t.b[p] = (M("dirt_path"), (), None)
    def _ruin_props(self, r):
        t = self.t
        for (x, y, z), (name, props, nbt) in list(t.b.items()):
            n = name.split(":")[-1]; props = dict(props)
            if n.endswith("_bed"): t.set(x, y, z, M("brown_carpet") if props.get("part") == "foot" else M("white_carpet") if r.random() < .5 else M("brown_carpet"))
            elif nbt and "__job" in nbt: t.set(x, y, z, M("cobblestone") if r.random() < .6 else M("mossy_cobblestone"))
            elif n.startswith("potted_"): t.set(x, y, z, M("potted_dead_bush"))
            elif n in ("wheat", "carrots", "potatoes", "beetroots", "melon_stem", "pumpkin_stem"): t.set(x, y, z, M("dead_bush") if r.random() < .5 else M("short_grass"))
            elif n == "farmland": t.set(x, y, z, M("coarse_dirt"))
            elif n == "lantern" and r.random() < .5: t.set(x, y, z, M("air")) if props.get("hanging") == "false" else None
            elif name == M("jigsaw") and nbt and "villagers" in str(nbt.get("pool", "")): t.set(x, y, z, M("dirt_path"))
        # cobwebs in a few upper interior corners
        air_corners = [(x, y, z) for (x, y, z), (n, _, _) in t.b.items() if n == M("air") and y >= 3
                       and sum(full(t.b.get((x + dx, y, z + dz), ("",))[0]) for dx, dz in H4.values()) >= 2 and full(t.b.get((x, y + 1, z), ("",))[0])]
        r.shuffle(air_corners)
        for p in air_corners[:4]: t.set(*p, M("cobweb"))
