"""rr_connect.py - sets R&R girder/beam end-connection states (neg/pos) on a nbtw.Tpl before it is saved.
WHY: jigsaw/template placement does not recompute neighbour-dependent blockstates, so connections must be written into the NBT.
Jar facts (blockstates + models, rustandrebar 3.6.2.2): rusted_girder axis x/y/z + neg/pos in {girder, column, flange} (only for axis x/z);
rusted_beam axis + low + neg/pos in {girder, column, beam_high, beam_low} (only for axis x/z). A connected end draws an extension that reaches into the
neighbour cell (7/16 for column/girder-in-beam style, thin plate for flange), so pieces visually merge instead of floating.
Rules used (best reading of the names; verify in game). Continuous same-kind runs (girder->girder, beam->beam of same `low`) get NO state (avoids overlapping end plates);
only real joints are set:
  girder end: vertical girder/beam -> column | horizontal beam or perpendicular girder -> flange (sub girder butting into a main I-beam)
  beam end:   vertical girder/beam -> column | any girder -> girder | collinear beam with a different `low` -> beam_high / beam_low
"""
G, B = "rustandrebar:rusted_girder", "rustandrebar:rusted_beam"
def connect(t):
    n = 0
    for pos, (name, props, nbt) in list(t.b.items()):
        if name not in (G, B): continue
        p = dict(props); ax = p.get("axis")
        if ax not in ("x", "z"): continue
        for end, s in (("neg", -1), ("pos", 1)):
            q = (pos[0] + s, pos[1], pos[2]) if ax == "x" else (pos[0], pos[1], pos[2] + s)
            nb = t.b.get(q)
            if not nb or nb[0] not in (G, B): continue
            nq = dict(nb[1]); nax = nq.get("axis"); val = None
            if nax == "y": val = "column"
            elif name == G:
                if not (nb[0] == G and nax == ax): val = "flange"
            else:
                if nb[0] == G: val = "girder"
                elif nb[0] == B and nax == ax and nq.get("low", "false") != p.get("low", "false"): val = "beam_low" if nq.get("low") == "true" else "beam_high"
            if val: p[end] = val; n += 1
        t.b[pos] = (name, tuple(sorted(p.items())), nbt)
    return n
