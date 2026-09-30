# Skeptic report: why we didn't invest in trained models, and how long it would have taken

**Scope.** I checked the four lenses against these sources:
- `CONTEXT.md`, cited as CTX with line numbers
- `experiments/RESULTS.md`, cited as RES
- `experiments/lb_poll/_final_subs.csv`: 57 rows, dates in UTC
- `research/KNOWLEDGE/FACTS.md` and `DECISIONS.md`
- `research/postmortem/POSTMORTEM_ru.md` and `lenses.json`
- `research/wf_ideas_v3/FINAL_REPORT.md`
- `CONTEXT_FRIEND_B.md` and the experiment READMEs
- git log

Everything was read-only. I made no Kaggle calls.

## 0. Is "we did not invest in trained models" true?

**No, not as stated.** The records show several own training efforts. Six were trained and one was declined:

| When | What | Cost | Source |
|---|---|---|---|
| 5–7 Sep | 9 fine-tunes of the pilkwang weights (exp03B/04/05/08/11/14/16/17/23) | About 9 Kaggle GPU-h in total, 27–95 min each | RES rows exp03B–exp23 |
| 6–9 Sep | Friend A's detector from scratch: 5 ep 2h33m, 20 ep 9.7 h, all-199 21 ep ≈ 16 h, resume to ep 31 ≈ 7–8 h | ≈ 35–36 h on the 5070 Ti | RES; CTX l.412–418, l.507–516 |
| 23–24 Sep | DaughterNet v1 (~20 min), v2 (~25 min), L3 dorado-only (634 s) | Under 1 GPU-h | CTX ~l.1275–1322 |
| 24 Sep | V1284 coordinate-head retrain on 199 videos | 7.2 GPU-h capture; failed its embryo kill test | CTX ~l.1488 |
| 24 Sep | Detector retrain | Declined, estimated at ~23 h per run | CTX ~l.1467 |
| 27 Sep | SEC secondary fine-tunes exp71 and exp77 | ≈ 2 h each | CTX ~l.3001, ~l.3301 |

In total that is about 20–23 Kaggle GPU-h plus about 36 h on the 5070 Ti, **about 55–60 GPU-h of own training**. That already reaches the low end of our own 25 Sep estimate for the top-team path, "≥ 2–3 недели и ≥ 50–100 GPU-ч" (wf_ideas_v3/FINAL_REPORT.md l.90). This total is derived from the rows above.

**What is true:**
1. No model was trained from 11 to 22 Sep.
2. Most of the effort went to the most expensive or least verifiable kinds of model:
   - in-sample fine-tunes;
   - a from-scratch detector with no pretrained encoder or sparse-label loss;
   - SEC.
3. The route of #12 and #18 was started only on 23 Sep, with DaughterNet. That route is cheap downstream heads on the public detector, checked with honest folds.
4. **A learned edge/link re-ranker was never attempted at all.** The only thing on the edges side was the B25 logistic node pruner, 12 videos, 15 Sep. The B34 linker was "blocked… training was not started" (experiments/local_friend_a_linker/README.md l.3).

So the correct lesson is "invest early and steadily in cheap learned heads with honest validation". "Invest in trained models" as such is not the lesson.

## 1. Confirmed claims (no change needed)

- **Submissions:** 57 in total, 12 days with none (4, 5, 8, 9, 12–14, 16–20 Sep). Per-day counts match the CSV. Of 135 possible slots, 57 were used.
- **Probe 1:** 0.899 public / 0.881 private. The 6 Sep pivot text is at CTX l.242–252, and "Heavy model work… next week's quota" is at l.342.
- **Probe 10 (friend A's model):** 0.920 / 0.893. That is −25 public and −14 private against P2 at 0.945 / 0.907.
- **Friend A's LOEO curve:** 0.6635 / 0.5547 / 0.6772 / 0.6803 at epochs 5/10/15/20. The 0.85 gate was not reached. On his own 6bba training videos he scored 0.833 (CTX l.507–520).
- **Absences:**
  - "FRIEND A: silent since 10 Sep" (CTX l.934). Git shows no Sasyami commits from 11 to 17 Sep.
  - Friend B committed only on 15 Sep (80 commits).
  - The 18 Sep entry reads "FRIEND A IS BACK, FRIEND B IS OUT".
  - Friend C is friend A's own MacBook (CTX 23 Sep entry, ~l.1240), and nothing ran on it (~l.1086).
- **Commit counts:** the per-day team and per-author counts match git exactly. The lead has 9 days with fewer than 5 commits, and 314 commits in 25–29 Sep.
- **DaughterNet:**
  - Trained 23 Sep at 21:40 UTC; OOF parent AUC 0.848; 5 folds with the 44b6 leak groups kept whole.
  - Confirmation +0.0019, CI [−0.0007, +0.0050]. Precision 27%, below its 31% gate.
  - Private reads: +5 (P28/P27), +3 (P35/P34), +3 (#37/#38); public +1 each time.
- **Decline and ban:**
  - The detector retrain was "declined on arithmetic" on 24 Sep.
  - PRE-REG v3 was approved by the user on 25 Sep at 13:38. It says "no detector/edge/head retraining before 29.09" and "M3 = NO".
  - The R9 row is in DECISIONS around l.1814.
- **exp71 delay:** it was blocked on 26 Sep at 21:54Z (CTX ~l.2539). The user said yes on 27 Sep at 11:11:40Z (~l.2933), a 13.3 h delay.
- **"Model swaps 0 of 5":** this is FACTS F-TRN-41. The private pairs are 0, −14, +3, −1, −2.
- **Quota readings:**
  - ~20 of 30 h used by ~7 Sep (l.617), ~5.5 h left on 9 Sep.
  - 26.7 h free on 23 Sep (~l.1253).
  - 18:56 used on 25 Sep (l.1745).
  - 07:55 used on 26 Sep (l.2542), 20:29 on 28 Sep (l.3476).
  - About 2.7 h left late on 28 Sep (l.4240).
- **User targets:** the timeline's **22 Sep** date for the 0.950 and 0.97 targets is correct. Git has "Programme 0.950 (user decision)" at 22 Sep 10:26 MSK and "Target 0.97 (user)" at 12:48 MSK. The CONTEXT entries are mislabelled "2026-09-23". Probes 21 and 22 went in on 22 Sep at 08:41 UTC.

## 2. Wrong or unsupported claims, with the correct value

### Timeline lens

1. **"GPU quota was never one of the recorded reasons."** This is false. Compute cost was cited when deferring or declining training at least four times:
   - 6 Sep: "Heavy model work … moves to next week's quota" (CTX l.342). The same day, "~11 h left this week" (l.341).
   - Day 1: "full epoch … ~2.1 h -> training from scratch infeasible" (RES l.10).
   - 22 Sep: "synthetic pretraining (3-4 GPU days)" was rejected (~l.1128).
   - 24 Sep: "1 run = ~23 h on the 5070 Ti" (~l.1467).

   Correct wording: *in hindsight the quota never ran out, especially counting the teammates' quotas, but compute or run time was a stated reason several times.*
2. **"5.6 of our 5.6 idle days fall in 10–22 Sep."** This contradicts itself. Its own table marks 4 Sep as idle (f = 1.0), and that is outside the window. Adding up the table's own f values gives 5.2, not 5.6.
3. **The class totals (a 5.7 / b 2.9 / c 4.8 / d 6.2 / e 2.0 / f 5.6) cannot be reproduced from the table.** The table's own fractions add up to about a 5.6, b 2.9, c 4.25, d 5.55, e 1.3, f 5.2. That is 24.8 of 27 days, and many rows add up to 0.8–0.9. The split must be labelled a subjective estimate, and the totals do not follow from the rows.
4. **"About 40 h on friend A's 5070 Ti."** The recorded epoch times give about 35–36 h of training.
5. **"exp77 about 2.4 h."** The records show a full epoch of 18,707 iterations at ~0.39 s/it, which is ≈ 2.0 h. Both recipes ran in parallel on T4×2. The session ran at most ~3.1 h: it was pushed after the 18:19Z yes and was COMPLETE at 21:24Z (CTX ~l.3301).
6. **"Probe 10 on 8 Sep."** It was submitted 7 Sep at 20:58 UTC (23:58 MSK) and scored 8 Sep.
7. **"Delayed the only retrain by ~13 h."** It was the *secondary* retrain. DaughterNet and the head retrain had already run on 23–24 Sep.
8. **"Dorado-pretrained variant."** L3 was trained on dorado only and closed with "no v3 init". No pretrained variant was ever used.
9. **"Days with 0 team commits: 4, 14, 17."** The list is 3–5, 14 and 17 Sep. Git starts on 6 Sep at 01:52 MSK, while the 5 Sep work shows up only in file mtimes.

### Models lens

1. **"DaughterNet was also the only model validated on held-out videos."** This is false, and the lens's own findings contradict it. Three other checks were honest held-out validations:
   - friend A's LOEO scratch model (embryo held out);
   - AdaBN on that model (+0.0073, honest);
   - the V1284 head retrain (leak-group OOF plus embryo held out).

   Correct wording: *the only held-out-validated model that shipped*. Also, DaughterNet's folds are by video and leak group, not by embryo (postmortem l.82).
2. **"0.68 on the unseen embryo against 0.88 for pilkwang."** The 0.8807 figure is leaky: CTX l.512–513 says "(both leaky)", because pilkwang saw 44b6. The comparison is not like-for-like.
3. **"Two of them (secondary exp23, secondary weight 0.5) were in fact private-positive."** Secondary weight 0.5 (P5) is a knob, not a model. It does not belong in a list of own models.
4. **"exp03B public +0.004 … priv ~0 vs P3/P4."** We never ran a verbatim 0.941 probe. The +0.004 is against the author's public score, and P3/P4 are knob variants. There is no clean private pair for exp03B on the 0.941 base.
5. **"exp15 ~1 GPU-h."** RES gives 20 min.
6. **"The two teammates' quotas sat idle."** Friend B's B20 stream ran through a private kernel on 15 Sep: 24 bundles × 25 min were planned (CTX l.960), paused at 148/199, so about 7 h were used. "Mostly unused" is correct; "idle" is not.

### Constraints lens

1. **"Our own quota went mostly to probe and dummy kernels: ~25 of 30 h in week 1."** Week 1 was about half training: RES lists about 9 h of fine-tune kernels by 7 Sep. lenses.json itself says week 1 was "front-loaded on our own fine-tunes". "Mostly probes and dummies" holds for week 4 only: about 27 h, of which about 4–5 h was SEC.
2. **"5 model-side probes (7, 10, 13, 52, 54)."** Weight or model changes were also probed in 1, 2, 11, 15, 17, 20, 28, 31 and 35, and the insertion is in every file from #37 on. There were **at least 13** model-side probes.
3. **"43 of the 57 submissions were public-stack knob or variant probes."** The category is not defined and I could not reproduce it. There were 46 submissions from 10 Sep on.
4. **DaughterNet timing, "23 Sep 18:30 to 24 Sep 03:45, ~9–10 h."** No 18:30 start appears in the records. The plan workflow finished at 20:30 UTC (~l.1244), which gives ≈ 7.25 h to submission, matching the models lens.
5. **"The 7.2 GPU-h head capture" counted as training.** It was feature capture, i.e. inference to produce training data. That is fine inside a "GPU spent on own models" total, but it is not training time.
6. **"~300 GPU-h" of friend A idle time and "≥ 150–300 GPU-h realistically usable."** This counts the card 24/7 while its owner was absent (11–17 Sep, and from 24 Sep). The files support **"theoretically available"**. "Realistically usable" is not supported, because the person was the constraint. Our own agent also noted that T4×2 may be charged double (FINAL_REPORT l.359; unverified).

### Feasibility lens

1. **"The 199-video table was blocked by the 82 GB of data."** Only friend B's machine was disk-blocked. The laptop had the full 82 GB by 15 Sep (CTX l.785). The Kaggle cache pass was ~8–10 h unattended (l.958), and friend A built it in about a day on 19 Sep. The blocker was staffing and attention, not disk.
2. **"ymg_aq's first heads were worth about +0.011 private within days."** The lens itself says "their start date before 9/17 is not stated". "Within days" is unsupported.
3. **None of the detailed external numbers are in the repo:**
   - Corwin's "52 days, 112 subs, >4,200 sub-agent runs, 478 workflows";
   - the per-stage CV of the 18th place: +0.021 / +0.020 / +0.021;
   - "9/18 0.957/0.927" and "9/20 TabPFN 0.942";
   - hjyact's "0.936 single / 0.926 public";
   - Corwin's "OOF secondary −0.007".

   lenses.json has only the headline numbers. The postmortem (l.106) says the write-ups were "читали в браузере, в репозитории они не сохранены, скептиком не проверены" (read in the browser, not saved in the repo, not checked by the skeptic). All of these must be labelled *unverified external*.

## 3. Contradictions between lenses

| Point | Lenses say | What the files support |
|---|---|---|
| Friend A GPU training | timeline ~40 h; constraints ~36 h; models ~36 h | **≈ 35–36 h** (RES; CTX l.412–418) |
| exp77 time | 2.4 h / ~2 h / 2.5–3 h | **≈ 2.0 h of training per recipe, in parallel; session ≤ ~3.1 h** |
| DaughterNet plan-to-LB time | ~7 h (models) vs 9–10 h (constraints) | **~7.25 h** from the 20:30 UTC plan to the 03:45 submit |
| Teammate quotas | "sat idle" (models) vs "~10 h used" (constraints) | **~7 h used** (friend B, 15 Sep); offered for the first time 28 Sep (CTX ~l.3688) |
| Week-1 quota use | constraints "mostly probes"; lenses.json and models "front-loaded on fine-tunes" | **fine-tunes ≈ half** (RES) |
| Effort for the heads-first route | models "5–8 working days, <15 GPU-h" vs feasibility "(d) 3–5 + (a) 10–15 person-days, 10–20 GPU-h" | **Feasibility's is better founded.** DaughterNet took ~1 day only because friend A's 199-video cache (19 Sep), the splits, the replay lab and div_insert already existed. That groundwork took about 4–5 person-days spread over 15–23 Sep. |
| "Only lever that transferred" | timeline and models: DaughterNet only | **DaughterNet was the only *own* lever.** The public x138 head (+3) and keeping DC 0.20 (+2, an inherited default) also carried over (postmortem l.34, l.40). |

## 4. Estimates that are overconfident or need a basis label

1. **Feasibility: "private ~0.925–0.940, central ~0.930; silver likely."** Overconfident. The basis is one outside team's deltas (ymg_aq +0.011…+0.026, with a different chassis, HOCT/Trackastra features, TabPFN, and unknown lead time) plus our DaughterNet +0.003…+0.005. What argues for a lower number:
   - Our second honest head, the coordinate retrain, failed across embryos.
   - Our in-sample labs got the sign wrong on 11 of 17 levers (postmortem l.73).
   - Corwin's bench over-read private by ~0.03.
   - Only 1 of ~20 own models transferred.
   - The silver cut is only bracketed at 0.921–0.924, not observed (lenses.json l.312).
   - Our existing exp70j (0.922) might already have cleared it, so silver may have been a selection problem, not a modelling one.

   A defensible label would read: *estimate; central ≈ +0.005 (≈ 0.925), range ≈ 0.918–0.935; silver roughly a coin flip. Basis: DaughterNet +0.003…+0.005, one outside team, our own transfer record.*
2. **Feasibility, gains for (a) +0.005…+0.020 and (b) +0.004…+0.012.** The upper ends rest on the gold-line and #12 teams. Say so, and give our own record (+0.003…+0.005 from one head) as the lower anchor.
3. **Feasibility (d): "harness alone +0.000…+0.003 (keep DC 0.20, avoid DIS, keep exp87a)."** Our lab got DC 0.30 wrong in sign (+0.0013 → −0.002, postmortem l.79). There is no evidence that the harness would have picked 0.20; it is hindsight. Label it *speculative*.
4. **Models: "5–8 working days and <15 GPU-h, feasible in 20 days."** Label it an estimate. It leaves out the harness groundwork, which took about 4–5 person-days in practice.
5. **Constraints: "GPU margin 2–5×."** It depends on the theoretical 150–300 GPU-h. Against what our own account actually had after 11 Sep, about 50–60 spare Kaggle GPU-h (derived), the margin is closer to 1×. The claim that compute was not the binding constraint still holds, because the top-team estimate for the heads-only route is 10–20 GPU-h.
6. **Timeline effort split:** subjective. Say so, and do not present the totals as derived from the table (see 2.3 above).

## 5. Framing the files support for the answer to the user

- **Did we invest?** Yes, in two bursts: 5–9 Sep and 23–27 Sep, about 55–60 GPU-h in total. But:
  - We spent it on the expensive or in-sample kinds: fine-tunes of in-sample weights, a raw from-scratch detector, SEC.
  - Nothing was trained from 11 to 22 Sep, when nearly everyone was absent: friend A silent from 11 to 17 Sep, friend B out by 18 Sep, the lead at ≤ 3 commits on most days.
  - The cheap heads route with honest folds started on day 20. We never tried a learned edge head.
- **Why:**
  1. The only validator we considered was the most expensive one, a from-scratch model. It stalled at 0.68, so the honest bed never existed until 23 Sep.
  2. From 6 Sep the public LB was treated as the only judge. Early model swaps read negative there ("0 of 5"), and that record hardened into R9 on 25 Sep, which the user approved.
  3. The team was only partly available in the middle of the competition.
  4. Public shortcuts (DivNet, x138) and the user's targets on 22 and 27 Sep pulled effort toward knob probes.
- **How long would it take?** These are the recorded costs, not estimates:
  - DaughterNet: about 1 person-day and under 1 GPU-h, once the cache and splits existed;
  - the 199-video cache: ~8–10 h unattended on Kaggle, or about 1 day on the 5070 Ti;
  - one detector retrain: ~23 h on the 5070 Ti, or 1.3 h per epoch on a T4.

  A heads-first plan is *estimated* at 2–4 weeks of one person's time and 10–20 GPU-h. It fit in 20 days only if started in week 1 and staffed continuously.