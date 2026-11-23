"""Собирает доски улик: boards/src/data/chNN.json -> boards/glava-NN.html + boards/index.html.

Мини-разметка в строках:
  §12      -> «стр. 12» (номер страницы PDF);  §сн10 -> «сноска 10»
  в связях: "p:Имя" — персонаж, "t:Вещь" — предмет, "l:Место" — место,
            "> глагол" — красная стрелка, остальное — обычный текст.
"""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent
CSS = (ROOT / "style.css").read_text(encoding="utf-8")
MUSTACHE = ('<svg viewBox="0 0 100 50" width="70" height="35" aria-label="усы"><path d="M50 22c-6-10-20-12-30-6-6 4-10 2-14-3 '
            '0 10 8 18 20 17 10 0 18-4 24-8zM50 22c6-10 20-12 30-6 6 4 10 2 14-3 0 10-8 18-20 17-10 0-18-4-24-8z" fill="#2b2118"/></svg>')
KIND = {"p": "person", "t": "thing", "l": "place"}
SECTIONS = [("who", "Кто"), ("things", "Улики и предметы"), ("where", "Где")]


def pg(s):
    def rep(m):
        v = m.group(1)
        if v.startswith("сн"):
            return f'<span class="pg">сноска {v[2:]}</span>'
        return f'<span class="pg">стр. {v}</span>'
    return re.sub(r"§([^\s<,;)]+)", rep, s)


def icon(i):
    return MUSTACHE if i == "mustache" else html.escape(i)


def card(c):
    k = c["k"]
    parts = [f'<div class="card {k}"><span class="pin"></span><span class="tag">{c["tag"]}</span>',
             f'<div class="portrait">{icon(c["icon"])}</div><h3>{c["name"]}</h3>']
    if c.get("role"):
        parts.append(f'<p class="role">{pg(c["role"])}</p>')
    if c.get("letter"):
        parts.append(f'<div class="letter">{c["letter"]}</div>')
    if c.get("items"):
        parts.append("<ul>" + "".join(f"<li>{pg(i)}</li>" for i in c["items"]) + "</ul>")
    parts.append("</div>")
    return "".join(parts)


def link(row):
    out = []
    for tok in row:
        if tok[:2] in ("p:", "t:", "l:"):
            out.append(f'<span class="chip {KIND[tok[0]]}">{tok[2:]}</span>')
        elif tok.startswith("> "):
            out.append(f'<span class="arrow">{tok[2:]}</span>')
        else:
            out.append(f"<span>{pg(tok)}</span>")
    return '<div class="link">' + "".join(out) + "</div>"


def ttl(d):
    t = d["title"]
    return t if t.startswith("(") else f"«{t}»"


def page(d, prev, nxt):
    n = d["num"]
    nav = '<nav class="chap">' + (
        f'<a href="glava-{prev:02d}.html">← Глава {prev}</a>' if prev else "<span></span>") + \
        '<a href="index.html">Все главы</a>' + (
        f'<a href="glava-{nxt:02d}.html">Глава {nxt} →</a>' if nxt else "<span></span>") + "</nav>"
    body = [nav, f'<header><span class="pin"></span><h1>🔎 Глава {d["roman"]}. {ttl(d)}</h1>'
            '<p>Агата Кристи, «Убийства по алфавиту». Все детали и цитаты взяты из текста книги; '
            '<span class="pg">стр.</span> — номер страницы в PDF.</p>'
            f'<span class="narr">{d["narr"]}</span></header>']
    for key, title in SECTIONS:
        if d.get(key):
            body.append(f'<h2 class="section">{title}</h2><div class="grid">' + "".join(card(c) for c in d[key]) + "</div>")
    if d.get("links"):
        body.append('<h2 class="section">Кто что сделал</h2><div class="links"><span class="pin"></span>'
                    + "".join(link(r) for r in d["links"]) + "</div>")
    if d.get("timeline"):
        body.append('<h2 class="section">Когда</h2><div class="timeline"><span class="pin"></span>'
                    + "".join(f'<div class="step"><span class="when">{s["when"]}</span><p>{pg(s["text"])}</p></div>'
                              for s in d["timeline"]) + "</div>")
    if d.get("remember"):
        body.append('<div class="remember"><span class="pin"></span><h2>📌 Запомни к викторине</h2><ol>'
                    + "".join(f"<li>{pg(r)}</li>" for r in d["remember"]) + "</ol></div>")
    body.append('<footer>Источник: А. Кристи, «Убийства по алфавиту», пер. А. С. Петухова (Эксмо, 2015). '
                'Страницы указаны по PDF.</footer>')
    return (f'<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Глава {d["roman"]} {ttl(d)} — доска улик · Убийства по алфавиту</title>'
            f'<style>{CSS}</style></head><body><div class="board">{"".join(body)}</div></body></html>')


def main():
    data = sorted((json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "data").glob("ch*.json")),
                  key=lambda d: d["num"])
    nums = [d["num"] for d in data]
    for i, d in enumerate(data):
        prev = nums[i - 1] if i else None
        nxt = nums[i + 1] if i + 1 < len(nums) else None
        (OUT / f'glava-{d["num"]:02d}.html').write_text(page(d, prev, nxt), encoding="utf-8")
    toc = "".join(f'<a href="glava-{d["num"]:02d}.html"><b>ГЛАВА {d["roman"]}</b>{ttl(d)}</a>' for d in data)
    (OUT / "index.html").write_text(
        f'<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Убийства по алфавиту — доски улик</title><style>{CSS}</style></head><body><div class="board">'
        '<header><span class="pin"></span><h1>🔎 «Убийства по алфавиту» — доски улик</h1>'
        '<p>Агата Кристи. Шпаргалка к викторине: по одной доске на главу. Все факты — из текста книги.</p></header>'
        '<a class="bigboard" href="obshchaya-doska.html"><span class="pin"></span>🕸️ <b>Общая доска: кто есть кто и кто что сделал</b>'
        '<small>Все персонажи, улики и места книги, их связи и действия — с ползунком по главам и кнопкой разгадки</small></a>'
        f'<div class="toc">{toc}</div></div></body></html>', encoding="utf-8")
    print("built", len(data), "boards:", nums)


if __name__ == "__main__":
    main()
