"""Minimal SNBT reader/writer for FTB Quests files (unquoted keys, newline- or comma-separated, typed number suffixes).
Numbers keep their suffix as Num(value, suffix) so a round trip writes them back unchanged."""
import re
class Num:
    def __init__(s, v, suf): s.v, s.suf = v, suf
    def __repr__(s): return f"{s.v}{s.suf}"
    def __eq__(s, o): return isinstance(o, Num) and o.v == s.v and o.suf == s.suf
TOK = re.compile(r'\s*(?:(\{)|(\})|(\[)|(\])|(:)|(,)|("(?:[^"\\]|\\.)*")|([^\s{}\[\]:,"]+))', re.S)
def tokens(s):
    pos = 0; out = []
    while True:
        m = TOK.match(s, pos)
        if not m or m.end() == pos:
            if s[pos:].strip(): raise ValueError(f"bad snbt at {pos}: {s[pos:pos+40]!r}")
            return out
        pos = m.end(); g = m.lastindex; out.append((g, m.group(g)))
def atom(t):
    if t in ('true', 'false'): return t == 'true'
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)([bBsSlLfFdD]?)', t)
    if m:
        v = float(m.group(1)) if ('.' in m.group(1) or 'e' in m.group(1).lower() or m.group(2) in 'dDfF' and m.group(2)) else int(m.group(1))
        return Num(v, m.group(2)) if m.group(2) else v
    return t
def parse(s):
    tk = tokens(s); i = 0
    def val():
        nonlocal i
        g, t = tk[i]; i += 1
        if g == 1:
            d = {}
            while tk[i][0] != 2:
                if tk[i][0] == 6: i += 1; continue
                k = tk[i][1]; k = bytes(k[1:-1], 'utf-8').decode('unicode_escape') if k.startswith('"') else k; i += 1
                assert tk[i][0] == 5, tk[i - 3:i + 2]; i += 1; d[k] = val()
            i += 1; return d
        if g == 3:
            if i + 1 < len(tk) and tk[i + 1][0] == 7 and False: pass
            if tk[i][0] == 8 and tk[i][1] in ('I', 'B', 'L') and i + 1 < len(tk) and tk[i + 1][1] == ';': pass
            l = []
            while tk[i][0] != 4:
                if tk[i][0] == 6: i += 1; continue
                l.append(val())
            i += 1; return l
        if g == 7: return bytes(t[1:-1], 'utf-8').decode('unicode_escape')
        return atom(t)
    v = val(); return v
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
SAFE = re.compile(r'^[A-Za-z0-9_.+-]+$')
def key(k): return k if SAFE.match(k) else q(k)
def dump(v, ind=0):
    t = '\t'
    if isinstance(v, dict):
        if not v: return '{ }'
        inner = [f"{t*(ind+1)}{key(k)}: {dump(v[k], ind+1)}" for k in sorted(v)]
        return '{\n' + '\n'.join(inner) + '\n' + t * ind + '}'
    if isinstance(v, list):
        if not v: return '[ ]'
        if all(not isinstance(x, (dict, list)) for x in v): return '[' + ', '.join(dump(x) for x in v) + ']'
        return '[\n' + '\n'.join(t * (ind + 1) + dump(x, ind + 1) for x in v) + '\n' + t * ind + ']'
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, Num): return repr(v)
    if isinstance(v, (int, float)): return repr(v)
    return q(str(v))
