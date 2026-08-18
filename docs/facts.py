#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FACTS — единственный мост между репозиторием и сайтом.

Принцип: ни одно число на сайте не набирается руками. Каждый факт объявлен
здесь как (файл-источник, регулярка); build.py подставляет их в шаблоны.
Если источник изменился и регулярка перестала находить значение — сборка
падает, страница не публикуется. Это и есть ворота G1 по построению.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ключ: (относительный путь, регулярка с одной группой)
FACTS_SPEC = {
    # --- sim4: мир и ворота (источник: sim4/README.md) ---
    "sim4.N":            ("sim4/README.md", r"seed 42; N=([\d\s]+?), U="),
    "sim4.U":            ("sim4/README.md", r"U=([\d\s]+?), пар"),
    "sim4.pairs":        ("sim4/README.md", r"пар ([\d\s]+?), стримов"),
    "sim4.streams":      ("sim4/README.md", r"стримов ([\d.]+M)\)"),
    "sim4.g1":           ("sim4/README.md", r"max\\\|UC/PR − 1\\\| \| ([\d.e+-]+) \|"),
    # sim4-D: нижний край (downside.py → sim4/README.md)
    "dw.zero_dir":       ("sim4/README.md", r"нулей среди артистов с аудиторией \| 0\.0% \| 0\.0% \| \*\*([\d.]+)%"),
    "dw.med_pool":       ("sim4/README.md", r"медиана среди получающих \(× средний\) \| ([\d.]+) \|"),
    "dw.med_dir":        ("sim4/README.md", r"медиана среди получающих \(× средний\) \| [\d.]+ \| [\d.]+ \| \*\*([\d.]+)\*\*"),
    "dw.es_pool":        ("sim4/README.md", r"expected shortfall, худшие 50% \| ([\d.]+) \|"),
    "dw.thr_pool":       ("sim4/README.md", r"доля выше порога θ = 0\.1 среднего \| ([\d.]+)% \|"),
    "dw.thr_dir":        ("sim4/README.md", r"доля выше порога θ = 0\.1 среднего \| [\d.]+% \| [\d.]+% \| \*\*([\d.]+)%"),
    "dw.gini_g0":        ("sim4/README.md", r"γ = 0 \(независимость\) \| [\d.]+ \| [\d.]+ \| −([\d.]+)"),
    "dw.gini_g12":       ("sim4/README.md", r"γ = \+0\.12 \(измеренный центр\) \| [\d.]+ \| [\d.]+ \| −([\d.]+)"),
    "dw.gini_pool12":    ("sim4/README.md", r"γ = \+0\.12 \(измеренный центр\) \| ([\d.]+) \|"),
    "dw.gini_dir12":     ("sim4/README.md", r"γ = \+0\.12 \(измеренный центр\) \| [\d.]+ \| ([\d.]+) \|"),
    "sim4.thr_lo":       ("sim4/SPEC.md", r"T1: доля артистов s̃<(\d+)"),
    "sim4.thr_hi":       ("sim4/SPEC.md", r"T2: доля s̃>([\d\s]+?) \|"),
    "sim4.t1_lo":        ("sim4/SPEC.md", r"T1: доля артистов s̃<\d+ \| \[(\d+)%"),
    "sim4.t1_hi":        ("sim4/SPEC.md", r"T1: доля артистов s̃<\d+ \| \[\d+%; (\d+)%\]"),
    "sim4.t2_lo":        ("sim4/SPEC.md", r"T2: доля s̃>[\d\s]+ \| \[([\d.]+)%"),
    "sim4.t2_hi":        ("sim4/SPEC.md", r"T2: доля s̃>[\d\s]+ \| \[[\d.]+%; ([\d.]+)%\]"),
    "sim4.t1":           ("sim4/README.md", r"доля артистов s̃<1000 \| ([\d.]+)%"),
    "sim4.t2":           ("sim4/README.md", r"доля s̃>225 734 \| ([\d.]+)%"),
    "sim4.t3":           ("sim4/README.md", r"доля стримов топ-0\.28% \| ([\d.]+)%"),
    "sim4.ident":        ("sim4/README.md", r"max\\\|UC/PR − P̄/H\\\| \| ([\d.e+-]+) \|"),
    "sim4.zerosum":      ("sim4/README.md", r"\\\|ΣUC−ΣPR\\\|/ΣPR \| ([\d.e+-]+) \|"),
    # --- sim4: кроссовер на измеренных γ ---
    "cross.g0.all":      ("sim4/README.md", r"контроль независимости: \*\*([\d.]+)% \("),
    "cross.g0.top":      ("sim4/README.md", r"контроль независимости: \*\*[\d.]+% \(([\d.]+)%\)"),
    "cross.g12.all":     ("sim4/README.md", r"измеренный центр emp1: \*\*([\d.]+)% \("),
    "cross.g12.top":     ("sim4/README.md", r"измеренный центр emp1: \*\*[\d.]+% \(([\d.]+)%\)"),
    "cross.g28.all":     ("sim4/README.md", r"голова emp1: \*\*([\d.]+)% \("),
    "cross.g28.top":     ("sim4/README.md", r"голова emp1: \*\*[\d.]+% \(([\d.]+)%\)"),
    # --- sim4-G: группы слушателей ---
    "grp.coef":          ("sim4/README.md", r"d log\(UC/PR\)/d\(доля beyond в аудитории\) = \*\*\+([\d.]+) ±"),
    "grp.se":            ("sim4/README.md", r"доля beyond в аудитории\) = \*\*\+[\d.]+ ± ([\d.]+)\*\*"),
    "grp.peak":          ("sim4/README.md", r"\*\*50% \(как BeyMS\)\*\* \| \*\*([\d.]+)%\*\*"),
    "grp.all_main":      ("sim4/README.md", r"0% \(все mainstream\) \| ([\d.]+)%"),
    "grp.all_beyond":    ("sim4/README.md", r"100% \(все beyond\) \| ([\d.]+)%"),
    # --- атомы нуля (fig15) ---
    "atom.direct":       ("sim4/README.md", r"direct — ([\d]+)% артистов с нулём"),
    "atom.pool":         ("sim4/README.md", r"пуловые — ([\d]+)% \(пустая аудитория"),
    # --- emp1: измерение ---
    "emp1.panel":        ("emp1/README.md", r"бленд 50/50 \| \+([\d.]+) ± [\d.]+ \|"),
    "emp1.panel_se":     ("emp1/README.md", r"бленд 50/50 \| \+[\d.]+ ± ([\d.]+) \|"),
    "emp1.main":         ("emp1/README.md", r"группа mainstream \| \+([\d.]+) ±"),
    "emp1.beyond":       ("emp1/README.md", r"группа beyond-mainstream \| \+([\d.]+) ±"),
    "emp1.year":         ("emp1/README.md", r"окно: календарный 2012 \| \+([\d.]+) ±"),
    "emp1.month":        ("emp1/README.md", r"окно: один месяц \(2013-03\) \| \+([\d.]+) ±"),
    "emp1.head":         ("emp1/README.md", r"при A≥50 / A≥200 \| \+[\d.]+ ± [\d.]+ / \+([\d.]+) ±"),
    "emp1.k360":         ("emp1/README.md", r"360K \(top-50 на юзера\) \| \+([\d.]+) ±"),
    "emp1.trunc":        ("emp1/README.md", r"усечённый до top-50 \(фальсификатор G3\) \| \+([\d.]+) ±"),
    "emp1.retention":    ("emp1/README.md", r"b\[длительность пары\] \+([\d.]+) \+"),
    "emp1.rate":         ("emp1/README.md", r"b\[плэи/день\] \*\*−([\d.]+)\*\*"),
    "emp1.gamma_model":  ("emp1/README.md", r"соответствует \*\*модельное γ ≈ \+([\d.]+)\*\*"),
    "emp1.atten":        ("emp1/README.md", r"ceil-дискретизация съедает ~(\d+)% наклона"),
    "emp1.atten_factor": ("emp1/README.md", r"фактор инверсии ([\d.]+) ⟹"),
    "emp1.artists":      ("emp1/README.md", r"\| \+0\.101 ± 0\.004 \|"),  # маркер таблицы
    # --- emp1: сверка с Moreau (реальные логи) ---
    "moreau.ident":      ("emp1/PRIOR_ART.md", r"max\|UC/PR − P̄/H\| = ([\d.]+e-\d+) на"),
    "moreau.artists":    ("emp1/PRIOR_ART.md", r"e-15 на ([\d\s]+?) артистах Last\.fm"),
    "moreau.elast":      ("emp1/PRIOR_ART.md", r"ucps × log\(intensity\) = −([\d.]+)\*\*\*"),
    "moreau.N":          ("emp1/PRIOR_ART.md", r"\(N = ([\d\s]+), song FE"),
    "moreau.am":         ("emp1/PRIOR_ART.md", r"у нас \+([\d.]+) \(AM\)"),
    "moreau.hm":         ("emp1/PRIOR_ART.md", r"\(AM\) и \+([\d.]+)\s*\n?\(HM\)"),
    # --- коридор наклонов (Фаза 0) ---
    "corr.sharp":        ("emp1/PRIOR_ART.md", r"Sharp 2010, стиральные порошки \(n=5\) \| CPG \| \*\*\+([\d.]+)\*\*"),
    "corr.habel":        ("emp1/PRIOR_ART.md", r"Habel & Rungie 2005, Dirichlet-линия \| теория \| \*\*\+([\d.]+)\*\*"),
    "corr.stocchi":      ("emp1/PRIOR_ART.md", r"Stocchi et al\. 2025.*?\*\*\+([\d.]+)\*\* Dirichlet-теор"),
    "corr.sulik":        ("emp1/PRIOR_ART.md", r"Šulik 2026, фильмы.*?\| \*\*\+([\d.]+)\*\*"),
    "corr.taneja_lo":    ("emp1/PRIOR_ART.md", r"Taneja 2020 / Baumann 2015.*?\+([\d.]+) \(страницы\)"),
    "corr.taneja_hi":    ("emp1/PRIOR_ART.md", r"\(страницы\), \+([\d.]+) \(минуты\)"),
    # --- Фаза 0: счёт источников ---
    "phase0.total":      ("emp1/PRIOR_ART.md", r"\*\*Итог: закрыты все (\d+)\nисточников\*\*"),
    "phase0.primary":    ("emp1/PRIOR_ART.md", r"источников\*\* — (\d+) первично"),
    # --- теория: машинные проверки ---
    "theory.ident_syn":  ("paper/THEORY.md", r"max \|UC/PR − E_w\[P̄/P_u\]\| = ([\d.]+e-\d+) \(машинный ноль\)"),
    "theory.matrices":   ("paper/THEORY.md", r"([\d]+) случайных матриц \(N ≤ 30"),
    "theory.atom":       ("paper/THEORY.md", r"атом\s+P\(Y=0\) = ([\d.]+) \(теория"),
    "theory.gini_pool":  ("paper/THEORY.md", r"\*\*G_pool = ([\d.]+) против"),
    "theory.gini_dir":   ("paper/THEORY.md", r"против G_direct = ([\d.]+)\*\*"),
    "theory.q":          ("paper/THEORY.md", r"q = E\[\(1−σ\)\^A\] = ([\d.]+) \(измеренная"),
    # --- sim1: контракт против правила ---
    "sim1.contract":     ("README.md", r"The contract moves viability ×([\d.]+)"),
    "sim1.rule":         ("README.md", r"only the rule axis \(×([\d.]+) at the baseline"),
}

def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()

def extract(strict=True):
    """Вытаскивает все факты. При strict=True падает на первом ненайденном."""
    cache, out, missing = {}, {}, []
    for key, (path, rx) in FACTS_SPEC.items():
        if path not in cache:
            cache[path] = load(path)
        m = re.search(rx, cache[path])
        if m is None:
            missing.append((key, path, rx))
            continue
        val = m.group(1) if m.groups() else m.group(0)
        out[key] = re.sub(r"\s+", " ", val).strip().replace(" ", " ") if " " in val else val
    if missing and strict:
        print("FACTS: не найдены источники для ключей:", file=sys.stderr)
        for k, p, rx in missing:
            print(f"  {k}  ({p})  /{rx}/", file=sys.stderr)
        sys.exit(1)
    return out, missing

if __name__ == "__main__":
    facts, missing = extract(strict=False)
    print(f"извлечено {len(facts)} из {len(FACTS_SPEC)}")
    for k in sorted(facts):
        print(f"  {k:22s} = {facts[k]}")
    if missing:
        print(f"\nНЕ НАЙДЕНО ({len(missing)}):")
        for k, p, rx in missing:
            print(f"  {k:22s} ({p})")
        sys.exit(1)
