/* Idealized slab explorer — standalone port of the defense site's
   Ch2SlabFieldViewer: sliders over the full-factorial sweep (notched at
   the available values), field rows x Simulation | Theory | Difference |
   x10 thumbnails, one big panel with the dashed free-slip patch, and a
   per-field colour scale that is FIXED at every slider position. */
'use strict';

const DATA = 'data/';
const COLS = [
  { id: 'da', short: 'Simulation', title: 'Simulation' },
  { id: 'theory', short: 'Theory', title: 'Theory' },
  { id: 'diff', short: 'Difference', title: 'Simulation − Theory' },
  { id: 'diff_zoom', short: '×10', title: 'Simulation − Theory · ×10' },
];
const PARAMS = [
  { key: 'H', sym: 'H', unit: 'km', fmt: (v) => num(v / 1000) },
  { key: 'alpha_deg', sym: 'α', unit: '°', fmt: (v) => num(v) },
  { key: 'gamma', sym: 'γ', unit: '', fmt: (v) => num(v) },
  { key: 'R', sym: 'R', unit: 'km', fmt: (v) => num(v / 1000) },
];
const FIELD_HTML = {
  st1: '<i>σ</i><sub>t1</sub>', st2: '<i>σ</i><sub>t2</sub>',
  trr: '<i>τ</i><sub><i>rr</i></sub>', trt: '<i>τ</i><sub><i>rθ</i></sub>',
  ttt: '<i>τ</i><sub><i>θθ</i></sub>', txx: '<i>τ</i><sub><i>xx</i></sub>',
  tyy: '<i>τ</i><sub><i>yy</i></sub>', txy: '<i>τ</i><sub><i>xy</i></sub>',
  srr: 'Δ<i>σ</i><sub><i>rr</i></sub>', stt: 'Δ<i>σ</i><sub><i>θθ</i></sub>',
  srt: 'Δ<i>σ</i><sub><i>rθ</i></sub>',
};

function num(v) { return String(Math.round(v * 100) / 100); }
function fmtKpa(v) {
  const a = Math.abs(v);
  return (a >= 10 ? Math.round(v) : a >= 1 ? v.toFixed(1) : v.toFixed(2)) + ' kPa';
}

let MAN = null;
let byParams = {};            // "R|H|alpha|gamma" -> run id
const state = { run: '', field: 'st1', col: 'da' };

function key(r) { return [r.R, r.H, r.alpha_deg, r.gamma].join('|'); }
function run() { return MAN.runs[state.run]; }
function src(f, c) {
  const r = run();
  const p = r[c] && r[c][f];
  return p ? DATA + p : '';
}

/* ── URL hash <-> state, so a view can be linked directly ── */
function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  if (h.get('run') && MAN.runs[h.get('run')]) state.run = h.get('run');
  if (h.get('field') && MAN.fields_all.includes(h.get('field'))) state.field = h.get('field');
  if (h.get('col') && COLS.some((c) => c.id === h.get('col'))) state.col = h.get('col');
}
function writeHash() {
  history.replaceState(null, '',
    `#run=${state.run}&field=${state.field}&col=${state.col}`);
}

/* ── build ── */
function build() {
  const app = document.getElementById('app');
  app.innerHTML = '';

  // sliders
  const ctl = el('div', 'sv-controls');
  for (const p of PARAMS) {
    const stops = MAN.params[p.key];
    const sl = el('div', 'sv-sl');
    sl.appendChild(el('span', 'sv-sym', p.sym));
    const track = el('div', 'sv-track');
    const input = document.createElement('input');
    input.type = 'range';
    input.min = 0; input.max = stops.length - 1; input.step = 1;
    input.setAttribute('aria-label', p.sym);
    input.dataset.key = p.key;
    input.addEventListener('input', () => onSlide(p.key, +input.value));
    track.appendChild(input);
    const ticks = el('div', 'sv-ticks');
    stops.forEach((v, i) => {
      const t = el('div', 'sv-tick');
      t.style.left = stops.length === 1 ? '50%' : `${(i / (stops.length - 1)) * 100}%`;
      t.appendChild(el('i', ''));
      t.appendChild(el('span', '', p.fmt(v)));
      ticks.appendChild(t);
    });
    track.appendChild(ticks);
    sl.appendChild(track);
    sl.appendChild(el('span', 'sv-val', ''));
    ctl.appendChild(sl);
  }
  app.appendChild(ctl);

  const body = el('div', 'sv-body');

  // picker
  const pick = el('div', 'sv-pick');
  const head = el('div', 'sv-head');
  head.appendChild(el('span', ''));
  for (const c of COLS) head.appendChild(el('span', '', c.short));
  pick.appendChild(head);
  for (const f of MAN.fields_all) {
    const row = el('div', 'sv-row');
    const lab = el('span', 'sv-row-label');
    lab.innerHTML = FIELD_HTML[f] || f;
    row.appendChild(lab);
    for (const c of COLS) {
      const b = document.createElement('button');
      b.className = 'sv-cell';
      b.dataset.f = f; b.dataset.c = c.id;
      b.setAttribute('aria-label', `${f} ${c.title}`);
      const img = document.createElement('img');
      img.alt = ''; img.draggable = false; img.loading = 'lazy'; img.decoding = 'async';
      b.appendChild(img);
      b.addEventListener('click', () => { state.field = f; state.col = c.id; render(); });
      row.appendChild(b);
    }
    pick.appendChild(row);
  }
  body.appendChild(pick);

  // big panel
  const paper = el('div', 'sv-paper');
  paper.innerHTML = `
    <div class="sv-title">
      <span class="sv-title-col" id="colTitle"></span>
      <img id="eqImg" alt="" />
    </div>
    <div class="sv-plot">
      <div class="sv-ylab">y [km]</div>
      <div class="sv-img">
        <img id="bigImg" alt="" draggable="false" />
        <svg class="sv-over" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <ellipse id="patch" class="sv-patch" vector-effect="non-scaling-stroke" />
        </svg>
        <div class="sv-xt" id="xt"></div>
        <div class="sv-yt" id="yt"></div>
      </div>
      <div class="sv-xlab">x [km]</div>
    </div>
    <div class="sv-cbar">
      <div class="sv-cbar-bar"></div>
      <div class="sv-cbar-ticks"><span id="cbLo"></span><span>0</span><span id="cbHi"></span></div>
      <div class="sv-cbar-note">fixed scale &mdash; identical at every slider position</div>
    </div>
    <div class="sv-max" id="maxTxt"></div>`;
  body.appendChild(paper);
  app.appendChild(body);
}

function onSlide(k, i) {
  const r = run();
  const want = { R: r.R, H: r.H, alpha_deg: r.alpha_deg, gamma: r.gamma };
  want[k] = MAN.params[k][i];
  const id = byParams[[want.R, want.H, want.alpha_deg, want.gamma].join('|')];
  if (id) { state.run = id; render(); }
}

/* ── render current state into the built DOM ── */
function render() {
  const r = run();

  for (const input of document.querySelectorAll('.sv-sl input')) {
    const k = input.dataset.key;
    const stops = MAN.params[k];
    const i = stops.findIndex((v) => Math.abs(v - r[k]) < 1e-9);
    input.value = i;
    const p = PARAMS.find((q) => q.key === k);
    input.closest('.sv-sl').querySelector('.sv-val').textContent =
      p.fmt(r[k]) + (p.unit === '°' ? '°' : p.unit ? ' ' + p.unit : '');
    input.closest('.sv-track').querySelectorAll('.sv-tick').forEach((t, j) =>
      t.classList.toggle('on', j === i));
  }

  for (const b of document.querySelectorAll('.sv-cell')) {
    b.classList.toggle('sv-cell--on', b.dataset.f === state.field && b.dataset.c === state.col);
    b.querySelector('img').src = src(b.dataset.f, b.dataset.c);
  }

  const col = COLS.find((c) => c.id === state.col);
  document.getElementById('colTitle').textContent = col.title;
  const eq = document.getElementById('eqImg');
  eq.src = `assets/eq/fb_${state.field}.svg`;
  eq.style.height = '30px'; eq.style.width = 'auto';
  document.getElementById('bigImg').src = src(state.field, state.col);

  const d = r.domain_km;
  const patch = document.getElementById('patch');
  patch.setAttribute('cx', ((0 - d[0]) / (d[1] - d[0])) * 100);
  patch.setAttribute('cy', ((d[3] - 0) / (d[3] - d[2])) * 100);
  patch.setAttribute('rx', (r.patch_km / (d[1] - d[0])) * 100);
  patch.setAttribute('ry', (r.patch_km / (d[3] - d[2])) * 100);

  const ticks = [];
  for (let t = Math.ceil(d[0] / 25) * 25; t <= d[1] + 1e-6; t += 25) ticks.push(t);
  document.getElementById('xt').innerHTML = ticks.map((t) => `<span>${t}</span>`).join('');
  document.getElementById('yt').innerHTML =
    [...ticks].reverse().map((t) => `<span>${t}</span>`).join('');

  const vl = MAN.vlim_kpa[state.field] / (state.col === 'diff_zoom' ? 10 : 1);
  document.getElementById('cbLo').textContent = '−' + num(vl);
  document.getElementById('cbHi').textContent = num(vl) + ' kPa';
  const m = r.max_kpa;
  const mv = state.col === 'da' ? m.sim_da[state.field]
    : state.col === 'theory' ? m.theory[state.field] : m.diff_abs[state.field];
  document.getElementById('maxTxt').textContent =
    'max ' + (mv === undefined ? '—' : fmtKpa(mv));

  writeHash();
}

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

fetch(DATA + 'manifest.json')
  .then((r) => r.json())
  .then((m) => {
    MAN = m;
    for (const [id, r] of Object.entries(m.runs)) byParams[key(r)] = id;
    state.run = m.hero;
    readHash();
    if (!MAN.runs[state.run]) state.run = Object.keys(m.runs)[0];
    document.getElementById('wait').remove();
    build();
    render();
    window.addEventListener('hashchange', () => { readHash(); render(); });
  })
  .catch(() => {
    document.getElementById('wait').textContent =
      'could not load data/manifest.json — is the bake finished?';
  });
