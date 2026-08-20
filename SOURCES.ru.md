*[🇬🇧 English](SOURCES.md) | 🇷🇺 Русский*

# SOURCES — каждый параметр, его значение, его происхождение

Одна строка на параметр модели: значение, которое реально используют
симуляции, источник, подтверждённый в ресерч-vault (tonify-research, 1 152
заметки), id заметки vault и место, где параметр входит в код/фигуры. Строки,
где vault **не** подтверждает атрибуцию из документов репо, говорят об этом
прямо — см. *Расхождения* под таблицей. Ничто в этом файле не процитировано
по памяти; каждая ссылка прочитана из заметки vault. Где источника в vault
нет — в строке стоит «допущение» или «нет в vault», а не выдуманная ссылка.

| # | Параметр | Значение в модели | Источник (проверен по vault) | Заметка vault | Где используется |
|---|----------|-------------------|------------------------------|---------------|------------------|
| 1 | Доля ниже 1000 стримов/год (мишень T1) | 87% | Ближайшее подтверждённое: Luminate year-end 2023 — 86,2% **треков** (не артистов) ≤1000 плэев, via MBW 14.03.2024 ([ссылка](https://www.musicbusinessworldwide.com/deezer-has-deleted-26m-useless-tracks-since-it-launched-artist-centric-model-with-universal-music-group/)); артистный аналог: Chartmetric 2025 — 86% артистов Spotify <10 слушателей/мес, via Kullick & Petry 2025 ([PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/61644B64A790CB6B4B15A36C3D6DF83C/S2059599925100150a.pdf)). См. расхождение D1. | `deezer-has-deleted-26m-fake-artist-and-noise-tracks-since-it-launched-its-artist`, `a-r-t-i-c-l-e` | конструкция мира sim1, валидация T1; fig2 |
| 2 | Правообладатели >$1000/год | 2,6% (259 700 из 10M+ загрузивших, 2023) | Spotify Loud & Clear (данные 2023), via Music Ally, 14.01.2025 ([ссылка](https://musically.com/2025/01/14/chartmetric-tracks-11m-spotify-artists-fewer-than-1-6m-have-over-10-listeners/)) | `chartmetric-tracks-11m-spotify-artists-fewer-than-16m-have-over-10-listeners-mus` | валидация T2; оговорка CRITIC §5 (правообладатели, не артисты) |
| 3 | Верхняя доля стримов (мишень T3) | топ-0,28% ≈ 50%; Gini 0,72 | Òscar Celma, PhD-диссертация *Music Recommendation and Discovery*, UPF Barcelona (кроул Last.fm, июль 2007: топ-737 из 260 525 артистов = 50% плэев) ([PDF](http://www.mtg.upf.edu/static/media/PhD_ocelma.pdf)). **Не число CMA** — собственное CMA: топ-0,4% → 63–65% стримов 2014–2020 ([финальный отчёт](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1120610/Music_and_streaming_final_report.pdf)). См. D2. | `music-recommendation-and-discovery`, `music-and-streaming`, `interim-report-c2-lfm-dataset-calibration-parameter` | валидация T3 (Gini мира валидируется на 0,97 по стримам) |
| 4 | Плэи слушателя у артиста | медиана 5,16, среднее 21,21 | Schedl & Hauger, *Int. J. Multimedia Information Retrieval* 6:71–84, 2017, Table 6 (LFM-1b: 120 322 юзера, 1,09 млрд событий) ([PDF](https://link.springer.com/content/pdf/10.1007%2Fs13735-017-0118-y.pdf)); интро датасета: Schedl, ICMR 2016 ([PDF](https://www.cp.jku.at/people/schedl/Research/Publications/pdf/schedl_icmr_2016.pdf)). Меряет жизнь панели, не год → красная команда расширила до 8–21 (CRITIC §2). | `int-j-multimed-info-retr-2017-67184`, `the-lfm-1b-dataset-for` | все числа MVA (PL=21,21 во всех трёх скриптах sim1); fig1/5/7 |
| 5 | Выплата pro-rata independent | $4,43 за 1000 стримов (US, янв 2026) | В PAPER §3 процитировано как Duetti; **нет в vault** — заметки Duetti не существует, публичная ссылка здесь не верифицирована. См. D3. | — | якорь независимого котла; fig1/5/7, breakeven |
| 6 | Карман подписанного за стрим | $0,0003/стрим | **Нет в vault** как прямая цифра. Ближайшие независимые точки vault: waterfall E&Y/SNEP 2015 via Techdirt ([ссылка](https://www.techdirt.com/2015/02/05/yes-major-record-labels-are-keeping-nearly-all-money-they-get-spotify-rather-than-giving-it-to-artists/)); AEPO-ARTIS ≈£0,00065/стрим (данные Sony в CMA); CMA ≈£0,001/стрим. См. D3. | `yes-major-record-labels-are-keeping-nearly-all-the-money-they-get-from-spotify-r`, `interim-report-per-fan-yield-for-the-mid-tail` | якорь подписанного кармана; 188 590; fig1/5/7 |
| 7 | Лейбловый проход | 6,772% — **производная** 0,0003/0,00443, не вход (PAPER CHANGELOG v0.5.1) | Независимая от vault корроборация порядка: проход 8–20% (Rose, *Streaming in the Dark*, Berkeley J. Ent. & Sports Law 13:1, май 2024, [PDF](https://publicknowledge.org/wp-content/uploads/2024/05/Streaming-in-the-Dark_Competitive-Dysfunction-Within-the-Music-Streaming-Ecosystem_Berkeley-Journal-of-Entertainment-Sports-Law_May-2024.pdf)); ~10,6% доходит до записывающих артистов (CMU via AEPO-ARTIS). «~6,8% (CNM)» из комментариев кода — **нет в vault**. См. D4. | `streaming-in-the-dark`, `spotifys-loud-but-not-so-clear-aepo-artis` | signed-колонка матрицы v05; контракт-мультипликатор ×14,8; fig7 |
| 8 | Доля суперфанов в аудитории | 0,6–1,7% (диапазон чувствительности; база 1,7%) | SoundCloud × MIDiA, *Building a fan economy with Fan-Powered Royalties*, июль 2022 (118 000 артистов: в среднем 1,5% взаимодействий → 29% дохода; «typically 1–2%»; FPR-winners 1,9% → 42%) ([PDF](https://vi.be/files/2022-08/soundcloud-x-midia-building-a-fan-economy-with-fan-powered-royalties.pdf)). Нижняя граница 0,6% — из правила участия 97-2-1 (CRITIC §7), не из white paper. См. D5. | `1-building-a-fan-economy-with-fan-powered-royalties` | диапазон breakeven (18 комбинаций); fig1, fig6 |
| 9 | Доля выручки суперфанов (вход отзыва) | 29% дохода артиста | Тот же white paper SoundCloud × MIDiA — доля *роялти* при FPR, не донатов; эта категориальная ошибка — причина отзыва «0,42 доната/год» (CRITIC §1) | `1-building-a-fan-economy-with-fan-powered-royalties` | отозванная инверсия P6; Retracted & bounded |
| 10 | Донатный чек | $3,1–6,9 (диапазон; база lognormal $5) | Якорь диапазона: Waskow, Markett, Montag et al., *Pay What You Want!*, Frontiers in Psychology 7:1023, 2016 — скорректированное среднее PWYW €3,10, отказ 24,4% vs 17,3% (128/525 vs 91/525), N=25, реальные Bandcamp-альбомы ([ссылка](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4933710/)). *Форма* lognormal($5, σ=0,8) — **допущение, не измерение** (RESULTS, честные ограничения). | `pay-what-you-want-a-pilot-study-on-neural-correlates-of-voluntary-payments-for-m`, `interim-report-pwyw-conditions-and-power-law-reproduction` | чек прямой экономики; fig1/5/6/7, breakeven |
| 11 | Цена подписки × доля пула | $11,99/мес × 70% в пул прав | 70%: «around 70%» по Bergantiños & Moreno-Ternero 2023 (со ссылкой на Meyn et al. 2023) ([PDF](https://arxiv.org/pdf/2310.11861)). $11,99 (US-цена) **нет в vault** (в vault — UK £-тарифы из отчёта CMA). См. D6. | `arxiv231011861v1-econth-18-oct-2023` | кошелёк user-centric; fig1/5/7 |
| 12 | Twitch: кеф платящего фана, цена, сплит | кеф 12+ структурно; $5/мес; сплит 50/50 | $5 месячная подписка: Sjöblom & Hamari, *Computers in Human Behavior* 2017 ([PDF](https://www.utupub.fi/bitstream/handle/10024/171134/Why%20do%20people%20watch%20others%20play%20video%20games.pdf?sequence=1)); сплит 50/50: только как *заголовок* ссылки 44 (письмо Clancy 2022) в списке литературы vault — процентов в телах заметок нет. См. D7. | `full-length-article`, `vol0123456789-2` | строка Twitch-механики (MVA 2 353); fig5/7; RESULTS §2 |
| 13 | Неравенство доходов Twitch | α=−2,13, Gini 0,57 (топ-10k), ≈0,93 на платформу | Houssard, Pilati, Tartari, Sacco & Gallotti, *Monetization in online streaming platforms*, Scientific Reports 13:1103 (2023) ([PDF](https://www.nature.com/articles/s41598-022-26727-5.pdf)) | `vol0123456789-2` | контекст бенчмарка RESULTS §2 |
| 14 | Модель мотиваций Twitch | объясняет 3,7% дисперсии подписок; N=1097 | Sjöblom & Hamari 2017 (та же статья, что №12) | `full-length-article` | RESULTS §2 (почему циферблат — частота, не мотивация) |
| 15 | Множитель гифтинга Tencent | ARPPU ¥175,1 vs ¥8,5 = 20,6× (4Q21); 6,4× после сжатия (4Q24); сегмент −66,3% за 3 года | Отчёт TME 4Q/FY2021 ([ссылка](https://ir.tencentmusic.com/2022-03-21-Tencent-Music-Entertainment-Group-Announces-Fourth-Quarter-and-Full-Year-2021-Unaudited-Financial-Results)); отчёт TME 4Q/FY2024 ([ссылка](https://www.prnewswire.com/news-releases/tencent-music-entertainment-group-announces-fourth-quarter-and-full-year-2024-unaudited-financial-results-302404220.html)) | `interim-report-tme-gifting-and-cis-willingness-to-pay`, `tencent-music-entertainment-group-announces-fourth-quarter-and-full-year-2021-un` | бенчмарк RESULTS §2; PAPER §4 (регуляторный риск в §9) |
| 16 | Patreon: кеф и масштаб | кеф 12 (арифметика месячного биллинга); ~25M платных vs ~100M бесплатных (дек 2025) | Water & Music, *Why superfan subscriptions are dying out*, дек 2025 ([ссылка](https://newsletter.waterandmusic.com/archive/why-superfan-subscriptions-are-dying-out/)). Кеф 12 — арифметика биллинга, не число из vault. | `why-superfan-subscriptions-are-dying-out` | бенчмарк RESULTS §2 |
| 17 | Telegram Stars: удержание и вывод | desktop 96,5% / mobile 67,5%; минимум вывода 1000 Stars (~$13); холд 21 день | Минимум 1000 Stars: **первичка Telegram** (`stars_revenue_withdrawal_min` в [api/config](https://core.telegram.org/api/config), [api/stars](https://core.telegram.org/api/stars)); удержание и $-конверсия: vendor-гайд Tribute 2026 ([ссылка](https://tribute.top/blog/telegram-stars-creators-guide)) — в vault диапазоны 95–97% / 65–70%; точечные 96,5/67,5 — середины. См. D8. | `telegram-stars-guide-2026-earning-conversion-withdrawal`, `client-configuration`, `telegram-stars` | рельсы fig4; логистика порога $13 (Finding 4) |
| 18 | Комиссия транзакции TON | ~$0,0005 в модели | В vault цифры в TON: ~0,00039 TON (маркетинг ton.org, [ссылка](https://ton.org/en/100000-transactions-per-second-ton-sets-the-world-record-on-its-first-performance-test)) и 0,000540370 TON измеренная ([бенчмарк TON docs](https://docs.ton.org/contracts/standard/wallets/performance)). **$-цифра — конверсия, не число vault** — см. D9. | `ton-the-leading-l1-blockchain`, `wallets-performance-benchmark`, `interim-report-cost-model-architecture-mismatch` | рельсы fig4 (0,1¢ из $1) |
| 19 | Коллапс Hamster Kombat | ×25 за 6 месяцев (300M → 12M), калибровочный якорь | 300M+ юзеров и пост-эйрдропное падение до 12M MAU: AInvest ([ссылка](https://www.ainvest.com/news/telegram-play-earn-ecosystem-high-growth-investment-opportunity-2025-2512/)), CryptoPotato сен 2024 ([ссылка](https://cryptopotato.com/hamster-kombat-announces-details-of-airdrop-2-3m-accounts-banned-for-cheating/)). Бывшая атрибуция «Caladan, апр 2026» — **нет в vault**; снята с подписей/SPEC (2026-08-19). См. D10. | `telegrams-play-to-earn-ecosystem-as-a-high-growth-investment-opportunity-in-2025`, `hamster-kombat-announces-details-of-airdrop-23m-accounts-banned-for-cheating` | калибровка sim3 T1; fig11–13 |
| 20 | Масштаб стримингового фрода (контекст) | до 85% стримов полностью-AI-треков фродовые (2025); ~$2 млрд/год потерь индустрии | **Два источника, не один:** 85% — Deezer Newsroom, 29.01.2026 ([ссылка](https://newsroom-deezer.com/2026/01/ai-generated-music-deezer-selling-detection-tool/), [июль 2026](https://newsroom-deezer.com/2026/07/ai-music-exceeds-50-percent-daily-uploads-deezer/)); $2 млрд/год — Beatdapp via MBW, 09.07.2024 ([ссылка](https://www.musicbusinessworldwide.com/streaming-fraud-costs-the-global-music-industry-2bn-a-year-according-to-beatdapp-now-its-partnering-with-beatport-to-combat-the-trend/)). См. D11. | `how-to-detect-ai-music-deezer-sells-its-detection-tool`, `ai-music-tops-50-of-daily-uploads-on-deezer`, `streaming-fraud-costs-the-global-music-industry-2bn-a-year-according-to-beatdapp` | мотивация fig3 (сама кривая разбавления — аналитика) |
| 21 | Теорема ядра правил дележа | любое устойчивое правило делит взнос слушателя только между теми, кого он слушал | Bergantiños & Moreno-Ternero, *Revenue sharing at music streaming platforms*, arXiv:2310.11861 [econ.TH], окт 2023 ([PDF](https://arxiv.org/pdf/2310.11861)) — полный текст в vault | `arxiv231011861v1-econth-18-oct-2023` | PAPER §1 (потолок World A); README Related work |
| 22 | Доля рынка нижних категорий | нижние две категории популярности ≈ 2% рынка (2,2 млрд оплаченных стримов) | Frederik Juul Jensen, PhD-диссертация *Alternative Payment Systems on Music Streaming Platforms*, Université Sorbonne Paris Nord, защита 05.09.2025 (данные Deezer: 160 747 юзеров, 2018–2020, 3,3 → 2,2 млрд стримов) ([PDF](https://www.musikindustrin.se/wp/wp-content/uploads/2025/09/Frederik-Juul-Jensen-PhD-dissertation-Alternative-Payment-Systems-on-Music-Streaming-Platforms-2025.pdf)) | `jensen-2025-phd-dissertation-alternative-payment-systems-on-music-streaming-plat` | валидация sim1 (сверка «нижние 90% держат 0,9%») |

## Расхождения (vault ≠ атрибуция в репо) — оставлены на виду намеренно

Таблица выше фиксирует то, что vault реально подтверждает. Где текст репо
атрибутирует иначе — различие перечислено здесь, а не молча сглажено: та же
политика, что в *Retracted & bounded*.

- **D1 — «87% артистов (Luminate)».** Число Luminate 2023 в vault — 86,2%
  **треков** ≤1000 плэев, не артистов. Артистные цифры в vault —
  Chartmetric (86% под 10 слушателей/мес). Подписи в бегущем тексте
  теперь говорят «треки» (2026-08-19); T1 остаётся стилизованной *долей
  мира артистов*, калиброванной на эту статистику треков.
- **D2 — «CMA/Last.fm» для топ-0,28% ≈ 50%.** Пара 0,28%/50% и Gini 0,72 —
  кроул Last.fm Celma 2007. Собственное измерение CMA: топ-0,4% → 63–65%
  (2014–2020). Совмещённую подпись «CMA/Last.fm» следует читать «Last.fm
  (Celma 2008); ср. CMA».
- **D3 — обоих per-stream якорей нет в vault.** Ни Duetti $4,43/1000
  (independent), ни $0,0003/стрим (карман подписанного) не имеют заметки в
  vault. Это калибровочные якоря / assumed external rates, не measured
  (PAPER §3, оговорка точности в CHANGELOG v0.5.1); ближайшие независимые
  точки vault: AEPO-ARTIS ≈£0,00065/стрим, CMA ≈£0,001/стрим, waterfall
  E&Y/SNEP 2015. L1–L4 от долларового уровня не зависят; все денежные
  величины, $d^*$ и MVA — да.
- **D4 — «CNM ~6,8%».** Ни одна CNM-заметка vault не несёт 6,8%. Оценки
  прохода в vault: 8–20% (Rose 2024) и ~10,6% (CMU/AEPO-ARTIS). В коде проход
  — *производная* двух якорей (6,772%), так что модель от цифры CNM не
  зависит; зависит только клейм корроборации.
- **D5 — нижняя граница суперфанов 0,6%.** White paper SoundCloud
  поддерживает 1,5% в среднем (→29% дохода), 1–2% типично, 1,9% winners;
  0,6% — из правила участия 97-2-1 (CRITIC §7), не из SoundCloud.
- **D6 — $11,99.** US-цена подписки не сорсится из vault (там UK £-тарифы
  via CMA); доля пула 70% сорсится (B&MT 2023).
- **D7 — Twitch 50/50.** В vault есть только заголовок письма Clancy 2022 о
  revenue shares в списке литературы; самого числа 50/50 нет в телах заметок.
- **D8 — Stars 96,5/67,5.** Vault (vendor-гайд) даёт диапазоны 95–97% и
  65–70%; модель использует середины. Минимум вывода 1000 Stars подтверждён
  первичкой Telegram (API config); конверсия ~$13 — по $0,013/Star из того же
  гайда (гайд внутренне противоречив в одном месте про $/Star).
- **D9 — комиссия TON.** Числа vault — 0,00039–0,00054 **TON** за перевод;
  модельные ~$0,0005 — долларовая конверсия, которой в vault нет (при TON
  $3–5 измеренная комиссия ~$0,0016–0,0027).
- **D10 — «Caladan, апр 2026».** Коллапс Hamster 300M→12M подтверждён vault
  (AInvest, CryptoPotato, Decrypt), но ни одна заметка не называет Caladan.
  Подписи и SPEC теперь ссылаются на AInvest / CryptoPotato (2026-08-19).
  Формулировка vault — падение MAU; рамка SPEC «DAU, окно 6 месяцев» грубее источников.
- **D11 — «фрод до 85%, $2 млрд/год (Beatdapp)».** Два разных источника:
  85% AI-стримов — Deezer; $2 млрд/год потерь — Beatdapp. Цитировать их как
  один нельзя.

*Проверено по vault tonify-research (1 152 заметки) 2026-08-09;
132 запроса search/note show, ничего не процитировано по памяти.*
