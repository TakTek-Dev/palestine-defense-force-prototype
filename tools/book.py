"""Build index.html, the identity book, and assets/pdf-identity.zip.

python -I tools/book.py
"""
import os
import zipfile

import shell as S
from shell import C, esc, icon, status_svg, lockup, MARKS

ROOT = S.ROOT


def grid_svg():
    """The mark on its 64 grid with the construction drawn over it."""
    g = MARKS['grid']
    cx, cy, r = MARKS['dot']
    lines = ''.join(f'<path d="M{v} 0V64"/>' for v in (g['x0'], g['x0'] + g['w'], g['tip'], cx)) + \
            ''.join(f'<path d="M0 {v}H64"/>' for v in (g['y0'], g['y0'] + g['w'], cy, g['y1'] - g['w'], g['y1']))
    cells = ''.join(f'<path d="M{i * 4} 0V64M0 {i * 4}H64"/>' for i in range(17))
    return f'''<svg viewBox="-4 -4 72 72" role="img" aria-label="The mark on its 64-unit construction grid">
<g stroke="var(--rule-2)" stroke-width=".15">{cells}</g>
<path d="{MARKS["bracket"]}" fill="var(--ink)"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="var(--stamp)"/>
<g stroke="var(--stamp)" stroke-width=".22" stroke-dasharray=".8 .8" fill="none">{lines}<circle cx="{cx}" cy="{cy}" r="{r + 3}"/></g>
<g font-family="Mona Sans" font-size="2.4" font-weight="600" fill="var(--stamp)"><text x="{g["x0"] + .6}" y="-1">stem {g["w"]}</text><text x="{g["tip"] - 6}" y="-1">tip {g["tip"]:g}</text><text x="{cx - 2}" y="67">r {r}</text></g></svg>'''


SW = [('Ink', '--ink', '#121419', 'Text, the bracket, every rule.'), ('Paper', '--paper', '#FFFFFF', 'The page. Never cream.'),
      ('Mist', '--mist', '#F3F4F7', 'Quiet bands: case files, groups.'), ('Rule', '--rule', '#D9DCE3', 'Hairlines between records.'),
      ('Stamp', '--stamp', '#4231D8', 'People. The point, figures of people held, the call for a lawyer.'),
      ('Night', '--night', '#101117', 'The docket, testimony, the footer.'), ('Stamp on night', '--stamp-night', '#9A90FF', 'The point and the count on night.')]


def main():
    C.R = ''
    st = ''.join(f'<li><span>{status_svg(k)}</span><span class="t">{esc(v[0])}<small>{esc(v[1])}</small></span><span></span></li>' for k, v in S.STATUS.items())
    sw = ''.join(f'<div class="sw"><i style="background:var({v})"></i><b>{n}</b><span class="meta">{h}</span><p>{esc(d)}</p></div>' for n, v, h, d in SW)
    chapters = [('idea', 'The idea'), ('mark', 'The mark'), ('lockup', 'Lockups'), ('grammar', 'The bracket grammar'), ('colour', 'Colour'),
                ('type', 'Type'), ('docket', 'The docket'), ('motion', 'Motion'), ('photo', 'Photographs'), ('voice', 'Voice'), ('files', 'Files')]
    toc = ''.join(f'<a href="#{a}"><span class="num">{i + 1:02d}</span>{t}</a>' for i, (a, t) in enumerate(chapters))
    ch = lambda i: f'<span class="label">{i + 1:02d} · {chapters[i][1]}</span>'
    body = f'''<section class="docket book-hero"><div class="wrap" style="display:block">
<span class="label">Identity book · {S.long_day(S.TODAY).split(" ", 1)[1]}</span>
<div class="book-lock">{lockup("", night=True)}</div>
<p class="docket-copy" style="max-width:36em">A legal-defense desk needs a mark that says what defense is: keeping a person in the record. This book sets out the mark, the grammar it gives the site, and how to use both.</p>
<div class="docket-cta"><a class="btn btn--stamp" href="home.html">See the site {icon("i-right")}</a><a class="btn btn--night" href="assets/pdf-identity.zip" download>Download the marks</a></div>
<nav class="toc" aria-label="Chapters">{toc}</nav></div></section>

<section class="block" id="idea"><div class="wrap book-2">{ch(0)}<div class="prose">
<p>In a court record, the square bracket is the one place where someone other than the speaker may write: <i>[emphasis added]</i>, <i>[sic]</i>, <i>[the witness pointed at the door]</i>. It is the mark of the editor and of counsel. It inserts, clarifies, objects.</p>
<p>Our mark is a bracket holding a point. The point is a person. The bracket is the defense reaching over them and keeping them in the record. Nothing else in the identity is in colour; the point is printed in stamp violet, the ink of the rubber stamp on every affidavit, every permit and every receipt a military court hands a family.</p>
<p>The idea carries into the site as a grammar: the bracket a person wears tells you the process the law allows them.</p></div></div></section>

<section class="block block--mist" id="mark"><div class="wrap book-2">{ch(1)}<div><div class="book-mark">{grid_svg()}</div>
<p class="note" style="margin-top:18px">Built on a 64-unit grid. Stem and arms share one weight (8.6). Outer corners ease at 8, inner corners at 2.4, the arm ends at 3: soft, never knife-cut, and still unmistakably a bracket. The arms end at 47, past the point’s centre at 37.5: they reach over it. At icon sizes the point grows to 9.4 so it can never read as the middle bar of an E.</p>
<div class="book-row"><img src="assets/brand/mark.svg?v={S.V}" alt="The mark" width="120" height="120"><img src="assets/brand/avatar.svg?v={S.V}" alt="Avatar" width="120" height="120"><img src="favicon.svg?v={S.V}" alt="Favicon" width="64" height="64"><img src="favicon.svg?v={S.V}" alt="Favicon at 32" width="32" height="32"><img src="favicon.svg?v={S.V}" alt="Favicon at 16" width="16" height="16"></div></div></div></section>

<section class="block" id="lockup"><div class="wrap book-2">{ch(2)}<div>
<div class="book-tile"><img src="assets/brand/lockup.svg?v={S.V}" alt="Stacked lockup" style="width:min(560px,100%)"></div>
<div class="book-tile book-tile--night"><img src="assets/brand/lockup-reverse.svg?v={S.V}" alt="Stacked lockup on night" style="width:min(460px,100%)"></div>
<div class="book-tile"><img src="assets/brand/wordmark.svg?v={S.V}" alt="One-line wordmark" style="width:min(520px,100%)"></div>
<p class="note">In the stacked lockup the bracket grows to span both lines and holds the name itself; its stem matches the stem of the letters (Mona Sans, width 112, weight 800). The point moves into the name: it is the dot of the i in Palestine, in stamp violet. Use the one-line wordmark only where height is short.</p></div></div></section>

<section class="block block--mist" id="grammar"><div class="wrap book-2">{ch(3)}<div>
<ul class="legend legend--paper">{st}</ul>
<p class="note" style="margin-top:18px">The same five shapes label people on case files, group the points on the docket and filter lists. The shape carries the meaning, so the colour never has to: they read in black and white, and on a screen reader each one is named.</p></div></div></section>

<section class="block" id="colour"><div class="wrap book-2">{ch(4)}<div><div class="sws">{sw}</div>
<p class="note" style="margin-top:18px">One colour, and it belongs to people. Stamp on paper passes 7:1; stamp on night is lifted to #9A90FF to pass 6:1. Status is never told by colour alone.</p></div></div></section>

<section class="block block--mist" id="type"><div class="wrap book-2">{ch(5)}<div>
<div class="type-a"><span class="label">Mona Sans · the record</span><p style="font:800 clamp(40px,6vw,84px)/1 var(--sans);font-stretch:125%;letter-spacing:-.03em;margin-top:12px">{S.n(S.E["docket"]["latest"]["administrative"])} <span class="stamp">held</span></p>
<p style="font:720 clamp(26px,3vw,38px)/1.1 var(--sans);letter-spacing:-.02em;margin-top:18px">Order renewed for a fifth time; the file stays secret</p>
<p class="note" style="margin-top:14px">Width carries weight. Counts of people are set wide (125), headlines at 100, labels at 104–108. GitHub’s Mona Sans, OFL.</p></div>
<div class="type-a"><span class="label">Petrona · people</span><p style="font:400 20px/1.62 var(--serif);margin-top:12px;max-width:34em">The order was renewed on Tuesday. Neither the detainee nor his lawyer has seen the evidence, which the military prosecutor filed as classified.</p>
<p style="font:italic 400 clamp(24px,2.6vw,32px)/1.3 var(--serif);margin-top:18px">“I asked what I am accused of. They said: you know.”</p>
<p class="note" style="margin-top:14px">A humanist serif with a pen in it, for reading and, in italic, for testimony: the voice of people against the engineered sans of the record. Ringo R. Seeber, OFL. The quote above is a specimen, not a testimony.</p></div></div></div></section>

<section class="block" id="docket"><div class="wrap book-2">{ch(6)}<div class="prose">
<p>The front page opens on the docket: every person held, one point each, grouped by the law that holds them, each group in its bracket. A scrubber walks back month by month to before October 2023, so the reader watches the groups without a bracket grow.</p>
<p><a class="ln" href="home.html#docket-h">See it live on the front page</a> · <a class="ln" href="docket.html">the full table</a>.</p></div></div></section>

<section class="block block--mist" id="motion"><div class="wrap book-2">{ch(7)}<div>
<div class="book-tile" style="min-height:260px"><div id="replay" style="width:min(520px,100%)">{lockup("", label="")}</div></div>
<button class="btn" type="button" id="replay-btn">Replay the loader</button>
<p class="note" style="margin-top:18px">Into the record: the bracket stands up, the name is entered line by line, and last the point drops into the i. Once a session, 1.6 seconds, skipped for reduced motion. Elsewhere, motion is small and has a reason: brackets close around a tab on hover, the case clocks count today, the docket fills once when it is first seen.</p></div></div></section>

<section class="block" id="photo"><div class="wrap book-2">{ch(8)}<div class="prose">
<p>Photographs show the place or institution in the story, with their real date, in their own colour, resized only. No filters, no duotones. Where no honest photograph exists, the page prints the status mark on a quiet plate instead. We do not show the faces of children in custody.</p></div></div></section>

<section class="block block--mist" id="voice"><div class="wrap book-2">{ch(9)}<div class="prose">
<p>Plain and exact, in the order a lawyer would want it: who, held where, under what law, since when, what happens next. Say “held without charge”, not “detained”. Name the law. Give the date. Put the source on the same page. Use the people’s own words in Petrona italic and attribute them.</p></div></div></section>

<section class="block" id="files"><div class="wrap book-2">{ch(10)}<div>
<a class="btn btn--stamp" href="assets/pdf-identity.zip" download>Download the marks (SVG) {icon("i-right")}</a>
<p class="note" style="margin-top:18px">Mark, stacked lockup and one-line wordmark in ink and reverse, avatar, favicon, the five status shapes, and the two typefaces with their licences.</p></div></div></section>'''
    extra = '''<style>
.book-hero .wrap{padding-block:56px 48px}.book-lock{margin:36px 0 26px;color:#fff}.book-lock svg{width:min(760px,100%);height:auto}
.toc{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:0 24px;margin-top:40px;border-top:1px solid var(--night-3)}
.toc a{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid var(--night-3);font:600 14.5px/1.2 var(--sans);color:var(--on-night)}.toc a:hover{color:var(--stamp-night)}
.toc .num{font-size:13px;color:var(--on-night-3);font-stretch:110%}
.book-2{display:grid;grid-template-columns:minmax(0,220px) minmax(0,1fr);gap:40px}
.book-mark{max-width:520px;background:var(--paper);border-radius:var(--r3);padding:16px;border:1px solid var(--rule)}
.book-row{display:flex;flex-wrap:wrap;align-items:end;gap:24px;margin-top:24px}
.book-tile{display:grid;place-items:center;padding:clamp(24px,5vw,56px);border:1px solid var(--rule);border-radius:var(--r3);margin-bottom:16px;background:var(--paper)}
.book-tile--night{background:var(--night);border-color:var(--night)}
.sws{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px}
.sw i{display:block;height:84px;border-radius:var(--r2);border:1px solid var(--rule);margin-bottom:10px}.sw b{font:680 15px var(--sans);display:block}.sw p{font:400 14px/1.45 var(--serif);color:var(--ink-2);margin-top:4px}
.type-a{padding:24px 0;border-top:1px solid var(--rule)}
@media (max-width:820px){.book-2{grid-template-columns:minmax(0,1fr);gap:16px}}
</style>'''
    js = '''<script>(()=>{const b=document.getElementById('replay-btn');if(!b)return;b.addEventListener('click',()=>{const s=document.querySelector('#replay svg'),e='cubic-bezier(.16,1,.3,1)';
const br=s.querySelector('.b'),l1=s.querySelector('.l1'),l2=s.querySelector('.l2'),d=s.querySelector('.dot');br.style.transformBox='fill-box';br.style.transformOrigin='50% 50%';
br.animate([{transform:'scaleY(0)'},{transform:'scaleY(1)'}],{duration:420,easing:e,fill:'both'});
l1.animate([{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0 0 0)'}],{duration:520,delay:300,easing:e,fill:'both'});
l2.animate([{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0 0 0)'}],{duration:560,delay:430,easing:e,fill:'both'});
d.animate([{opacity:0,transform:'translateY(-160px)'},{opacity:1,transform:'translateY(0)',offset:.62},{transform:'translateY(-14px)',offset:.8},{opacity:1,transform:'translateY(0)'}],{duration:640,delay:900,easing:'cubic-bezier(.4,0,.6,1)',fill:'both'});});})()</script>'''
    page = S.head('Identity book', 'The mark, grammar, colour, type and motion of Palestine Defense Force.', 'index.html', extra=extra) + S.top('book') + body + S.foot().replace('</body>', js + '</body>')
    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(page)
    z = os.path.join(ROOT, 'assets', 'pdf-identity.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(os.listdir(os.path.join(ROOT, 'assets', 'brand'))):
            zf.write(os.path.join(ROOT, 'assets', 'brand', f), 'svg/' + f)
        zf.write(os.path.join(ROOT, 'favicon.svg'), 'svg/favicon.svg')
        for f in os.listdir(os.path.join(ROOT, 'assets', 'fonts')):
            zf.write(os.path.join(ROOT, 'assets', 'fonts', f), 'fonts/' + f)
    print('index.html', len(page) // 1024, 'KB; zip', os.path.getsize(z) // 1024, 'KB')


if __name__ == '__main__':
    main()
