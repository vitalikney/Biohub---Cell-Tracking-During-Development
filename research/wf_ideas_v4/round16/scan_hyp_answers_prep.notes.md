# scan_hyp_answers_prep notes (round 16)
- 2026-09-27 08:31Z start. No prior JSON existed; folder round16 created.
- Sources read: CONTEXT.md l.2599-2881 (RESUME 22:46Z 26 Sep + all 27 Sep entries through 07:41Z D2 read);
  round15/REPORT.md; round15/report.json R15-A1..A8 (R15-A2 = brief text sent ~07:45Z, questions: Q1 class C, Q2 E10 v2, Q3-5 exp71/exp72 Q1-Q3, Q6 last-submit cap).
- D2 (07:41Z): exp70b 56592350 = 0.954 U4 (attributable UP, 6 TeamIds passed), ledger (7.41,7.58] h, insertion gate did NOT fire; not V* (<0.955) -> pair {#37,#38}; SELECTED 2/2 07:41:28Z.
- 08:35Z FACTS: experiments/e10_watch/20260927T0831Z.txt: our rank 255, 0.954, 8th of 113 in the 0.954 block (248-360) [05:32Z: 17th of 102] -> consistent with exp70b's attributable UP; >= 0.955: 247 (+8 in 3 h); P2 largest group 1; NEW kernel mtoshidesu/testbiohub-lf-dctta020-sectta1 (sjlee lf-dctta family, not x138) -> notify only; amanatar V6 status unchanged.
- ledger (uncommitted, 08:30:46Z): 43/44 PENDING, L > 3.03/3.04 h at 08:30:44Z; 9.0 h clocks 14:28:13Z/14:28:22Z; earliest terminal ~12:15-12:20Z (exp70a L 6.87 h).
- E10 v2 text: CONTEXT l.2352-2360 (V2 scope = successors FIRST SEEN after the OK; V4 pair {PORT, #37}, 'never drop #37'; V3 last port submit 29 Sep 02:00Z).
- exp71: experiments/exp71_secft_all (NEVER_SUBMIT.md; kernel id vitaliineibauer/biohub-exp71-secft-all; T4, internet on; push blocked by classifier 26 Sep 21:54Z, CONTEXT l.2539-2544).
- exp72 pipeline: research/wf_ideas_v4/reach0955/r_retrain.json RT-2 steps (dataset create --dir-mode zip; build cmd with --patch secswap; manifest path /kaggle/input/datasets/vitaliineibauer/biohub-secft-all-v1/ARTIFACT_MANIFEST.json); builder guards tools/build_probe_kernel.py l.2552-2575.
- exp72 governance: CONTEXT l.2722-2746 (R13-A3: class C unless Q3; eligibility COMPLETE, L_hi <= 8.0 h, display >= 0.956 and > V*, G2 >= -0.0005 by 29 Sep 12:00Z; dummy gate list).
- G2 needs a SECFT_PREFIX cell that does not exist (WATCHLIST I130) + a second ~4 GPU-h run + a GPU lab re-run on 39 6bba clips.
- R8 cap: R12-A3 (c) CONTEXT l.2521-2524: last submit 29 Sep 02:00Z default; 11:00Z scores ~18:30Z.
- Class-C table: R15-A1 (4) CONTEXT l.2833-2853 (letter counts pre-registered only if logged before the first poll.log header with 43 or 44 terminal).
- Slot priority R15-A1 (2): E10 port > unchanged resubmit of an ERRORed finals-relevant file > exp72 (yes only) > empty; 27 Sep: 2 slots left.
- CONFLICT spotted: E10 v2 V4 'never drop #37' vs a user yes to exp70b replacing #37; E10 v1 P6 pairs PORT with #37 too. Needs a one-line reading ('#37' = the insertion final currently ticked).
- CONFLICT 2: class-C (b) drops #38 while a PORT would drop #38 too -> both-insertion + port collisions; propose slot table (no-insertion slot: PORT > #38; insertion slot: user-chosen).
- Timeline exp72 from yes time T: push T+5m; exp71 done T+4.5 h (range 2.7-6 h); dataset ready T+4.9 h; exp72 dummy done T+5.6 h; submit ~T+5.8 h; score ~T+13.3 h (K2-like latency 7.4-7.6 h).
- 08:43Z JSON written (11 findings R16AP-0..10); complete.
