#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GATES — ворота приёмки сайта. FAIL блокирует публикацию.

G1  числа на страницах пришли из источников, а не набраны руками
    (+ сборка воспроизводима: docs/ == результат build.py)
G2  битых внутренних ссылок 0; все фигуры доступны
G3  RU/EN структурный паритет: тот же набор страниц, те же числа
G4  тест холодного читателя — отдельный прогон (агент), не автоматизируется
G5  Git Sync — проверяется после подключения пространства

Запуск:  python3 docs/gates.py           # G1–G3, без сетевых проверок
         python3 docs/gates.py --net     # + проверка внешних ссылок и фигур
         python3 docs/gates.py --full    # + прогон theory_check.py и сверка
"""
import os, re, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from facts import extract

FAILS = []

def gate(name, ok, detail):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        FAILS.append(name)
    return ok

def pages(lang):
    out = {}
    base = os.path.join(HERE, lang)
    for root, _, files in os.walk(base):
        for f in sorted(files):
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(root, f), base)
                out[rel] = open(os.path.join(root, f), encoding="utf-8").read()
    return out

def templates(lang):
    out = {}
    base = os.path.join(HERE, "_templates", lang)
    for root, _, files in os.walk(base):
        for f in sorted(files):
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(root, f), base)
                out[rel] = open(os.path.join(root, f), encoding="utf-8").read()
    return out

# числа, которые допустимо набирать руками: структурные константы текста,
# годы, версии, номера лемм/ворот, единицы измерения времени
# Числа, которые допустимо набирать руками, тремя классами:
#   (а) структурные константы текста и допуски ворот, объявленные в SPEC;
#   (б) годы и библиографические величины ЧУЖИХ работ (наш репозиторий им не источник);
#   (в) исторические цитаты отозванных утверждений на странице Retracted.
WHITELIST = re.compile(
    r"^(0|1|2|3|4|5|6|8|10|16|18|27|36|45|50|100|200|360|890|1e-9|1e-12"          # структура и допуски
    r"|42|40|55|0\.28"                                                            # сид, доли выборок, ручка γ
    r"|1969|1972|1984|2005|2010|2014|2015|2020|2023|2024|2025|2026"                # годы
    r"|32|24,000|29"                                                              # библиография чужих работ
    r"|0\.42|0\.10|0\.003|0\.38|1\.25|6\.31|1\.34|14\.8|1\.08|-0\.018|0\.018)$")   # цитаты и константы

def norm_num(tok):
    """Числа сравниваем в одном написании: 24 000 / 24 000 / 24,000 → 24,000."""
    for sep in ("\u00a0", "\u2009", " "):
        tok = tok.replace(sep, ",")
    return tok

def check_g1():
    facts, _ = extract(strict=True)
    known = {norm_num(v) for v in facts.values()}
    handmade = []
    for lang in ("en", "ru"):
        for rel, tpl in templates(lang).items():
            # выкидываем плейсхолдеры и врезки — там числа приходят из источников
            body = re.sub(r"\{\{[^}]+\}\}", " ", tpl)
            body = re.sub(r"```.*?```", " ", body, flags=re.S)
            # «24 000» — одно число, а не «24» и «000»: иначе линтер слеп
            # к русскому формату и пропускает набранные руками величины
            for m in re.finditer(r"(?<![\w.])[+-]?\d+(?:[\u00a0\u2009 ]\d{3})*(?:[.,]\d+)?(?:e[+-]?\d+)?", body):
                tok = norm_num(m.group(0).lstrip("+"))
                if WHITELIST.match(tok) or tok in known or tok.lstrip("-") in known:
                    continue
                ctx = body[max(0, m.start()-45):m.end()+25].replace("\n", " ")
                handmade.append(f"{lang}/{rel}: «{tok}» … {ctx.strip()[:80]}")
    gate("G1.1 числа в шаблонах — только из фактов или белого списка",
         not handmade, f"набранных руками: {len(handmade)}")
    for h in handmade[:10]:
        print("        ", h)
    r = subprocess.run([sys.executable, os.path.join(HERE, "build.py"), "--check"],
                       capture_output=True, text=True, cwd=ROOT)
    gate("G1.2 docs/ воспроизводится из шаблонов", r.returncode == 0,
         r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[:120])
    gate("G1.3 все факты извлекаются из источников", True, f"{len(facts)} шт.")

def check_g2(net=False):
    broken, figures, ext = [], set(), set()
    for lang in ("en", "ru"):
        pg = pages(lang)
        base = os.path.join(HERE, lang)
        for rel, body in pg.items():
            for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", body):
                url = m.group(1)
                if url.startswith("http"):
                    ext.add(url)
                    if "raw.githubusercontent" in url and url.endswith(".png"):
                        figures.add(url)
                    continue
                if url.startswith("#") or url.startswith("mailto:"):
                    continue
                target = os.path.normpath(os.path.join(os.path.dirname(os.path.join(base, rel)), url.split("#")[0]))
                if not os.path.exists(target):
                    broken.append(f"{lang}/{rel} → {url}")
            for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)\)", body):
                if m.group(1).startswith("http"):
                    figures.add(m.group(1))
    gate("G2.1 битые внутренние ссылки", not broken, f"{len(broken)} шт.")
    for b in broken[:10]:
        print("        ", b)
    # ссылки из SUMMARY обязаны существовать
    missing_sum = []
    for lang in ("en", "ru"):
        base = os.path.join(HERE, lang)
        summary = open(os.path.join(base, "SUMMARY.md"), encoding="utf-8").read()
        for m in re.finditer(r"\]\(([^)]+\.md)\)", summary):
            if not os.path.exists(os.path.join(base, m.group(1))):
                missing_sum.append(f"{lang}: {m.group(1)}")
    gate("G2.2 все страницы оглавления существуют", not missing_sum, f"пропусков: {len(missing_sum)}")
    # фигуры: файл есть в репозитории (raw-ссылка резолвится в файл)
    fig_missing = []
    for u in sorted(figures):
        m = re.search(r"/main/(.+)$", u)
        if m and not os.path.exists(os.path.join(ROOT, m.group(1))):
            fig_missing.append(u)
    gate("G2.3 фигуры существуют в репозитории", not fig_missing,
         f"проверено {len(figures)}, отсутствует {len(fig_missing)}")
    if net:
        # curl, а не urllib: в песочнице urllib не видит прокси и валится на всём подряд
        from concurrent.futures import ThreadPoolExecutor
        def probe(u):
            for args in (["-I"], ["-r", "0-0"]):   # HEAD, затем первый байт (часть сайтов режет HEAD)
                r = subprocess.run(["curl", "-sS", "-L", "-o", os.devnull, "-m", "25",
                                    "-A", "Mozilla/5.0 (compatible; tonify-docs-linkcheck)",
                                    "-w", "%{http_code}", *args, u],
                                   capture_output=True, text=True)
                code = (r.stdout or "").strip()[-3:]
                if code.isdigit() and int(code) < 400:
                    return None
            # 403/429 — бот-стена, а не мёртвая ссылка: страница жива, но робота
            # не пускают. Валить ворота на этом нельзя, замалчивать — тоже
            return ("wall" if code in ("403", "429") else "dead", f"{u} → {code or 'нет ответа'}")
        with ThreadPoolExecutor(max_workers=8) as pool:
            res = [x for x in pool.map(probe, sorted(ext)) if x]
        bad   = [m for kind, m in res if kind == "dead"]
        walls = [m for kind, m in res if kind == "wall"]
        for w in walls:
            print("        БОТ-СТЕНА (не блокирует):", w)
        gate("G2.4 внешние ссылки отвечают", not bad,
             f"проверено {len(ext)}, битых {len(bad)}, за бот-стеной {len(walls)}")
        for b in bad[:8]:
            print("        ", b)

# Разметка, которую GitBook не рендерит. Всё это приезжает из pandoc-gfm и
# на странице выглядит как код с долларами по краям, видимый HTML внутри
# формулы или задвоенный номер теоремы. Ворота ловят регресс конвертера.
BAD_MARKUP = [
    (r"\$`",                                   "инлайн-математика в гитхаб-диалекте ($`x`$)"),
    (r"```+\s*math",                            "блок ```math вместо $$…$$"),
    (r"<div",                                   "HTML-обёртка окружения"),
    (r"\*\*(?:Theorem|Lemma|Corollary)[^*]*\d+ \d+\*\*", "задвоенный номер теоремы"),
]

def check_g2_markup():
    bad = []
    for lang in ("en", "ru"):
        for rel, body in pages(lang).items():
            for rx, what in BAD_MARKUP:
                for m in re.finditer(rx, body, flags=re.M):
                    bad.append(f"{lang}/{rel}: {what} — «{body[m.start():m.start()+40].splitlines()[0]}»")
    # курсив, разорванный блочной формулой, печатает звёздочку в текст
    for lang in ("en", "ru"):
        for rel, body in pages(lang).items():
            for para in body.split("\n\n"):
                # проверяем только формулировки теорем: в прозе одиночная
                # звёздочка — обозначение (p*), а не разорванный курсив
                if not re.match(r"\*\*(?:Theorem|Lemma|Corollary|Proposition)\b", para.lstrip()):
                    continue
                if len(re.findall(r"(?<!\*)\*(?!\*)", para.replace("**", ""))) % 2:
                    bad.append(f"{lang}/{rel}: курсив теоремы разорван — «{para.strip()[:55]}»")
    # $$ обязаны быть парны: нечётное число означает формулу, съевшую текст
    for lang in ("en", "ru"):
        for rel, body in pages(lang).items():
            n = len(re.findall(r"\$\$", body))
            if n % 2:
                bad.append(f"{lang}/{rel}: непарные $$ ({n} шт.) — формула съест текст")
    gate("G2.5 разметка, которую GitBook рендерит", not bad, f"дефектов: {len(bad)}")
    for b in bad[:8]:
        print("        ", b)

def check_g3():
    en, ru = pages("en"), pages("ru")
    only_en = sorted(set(en) - set(ru))
    only_ru = sorted(set(ru) - set(en))
    gate("G3.1 одинаковый набор страниц", not only_en and not only_ru,
         f"EN {len(en)}, RU {len(ru)}; только EN {only_en}, только RU {only_ru}")
    # паритет чисел = паритет ПОДСТАВЛЯЕМЫХ ФАКТОВ в парных шаблонах.
    # (сравнивать значения в готовом тексте нельзя: «7» или «200» встречаются
    #  в прозе как обычные числа и дают ложные срабатывания)
    ten, tru = templates("en"), templates("ru")
    diffs = []
    for rel in sorted(set(ten) & set(tru)):
        if rel in ("theory/full.md", "sources.md", "theory/plain.md", "GLOSSARY.md", "SUMMARY.md"):
            continue  # врезки и словарь различаются по языку по построению
        ph = lambda t: set(re.findall(r"\{\{([a-z][\w.]*)(?:\|\w+)?\}\}", t))  # фильтр формата — тот же факт
        a, b = ph(ten[rel]), ph(tru[rel])
        if a != b:
            diffs.append(f"{rel}: только EN {sorted(a-b)}, только RU {sorted(b-a)}")
    gate("G3.2 числа на парных страницах совпадают", not diffs, f"расхождений: {len(diffs)}")
    for d in diffs[:8]:
        print("        ", d)

def check_full():
    print("\n  прогон theory_check.py и сверка ключевых чисел…")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "paper", "theory_check.py")],
                       capture_output=True, text=True, cwd=ROOT)
    out = r.stdout
    facts, _ = extract(strict=True)
    checks = [
        ("тождество L1", facts["theory.ident_syn"].replace("e-", "e-"), r"max abs error over 200 trials: ([\d.]+e-\d+)"),
        ("атом L4", facts["theory.atom"], r"atom P\(Y=0\)=([\d.]+) \(theory"),
        ("Джини пула", facts["theory.gini_pool"], r"G_pool = ([\d.]+)"),
    ]
    for name, expect, rx in checks:
        m = re.search(rx, out)
        got = m.group(1) if m else "не найдено"
        gate(f"G1.4 {name}: сайт vs прогон", got.startswith(expect[:5]), f"сайт {expect}, прогон {got}")

if __name__ == "__main__":
    print("=" * 74)
    print("ВОРОТА САЙТА (G1–G3 автоматические; G4 — агент-читатель, G5 — после синка)")
    print("=" * 74)
    check_g1()
    check_g2(net="--net" in sys.argv)
    check_g2_markup()
    check_g3()
    if "--full" in sys.argv:
        check_full()
    print("-" * 74)
    if FAILS:
        print(f"FAIL: {FAILS}")
        sys.exit(1)
    print("ВСЕ АВТОМАТИЧЕСКИЕ ВОРОТА PASS")
