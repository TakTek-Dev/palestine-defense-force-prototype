"""The page shell every built page shares: head, strip, masthead, drawer, section nav, footer, loader.

Imported by build.py (home) and pages.py (everything else). C.R is the path back to the site root;
pages in folders set it to '../', the 404 page to the absolute site path.
"""
import datetime as dt
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '7'                                       # bump on any asset change (Chrome caches hard)
SITE = 'Palestine Defense Force'
BASE_URL = 'https://taktek-dev.github.io/palestine-defense-force-prototype/'
E = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))
PH_P = os.path.join(ROOT, 'tools', 'photos.json')
PH = json.load(open(PH_P, encoding='utf-8')) if os.path.exists(PH_P) else {}
DIM_P = os.path.join(ROOT, 'tools', 'out', 'photos.json')
DIM = json.load(open(DIM_P, encoding='utf-8')) if os.path.exists(DIM_P) else {}
esc = html.escape
D = dt.date.fromisoformat
TODAY = D(E['date'])


class Ctx:
    R = ''


C = Ctx()

SECTIONS = [  # slug, nav label, page title, standfirst
    ('detention', 'Detention', 'Detention', 'Arrests, administrative detention, prison conditions and the people held, followed from the night of the arrest to the day of release.'),
    ('courts', 'Courts', 'Courts', 'Military courts, the Supreme Court in Jerusalem and the petitions lawyers bring there, ruling by ruling.'),
    ('land', 'Land & homes', 'Land and homes', 'Demolition orders, evictions, permits refused and the communities fighting them in Area C and East Jerusalem.'),
    ('gaza', 'Gaza', 'Gaza', 'The law of war as it applies to Gaza: detainees taken from the Strip, aid, hospitals and the evidence kept for courts.'),
    ('international', 'International law', 'International law', 'The International Court of Justice, the International Criminal Court, the UN and the states that answer to them.'),
    ('children', 'Children', 'Children', 'Children arrested, interrogated and tried, and the rules that are supposed to protect them.'),
    ('speech', 'Speech', 'Speech and protest', 'Arrests over posts, songs, sermons and slogans, and the laws used to make them.'),
]
SEC = {s[0]: s for s in SECTIONS}

STATUS = {  # kind: (label, one-line meaning)
    'sentenced': ('Sentenced', 'Tried and sentenced. The record is closed.'),
    'remand': ('Remand', 'Held for interrogation or trial. The record is open.'),
    'administrative': ('Administrative detention', 'Held without charge on a secret file, by renewable order.'),
    'unlawful_combatant': ('“Unlawful combatant”', 'Held outside the courts under the 2002 law, mostly from Gaza.'),
    'released': ('Released', 'Out of custody.'),
    'died_in_custody': ('Died in custody', 'Held by Israel when they died.'),
}
COMMUNITY = {
    'demolition_order': 'Demolition orders',
    'evicted': 'Evicted',
    'pending_ruling': 'Awaiting a ruling',
    'ruled': 'Ruled',
}


def day(d, year=False, wd=False):
    """'2026-10-27' -> '27 Oct'; a date known only to the month or year prints as much as is known."""
    if isinstance(d, str) and len(d) == 4:
        return d
    if isinstance(d, str) and len(d) == 7:
        return dt.date.fromisoformat(d + '-01').strftime('%b %Y')
    d = D(d) if isinstance(d, str) else d
    s = f"{d.day} {d.strftime('%b')}" + (f" {d.year}" if year else '')
    return (d.strftime('%a') + ' ' + s) if wd else s


def long_day(d):
    d = D(d) if isinstance(d, str) else d
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B')} {d.year}"


def n(v):
    return f'{v:,}'


# ---------------------------------------------------------------- icons and marks
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="i-right" viewBox="0 0 16 16"><path d="M3 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-search" viewBox="0 0 16 16"><path d="M7 2.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9zM10.4 10.4 14 14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-out" viewBox="0 0 16 16"><path d="M6 3.5H3.5v9h9V10M9 3h4v4M13 3 7.5 8.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-menu" viewBox="0 0 16 16"><path d="M2.5 5h11M2.5 11h11" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-x" viewBox="0 0 16 16"><path d="m3.5 3.5 9 9m0-9-9 9" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-play" viewBox="0 0 16 16"><path d="M5 3.2v9.6c0 .5.5.8.9.5l7-4.8a.6.6 0 0 0 0-1L5.9 2.7c-.4-.3-.9 0-.9.5z" fill="currentColor"/></symbol>
<symbol id="i-pause" viewBox="0 0 16 16"><rect x="4" y="3" width="2.6" height="10" rx=".8" fill="currentColor"/><rect x="9.4" y="3" width="2.6" height="10" rx=".8" fill="currentColor"/></symbol>
</defs></svg>'''


def icon(name, cls='ic'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'


def status_svg(kind, label=None):
    s = MARKS['status'][kind]
    a = f'role="img" aria-label="{esc(label)}"' if label else 'aria-hidden="true"'
    return f'<svg viewBox="0 0 {s["w"]} 64" {a}>{s["body"]}</svg>'


def status_tag(kind, night=False):
    lab = STATUS.get(kind, (COMMUNITY.get(kind, kind),))[0]
    glyph = status_svg(kind) if kind in MARKS['status'] else status_svg('remand')
    return f'<span class="st{" st--night" if night else ""}">{glyph}{esc(lab)}</span>'


def lockup(cls='', night=False, label=SITE):
    L = MARKS['lockup']
    ink = 'currentColor'
    stamp = 'var(--stamp-night)' if night else 'var(--stamp)'
    return (f'<svg class="{cls}" viewBox="0 {L["y0"]:.2f} {L["w"]} {L["h"]:.2f}" role="img" aria-label="{esc(label)}">'
            f'<path class="b" d="{L["br"]}" fill="{ink}"/><path class="l1" d="{L["l1"]}" fill="{ink}"/>'
            f'<path class="l2" d="{L["l2"]}" fill="{ink}"/><path class="dot" d="{L["dot"]}" fill="{stamp}"/></svg>')


def mark_svg(cls='mk', label=None):
    a = f'role="img" aria-label="{esc(label)}"' if label else 'aria-hidden="true"'
    g = MARKS['dot']
    return (f'<svg class="{cls}" viewBox="0 0 64 64" {a}><path d="{MARKS["bracket"]}" fill="currentColor"/>'
            f'<circle cx="{g[0]}" cy="{g[1]}" r="{g[2]}" fill="var(--stamp-night,#9A90FF)"/></svg>')


# ---------------------------------------------------------------- photographs
def photo(slug, sizes='100vw', cls='ph ph--32', eager=False, caption=False):
    if not slug or slug not in PH or slug not in DIM:
        return ''
    p = PH[slug]
    dm = DIM[slug]
    pos = f' style="object-position:{p["focus"]}"' if p.get('focus') else ''
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    img = (f'<div class="{cls}"><img src="{C.R}assets/img/photo/{slug}.webp?v={V}" width="{dm["w"]}" height="{dm["h"]}" '
           f'alt="{esc(p["alt"])}" sizes="{sizes}" {load}{pos}></div>')
    if caption:
        return f'<figure style="margin:0">{img}<figcaption>{esc(p["caption"])} Photo: {esc(p["author"])}, {esc(p["license"])}.</figcaption></figure>'
    return img


# ---------------------------------------------------------------- links
def story_url(sid):
    return f'{C.R}story/{sid}.html'


def case_url(cid):
    return f'{C.R}case/{cid}.html'


def sec_link(slug):
    return f'<a class="label" href="{C.R}{slug}.html">{esc(SEC[slug][1])}</a>'


# ---------------------------------------------------------------- shell
NAV = [('cases', 'Case files'), ('docket', 'The docket'), ('rights', 'Know your rights'), ('about', 'About')]


def head(title, desc, path, og=None, extra=''):
    t = f'{title} · {SITE}' if title != SITE else f'{SITE} — legal defense and the record of Palestinians held'
    url = BASE_URL + path
    og = og or BASE_URL + 'assets/og.png'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(t)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#101117">
<link rel="icon" href="{C.R}favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="{C.R}assets/fonts/mona.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{C.R}assets/fonts/petrona.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{C.R}assets/css/pdf.css?v={V}">
<script>(function(){{try{{var f=/[?&]loader/.test(location.search);if(f||!sessionStorage.getItem('pdf-in')){{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('ld-on')}}}}catch(e){{}}}})()</script>
{extra}
</head>
'''


def loader():
    return f'<div class="ld" aria-hidden="true">{lockup("", label="")}</div>'


def top(current=None):
    tabs = ''.join(f'<a href="{C.R}{s[0]}.html"{" aria-current=page" if current == s[0] else ""}>{esc(s[1])}</a>' for s in SECTIONS[:5])
    sec = ''.join(f'<a href="{C.R}{s[0]}.html"{" aria-current=page" if current == s[0] else ""}>{esc(s[1])}</a>' for s in SECTIONS)
    sec += ''.join(f'<a href="{C.R}{p}.html"{" aria-current=page" if current == p else ""}>{esc(l)}</a>' for p, l in NAV)
    drawer = ''.join(f'<a href="{C.R}{s[0]}.html">{esc(s[1])}<small>{icon("i-right")}</small></a>' for s in SECTIONS)
    drawer += ''.join(f'<a href="{C.R}{p}.html">{esc(l)}<small>{icon("i-right")}</small></a>' for p, l in NAV)
    held = E['docket']['latest']
    return f'''<body>
{SPRITE}
{loader()}
<a class="skip" href="#main">Skip to the record</a>
<div class="util"><div class="wrap">
<span class="live"><i></i>{long_day(TODAY)}</span>
<span class="util-r"><a href="{C.R}docket.html">{n(held["total"])} held · {n(held["administrative"])} without charge</a><a href="{C.R}help.html">Request a lawyer</a></span>
</div></div>
<header class="mast"><div class="wrap">
<a class="brand" href="{C.R}home.html" aria-label="{SITE}, front page">{lockup()}</a>
<nav class="tabs" aria-label="Sections">{tabs}</nav>
<div class="mast-tools">
<a class="icon-btn" href="{C.R}search.html" aria-label="Search the record">{icon("i-search")}</a>
<a class="btn btn--stamp" href="{C.R}help.html">Request a lawyer</a>
<button class="icon-btn menu-btn" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu">{icon("i-menu")}</button>
</div></div></header>
<nav class="secnav" aria-label="All sections"><div class="wrap">{sec}</div></nav>
<div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Menu">
<div class="drawer-h">{lockup()}<button class="icon-btn" type="button" data-close aria-label="Close menu">{icon("i-x")}</button></div>
<nav>{drawer}</nav>
<a class="btn btn--stamp" href="{C.R}help.html">Request a lawyer {icon("i-right")}</a>
</div>
<main id="main">
'''


def help_band():
    return f'''<section class="help"><div class="wrap">
<div><h2>Someone you know was arrested tonight?</h2>
<p>Write down the time, the place, the unit if you saw it, and the names of everyone taken. Then ask for a lawyer: the first hours decide what the record will say.</p></div>
<div class="help-r"><a class="btn" href="{C.R}help.html">Request a lawyer {icon("i-right")}</a>
<small>Or go straight to the legal-aid groups listed on the <a class="ln" href="{C.R}rights.html">Know your rights</a> page.</small></div>
</div></section>'''


def foot(js=True):
    secs = ''.join(f'<li><a href="{C.R}{s[0]}.html">{esc(s[2])}</a></li>' for s in SECTIONS)
    return f'''</main>
<footer class="foot"><div class="wrap">
<div class="foot-top">
<div>{lockup(night=True)}<p>A legal-defense desk for Palestinians: who is held, on what law, in which court, and what can be done about it. Every figure is linked to its source.</p></div>
<div><h4>Sections</h4><ul>{secs}</ul></div>
<div><h4>The record</h4><ul><li><a href="{C.R}docket.html">The docket</a></li><li><a href="{C.R}cases.html">Case files</a></li><li><a href="{C.R}rights.html">Know your rights</a></li><li><a href="{C.R}search.html">Search</a></li></ul></div>
<div><h4>Us</h4><ul><li><a href="{C.R}about.html">About</a></li><li><a href="{C.R}method.html">How we keep the record</a></li><li><a href="{C.R}help.html">Request a lawyer</a></li><li><a href="{C.R}credits.html">Credits</a></li><li><a href="{C.R}index.html">Identity book</a></li></ul></div>
</div>
<div class="foot-bot"><span>© {TODAY.year} {SITE}. Design prototype; reporting summarised from the sources linked on each page.</span><span>Photographs: Wikimedia Commons, credited on each.</span></div>
</div></footer>
{f'<script src="{C.R}assets/js/pdf.js?v={V}" defer></script>' if js else ''}
</body>
</html>
'''
