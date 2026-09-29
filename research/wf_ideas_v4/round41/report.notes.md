# round41 report notes

- 2026-09-29T14:31Z start; no report.json existed. Inputs: round41 scan_*.json + v_*.json (findings + skeptic verdicts in task).
- 14:33:37Z NOTE (self-correction): my in-memory mk_card guard test failed to neutralise the file write for 6 single builds; it wrote scratchpad card_1837_{PENDING,T1,T3KEEP,T5,T6}.txt at 14:33:14Z (test inputs, --now 18:37Z). Removed at 14:33:37Z so no stale test card can be sent at 18:37Z. mk_card_1837.py itself untouched (sha8 59c54168).
- 14:35Z (v2 14:40Z) R41-A3 PATCH PROGRAM for mk_card_1837.py (merges PC41-03 + R41D-3; v2 keys late (> 19:12:17Z) and the admit edge (<= 19:45:17Z) on the READ poller header as CONTEXT 13:34Z logs, not on L_hi incl. retry slack; tested in memory with writes blocked: patched sha8 a19e1bd6, --dry-all 35/35 ok, 9 valid builds ok (T3KEEP bff20720, T1 23e775dd, T5 d1c396dc, PENDING 3b6e5cac = same as 59c54168), 13/13 bad inputs rejected). Save the text between the markers as <SP>/patch_mk_card_r41.py, run 'python <SP>/patch_mk_card_r41.py' (prints sha8 only), then with '--write'. It refuses unless the source is sha8 59c54168.
<<<PATCHR41
import hashlib, sys
SP = r"C:\Users\vital\AppData\Local\Temp\claude\c--Users-vital-Documents-kAGGLE-Biohub---Cell-Tracking-During-Development\acabaea6-42c1-4115-a146-2ddc5bb7e8c8\scratchpad"
fn = SP + r"\mk_card_1837.py"
src = open(fn, encoding="utf-8").read()
assert hashlib.sha256(src.encode()).hexdigest()[:8] == "59c54168", "source changed"
L = src.split("\n")
assert L[50].startswith('    if code in ("T1",): assert not late')
old49 = 'late = a.lhi is not None and a.lhi > 10.2'
assert L[48].count(old49) == 1
L[48] = L[48].replace(old49, 'late = a.lhi is not None and (hdr - P("2026-09-29T09:00:17Z")).total_seconds() / 3600 > 10.2')
guard = [
 '    # R41-A3 guard (decision B; admit edges keyed on the poller header as logged); --hdr = the READ header except PENDING',
 '    assert code in ("PENDING", "T1", "T2", "T3KEEP", "T5", "T6", "T8"), ("obsolete code under decision B", code)',
 '    if code != "PENDING":',
 '        assert a.lhi is not None, "--lhi needed"',
 '        base = (hdr - P("2026-09-29T09:00:17Z")).total_seconds() / 3600',
 '        assert -0.02 < a.lhi - base < 0.2, ("--lhi disagrees with --hdr", a.lhi, round(base, 3))',
 '    if code in ("T1", "T2", "T3KEEP", "T5"):',
 '        assert base <= 10.75, "read header after 19:45:17Z -> T8"',
 '        dv = float(disp); want = ("T2" if late else "T1") if dv >= 0.9595 else ("T3KEEP" if dv >= 0.9585 else "T5")',
 '        assert code == want, ("code/disp mismatch", code, disp, want)',
 '    if code in ("T1", "T2"): assert a.llo is not None, "--llo needed"',
 '    if code == "T8": assert base > 10.75, "T8 needs a read header after 19:45:17Z"']
s = "\n".join(L[:51] + guard + L[51:])
for old, new in (('PROMO = {"T1", "T2", "T3"}', 'PROMO = {"T1", "T2"}'),
                 ('ap.add_argument("--lb", default="pre_exp89t")', 'ap.add_argument("--lb", default="e10_20260929T1141Z")'),
                 ('ap.add_argument("--teams", type=int)', 'ap.add_argument("--teams", type=int, default=3994)')):
    assert s.count(old) == 1, old; s = s.replace(old, new)
i = s.index('    V = {"PENDING": {}'); j = s.index('    for code, extra in V.items():')
s = s[:i] + '''    V = {"PENDING": {}, "T1": dict(disp="0.960", llo=9.20, lhi=9.37),
         "T2": dict(disp="0.960", llo=10.22, lhi=10.39, hdr="2026-09-29T19:23:40Z"),
         "T3KEEP": dict(disp="0.959", llo=9.20, lhi=9.37), "T5": dict(disp="0.958", llo=9.20, lhi=9.37), "T6": dict(lhi=9.37),
         "T8": dict(disp="0.960", llo=10.70, lhi=10.87, hdr="2026-09-29T19:52:00Z")}
''' + s[j:]
h = hashlib.sha256(s.encode()).hexdigest()[:8]; print("patched sha8", h); assert h == "a19e1bd6", h
if "--write" in sys.argv:
    open(fn + ".59c54168.bak", "w", encoding="utf-8", newline="\n").write(src)
    open(fn, "w", encoding="utf-8", newline="\n").write(s); print("written", fn)
PATCHR41>>>
- 14:35Z local re-checks (0 Kaggle calls): pre_exp89t.sh w36816 STILL ALIVE at 14:32Z (R41D-1 not yet applied); manual_admit w3028, t7 w29648, poller w37016, watcher w30864, watchdog w22236, feed stop job w32220 alive. FEED SIGNAL waiter re-armed as w24700/11836 at 14:30:11Z (old w24352 fired on the 14:29:04Z run). Battery: AC (status 2), 78% at 14:35Z. Feed 14:29:04Z: 1 new topic 744357 'Farewell and Thanks' (nusrati), 0 comments, E10 FLAG none (https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744357). Newest poll header 14:29:30Z: 56669888 PENDING. CONTEXT newest entry = 13:58Z (round 40 applied); nothing logged since.
- Verified T7 texts (round40 scan_hyp_exp89tmsg40.json messages_case_a_P3.T7 / messages_case_b_P2.T7) contain '≥ 0.960 или 0.959 с UP'; manual_admit_COMPLETE = 'use T2 / T3 (UNPROVEN-ins) / T4_question / T5_late by display'. T8 texts do not mention UP. t7_trigger.sh prints header + status only; the message text is sent by the main session.
- pre_exp89t.sh read: waits for 17:40:00Z, skips only if newest non-error block shows 56669888 COMPLETE/ERROR, else up to 2 'timeout 180 uptest.py save pre_exp89t' (300 s apart).
- 14:42Z design choices for report: (1) merged PC41-03/R41D-3 guard but keyed the admit edge and 'late' on the READ poller header (CONTEXT 13:34Z 'poller header <= 19:45:17Z, > 19:12:17Z flagged UNPROVEN-ins'), not on L_hi (which adds 210 s per failed CLI attempt, tools/runtime_ledger.py l.42/210): with PC41-03's 'lhi <= 10.75' a header at 19:43:00Z with one retry note (L_hi 10.78) would be wrongly forced to T8. (2) PC41-01's verification filter (Win32_Process CommandLine -match 'pre_exp89t') would match the checking PowerShell itself -> use Get-Process -Id 36816. (3) REPORT.md not written (subagent rule: no report .md files; rounds 38-40 same); REPORT_RU text is carried in report.json next_focus. (4) R41-RC-B refuted -> rejected; do not log 'floor'.
- 14:42:57Z report.json written and validated (8 actionable R41-A1..A8; REPORT_RU carried in next_focus).
