- 16:25Z start skeptic check r43-ops-card
- 16:25Z: <SP>/mk_card_1837.py sha256 a19e1bd64d3c... (sha8 a19e1bd6 confirmed); source card_1203_sent.txt sha8 4fa899f9 (script asserts it). Python 3.12.10.
- --dry-all from repo root: rc 0, 35 'ok' lines, nothing written (confirmed).
- Negative tests via a wrapper that blocks card_1837 writes (0 Kaggle calls, no file left):
  T1 --disp 0.959 -> AssertionError code/disp mismatch want T3KEEP; T2 0.959 (hdr 19:23:40Z) -> same; T5 0.959 -> want T3KEEP;
  T3KEEP 0.960 -> want T1 (so 0.960 cannot be kept on exp87a by mistake either); T3 -> 'obsolete code under decision B';
  T8 with hdr 18:21Z -> refused; T1 with hdr 19:52Z -> 'use T2' (then T2 -> T8 edge 10.75 h). Positive: T3KEEP 0.959, T1 0.960, PENDING build.
- Decision B mapping in code l.60: dv >= 0.9595 -> T1/T2 (promo), 0.9585 <= dv < 0.9595 -> T3KEEP, else T5. Matches user decision B (promote only at >= 0.960).
- Nits (no action): error ordering T1-late says 'use T2' before T8 edge (fail-closed); --disp 0.9595 would pass T1 but LB display is 3 d.p.; utcnow() DeprecationWarning only if --now omitted (stderr, harmless).
- Wrapper/test files deleted; 0 card_1837_* files in scratchpad at 16:27Z.
