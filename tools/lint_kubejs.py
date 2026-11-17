"""Lint KubeJS scripts for Rhino 2101 pitfalls: `const` inside a try block (throws "redeclaration of var" on every call)
or a loop body (throws on the second iteration). Use `let` there.

usage: python3 -I tools/lint_kubejs.py [dir ...]   (default: modpack/overrides/kubejs)
"""
import os, re, sys


def strip(src):
    """Blank out comments and string/template literals, keeping offsets and newlines."""
    out, i, n = list(src), 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith('//', i):
            j = src.find('\n', i)
            j = n if j < 0 else j
            out[i:j] = ' ' * (j - i); i = j
        elif src.startswith('/*', i):
            j = src.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out[i:j] = [ch if ch == '\n' else ' ' for ch in src[i:j]]; i = j
        elif c in '\'"`':
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == '\\' else 1
            out[i + 1:j] = [ch if ch == '\n' else ' ' for ch in src[i + 1:j]]; i = j + 1
        else:
            i += 1
    return ''.join(out)


def match(s, i):
    """i at an opening brace/paren; return index of its match."""
    o = s[i]; cl = {'{': '}', '(': ')'}[o]; d = 0
    for j in range(i, len(s)):
        if s[j] == o: d += 1
        elif s[j] == cl:
            d -= 1
            if d == 0: return j
    return len(s)


def body_after(s, i):
    """i just after a loop header / try keyword: return (start, end) of the body."""
    while i < len(s) and s[i].isspace(): i += 1
    if i < len(s) and s[i] == '{': return i, match(s, i)
    j = s.find('\n', i)  # single-statement body
    return i, (len(s) if j < 0 else j)


for root in sys.argv[1:] or [os.path.join(os.path.dirname(__file__), "..", "modpack", "overrides", "kubejs")]:
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.js'):
                continue
            p = os.path.join(dp, f)
            src = open(p, encoding='utf8', errors='replace').read()
            s = strip(src)
            hits = set()
            for m in re.finditer(r'\b(for|while)\s*\(|\btry\b', s):
                if m.group(0) == 'try':
                    a, b = body_after(s, m.end())
                else:
                    a, b = body_after(s, match(s, m.end() - 1) + 1)
                for c in re.finditer(r'\bconst\b', s[a:b]):
                    hits.add(a + c.start())
            for h in sorted(hits):
                line = src.count('\n', 0, h) + 1
                print(f'{os.path.relpath(p, root)}:{line}: {src.splitlines()[line - 1].strip()[:110]}')
