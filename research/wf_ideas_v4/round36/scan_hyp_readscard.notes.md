# scan_hyp_readscard notes (round 36)
- 2026-09-29T08:13:44Z started; round36 folder created; no prior json.
- 08:14Z poll.log header 2026-09-29T08:08:16Z: 56657612 exp89p COMPLETE 0.956; 56656157 exp75 and 56656147 exp89r PENDING. CONTEXT 07:59Z line: P '-', L (7.03, 7.19] h (submit 00:46:36Z; headers 07:48:12Z PENDING / 07:58:14Z COMPLETE -> L_lo 7.027 h, L_hi 7.194 h; recomputed OK).
- Card v5 sha256 a134d5e4... (research/wf_ideas_v4/round29/finals_card_v5_ru.md) = the 02:53Z (4) sha8: unchanged since.
- Rules read: MORNING TABLE v1.1 (CONTEXT l.3931-3955), EXP75 PARTNER RULE v2 (l.3965), GAP RULE v2 (l.4011), freeze (9) (l.4234), 02:02Z (1)-(5), 02:53Z (1)-(5), 04:51Z P LATE 8.0 h, 07:23Z prep, 07:59Z read line.
- DIS code branch A recheck: dd = (d_R - 0.956) - (0.959 - 0.958) >= 0.002 AND d_R > 0.959 -> d_R >= 0.960; '-' iff d_R <= 0.955; '?' d_R 0.956-0.959. Matches the 07:59Z line.
- exp89t (K + DIS + CI) never built (defaults 15:43Z: no exp89t). exp89a (C6 + DIS + CI, no K) built 28 Sep 11:19Z, not relevant (no K).
- exp89s kernel vitaliineibauer/biohub-exp89s-k2cap6-k-dis225, dummy PASS 14:40Z 28 Sep, CSV 8956f46c6824, nodes 121,389 (-0.77% vs exp85a), 1,566 s.
- 08:2xZ e10 snapshot experiments/e10_watch/20260929T0813Z.txt: our row rank 139, 0.959, count 54 (exp89p completion), 16/20 in 0.959 block (124-143), >=0.960: 123, total 3,987; 0.957 block 164-223 (silver #199), 0.955 block 362-465 (bronze #398). Kernel lists no change.
- IDEAS checked: I-484 (exp89s in-plan), I-486 (exp89t default NO), I-506 (blind exp89s refuted 27 Sep), I-532 (V_pub = max display upheld; winner's-curse rule retired), I-509, I-450. R30M-7 (round30) refused using an UNUSED slot for exp89s as winners-only violation.
- MC (scratch /tmp/mc36.py, 4M draws; conditioned on exp87a disp 0.959, exp89p disp 0.956; u85a~U(.9575,.9585), CI~N(.001,.0008), SEC~N(-.001,.0015), DIS~N(0,.0010-.0015), interaction noise .0003-.0005):
  P(exp89s becomes V_pub: >=0.960 or 0.959 & > u87a [UP upper bound]) = 0.18-0.26 (>=0.960 part 0.08-0.17); P(exp89r becomes V_pub) = 0.04-0.12.
  E[u89s-u87 | win] = +0.0006..+0.0010; E[DIS-CI | win] = +0.0005..+0.0008.
  By exp89r display d_R: P(d_R) .955 .07-.12 / .956 .19-.24 / .957 .24-.34 / .958 .21-.25 / .959 .09-.12 / >=.960 .02-.07; P(89s wins|d_R) .001-.006 / .02-.04 / .10-.15 / .29-.38 / .57-.66 / .83-.90.
  Gate d_R >= 0.958 captures 77-84% of all exp89s wins; the extension cells {0.958, 0.959} add ~0.14-0.16 switch probability over the logged A-M2 (d_R >= 0.960 only).
- Timing: exp89r submit 00:05:28Z + L (9.30, 9.48] h -> header 09:23-09:34Z; exp89s sent 09:35Z + 7.03-7.19 h -> read 16:37-16:47Z; sent 08:30Z -> 15:32-15:42Z; admit edge 10:50Z send -> ~17:55-18:05Z; all before 18:37Z card.
- 2026-09-29T08:21:33Z final JSON written: research/wf_ideas_v4/round36/scan_hyp_readscard.json (8 findings); MC script copy in session scratchpad mc36.py.
