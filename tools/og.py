"""tools/out/og.html: the 1200x630 sharing card (the docket figure on the left, the lead photo on the right).

python -I tools/og.py
node --experimental-websocket tools/shot.mjs http://localhost:8277/tools/out/og.html assets/og.png 1200 630 view
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir

import shell as S
from shell import C, E, esc, n

L = E['docket']['latest']
lead = E['stories'][E['order']['lead']]
C.R = '../../'
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>og</title>
<link rel="stylesheet" href="../../assets/css/pdf.css?v={S.V}">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:var(--night)}}
.og{{display:grid;grid-template-columns:680px 520px;height:630px}}
.l{{padding:48px 52px 44px;display:flex;flex-direction:column;color:var(--on-night)}}
.l .brand svg{{width:330px;height:auto;color:#fff}}
.l .n{{margin-top:auto;font:820 150px/.85 var(--sans);font-stretch:125%;color:var(--stamp-night);letter-spacing:-.04em}}
.l p{{margin-top:18px;font:700 34px/1.12 var(--sans);letter-spacing:-.02em;color:#fff;max-width:18em}}
.l p span{{color:var(--on-night-2)}}
.l .s{{margin-top:14px;font:500 16px/1.3 var(--sans);color:var(--on-night-3)}}
.r img{{width:100%;height:100%;object-fit:cover}}
</style></head><body><div class="og"><div class="l"><div class="brand">{S.lockup(night=True)}</div>
<div class="n">{n(L["total"])}</div><p>Palestinians held by Israel. <span>{n(L["administrative"] + L["unlawful_combatants"])} without charge or trial.</span></p>
<p class="s">Israel Prison Service figures via HaMoked · {esc(L["label"])}</p></div>
<div class="r"><img src="../../assets/img/photo/{lead["photo"]}.webp" alt=""></div></div></body></html>'''
_os.makedirs(_os.path.join(S.ROOT, 'tools', 'out'), exist_ok=True)
open(_os.path.join(S.ROOT, 'tools', 'out', 'og.html'), 'w', encoding='utf-8').write(html)
print('tools/out/og.html')
