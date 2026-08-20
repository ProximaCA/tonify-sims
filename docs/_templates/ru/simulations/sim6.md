---
description: Direct + guaranteed discovery floor — убрать атом нуля, не превращая Tonify обратно в обычный streaming pool.
---

# sim6 — Direct + guaranteed discovery floor

**Вопрос.** L4 говорит: проблема малых артистов — атом нуля, не среднее и не $k$. Сколько стоит убрать эту лотерею, не превращая продукт обратно в обычный streaming pool?

**Ворота.** Якоря мира T1–T3; $q_{\mathrm{eligible}}=0$ при $B>0$; пол суммируется в $B$; direct-терм не тронут; при $\beta<1$ верхняя доля пола легче, чем у $D$; MVA при $B=0$ совпадает с чистым direct.

**Заголовок.** Атом стоит eligibility. Жизнь стоит $B$. Любой $B>0$ даёт $q_{\mathrm{eligible}}=0$. Среди артистов с $A_i>0$ чистый direct — {{s6.q_dir}}% нулей; $A_{\min}=1$ убивает атом, $A_{\min}\le{{s6.amin50}}$ оставляет не больше половины. При 5% независимого пула, $A_{\min}=10$, средний пол ${{s6.mean_floor}}/год, MVA гибрида {{s6.mva_hyb05}} против чистого direct {{s6.mva_dir}}.

**Запуск.** `python3 sim6/floor.py`.

***

{{INCLUDE:README.ru.md|## sim6 — Direct + guaranteed discovery floor|## Воспроизводимость}}
