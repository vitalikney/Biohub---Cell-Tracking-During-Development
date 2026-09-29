- 2026-09-29T05:28:03Z report agent started; no report.json existed
- 2026-09-29T05:58:58Z report agent (2nd start) started; report.json absent; reading CONTEXT tail + round reports
- 06:00Z poll.log: header 05:57:51Z OK (3 night refs PENDING; 56640366 exp87a COMPLETE 0.959). Headers 05:34:41Z and 05:46:17Z FAILED (NameResolutionError / SSLEOFError) = network outage during the user's trip.
- 06:00Z e10 watch_loop.log RUN 41 (snapshot 20260929T0541Z.txt, logged 05:47:43Z): fetch 0 OK / 8 FAILED incl. leaderboard -> no LB snapshot between 05:13Z and the next run 06:41:53Z.
- feed_loop.log 05:28:19Z: new topics 1 (744250, kostopr4v 05:06:55Z), new comments 0, E10 FLAG none; digest_20260929T0528Z.md top public 0.9530.
- Win32_Battery 06:00Z: BatteryStatus 1 (discharging) 72%. Processes: lb_poll 37016, e10 18040, feed 10924, watchers 16292 / 1760 (56656147) / 17532 (56656157) alive (sleep 120, no uptest save); main session armed 18900 'BACK ON AC' watcher and 13836 feed-signal watcher at 05:27-05:29Z.
- card v5 sha8 a134d5e4, night_checklist 2b442e87 (re-verified). Card l.45 names {V_pub, exp70g} as 'best + closest neighbour' and 'below P1' -> wrong for V_pub exp87a (no P1 row for a CI V_pub; nearest neighbour = exp85a, differs only by CI).
- R28-RC-C (CI prior +0.0002) REFUTED in round28/report.json; mc26.py standing prior CI_MU 0.0005 CI_SD 0.0008. mc34_*.txt used CI_MU 0.0002 (refuted prior).
- Re-ran scratchpad r26/mc26.py under the STANDING prior, VPUB=exp87a, PARTNERS #37,exp75,exp85a,exp89u (stdout only):
  base K 0.0009 s11: #37 .791/.580 | exp75 .824/.622 | exp85a .742/.586 | exp89u .835/.648 (bronze/silver)
  base K 0.0003 s11: #37 .740/.502 | exp75 .789/.561 | exp85a .657/.497 | exp89u .739/.536
  base K 0      s11: #37 .714/.466 | exp75 .772/.534 | exp85a .612/.457 | exp89u .684/.485
  base s23:          #37 .785/.576 | exp75 .815/.613 | exp85a .737/.581 | exp89u .826/.645
  overfit s11:       #37 .859/.675 | exp75 .880/.721 | exp85a .788/.663 | exp89u .883/.741
  => exp89u leads the ALREADY-SUBMITTED exp75 partner by only ~0.003-0.011 bronze at K +0.0009 and loses by 0.05-0.09 at K <= +0.0003. RC-A dead.
  => {exp87a, exp85a} below P3 on bronze 5/5; silver ~level at base (0.586 vs 0.580), below at K<=0.0003 and overfit -> skeptic's 'ABOVE P3 on silver 12/12' is a refuted-prior artefact.
- tools/uptest.py: save = LB download (no internal timeout) + prints rank/score/SubmissionCount; compare = TeamIds passed; loads _lb/<tag>/*.zip.
- 06:04:02Z verified IDEAS ids for r34x-3 mapping; drafting report.json
- 06:05:39Z report.json written (4 actionable; RC-A/PI/RC-B rejected; REPORT.md text in report_md_ru)
