# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 7: state as of 2026-09-26 ~09:05 UTC, git HEAD 42d1a55 (08:58Z; the three curators read up to 4d0c477/4790f1f) plus the untracked `research/wf_ideas_v4/round7/`. Previous: curation 6 (~06:30 UTC, 2f6ec9d). All times UTC; every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY by 29 Sep 20:00. Sources: `CONTEXT.md` §1; PRE-REG v3 l.1576-1736 (§f l.1707-1736); v4 l.2058-2069; SCORE READ l.2070-2081; option b l.2082; wave check l.2083-2095; rules check l.2096-2109; overlap-consensus line + PAUSE l.2110-2129.

## STATE IN 10 LINES

1. **Scored:** #37 K2 exp58 (56563521) = **0.954**, clean, L in (7.36, 7.54] h; #38 twin exp58n (56563534) = **0.953**, L in (6.69, 6.87] h; both R5(a). READ TABLE row 3 -> **finals #37 + #38**. Sources: `CONTEXT.md` l.2070-2081; `experiments/RESULTS.md` l.70-71; `DECISIONS.md` §1, §2.
2. **Rank #183 of 3,923 at 08:22Z** (#185 at 08:38Z), 12th of 87 in the 0.954 block, silver line ~11-13 ranks below and closing; 0.955: 46 teams, 0.956: 26. Sources: `CONTEXT.md` l.2083-2088; `research/wf_ideas_v4/round7/report.json` new_facts 1; `FACTS.md` F-LB-02 [c7].
3. **Base** = x138 + safetail (C01) + lowrefine + gated DaughterNet insertion (K2); insertion transferred to the LB again (+0.001; "2nd" per IDEAS I-062, "3rd" per FACTS §7 - count unreconciled), lowrefine and C01 invisible at 3 decimals. Sources: `IDEAS.md` I-001 l.101, I-062, I-036; `FACTS.md` §7 [c7].
4. **Finals ticked: 0 of 2** (API group=SELECTED = 0 at 08:37:15Z, page 0/2). With no tick, auto-select from the 0.954 tie (#37, #35, P36) may pick P36 + #35 (forbidden). Sources: round7 `report.json` new_facts 4, R7-A1; `FACTS.md` F-RUL-12/13; `WATCHLIST.md` W54.
5. **Running now:** no submission pending; 3 slots on 26 Sep unused; poller PID 20052 alive (last header 08:54:28Z) and must stay up to 29 Sep 20:00. Full research rounds every ~2.5 h to R8 (option b, user 08:21Z; "давай б" relayed again). Sources: `experiments/lb_poll/poll.log` l.4227; `CONTEXT.md` l.2081-2082; round7 `report.json` R7-A6.
6. **NEW after the curators (08:58Z): OVERLAP-CONSENSUS candidate line (K6 = K2 + overlapcons; gates G-A, G-P bit-probe (1 slot), G-B, G-D, G-LB), PAUSED by the user until this curator report.** Nothing built. Its ledger status is stale: I-208 still reads "refuted by R9". Sources: `CONTEXT.md` l.2110-2129; `IDEAS.md` l.391; commits 539ea8b, 42d1a55.
7. **E10 watch** (public x138 heir >= 0.956): NOT met at 08:27Z (overnight 0.955/0.956 wave has no public source). P(trigger) ~5-10%. PORT RULE P1-P8 exists only in round7 `report.json` e10_port_rule_text and `DECISIONS.md` §2f. Sources: `CONTEXT.md` l.2083-2095; `FACTS.md` F-LB-10, C-48, C-55.
8. **Round 7 closures on x138** (research files only): gap LAP + sandwich (TP 5 / FP 458), z-split (1 reachable merge), headroom family (value/LB/R8), forkmid = the one power-limited closure. Rules check: leaked CSVs not allowed; R7/R9 are team policy, not Kaggle rules. Sources: `DECISIONS.md` §1b G23-G26; `FACTS.md` F-TRN-28/29, F-RUL-14, C-57.
9. **Next decision points:** tick now; overlap-consensus resume or not (user); round 8 ~11:00Z; records by 12:00; E10 yes before ~19:00Z; R8 cutoff 27 Sep 12:00; S14 28 Sep; last E10 trigger 29 Sep 00:00 / port submit 02:00; tick checks 28 Sep evening, 29 Sep 12:00 + 18:00; ticks final 29 Sep 20:00. Sources: `WATCHLIST.md` NEXT 24 H l.60, LATER l.80; `CONTEXT.md` l.1611-1617, l.1671-1672.
10. **Ideas ledger:** 265 ideas: lb-tested 41, lab-tested 20, refuted 153, deferred 22, in-plan 28, open-untested 1. Strict orphan I-233; at risk I-229, I-232, I-243, I-256, I-257, I-259, I-262. Source: `IDEAS.md` l.9, l.11, ORPHANS l.397.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by the curator workflow `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md`: this page. `research/KNOWLEDGE/CHANGES.md`: delta per curation (v4, 2-7).
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json`: I-001..I-265 in 12 clusters (FINALS l.37, BASE l.72, RUN l.95 ... TESTSET l.385), delta l.11, ORPHANS l.397; per-ID log in `ideas.json` meta.curations.
- `research/KNOWLEDGE/FACTS.md`: §1 metric .. §7 lab-to-LB transfer (l.147); CONTRADICTIONS l.181 (new C-48..C-57).
- `research/KNOWLEDGE/DECISIONS.md`: probes P01..P38 (§1 l.21), lab gates G01-G26 (§1b l.117), finals (§2 l.165), READ TABLE + v2-v4 (§2b-§2e, all in CONTEXT), proposed E10 PORT RULE (§2f l.316), R1-R10 (§3 l.339).
- `research/KNOWLEDGE/WATCHLIST.md`: OVERDUE l.48, NEXT 24 H l.60, LATER l.80, INSIGHTS AT RISK l.114 (W, T, I IDs).
- Curator logs: `research/KNOWLEDGE/_curation/{v4,2,3,4,5,6,7}/`.

Key sources (repo root):
- `CONTEXT.md`: single source of truth; newest entry ends at l.2129, just above "## 9. Literature" (l.2130). Newest RESUME POINT l.2006 is pre-score (stale, C-56).
- `experiments/RESULTS.md` (every LB probe; P37/P38 l.70-71). `experiments/lb_poll/poll.log` (10-min poll), `experiments/lb_poll/ledger.md` (latency bounds, R5).
- Finals kernels: `experiments/exp58_x138_safe_lowref/` (K2, #37), `experiments/exp58n_x138_safe_lowref/` (twin, #38); `experiments/*/probe.json` says what each changed.
- `experiments/exp60_trainlab/results.md` (x138 lab verdicts); `experiments/runtime_step0/` (hidden-N bound).
- `tools/build_probe_kernel.py` (bases exp39/x138 only, l.99; safetail needs --base x138, l.2026-2027), `tools/runtime_ledger.py` (`--print`), `tools/dummy_gates.py`, `tools/official/src/tracking_cellmot/metrics.py` (edge FP rule l.157-195).
- `research/wf_ideas_v4/round7/report.json` (untracked, 08:45Z): R7-A1..A8, `e10_port_rule_text`, `resume_point_text`, `records_text`, `tick_check_cmd`, `report_md_ru` (no REPORT.md yet).
- Overlap-consensus design: `research/wf_ideas_v2/r2_research_overlap-consensus.json`; round prompt `experiments/workflows/biohub-research-round.js` (l.20, l.35-36 stale).
- `research/wf_ideas_v3/FINAL_REPORT.md` (pre-reg source); `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md`, `TEAM.md`; intel `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`, `research/survey_*.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-227 / I-258 | Finals tick #37 + #38; verify by API SELECTED + one page read | in-plan, top alert: 0/2 at 08:37Z | `IDEAS.md` l.57, l.69 |
| I-208 | Overlap consensus across overlapping test crops (K6 candidate) | ledger says refuted (R9); CONTEXT 08:58 = candidate, PAUSED; needs the user's word | `IDEAS.md` l.391; `CONTEXT.md` l.2110-2129 |
| I-256 / I-262 | E10 PORT RULE P1-P8 (pair {port, K2 #37}); E10 dry run (no push) | at risk: not in CONTEXT; one conditional yes before any trigger; dry run in round 8 | `IDEAS.md` l.90-91; `DECISIONS.md` §2f |
| I-257 | Post-score RESUME POINT + MEMORY.md lines | at risk: with the next CONTEXT write | `IDEAS.md` l.68 |
| I-259 / I-265 | Round focus text (R8 hard line, closures, drop "~4 h headroom"); cadence option b | at risk: before round 8 (~11:00Z) | `IDEAS.md` l.381-382 |
| I-229 | 29 Sep tick checklist + calendar reminders 12:00/18:00 | at risk: reminders unconfirmed (W50) | `IDEAS.md` l.59 |
| I-232 / I-243 | round7 REPORT.md; ledger text fix (only if an E10 port is built) | at risk | `IDEAS.md` l.378, l.125 |
| I-233 | Poller logs error_description | strict orphan; close with one line unless a port is submitted | `IDEAS.md` l.119 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/7/{ideas,facts,watch}.json`, plus CONTEXT after 4790f1f)

1. [now] **Finals not ticked.** User ticks exactly #37 56563521 ("probe 37: exp58") + #38 56563534 ("probe 38: exp58n"); verify with round7 `tick_check_cmd` (must print [56563521, 56563534]) + one page read; log "FINALS TICKED 2/2". Never tick #35, P36, #34. Sources: `CONTEXT.md` l.2078-2080; `WATCHLIST.md` W54; `IDEAS.md` I-227, I-258.
2. [now] **Overlap-consensus line waits on the user (paused for this report).** Not assessed by the three curators. Inputs for the call: design ceiling +0.004..+0.006 on a 44b6-type embryo, 0 on 6bba-type (l.2113-2114); the 08:49 check found it rule-legal but small (+0.0005 expected, needs overlapping hidden crops) and "too tight for R8" (l.2107-2109); G-P spends 1 of 3 26 Sep slots; K6 must be submitted by 27 Sep 12:00; if K6 replaced K2 as F1, the E10 pair {port, K2 #37} (§2f) would need restating. Ledger I-208 / F-RUL-08 not yet updated. Sources: `CONTEXT.md` l.2096-2129; `IDEAS.md` l.391; `FACTS.md` F-RUL-08, C-57.
3. [now] **Correct the plan sent to the user** (~08:2xZ): E10 watch runs to 29 Sep 00:00 (last port submit 02:00), not 27 Sep 12:00; P(trigger) ~5-10%, not 15-20%; rank #185, not 162. Full rounds end at R8 (option b); light CLI E10 checks every ~6 h after. Sources: `FACTS.md` C-48; `WATCHLIST.md` W74; round7 `scan_plancheck.json` PC7-01. (Curators split now/today; INDEX sends it with the tick message.)
4. [today] **E10 PORT RULE not in CONTEXT.** A verbatim port cannot carry C01, so §f(iii) blocks it without the rule. Paste `e10_port_rule_text`, ask ONE conditional yes before ~19:00Z and before any trigger, log with `date -u`. Sources: `DECISIONS.md` §2f; `FACTS.md` C-55, F-MOD-21; `WATCHLIST.md` W69.
5. [today, by 12:00] **Round 5-7 records into CONTEXT** (`records_text`, R6-A6, node-miss FACT with the skeptic wording, forkmid power-limited, CONTEXT l.22 "GT still moving", B5 l.196) and save round7/REPORT.md; commit as the user. Sources: `WATCHLIST.md` W57, W60, W75; `IDEAS.md` I-232.
6. [today] **Stale RESUME POINT and MEMORY.md** (l.8 lists closed riders; l.9 points to 25 Sep 10:20). Paste `resume_point_text`. Sources: `FACTS.md` C-56; `WATCHLIST.md` W70; `IDEAS.md` I-257.
7. [today, before ~11:00Z] **Round prompt** still invites "~4 h headroom", lacks the R8 line and round-7 closures, calls R9 a Kaggle rule. Sources: `experiments/workflows/biohub-research-round.js` l.20, l.35-36; `WATCHLIST.md` W71; `FACTS.md` C-53, C-57.
8. [before-finals] **Durable 29 Sep reminders** (12:00, 18:00) unconfirmed; API tick checks 28 Sep evening, 29 Sep 12:00/18:00. Sources: `WATCHLIST.md` W50; `IDEAS.md` I-229.
9. [info] **Keep poller PID 20052 to 29 Sep 20:00** (W6 stop condition met, but an E10 port or K6 needs coverage); last header < 15 min before any submit. Sources: `FACTS.md` C-50; `WATCHLIST.md` W19/W73.
10. [info] Insertion cost on LB <= 0.85 h vs 1.95 h dummy estimate (C-51, post-deadline lesson); overnight LB burst = daily quota reset, not an E10 signal; I-233 orphan; friend A card (W03), ext_* untracked (W05), NEXT_RESEARCH (W26). Sources: `FACTS.md` C-51; `WATCHLIST.md` OVERDUE l.48, INSIGHTS l.114.

## HOW TO USE

- "Score of probe N, what it changed, why dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "Which files are the finals, and what if something new appears?" -> `DECISIONS.md` §2 and §2f, then `CONTEXT.md` l.2070-2081 and l.2110-2129.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b (G01-G26), then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this; is it Kaggle's or ours?" -> `DECISIONS.md` §3; `FACTS.md` §5 (F-RUL-14); rule text `CONTEXT.md` l.1576-1736, l.2096-2109.
- "Was idea X tried?" -> search the alias in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md` and its CONTRADICTIONS.
- "What is next / overdue / at risk?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. Anything newer than ~09:05Z 26 Sep -> tail of `CONTEXT.md` §14 and `experiments/lb_poll/poll.log`.
