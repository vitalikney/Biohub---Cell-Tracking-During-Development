# notes r32x-3 (started 2026-09-29T03:33:06Z)
- 03:35Z no prior JSON. Checked CONTEXT.md:
  - l.3171-3176 (7) LAST USEFUL SUBMIT: T_last = 18:30Z - (L_ref + 0.25 h) -> ~10:30Z, never later than 11:00Z; CI files T_last - 2.4 h (~08:05Z); 'A file submitted after its T_last is never a finals candidate.'
  - l.3194 / 3376 / 3394: FINALS READ ~19:00Z 29 Sep; E10 copy after 02:00Z allowed until ~10:00Z; after 02:00Z no CI file (kinds of AMEND 2 (5)) unless user yes.
  - l.3606-3614 (07:47Z 28 Sep): cap lift = up to 2 NON-CI files until ~10:25Z; E10 after 02:00Z case-by-case, user yes per notebook.
  - l.4175-4199: probe 51 exp87a = 0.959 -> E10 trigger now >= 0.960; night used 3 of 5 29-Sep slots (52/53/54), 2 left for MORNING TABLE (A-M1 exp89l, A-M2).
  - watch_loop.log START lines: 'until 2026-09-29T12:00:00Z' (confirmed).
- Verdict: finding anchors on the 20:00Z tick, not the registered 18:30Z T_last anchor / 19:00Z finals read -> its 10:30Z (CI) / 12:45Z (non-CI) are ~2.3 h later than the pre-registered T_last (~08:05Z CI / ~10:25-10:30Z non-CI). As a 'reminder' it contradicts rule (7). Ignores slot budget (2 left). Zero value; refute.
