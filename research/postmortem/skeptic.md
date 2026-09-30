**Skeptic verification: five post-deadline lenses checked against the repo files**

Scope: I re-parsed `experiments\lb_poll\_final_subs.csv` (57 rows, header on l.1; data on odd lines 3–115) and recomputed every correlation with a scratch script at `C:\Users\vital\AppData\Local\Temp\claude\...\scratchpad\sk.py`. I also checked the cited lines in CONTEXT.md, RESULTS.md, FACTS.md, risk_audit and round9/LESSONS_draft.md. I made no Kaggle calls. Numbers from the private leaderboard web page and from other teams' write-ups (the "leaders" lens) are not in any repo file and are marked as not verifiable.

## (a) Confirmed key numbers

1. **Table A matches the CSV on all 57 rows** (refs, CSV line numbers, public and private scores). Examples:
   - exp89t l.3: 0.960/0.920
   - exp87a l.11: 0.959/0.921
   - #37 l.39: 0.954/0.920
   - #38 l.37: 0.953/0.917
   - exp70j l.27: 0.954/0.922
   - x138 l.45: 0.953/0.917
   - P5 l.105: 0.943/0.914
   - P26 l.61: 0.911/0.894
   - Probe 18 appears twice (l.79 ref 56252420, l.77 ref 56252506). RESULTS l.51 names 56252506 as the accidental duplicate.
2. **Insertion pairs** give public +1/+1/+1 and private +5/+3/+3 (CSV l.57/59, l.43/45, l.39/37).
   - The lab CONFIRMATION number is +0.0019, 90% CI [-0.0007, +0.0050] (CONTEXT l.1305-1306).
   - The pre-registered reads C1=C2=+3 give outcome (iii) "promote" (CONTEXT l.2575).
   - CONTEXT l.4768-4771 records the same numbers.
3. **Knob contrasts on the x138 base:**
   - cap 6 +2/0, cap 8 +1/0, cap 12+FC2 +1/-1, K (P50 vs P45) +2/0.
   - CI +1/0, +1/+1 and +1/0; DIS +1/-1.
   - Sums: public +10, private -1.
   - Stack: exp87a vs #37 is +5/+1; exp89t vs #37 is +6/0.
4. **DeepCenter (DC) dose on the K2 base**, private: 0.30 → 0.918 (l.31), 0.25 → 0.920, 0.225 → 0.921 (l.25), 0.20 → 0.922 (l.27). Public: -5, 0, 0.
   - Lab dc0.20 on 6bba = -0.0008 (CONTEXT l.2804-2805).
   - The lab's best threshold (t*) was 0.30, and the gate failed (CONTEXT l.1930).
5. **Losers that public hid:**
   - DivNet veto: 0/-4 (l.73 vs l.87). Lab +0.0023 (RESULTS l.53).
   - Edge filter: 0/-1 and -1/-2 (l.55, l.53 vs l.73). Lab +0.0162 and +0.0095 (RESULTS l.62-63).
   - The T set is 7 negative vs 2 positive (CONTEXT l.2594-2595). H-E holds (E = +5, +3, +3, +3).
6. **Private gains that public hid or reversed:**
   - P5 -2/+7 (l.105 vs l.111); RESULTS l.37 dropped it.
   - P13 -7/+3, P16 -9/+2, P12 -3/+1.
   - CONTEXT l.294 had closed Z-flip "for good".
7. **Correlations reproduced:**

   | Set | n | Spearman |
   |---|---|---|
   | All | 57 | 0.837 (Kendall 0.672, Pearson 0.911, slope 0.64) |
   | Dedup | 56 | 0.840 |
   | exp06 era | 9 | 0.075 |
   | TTA era, dedup | 22 | 0.027 |
   | x138 family | 22 | 0.487 (p 0.021, slope 0.25) |
   | x138 without DC 0.30 files | 20 | 0.299 |
   | Public ≥ 0.954 | 18 | -0.042 |
   | Public ≥ 0.950 | 22 | 0.273 |
   | Pre-x138 | 35 | 0.506 |

   - Mean private: 0.9201 for the 11 files at public ≥ 0.955, 0.9204 for the 7 at 0.954.
   - Histogram: 15 files at 0.920, 3 at 0.921, 1 at 0.922.
8. **Finals decisions:**
   - Decision B, 13:34Z: promote only at ≥ 0.960 (CONTEXT l.4607-4617).
   - Re-tick at 19:07:17Z (l.4755), 53 minutes before the 20:00Z tick limit.
   - П3 tick at 12:37Z (l.4579). {#37, #38} ticked 26 Sep, API 20:04Z (l.2599-2600).
   - DIS estimate 0.000 ± 0.002 (l.4480). Dummy lab +0.00089, of which +0.00048 is the node term (l.4525).
   - 17 probes after the 26 Sep tick: 4 above #37, 10 equal, 3 below. All pair counterfactuals are 0.920 or 0.921.
9. **Risk audit:**
   - 0.79/0.58 base; 0.72/0.42 with cap 6 and K = 0; 0.56/0.19 in the Cyrus case (answer_ru l.21-23).
   - Scenario (d) 0.85/0.59, the "#346 with cap 6 + CI = 0" scenario, and "#37 alone ~#489" (skeptic.md l.33, l.39).
   - The +0.05 bronze hedge value (results.json [3].points[5]).
   - The audit itself said to promote exp89t at ≥ 0.960 (answer_ru l.35).
10. **Other:**
    - K dummy: 0.92184 vs 0.92052 (CONTEXT l.4046).
    - cap 6 lab -0.00057 (CONTEXT l.2545-2546, F-TRN-42).
    - In-sample insertion +0.0065 (F-TRN-14/20).
    - 43 report.json files in 44 round folders (R42 missing).
    - 239 of 328 dated CONTEXT entries fall on 26-29 Sep (lines 2006-4761, about 57%).
    - 672 commits.
    - Submissions per day match the CSV.
    - Private result #346 / 0.920 / public #136 (CONTEXT l.4762-4776).

## (b) Wrong or unsupported claims, with the correct value

1. **"#37 alone would have medalled" (calibration).** Unsupported.
   - #37 and exp89t both display 0.920. The leaders lens puts the 0.920 block at about #336-#413, with bronze line #402 inside it (web data, not in the repo).
   - #37 alone could rank anywhere in that block. Nobody knows which of the two finals produced #346.
   - Correct statement: unresolved, probably a medal but not certain. The same applies to "{#37, #38} = the actual result" at rank level.
2. **"Public understated the insertion 3-5x" (levers, calibration).** This is a ratio of displays only.
   - The public true delta is in (0, +0.002) and the private one in (+0.002, +0.004) for the x138-base pairs.
   - Resolved: private > public. The ratio itself is unresolved (from about 1 up).
3. **"Public veto: 8 of 9 resolved cases agreed" (calibration lesson).**
   - Their own table gives 7 of 9 (Z-flip and secondary exp23 flipped).
   - Across all public-negative pairs in Table B with non-zero private: 15 kept sign, 5 flipped (P5, P6, P12, P13, P16).
4. **"Veto only large drops (≥ 0.004), which carried in sign" (decisions lesson).** False outside the x138 family.
   - Of 8 public drops of ≥ 4 thousandths, 5 kept sign, 2 flipped (P13 -7/+3, P16 -9/+2) and 1 went to 0 (P7 -16/0, l.101).
5. **"Only learned components with held-out evidence carried … x138 coordinate head +0.003" (process); "cross-embryo localisation +" as a lab sign (calibration).**
   - The repo has no held-out lab for the V1284 head. Its only support was x138's public +0.007 (RESULTS l.64; CONTEXT l.1382-1395).
   - Correct: a learned model, supported only by public. It still carried (+2 public / +3 private, l.51 vs l.57).
   - The calibration tally for the lab should drop this row: lab 5 right / 11 wrong.
6. **"The insertion is the OOF-backed lever" (all lenses).** Incomplete.
   - It failed its own pre-registered gate: added-fork precision 27% < 31% (CONTEXT l.1307). The audit repeated this (CONTEXT l.4601).
   - The OOF was on an older config and used held-out videos, not a held-out embryo.
7. **Calibration uses labs that were not sign reads:**
   - K dummy: CONTEXT l.4046 says "sanity only, not a sign read".
   - CI: the refiner lab was chosen over the dummy lab (-0.0055, F-TRN-60(b)). With the dummy lab, CI counts as a lab miss.
   - Secondary exp23: one lab bed gives +0.0033 (RESULTS l.48, exp32 0.8969 vs exp30 0.8936), which would count as a lab hit. Friend B's bed gives -0.0132 to -0.0146 (RESULTS l.93).
   - The 6/11 vs 11/3 tally shifts by 1-2 depending on which lab is picked. The direction (public beats in-sample labs on sign) survives.
8. **"Public ≥ 0.935: n = 51, Spearman 0.790" (levers).** Correct values: n = 52, Spearman 0.787.
9. **Correlations read as proof.** "Within-era Spearman ≈ 0 means public carries no information" (levers, calibration, leaders) goes too far.
   - In the n = 18 set, 13 of 18 private displays are 0.920, so the -0.04 comes from 5 files and is a rounding artefact.
   - Correct: undetectable at 3-decimal resolution.
   - In the exp06 era, Pearson is 0.77 even though Spearman is 0.075. Large drops (P10) did transfer.
10. **"Post-processing and structural public negatives keep sign; weight/TTA swaps flip" (levers).** Weakly supported.
    - P6 (min track length, a post-processing knob) flipped -2/+1, and levers itself lists it among the flips.
    - Weight swaps P10 (-25/-14) and P17 (-4/-2) kept sign.
    - Rough count: 3 flips in 8 swaps vs 2 in about 11 post-processing changes. The sample is too small for a type rule.
11. **"The largest private gain we discarded was a weight/TTA swap" (levers).** Wrong: P5 is a detection-mixing weight knob, not a model swap.
12. **"8 days had 0 submissions" (process).** Between 3 and 29 Sep there were 12 zero-submission days: 4, 5, 8, 9, 12-14 and 16-20 Sep.
13. **"231 commits after 25 Sep 20:00Z" (process).** git gives 216 by both author and committer date.
14. **"Duplicate submission, CONTEXT l.208" (process).** Wrong citation: l.208 is the B27 hygiene row. The duplicate is recorded at RESULTS l.51.
15. **"DC 0.20 could not be picked / neither predictor saw it" (levers, calibration, decisions).** Overstated.
    - DC 0.20 was the default of our whole pre-x138 stack: RESULTS l.43 (sjlee "DC div thr 0.20"); CSV l.51, where probe 31 says "DeepCenter stays 0.20".
    - Public showed 0.20 = 0.25 on two stacks (RESULTS l.82; CONTEXT l.2852).
    - The x138 switch changed it to 0.25 without any check. A rule of "keep the incumbent value on a public tie" would have kept 0.922-level files.
16. **"CI +0.001 / DIS -0.001 unresolved" (leaders); "true differences between -0.002 and +0.002" (process).**
    - A one-step display difference fixes the sign: exp89t < exp87a strictly.
    - Only the size is unresolved. The calibration lens states this correctly.
17. **"Public rank #268 → #136" (decisions).** #268 is from 27 Sep 13:14Z (CONTEXT l.2997), after the drift. At the 26 Sep tick the rank was about #155-#210 at 0.954 (LESSONS_draft l.41; CONTEXT l.2048).
18. **Process summary garble.** "Seven of them agree with the private sign, two show a -0.001 read" is not supported by any count. The file-supported version: of the 8 x138 knob contrasts, 6 read 0, 1 read +1 and 1 read -1 on private.
19. **Levers "+10 / -1" sum.** It depends on the choice of contrasts: CI is counted 3 times and K once. Adding K on the CI base (exp87a vs exp79a: +2/+1) gives +12/0. The stack contrasts (+5/+1, +6/0) are the non-overlapping measure.
20. **Leaders: yu4u "lost about 0.010" vs their own table "-0.011".** Internal mismatch; not verifiable from the repo.

## (c) Contradictions between lenses, and which side the files support

1. **"#37 alone medals" (calibration) vs "bronze depended on the tie order inside the 0.920 block" (leaders).** Leaders' caution is right. CONTEXT l.4766 records only "56 places of margin" by rank; it has no score margin.
2. **Signs of one-step displays.** Leaders and process call them "unresolved"; calibration says "the sign is fixed". Calibration is right.
3. **Where to invest.** Process says the detector ("the gap to 0.977 is there"). Leaders' own data say the 12th and 18th places kept the public detector and reached 0.946 and 0.941 with learned division/link models (external, not verifiable).
   - Our files favour downstream learned models:
     - DaughterNet insertion +3/+5 private and the V1284 head +3.
     - Our own scratch detector as secondary: -25/-14 (l.95). Its local best was 0.68 (RESULTS l.89-91).
4. **x138 coordinate head.** Process calls it "held-out evidence"; levers and calibration call it a "cross-embryo check". The files show public-only support (see b5).
5. **Public veto strength.** Calibration says 8/9 and decisions says "≥ 0.004 drops carried". Levers' count of 5 pre-x138 flips is what the CSV supports (see b3, b4).
6. **Did the x138 switch add private?** Process says 0 (probe 31 was already 0.920). Levers says x138 verbatim vs our port is +3/-3, confounded.
   - Both confounded comparisons fit the files, if one also accounts for DC: P31 carries DC 0.20 (+2 on K2) and the veto (-4 on sjlee).
   - A rough additive split gives x138's non-head stages about -0.002 on private. That split is unresolved.

## (d) Important lessons the lenses missed

1. **A mechanism links all the "more forks paid on private" results.**
   - Break-even precision for an added fork is J/(1+J) (CONTEXT l.1307).
   - Public division Jaccard ≈ 0.36 (RESULTS l.59), so break-even ≈ 0.265. P26 gives private division Jaccard ≈ 0.22 (0.916-0.894), so break-even ≈ 0.18.
   - The insertion's 27% precision is break-even on public, which is why it showed +0.001 there (l.1308 predicted "~0" on public). On private it is clearly positive.
   - The same arithmetic explains DC 0.20 at +2 (96 vs 75 forks on the dummy clips, CONTEXT l.2807) and DC 0.30 at -2.
   - Lesson: judge fork-adding levers by precision against each embryo's break-even, not by the public display.
2. **The lab predicted the density dependence.**
   - The in-sample insertion gain sat on sparse clips: Q0 +0.0246, sparse half 8 TP / 3 FP vs dense half 1 TP / 3 FP (F-TRN-14).
   - F-TRN-20 warned only about a dense private embryo.
   - The leaders lens reports (from yu4u's write-up, external) that the private embryo is sparser. That fits the +3 to +5.
   - Lesson: stratify lab reads by density and weight them by the likely test density.
3. **A narrowly failed gate was the right call to override.** The one lever that carried had failed its pre-registered lab gate. That gate's precision bar was implicitly tuned to the public embryo's division Jaccard. Gates tied to one embryo's J reject levers that help on other embryos.
4. **A base switch carries silent default changes.** Adopting x138 moved DC 0.20 → 0.25, a public tie that cost about 0.002 on private. Diff every inherited default against the incumbent. On a public tie, keep the incumbent value.
5. **Which final set our rank is unknown.** A post-mortem that attributes #346 to exp89t is also unsupported.
6. **Last-minute swaps: keep the demoted file.** The promotion came 53 minutes before the tick limit, at +1 public on a lever with no off-public check (decision B). The lenses mention the hedge; the concrete rule is: when you swap in a +1 public file, keep the demoted file as partner. {exp89t, exp87a} = 0.921. The audit's cap-6/K hedge never paid, because those levers came out at 0, not negative.