# Kaggle competition verdict, 30 Sep 2026

**Checks:** I made one read-only Kaggle call (`kaggle competitions list --sort-by prize`). It confirms that ARC-AGI-3 and ARC-AGI-2 both close 2026-11-02 23:59 UTC and have 3,493 and 2,260 teams. It also confirms the ARC paper track closes 2026-11-09. Everything else below comes from the page facts and assessments I was given. I did not recheck them against the site. The GitHub repos the assessors cite are unverified third-party claims. All probabilities and GPU-hour figures are my estimates.

## Ranking

1. **Enveda CASMI 2026 — molecule ID from mass spectra (Featured, medals, 75 days left). Enter.**
   - The work is retrieval plus ranking over about 3 GB of array data. That runs on a laptop CPU, the ranker is gradient boosting, and the GPU need is small (20–60 GPU-h, estimate).
   - It allows an honest CV early (the enveda-np-examples set with three masks), which is our main post-mortem lesson.
   - There is visible room above the public notebooks: the best notebook scores 0.386 and #1 scores 0.464.
   - I downgraded the fit from 8 to 7.5 and the medal odds from 40–50% bronze / 15–20% silver to about 30–40% bronze and about 10% silver:
     - We have no mass-spec or chemistry background.
     - We start on day 16 of 91.
     - By December many teams will be sitting on copies of the best public notebook ("fork" copies). That will likely push the bronze cutoff to or above the notebook ceiling, so a medal needs our own gains, and the assessor admits this in its own dealbreakers.
     - The public LB covers only about 130 molecules (standard error about 0.035), so it is a weak guide.
     - The GPU arithmetic is consistent: 75 days is about 10.7 weeks, and 20–60 GPU-h is far below one account's quota.

2. **Gemma 4 Developer Agent (Featured, medals, 63 days left). Watch, decide later.**
   - The assessor calls this "the rare competition where GPU matters less". That contradicts its own numbers: one honest CV pass is 8–12 Kaggle GPU-h, so only about 2–3 passes fit in a week.
   - The score is very coarse. With about 60 private tasks, one task is about 1.7 points, and a single pass's standard error is about 4.6 points, wider than the gap between medal bands. The private rank is close to a lottery.
   - LoRA on a 31B model is out of reach for our compute. An unverified dev repo also claims the scorer drops adapters.
   - I downgraded fit from 5 to 4.5. Bronze is about 10–20% (estimate).
   - Its GPU use would not block Enveda (Enveda needs little GPU), but both compete for the same scarce attention: the user's and the assistant's.

3. **ARC Prize 2026 — ARC-AGI-3 (33 days left, entry deadline 26 Oct). Skip as a main competition.**
   - The only medal route is forking a public agent. The best one scores 5.75, about rank 47; bronze is about rank 349.
   - There is no honest CV: only 25 public games against 110 hidden ones.
   - LLM agents are random between runs, and the private set is 55 games.
   - It is unverified whether runs on the dedicated RTX 6000 machines count against our GPU quota.
   - Fit stays at 4. Bronze is about 20–30%, and only by lottery.

4. **ARC Prize 2026 — ARC-AGI-2 (33 days left). Skip.**
   - A fork of the 33.89 public notebook ties about rank 14–15, while bronze is about rank 226. So the margin to the bronze line is actually large, but we lose every tie on submission time to the earlier forkers.
   - The assessor's claim that one run costs about 24 GPU-h assumes a full 12 h run on the L4x4 machines, which count double. The commit run on the small public data may be much cheaper; that is unverified.
   - It teaches us almost nothing and is not our own model. Fit stays at 3.5.

5. **RSNA Knee Abnormality Detection (22 days left, entry deadline 15 Oct). Skip.**
   - 570 GB of DICOM and a saturated top 50 (0.953–0.961). A medal needs 60–150+ GPU-h of 3D CNN training we do not have time or hardware for. Fit is 2.5–3.

6. **Playground S6E10 (expected around 1–31 Oct; an estimate, not announced yet). Optional practice only, no medals.**
   - Only useful to rehearse ranking with LightGBM if there are idle cycles. Otherwise skip. S6E9 closes today.

7. **Not considered:**
   - Kaggriculture: closes today.
   - The ARC and Gemma paper tracks: no medals. The Gemma paper track only makes sense if we enter Gemma.
   - Pokémon PTCG Playground, the Community competitions, the Community hackathons and the Getting Started competitions: no medals.

## Picks

- **Enter now: Enveda CASMI 2026 only.** Deadlines: entry and team merger by 7 Dec 23:59 UTC (8 Dec 02:59 MSK); final by 14 Dec 23:59 UTC (15 Dec 02:59 MSK). The user must accept the rules manually on the site; we do not join through the API.
- **No second competition now.** None of the others is both a fit and cheap in attention. The two ARC competitions are fork lotteries that contradict the post-mortem.
- **Watch: Gemma 4 agent.** Go/no-go around 20 Oct (MSK). Enter only if all three of these hold:
  - The Enveda CV harness and baseline are running.
  - A hosted Gemma 4 API proves close enough to the scored model to iterate cheaply, or a CV pass costs clearly under 8 GPU-h.
  - The spread of the leaderboard has grown beyond one-task steps.
  - Hard deadline for the decision: 25 Nov.

## What could change the decision

- **Enveda turns out not to be beatable.** If by about day 14 (around 14 Oct) our CV and one approved probe cannot beat the public-notebook plateau, and PubChem candidate retrieval (candidate recall on masks B and C) adds nothing, drop Enveda down the list and reconsider Gemma.
- **A new Featured competition appears.** If a medal competition with tabular data or a small-head model and 2–3+ months left launches in October, it would beat Enveda's late start. Recheck the list about 15 Oct, one light call.
- **ARC fork runs turn out to be cheap.** If a fork submission costs almost no GPU quota and a teammate is willing to handle it on their own account before 26 Oct, one fork submission in ARC-AGI-2 or ARC-AGI-3 becomes a reasonable zero-attention ticket. It is not a pick unless the user wants a lottery ticket.
- **Teammates reliably commit their GPUs.** This barely matters for Enveda. It would only make Gemma LoRA work slightly more realistic, and even then 12–16 GB cards are too small for a 31B model.

## Main risks (Enveda)

1. **Domain ramp-up.** Mass spectrometry and chemistry tooling (RDKit, InChIKey, adducts, timsTOF) are new to us, against likely expert teams from the CASMI community. Budget about 1 week of learning.
2. **Hidden class mix and small public LB.** Public covers about 130 molecules, and the mix of the three molecule types is hidden and may differ between public and private. Decide by the np-examples three-mask CV. Treat public-LB moves under about 0.02 as noise, and keep one CV-best final and one robust final.
3. **Offline engineering within 9 h.** A mass-filtered PubChem/COCONUT pool must be built on the laptop (a multi-hour job; the size, tens of GB, is an estimate) and published as a public Kaggle dataset to satisfy the external-data rule. Candidate scoring plus the ranker must fit a 9 h notebook with no internet.
4. **Crowd of notebook copies.** Public notebooks will keep improving and lift the bronze line, so own retrieval and ranker gains are mandatory, not optional.
5. **Process.** Kaggle API use stays light, and every submission needs the user's explicit approval.