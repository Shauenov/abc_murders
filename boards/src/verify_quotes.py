"""Проверяет, что каждая цитата <q>…</q> из досок дословно есть в тексте главы книги."""
import json, re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BOOK = ROOT / "book" / "chapters"


def norm(s):
    s = re.sub(r"=== PAGE \d+ ===", " ", s)
    s = re.sub(r"\[\d+\]", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.lower().replace("ё", "е").replace(" ", " ")
    s = re.sub(r"[«»\"'“”…\.,;:!?\-–—()\[\]]", " ", s)
    s = re.sub(r"\d+", " ", s) if False else s
    return re.sub(r"\s+", " ", s).strip()


def walk(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for x in o:
            yield from walk(x)
    elif isinstance(o, dict):
        for v in o.values():
            yield from walk(v)


bad = 0
total = 0
for p in sorted((ROOT / "boards" / "src" / "data").glob("ch*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    n = d["num"]
    text = norm((BOOK / f"ch{n:02d}.txt").read_text(encoding="utf-8"))
    # сноски и спец. главы: цитаты могут быть и из сносок
    notes = norm((BOOK / "notes.txt").read_text(encoding="utf-8"))
    for s in walk(d):
        for m in re.finditer(r"<q>(.*?)</q>", s):
            q = norm(m.group(1))
            if not q:
                continue
            total += 1
            if q not in text and q not in notes:
                bad += 1
                print(f"ch{n:02d}: НЕ НАЙДЕНО: {m.group(1)}")
print(f"проверено цитат: {total}, не найдено: {bad}")
