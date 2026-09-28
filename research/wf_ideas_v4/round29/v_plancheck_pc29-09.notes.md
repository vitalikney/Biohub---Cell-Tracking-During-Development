# v_plancheck PC29-09 notes (2026-09-28 20:38Z)
- round27/finals_card_v4_ru.md mtime 15:55:37Z: confirmed l.40 П3 silver '~0.51', l.64 '22:30 МСК (19:30 UTC)[если принято R27C-3 ...]', fill_times notify_only 19:30Z. Diagnosis of PC29-09 is correct for v4.
- CONTEXT.md l.4029-4034 (16:26Z entry) claims card filled "with the R27-A8 edits" -> wrong for v4 (needs correction line).
- BUT round29/finals_card_v5_ru.md exists (mtime 20:26:43Z, same round, scan_hyp_cardfix): v4 + R27-A8 (1)-(7) + R28-A5 + R28-A4(vi). grep: l.41 'серебро ~0.39–0.63 (база 0.51)'; l.69 '22:43 МСК (19:43 UTC)' + 21:05Z SELECTED check (ddc5884d); l.93 waiters 2e9ce42e/ec670938/64b9bb56/ddc5884d; change list l.145-153 covers R27-A8 (1)-(5) and R28-A5 (token keying by file-name substring, not probe number).
- scan_hyp_cardfix.json l.41 action already: log R28-A5 correction pointing to v5, point 12:03Z/18:37Z waiters at v5.
- => PC29-09 action (edit v4 at 00:46Z/06:07Z) is superseded; editing v4 would create a second divergent card. Only residual: CONTEXT correction + waiter text -> v5 (owned by R29-CARDFIX).
- Value: 0 on private/public score (ops text only). Refute as duplicate/superseded.
