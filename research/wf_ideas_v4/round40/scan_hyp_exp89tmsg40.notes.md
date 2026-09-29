# scan_hyp_exp89tmsg40 notes (round 40)

- 2026-09-29T13:14:43Z start. JSON absent -> fresh run. Inputs: round38/report.json R38-A5, round39/report.json R39-A3..A7, scratchpad card_1203_sent.txt (11006 B, 15:04 local), mk_card_v3.py, t7_trigger.sh.
- 13:15Z: poll.log header 13:09:12Z: 56669888 PENDING. CONTEXT newest entry 12:59Z (744250 finish-by-23:59Z rule). SELECTED 12:37:31Z = {56640366 exp87a, 56563521 #37} = П3 (CONTEXT l.4579).
- card_1203_sent.txt sha256[:8] = 4fa899f9 (whole file, 60 lines incl. trailing), = CONTEXT l.4575. card v3 ae03f566. mk_card_1837.py NOT yet written (scratchpad listing 13:15Z).
- tools/uptest.py load(tag) returns (rows, ranks, ours); e10_20260929T1141Z/lb.csv has only 1006 rows (teams 3 994 came from the e10 txt) -> mk_card must not use len(rows) from an e10 csv.
- Stale card lines after the П3 tick: l.7 SELECTED, l.32 '{#37,#38}' model line, l.49 'отметьте выбранную пару сейчас', l.40 'слот ... держим в запасе' (dead for x138 files after ~15:00Z per 744250, CONTEXT 12:59Z), l.3/l.8 header/rank, l.48 read window.
- R38-A5 T1 (b) leads with П3 double swap; R39-A4 (later) says push to П2 when the user chose П2 and only V_pub is stale -> conflict, П2-first used.
- MASKED impossible today: slot 2 unused (11:54Z), exp89t the only PENDING ref -> count can move by 1 only (lastok block 13:19:14Z: 1 PENDING row).
- 13:25Z: heredoc-to-python failed in Git Bash (quote parse); script kept below between markers and exec'd from this file (no other file written).

## mk_card_1837.py (proposed; copy verbatim to the scratchpad)

<<<MKCARD
# mk_card_1837.py (R39-A7 / R40): builds the 18:37Z (21:37 MSK) card from scratchpad card_1203_sent.txt
# (sha8 4fa899f9); 0 Kaggle calls. Run from the repo root.
#  python <SP>/mk_card_1837.py CODE --hdr 2026-09-29T18:21:40Z [--disp 0.960] [--llo 9.20 --lhi 9.35] [--k 3]
#         [--why k0|blind|q] --sel 56640366,56563521 --seltime 2026-09-29T18:36:10Z --lb pre_exp89t [--teams 3994]
#  CODE in PENDING, UPWAIT, T1, T2, T3, T4, T5, T6, T8.  --dry-all builds every variant, writes nothing.
import argparse, datetime as dt, hashlib, os, re, sys
SP = r"C:\Users\vital\AppData\Local\Temp\claude\c--Users-vital-Documents-kAGGLE-Biohub---Cell-Tracking-During-Development\acabaea6-42c1-4115-a146-2ddc5bb7e8c8\scratchpad"
sys.path.insert(0, "tools"); import uptest
SRC = os.path.join(SP, "card_1203_sent.txt")
NAME = {"56640366": ("exp87a", "0.959"), "56563521": ("#37", "0.954"), "56656157": ("exp75", "0.955"),
        "56563534": ("#38", "0.953"), "56629533": ("exp85a", "0.958"), "56669888": ("exp89t", None)}
PROMO = {"T1", "T2", "T3"}
def msk(ts): return (ts + dt.timedelta(hours=3)).strftime("%H:%M")
def utc(ts): return ts.strftime("%H:%M")
def P(s): return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
def komand(k): return "команду" if k % 10 == 1 and k % 100 != 11 else ("команды" if k % 10 in (2, 3, 4) and k % 100 not in (12, 13, 14) else "команд")
def hh(x): return f"{x:.2f}".replace(".", ",")
def sgn(x): return ("+" if x > 0.0005 else ("−" if x < -0.0005 else "")) + f"{abs(x):.3f}"
def sel_case(sel, promo):
    v = "56669888" if promo else "56640366"
    if sel == {v, "56563521"}: return "a"
    if sel == {v, "56656157"}: return "b"
    if promo and sel == {"56640366", "56563521"}: return "a_old"
    if promo and sel == {"56640366", "56656157"}: return "b_old"
    if sel == {"56563521", "56563534"}: return "c"
    return "d"
def steps(case, promo, sel):
    v = "exp89t 56669888" if promo else "exp87a 56640366"
    if case == "a": return f"Менять ничего не нужно: у вас отмечена П3 {{{v}, #37 56563521}}."
    if case == "b": return f"У вас П2 {{{v}, exp75 56656157}} — допустимый обмен, менять не обязательно."
    if case == "a_old": return "Что сделать: сначала снимите exp87a 56640366, потом отметьте exp89t 56669888 (#37 оставьте); проверьте «2 of 2 selected» до 23:00 МСК."
    if case == "b_old": return ("Что сделать (у вас П2): сначала снимите exp87a 56640366, потом отметьте exp89t 56669888 (exp75 оставьте); "
                                "для П3 снимите ещё exp75 56656157 и отметьте #37 56563521; проверьте «2 of 2 selected» до 23:00 МСК.")
    if case == "c": return f"Что сделать: сначала снимите #38 56563534, потом отметьте {v} (#37 оставьте); проверьте «2 of 2 selected» до 23:00 МСК."
    keep = {v.split()[1], "56563521"}
    off = ", ".join(f"{NAME.get(r, ('ref',))[0]} {r}" for r in sorted(sel) if r not in keep)
    on = " и ".join(x for r, x in ((v.split()[1], v), ("56563521", "#37 56563521")) if r not in sel)
    return f"Что сделать: сначала снимите {off}, потом отметьте {on} (П3); проверьте «2 of 2 selected» до 23:00 МСК."
def build(a):
    s = open(SRC, encoding="utf-8").read()
    assert hashlib.sha256(s.encode()).hexdigest()[:8] == "4fa899f9", "card_1203_sent.txt changed"
    L = s.split("\n")
    def idx(prefix):
        i = [j for j, l in enumerate(L) if l.startswith(prefix)]; assert len(i) == 1, (prefix, i); return i[0]
    def sub(i, old, new):
        assert L[i].count(old) == 1, (i, old); L[i] = L[i].replace(old, new)
    code = a.code; promo = code in PROMO; now = P(a.now) if a.now else dt.datetime.utcnow().replace(microsecond=0)
    hdr = P(a.hdr); sel = set(a.sel.split(",")); assert len(sel) == 2, "SELECTED must be exactly 2 refs"
    case = sel_case(sel, promo); disp = a.disp; late = a.lhi is not None and a.lhi > 10.2
    if code in ("T2",): assert late, "T2 needs L_hi > 10.2"
    if code in ("T1",): assert not late, "L_hi > 10.2 -> use T2"
    L[idx("ФИНАЛЫ: карточка на")] = f"ФИНАЛЫ: карточка на {msk(now)} МСК ({utc(now)} UTC), поллер {msk(hdr)} МСК ({utc(hdr)} UTC)."
    order = sorted(sel, key=lambda r: (r not in ("56669888", "56640366"), r))
    def nm(r):
        n, sc = NAME.get(r, ("ref", "?")); return f"{n} {r} ({(disp or 'не прочитан') if r == '56669888' else sc})"
    L[idx("Сейчас отмечены (API,")] = f"Сейчас отмечены (API, {msk(P(a.seltime))} МСК): {nm(order[0])} и {nm(order[1])}."
    rows, ranks, o = uptest.load(a.lb)
    teams = len(rows) if len(rows) > 3000 else a.teams; assert teams, "--teams needed (truncated LB csv)"
    sc = o["Score"]; same = [r["TeamId"] for r in rows if r["Score"] == sc]; pos = same.index(uptest.TEAM) + 1
    d0 = os.path.join(uptest.OUT, a.lb)
    lbt = dt.datetime.fromtimestamp(max(os.path.getmtime(os.path.join(d0, f)) for f in os.listdir(d0)), dt.timezone.utc).replace(tzinfo=None)
    lab = f"{msk(lbt)} МСК" + (", до чтения exp89t" if promo and a.lb != "post_exp89t" else "")
    tt = f"{teams:,}".replace(",", " ")
    L[idx("Мы на ЛБ (")] = f"Мы на ЛБ ({lab}): #{o['Rank']} из {tt}, лучший паблик {sc}, место {pos} из {len(same)} в блоке {sc}."
    flag = ", UNPROVEN-ins" if late else ""
    if promo:
        L[idx("1) ОСНОВНОЙ ФАЙЛ (V_pub) =")] = f"1) ОСНОВНОЙ ФАЙЛ (V_pub) = exp89t 56669888, паблик {disp}, с CI{flag}."
        i = idx("   exp87a | 56640366 |")
        up = "не нужен (выше 0.959)" if code != "T3" else f"обошли {a.k} {komand(a.k)} (против 0.959)"
        row = f"   exp89t | 56669888 | {disp} | CI да | SEC нет | 4 (cap 6, K, CI, DIS) | {up} | {a.llo:.2f}–{a.lhi:.2f}{' UNPROVEN-ins' if late else ''}"
        if code == "T3": L.insert(i, row)
        else: L[i] = row
        sub(idx("   Лучший файл с CI: V_CI ="), "exp87a 56640366 (0.959)", f"exp89t 56669888 ({disp})")
        sub(idx("   П2 {exp87a 56640366, exp75 56656157}:"), "П2 {exp87a 56640366,", "П2 {exp89t 56669888,")
        i = idx("   П3 {exp87a 56640366, #37 56563521}:"); sub(i, "П3 {exp87a 56640366,", "П3 {exp89t 56669888,"); sub(i, "(cap 6, K, CI).", "(cap 6, K, CI, DIS).")
        L[idx("   Для сведения: {exp87a 56640366, exp85a 56629533}")] = ("   Для сведения: {exp89t 56669888, exp87a 56640366} — это и есть «лучший + ближайший сосед» "
            "(exp87a отличается только DIS). cap 6, K и CI в обоих файлах, пара страхует только DIS; вне согласованного плана.")
    i = idx("   Сейчас отмечено {#37 56563521, #38 56563534}:")
    if case != "c": del L[i]
    sub(idx("   SEC: высокий."), "последний слот дня держим в запасе (только под новый публичный ноутбук, по вашему «да»)",
        "последний слот дня не использован: файл семейства x138, отправленный сейчас, не досчитается до 02:59 МСК (23:59 UTC), а незавершённый файл выбрать нельзя (обсуждение 744250)")
    i = idx("   DIS 2.25: ~0."); old = "Прямое чтение с CI — exp89t (раздел 5)."
    d = None if disp is None else round(float(disp) - 0.959, 3)
    dis = {"UPWAIT": "Прямое чтение с CI: exp89t 0.959 = exp87a 0.959, UP-тест идёт (раздел 5).",
           "T3": f"Прямое чтение с CI: exp89t 0.959 = exp87a 0.959, но UP-тест: мы обошли {a.k} {komand(a.k) if a.k else ''} — без округления выше, разница от 0 до +0.001 на одном эмбрионе.",
           "T4": ("Прямое чтение с CI: exp89t 0.959 = exp87a 0.959, UP не подтверждён: DIS на базе с CI ≈ 0." if a.why != "q"
                  else "DIS на базе с CI не прочитан (код «?»: exp89t завершился после 22:12 МСК, UP не подтверждён)."),
           "T6": "Прямого чтения с CI нет: exp89t завершился с ошибкой.",
           "T8": f"exp89t прочитан только после 22:45 МСК ({disp}) — для сведения, вне финала."}
    if d is not None:
        dis["T1"] = dis["T2"] = f"Прямое чтение с CI: exp89t {disp} против exp87a 0.959 — по округлённым {sgn(d)}, истинная разница от {sgn(d-0.001)} до {sgn(d+0.001)} на одном эмбрионе."
        dis["T5"] = (f"Прямое чтение с CI: exp89t {disp} против exp87a 0.959: {sgn(d)} по округлённому паблику (истинно от {sgn(d-0.001)} до {sgn(d+0.001)}), т.е. ≈ 0 или минус."
                     if not late else "DIS с CI: «?» (exp89t завершился после 22:12 МСК).")
    if code != "PENDING": sub(i, old, dis[code])
    if code not in ("PENDING", "T6"): sub(i, "Паблик: прямого чтения нет; косвенно", "Без CI прямого чтения нет; косвенно")
    i = idx("5) ЕЩЁ НЕ ПРОЧИТАНЫ (PENDING)"); j = idx("   exp89t 56669888 (exp87a + DIS 2.25"); k49 = idx("   exp89t ещё не прочитан:")
    ex = ("снимите exp87a 56640366, отметьте exp89t 56669888 (exp75 оставьте)" if case == "b"
          else "снимите exp87a 56640366, отметьте exp89t 56669888 (#37 оставьте)")
    if code == "PENDING":
        sub(j, "чтение ожидается ~20:55–21:30 МСК (хвост до ~22:54; основным может стать, только если поллер покажет его завершённым до 22:45 МСК (после 22:12 — с пометкой UNPROVEN-ins) и чтение ≥ 0.960 или 0.959 с приписываемым UP; если позже 22:45 МСК — не финал при любом паблике)",
            f"ещё считается на {msk(now)} МСК (поллер {msk(hdr)} МСК; обычно 9,3–9,5 ч, хвост до ~22:54): до 22:12 МСК — обычное чтение, 22:12–22:45 — с пометкой UNPROVEN-ins, позже 22:45 — не финал при любом паблике; основным может стать только при ≥ 0.960 или 0.959 с приписываемым UP")
        if case in ("a", "b"): L[k49] = f"   exp89t ещё не прочитан. Ваша пара уже отмечена, ждать его не нужно; если он сменит основной файл: {ex}."
    else:
        rd = f"exp89t 56669888 (exp87a + DIS 2.25: cap 6, K, CI, DIS; без SEC) прочитан {msk(hdr)} МСК ({utc(hdr)} UTC)"
        L[i] = "5) exp89t: ОШИБКА" if code == "T6" else "5) ЧТЕНИЕ exp89t"
        why = {"k0": "после его завершения мы не обошли ни одной команды", "blind": "снимок ЛБ после чтения не скачался",
               "q": "код «?»: завершился после 22:12 МСК"}.get(a.why, "")
        un = (" (поллер показал его завершённым только после 22:12 МСК, L_hi > 10,2 ч: пометка UNPROVEN-ins — гейт вставки мог сработать на последних клипах (≤ ~0,0005); по записанному правилу это обычное чтение)" if late else "")
        lh = hh(a.lhi) if a.lhi else "?"
        body = {"T1": f"{rd}: {disp}, L_hi {lh} ч{un} — выше exp87a 0.959, стал основным. П3 = {{exp89t 56669888, #37 56563521}}; П2 {{exp89t 56669888, exp75 56656157}} — только как обмен.",
                "T3": f"{rd}: 0.959, L_hi {lh} ч{un}; UP-тест: после его завершения мы обошли {a.k} {komand(a.k) if a.k else ''} (счётчик 56 → 57) — он выше exp87a без округления, стал основным. П3 = {{exp89t 56669888, #37 56563521}}; П2 {{exp89t 56669888, exp75 56656157}} — только как обмен.",
                "UPWAIT": f"{rd}: 0.959 — как у exp87a; идёт UP-тест, ответ не позже 22:50 МСК. Пока основной — exp87a 56640366.",
                "T4": f"{rd}: 0.959, но UP не подтверждён ({why}); по правилу «чемпион по порядку завершения» основной остаётся exp87a 56640366, пары выше без изменений.",
                "T5": f"{rd}: {disp} — ниже exp87a, основной остаётся exp87a 56640366, пары выше без изменений.",
                "T6": f"exp89t 56669888 завершился с ошибкой ({msk(hdr)} МСК, {utc(hdr)} UTC; через {lh} ч): основной остаётся exp87a 56640366; повторной отправки нет (не успеет прочитаться до 23:00 МСК).",
                "T8": f"{rd} — позже края допуска 22:45 МСК: паблик {disp} — только для сведения, в финал он не идёт при любом значении; основной остаётся exp87a 56640366."}
        body["T2"] = body["T1"]
        L[j] = "   " + body[code]
        st = steps(case, promo, sel)
        if code == "UPWAIT" and case in ("a", "b"): st += f" Если UP подтвердится, пришлю одну строку: {ex}."
        L[k49] = "   " + st
        sub(idx("   Если основной файл изменится после этой карточки"),
            "Если основной файл изменится после этой карточки, пришлю одну строку сразу после чтения exp89t (и проверю в 22:43 МСК, 19:43 UTC). После чтения можно перевыбрать до 23:00 МСК.",
            "Результат UP-теста пришлю одной строкой; проверю отметку в 22:43 МСК (19:43 UTC); перевыбрать можно до 23:00 МСК." if code == "UPWAIT"
            else ("Перевыбрать можно до 23:00 МСК." if hdr >= P("2026-09-29T19:43:00Z") else "Проверю отметку в 22:43 МСК (19:43 UTC); перевыбрать можно до 23:00 МСК."))
    out = "\n".join(L)
    blk = out[out.index("====="):out.rindex("=====")]
    assert out.count("=====") == 2
    for t in ("П1", "рекомендую", "<", "[если", "П4", "довод", "держим в запасе", "15:04 МСК", "поллер 14:59", "  ,", " ;"):
        assert blk.count(t) == 0, t
    assert blk.lower().count("подтверждено") == 2, blk.lower().count("подтверждено")
    bad = re.findall(r"\{[a-z_]+\}|None|nan|\?\s*ч", blk); assert not bad, bad
    assert blk.count("Сейчас отмечено {#37 56563521, #38 56563534}") == (case == "c")
    assert blk.count("отметьте выбранную пару сейчас") == (code == "PENDING" and case not in ("a", "b"))
    l7 = [l for l in out.split("\n") if l.startswith("Сейчас отмечены (API,")][0]; assert all(r in l7 for r in sel)
    if code == "PENDING": assert blk.count("чтение ожидается") == 0 and blk.count("ещё считается на") == 1
    else: assert blk.count("ЕЩЁ НЕ ПРОЧИТАНЫ") == 0 and blk.count("ещё не прочитан") == 0 and blk.count("чтение ожидается") == 0
    if promo:
        for t, n in (("V_pub) = exp89t 56669888", 1), ("V_CI = exp89t 56669888", 1), ("П3 {exp87a", 0), ("П2 {exp87a", 0)):
            assert blk.count(t) == n, t
        assert blk.count("{exp89t 56669888, #37 56563521}") >= 2 and blk.count("cap 6, K, CI, DIS") >= 3
        assert ("UNPROVEN-ins" in [l for l in out.split("\n") if l.startswith("1) ")][0]) == late
    else:
        for t, n in (("V_pub) = exp87a 56640366", 1), ("V_CI = exp87a 56640366", 1)):
            assert blk.count(t) == n, t
        assert blk.count("П3 {exp87a 56640366, #37 56563521}") >= 1
        assert blk.count("П3 {exp89t") == 0
    return out, case
ap = argparse.ArgumentParser(); ap.add_argument("code", nargs="?"); ap.add_argument("--hdr"); ap.add_argument("--now"); ap.add_argument("--disp")
ap.add_argument("--llo", type=float); ap.add_argument("--lhi", type=float); ap.add_argument("--k", type=int); ap.add_argument("--why")
ap.add_argument("--s0"); ap.add_argument("--s1"); ap.add_argument("--sel"); ap.add_argument("--seltime"); ap.add_argument("--lb", default="pre_exp89t")
ap.add_argument("--teams", type=int); ap.add_argument("--dry-all", action="store_true"); ap.add_argument("--show")
a = ap.parse_args(sys.argv[1:])
if a.dry_all:
    base = dict(hdr="2026-09-29T18:21:40Z", now="2026-09-29T18:37:00Z", seltime="2026-09-29T18:36:10Z", lb="e10_20260929T1141Z", teams=3994,
                disp=None, llo=None, lhi=None, k=None, why=None, s0=None, s1=None)
    V = {"PENDING": {}, "UPWAIT": dict(disp="0.959", llo=9.20, lhi=9.37), "T1": dict(disp="0.960", llo=9.20, lhi=9.37),
         "T2": dict(disp="0.960", llo=10.22, lhi=10.39, hdr="2026-09-29T19:23:40Z"), "T3": dict(disp="0.959", llo=9.20, lhi=9.37, k=3),
         "T4": dict(disp="0.959", llo=9.20, lhi=9.37, why="k0"), "T5": dict(disp="0.958", llo=9.20, lhi=9.37), "T6": dict(lhi=9.37),
         "T8": dict(disp="0.960", llo=10.70, lhi=10.87, hdr="2026-09-29T19:52:00Z")}
    for code, extra in V.items():
        for sel in ("56640366,56563521", "56640366,56656157", "56563521,56563534", "56669888,56563521", "56640366,56629533"):
            ns = argparse.Namespace(code=code, sel=sel, **{**base, **extra})
            out, case = build(ns)
            print(code, sel, case, hashlib.sha256(out.encode()).hexdigest()[:8], "ok")
            if a.show and a.show == f"{code}:{case}": print(out)
else:
    out, case = build(a)
    fn = os.path.join(SP, f"card_1837_{a.code}.txt"); open(fn, "w", encoding="utf-8", newline="\n").write(out)
    print(fn, "case", case, "sha8", hashlib.sha256(out.encode()).hexdigest()[:8])
MKCARD>>>

- 13:40Z: mk_card_1837 dry-all (exec from this file, synthetic inputs, lb e10_20260929T1141Z + --teams 3994): 45/45 variants (PENDING, UPWAIT, T1, T2, T3, T4, T5, T6, T8 x SELECTED {П3, П2, #37+#38, exp89t+#37, other}) pass every token assert. Fixes found while testing: teams comma lost by a global replace; 'П3 = {' vs 'П3 {'; DIS line 'Паблик: прямого чтения нет' contradicts a read -> 'Без CI прямого чтения нет'; T8 after 19:43Z should not promise the 22:43 check.
- 13:45Z: messages drafted (case (a) П3 and (b) П2) for T1, T2, T3 interim/promo, T4 (k0/BLIND/'?'), T5 (+ >10.2 h), T6, T7, T8 (pre-20:00Z / post-20:00Z / not terminal after the 19:44:45Z manual list). Honest null for new levers: no file can both finish by 23:59Z and read before the 20:00Z tick; nothing reaches R8.
