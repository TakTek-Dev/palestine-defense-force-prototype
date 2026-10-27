"""Second round of pages, and the fuller versions of the story, case, section and guide pages.

Called from pages.py main(); not run on its own.
  story/<id>.html   breadcrumb, reading time, copy link, previous/next in the section, NewsArticle JSON-LD
  case/<id>.html    related cases, photo in the share card
  <section>.html    the newest story as a lead, the rest grouped by month
  rights/<id>.html  numbered points, print button, the glossary terms that belong to the guide
  status/<kind>.html   one page per group on the docket: definition, the month-by-month line, cases
  archive.html, glossary.html, directory.html, contact.html, corrections.html, privacy.html
"""
import datetime as dt
import json
import os

import shell as S
from shell import C, E, SEC, SECTIONS, esc, n, icon, photo, story_url, case_url, status_svg, day, long_day
import build as B
import pages as P

ROOT = S.ROOT
ST = E['stories']
GL = json.load(open(os.path.join(ROOT, 'tools', 'glossary.json'), encoding='utf-8'))
GUIDE = {g['id']: g for g in E['guides']}
ORGS = json.load(open(os.path.join(ROOT, 'research', 'news.json'), encoding='utf-8'))['orgs']

# the four groups of the docket: key in the series, status glyph, page slug, title, guide, line
KINDS = [
    ('sentenced', 'sentenced', 'sentenced', 'Sentenced', 'military-courts',
     'People tried, convicted and serving a sentence, nearly all of them by Israeli military courts.'),
    ('remand', 'remand', 'remand', 'Remand', 'military-courts',
     'People under interrogation, charged and awaiting trial, or on trial. Their record is still open.'),
    ('administrative', 'administrative', 'administrative', 'Administrative detention', 'administrative-detention',
     'People held without charge or trial on a commander’s order, renewed every six months or less, on a file they may not see.'),
    ('unlawful_combatants', 'unlawful_combatant', 'unlawful-combatants', '“Unlawful combatants”', 'unlawful-combatants-law',
     'People held under the 2002 Unlawful Combatants Law, almost all of them from Gaza, outside any criminal court.'),
]
KIND_BY_STATUS = {'sentenced': 'sentenced', 'remand': 'remand', 'administrative': 'administrative', 'unlawful_combatant': 'unlawful-combatants'}


def crumbs(*parts):
    """parts: (label, href or None)"""
    li = ''.join(f'<li>{f"""<a href="{h}">{esc(l)}</a>""" if h else f"""<span aria-current="page">{esc(l)}</span>"""}</li>' for l, h in parts)
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{li}</ol></nav>'


def minutes(paras):
    w = sum(len(p.split()) for p in paras)
    return max(1, round(w / 220))


def og_photo(slug):
    return f'{S.BASE_URL}assets/img/photo/{slug}.webp' if slug and slug in S.DIM else None


def jsonld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


# ---------------------------------------------------------------- story
def story(sid):
    s = ST[sid]
    C.R = '../'
    sec = s['section']
    ids = [i for i in E['by_date'] if ST[i]['section'] == sec]
    k = ids.index(sid)
    newer = ids[k - 1] if k > 0 else None
    older = ids[k + 1] if k + 1 < len(ids) else None
    figs = ''.join(f'<div class="fig"><span class="num">{esc(f["v"])}</span><span>{esc(f["label"])}</span></div>' for f in s.get('figures', []))
    aside = f'<div class="box"><span class="label">In figures</span><div class="figs">{figs}</div></div>' if figs else ''
    aside += P.sources_box(s['sources'])
    if s.get('differ'):
        aside += f'<div class="box box--differ"><span class="label">Where the sources differ</span><p>{esc(s["differ"])}</p></div>'
    if not s.get('verified'):
        aside += '<p class="note">Reported by one outlet so far. We will add a second source, or correct this page, when there is one.</p>'
    cs = [c for c in E['cases'] if sid in c.get('stories', [])]
    if cs:
        aside += ('<div class="box"><span class="label">Case file</span>' + ''.join(
            f'<a class="st st--link" href="{case_url(c["id"])}">{status_svg(c["status"]) if c["status"] in S.MARKS["status"] else ""}{esc(c["title"])}</a>' for c in cs) + '</div>')
    terms = [g for g in GL if any(w.lower() in ' '.join(s['body']).lower() for w in [g['term'].strip('“”').split(' (')[0]])][:4]
    if terms:
        aside += ('<div class="box"><span class="label">Terms in this story</span><ul class="terms">' + ''.join(
            f'<li><a href="../glossary.html#{g["id"]}">{esc(g["term"])}</a></li>' for g in terms) + '</ul></div>')
    body = ''.join(f'<p>{esc(p)}</p>' for p in s['body'])
    fig = photo(s.get('photo'), '(max-width:1180px) 100vw, 1180px', 'ph ph--169', eager=True, caption=True)
    rel = ''.join(B.card(i, '(max-width:640px) 100vw, 25vw') for i in P.related(sid))
    pn = ''
    if newer or older:
        cell = lambda i, lab, cls: (f'<a class="pn-a {cls}" href="{i}.html"><span class="label">{lab}</span><b>{esc(ST[i]["headline"])}</b>'
                                    f'<span class="meta">{day(ST[i]["date"], True)}</span></a>') if i else ''
        pn = f'<nav class="pn" aria-label="More in {esc(SEC[sec][2])}">{cell(older, "← Earlier in " + SEC[sec][1], "pn-prev")}{cell(newer, "Later in " + SEC[sec][1] + " →", "pn-next")}</nav>'
    url = f'{S.BASE_URL}story/{sid}.html'
    ld = jsonld({'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': s['headline'], 'description': s['dek'],
                 'datePublished': s['date'], 'dateModified': E['date'], 'mainEntityOfPage': url,
                 'image': [og_photo(s.get('photo'))] if og_photo(s.get('photo')) else [S.BASE_URL + 'assets/og.png'],
                 'publisher': {'@type': 'Organization', 'name': S.SITE, 'logo': {'@type': 'ImageObject', 'url': S.BASE_URL + 'assets/brand/avatar.svg'}},
                 'isBasedOn': [x['url'] for x in s['sources']]})
    html = f'''<article>
<header class="art-h"><div class="wrap">{crumbs(("Front page", "../home.html"), (SEC[sec][2], f"../{sec}.html"), ("This story", None))}
<h1>{esc(s["headline"])}</h1><p class="dek">{esc(s["dek"])}</p>
<div class="art-meta"><p class="meta"><span><b>{long_day(s["date"])}</b></span><span>{esc(s["place"])}</span><span>{minutes(s["body"])} min read</span><span>{len(s["sources"])} source{"s" if len(s["sources"]) > 1 else ""}</span></p>
<button class="chip chip--sm" type="button" data-copy="{url}">{icon("i-link")}<span>Copy link</span></button></div></div></header>
{f'<div class="art-fig">{fig}</div>' if fig else ''}
<div class="art"><div><div class="prose">{body}</div>{pn}</div><aside class="aside">{aside}</aside></div>
</article>
<section class="block" style="margin-top:48px"><div class="wrap"><div class="block-h"><h2 class="bh">Also on the record</h2></div><div class="grid rail-x">{rel}</div></div></section>'''
    P.write(f'story/{sid}.html', S.head(s['headline'], s['dek'], f'story/{sid}.html', og=og_photo(s.get('photo')), extra=ld, kind='article')
            + S.top(sec) + html + S.help_band() + S.foot())


# ---------------------------------------------------------------- case
def case(c):
    C.R = '../'
    person = c['kind'] == 'person'
    if person:
        lab, line = S.STATUS.get(c['status'], (c['status'], ''))
        big = ''
        if c.get('since'):
            until = c.get('until')
            days = (S.D(until) if until else S.TODAY).toordinal() - S.D(c['since']).toordinal()
            big = (f'<span class="num" data-since="{c["since"]}"{f" data-until={until}" if until else ""}>{days:,}</span>'
                   f'<b>{esc(c.get("clock_label", "days held"))}</b><span class="meta">since {day(c["since"], True)}</span>')
        elif c.get('figure'):
            big = f'<span class="num">{esc(c["figure"])}</span><b>{esc(c.get("figure_label", ""))}</b>'
        glyph = status_svg(c['status'], lab) if c['status'] in S.MARKS['status'] else ''
        kslug = KIND_BY_STATUS.get(c['status'])
        st = f'<a class="st st--link" href="../status/{kslug}.html">{esc(lab)} {icon("i-right")}</a>' if kslug else f'<span class="st">{esc(lab)}</span>'
    else:
        lab, line = S.COMMUNITY.get(c['status'], c['status']), ''
        big = f'<span class="num">{esc(c.get("figure", ""))}</span><b>{esc(c.get("figure_label", ""))}</b>' if c.get('figure') else ''
        glyph, st = '', f'<span class="st">{esc(lab)}</span>'
    tl = ''.join(f'<li><time>{day(t["date"], True)}</time><p>{esc(t["event"])}</p>{f"""<a href="{t["source_url"]}" rel="noopener">Source</a>""" if t.get("source_url") else ""}</li>' for t in c['timeline'])
    stories = ''.join(B.card(i) for i in c.get('stories', []) if i in ST)
    others = [x for x in E['cases'] if x['id'] != c['id'] and (x['kind'] == c['kind'])][:4]
    more = ''.join(B.case_card(x) for x in others)
    fig = photo(c.get('photo'), '(max-width:980px) 100vw, 640px', 'ph ph--32', caption=True)
    html = f'''<header class="case-h"><div class="wrap"><div>
{crumbs(("Front page", "../home.html"), ("Case files", "../cases.html"), (c["title"].split(",")[0], None))}
<h1>{esc(c["title"])}</h1><p class="dek">{esc(c["summary"])}</p><p class="meta" style="margin-top:16px">{esc(c["place"])}</p></div>
<div class="big">{glyph}{big}{st}{f'<span class="meta">{esc(line)}</span>' if line else ''}</div></div></header>
<div class="art"><div><h2 class="bh" style="font-size:26px;margin-bottom:24px">The record, in order</h2><ol class="tl">{tl}</ol>
{f'<div style="margin-top:20px">{fig}</div>' if fig else ''}</div>
<aside class="aside">{P.sources_box(c["sources"])}<p class="note">Status checked {day(E["date"], True)}. If you know of a later order or ruling, tell us through the <a class="ln" href="../contact.html">contact form</a>.</p></aside></div>
{f'<section class="block" style="margin-top:40px"><div class="wrap"><div class="block-h"><h2 class="bh">Reporting on this case</h2></div><div class="grid rail-x">{stories}</div></div></section>' if stories else ''}
{f'<section class="block block--mist"><div class="wrap"><div class="block-h"><h2 class="bh">Other case files</h2><a class="more" href="../cases.html">All case files {icon("i-right")}</a></div><div class="cases rail-x">{more}</div></div></section>' if more else ''}'''
    P.write(f'case/{c["id"]}.html', S.head(c['title'], c['summary'], f'case/{c["id"]}.html', og=og_photo(c.get('photo'))) + S.top('cases') + html + S.help_band() + S.foot())


# ---------------------------------------------------------------- section: lead, then months
def month_groups(ids):
    out, cur = [], None
    for i in ids:
        m = ST[i]['date'][:7]
        if m != cur:
            out.append((m, []))
            cur = m
        out[-1][1].append(i)
    return out


def months_html(ids):
    h = ''
    for m, group in month_groups(ids):
        lab = dt.date.fromisoformat(m + '-01').strftime('%B %Y')
        h += f'<h2 class="month" id="m-{m}"><span>{lab}</span><span class="meta">{len(group)} on the record</span></h2><div class="list">{"".join(P.item(i) for i in group)}</div>'
    return h


def section(slug):
    C.R = ''
    t = SEC[slug]
    ids = [i for i in E['by_date'] if ST[i]['section'] == slug]
    lead = next((i for i in ids if ST[i].get('photo')), ids[0])
    rest = [i for i in ids if i != lead]
    s = ST[lead]
    cs = [c for c in E['cases'] if any(ST.get(x, {}).get('section') == slug for x in c.get('stories', []))]
    body = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "home.html"), (t[2], None))}<h1>{esc(t[2])}</h1><p>{esc(t[3])}</p>
<p class="meta" style="margin-top:16px">{len(ids)} stories · latest {day(ST[ids[0]]["date"], True)}</p></div></header>
<section class="block"><div class="wrap lead lead--sec"><a class="lead-main" href="story/{lead}.html">{photo(s.get("photo"), "(max-width:980px) 100vw, 58vw", "ph ph--169", eager=True)}
<h2>{esc(s["headline"])}</h2><p class="dek">{esc(s["dek"])}</p><p class="meta">{long_day(s["date"])} · {esc(s["place"])}</p></a>
<div class="rail"><span class="label">Case files here</span>{"".join(f"""<a class="row row--np" href="case/{c["id"]}.html"><div><span class="label">{esc(S.STATUS.get(c["status"], (S.COMMUNITY.get(c["status"], ""),))[0])}</span><h3>{esc(c["title"])}</h3></div></a>""" for c in cs) or '<p class="note" style="margin-top:14px">No open case file in this section yet.</p>'}
<a class="more" href="cases.html">All case files {icon("i-right")}</a></div></div></section>
<div class="wrap">{months_html(rest)}</div><div style="height:56px"></div>'''
    P.write(f'{slug}.html', P.page(f'{slug}.html', t[2], t[3], body + S.help_band(), slug))


# ---------------------------------------------------------------- guides
def guide(i, x):
    C.R = '../'
    pts = ''.join(f'<li id="p{j + 1}"><span class="pnum">§{i + 1}.{j + 1}</span><p>{esc(p["text"])}</p>{f"""<a href="{p["source_url"]}" rel="noopener">Source</a>""" if p.get("source_url") else ""}</li>' for j, p in enumerate(x['points']))
    terms = [g for g in GL if g.get('guide') == x['id']]
    tbox = ('<div class="box"><span class="label">Words used here</span><dl class="dl">' + ''.join(
        f'<dt><a href="../glossary.html#{g["id"]}">{esc(g["term"])}</a></dt><dd>{esc(g["def"].split(". ")[0].rstrip("."))}.</dd>' for g in terms) + '</dl></div>') if terms else ''
    g = E['guides']
    others = ''.join(f'<a class="guide" href="{y["id"]}.html"><span class="num">§{j + 1}</span><h3>{esc(y["title"])}</h3><p>{esc(y["line"])}</p></a>' for j, y in enumerate(g) if y['id'] != x['id'])
    stat = next((k for k in KINDS if k[4] == x['id']), None)
    sbox = (f'<a class="box box--link" href="../status/{stat[2]}.html"><span class="label">On the docket</span>{status_svg(stat[1])}'
            f'<span class="num stamp" style="font-size:34px">{n(E["docket"]["latest"][stat[0]])}</span><span class="meta">{esc(stat[3])}, {esc(E["docket"]["latest"]["label"])}</span></a>') if stat else ''
    html = f'''<header class="art-h"><div class="wrap">{crumbs(("Front page", "../home.html"), ("Know your rights", "../rights.html"), (f"§{i + 1}", None))}
<h1>{esc(x["title"])}</h1><p class="dek">{esc(x["line"])}</p>
<div class="art-meta"><p class="meta"><span>{len(x["points"])} points</span><span>Checked {day(E["date"], True)}</span></p>
<button class="chip chip--sm" type="button" data-print>{icon("i-print")}<span>Print this guide</span></button></div></div></header>
<div class="art"><div><ol class="tl tl--plain tl--guide">{pts}</ol></div><aside class="aside">{sbox}{tbox}<p class="note">This guide explains the law in general. It is not advice on a particular case: for that, ask a lawyer as early as you can.</p>
<a class="btn btn--stamp" href="../help.html">Request a lawyer {icon("i-right")}</a></aside></div>
<section class="block" style="margin-top:40px"><div class="wrap"><div class="block-h"><h2 class="bh">The other guides</h2></div><div class="guides">{others}</div></div></section>'''
    P.write(f'rights/{x["id"]}.html', S.head(x['title'], x['line'], f'rights/{x["id"]}.html') + S.top('rights') + html + S.foot())


# ---------------------------------------------------------------- status pages and their chart
def chart(key):
    ser = E['docket']['series']
    W, H, L, R, T, Bm = 820, 300, 54, 18, 18, 36
    t0 = dt.date.fromisoformat(ser[0]['as_of'])
    t1 = dt.date.fromisoformat(ser[-1]['as_of'])
    span = (t1 - t0).days
    X = lambda d: L + (dt.date.fromisoformat(d) - t0).days / span * (W - L - R)
    top = max(s['total'] for s in ser)
    step = 2000 if top > 6000 else 1000
    ymax = (top // step + 1) * step
    Y = lambda v: T + (1 - v / ymax) * (H - T - Bm)
    grid = ''.join(f'<path d="M{L} {Y(v):.1f}H{W - R}"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{v:,}</text>' for v in range(0, ymax + 1, step))
    years = ''.join(f'<text x="{X(f"{y}-01-01"):.1f}" y="{H - 12}" text-anchor="middle">{y}</text><path class="yr" d="M{X(f"{y}-01-01"):.1f} {T}V{H - Bm}"/>'
                    for y in range(t0.year + 1, t1.year + 1))
    tot = ' '.join(f'{X(s["as_of"]):.1f},{Y(s["total"]):.1f}' for s in ser)
    pts = [(X(s['as_of']), Y(s[key]), s) for s in ser]
    line = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _ in pts)
    area = f'M{pts[0][0]:.1f} {Y(0):.1f}L' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y, _ in pts) + f'L{pts[-1][0]:.1f} {Y(0):.1f}Z'
    dots = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2"><title>{s["label"]}: {s[key]:,}</title></circle>' for x, y, s in pts)
    lx, ly, ls = pts[-1]
    hi = max(pts, key=lambda p: p[2][key])
    return f'''<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ch-t"><title id="ch-t">Month by month, {ser[0]["label"]} to {ser[-1]["label"]}; the table below gives every figure.</title>
<g class="g">{grid}{years}</g><polyline class="tot" points="{tot}"/><path class="ar" d="{area}"/><polyline class="ln" points="{line}"/><g class="pt">{dots}</g>
<text class="lab" x="{lx - 6:.1f}" y="{ly - 12:.1f}" text-anchor="end">{ls[key]:,}</text>
{f'<text class="lab lab--hi" x="{hi[0]:.1f}" y="{hi[1] - 12:.1f}" text-anchor="middle">highest shown {hi[2][key]:,}</text>' if hi is not pts[-1] else ''}
<text class="tl-lab" x="{pts[0][0] + 4:.1f}" y="{Y(ser[0]["total"]) - 8:.1f}">all held</text></svg>'''


def status_pages():
    d = E['docket']
    L, ser = d['latest'], d['series']
    first = ser[0]
    for key, glyph, slug, title, gid, line in KINDS:
        C.R = '../'
        cs = [c for c in E['cases'] if KIND_BY_STATUS.get(c['status']) == slug]
        rows = ''.join(f'<tr><td>{esc(s["label"])}</td><td><b>{n(s[key])}</b></td><td>{round(s[key] / s["total"] * 100)}%</td><td>{n(s["total"])}</td></tr>' for s in reversed(ser))
        g = GUIDE.get(gid)
        nav = ''.join(f'<a class="chip{" chip--on" if k[2] == slug else ""}" href="{k[2]}.html"{" aria-current=page" if k[2] == slug else ""}>{status_svg(k[1])}{esc(k[3])}</a>' for k in KINDS)
        change = L[key] - first[key]
        html = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "../home.html"), ("The docket", "../docket.html"), (title, None))}
<div class="stat-h"><div>{status_svg(glyph, title)}<h1>{esc(title)}</h1><p>{esc(line)}</p></div>
<div class="stat-n"><span class="num">{n(L[key])}</span><span class="meta">{esc(L["label"])} · {round(L[key] / L["total"] * 100)}% of all {n(L["total"])} held</span>
<span class="meta">{"+" if change >= 0 else "−"}{n(abs(change))} since {esc(first["label"])}</span></div></div>
<nav class="filters" aria-label="Groups on the docket">{nav}</nav></div></header>
<section class="block"><div class="wrap"><h2 class="bh" style="font-size:26px;margin-bottom:20px">Month by month</h2>
<figure class="chart-f">{chart(key)}<figcaption>The line is this group; the thin line above it is everyone held. Israel Prison Service figures as published by <a class="ln" href="{d["source"]["url"]}">HaMoked</a>.</figcaption></figure>
<div class="art art--wide" style="margin-top:36px">
<div class="scroll-x"><table class="tbl"><thead><tr><th scope="col">Month</th><th scope="col">{esc(title)}</th><th scope="col">Share</th><th scope="col">All held</th></tr></thead><tbody>{rows}</tbody></table></div>
<aside class="aside">{f"""<a class="box box--link" href="../rights/{g["id"]}.html"><span class="label">The law behind it</span><b class="box-t">{esc(g["title"])}</b><span class="meta">{esc(g["line"])}</span></a>""" if g else ""}
{f"""<div class="box"><span class="label">Case files in this group</span>{"".join(f'<a class="st st--link" href="../case/{c["id"]}.html">{status_svg(c["status"])}{esc(c["title"])}</a>' for c in cs)}</div>""" if cs else ""}
<p class="note">{esc(d["note"])}</p></aside></div></div></section>'''
        P.write(f'status/{slug}.html', S.head(f'{title} · the docket', line, f'status/{slug}.html') + S.top('docket') + html + S.help_band() + S.foot())


# ---------------------------------------------------------------- archive
def archive():
    C.R = ''
    ids = E['by_date']
    chips = '<button class="chip" type="button" data-v="all" aria-pressed="true">All</button>' + ''.join(
        f'<button class="chip" type="button" data-v="{s[0]}" aria-pressed="false">{esc(s[1])} <span class="meta">{sum(1 for i in ids if ST[i]["section"] == s[0])}</span></button>' for s in SECTIONS)
    body = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "home.html"), ("Archive", None))}<h1>Archive</h1>
<p>Everything on the record, newest first. {len(ids)} stories from {day(ST[ids[-1]]["date"], True)} to {day(ST[ids[0]]["date"], True)}.</p>
<div class="filters" data-filter=".arch .item">{chips}</div></div></header>
<div class="wrap arch">{months_html(ids)}</div><div style="height:56px"></div>'''
    P.write('archive.html', P.page('archive.html', 'Archive', 'Every story on the record, newest first.', body, 'archive'))


# ---------------------------------------------------------------- glossary
def glossary():
    C.R = ''
    idx = {g['id']: g for g in GL}
    letters = sorted({g['term'].strip('“”')[0] for g in GL})
    jump = ''.join(f'<a href="#l-{l}">{l}</a>' for l in letters)
    items, cur = '', None
    for g in sorted(GL, key=lambda g: g['term'].strip('“”').lower()):
        l = g['term'].strip('“”')[0]
        if l != cur:
            items += f'<h2 class="month" id="l-{l}"><span>{l}</span></h2>'
            cur = l
        see = ', '.join(f'<a href="#{s}">{esc(idx[s]["term"])}</a>' for s in g.get('see', []) if s in idx)
        gd = GUIDE.get(g.get('guide'))
        items += f'''<dl class="term" id="{g["id"]}"><dt>{status_svg(g["status"]) if g.get("status") else ""}<span>{esc(g["term"])}</span></dt>
<dd><p>{esc(g["def"])}</p><p class="meta">{f"See also {see}. " if see else ""}{f"""Guide: <a href="rights/{gd["id"]}.html">{esc(gd["title"])}</a>. """ if gd else ""}<a href="{g["source"]}" rel="noopener">Source</a></p></dd></dl>'''
    body = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "home.html"), ("Glossary", None))}<h1>Glossary</h1>
<p>The words of detention law and the courts, in plain English, each with its source.</p><nav class="az" aria-label="Jump to a letter">{jump}</nav></div></header>
<div class="wrap"><div class="gl">{items}</div></div><div style="height:56px"></div>'''
    P.write('glossary.html', P.page('glossary.html', 'Glossary', 'The words of detention law and the courts, in plain English.', body + S.help_band(), 'glossary'))


# ---------------------------------------------------------------- directory
def directory():
    C.R = ''
    live = [o for o in ORGS if o.get('url')]
    closed = [o for o in ORGS if not o.get('url')]
    host = lambda u: u.split('//')[1].split('/')[0].replace('www.', '')
    cards = ''.join(f'''<a class="dir rv" href="{o["url"]}" rel="noopener"><b>{esc(o["name"])}</b><p>{esc(o["description"])}</p>
<span class="meta">{esc(host(o["url"]))} {icon("i-out")}</span></a>''' for o in live)
    gone = ''.join(f'<div class="dir dir--closed"><b>{esc(o["name"])}</b><p>{esc(o["description"])}</p></div>' for o in closed)
    body = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "home.html"), ("Legal-aid directory", None))}<h1>Legal-aid directory</h1>
<p>The groups that defend Palestinians in court, document what happens to them, or both. Reach them through their own sites: we do not list phone numbers we cannot check.</p></div></header>
<section class="block"><div class="wrap"><div class="dirs">{cards}</div>
{f'<h2 class="bh" style="font-size:22px;margin:48px 0 16px">No longer operating</h2><div class="dirs">{gone}</div>' if gone else ''}</div></section>'''
    P.write('directory.html', P.page('directory.html', 'Legal-aid directory', 'Legal-aid and rights groups defending Palestinians.', body + S.help_band(), 'directory'))


# ---------------------------------------------------------------- contact, corrections, privacy
def small_pages():
    C.R = ''
    contact = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "home.html"), ("Contact", None))}<h1>Write to the desk</h1>
<p>A correction, a later ruling on a case we follow, a document we should read. If someone has just been arrested, use <a class="ln" href="help.html">Request a lawyer</a> instead: it goes to the legal-aid desk first.</p></div></header>
<div class="art" style="margin-top:40px"><form class="form" id="contact-form">
<label>What is it about?<select name="topic"><option>A correction</option><option>An update on a case file</option><option>A document or a source</option><option>Something else</option></select></label>
<label>Page it concerns <small>Optional. Paste the address.</small><input name="page" type="url" placeholder="https://"></label>
<label>Your message<textarea name="msg" required></textarea><small>Link to the order, ruling or report if you can. We check before we change anything.</small></label>
<label>Your email<input name="email" type="email" autocomplete="email" required><small>Only to reply to you. See <a class="ln" href="privacy.html">Privacy</a>.</small></label>
<button class="btn btn--stamp" type="submit" style="justify-self:start">Send {icon("i-right")}</button>
<p class="note" id="contact-done" tabindex="-1" hidden>Prototype: nothing was sent.</p></form>
<aside class="aside"><div class="box"><span class="label">What happens next</span><ol class="record"><li><span>We read every message.</span></li><li><span>A correction is checked against its source before the page changes.</span></li><li><span>Every change is logged on <a href="corrections.html">Corrections</a> with its date.</span></li></ol></div></aside></div><div style="height:64px"></div>'''
    P.write('contact.html', P.page('contact.html', 'Contact', 'Write to the desk: corrections, case updates, documents.', contact, 'contact'))

    corr = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "home.html"), ("Corrections", None))}<h1>Corrections</h1>
<p>When we get something wrong we correct the page, say what changed and when, and list it here. We do not delete the mistake from the record.</p></div></header>
<div class="art" style="margin-top:40px"><div><div class="empty">{status_svg("released")}<h2>No corrections yet</h2><p>This log starts with the first edition, {long_day(E["date"])}. Spotted an error? <a class="ln" href="contact.html">Tell us</a>.</p></div></div>
<aside class="aside"><div class="box"><span class="label">How a correction reads</span><p class="note" style="border:0;padding:0">Each entry gives the date, the page, the sentence as it stood, the sentence as it stands, and the source that showed us the error.</p></div></aside></div><div style="height:64px"></div>'''
    P.write('corrections.html', P.page('corrections.html', 'Corrections', 'Every correction we make, dated.', corr, 'corrections'))

    priv = f'''<header class="page-h"><div class="wrap">{crumbs(("Front page", "home.html"), ("Privacy", None))}<h1>Privacy</h1><p>What we keep, and what we never do.</p></div></header>
<div class="art" style="margin-top:40px"><div class="prose">
<p><b>The lawyer request.</b> The form asks only for what a legal-aid group needs to act: who was taken, when, where, and how to reach you. On the live site it will go to the legal-aid desk alone. We will not publish it, sell it or share it with anyone who is not handling the case.</p>
<p><b>Children.</b> We do not publish details that identify a child in custody, and we ask you not to send photographs of them.</p>
<p><b>This site.</b> No advertising, no tracking pixels, no third-party scripts. The fonts are served from this site. Your browser keeps one note, that you have already seen the opening animation, and only for this visit.</p>
<p><b>This prototype.</b> The forms on this design prototype send nothing.</p>
</div><aside class="aside"><div class="box"><span class="label">In short</span><ol class="record"><li><span>No trackers.</span></li><li><span>Requests go to the legal-aid desk only.</span></li><li><span>Nothing that identifies a child.</span></li></ol></div></aside></div><div style="height:64px"></div>'''
    P.write('privacy.html', P.page('privacy.html', 'Privacy', 'What we keep, and what we never do.', priv, 'privacy'))


def main():
    for sid in E['by_date']:
        story(sid)
    for c in E['cases']:
        case(c)
    for slug, *_ in SECTIONS:
        section(slug)
    for i, x in enumerate(E['guides']):
        guide(i, x)
    status_pages()
    archive()
    glossary()
    directory()
    small_pages()
    print('more: status 4, archive, glossary', len(GL), 'terms, directory, contact, corrections, privacy')
