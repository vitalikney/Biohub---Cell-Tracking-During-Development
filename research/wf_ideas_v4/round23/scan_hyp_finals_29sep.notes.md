# round23 scan_hyp_finals_29sep notes
- 2026-09-28T04:01Z started; no prior json in round23 (folder created). UTC now 04:01Z; W1 47/48/49 PENDING per poll.log.
- Read: CONTEXT tail (l.3100-3437), round20/21/22/16 REPORT.md, r21w-8 skeptic (fixes a-g for the finals card ranges).
- Forecast method source: scratchpad r21/mc21.py (= r20 mc20.py + cap12/CI/SEC terms); r21 numbers in round21/scan_hyp_w2_w4_plan.notes.md.
- 04:10Z LB 04:01:06Z download (experiments/e10_watch/20260928T0400Z.txt): 3,961 teams; ours #172 CSV rank / 163 = 1+strictly better; 10th of 59 in 0.956 block (ranks 163-221); >=0.955 308, >=0.960 95, 0.954 130, 0.953 420.
- Existing finals card = I-406 / R21-A9 (iv) Russian text + R22-A4 (A) balanced CI caveat (round21/report.json, round22/report.json). Letter (b) 11:09:39Z = {V*, #37}; user 20:33Z 26 Sep: one public-aimed + one private-aimed (default #37). I-092: MC never decides (ranges are info only).
- 04:12Z MC re-run: scratchpad r23/mc23.py (imports r21/mc21 + r21/mc20 unchanged; field re-based to 04:01Z counts, HOURS 44, own row removed from 0.956). Output scratchpad r23/mc23_out.txt.
  base (seed 11/7/23): A{#37,#38} .51/.11; P1{exp70g,#37} .66/.38; P2{exp70g,#38} .51/.35; P3{exp70g,exp70b} .68/.40; P15{exp70b,#37} .59/.18; B{exp70b,#38} .53/.16; P6{exp78a,#37} .66-.67/.41; P7{exp78a,exp70g} .57/.42; P8{exp78b,#37} .69/.42; P16{exp78b,#38} .46/.37. Seeds within +-0.01.
  range over scenarios (qpub0, qpub_hi, overfit, central, inspes, qpub0_pes): P1 bronze .50-.76 silver .22-.47; A .34-.66 / .035-.23; P2 .34-.59 / .19-.42; P3 .53-.78 / .25-.50; P6 .48-.76/.22-.50; P8 .47-.79/.19-.54.
  single #38 bronze 0.000 in every scenario (e=0 ties sit mid copy block, rank ~439-858 >> bronze ~#400): #38's hedge value for bronze is 0 in this model by construction.
- 04:20Z sensitivity scratchpad r23/mc23b.py (forkmid mean FMU, CI mean): P3{exp70g,exp70b} - P1 = +0.024 (FMU +5e-5, mc20 prior) / +0.012 (FMU 0: pure variance option value) / -0.008 (FMU -1e-4). CI stacks base: P13{exp79a,#37} .69/.41 (CI +2e-4), .64/.33 (CI -5e-4); qpub0 .57-.62; P14{exp79a,exp70g} .54-.59 (own parent -0.10); P9{exp83a,#37} .67-.69.
- Refs for tick text (poll.log): #37 56563521 26 Sep 00:02:12Z 'probe 37: exp58 = K2 ...' 0.954; #38 56563534 26 Sep 00:02:18Z 'probe 38: exp58n ...' 0.953; exp70g 56606948 27 Sep 11:15:12Z 'probe 45: exp70g ...' 0.956, L (7.49,7.67] h gate did NOT fire; exp70b 56592350 27 Sep 00:05:50Z 0.954.
- API SELECTED check cmd = round7/report.json tick_check_cmd (KaggleApi.competition_submissions(group=SUBMISSION_GROUP_SELECTED)).
- CONTEXT: 0 hits 'FINALS CARD' at 04:15Z -> R21-A9/R22-A4 still not logged (3rd deferral; deadline first W1 terminal, R22 hard stop 06:45Z). poll.log: 47/48/49 PENDING.
- User letters: 26 Sep 20:33Z 'один под паблик другой под прайват' (private-aimed default #37); 27 Sep 11:09:39Z letter (b) = {V*, #37}; 27 Sep 19:10:58Z picks on 29 Sep.
- No new mechanism: R8 passed 27 Sep 12:00Z; every item here is a message/ops line (runtime 0).
- 04:36Z final JSON written: research/wf_ideas_v4/round23/scan_hyp_finals_29sep.json (8 findings R23F-1..8 + draft_ru + model_table_r23); writer scratchpad r23_finals/write_finals_json.py
