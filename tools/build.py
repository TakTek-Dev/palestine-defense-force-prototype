"""Build home.html from tools/edition.json.

python -I tools/build.py
"""
import json
import os

import shell as S
from shell import C, E, SEC, esc, n, icon, photo, story_url, case_url, status_svg, status_tag, mark_svg, day

ROOT = S.ROOT
ST = E['stories']
KIND_ROWS = [  # docket key, status glyph, label, line
    ('sentenced', 'sentenced', 'Sentenced', 'Tried by a court and serving a sentence.'),
    ('remand', 'remand', 'Remand', 'Under interrogation, charged, or on trial.'),
    ('administrative', 'administrative', 'Administrative detention', 'No charge, no trial. A secret file, renewed by order.'),
    ('unlawful_combatants', 'unlawful_combatant', '“Unlawful combatants”', 'Held outside the courts, mostly from Gaza.'),
]


def kicker(s):
    return f'<div class="kick">{S.sec_link(s["section"])}<span class="meta">{esc(s["place"])}</span></div>'


def docket():
    d = E['docket']
    L = d['latest']
    slug = {'sentenced': 'sentenced', 'remand': 'remand', 'administrative': 'administrative', 'unlawful_combatants': 'unlawful-combatants'}
    rows = ''.join(f'''<li><span>{status_svg(g)}</span><a class="t" href="{C.R}status/{slug[k]}.html">{lab}<small>{line}</small></a>
<span class="n"><b>{n(L[k])}</b><small>{round(L[k] / L["total"] * 100)}% of all held</small></span></li>''' for k, g, lab, line in KIND_ROWS)
    ser = d['series']
    first, last = ser[0], ser[-1]
    data = json.dumps({'series': ser}, separators=(',', ':'))
    src = d['source']
    return f'''<section class="docket" aria-labelledby="docket-h"><div class="wrap">
<div>
<span class="label">The docket · {esc(S.long_day(L["as_of"]).split(" ", 1)[1])}</span>
<h1 id="docket-h"><span class="num">{n(L["total"])}</span> Palestinians are held by Israel. <span class="soft"><span class="num">{n(L["administrative"] + L["unlawful_combatants"])}</span> of them without charge or trial.</span></h1>
<p class="docket-copy">Each point is one person. The bracket around a group is the process the law allows them: a closed record, an open one, a <b>secret file</b>, or <b>none at all</b>.
In {esc(first["label"])} the prisons held {n(first["total"])}.</p>
<ul class="legend">{rows}</ul>
<div class="docket-cta"><a class="btn btn--night" href="docket.html">The full docket {icon("i-right")}</a><a class="btn btn--stamp" href="help.html">Request a lawyer</a></div>
</div>
<div class="field" id="field">
<div class="field-c"><canvas role="img" aria-label="{n(L["total"])} points, one per person held, in four groups: {n(L["sentenced"])} sentenced, {n(L["remand"])} on remand, {n(L["administrative"])} in administrative detention, {n(L["unlawful_combatants"])} held as unlawful combatants."></canvas><div class="field-tip" role="presentation"></div></div>
<div class="scrub"><button class="icon-btn" id="scrub-play" type="button" aria-label="Play the months">{icon("i-play")}</button>
<input id="scrub" type="range" min="0" step="1" aria-label="Month"><output id="scrub-out" for="scrub">{esc(last["label"])}</output></div>
<div class="ticks" aria-hidden="true"><span>{esc(first["label"])}</span><span>{esc(last["label"])}</span></div>
<p class="src">Israel Prison Service figures as published by <a href="{src["url"]}">{esc(src["outlet"])}</a>, monthly. Remand counts people under interrogation, awaiting trial and on trial. People held by the army and not yet handed to the prison service are not counted.</p>
</div>
</div><script type="application/json" id="docket-data">{data}</script></section>'''


def row(sid, with_photo=True):
    s = ST[sid]
    ph = photo(s.get('photo'), '112px', 'ph') if with_photo else ''
    cls = 'row' if ph else 'row row--np'
    return f'''<a class="{cls}" href="{story_url(sid)}"><div><span class="label">{esc(SEC[s["section"]][1])}</span>
<h3>{esc(s["headline"])}</h3><span class="meta">{day(s["date"])} · {esc(s["place"])}</span></div>{ph}</a>'''


def card(sid, sizes='(max-width:640px) 100vw, 25vw'):
    s = ST[sid]
    # no honest photograph: a typographic plate (section bracket, place, date) keeps every card in a row
    # the same shape, so headlines line up; it never pretends to be a picture
    ph = photo(s.get('photo'), sizes, 'ph ph--32') or (
        f'<div class="plate plate--story" aria-hidden="true"><span class="pl-sec">{esc(SEC[s["section"]][1])}</span>'
        f'<b>{esc(s["place"])}</b><span class="pl-d">{day(s["date"], True)}</span></div>')
    return f'''<a class="card rv" href="{story_url(sid)}">{ph}<span class="label">{esc(SEC[s["section"]][1])}</span><h3>{esc(s["headline"])}</h3>
<p>{esc(s["dek"])}</p><span class="meta">{day(s["date"])} · {esc(s["place"])}</span></a>'''


def lead():
    o = E['order']
    s = ST[o['lead']]
    return f'''<section class="block"><div class="wrap lead">
<a class="lead-main" href="{story_url(o["lead"])}">{photo(s.get("photo"), "(max-width:980px) 100vw, 58vw", "ph ph--169", eager=True)}
<div style="margin-top:20px">{kicker(s).replace("<a ", "<span ").replace("</a>", "</span>")}</div>
<h2>{esc(s["headline"])}</h2><p class="dek">{esc(s["dek"])}</p><p class="meta">{S.long_day(s["date"])}</p></a>
<div class="rail"><span class="label">Latest on the record</span>{"".join(row(i) for i in o["top"])}</div>
</div></section>'''


def case_card(c):
    if c['kind'] == 'person':
        since = c.get('since')
        until = c.get('until')
        clk = (f'<div class="clock"><span class="num" data-since="{since}"{f" data-until={until}" if until else ""}>'
               f'{(S.D(until) if until else S.TODAY).toordinal() - S.D(since).toordinal():,}</span><span>{esc(c.get("clock_label", "days held"))}</span></div>') if since else ''
        glyph = status_svg(c['status']) if c['status'] in S.MARKS['status'] else ''
        lab = S.STATUS.get(c['status'], (c['status'],))[0]
        cls = 'case'
    else:
        clk = f'<div class="clock"><span class="num">{esc(c.get("figure", ""))}</span><span>{esc(c.get("figure_label", ""))}</span></div>' if c.get('figure') else ''
        glyph = ''
        lab = S.COMMUNITY.get(c['status'], c['status'])
        cls = 'case case--community'
    return f'''<a class="{cls} rv" href="{case_url(c["id"])}"><div class="case-top"><span class="label">{esc(lab)}</span>{glyph}</div>
<h3>{esc(c["title"])}</h3><p>{esc(c["summary"])}</p>{clk}</a>'''


def cases():
    cs = [c for c in E['cases'] if c['id'] in E['order']['cases']]
    cs.sort(key=lambda c: E['order']['cases'].index(c['id']))
    return f'''<section class="block block--mist"><div class="wrap">
<div class="block-h"><div><h2 class="bh">Case files</h2><p>People and communities we follow from the first order to the last ruling. The clock counts today.</p></div>
<a class="more" href="cases.html">All case files {icon("i-right")}</a></div>
<div class="cases rail-x">{"".join(case_card(c) for c in cs)}</div></div></section>'''


def section_block(slug, ids):
    if not ids:
        return ''
    t = SEC[slug]
    return f'''<section class="block"><div class="wrap">
<div class="block-h"><div><h2 class="bh">{esc(t[2])}</h2><p>{esc(t[3])}</p></div><a class="more" href="{slug}.html">More {esc(t[1].lower())} {icon("i-right")}</a></div>
<div class="grid rail-x">{"".join(card(i) for i in ids[:4])}</div></div></section>'''


def guides():
    g = E['guides']
    items = ''.join(f'''<a class="guide rv" href="rights/{x["id"]}.html"><span class="num">§{i + 1}</span><h3>{esc(x["title"])}</h3><p>{esc(x["line"])}</p></a>''' for i, x in enumerate(g))
    return f'''<section class="block"><div class="wrap">
<div class="block-h"><div><h2 class="bh">Know your rights</h2><p>Short guides to the laws used to hold people, written so they can be read on a phone at a checkpoint. Every point links to its source.</p></div>
<a class="more" href="rights.html">All guides {icon("i-right")}</a></div>
<div class="guides">{items}</div></div></section>'''


def testimony():
    q = E.get('quote')
    if not q:
        return ''
    return f'''<section class="testimony"><div class="wrap">{mark_svg()}
<blockquote><p class="fact">{esc(q["text"])}</p><cite>{esc(q["who"])} · <a href="{q["url"]}">{esc(q["outlet"])}, {day(q["date"], True)}</a></cite></blockquote>
</div></section>'''


def orgs():
    o = E['orgs']
    items = ''.join(f'<a class="org" href="{x["url"]}" rel="noopener"><b>{esc(x["name"])}{icon("i-out")}</b><span>{esc(x["line"])}</span></a>' for x in o)
    return f'''<section class="block block--mist"><div class="wrap">
<div class="block-h"><div><h2 class="bh">Who keeps the record with us</h2><p>The legal-aid and rights groups whose casework, petitions and data this desk relies on.</p></div></div>
<div class="orgs">{items}</div></div></section>'''


def main():
    C.R = ''
    o = E['order']
    secs = [section_block(sl, o['sections'].get(sl, [])) for sl in o['section_order']]
    page = (S.head(S.SITE, 'Who is held, on what law, in which court, and what can be done about it: a legal-defense desk for Palestinians.', 'home.html')
            + S.top('home') + docket() + lead() + cases() + ''.join(secs[:2]) + testimony() + ''.join(secs[2:])
            + guides() + S.help_band() + orgs() + S.foot())
    with open(os.path.join(ROOT, 'home.html'), 'w', encoding='utf-8') as fh:
        fh.write(page)
    print('home.html', len(page) // 1024, 'KB')


if __name__ == '__main__':
    main()
