---
description: Every input with its status — measured, derived, assumed, or a model parameter.
layout:
  width: wide
---

# Sources

Every quantity in this study carries one of four statuses, and the status is part of the claim:

| Status | Meaning |
|---|---|
| **M — measured** | comes from data or a published measurement, with the source named |
| **D — derived** | arithmetic over measured quantities |
| **A — assumed** | a modelling assumption; the study says so and shows what breaks if it is wrong |
| **P — model parameter** | a dial of the simulation, not a claim about the world |

The rule that makes this useful: an assumed number may never be reported as if it were measured. Where a source is weaker than it looks — an industry figure without a methodology, a panel statistic normalised over a lifetime rather than a year — the caveat travels with the number everywhere it is used.

***

*🇬🇧 English | [🇷🇺 Русский](https://github.com/ProximaCA/tonify-sims/blob/main/SOURCES.ru.md)*

## SOURCES — every parameter, its value, its provenance

One row per model parameter: the value the simulations actually use, the
source as verified in the research vault (tonify-research, 1,152 notes), the
vault note id, and where the parameter enters the code/figures. Rows where
the vault does **not** confirm the repo's attribution say so explicitly — see
*Discrepancies* below the table. Nothing in this file is cited from memory;
every link was read from a vault note. Where the vault has no source, the row
says `assumption` or `not in vault` instead of inventing one.

| # | Parameter | Value used | Source (as verified in vault) | Used in |
|---|-----------|-----------|-------------------------------|---------|
| 1 | Artists under 1,000 streams/yr (target T1) | 87% | Closest verified: Luminate year-end 2023 — 86.2% of **tracks** (not artists) ≤1,000 plays, via MBW 14 Mar 2024 ([link](https://www.musicbusinessworldwide.com/deezer-has-deleted-26m-useless-tracks-since-it-launched-artist-centric-model-with-universal-music-group/)); artist-side analogue: Chartmetric 2025 — 86% of Spotify artists <10 monthly listeners, via Kullick & Petry 2025 ([PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/61644B64A790CB6B4B15A36C3D6DF83C/S2059599925100150a.pdf)). See discrepancy D1. | sim1 world construction, validation T1; fig2 |
| 2 | Rightsholders above $1,000/yr | 2.6% (259,700 of 10M+ uploaders, 2023) | Spotify Loud & Clear (2023 data), via Music Ally, 14 Jan 2025 ([link](https://musically.com/2025/01/14/chartmetric-tracks-11m-spotify-artists-fewer-than-1-6m-have-over-10-listeners/)) | sim1 validation T2; CRITIC §5 bound (rightsholders, not artists) |
| 3 | Top share of streams (target T3) | top-0.28% ≈ 50%; Gini 0.72 | Òscar Celma, PhD thesis *Music Recommendation and Discovery*, UPF Barcelona (Last.fm crawl, July 2007: top-737 of 260,525 artists = 50% of playcounts) ([PDF](http://www.mtg.upf.edu/static/media/PhD_ocelma.pdf)). **Not a CMA number** — CMA's own: top-0.4% → 63–65% of streams 2014–2020 ([final report](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1120610/Music_and_streaming_final_report.pdf)). See D2. | sim1 validation T3 (world Gini validates at 0.97 by streams) |
| 4 | Plays per listener per artist | median 5.16, mean 21.21 | Schedl & Hauger, *Int. J. Multimedia Information Retrieval* 6:71–84, 2017, Table 6 (LFM-1b: 120,322 users, 1.09B events) ([PDF](https://link.springer.com/content/pdf/10.1007%2Fs13735-017-0118-y.pdf)); dataset intro: Schedl, ICMR 2016 ([PDF](https://www.cp.jku.at/people/schedl/Research/Publications/pdf/schedl_icmr_2016.pdf)). Measures panel lifetime, not a year → red team widened to 8–21 (CRITIC §2). | every MVA number (PL=21.21 in all three sim1 scripts); fig1/5/7 |
| 5 | Pro-rata independent payout | $4.43 per 1,000 streams (US, Jan 2026) | Cited in PAPER §3 as Duetti; **not in vault** — no Duetti note exists, no public link verified here. See D3. | anchor of the independent pool; fig1/5/7, breakeven |
| 6 | Signed artist per-stream take | $0.0003/stream | **Not in vault** as a direct figure. Nearest independent points in vault: E&Y/SNEP 2015 waterfall via Techdirt ([link](https://www.techdirt.com/2015/02/05/yes-major-record-labels-are-keeping-nearly-all-money-they-get-spotify-rather-than-giving-it-to-artists/)); AEPO-ARTIS ≈£0.00065/stream (Sony data in CMA); CMA ≈£0.001/stream. See D3. | anchor of the signed pocket; 188,590; fig1/5/7 |
| 7 | Label pass-through | 6.772% — **derived** as 0.0003/0.00443, not an input (PAPER CHANGELOG v0.5.1) | Vault-independent corroboration of the order: 8–20% pass-through (Rose, *Streaming in the Dark*, Berkeley J. Ent. & Sports Law 13:1, May 2024, [PDF](https://publicknowledge.org/wp-content/uploads/2024/05/Streaming-in-the-Dark_Competitive-Dysfunction-Within-the-Music-Streaming-Ecosystem_Berkeley-Journal-of-Entertainment-Sports-Law_May-2024.pdf)); ~10.6% reaches recording artists (CMU via AEPO-ARTIS). The "~6.8% (CNM)" corroboration named in code comments is **not in vault**. See D4. | v05 matrix signed column; ×14.8 contract multiplier; fig7 |
| 8 | Superfan share of audience | 0.6–1.7% (sensitivity range; 1.7% base) | SoundCloud × MIDiA, *Building a fan economy with Fan-Powered Royalties*, July 2022 (118,000 artists: avg 1.5% of interactions → 29% of income; "typically 1–2%"; FPR winners 1.9% → 42%) ([PDF](https://vi.be/files/2022-08/soundcloud-x-midia-building-a-fan-economy-with-fan-powered-royalties.pdf)). Lower bound 0.6% from the 97-2-1 participation rule (CRITIC §7), not from the white paper. See D5. | breakeven range (18 combinations); fig1, fig6 |
| 9 | Superfan revenue share (retraction input) | 29% of artist income | Same SoundCloud × MIDiA white paper — share of *royalties* under FPR, not donations; this category error is why "0.42 donations/yr" was retracted (CRITIC §1) | retracted P6 inversion; Retracted & bounded |
| 10 | Donation check | $3.1–6.9 (range; lognormal $5 base) | Range anchor: Waskow, Markett, Montag et al., *Pay What You Want! A Pilot Study on Neural Correlates of Voluntary Payments for Music*, Frontiers in Psychology 7:1023, 2016 — corrected mean PWYW €3.10, refusal 24.4% vs 17.3% (128/525 vs 91/525), N=25, real Bandcamp albums ([link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4933710/)). The lognormal($5, σ=0.8) *shape* is an **assumption, not measured** (RESULTS, honest limitations). | direct-economy check; fig1/5/6/7, breakeven |
| 11 | Subscription price × pool share | $11.99/mo × 70% to the rights pool | 70%: "around 70%" per Bergantiños & Moreno-Ternero 2023 (citing Meyn et al. 2023) ([PDF](https://arxiv.org/pdf/2310.11861)). $11.99 (US price) **not in vault** (vault holds UK £ tariffs from the CMA report). See D6. | user-centric wallet model; fig1/5/7 |
| 12 | Twitch paying-fan cadence, sub price, split | k=12+ structural; $5/mo; 50/50 split | $5 monthly sub: Sjöblom & Hamari, *Computers in Human Behavior* 2017 ([PDF](https://www.utupub.fi/bitstream/handle/10024/171134/Why%20do%20people%20watch%20others%20play%20video%20games.pdf?sequence=1)); 50/50 split: only as the *title* of ref. 44 (Clancy 2022 letter) in the vault — percentages not in any note body. See D7. | Twitch mechanics row (MVA 2,353); fig5/7; RESULTS §2 |
| 13 | Twitch income inequality | α=−2.13, Gini 0.57 (top-10k), ≈0.93 platform-wide | Houssard, Pilati, Tartari, Sacco & Gallotti, *Monetization in online streaming platforms*, Scientific Reports 13:1103 (2023) ([PDF](https://www.nature.com/articles/s41598-022-26727-5.pdf)) | RESULTS §2 benchmark context |
| 14 | Twitch motivation model | explains 3.7% of subscription variance; N=1,097 | Sjöblom & Hamari 2017 (same paper as #12) | RESULTS §2 (why cadence, not motivation, is the dial) |
| 15 | Tencent gifting multiplier | ARPPU ¥175.1 vs ¥8.5 = 20.6× (4Q21); 6.4× after squeeze (4Q24); segment −66.3% over 3 yrs | TME 4Q/FY2021 results ([link](https://ir.tencentmusic.com/2022-03-21-Tencent-Music-Entertainment-Group-Announces-Fourth-Quarter-and-Full-Year-2021-Unaudited-Financial-Results)); TME 4Q/FY2024 results ([link](https://www.prnewswire.com/news-releases/tencent-music-entertainment-group-announces-fourth-quarter-and-full-year-2024-unaudited-financial-results-302404220.html)) | RESULTS §2 benchmark; PAPER §4 (regulatory risk in §9) |
| 16 | Patreon cadence and scale | k=12 (monthly billing arithmetic); ~25M paid vs ~100M free (Dec 2025) | Water & Music, *Why superfan subscriptions are dying out*, Dec 2025 ([link](https://newsletter.waterandmusic.com/archive/why-superfan-subscriptions-are-dying-out/)). k=12 is billing arithmetic, not a vault number. | RESULTS §2 benchmark |
| 17 | Telegram Stars retention and payout | desktop 96.5% / mobile 67.5%; min withdrawal 1,000 Stars (~$13); 21-day hold | Withdrawal minimum 1,000 Stars: **Telegram primary** (`stars_revenue_withdrawal_min` in [api/config](https://core.telegram.org/api/config), [api/stars](https://core.telegram.org/api/stars)); retention and $-conversion: Tribute vendor guide 2026 ([link](https://tribute.top/blog/telegram-stars-creators-guide)) — vault holds ranges 95–97% / 65–70%; the point values 96.5/67.5 are midpoints. See D8. | fig4 rails; $13 threshold logistics (Finding 4) |
| 18 | TON transaction fee | ~$0.0005 used in the model | Vault holds TON-denominated figures: ~0.00039 TON (ton.org marketing, [link](https://ton.org/en/100000-transactions-per-second-ton-sets-the-world-record-on-its-first-performance-test)) and 0.000540370 TON measured ([TON docs benchmark](https://docs.ton.org/contracts/standard/wallets/performance)). The **$ figure is a conversion, not a vault number** — see D9. | fig4 rails (0.1¢ of $1) |
| 19 | Hamster Kombat collapse | ×25 in 6 months (300M → 12M), calibration anchor | 300M+ users and post-airdrop decline to 12M MAU: AInvest ([link](https://www.ainvest.com/news/telegram-play-earn-ecosystem-high-growth-investment-opportunity-2025-2512/)), CryptoPotato Sep 2024 ([link](https://cryptopotato.com/hamster-kombat-announces-details-of-airdrop-2-3m-accounts-banned-for-cheating/)). The former "Caladan, Apr 2026" attribution is **not in vault** and has been removed from captions/SPEC (2026-08-19). See D10. | sim3 calibration T1; fig11–13 |
| 20 | Streaming fraud scale (context) | up to 85% of fully-AI-track streams fraudulent (2025); ~$2B/yr industry losses | **Two sources, not one:** 85% — Deezer Newsroom, 29 Jan 2026 ([link](https://newsroom-deezer.com/2026/01/ai-generated-music-deezer-selling-detection-tool/), [Jul 2026](https://newsroom-deezer.com/2026/07/ai-music-exceeds-50-percent-daily-uploads-deezer/)); $2B/yr — Beatdapp via MBW, 9 Jul 2024 ([link](https://www.musicbusinessworldwide.com/streaming-fraud-costs-the-global-music-industry-2bn-a-year-according-to-beatdapp-now-its-partnering-with-beatport-to-combat-the-trend/)). See D11. | motivation for fig3 (the model's dilution curve itself is analytic) |
| 21 | Payout-rule core theorem | any stable rule divides a listener's fee only among artists that listener streamed | Bergantiños & Moreno-Ternero, *Revenue sharing at music streaming platforms*, arXiv:2310.11861 [econ.TH], Oct 2023 ([PDF](https://arxiv.org/pdf/2310.11861)) — full text in vault | PAPER §1 (World-A ceiling argument); README Related work |
| 22 | Bottom-tier market share | bottom two popularity categories ≈ 2% of market (2.2B remunerated streams) | Frederik Juul Jensen, PhD dissertation *Alternative Payment Systems on Music Streaming Platforms*, Université Sorbonne Paris Nord, defended 5 Sep 2025 (Deezer data: 160,747 users, 2018–2020, 3.3B → 2.2B streams) ([PDF](https://www.musikindustrin.se/wp/wp-content/uploads/2025/09/Frederik-Juul-Jensen-PhD-dissertation-Alternative-Payment-Systems-on-Music-Streaming-Platforms-2025.pdf)) | sim1 validation ("bottom 90% hold 0.9%" cross-check) |

### Discrepancies (vault vs repo attribution) — kept visible on purpose

The table above records what the vault actually verifies. Where the repo's
running text attributes differently, the difference is listed here rather
than silently harmonized — the same policy as *Retracted & bounded*.

- **D1 — "87% of artists (Luminate)".** The vault's Luminate 2023 number is
  86.2% of **tracks** ≤1,000 plays, not artists. The artist-side figures in
  the vault are Chartmetric's (86% under 10 monthly listeners). The T1 anchor
  functions as a stylized target; its label "artists (Luminate)" overstates
  the source's granularity.
- **D2 — "CMA/Last.fm" for top-0.28% ≈ 50%.** The 0.28%/50% pair and
  Gini 0.72 are Celma's 2007 Last.fm crawl. CMA's own measurement is
  top-0.4% → 63–65% (2014–2020). The repo's combined label "CMA/Last.fm"
  should read "Last.fm (Celma 2008); cf. CMA".
- **D3 — the two per-stream anchors are not in the vault.** Neither Duetti
  $4.43/1,000 (independent) nor $0.0003/stream (signed pocket) has a vault
  note. They are the model's declared external anchors (PAPER §3, CHANGELOG
  v0.5.1 precision caveat); nearest independent vault points: AEPO-ARTIS
  ≈£0.00065/stream, CMA ≈£0.001/stream, E&Y/SNEP 2015 waterfall.
- **D4 — "CNM ~6.8%".** No CNM note in the vault carries 6.8%. The vault's
  pass-through estimates span 8–20% (Rose 2024) and ~10.6% (CMU/AEPO-ARTIS).
  In the code the pass-through is *derived* from the two anchors (6.772%),
  so the model does not depend on the CNM figure; the corroboration claim
  does.
- **D5 — superfan lower bound 0.6%.** The SoundCloud white paper supports
  1.5% average (→29% of income), 1–2% typical, 1.9% winners; 0.6% comes from
  the 97-2-1 participation rule (CRITIC §7), not from SoundCloud.
- **D6 — $11.99.** The US subscription price is not vault-sourced (vault
  holds UK £ tariffs via CMA); 70% pool share is sourced (B&MT 2023).
- **D7 — Twitch 50/50.** Only the title of Clancy's 2022 letter on revenue
  shares exists in the vault's reference list; the 50/50 number itself is
  not in any note body.
- **D8 — Stars 96.5/67.5.** Vault (vendor guide) gives ranges 95–97% and
  65–70%; the model uses the midpoints. The 1,000-Star withdrawal minimum is
  confirmed by Telegram's own API config; the ~$13 conversion uses the same
  guide's $0.013/Star (the guide is internally inconsistent about $/Star at
  one point).
- **D9 — TON fee.** Vault numbers are 0.00039–0.00054 **TON** per transfer;
  the model's ~$0.0005 is a dollar conversion not present in the vault (at
  TON $3–5 the measured fee is ~$0.0016–0.0027).
- **D10 — "Caladan, Apr 2026".** The Hamster 300M→12M collapse is
  vault-confirmed (AInvest, CryptoPotato, Decrypt), but no vault note names
  Caladan. Captions and SPEC now cite AInvest / CryptoPotato (2026-08-19);
  the vault wording is MAU decline; the SPEC's "DAU, 6-month window" framing
  is coarser than the sources.
- **D11 — "fraud up to 85%, $2B/yr (Beatdapp)".** Two different sources: the
  85% share of AI-track streams is Deezer's; the $2B/yr industry loss is
  Beatdapp's. They should not be cited as one.

*Verified from the tonify-research vault (1,152 notes) on 2026-08-09;
132 search/note-show queries, nothing cited from memory.*
