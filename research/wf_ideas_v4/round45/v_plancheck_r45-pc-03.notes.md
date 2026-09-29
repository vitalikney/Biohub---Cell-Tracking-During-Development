# v_plancheck R45-PC-03 (battery) - skeptic notes
- 18:30:31Z: no prior v_plancheck_r45-pc-03.json; writing fresh.
- 18:30Z WMI Win32_Battery: EstimatedChargeRemaining 64, BatteryStatus 1, EstimatedRunTime 136 min. root/wmi BatteryStatus: PowerOnline False, Discharging True, RemainingCapacity 35264 mWh, DischargeRate 15520 mW.
- Rate check: 69% @18:14:58Z -> 64% @18:30:31Z = 5%/15.5 min ~ 19-20 %/h (the 28 %/h in the finding came from a 4-min 69->67 window; rounding noise).
- powercfg SCHEME_BALANCED: STANDBYIDLE DC = 0 (never idle-sleeps); BATLEVELCRIT DC = 2 %; BATACTIONCRIT DC = 2 (Hibernate).
- Projection: to 2% = 62 pts / 19.5 %/h ~ 3.2 h -> ~21:40Z; by energy 35.3 Wh*(62/64)/15.5 W ~ 2.2 h -> ~20:45Z; WMI 136 min -> 20:46Z. Hibernate window ~20:45-21:40Z (23:45 MSK - 00:40 MSK).
- Pre-20:00Z events (18:37Z card, T7 19:12-19:20Z, manual-admit 19:44:45Z, 19:43Z check) are safe. 21:05Z (00:05 MSK) check ~ coin flip; 00:07Z (03:07 MSK) save/stop/commit certainly lost if not on AC. Ticked pair П3 unaffected (server-side).
- 16220 watchdog: battery-while-loop, alerts only on AC return / stale poll (scan_plancheck.json evidence) - no percent alert. Confirmed PID 16220 alive.
- Verdict: fact confirmed, action (chat message + optional local <=25 % alert, 0 Kaggle calls) is cheap, fail-soft, no rule impact. Not refuted; only refresh numbers in the message.
