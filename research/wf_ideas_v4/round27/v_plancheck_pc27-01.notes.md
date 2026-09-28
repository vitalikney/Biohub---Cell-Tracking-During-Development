# v_plancheck PC27-01 notes (2026-09-28 ~16:05Z)
- Get-WinEvent Kernel-Power (last 4h), re-checked 16:04Z: 14:59:00Z 506 enter MS Reason Lid; 14:59:01Z 105 Power source change; 14:59:11Z 172 Disconnected (Adaptive Connected Standby); 15:15:31Z 507/506 Austerity Battery Drain Budget Exceeded; 15:15:42Z 172 Disconnected (Policy Setting); 15:39:48Z 507 exit Reason Lid. CONFIRMED.
- Earlier: 12:29:55Z and 14:42:45Z enter MS Idle Timeout; 14:44:19Z poll header still ran (no 172 Disconnected) -> idle standby kept network.
- Win32_Battery 16:04Z: BatteryStatus 1 (discharging), 58% (finding said 64% at 15:49Z) -> ~6%/15 min ~ 24%/h -> empty ~18:30Z (21:30 MSK), i.e. BEFORE probe-51 read (21:30-22:15Z). More urgent than finding says.
- powercfg /a: S0 low power idle, network connected; STANDBYIDLE AC/DC 0; VIDEOIDLE 0x12c=300 s AC/DC.
- poll.log headers: 14:54:21Z -> 15:15:31Z (NameResolutionError x2) -> 15:41:53Z; 10-min cadence otherwise.
- CONTEXT 15:43Z entry says 'network outage, not a sleep' -> wrong; needs correction.
- Caveats: (a) SetThreadExecutionState keep-awake does NOT block lid-close standby, only idle; (b) LIDACTION via setacvalueindex only on AC; on battery lid close still sleeps -> charger is the primary ask; (c) finals/poller run to 29 Sep 20:00Z (23:00 MSK), so charger/keep-awake until then, not 15:00 MSK / 12:00Z; (d) 23:25Z single check is too late (battery may be dead by 18:30Z) -> check every 30 min now, push if BatteryStatus!=2 or <30%.
