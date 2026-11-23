"""Собирает общую доску-схему по всей книге: boards/src/erd.json -> boards/obshchaya-doska.html."""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "obshchaya-doska.html"
MUSTACHE = ('<svg viewBox="0 0 100 50" width="46" height="23" aria-label="усы"><path d="M50 22c-6-10-20-12-30-6-6 4-10 2-14-3 '
            '0 10 8 18 20 17 10 0 18-4 24-8zM50 22c6-10 20-12 30-6 6 4 10 2 14-3 0 10-8 18-20 17-10 0-18-4-24-8z" fill="#2b2118"/></svg>')
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII",
         "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX", "XXXI",
         "XXXII", "XXXIII", "XXXIV"]


def pg(s):
    def rep(m):
        v = m.group(1)
        return f'<span class="pg">{"сноска " + v[2:] if v.startswith("сн") else "стр. " + v}</span>'
    return re.sub(r"§([^\s<,;)]+)", rep, s)


data = json.loads((ROOT / "erd.json").read_text(encoding="utf-8"))
for n in data["nodes"]:
    n["facts"] = [pg(f) for f in n.get("facts", [])]
titles = {}
for p in (ROOT / "data").glob("ch*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    titles[d["num"]] = d["title"]
data["titles"] = {str(k): f"Глава {ROMAN[k]}. {v if v.startswith('(') else '«' + v + '»'}" for k, v in titles.items()}
data["roman"] = ROMAN
data["mustache"] = MUSTACHE

HTML = r"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Общая доска: кто есть кто и кто что сделал · Убийства по алфавиту</title>
<style>
:root{--cork:#c9a26b;--cork-dark:#a9824e;--paper:#fffaf0;--ink:#2b2118;--muted:#6b5a48;--red:#b3261e;--rel:#7d6a55;
 --person:#f6e7c8;--thing:#e6eef6;--place:#e3f0e1;--group:#efe4f6;--yellow:#fff3b0}
*{box-sizing:border-box}
html,body{margin:0;height:100%;font-family:Georgia,"Times New Roman",serif;color:var(--ink)}
body{display:flex;flex-direction:column;background:var(--cork-dark)}
#bar{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:10px 16px;background:var(--paper);box-shadow:0 2px 8px rgba(0,0,0,.3);z-index:5}
#bar h1{font-size:19px;margin:0 8px 0 0}
#bar a{color:var(--ink)}
.ctl{display:flex;align-items:center;gap:8px;font-size:14px}
#chSlider{width:240px}
#chLabel{min-width:290px;font-weight:bold}
button{font:inherit;font-size:14px;padding:6px 12px;border-radius:4px;border:1px solid #8a7258;background:#fff;cursor:pointer}
#revealBtn{background:var(--red);color:#fff;border-color:var(--red);font-weight:bold}
#revealBtn.on{background:#fff;color:var(--red)}
.legend{display:flex;gap:12px;font-size:13px;align-items:center;margin-left:auto}
.legend i{display:inline-block;width:26px;height:0;border-top:2px solid var(--rel);vertical-align:middle;margin-right:4px}
.legend i.act{border-top:3px solid var(--red)}
.legend b{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:middle;margin-right:3px;border:1px solid rgba(0,0,0,.2)}
#main{flex:1;display:flex;min-height:0}
#viewport{flex:1;position:relative;overflow:hidden;cursor:grab;
 background:radial-gradient(circle at 20% 30%,rgba(0,0,0,.06) 1px,transparent 2px) 0 0/14px 14px,var(--cork)}
#viewport.drag{cursor:grabbing}
#world{position:absolute;left:0;top:0;width:2600px;height:1700px;transform-origin:0 0}
.zone{position:absolute;border:3px dashed rgba(60,40,20,.35);border-radius:14px;background:rgba(255,250,240,.12)}
.zone h2{position:absolute;top:-2px;left:16px;margin:0;font-size:30px;color:rgba(43,33,24,.7);letter-spacing:1px}
.zone h2 small{font-size:18px;font-weight:normal;margin-left:10px}
#M h2{font-size:24px}
svg#edges{position:absolute;left:0;top:0;width:2600px;height:1700px;overflow:visible;pointer-events:none}
.edge path{fill:none;stroke:var(--rel);stroke-width:2.2;pointer-events:stroke}
.edge.act path{stroke:var(--red);stroke-width:3.2}
.edge.reveal path{stroke:#7a0f9e;stroke-dasharray:9 5;stroke-width:3.6}
.edge text{font-size:13px;fill:var(--ink);pointer-events:all}
.edge rect{fill:#fffaf0;stroke:rgba(0,0,0,.15);rx:4}
.edge.act text{fill:#7a1611;font-weight:bold}
.edge.reveal text{fill:#5b0b76}
.edge.dim{opacity:.08}
.node{position:absolute;width:204px;background:var(--paper);border-radius:4px;padding:8px 10px 8px 64px;min-height:64px;
 box-shadow:0 4px 9px rgba(0,0,0,.3);cursor:pointer;transition:opacity .2s,box-shadow .2s}
.node::before{content:"";position:absolute;top:-7px;left:50%;width:14px;height:14px;margin-left:-7px;border-radius:50%;
 background:radial-gradient(circle at 35% 35%,#ff8a80,#d33 55%,#7a1010);box-shadow:0 2px 3px rgba(0,0,0,.4)}
.node .ic{position:absolute;left:8px;top:8px;width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;border:2px solid #fff;box-shadow:0 0 0 1px var(--cork-dark)}
.node.person .ic{background:var(--person)} .node.thing .ic{background:var(--thing)} .node.place .ic{background:var(--place)} .node.group .ic{background:var(--group)}
.node.place{border-top:5px solid #5d8f55} .node.thing{border-top:5px solid #5577a0} .node.group{border-top:5px solid #8a5ca8} .node.person{border-top:5px solid #b88a3a}
.node .nm{font-weight:bold;font-size:15px;line-height:1.15}
.node .rl{font-size:12.5px;color:var(--muted);font-style:italic;margin-top:3px;line-height:1.2}
.node .chb{position:absolute;right:6px;bottom:4px;font-size:10.5px;color:var(--muted)}
.node.killer{box-shadow:0 0 0 4px #7a0f9e,0 4px 9px rgba(0,0,0,.3)}
.node.killer .rl{color:#7a0f9e;font-weight:bold;font-style:normal}
.node.framed .rl{color:#7a0f9e;font-weight:bold}
.node.sel{box-shadow:0 0 0 4px var(--yellow),0 0 0 7px var(--ink),0 6px 14px rgba(0,0,0,.4)}
.node.dim{opacity:.22}
.node.hidden,.edge.hidden{display:none}
#panel{width:340px;background:var(--paper);overflow:auto;padding:16px 18px;box-shadow:-2px 0 8px rgba(0,0,0,.25);font-size:14.5px;line-height:1.4}
#panel h3{margin:0 0 2px;font-size:20px}
#panel .rl{color:var(--muted);font-style:italic;margin:0 0 10px}
#panel ul{padding-left:18px;margin:6px 0 12px} #panel li{margin:4px 0}
#panel h4{margin:12px 0 4px;font-size:14px;letter-spacing:1px;text-transform:uppercase;color:var(--muted)}
#panel .cx{margin:6px 0;padding:6px 8px;border-left:4px solid var(--rel);background:#fff}
#panel .cx.act{border-color:var(--red)} #panel .cx.reveal{border-color:#7a0f9e}
#panel .cx a{color:var(--ink);font-weight:bold;cursor:pointer;text-decoration:underline dotted}
#panel q{font-style:italic;quotes:"«" "»"}
.pg{color:var(--muted);font-size:11.5px;white-space:nowrap}
#timeline{display:flex;gap:0;background:var(--paper);border-top:2px solid var(--cork-dark);z-index:5}
#timeline button{flex:1;border:0;border-right:2px dashed var(--cork-dark);border-radius:0;padding:8px 6px;background:transparent;text-align:center;font-size:13.5px}
#timeline button:last-child{border-right:0}
#timeline button b{display:block;font-size:15px;color:var(--red)}
#timeline button.cur{background:var(--yellow)}
#help{font-size:12.5px;color:var(--muted)}
@media print{
 @page{size:A3 landscape;margin:6mm}
 body{display:block;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 #bar .ctl,#bar .legend button,#panel,#timeline,#help,#bar a{display:none}
 #main{display:block} #viewport{overflow:visible;background:#fff;height:auto}
 #world{transform:none!important;zoom:.56;position:relative}
 .node{box-shadow:0 0 0 1px #999} .node.dim,.edge.dim{opacity:1}
}
</style></head>
<body>
<div id="bar">
  <h1>🔎 «Убийства по алфавиту» — кто есть кто и кто что сделал</h1>
  <a href="index.html">← все главы</a>
  <div class="ctl">Показать события по <input type="range" id="chSlider" min="1" max="34" value="34"> <span id="chLabel"></span></div>
  <div class="ctl"><button id="revealBtn">🔓 Показать разгадку</button><button id="fitBtn">⤢ Вся доска</button></div>
  <div class="legend">
    <span><i></i>отношения</span><span><i class="act"></i>действия</span>
    <span><b style="background:var(--person)"></b>люди</span><span><b style="background:var(--thing)"></b>улики</span>
    <span><b style="background:var(--place)"></b>места</span><span><b style="background:var(--group)"></b>группы</span>
  </div>
</div>
<div id="main">
  <div id="viewport"><div id="world"><svg id="edges"><defs>
    <marker id="arAct" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="#b3261e"/></marker>
    <marker id="arRev" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="#7a0f9e"/></marker>
  </defs></svg></div></div>
  <div id="panel"><h3>Как пользоваться</h3>
    <p>Нажмите на любую карточку — подсветятся все её связи, а здесь появятся детали из книги.</p>
    <p><b>Колесо мыши</b> — приблизить, <b>перетаскивание</b> — двигать доску.</p>
    <p><b>Ползунок</b> вверху показывает только то, что известно к выбранной главе.</p>
    <p><b>Красные</b> нити — действия (убил, нашёл тело, прислал письмо). <b>Серые</b> — отношения (муж, сестра, работает в…).</p>
    <p>Кнопка <b>«Показать разгадку»</b> открывает, кто настоящий A. B. C. — <i>спойлер!</i></p>
    <p id="help">Все факты взяты из текста книги; «стр.» — страница PDF.</p></div>
</div>
<div id="timeline"></div>
<script>
const DATA = __DATA__;
const W = document.getElementById('world'), VP = document.getElementById('viewport'), SV = document.getElementById('edges');
const S = {ch: 34, reveal: false, sel: null, k: 1, x: 0, y: 0};
const byId = {}; DATA.nodes.forEach(n => byId[n.id] = n);
const RN = DATA.roman;

// zones
DATA.zones.forEach(z => {
  const d = document.createElement('div'); d.className = 'zone'; d.id = z.id;
  Object.assign(d.style, {left: z.x + 'px', top: z.y + 'px', width: z.w + 'px', height: z.h + 'px'});
  d.innerHTML = `<h2>${z.title}<small>${z.date}</small></h2>`; W.insertBefore(d, SV);
});
// nodes
DATA.nodes.forEach(n => {
  const d = document.createElement('div'); d.className = 'node ' + n.kind; d.id = 'n-' + n.id;
  d.innerHTML = `<div class="ic">${n.icon === 'mustache' ? DATA.mustache : n.icon}</div><div class="nm">${n.name}</div><div class="rl">${n.role || ''}</div><div class="chb">с гл. ${RN[n.ch]}</div>`;
  W.appendChild(d); n.el = d;
  d.addEventListener('click', e => { e.stopPropagation(); select(n.id); });
});
function place() {
  DATA.nodes.forEach(n => { n.w = n.el.offsetWidth; n.h = n.el.offsetHeight; n.el.style.left = (n.x - n.w / 2) + 'px'; n.el.style.top = (n.y - n.h / 2) + 'px'; });
}
// edges
const NS = 'http://www.w3.org/2000/svg';
const pairCount = {}, pairIdx = {};
DATA.edges.forEach(e => { const k = [e.from, e.to].sort().join('|'); pairCount[k] = (pairCount[k] || 0) + 1; });
DATA.edges.forEach((e, i) => {
  const k = [e.from, e.to].sort().join('|'); pairIdx[k] = (pairIdx[k] || 0); e.off = (pairIdx[k] - (pairCount[k] - 1) / 2) * 70; pairIdx[k]++;
  const g = document.createElementNS(NS, 'g'); g.setAttribute('class', 'edge ' + e.type + (e.reveal ? ' reveal' : ''));
  const p = document.createElementNS(NS, 'path'); const r = document.createElementNS(NS, 'rect'); const t = document.createElementNS(NS, 'text');
  if (e.type === 'act') p.setAttribute('marker-end', e.reveal ? 'url(#arRev)' : 'url(#arAct)');
  t.textContent = e.label; const ti = document.createElementNS(NS, 'title');
  ti.textContent = `${e.label} — гл. ${RN[e.ch]}, стр. ${e.pg}` + (e.quote ? `\n«${e.quote}»` : ''); g.appendChild(ti);
  g.append(p, r, t); SV.appendChild(g); e.g = g; e.p = p; e.r = r; e.t = t;
});
function clip(cx, cy, w, h, tx, ty) { const dx = tx - cx, dy = ty - cy; const s = Math.min((w / 2 + 6) / Math.abs(dx || 1e-6), (h / 2 + 6) / Math.abs(dy || 1e-6)); return [cx + dx * s, cy + dy * s]; }
function route() {
  DATA.edges.forEach(e => {
    const a = byId[e.from], b = byId[e.to];
    const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2, dx = b.x - a.x, dy = b.y - a.y, L = Math.hypot(dx, dy) || 1;
    const bend = e.off + (pairCount[[e.from, e.to].sort().join('|')] === 1 ? Math.min(40, L * .06) : 0);
    const cx = mx - dy / L * bend, cy = my + dx / L * bend;
    const [sx, sy] = clip(a.x, a.y, a.w, a.h, cx, cy), [ex, ey] = clip(b.x, b.y, b.w, b.h, cx, cy);
    e.p.setAttribute('d', `M${sx},${sy} Q${cx},${cy} ${ex},${ey}`);
    const lx = .25 * sx + .5 * cx + .25 * ex, ly = .25 * sy + .5 * cy + .25 * ey;
    e.t.setAttribute('x', lx); e.t.setAttribute('y', ly + 4); e.t.setAttribute('text-anchor', 'middle');
    const bb = e.t.getBBox(); Object.entries({x: bb.x - 4, y: bb.y - 2, width: bb.width + 8, height: bb.height + 4}).forEach(([k, v]) => e.r.setAttribute(k, v));
  });
}
// visibility
function visNode(n) { return n.ch <= S.ch && (!n.reveal || S.reveal); }
function visEdge(e) { return e.ch <= S.ch && (!e.reveal || S.reveal) && visNode(byId[e.from]) && visNode(byId[e.to]); }
function render() {
  DATA.nodes.forEach(n => {
    n.el.classList.toggle('hidden', !visNode(n));
    const rr = S.reveal && n.revealRole ? n.revealRole : n.role; n.el.querySelector('.rl').textContent = rr || '';
    n.el.classList.toggle('killer', S.reveal && n.id === 'franklin');
    n.el.classList.toggle('framed', S.reveal && n.id === 'cust');
  });
  DATA.edges.forEach(e => e.g.classList.toggle('hidden', !visEdge(e)));
  document.getElementById('chLabel').textContent = (DATA.titles[S.ch] || 'Глава ' + RN[S.ch]);
  document.getElementById('chSlider').value = S.ch;
  const rb = document.getElementById('revealBtn'); rb.classList.toggle('on', S.reveal); rb.textContent = S.reveal ? '🔒 Скрыть разгадку' : '🔓 Показать разгадку';
  document.querySelectorAll('#timeline button').forEach(b => b.classList.toggle('cur', +b.dataset.ch === S.ch));
  highlight(); if (S.sel) panel(S.sel);
}
function highlight() {
  const sel = S.sel && visNode(byId[S.sel]) ? S.sel : null; const nb = new Set([sel]);
  DATA.edges.forEach(e => { const on = !sel || e.from === sel || e.to === sel; e.g.classList.toggle('dim', !on); if (sel && on && visEdge(e)) { nb.add(e.from); nb.add(e.to); } });
  DATA.nodes.forEach(n => { n.el.classList.toggle('dim', !!sel && !nb.has(n.id)); n.el.classList.toggle('sel', n.id === sel); });
}
function panel(id) {
  const n = byId[id]; const P = document.getElementById('panel');
  const cx = DATA.edges.filter(e => visEdge(e) && (e.from === id || e.to === id)).sort((a, b) => a.ch - b.ch).map(e => {
    const other = byId[e.from === id ? e.to : e.from]; const dir = e.from === id ? `${e.label} → <a data-id="${other.id}">${other.name}</a>` : `<a data-id="${other.id}">${other.name}</a> → ${e.label}`;
    return `<div class="cx ${e.type}${e.reveal ? ' reveal' : ''}">${dir} <span class="pg">гл. ${RN[e.ch]}, стр. ${e.pg}</span>${e.quote ? `<br><q>${e.quote}</q>` : ''}</div>`;
  }).join('');
  const rr = S.reveal && n.revealRole ? n.revealRole : n.role;
  P.innerHTML = `<h3>${n.icon === 'mustache' ? '' : n.icon + ' '}${n.name}</h3><p class="rl">${rr || ''} · появляется в гл. ${RN[n.ch]}</p>` +
    `<h4>Что о нём известно</h4><ul>${n.facts.map(f => `<li>${f}</li>`).join('')}</ul><h4>Связи (к гл. ${RN[S.ch]})</h4>${cx || '<p>пока нет</p>'}`;
  P.querySelectorAll('a[data-id]').forEach(a => a.onclick = () => select(a.dataset.id));
}
function select(id) { S.sel = id; highlight(); panel(id); }
VP.addEventListener('click', () => { if (moved) return; S.sel = null; highlight(); });
// controls
document.getElementById('chSlider').oninput = ev => { S.ch = +ev.target.value; if (S.ch < 34) S.reveal = false; render(); };
document.getElementById('revealBtn').onclick = () => { S.reveal = !S.reveal; if (S.reveal) S.ch = 34; render(); };
document.getElementById('fitBtn').onclick = fit;
const TL = [[1, 'Письмо Пуаро', 'гл. I'], [3, 'A — Андовер', '21 июня'], [9, 'B — Бэксхилл', '25 июля'], [14, 'C — Керстон', '30 июля'],
  [18, 'Спецкоманда', 'гл. XVIII'], [24, 'D — Донкастер', '11 сентября'], [30, 'Каст в полиции', 'гл. XXX'], [33, 'Суд и тюрьма', 'ноябрь']];
TL.forEach(([ch, t, d]) => { const b = document.createElement('button'); b.dataset.ch = ch; b.innerHTML = `<b>${d}</b>${t}`; b.onclick = () => { S.ch = ch; S.reveal = false; render(); }; document.getElementById('timeline').appendChild(b); });
// pan & zoom
function apply() { W.style.transform = `translate(${S.x}px,${S.y}px) scale(${S.k})`; }
function fit() { const r = VP.getBoundingClientRect(); S.k = Math.min(r.width / 2600, r.height / 1700) * .98; S.x = (r.width - 2600 * S.k) / 2; S.y = (r.height - 1700 * S.k) / 2; apply(); }
VP.addEventListener('wheel', ev => { ev.preventDefault(); const r = VP.getBoundingClientRect(); const mx = ev.clientX - r.left, my = ev.clientY - r.top;
  const nk = Math.max(.25, Math.min(2.5, S.k * (ev.deltaY < 0 ? 1.12 : 1 / 1.12))); S.x = mx - (mx - S.x) * nk / S.k; S.y = my - (my - S.y) * nk / S.k; S.k = nk; apply(); }, {passive: false});
let drag = null, moved = false;
VP.addEventListener('mousedown', ev => { drag = [ev.clientX, ev.clientY, S.x, S.y]; moved = false; });
window.addEventListener('mousemove', ev => { if (!drag) return; const dx = ev.clientX - drag[0], dy = ev.clientY - drag[1]; if (Math.abs(dx) + Math.abs(dy) > 4) { moved = true; VP.classList.add('drag'); } S.x = drag[2] + dx; S.y = drag[3] + dy; apply(); });
window.addEventListener('mouseup', () => { drag = null; VP.classList.remove('drag'); setTimeout(() => moved = false, 0); });
window.addEventListener('resize', fit);
place(); route(); render(); fit();
</script></body></html>"""

OUT.write_text(HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
print("built", OUT.name, len(data["nodes"]), "nodes", len(data["edges"]), "edges")
