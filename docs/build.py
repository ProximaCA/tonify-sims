#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BUILD — собирает docs/en и docs/ru из шаблонов и фактов репозитория.

Правило: страницы сайта — генерируемый артефакт, а не рукопись. Числа
приходят из facts.py (извлечение из источников), крупные блоки — через
{{INCLUDE:path}} (дословная врезка файла репозитория). Руками в docs/en
и docs/ru не правят: следующая сборка затрёт.

Запуск:  python3 docs/build.py         — собрать
         python3 docs/build.py --check — проверить, что собранное совпадает
                                          с закоммиченным (ворота CI)
"""
import os, re, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from facts import extract, ROOT as FROOT

RAW = "https://raw.githubusercontent.com/ProximaCA/tonify-sims/main"
REPO = "https://github.com/ProximaCA/tonify-sims"

def include(path, strip_h1=True, cut=None):
    """Дословная врезка файла репозитория."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        txt = f.read()
    if cut:
        start, end = cut
        i = txt.find(start)
        j = txt.find(end, i + 1) if end else len(txt)
        if i >= 0:
            txt = txt[i:j if j > 0 else len(txt)]
    if strip_h1:
        txt = re.sub(r"\A#\s+[^\n]*\n+", "", txt)
    # заголовки сдвигаем на уровень вниз, чтобы вписались в страницу
    txt = re.sub(r"^(#{1,5}) ", r"#\1 ", txt, flags=re.M)
    # относительные ссылки на картинки → raw (GitBook грузит из репозитория)
    txt = re.sub(r"!\[([^\]]*)\]\((?!http)([^)]+\.(?:png|gif|jpg|svg))\)",
                 lambda m: f"![{m.group(1)}]({RAW}/{norm(path, m.group(2))})", txt)
    # прочие относительные ссылки на репо → абсолютные
    txt = re.sub(r"\]\((?!http|#)([^)]+\.(?:md|py|png|gif|jpg|svg|pdf|tex|csv|npz|yaml|cff))\)",
                 lambda m: f"]({REPO}/blob/main/{norm(path, m.group(1))})", txt)
    return txt.strip()

def norm(base, rel):
    d = os.path.dirname(base)
    return os.path.normpath(os.path.join(d, rel)).replace("\\", "/")

def pandoc_tex(path):
    """LaTeX → GitHub-flavored markdown (канон EN живёт в .tex)."""
    import subprocess
    r = subprocess.run(["pandoc", "-f", "latex", "-t", "gfm",
                        os.path.join(ROOT, path)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"BUILD: pandoc не смог сконвертировать {path}: {r.stderr[:300]}")
    txt = r.stdout
    txt = re.sub(r"\A#\s+[^\n]*\n+", "", txt)          # снять первый H1
    txt = re.sub(r"^(#{1,5}) ", r"#\1 ", txt, flags=re.M)  # сдвинуть уровни
    return gitbook_math(txt).strip()

def gitbook_math(txt):
    """Диалект pandoc-gfm → диалект GitBook.

    Pandoc пишет математику по-гитхабовски ($`x`$ и блок ```math), а окружения
    теорем оборачивает в <div>. GitBook не понимает ни того, ни другого: формула
    показывается как код с долларами по краям, а div склеивается с соседней
    формулой и утекает в неё видимым HTML. Всё это переводится в $$…$$.
    """
    # блочная формула: ```math … ``` → $$ … $$ (вместе с курсивом, который
    # pandoc иногда навешивает на весь блок теоремы — он ломает разметку)
    def block(m):
        return "\n$$\n" + m.group(1).strip() + "\n$$\n"
    txt = re.sub(r"```+\s*math\n(.*?)\n```+\*?", block, txt, flags=re.S)
    # инлайн-формула: $`x`$ → $$x$$, в одну строку — перенос внутри инлайновой
    # формулы GitBook не рендерит (pandoc переносит по ширине 72)
    txt = re.sub(r"\$`(.+?)`\$",
                 lambda m: "$$" + re.sub(r"\s+", " ", m.group(1)).strip() + "$$",
                 txt, flags=re.S)
    # обёртки окружений: смысл несёт сам текст («**Theorem 1**», «*Proof.*»)
    txt = re.sub(r"^</?div[^>]*>\s*$", "", txt, flags=re.M)
    # \newtheorem* не нумерует — номер уже внутри названия, а pandoc всё равно
    # приписывает счётчик: «Theorem 1 1», «Corollary (a) 1»
    txt = re.sub(r"\*\*((?:Theorem|Lemma|Proposition) \d+|Corollary \([a-z]\)|Remark) \d+\*\*",
                 r"**\1**", txt)
    return re.sub(r"\n{3,}", "\n\n", txt)

def plain_route(path):
    r"""Нетехнический маршрут: блоки \why{} и \whatitsays{} с их разделами."""
    import subprocess
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        tex = f.read()
    out, section = [], None
    for m in re.finditer(r"\\section\{([^}]*)\}|\\paragraph\{([^}]*)\}|\\(why|whatitsays)\{", tex):
        if m.group(1):
            section = m.group(1)
            continue
        if m.group(2):
            par = m.group(2).rstrip(".")
            if re.match(r"^(L\d|Theorem|Lemma)", par):
                section = par
            continue
        kind = m.group(3)
        # вытащить сбалансированный аргумент команды
        i = m.end(); depth = 1; buf = []
        while i < len(tex) and depth:
            c = tex[i]
            if c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: break
            buf.append(c); i += 1
        body = "".join(buf)
        r = subprocess.run(["pandoc", "-f", "latex", "-t", "gfm"],
                           input=body, capture_output=True, text=True)
        body_md = gitbook_math(r.stdout if r.returncode == 0 else body).strip()
        label = "Why this matters" if kind == "why" else "What it says"
        out.append((section, label, body_md))
    blocks, cur = [], None
    for section, label, body in out:
        if section != cur:
            blocks.append(f"\n## {section}\n")
            cur = section
        blocks.append(f"**{label}.** {body}\n")
    return "\n".join(blocks).strip()

def plain_route_ru(path):
    """Русский нетехнический маршрут: блоки «Зачем это» и «Что это значит»."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        md = f.read()
    # леммы размечены как #### 3.4.N L*: заголовок
    parts = re.split(r"^#### 3\.4\.\d+ (L\d[^\n]*)$", md, flags=re.M)
    out = []
    for i in range(1, len(parts), 2):
        title = parts[i].split("—")[0].strip()
        body = parts[i + 1]
        blocks = []
        for label in ("Зачем это", "Что это значит"):
            m = re.search(r"\*\*" + label + r"\.\*\*(.+?)(?=\n\n\*\*|\n\n####|\Z)", body, flags=re.S)
            if m:
                txt = re.sub(r"\s+", " ", m.group(1)).strip()
                blocks.append(f"**{label}.** {txt}")
        if blocks:
            out.append(f"\n## {title}\n\n" + "\n\n".join(blocks))
    return "\n".join(out).strip()

def drop_columns(md, names):
    """Убрать колонки GFM-таблицы по заголовку.

    На сайте колонка со ссылками на заметки волта бесполезна — самого волта в
    публичном репозитории нет, — а её значения (id по 190 символов моноширинным
    кодом, без пробелов) физически распирают таблицу: остальные колонки
    сплющиваются до одного слова в строке.
    """
    out, drop = [], None
    for line in md.split("\n"):
        if not line.lstrip().startswith("|"):
            out.append(line)
            if line.strip() == "":
                drop = None            # таблица кончилась
            continue
        cells = line.split("|")
        if drop is None:
            drop = {i for i, c in enumerate(cells) if c.strip() in names}
            if not drop:
                out.append(line)
                continue
        out.append("|".join(c for i, c in enumerate(cells) if i not in drop))
    return "\n".join(out)

def render(text, facts):
    """{{key}} → факт; {{INCLUDE:path}} и {{INCLUDE:path|start|end}} → врезка."""
    def inc(m):
        spec = m.group(1)
        parts = spec.split("|")
        cut = (parts[1], parts[2] if len(parts) > 2 else None) if len(parts) > 1 else None
        return include(parts[0], cut=cut)
    text = re.sub(r"\{\{SOURCETABLE:([^}]+)\}\}",
                  lambda m: drop_columns(include(m.group(1)),
                                         {"Vault note", "Заметка vault"}), text)
    text = re.sub(r"\{\{INCLUDE:([^}]+)\}\}", inc, text)
    text = re.sub(r"\{\{PANDOC:([^}]+)\}\}", lambda m: pandoc_tex(m.group(1)), text)
    text = re.sub(r"\{\{PLAINROUTE:([^}]+)\}\}", lambda m: plain_route(m.group(1)), text)
    text = re.sub(r"\{\{PLAINROUTE_RU:([^}]+)\}\}", lambda m: plain_route_ru(m.group(1)), text)
    def fact(m):
        k, filt = m.group(1), m.group(2)
        if k not in facts:
            raise SystemExit(f"BUILD: неизвестный факт {{{{{k}}}}} — добавь в facts.py")
        v = facts[k]
        # один факт, два языковых написания: {{key}} — как в источнике,
        # {{key|comma}} — с запятой в разряде тысяч для английских страниц
        return v.replace("\u2009", ",").replace(" ", ",") if filt == "comma" else v
    text = re.sub(r"\{\{([a-z][\w.]*)(?:\|(\w+))?\}\}", fact, text)
    text = text.replace("{{RAW}}", RAW).replace("{{REPO}}", REPO)
    return text

def build(check=False):
    facts, _ = extract(strict=True)
    changed = []
    for lang in ("en", "ru"):
        src = os.path.join(HERE, "_templates", lang)
        dst = os.path.join(HERE, lang)
        if not os.path.isdir(src):
            sys.exit(f"BUILD: нет шаблонов {src}")
        if not check:
            # чистим только .md, конфиги (.gitbook.yaml) не трогаем
            for root, _, files in os.walk(dst):
                for f in files:
                    if f.endswith(".md"):
                        os.remove(os.path.join(root, f))
        for root, _, files in os.walk(src):
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                rel = os.path.relpath(os.path.join(root, f), src)
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    out = render(fh.read(), facts)
                target = os.path.join(dst, rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if check:
                    if not os.path.exists(target):
                        changed.append(rel + " (нет в docs/)")
                    elif open(target, encoding="utf-8").read() != out:
                        changed.append(rel)
                else:
                    with open(target, "w", encoding="utf-8") as fh:
                        fh.write(out)
    if check:
        if changed:
            print("BUILD --check: страницы разошлись с шаблонами:")
            for c in changed:
                print("  ", c)
            sys.exit(1)
        print(f"BUILD --check: docs/ актуальны ({len(facts)} фактов из источников)")
    else:
        n = sum(len(fs) for _, _, fs in os.walk(os.path.join(HERE, "en")))
        print(f"BUILD: собрано EN+RU, {len(facts)} фактов подставлено из источников")

if __name__ == "__main__":
    build(check="--check" in sys.argv)
