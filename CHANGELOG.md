# Changelog

## unreleased — structural pass over THEORY (2026-08-14)

- **paper/THEORY.md v0.5, paper/THEORY.tex v0.5** — structural pass,
  math untouched: канон работы по математическому моделированию —
  §1 содержательная постановка (без формул) → §2 концептуальная (сущности
  до символов; статусы величин; развилка «теоремы на произвольной p vs
  генератор sim4»; Фаза 0) → §3 математическая (исчерпывающая таблица
  обозначений с типами/единицами/статусами и словарём нотации Alaei;
  операторы с доменами и краевыми случаями; допущения A1–A8 + (C) единым
  списком; леммы со строками «Использует допущения») → §4 численная
  реализация (генеративная модель, верификация, воспроизводимость от
  git clone) → §5 red team → §6 открытое → §7 мост. RU/EN структурно
  идентичны, канон — EN PDF. Ворота: Q1 (символ-аудит .tex скриптом — 0
  непокрытых), Q2 (сверка утверждений против v0.4), Q3 (холодный
  математик по §1–§3), Q4 (свежий клон воспроизводит все числа), Q5
  (компиляция + структурная идентичность).

## editorial pass over THEORY (2026-08-14, commit 52ab2e8)

- **paper/THEORY.md v0.4, paper/THEORY.tex v0.4** — editorial pass,
  математика не тронута: ни одна формула, константа, вердикт или оговорка
  не изменены. Новое вступление (четыре вопроса + маршрут чтения без
  математики), таблица обозначений, каждая лемма по шаблону «Зачем это /
  Формулировка и доказательство / Что это значит / Что может это сломать»,
  red team §7 переписан из леджера в рассказ, §10 с вводными
  предложениями, линейность изложения (ссылки только назад), .tex —
  двухслойная вёрстка (маршрут курсивом, доказательства мелким кеглем).
  Ворота: Q1 (grep форвард-ссылок), Q2 (сверка утверждение-в-утверждение
  против v0.3), Q3 (тест холодного читателя), Q4 (компиляция).

## v1.2-theory — 2026-08-14

- **paper/THEORY.md** — formal core (RU, source of truth): L1 ratio identity
  UC/PR = P̄/H with AM–HM decomposition and corollaries (a)–(d); L2
  pass-through invariance split 2a/2b + breaking channels B1–B5; L3 tail
  preservation + atom at zero, Gini G = q + (1−q)G⁺; L4 full FOSD/SSD
  blockade with breakeven d* = PL·rate/(σ·ḡ·τ). Prior art verified first
  (Alaei, Makhdoumi, Malekian & Pekeč, Mgmt. Sci. 2022 — crossover
  condition; our identity/decomposition/tail results are complementary).
- **paper/THEORY.tex / .pdf** — 3-page English distillate, canon numbering.
- **paper/theory_check.py** — machine verification of every proved claim
  (identity to 9e-16, counterexamples, atom vs Monte Carlo).
- **sim4/** — synthetic bipartite user×artist play matrix (N=20 000,
  U≈1.1M, 21.8M pairs, seed 42): one graph, three intensity regimes
  (ergodic control, heterogeneous, γ-coupled); gates G1–G3 printed before
  any conclusion (G1 exact zero); exports in data/ with loader example.
- **figures/fig15–16** — three mechanisms on one substrate; L1 identity
  on the matrix with the γ-family.
- Two red-team passes over THEORY — ledger in THEORY.md §7. Pass 1:
  retracted inequality, retracted Hoeffding bound, lemma split,
  load-bearing assumption A1. Pass 2 (25 confirmed findings, 5 attackers +
  independent verification of every accusation): exact MVA criterion
  F⁻¹(V/ρ)=F⁻¹(V)/ρ replacing a false necessity claim, artist-level
  assumption + channel B6 in 2a, retracted sim4 head-saturation narrative
  (circular top-56 sampling; real head Ã/ℓ = 1.08). sim4 red team R1–R7
  in sim4/README.md.

## v1.1-public — 2026-08

- sim1 v1.1: closed the external review — SPEC.md, gates, UC crossover u*,
  honest multipliers; bilingual figure sets (EN canon + figures/ru).

## v1.0-public — 2026-07

- Initial public release: sim1 (cash model v0.2→v0.5), sim2 (Telegram
  graph, complex contagion), sim3 (anti-graveyard treasury), fig1–fig13,
  paper/ (PAPER, RESULTS, CRITIC), run_all.py, MIT.
