"""Palestine Defense Force marks.

python -I tools/brand.py   -> assets/brand/*.svg + favicon.svg + tools/out/marks.json

The mark is a square bracket holding a point. In a court record the bracket is the one place the
defense may write into someone else's text: [emphasis added], [sic], [the witness pointed]. Here
it is drawn as two arms that reach over a person and keep them in the record. The point is the
only thing in colour, stamp-pad violet, the ink every affidavit and every receipt from a
military court is stamped in. The person is the colour; everything else is ink.

The bracket is also the site's grammar for what the law has done to someone held:
  [•]  sentenced      tried, a closed record
  [•   remand         charged, the record still open
  [:•  administrative held on a secret file: a bracket with no body, only its ends
   •   unlawful combatant: held outside any court, no bracket at all
  [ ]• released      out of the record
In the lockup the bracket spans the two lines of the name, and holds it.
"""
import io
import json
import os

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'brand')
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)

INK, PAPER, STAMP = '#121419', '#FFFFFF', '#4231D8'
NIGHT, ON_NIGHT, STAMP_NIGHT = '#101117', '#EEF0F4', '#9A90FF'

# the bracket on a 64 grid. Stem and arms share one weight; the arm ends are full round caps,
# the outer corners a generous 9, the inner corners a tight 3, so the bracket reads as drawn
# with a broad pen, not cut from sheet.
X0, Y0, Y1 = 13.0, 6.0, 58.0            # outer left edge, top, foot
W = 8.6                                 # stem and arm weight
TIP = 47.0                              # where the arms end (past the point's centre: they reach over it)
RO, RI = 8.0, 2.4                       # outer and inner corner radii
DOT = (37.5, 32.0, 7.6)                 # the person: centre x, y, radius


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def bracket_d(x0=X0, y0=Y0, y1=Y1, w=W, tip=TIP, ro=RO, ri=RI, k=1.0, ox=0.0, oy=0.0, flip=False):
    """Outline of the bracket as one filled path. flip draws the closing bracket ]."""
    c = ri * 1.25                                     # the arm ends: square, eased, never knife-cut
    pts = [
        ('M', x0 + ro, y0), ('H', tip - c), ('A', c, tip, y0 + c, 1), ('V', y0 + w - c), ('A', c, tip - c, y0 + w, 1),
        ('H', x0 + w + ri), ('A', ri, x0 + w, y0 + w + ri, 0), ('V', y1 - w - ri), ('A', ri, x0 + w + ri, y1 - w, 0),
        ('H', tip - c), ('A', c, tip, y1 - w + c, 1), ('V', y1 - c), ('A', c, tip - c, y1, 1),
        ('H', x0 + ro), ('A', ro, x0, y1 - ro, 1), ('V', y0 + ro), ('A', ro, x0 + ro, y0, 1)]
    mx = (lambda x: 64 - x) if flip else (lambda x: x)
    X = lambda x: f(ox + mx(x) * k)
    Y = lambda y: f(oy + y * k)
    out = []
    for p in pts:
        if p[0] == 'M':
            out.append(f'M{X(p[1])} {Y(p[2])}')
        elif p[0] == 'H':
            out.append(f'H{X(p[1])}')
        elif p[0] == 'V':
            out.append(f'V{Y(p[1])}')
        if p[0] == 'A':
            _, r, x, y, sw = p
            out.append(f'A{f(r * k)} {f(r * k)} 0 0 {sw ^ flip} {X(x)} {Y(y)}')
    return ''.join(out) + 'Z'


def dot(color=STAMP, k=1.0, ox=0.0, oy=0.0, x=None, hollow=False):
    cx, cy, r = DOT
    cx = cx if x is None else x
    if hollow:
        return (f'<circle cx="{f(ox + cx * k)}" cy="{f(oy + cy * k)}" r="{f((r - 1.6) * k)}" fill="none" '
                f'stroke="{color}" stroke-width="{f(3.2 * k)}"/>')
    return f'<circle cx="{f(ox + cx * k)}" cy="{f(oy + cy * k)}" r="{f(r * k)}" fill="{color}"/>'


def mark(ink=INK, stamp=STAMP, k=1.0, ox=0.0, oy=0.0):
    return f'<path d="{bracket_d(k=k, ox=ox, oy=oy)}" fill="{ink}"/>' + dot(stamp, k, ox, oy)


# ---------------------------------------------------------------- statuses
def status(kind, ink=INK, stamp=STAMP):
    """The five states on the 64 grid (viewBox 0 0 64 64; 'sentenced' and 'released' are wider: 0 0 80 64)."""
    if kind == 'sentenced':
        return (f'<path d="{bracket_d(tip=40)}" fill="{ink}"/><path d="{bracket_d(tip=40, flip=True, ox=16)}" fill="{ink}"/>'
                + dot(stamp, x=40))
    if kind == 'remand':
        return mark(ink, stamp)
    if kind == 'administrative':
        arm = lambda y: f'<rect x="{f(X0)}" y="{f(y)}" width="{f(TIP - X0)}" height="{f(W)}" rx="{f(RI * 1.25)}" fill="{ink}"/>'
        return arm(Y0) + arm(Y1 - W) + dot(stamp)
    if kind == 'unlawful_combatant':
        return dot(stamp, x=32)
    if kind == 'released':
        return (f'<path d="{bracket_d(tip=30)}" fill="{ink}"/><path d="{bracket_d(tip=30, flip=True)}" fill="{ink}"/>'
                + dot(stamp, x=68))
    if kind == 'died_in_custody':
        return (f'<path d="{bracket_d(tip=40)}" fill="{ink}"/><path d="{bracket_d(tip=40, flip=True, ox=16)}" fill="{ink}"/>'
                + dot(ink, x=40, hollow=True))
    raise KeyError(kind)


STATUS_BOX = {'sentenced': 80, 'released': 80, 'died_in_custody': 80}

# ---------------------------------------------------------------- type as outlines
_cache = {}


def face(name, axes):
    key = (name, tuple(sorted(axes.items())))
    if key not in _cache:
        font = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, name)), axes)
        buf = io.BytesIO()
        font.save(buf)
        data = buf.getvalue()
        _cache[key] = (TTFont(io.BytesIO(data)), hb.Font(hb.Face(data)))
    return _cache[key]


def text_path(name, axes, text, x, base, size, track=0.0, features=None, tittles=None):
    """Shape with HarfBuzz (kerning), draw with fontTools. Returns (d, advance).

    With tittles=[] the dot of every i is drawn apart and appended to that list as its own path,
    so the lockup can set it in stamp violet: the person inside the name."""
    tt, hf = face(name, axes)
    upm = tt['head'].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hf, buf, features or {'kern': True, 'liga': False, 'calt': False})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = size / upm
    pen = SVGPathPen(gs, ntos=lambda v: f(v))
    cx = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = order[info.codepoint]
        tr = (s, 0, 0, -s, x + (cx + pos.x_offset) * s, base - pos.y_offset * s)
        if tittles is not None and g == tt.getBestCmap()[ord('i')]:
            from fontTools.pens.recordingPen import DecomposingRecordingPen as RecordingPen
            rp = RecordingPen(gs)
            gs[g].draw(rp)
            contours, cur = [], []
            for op in rp.value:
                cur.append(op)
                if op[0] in ('closePath', 'endPath'):
                    contours.append(cur)
                    cur = []
            top = max(contours, key=lambda c: min(p[1] for o, a in c for p in a))
            for c in contours:
                target = SVGPathPen(gs, ntos=lambda v: f(v)) if c is top else pen
                tp = TransformPen(target, tr)
                for o, a in c:
                    getattr(tp, o)(*a)
                if c is top:
                    tittles.append(target.getCommands())
            cx += pos.x_advance + track * upm
            continue
        gs[g].draw(TransformPen(pen, tr))
        cx += pos.x_advance + track * upm
    return pen.getCommands(), (cx - track * upm) * s


def metrics(name, axes):
    tt, _ = face(name, axes)
    upm = tt['head'].unitsPerEm
    os2 = tt['OS/2']
    return os2.sCapHeight / upm, os2.sxHeight / upm


def stem(name, axes, glyph='l'):
    """Width of a vertical stem, as a fraction of the em (measured on the outline bounds)."""
    from fontTools.pens.boundsPen import BoundsPen
    tt, _ = face(name, axes)
    gs = tt.getGlyphSet()
    g = tt.getBestCmap()[ord(glyph)]
    bp = BoundsPen(gs)
    gs[g].draw(bp)
    return (bp.bounds[2] - bp.bounds[0]) / tt['head'].unitsPerEm


MONA = 'MonaSans[wdth,wght].ttf'
WM_AXES = {'wdth': 112, 'wght': 800}


def lockup():
    """Stacked lockup: the bracket spans both lines and holds the name."""
    size, lead = 100.0, 96.0
    cap, _ = metrics(MONA, WM_AXES)
    st = stem(MONA, WM_AXES) * size
    b1, b2 = 100.0, 100.0 + lead
    top, foot = b1 - cap * size, b2
    pad = st * 1.15                                   # air between the arms and the letters
    y0, y1 = top - pad - st, foot + pad + st          # arms sit outside the cap line and baseline
    x0 = 0.0
    tx = x0 + st + pad * 1.35                         # text starts after the stem and its air
    tit = []
    l1, w1 = text_path(MONA, WM_AXES, 'Palestine', tx, b1, size, track=-0.012, tittles=tit)
    l2, w2 = text_path(MONA, WM_AXES, 'Defense Force', tx, b2, size, track=-0.012)
    tip = tx + st * 2.6                               # arms reach over the first letters
    br = bracket_d(x0=x0, y0=y0, y1=y1, w=st, tip=tip, ro=st * 0.82, ri=st * 0.27)
    width = tx + max(w1, w2)
    return {'br': br, 'l1': l1, 'l2': l2, 'dot': tit[0], 'w': round(width + 2, 1), 'y0': y0, 'h': y1 - y0, 'st': st}


def line_mark():
    """One-line wordmark for tight headers: the mark at cap height + the name in one line."""
    size = 100.0
    cap, _ = metrics(MONA, WM_AXES)
    st = stem(MONA, WM_AXES) * size
    k = (cap * size + 2 * st * 1.6) / (Y1 - Y0)       # the mark's height: cap height plus overhang
    oy = 100 - cap * size - st * 1.6 - Y0 * k
    m = mark(k=k, ox=-X0 * k, oy=oy)
    tx = (TIP + 10) * k - X0 * k
    d, w = text_path(MONA, WM_AXES, 'Palestine Defense Force', tx, 100, size, track=-0.012)
    return m, d, tx + w, oy + Y0 * k, (Y1 - Y0) * k


def svg(vb, body, label=None):
    a = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" {a}>{body}</svg>\n'


def write(name, s):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
        fh.write(s)


def main():
    L = lockup()
    vb = f'0 {f(L["y0"])} {f(L["w"])} {f(L["h"])}'
    for name, ink, stamp in (('lockup', INK, STAMP), ('lockup-reverse', ON_NIGHT, STAMP_NIGHT)):
        write(f'{name}.svg', svg(vb, f'<path d="{L["br"]}" fill="{ink}"/><path d="{L["l1"]}" fill="{ink}"/>'
                                    f'<path d="{L["l2"]}" fill="{ink}"/><path d="{L["dot"]}" fill="{stamp}"/>', 'Palestine Defense Force'))
    m, d, w, ly, lh = line_mark()
    for name, ink, stamp in (('wordmark', INK, STAMP), ('wordmark-reverse', ON_NIGHT, STAMP_NIGHT)):
        body = m.replace(INK, ink).replace(STAMP, stamp) + f'<path d="{d}" fill="{ink}"/>'
        write(f'{name}.svg', svg(f'0 {f(ly)} {f(w + 2)} {f(lh)}', body, 'Palestine Defense Force'))
    write('mark.svg', svg('0 0 64 64', mark(), 'Palestine Defense Force'))
    write('mark-reverse.svg', svg('0 0 64 64', mark(ON_NIGHT, STAMP_NIGHT), 'Palestine Defense Force'))
    # avatar and favicon: at icon sizes the point is drawn larger so it never reads as the middle bar of an E
    small = lambda ink, stamp, k, ox, oy: (f'<path d="{bracket_d(k=k, ox=ox, oy=oy, w=W * 1.12)}" fill="{ink}"/>'
                                           + f'<circle cx="{f(ox + 37.5 * k)}" cy="{f(oy + 32 * k)}" r="{f(9.4 * k)}" fill="{stamp}"/>')
    write('avatar.svg', svg('0 0 64 64', f'<rect width="64" height="64" rx="14" fill="{STAMP}"/>'
                            + small(PAPER, INK, .74, 9.6, 8.3), 'Palestine Defense Force'))
    fav = svg('0 0 64 64', f'<rect width="64" height="64" rx="15" fill="{INK}"/>' + small(PAPER, STAMP_NIGHT, .78, 8.2, 7))
    with open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8') as fh:
        fh.write(fav)
    st = {}
    for kind in ('sentenced', 'remand', 'administrative', 'unlawful_combatant', 'released', 'died_in_custody'):
        w = STATUS_BOX.get(kind, 64)
        s = status(kind, 'currentColor', 'var(--stamp)')
        st[kind] = {'w': w, 'body': s}
        write(f'status-{kind}.svg', svg(f'0 0 {w} 64', status(kind), kind.replace('_', ' ')))
    marks = {
        'bracket': bracket_d(), 'dot': DOT, 'grid': {'x0': X0, 'y0': Y0, 'y1': Y1, 'w': W, 'tip': TIP},
        'lockup': L, 'line': {'mark': m, 'name': d, 'w': w + 2, 'y': ly, 'h': lh}, 'status': st,
    }
    with open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), 'w', encoding='utf-8') as fh:
        json.dump(marks, fh)
    print('lockup', L['w'], 'x', round(L['h'], 1), 'stem', round(L['st'], 2))


if __name__ == '__main__':
    main()
