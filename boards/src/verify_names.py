"""Эвристика: имена/названия с заглавной буквы из досок должны встречаться в тексте главы (по началу слова)."""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
BOOK = ROOT / "book" / "chapters"
SKIP = {"глава", "пуаро"}


def clean(s):
    s = re.sub(r"=== PAGE \d+ ===", " ", s)
    return s.lower().replace("ё", "е")


def walk(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for x in o:
            yield from walk(x)
    elif isinstance(o, dict):
        for v in o.values():
            yield from walk(v)


for p in sorted((ROOT / "boards" / "src" / "data").glob("ch*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    n = d["num"]
    text = clean((BOOK / f"ch{n:02d}.txt").read_text(encoding="utf-8") + (BOOK / "notes.txt").read_text(encoding="utf-8"))
    miss = set()
    for s in walk({k: v for k, v in d.items() if k not in ("remember",)}):
        s = re.sub(r"<[^>]+>", " ", s)
        s = re.sub(r"§\S+", " ", s)
        for m in re.finditer(r"(?<![.!?«\"—–-] )(?<!^)\b([А-ЯЁ][а-яё]{3,})", s):
            w = m.group(1).lower().replace("ё", "е")
            if w in SKIP:
                continue
            if w[: max(4, len(w) - 2)] not in text:
                miss.add(m.group(1))
    if miss:
        print(f"ch{n:02d}: {', '.join(sorted(miss))}")
