"""Check every local href/src in the built pages resolves to a file.

python -I tools/links.py
"""
import os
import re
from urllib.parse import urlsplit, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://taktek-dev.github.io/palestine-defense-force-prototype/'
pages = [os.path.join(dp, f) for dp, _, fs in os.walk(ROOT) for f in fs
         if f.endswith('.html') and 'research' not in dp and 'tools' not in dp]
bad = 0
for p in pages:
    html = open(p, encoding='utf-8').read()
    for u in re.findall(r'(?:href|src)="([^"#]+)', html):
        if u.startswith(BASE):
            u = os.path.relpath(os.path.join(ROOT, u[len(BASE):]), os.path.dirname(p))
        if re.match(r'^(https?:|mailto:|data:|tel:)', u):
            continue
        path = unquote(urlsplit(u).path)
        if not path:
            continue
        t = os.path.normpath(os.path.join(os.path.dirname(p), path))
        if not os.path.exists(t):
            bad += 1
            print('BROKEN', os.path.relpath(p, ROOT), '->', u)
print(len(pages), 'pages,', bad, 'broken')
