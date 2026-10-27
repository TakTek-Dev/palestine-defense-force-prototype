/* Palestine Defense Force — behaviour.
   Loader (once a session), menu drawer, scroll reveal, the docket field, case clocks, list filters, search. */
(() => {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  /* ---------------------------------------------------------- loader: into the record
     The bracket stands up, the name is entered line by line, and last the point (the person)
     drops into the i of Palestine. Then the page is revealed. */
  const ld = $('.ld');
  if (ld) {
    if (!root.classList.contains('ld-on')) ld.remove();
    else {
      const svg = $('svg', ld), b = $('.b', svg), l1 = $('.l1', svg), l2 = $('.l2', svg), dot = $('.dot', svg);
      const ease = 'cubic-bezier(.16,1,.3,1)';
      [l1, l2].forEach(l => { l.style.clipPath = 'inset(0 100% 0 0)'; });
      dot.style.opacity = 0;
      b.animate([{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }], { duration: 420, easing: ease, fill: 'both' });
      b.style.transformBox = 'fill-box'; b.style.transformOrigin = '50% 50%';
      l1.animate([{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)' }], { duration: 520, delay: 300, easing: ease, fill: 'both' });
      l2.animate([{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)' }], { duration: 560, delay: 430, easing: ease, fill: 'both' });
      const drop = dot.animate([
        { opacity: 0, transform: 'translateY(-160px)' },
        { opacity: 1, transform: 'translateY(0)', offset: .62 },
        { transform: 'translateY(-14px)', offset: .8 },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 640, delay: 900, easing: 'cubic-bezier(.4,0,.6,1)', fill: 'both' });
      const done = () => {
        try { sessionStorage.setItem('pdf-in', '1'); } catch (e) {}
        ld.classList.add('go');
        root.classList.remove('ld-on');
        setTimeout(() => ld.remove(), 600);
        const bd = $('.brand .dot');
        if (bd) bd.animate([{ transform: 'translateY(-6px)' }, { transform: 'none' }], { duration: 500, easing: ease });
      };
      drop.finished.then(() => setTimeout(done, 260));
      setTimeout(done, 3200);                                   // never trap the reader
    }
  }

  /* ---------------------------------------------------------- drawer */
  const mb = $('.menu-btn'), dr = $('#drawer');
  if (mb && dr) {
    const close = () => { dr.classList.remove('open'); mb.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''; mb.focus(); };
    mb.addEventListener('click', () => {
      dr.classList.add('open'); mb.setAttribute('aria-expanded', 'true'); document.body.style.overflow = 'hidden';
      $('[data-close]', dr).focus();
    });
    $('[data-close]', dr).addEventListener('click', close);
    dr.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  }

  /* ---------------------------------------------------------- reveal */
  if (!reduce && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    $$('.rv').forEach(el => io.observe(el));
  } else $$('.rv').forEach(el => el.classList.add('in'));

  /* ---------------------------------------------------------- case clocks: days held, counted today */
  const today = new Date();
  $$('[data-since]').forEach(el => {
    const d = new Date(el.dataset.since + 'T00:00:00');
    const until = el.dataset.until ? new Date(el.dataset.until + 'T00:00:00') : today;
    const days = Math.max(0, Math.floor((until - d) / 864e5));
    el.textContent = days.toLocaleString('en-GB');
  });

  /* ---------------------------------------------------------- filters (chips) */
  $$('[data-filter]').forEach(bar => {
    const items = $$(bar.dataset.filter);
    bar.addEventListener('click', e => {
      const b = e.target.closest('.chip');
      if (!b) return;
      $$('.chip', bar).forEach(c => c.setAttribute('aria-pressed', c === b ? 'true' : 'false'));
      const v = b.dataset.v;
      items.forEach(it => { it.hidden = v !== 'all' && !(it.dataset.k || '').split(' ').includes(v); });
    });
  });

  /* ---------------------------------------------------------- search */
  const sf = $('#q');
  if (sf) {
    const out = $('#results'), idx = JSON.parse($('#search-index').textContent);
    const cnt = $('#count');
    const run = () => {
      const q = sf.value.trim().toLowerCase();
      const words = q.split(/\s+/).filter(Boolean);
      const hits = !words.length ? [] : idx.filter(r => words.every(w => r.t.toLowerCase().includes(w)));
      cnt.textContent = words.length ? `${hits.length} on the record for “${sf.value.trim()}”` : '';
      out.innerHTML = hits.slice(0, 60).map(r => `<a class="item" href="${r.u}"><time>${r.d}</time><div><span class="label">${r.k}</span><h2>${r.h}</h2><p>${r.s}</p></div><div></div></a>`).join('');
      history.replaceState(null, '', q ? '?q=' + encodeURIComponent(sf.value.trim()) : location.pathname);
    };
    sf.addEventListener('input', run);
    const q0 = new URLSearchParams(location.search).get('q');
    if (q0) { sf.value = q0; run(); }
  }

  /* ---------------------------------------------------------- copy link, print */
  $$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
    const lab = $('span', b), was = lab.textContent;
    // the Clipboard API is refused in some embedded and older browsers: fall back to a selected field
    const legacy = () => {
      const t = document.createElement('textarea');
      t.value = b.dataset.copy; t.setAttribute('readonly', ''); t.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(t); t.select();
      const ok = document.execCommand('copy'); t.remove(); return ok;
    };
    let ok = false;
    try { await navigator.clipboard.writeText(b.dataset.copy); ok = true; } catch (e) { ok = legacy(); }
    lab.textContent = ok ? 'Link copied' : 'Press Ctrl+C to copy';
    b.classList.add('ok');
    setTimeout(() => { lab.textContent = was; b.classList.remove('ok'); }, 1800);
  }));
  $$('[data-print]').forEach(b => b.addEventListener('click', () => print()));

  /* ---------------------------------------------------------- prototype forms */
  const cf = $('#contact-form');
  if (cf) cf.addEventListener('submit', e => { e.preventDefault(); $('#contact-done').hidden = false; $('#contact-done').focus(); });
  const form = $('#help-form');
  if (form) form.addEventListener('submit', e => {
    e.preventDefault();
    $('#help-done').hidden = false;
    $('#help-done').focus();
  });

  /* ---------------------------------------------------------- the docket
     Every person held is one point. Points are grouped by the law that holds them, and each group
     wears its bracket: sentenced [ ], remand [ , administrative only the bracket's ends (a file nobody
     may read), "unlawful combatants" no bracket at all. Scrub the months to watch the groups change. */
  const fieldEl = $('#field');
  if (!fieldEl) return;
  const data = JSON.parse($('#docket-data').textContent);
  const series = data.series;
  const KINDS = ['sentenced', 'remand', 'administrative', 'unlawful_combatants'];
  const NAMES = ['SENTENCED', 'REMAND', 'ADMINISTRATIVE', 'UNLAWFUL COMBATANTS'];
  const canvas = $('canvas', fieldEl), ctx = canvas.getContext('2d');
  const tip = $('.field-tip', fieldEl);
  const range = $('#scrub'), out = $('#scrub-out'), play = $('#scrub-play');
  const legend = $$('.legend li');
  const css = getComputedStyle(root);
  const C_DOT = css.getPropertyValue('--stamp-night').trim() || '#9A90FF';
  const C_INK = css.getPropertyValue('--on-night').trim() || '#EEF0F4';
  const C_DIM = css.getPropertyValue('--on-night-3').trim() || '#7B8090';
  let W = 0, H = 0, dpr = 1, cur = { ...series[series.length - 1] }, from = cur, to = cur, t0 = 0, hot = -1, boxes = [];
  const maxTotal = Math.max(...series.map(s => KINDS.reduce((a, k) => a + s[k], 0)));

  const size = () => {
    const r = fieldEl.querySelector('.field-c').getBoundingClientRect();
    dpr = Math.min(2, devicePixelRatio || 1);
    W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  };

  // layout: blocks side by side on wide canvases, stacked on tall ones; one pitch for the whole series
  const layout = s => {
    const wide = W / H > .95;
    const pad = wide ? Math.max(22, Math.min(W, H) * .07) + 6 : 22, gap = wide ? Math.max(34, W * .06) : 18, head = wide ? 46 : 42;
    const counts = KINDS.map(k => s[k]);
    const out = [];
    if (wide) {
      const aw = W - pad * 2 - gap * 3, ah = H - pad * 2 - head;
      const p = Math.sqrt(aw * ah / maxTotal) * .97;
      const rows = Math.max(1, Math.floor(ah / p));
      let x = pad;
      counts.forEach((c, i) => {
        const cols = Math.max(1, Math.ceil(c / rows));
        out.push({ x, y: pad + head, w: cols * p, h: rows * p, rows, cols, p, c, vertical: false });
        x += cols * p + gap;
      });
    } else {
      const aw = W - pad * 2, ah = H - pad * 2 - (gap + head) * 3 - head;
      const p = Math.sqrt(aw * ah / maxTotal) * .9;
      const cols = Math.max(1, Math.floor(aw / p));
      let y = pad + head;
      counts.forEach(c => {
        const rows = Math.max(1, Math.ceil(c / cols));
        out.push({ x: pad, y, w: cols * p, h: rows * p, rows, cols, p, c, vertical: true });
        y += rows * p + gap + head;
      });
    }
    return out;
  };

  const bracket = (b, kind, a) => {
    const m = Math.max(7, b.p * 1.6), arm = Math.min(22, Math.max(9, b.w * .18)), lw = 2.4;
    const x0 = b.x - m, x1 = b.x + b.w + m, y0 = b.y - m, y1 = b.y + b.h + m;
    ctx.strokeStyle = C_INK; ctx.globalAlpha = a; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath();
    if (kind === 'sentenced' || kind === 'remand') {
      ctx.moveTo(x0 + arm, y0); ctx.lineTo(x0, y0); ctx.lineTo(x0, y1); ctx.lineTo(x0 + arm, y1);
    }
    if (kind === 'sentenced') { ctx.moveTo(x1 - arm, y0); ctx.lineTo(x1, y0); ctx.lineTo(x1, y1); ctx.lineTo(x1 - arm, y1); }
    if (kind === 'administrative') { ctx.moveTo(x0 + arm, y0); ctx.lineTo(x0, y0); ctx.moveTo(x0 + arm, y1); ctx.lineTo(x0, y1); }
    ctx.stroke();
    ctx.globalAlpha = 1;
  };

  const draw = () => {
    if (!W) return;
    ctx.clearRect(0, 0, W, H);
    boxes = layout(to);                                  // the shape is the month's; the points fill into it
    boxes.forEach((b, i) => {
      b.c = cur[KINDS[i]];
      const a = hot < 0 || hot === i ? 1 : .22;
      bracket(b, KINDS[i], a);
      ctx.fillStyle = C_DOT; ctx.globalAlpha = a;
      const r = Math.max(.9, b.p * .34), c = Math.round(b.c);
      ctx.beginPath();
      for (let k = 0; k < c; k++) {
        const col = b.vertical ? k % b.cols : Math.floor(k / b.rows);
        const row = b.vertical ? Math.floor(k / b.cols) : b.rows - 1 - (k % b.rows);
        const x = b.x + col * b.p + b.p / 2, y = b.y + row * b.p + b.p / 2;
        ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, 6.2832);
      }
      ctx.fill();
      ctx.globalAlpha = a;
      const lift = b.vertical ? 16 : 20;
      ctx.fillStyle = C_INK; ctx.font = '800 17px "Mona Sans", system-ui'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(Math.round(b.c).toLocaleString('en-GB'), b.x - 2, b.y - lift);
      ctx.fillStyle = C_DIM; ctx.font = '600 11.5px "Mona Sans", system-ui';
      ctx.fillText(NAMES[i], b.x - 2, b.y - lift - 20);
      ctx.globalAlpha = 1;
    });
  };

  const setMonth = (i, animate = true) => {
    const s = series[i];
    out.textContent = s.label;
    range.setAttribute('aria-valuetext', `${s.label}: ${s.total.toLocaleString('en-GB')} held, ${s.administrative.toLocaleString('en-GB')} without charge`);
    legend.forEach((li, k) => {
      const v = s[KINDS[k]];
      $('.n b', li).textContent = v.toLocaleString('en-GB');
      $('.n small', li).textContent = Math.round(v / s.total * 100) + '% of all held';
    });
    from = { ...cur }; to = s; t0 = performance.now();
    if (!animate || reduce) { cur = { ...s }; draw(); return; }
    const step = now => {
      const k = Math.min(1, (now - t0) / 650), e = 1 - Math.pow(1 - k, 3);
      KINDS.forEach(kd => { cur[kd] = from[kd] + (to[kd] - from[kd]) * e; });
      draw();
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  range.max = series.length - 1; range.value = series.length - 1;
  range.addEventListener('input', () => { stop(); setMonth(+range.value); });
  let timer = null;
  const stop = () => { clearInterval(timer); timer = null; play.innerHTML = '<svg class="ic"><use href="#i-play"/></svg>'; play.setAttribute('aria-label', 'Play the months'); };
  play.addEventListener('click', () => {
    if (timer) return stop();
    let i = +range.value >= series.length - 1 ? 0 : +range.value;
    range.value = i; setMonth(i);
    play.innerHTML = '<svg class="ic"><use href="#i-pause"/></svg>'; play.setAttribute('aria-label', 'Pause');
    timer = setInterval(() => {
      i++;
      if (i >= series.length) return stop();
      range.value = i; setMonth(i);
    }, 900);
  });

  const pick = (x, y) => boxes.findIndex(b => { const m = b.p * 2.5; return x > b.x - m && x < b.x + b.w + m && y > b.y - m - 30 && y < b.y + b.h + m; });
  const highlight = i => {
    if (i === hot) return;
    hot = i; draw();
    legend.forEach((li, k) => li.classList.toggle('on', k === i));
  };
  canvas.addEventListener('pointermove', e => {
    const r = canvas.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top, i = pick(x, y);
    highlight(i);
    if (i < 0) { tip.classList.remove('on'); return; }
    const li = legend[i];
    tip.innerHTML = `${$('.t', li).firstChild.textContent.trim()}<br><b>${Math.round(cur[KINDS[i]]).toLocaleString('en-GB')}</b> people`;
    tip.style.left = Math.min(W - 230, x + 14) + 'px'; tip.style.top = Math.max(8, y - 50) + 'px';
    tip.classList.add('on');
  });
  canvas.addEventListener('pointerleave', () => { highlight(-1); tip.classList.remove('on'); });
  legend.forEach((li, k) => {
    li.addEventListener('pointerenter', () => highlight(k));
    li.addEventListener('pointerleave', () => highlight(-1));
  });

  new ResizeObserver(size).observe($('.field-c', fieldEl));
  document.fonts.ready.then(draw);
  setMonth(series.length - 1, false);
  // the field fills in once, from nothing, the first time it is seen
  if (!reduce) {
    const zero = Object.fromEntries(KINDS.map(k => [k, 0]));
    cur = { ...cur, ...zero };
    const io = new IntersectionObserver(es => { if (es[0].isIntersecting) { io.disconnect(); setTimeout(() => setMonth(series.length - 1), root.classList.contains('ld-on') ? 1700 : 150); } });
    io.observe(fieldEl);
  }
})();
