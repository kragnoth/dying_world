"""nbtw.py - tiny structure-NBT writer (no deps). Tpl(sx,sy,sz).set(x,y,z,name,props,nbt_strings) ; .bytes() -> gzipped .nbt (1.21.1)."""
import gzip, struct
DATA_VERSION = 3955
def _s(s): b = s.encode("utf8"); return struct.pack(">H", len(b)) + b
def _pay(t, v):
    if t == 1: return struct.pack(">b", v)
    if t == 5: return struct.pack(">f", v)
    if t == 6: return struct.pack(">d", v)
    if t == 3: return struct.pack(">i", v)
    if t == 8: return _s(v)
    if t == 9:
        it, items = v; return struct.pack(">bi", it, len(items)) + b"".join(_pay(it, x) for x in items)
    if t == 10: return b"".join(struct.pack(">b", tt) + _s(k) + _pay(tt, vv) for k, (tt, vv) in v.items()) + b"\x00"
    raise ValueError(t)
S = lambda v: (8, v); I = lambda v: (3, v); B = lambda v: (1, v); F = lambda v: (5, v); D = lambda v: (6, v)
def L(t, items): return (9, (t, items))
class Tpl:
    def __init__(self, sx, sy, sz): self.sx, self.sy, self.sz, self.b, self.ents = sx, sy, sz, {}, []
    def entity(self, x, y, z, nbt):
        """nbt = typed compound dict {key: (tag, value)} incl. id; x/y/z = float position inside the template"""
        self.ents.append({"pos": L(6, [float(x), float(y), float(z)]), "blockPos": L(3, [int(x), int(y), int(z)]), "nbt": (10, nbt)})
    def set(self, x, y, z, name, props=None, nbt=None):
        assert 0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz, (x, y, z, self.sx, self.sy, self.sz)
        self.b[(x, y, z)] = (name, tuple(sorted((props or {}).items())), nbt)
    def has(self, x, y, z): return (x, y, z) in self.b
    def bytes(self):
        pal, idx, blocks = [], {}, []
        for pos in sorted(self.b, key=lambda p: (p[1], p[2], p[0])):
            name, props, nbt = self.b[pos]; k = (name, props)
            if k not in idx:
                idx[k] = len(pal); e = {"Name": S(name)}
                if props: e["Properties"] = (10, {a: S(str(c)) for a, c in props})
                pal.append(e)
            e = {"pos": L(3, list(pos)), "state": I(idx[k])}
            if nbt: e["nbt"] = (10, {a: (c if isinstance(c, tuple) else S(c)) for a, c in nbt.items()})   # typed values pass through (9-9 spawners)
            blocks.append(e)
        root = {"DataVersion": I(DATA_VERSION), "size": L(3, [self.sx, self.sy, self.sz]),
                "palette": L(10, pal), "blocks": L(10, blocks), "entities": L(10, self.ents)}
        return gzip.compress(struct.pack(">b", 10) + _s("") + _pay(10, root), mtime=0)
