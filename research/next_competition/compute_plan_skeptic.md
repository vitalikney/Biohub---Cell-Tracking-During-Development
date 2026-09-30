**Skeptic review of the three lenses (Enveda, others, compute).** I checked three sources myself: the mccormickml Colab page, the ms-pred README and the FRIGID README. I made no Kaggle calls. The Kaggle discussion threads cited in the Enveda lens are unverified by me.

## (a) Prices and GPU-hours: mostly sourced and plausible, with these errors

1. **Colab burn rates check out.** The mccormickml page (updated Mar 2026) gives T4 1.19, L4 1.71, A100-40GB 5.40 and A100-80GB 7.52 compute units per hour. The others lens's "A100 5–11 CU/h" upper end is outdated.
   - Pro+ is almost certainly 500 units, not 600. That page does not state the allowance, so the user should check colab.research.google.com/signup.
   - The Enveda lens's "Pro+ ≈ 110 A100-h/month" should be about 90 (500 / 5.4). Availability is not guaranteed.
2. **The lenses give three different A100 prices.**
   - The Enveda lens says "vast.ai A100 80GB ~$1.76/h". That figure is the cross-tracker median (compute lens) or the vast H100 price (others lens), not vast's A100 price.
   - Vast's A100 is about $0.40–0.72/h (compute and others lenses). RunPod's $1.19–1.39/h is consistent across all three.
   - Effect: the Enveda lens's "$200–450 for 150–300 A100-h" is priced at RunPod rates. At vast rates the same hours cost about $100–200 (estimate).
3. **The Kaggle quota is undercounted, which inflates the "compute is now 5–20x" premise.**
   - The Kaggle GPU option is 2×T4, so 30 h/week is about 60 T4-hours, or roughly 7–12 A100-equivalent hours, not 3–6 (estimate).
   - The two lenses disagree on the 5070 Ti. The Enveda lens puts it at 0.25–0.35x an A100. The compute lens implies about 0.5x (3x vs 6x a T4). Both are estimates without a benchmark on this workload.
4. **The ICEBERG training constraint is confirmed.** The ms-pred README says "two GPUs with at least 24GB RAM to train ICEBERG". It offers ICEBERG 2.1 and GLACIER checkpoints trained on MassSpecGym, and NIST weights only by email with proof of licence.
   - The README does not mention DGL, so "DGL may lack wheels" is unverified in both directions.
   - The README tested inference on an 8 GB RTX 4070M, so simulating the pool could run on the 5070 Ti. Only training needs rented GPUs.
5. **FRIGID's speed is confirmed but not its per-molecule arithmetic.** The README gives 6.58 s per spectrum on an RTX 6000 Ada and requires the precursor formula. The Enveda lens multiplies by about 400 molecules.
   - The test has about 1,500 spectra. At about 3–4x slower on a T4 (estimate), running per spectrum would take about 8–10 h, which breaks the 9 h limit.
   - It is safe only if it runs once per molecule and only on molecules flagged as novel.
6. **Unsourced key numbers.**
   - "~5 A100-h for 32 epochs of MIST on MassSpecGym" has no citation.
   - "ICEBERG 10.8 ms per spectrum" is "via a search result".
   - "NVARC 864 H100-h" is a search summary the others lens itself calls not verified directly.
   - Each is labelled an estimate, but together they carry the whole cost of burst 2.

## (b) Odds changes: the Enveda lens's are not justified; the compute lens's are better supported

1. **The Enveda lens's new odds exactly undo the judge's downgrade.** In judge.md the first assessor proposed bronze 40–50% / silver 15–20%. The judge cut this to 30–40% / ~10% for four reasons: no domain expertise, a start on day 16, fork crowding of the bronze line, and a ~130-molecule public LB. More compute fixes none of these four. The Enveda lens claims to account for "attention binding" but restores the pre-downgrade numbers anyway.
2. **The Enveda lens's numbers do not fit together.** It puts the central score at 0.425 against a bronze line of 0.40–0.42, with a private SE of 0.02–0.025. On those numbers bronze would be above 60%, yet it states 40–50%.
   - The real problem is that 0.425 comes from summing speculative component gains.
   - Its own evidence undercuts those gains. In discussion 743254, the fragmentation gain shrank 2.8x when held out, from +0.065 to +0.023, and the LB did not move (0.341 → 0.336). Top teams also report no LB payoff yet from generated candidates.
   - The forward-simulation "+0.01–0.04" and de novo "0–0.03" gains are unevidenced on this task.
3. **The compute lens's odds (bronze 35–45%, silver 12–15%) are better supported.**
   - In Biohub the quota never ran out: 26.7 h were free on 23 Sep, and about 55–60 GPU-h were used in total.
   - Teammates' quotas were about 7 h used.
   - The survey's own need of 20–60 GPU-h was already far below 320 GPU-h per account.
   - Extra compute mostly buys faster iteration, not a new ceiling.
4. **The others lens's Gemma upgrade (bronze 10–20% → 20–30%) is only partly justified.** Cheap CV passes lower our own selection error. They do not change the private noise of about 60 tasks with SE ≈ 4.6 points, which was the judge's main objection.

## (c) Rule and process problems

1. **The Enveda lens drops the public-dataset requirement.** It says simulated spectra and the pool can be a Kaggle dataset where "private is enough for our own artefacts".
   - The survey said the PubChem/COCONUT pool must be public under the external-data rule, and that publishing needs the user's yes.
   - The compute lens correctly calls this an open rules question. The user must read the rules page himself, because it does not render without login.
   - Until then, assume the derived pool must be public and needs the user's yes.
2. **Licence risk in the weights is under-checked.** The host said anything using or trained on NIST means disqualification.
   - ms-pred's public checkpoints are MassSpecGym-trained, which is fine.
   - The FRIGID README does not say what its MIST encoder and decoder were trained on. It says only "separate ICEBERG models are trained on the training split of each benchmark".
   - The MIST repo also has NIST-era results.
   - Every pretrained checkpoint needs a written check of its training data and licence before use. The host also requires commercial use and redistribution, so NC-licensed library subsets in MassSpecGym or NPLIB1 need a per-source check.
3. **Competition data on third-party hardware.** Discussion 741876 (cited by the Enveda lens, unverified by me) allows training in a "private external cloud".
   - Vast.ai "unverified" community hosts are strangers' machines, and the data is CC BY-NC with no-redistribution rules.
   - Safer: vast.ai verified or datacenter hosts, RunPod Secure, Colab, or the friend's 5070 Ti. The compute lens's cheapest spot prices mostly assume the unsafe tier.
4. **Credentials.**
   - All three lenses keep the user as the one who sets tokens. Good.
   - The compute lens says "no Kaggle token on community hosts" but then suggests a fine-grained HF token on the box. That is allowed only if the user sets it and rotates it afterwards.
   - For Gemma, the gated HF checkpoint needs the user to accept the Gemma licence and set a token himself.
5. **Submissions.**
   - The Enveda lens's "Probes 2–3" and "2–3 probes" rely on a blanket standing rule. Each probe should be a separate yes.
   - The others lens's "teammate submits an ARC fork" is gated on the user's yes. Correct.
   - The Gemma "adapter-applied" probe needs a separate yes and would use Gemma's 1-per-day limit.
6. **The 9 h limit:** only the FRIGID per-spectrum case risks breaking it (see (a) point 5). Everything else is precomputed.

## (d) Contradictions between lenses, and which is better supported

1. **Budget:** Enveda lens $150–400; compute lens $50 by default, $150 only after gates; others lens $300–600 for Enveda plus Gemma. The compute lens is better supported: money follows the CV, and GPU was never the binding constraint. The Enveda lens also fixes rental weeks (W4, W5–6) on the calendar before its CV has been checked against the LB.
2. **Scope:** the Enveda lens adds three GPU-heavy lines (a full fingerprint model, an ICEBERG fine-tune plus pool simulation, FRIGID de novo). The compute lens adds a DreaMS-first head and at most one de novo experiment.
   - The Enveda lens's own finding says isomer ranking is the bottleneck, which argues for the ranker plus one structure-aware feature. It does not argue for de novo (DiffMS 2.3%; no LB transfer reported).
   - Biohub's post-mortem lesson (why_no_trained_models_ru.md, section 5) was cheap trained heads on a public base first, with the expensive model on a separate line only if a person and a card are available for 2+ weeks. The compute lens follows it; the Enveda lens inverts it.
3. **5070 Ti:** the others lens calls it useless for Gemma, which is true (31B w4a16 does not fit in 16 GB). The compute lens says it fits all Enveda models. Both agree it must stay off the critical path, which Biohub supports: friends' cards disappeared mid-competition.
4. **Second competition:**
   - The others lens raises Gemma to fit ~6 and asks for 20–25% of attention, "ideally owned by a teammate".
   - The Biohub record contradicts that ownership model: Vanya was silent 10–18 Sep, the second teammate worked about one day, and the third "member" turned out to be Vanya's Mac.
   - Gemma's final on 2 Dec lands in Enveda's integration weeks (W8–W9).
   - The judge's "watch, decide ~20 Oct, all conditions" is better supported. Cheap rented CV passes satisfy only one of its three conditions.
5. **CV design:** the Enveda lens's fix (remove each structure by InChIKey14 across all libraries; np-examples structures appear in other libraries per discussion 741597) supersedes the survey's masks. Verify it on day 1 with a join on the data.

## (e) The biggest risk the plan ignores: pretrained weights leak into our CV

This is Biohub's pilkwang failure again. There, public detector weights had seen all 199 videos, so every local number was in-sample.

- **The overlap.** MassSpecGym is built from GNPS, MoNA, MassBank and Pluskal-lab MSnLib spectra (a known fact, not re-fetched this session). MIST, ICEBERG 2.1, GLACIER, FRIGID and DreaMS fine-tunes on MassSpecGym were trained on those spectra. The Enveda lens's class-2 panels are built from exactly those libraries, and so are the np-examples structures.
- **Why the fix misses it.** Removing a structure by InChIKey14 from our train does not remove it from pretrained weights.
- **The consequence.** Any gain from a pretrained fingerprint, simulator or de novo feature on those panels is inflated in-sample. Every "+0.015 / +0.02 held-out" gate for pretrained features would pass for the wrong reason. Real class-2 and class-3 test molecules, by definition, have no public spectra those models saw.
- **Precedent.** Our own memory already records "lab over-trusts in-sample" (edge filter: +0.016 local, 0 on LB). The NeckBeard 2.8x shrink points the same way.
- **The LB cannot catch it.** The SE of a difference between two submissions is about 0.016, so with 15–25 probes the LB cannot catch a 0.01–0.03 inflation.
- **Required fix before any rented burst:**
  1. For each pretrained checkpoint, list its training InChIKey14 set (MassSpecGym is public).
  2. Evaluate pretrained features only on panel molecules absent from that set.
  3. Otherwise retrain from scratch on our masked train. That is where rented GPU time actually earns its keep.

A secondary risk nobody quantifies: who owns the work day to day, and for how many hours a week. The Enveda plan runs 4–5 parallel lines (CV, pool, ranker, fingerprint model, forward simulator, de novo) for one user plus the assistant. The Biohub failure was an 11-day gap with no models, not a GPU shortage.

## Verdict

- **Base:** use the compute lens's budget and gates. Use the Enveda lens's CV fix and its isomer-ranking diagnosis.
- **Scope:** drop FRIGID and de novo unless a clean "genuinely absent" panel shows a gain.
- **Leakage audit:** make it gate 0, before any rental.
- **Odds (estimate):** bronze about 35–45%, silver about 12–15%, gold under 3%.
- **Gemma:** stays on watch under the judge's conditions.
- **RSNA and ARC:** stay skipped. All three lenses agree, and the extra compute does not address their blockers (time, no honest CV, fork lotteries).

**Sources I checked:**
- https://mccormickml.com/2024/04/23/colab-gpus-features-and-pricing/
- https://github.com/coleygroup/ms-pred/blob/main/README.md
- https://github.com/coleygroup/FRIGID

**Files read (all under C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\research):**
- next_competition\recommendation_ru.md
- next_competition\judge.md
- next_competition\raw.json
- postmortem\why_no_trained_models_ru.md