"""Build every page but the front page and the identity book.

python -I tools/pages.py
  story/<id>.html, case/<id>.html, rights/<id>.html, <section>.html,
  cases.html, docket.html, rights.html, about.html, method.html, help.html, credits.html, search.html, 404.html
"""
import json
import os

import shell as S
from shell import C, E, SEC, SECTIONS, esc, n, icon, photo, story_url, case_url, status_svg, day, long_day
import build as B

ROOT = S.ROOT
ST = E['stories']


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as fh:
        fh.write(html)


def page(path, title, desc, body, current=None, depth=0):
    C.R = '../' * depth
    return S.head(title, desc, path) + S.top(current) + body + S.foot()


def sources_box(srcs):
    li = ''.join(f'<li><span><a href="{s["url"]}" rel="noopener">{esc(s["title"])}</a><small>{esc(s["outlet"])}, {day(s["date"], True) if s.get("date") else ""}</small></span></li>' for s in srcs)
    return f'<div class="box"><span class="label">The record</span><ol class="record">{li}</ol></div>'


def related(sid, k=4):
    s = ST[sid]
    same = [i for i in E['by_date'] if i != sid and ST[i]['section'] == s['section']]
    rest = [i for i in E['by_date'] if i != sid and i not in same]
    return (same + rest)[:k]


# ---------------------------------------------------------------- story
def story(sid):
    s = ST[sid]
    C.R = '../'
    figs = ''.join(f'<div class="fig"><span class="num">{esc(f["v"])}</span><span>{esc(f["label"])}</span></div>' for f in s.get('figures', []))
    aside = ''
    if figs:
        aside += f'<div class="box"><span class="label">In figures</span><div class="figs">{figs}</div></div>'
    aside += sources_box(s['sources'])
    if not s.get('verified'):
        aside += '<p class="note">Reported by one outlet so far. We will add a second source or correct this page when there is one.</p>'
    cs = [c for c in E['cases'] if sid in c.get('stories', [])]
    if cs:
        aside += f'<div class="box"><span class="label">Case file</span>{"".join(f"""<a class="st" href="{case_url(c["id"])}" style="margin-top:6px">{status_svg(c["status"]) if c["status"] in S.MARKS["status"] else ""}{esc(c["title"])}</a>""" for c in cs)}</div>'
    body = ''.join(f'<p>{esc(p)}</p>' for p in s['body'])
    fig = photo(s.get('photo'), '(max-width:1180px) 100vw, 1180px', 'ph ph--169', eager=True, caption=True)
    rel = ''.join(B.card(i, '(max-width:640px) 100vw, 25vw') for i in related(sid))
    html = f'''<article>
<header class="art-h"><div class="wrap">{S.sec_link(s["section"])}
<h1>{esc(s["headline"])}</h1><p class="dek">{esc(s["dek"])}</p>
<p class="meta"><span><b>{long_day(s["date"])}</b></span><span>{esc(s["place"])}</span><span>{len(s["sources"])} source{"s" if len(s["sources"]) > 1 else ""}</span></p></div></header>
{f'<div class="art-fig">{fig}</div>' if fig else ''}
<div class="art"><div class="prose">{body}</div><aside class="aside">{aside}</aside></div>
</article>
<section class="block" style="margin-top:48px"><div class="wrap"><div class="block-h"><h2 class="bh">Also on the record</h2></div><div class="grid">{rel}</div></div></section>'''
    write(f'story/{sid}.html', S.head(s['headline'], s['dek'], f'story/{sid}.html') + S.top(s['section']) + html + S.help_band() + S.foot())


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
        glyph = status_svg(c['status'], lab) if c['status'] in S.MARKS['status'] else ''
    else:
        lab, line = S.COMMUNITY.get(c['status'], c['status']), ''
        big = f'<span class="num">{esc(c.get("figure", ""))}</span><b>{esc(c.get("figure_label", ""))}</b>' if c.get('figure') else ''
        glyph = ''
    tl = ''.join(f'<li><time>{day(t["date"], True)}</time><p>{esc(t["event"])}</p>{f"""<a href="{t["source_url"]}" rel="noopener">Source</a>""" if t.get("source_url") else ""}</li>' for t in c['timeline'])
    st = ''.join(B.card(i) for i in c.get('stories', []) if i in ST)
    fig = photo(c.get('photo'), '(max-width:980px) 100vw, 640px', 'ph ph--32', caption=True)
    html = f'''<header class="case-h"><div class="wrap"><div>
<a class="label" href="../cases.html">Case file · {esc(c["place"])}</a>
<h1>{esc(c["title"])}</h1><p class="dek">{esc(c["summary"])}</p></div>
<div class="big">{glyph}{big}<span class="st">{esc(lab)}</span>{f'<span class="meta">{esc(line)}</span>' if line else ''}</div></div></header>
<div class="art"><div><h2 class="bh" style="font-size:26px;margin-bottom:24px">The record, in order</h2><ol class="tl">{tl}</ol>
{f'<div style="margin-top:20px">{fig}</div>' if fig else ''}</div>
<aside class="aside">{sources_box(c["sources"])}<p class="note">Status checked {day(E["date"], True)}. If you know of a later order or ruling, write to us through the <a class="ln" href="../help.html">request form</a>.</p></aside></div>
{f'<section class="block" style="margin-top:40px"><div class="wrap"><div class="block-h"><h2 class="bh">Reporting on this case</h2></div><div class="grid">{st}</div></div></section>' if st else ''}'''
    write(f'case/{c["id"]}.html', S.head(c['title'], c['summary'], f'case/{c["id"]}.html') + S.top('cases') + html + S.help_band() + S.foot())


# ---------------------------------------------------------------- lists
def item(sid):
    s = ST[sid]
    ph = photo(s.get('photo'), '220px', 'ph ph--32') or '<div></div>'
    return f'''<a class="item" href="{C.R}story/{sid}.html" data-k="{s["section"]}"><time datetime="{s["date"]}">{day(s["date"], True)}</time>
<div><span class="label">{esc(SEC[s["section"]][1])} · {esc(s["place"])}</span><h2>{esc(s["headline"])}</h2><p>{esc(s["dek"])}</p></div>{ph}</a>'''


def section(slug):
    C.R = ''
    t = SEC[slug]
    ids = [i for i in E['by_date'] if ST[i]['section'] == slug]
    body = f'''<header class="page-h"><div class="wrap"><span class="label">Section</span><h1>{esc(t[2])}</h1><p>{esc(t[3])}</p></div></header>
<div class="wrap"><div class="list">{"".join(item(i) for i in ids)}</div></div>'''
    write(f'{slug}.html', page(f'{slug}.html', t[2], t[3], body + '<div style="height:56px"></div>' + S.help_band(), slug))


def cases_page():
    C.R = ''
    kinds = [('all', 'All', None)] + [(k, S.STATUS[k][0], k) for k in ('remand', 'administrative', 'unlawful_combatant', 'sentenced', 'released', 'died_in_custody')
                                      if any(c['status'] == k for c in E['cases'])] + [('community', 'Communities', None)]
    chips = ''.join(f'<button class="chip" type="button" data-v="{k}" aria-pressed="{"true" if k == "all" else "false"}">{status_svg(g) if g else ""}{esc(l)}</button>' for k, l, g in kinds)
    cards = ''.join(B.case_card(c).replace('class="case', f'data-k="{c["status"] if c["kind"] == "person" else "community"}" class="case', 1) for c in E['cases'])
    legend = ''.join(f'<li><span>{status_svg(k)}</span><span class="t">{esc(S.STATUS[k][0])}<small>{esc(S.STATUS[k][1])}</small></span><span></span></li>' for k in S.STATUS)
    body = f'''<header class="page-h"><div class="wrap"><span class="label">The record</span><h1>Case files</h1>
<p>People held and communities facing orders, each followed from the first order to the latest ruling. The bracket beside a name is the process the law allows them.</p></div></header>
<div class="wrap"><div class="filters" data-filter=".cases .case">{chips}</div>
<h2 class="vh">All case files</h2><div class="cases" style="margin-top:20px">{cards}</div>
<div class="block" style="padding-bottom:0"><h2 class="bh" style="font-size:24px;margin-bottom:12px">How to read the brackets</h2>
<ul class="legend legend--paper">{legend}</ul></div></div><div style="height:56px"></div>'''
    write('cases.html', page('cases.html', 'Case files', 'People held and communities facing orders, followed from the first order to the latest ruling.', body + S.help_band(), 'cases'))


def docket_page():
    C.R = ''
    d = E['docket']
    rows = ''.join(f'<tr><td>{esc(s["label"])}</td><td>{n(s["sentenced"])}</td><td>{n(s["remand"])}</td><td><b>{n(s["administrative"])}</b></td><td>{n(s["unlawful_combatants"])}</td><td><b>{n(s["total"])}</b></td></tr>'
                   for s in reversed(d['series']))
    extra = ''.join(f'<div class="fig"><span class="num">{esc(x["value"])}</span><span>{esc(x["label"])} · <a class="ln" href="{x["source"]["url"]}">{esc(x["source"]["outlet"])}</a>, {day(x["as_of"], True)}</span></div>' for x in d['extra'])
    srcs = ''.join(f'<li><span><a href="{s["url"]}">{esc(s["title"])}</a><small>{esc(s["outlet"])}{", " + day(s["date"], True) if s.get("date") else ""}</small></span></li>' for s in d['sources'])
    C.R = ''
    body = f'''{B.docket().replace('<h1 id="docket-h">', '<h1 id="docket-h" style="font-size:clamp(32px,4vw,54px)">', 1)}
<section class="block"><div class="wrap"><div class="art art--wide">
<div><h2 class="bh" style="font-size:28px;margin-bottom:20px">Month by month</h2>
<div class="scroll-x"><table class="tbl"><thead><tr><th scope="col">Month</th><th scope="col">Sentenced</th><th scope="col">Remand</th><th scope="col">Administrative</th><th scope="col">“Unlawful combatants”</th><th scope="col">Total</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note" style="margin-top:18px">{esc(d.get("note", ""))}</p></div>
<aside class="aside">{f'<div class="box"><span class="label">Also on the record</span><div class="figs">{extra}</div></div>' if extra else ''}
<div class="box"><span class="label">Sources</span><ol class="record">{srcs}</ol></div></aside></div></div></section>'''
    write('docket.html', page('docket.html', 'The docket', 'Palestinians held by Israel, month by month, by the law that holds them.', body + S.help_band(), 'docket'))


def rights():
    C.R = ''
    g = E['guides']
    items = ''.join(f'<a class="guide" href="rights/{x["id"]}.html"><span class="num">§{i + 1}</span><h3>{esc(x["title"])}</h3><p>{esc(x["line"])}</p></a>' for i, x in enumerate(g))
    orgs = ''.join(f'<a class="org" href="{x["url"]}" rel="noopener"><b>{esc(x["name"])}{icon("i-out")}</b><span>{esc(x["line"])}</span></a>' for x in E['orgs'])
    body = f'''<header class="page-h"><div class="wrap"><span class="label">Guides</span><h1>Know your rights</h1>
<p>What the law says, what it is used for, and where to turn. These guides explain; they are not legal advice for a particular case. For that, ask a lawyer.</p></div></header>
<section class="block"><div class="wrap"><h2 class="vh">The guides</h2><div class="guides">{items}</div></div></section>
<section class="block block--mist"><div class="wrap"><div class="block-h"><div><h2 class="bh">Legal aid and rights groups</h2><p>Go to them directly. Their own sites list how to reach them.</p></div><a class="more" href="directory.html">The full directory {icon("i-right")}</a></div><div class="orgs">{orgs}</div></div></section>
<section class="block"><div class="wrap"><div class="block-h"><div><h2 class="bh">The words of the law</h2><p>Administrative detention, remand, secret file, firing zone: the terms these guides use, in plain English.</p></div><a class="more" href="glossary.html">Open the glossary {icon("i-right")}</a></div></div></section>'''
    write('rights.html', page('rights.html', 'Know your rights', 'Short guides to the laws used to hold Palestinians, and where to turn.', body + S.help_band(), 'rights'))
    for i, x in enumerate(g):
        C.R = '../'
        pts = ''.join(f'<li><p>{esc(p["text"])}</p>{f"""<a href="{p["source_url"]}" rel="noopener">Source</a>""" if p.get("source_url") else ""}</li>' for p in x['points'])
        others = ''.join(f'<a class="guide" href="{y["id"]}.html"><span class="num">§{j + 1}</span><h3>{esc(y["title"])}</h3><p>{esc(y["line"])}</p></a>' for j, y in enumerate(g) if y['id'] != x['id'])
        html = f'''<header class="art-h"><div class="wrap"><a class="label" href="../rights.html">Know your rights · §{i + 1}</a><h1>{esc(x["title"])}</h1><p class="dek">{esc(x["line"])}</p></div></header>
<div class="art"><div><ol class="tl tl--plain">{pts}</ol></div><aside class="aside"><p class="note">This guide explains the law in general. It is not advice on a particular case: for that, ask a lawyer as early as you can.</p>
<a class="btn btn--stamp" href="../help.html">Request a lawyer {icon("i-right")}</a></aside></div>
<section class="block" style="margin-top:40px"><div class="wrap"><div class="block-h"><h2 class="bh">The other guides</h2></div><div class="guides">{others}</div></div></section>'''
        write(f'rights/{x["id"]}.html', S.head(x['title'], x['line'], f'rights/{x["id"]}.html') + S.top('rights') + html + S.foot())


def static_pages():
    C.R = ''
    about = f'''<header class="page-h"><div class="wrap"><span class="label">About</span><h1>We keep the record, and we ask for a lawyer.</h1>
<p>{S.SITE} is a legal-defense desk. It follows Palestinians held by Israel and the communities facing its orders, explains the laws used against them, and points people to the lawyers and rights groups who can act.</p></div></header>
<div class="art" style="margin-top:48px"><div class="prose">
<p>The name is about defense in the sense a court uses it: the side that answers the charge. Most of the people on our docket never meet a charge to answer. They are held on a secret file, or held outside any court at all. Defending them starts with saying they are there.</p>
<p>So the first thing on our front page is a count: every person held, grouped by the law that holds them. The bracket around each group in our mark and on our pages is the process that law allows. Sentenced people have a closed record. People on remand have an open one. People in administrative detention have only the bracket’s ends: a file that exists and that no one may read. People held as “unlawful combatants” have no bracket at all.</p>
<p>Everything we publish is summarised from sources we link on the same page: rights groups, courts, UN bodies and news outlets. When one outlet carries a story alone, we say so.</p>
</div><aside class="aside"><div class="box"><span class="label">The mark</span>{S.mark_svg("mk")}<p class="note" style="margin-top:14px">A bracket holding a point. The bracket is where the defense writes into the record; the point is a person, and the only thing we print in colour.</p></div></aside></div><div style="height:64px"></div>'''
    write('about.html', page('about.html', 'About', 'A legal-defense desk for Palestinians: who is held, on what law, and where to turn.', about + S.help_band(), 'about'))

    method = f'''<header class="page-h"><div class="wrap"><span class="label">Method</span><h1>How we keep the record</h1><p>Where our figures come from, how we write about people held, and how we correct ourselves.</p></div></header>
<div class="art" style="margin-top:48px"><div class="prose">
<p><b>The count.</b> The docket uses the Israel Prison Service’s own monthly figures as obtained and published by HaMoked. They group people by legal status. We merge the prison service’s categories for people under interrogation, awaiting trial and on trial into one group, remand. People held by the army who have not been transferred to the prison service do not appear in these figures, so the true number held is higher.</p>
<p><b>The clocks.</b> The number of days on a case file is counted from the arrest date reported by the sources on that file, to today. It changes every day without anyone editing the page.</p>
<p><b>Sources.</b> Every page lists the record it was written from, numbered. A story reported by a single outlet carries a note saying so.</p>
<p><b>Photographs.</b> We use photographs only where they honestly show the place or the institution in the story, with their real date. Where no honest photograph exists, we print the status mark instead.</p>
<p><b>Corrections.</b> We correct pages in place and say what changed and when.</p>
</div><aside class="aside">{sources_box(E["docket"]["sources"][:3])}</aside></div><div style="height:64px"></div>'''
    write('method.html', page('method.html', 'How we keep the record', 'Where our figures come from and how we correct ourselves.', method, 'method'))

    help_ = f'''<header class="page-h"><div class="wrap"><span class="label">Request a lawyer</span><h1>Tell us who was taken.</h1>
<p>Fill in what you know. A volunteer passes it to a legal-aid group that takes this kind of case. This is a design prototype: the form does not send anything yet.</p></div></header>
<div class="art" style="margin-top:40px"><form class="form" id="help-form">
<label>Name of the person arrested<input name="name" autocomplete="off" required></label>
<label>Date and time of the arrest<input name="when" type="datetime-local" required></label>
<label>Where it happened<input name="where" placeholder="Town, street, checkpoint" required></label>
<label>What do you know?<select name="what"><option>Arrested at home</option><option>Arrested at a checkpoint</option><option>Arrested at a protest</option><option>Taken from Gaza</option><option>An administrative detention order was issued</option><option>A demolition or eviction order was served</option><option>Something else</option></select></label>
<label>Anything else<textarea name="more" placeholder="The unit, if you saw it. Other people taken. Whether they are a child."></textarea><small>Write only what you saw or were told directly. Leave out anything that could put someone in danger.</small></label>
<label>How can we reach you?<input name="contact" autocomplete="tel" required><small>A phone number or an email. We will not publish it.</small></label>
<button class="btn btn--stamp" type="submit" style="justify-self:start">Send to a lawyer {icon("i-right")}</button>
<p class="note" id="help-done" tabindex="-1" hidden>Prototype: nothing was sent. On the live site, this request would go to the legal-aid desk.</p>
</form><aside class="aside"><div class="box"><span class="label">In the first hours</span><ol class="record">
<li><span>Write down the time, place and unit, and every name.</span></li><li><span>Ask for a lawyer. A detainee may be barred from seeing one for days; asking puts the request on record.</span></li>
<li><span>Do not post the arrest with details that identify children.</span></li><li><span>Contact one of the groups on <a href="rights.html">Know your rights</a> directly as well.</span></li></ol></div></aside></div><div style="height:64px"></div>'''
    write('help.html', page('help.html', 'Request a lawyer', 'Tell us who was taken, and we pass it to a legal-aid group.', help_, 'help'))

    cred = ''.join(f'<li><span>{esc(p["caption"])}<small><a href="{p["page_url"]}">{esc(p["file"][5:])}</a> · {esc(p["author"])} · {esc(p["license"])}</small></span></li>' for k, p in S.PH.items() if k in S.DIM)
    credits = f'''<header class="page-h"><div class="wrap"><span class="label">Credits</span><h1>Credits</h1><p>Type, photographs and the sources behind the figures.</p></div></header>
<div class="art" style="margin-top:40px"><div class="prose"><p><b>Type.</b> Mona Sans by GitHub and Petrona by Ringo R. Seeber, both under the SIL Open Font License, self-hosted.</p>
<p><b>Figures.</b> Israel Prison Service figures as published by HaMoked; other figures as credited on each page.</p>
<p><b>Photographs.</b> From Wikimedia Commons, in their own colour, resized only.</p></div>
<aside class="aside"><div class="box"><span class="label">Photographs</span><ol class="record">{cred}</ol></div></aside></div><div style="height:64px"></div>'''
    write('credits.html', page('credits.html', 'Credits', 'Type, photographs and sources.', credits, 'credits'))

    idx = [{'u': f'story/{i}.html', 'd': day(ST[i]['date'], True), 'k': esc(SEC[ST[i]['section']][1]), 'h': esc(ST[i]['headline']), 's': esc(ST[i]['dek']),
            't': ' '.join([ST[i]['headline'], ST[i]['dek'], ST[i]['place'], ' '.join(ST[i]['body'])] + ST[i].get('people', []))} for i in E['by_date']]
    idx += [{'u': f'case/{c["id"]}.html', 'd': 'Case file', 'k': 'Case file', 'h': esc(c['title']), 's': esc(c['summary']), 't': c['title'] + ' ' + c['summary'] + ' ' + c['place']} for c in E['cases']]
    GL = json.load(open(os.path.join(ROOT, 'tools', 'glossary.json'), encoding='utf-8'))
    idx += [{'u': f'rights/{g["id"]}.html', 'd': 'Guide', 'k': 'Know your rights', 'h': esc(g['title']), 's': esc(g['line']),
             't': g['title'] + ' ' + g['line'] + ' ' + ' '.join(p['text'] for p in g['points'])} for g in E['guides']]
    idx += [{'u': f'glossary.html#{g["id"]}', 'd': 'Glossary', 'k': 'Glossary', 'h': esc(g['term']), 's': esc(g['def']), 't': g['term'] + ' ' + g['def']} for g in GL]
    search = f'''<header class="page-h"><div class="wrap"><span class="label">Search</span><h1>Search the record</h1>
<form class="form" role="search" onsubmit="return false" style="margin-top:22px;max-width:720px"><label><span class="vh">Search</span><input id="q" type="search" placeholder="A name, a town, a court, a law" autofocus></label></form>
<p class="meta" id="count" aria-live="polite" style="margin-top:14px"></p></div></header>
<div class="wrap"><div class="list" id="results"></div></div><div style="height:64px"></div>
<script type="application/json" id="search-index">{json.dumps(idx, ensure_ascii=False)}</script>'''
    write('search.html', page('search.html', 'Search', 'Search every story and case file.', search, 'search'))

    C.R = S.BASE_URL
    nf = f'''<header class="page-h" style="border:0"><div class="wrap" style="padding-block:40px 80px">{status_svg("unlawful_combatant", "")}
<span class="label" style="display:block;margin-top:24px">404 · Not on the record</span><h1>This page was never filed.</h1>
<p>The address may be mistyped, or the page moved. Everything we have published is one search away.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:28px"><a class="btn btn--stamp" href="{S.BASE_URL}home.html">Front page</a><a class="btn" href="{S.BASE_URL}search.html">Search the record</a></div></div></header>'''
    write('404.html', S.head('Not on the record', 'Page not found.', '404.html') + S.top() + nf + S.foot())


def main():
    for sid in E['by_date']:
        story(sid)
    for c in E['cases']:
        case(c)
    for slug, *_ in SECTIONS:
        section(slug)
    cases_page()
    docket_page()
    rights()
    static_pages()
    import more                                    # fuller story/case/section/guide pages, and the second round
    more.main()
    print('pages:', len(E['by_date']), 'stories,', len(E['cases']), 'cases,', len(E['guides']), 'guides')


if __name__ == '__main__':
    main()
