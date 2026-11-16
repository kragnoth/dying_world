"""nbtrw.py - typed NBT round-trip (no deps). read(bytes_gz)->('root' typed tree), write(tree)->bytes_gz.
Typed tree: (tag, value); compound value = dict name->(tag, value); list value = (item_tag, [values]); arrays kept as raw bytes (tag 7/11/12).
Used to EDIT existing structure NBTs (append palette/blocks/entities) without losing tag types."""
import gzip, struct

def read(gz):
    data = gzip.decompress(gz); pos = [0]
    def r(fmt):
        s = struct.calcsize(fmt); v = struct.unpack_from(fmt, data, pos[0])[0]; pos[0] += s; return v
    def string():
        n = r(">H"); s = data[pos[0]:pos[0] + n].decode("utf8"); pos[0] += n; return s
    def pay(t):
        if t in (1, 2, 3, 4, 5, 6): return r({1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}[t])
        if t in (7, 11, 12):
            n = r(">i"); k = {7: 1, 11: 4, 12: 8}[t]; b = data[pos[0]:pos[0] + n * k]; pos[0] += n * k; return (n, b)
        if t == 8: return string()
        if t == 9:
            it = r(">b"); n = r(">i"); return (it, [pay(it) for _ in range(n)])
        if t == 10:
            d = {}
            while True:
                tt = r(">b")
                if tt == 0: return d
                k = string(); d[k] = (tt, pay(tt))
        raise ValueError(t)
    t = r(">b"); string(); return (t, pay(t))

def _s(s): b = s.encode("utf8"); return struct.pack(">H", len(b)) + b
def _pay(t, v):
    if t in (1, 2, 3, 4, 5, 6): return struct.pack({1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}[t], v)
    if t in (7, 11, 12): n, b = v; return struct.pack(">i", n) + b
    if t == 8: return _s(v)
    if t == 9:
        it, items = v; return struct.pack(">bi", it if items else (it or 0), len(items)) + b"".join(_pay(it, x) for x in items)
    if t == 10: return b"".join(struct.pack(">b", tt) + _s(k) + _pay(tt, vv) for k, (tt, vv) in v.items()) + b"\x00"
    raise ValueError(t)

def write(tree):
    t, v = tree; return gzip.compress(struct.pack(">b", t) + _s("") + _pay(t, v), mtime=0)

class Struct:
    """convenience view over a structure NBT: blocks as {(x,y,z): (name, props_dict, nbt_typed_or_None)}"""
    def __init__(self, gz):
        self.tree = read(gz); root = self.tree[1]
        self.size = [v for v in root["size"][1][1]]
        pal = root["palette"][1][1]
        self.pal = [(p["Name"][1], {k: vv for k, (tt, vv) in p.get("Properties", (10, {}))[1].items()}) for p in pal]
        self.b = {}
        for blk in root["blocks"][1][1]:
            pos = tuple(blk["pos"][1][1]); name, props = self.pal[blk["state"][1]]
            self.b[pos] = (name, dict(props), blk.get("nbt"))
        self.ents = list(root.get("entities", (9, (10, [])))[1][1])
    def set(self, x, y, z, name, props=None, nbt=None): self.b[(x, y, z)] = (name, dict(props or {}), nbt)
    def entity(self, x, y, z, nbt):
        self.ents.append({"pos": (9, (6, [float(x), float(y), float(z)])), "blockPos": (9, (3, [int(x), int(y), int(z)])), "nbt": (10, nbt)})
    def bytes(self):
        root = dict(self.tree[1]); pal, idx, blocks = [], {}, []
        for pos in sorted(self.b, key=lambda p: (p[1], p[2], p[0])):
            name, props, nbt = self.b[pos]; k = (name, tuple(sorted(props.items())))
            if k not in idx:
                idx[k] = len(pal); e = {"Name": (8, name)}
                if props: e["Properties"] = (10, {a: (8, str(c)) for a, c in sorted(props.items())})
                pal.append(e)
            e = {"pos": (9, (3, list(pos))), "state": (3, idx[k])}
            if nbt: e["nbt"] = nbt
            blocks.append(e)
        root["palette"] = (9, (10, pal)); root["blocks"] = (9, (10, blocks)); root["entities"] = (9, (10, self.ents)); root["size"] = (9, (3, list(self.size)))
        root.pop("palettes", None)
        return write((10, root))
