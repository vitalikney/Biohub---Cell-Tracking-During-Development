# КАРТОЧКА ФИНАЛОВ v4 (черновик, раунд 27; заполнить 29 сен в 15:03 МСК / 12:03 UTC и в 21:37 МСК / 18:37 UTC)

Источник: R26-A5 (2) (правки к черновику R26F-8), правило партнёра exp75 v2 (CONTEXT 28 сен 14:12 UTC), пул и PENDING (R26-A4 (d)), утренняя таблица v1.1.
Всё в `<...>` заполняется по таблице в конце файла. Строки с пометкой `[если ...]` удаляются, когда условие не выполнено.
Отправлять только блок между линиями `=====`. Часть «ДЛЯ СЕССИИ» не отправлять.

=====

ФИНАЛЫ: карточка на <T_MSK> МСК (<T_UTC> UTC), поллер <HDR_UTC> UTC.
Отметить до 23:00 МСК (20:00 UTC). Kaggle даёт перевыбрать до 02:59 МСК 30 сен (23:59 UTC).
Галочки ставите только вы: сессия их не ставит.

Сейчас отмечены: <SELECTED>.
Мы на ЛБ: #<RANK> из <TEAMS>, лучший паблик <BEST_DISPLAY>, место <BLOCK_POS> в блоке <BEST_DISPLAY>.

1) ОСНОВНОЙ ФАЙЛ (V_pub) = <V_PUB_FILE> <V_PUB_REF>, паблик <V_PUB_SCORE>, <V_PUB_KIND>.
   Кандидаты с наибольшим пабликом (COMPLETE; гейт вставки не сработал; для CI L_hi ≤ 10.2 ч):
   <POOL_TABLE>
   (столбцы: файл | ref | паблик | CI | SEC | рычаги | UP-тест | L, ч)
   При равном паблике выбор такой (порядок записан до чтений):
   (1) файл, после которого МЫ обошли команды (UP-тест; 0 обойдённых = не решено);
   (2) без CI;
   (3) меньше рычагов;
   (4) отправлен раньше.
   Лучший файл без CI: V_nonCI = <V_NONCI_FILE> <V_NONCI_REF> (<V_NONCI_SCORE>).
   Лучший файл с CI: V_CI = <V_CI_FILE> <V_CI_REF> (<V_CI_SCORE>).
   Файл с SEC допустим только как основной (ваш ответ 28 сен 14:26 МСК), никогда как страховка.
   [если V_NONCI несёт SEC и V_NONCI ≠ V_pub] Пара П1 поставила бы SEC-файл в финал, хотя он не основной. По вашему ответу Q3 так нельзя без отдельного «да». Без него в П1 идёт <V_NONCI_NOSEC_FILE> <V_NONCI_NOSEC_REF> (<V_NONCI_NOSEC_SCORE>).
   [если V_pub = копия публичного ноутбука (E10)] Второй файл = лучший наш собственный файл: <OWN_BEST_FILE> <OWN_BEST_REF>.

2) ПАРЫ. Модель (оценка по одному эмбриону; ранжирует, но не решает) выше по бронзе у П1. Выбираете вы.
   П1 {<V_NONCI_FILE> <V_NONCI_REF>, exp75 <EXP75_REF>}: рычаги разнесены по двум файлам.
      Основной файл несёт cap 6 + K<V_NONCI_EXTRA>. exp75 = #37 + CI и несёт только CI. На привате засчитывается лучший из двух.
      Модель: бронза ~0.77–0.91, серебро ~0.50–0.74.
      Статус exp75: <EXP75_ROW>.
   [если V_CI ≥ V_nonCI по паблику и exp75 ≥ 0.955 и чистый]
   П2 {<V_CI_FILE> <V_CI_REF>, exp75 <EXP75_REF>}: CI в обоих файлах, CI не застрахован.
      Модель: бронза ~0.75–0.93, серебро ~0.59–0.78. При широком разбросе CI на привате (sd ≥ 0.0015) она на 0.03–0.08 ниже П1 по бронзе.
   П3 {<V_PUB_FILE> <V_PUB_REF>, #37 56563521}: #37 страхует всё сразу (cap 6, K, CI, SEC, DIS).
      Модель: бронза ~0.68–0.85, серебро ~0.51.
   [если exp89u отправлен] П4 {<V_PUB_FILE> <V_PUB_REF>, exp89u <EXP89U_REF>} (#37 + K): страхует только cap. В модели ниже П1 во всех 15 прогонах.
   Для сведения: {<V_PUB_FILE>, exp70g 56606948} ниже П1 во всех прогонах по бронзе, серебру и матожиданию.
   Сейчас отмечено {#37 56563521, #38 56563534}: бронза ~0.48–0.66, серебро ~0.10–0.23.
   Модель посчитана для основного файла exp85a (28 сен 16:18 МСК). Для другого V_pub её не пересчитывали.
   П1 выше П3, пока средний эффект CI на привате не ниже ~−0.0002…−0.0004. На паблике CI дал +0.001.

3) ЗАПАСНЫЕ ВАРИАНТЫ
   exp75 не прочитан, выдал ошибку, CI не отработал (NO-OP) или exp75 ≤ 0.953: партнёр #37 (пара П3).
   exp75 ≤ 0.953 или ошибка: пометка «риск CI» у основного файла с CI.
   [если проба 51 = «−»] Пометка «риск CI» у каждого файла с CI в этой карточке.
   exp75 = 0.954 и чистый: П1 и П3 почти равны; [если проба 51 = «−»] первой идёт П3.
   [если V_pub — файл с CI] exp75 идёт в пару только при ≥ 0.955 и только как обмен (правило R25).

4) РИСКИ РЫЧАГОВ (все чтения сделаны на одном публичном эмбрионе)
   cap 6: высокий. Паблик +0.002, лаборатория −0.0006, cap 8 и cap 12 на паблике по −0.001.
   SEC: высокий. In-sample −0.0016, замены весов на LB 0 из 5. Первый прогон на скрытых был этой ночью: <SEC_READ>.
   K: средний. Паблик +0.002 (проба 50). +0.84% узлов стоят ~−0.0008 на любом эмбрионе.
   DIS 2.25: ~0. Бонус за узлы ~+0.0007 уже учтён в dummy-лаборатории: −0.0008 на exp70g, +0.0004 на exp89p. exp13 не переносится. Паблик: <DIS_READ>.
   CI: средне-низкий. Паблик +0.001, один эмбрион. Проба 51: <C51_READ>.

5) ЕЩЁ НЕ ПРОЧИТАНЫ (PENDING)
   <PENDING_LINES>
   (одна строка на файл: «<файл> <ref>, отправлен <время МСК>, чтение ожидается <окно МСК>; если прочитается ≥ <порог>, основным станет он и пары выше меняются так: <замена>»)
   Если основной файл изменится, пришлю одну строку в 22:30 МСК (19:30 UTC)[если принято R27C-3: и ещё раз в 22:43 МСК (19:43 UTC)]. После чтения можно перевыбрать до 23:00 МСК.
   [если PENDING пуст] Все файлы прочитаны; ожидающих нет.

6) ОДИН ЭМБРИОН ИЛИ ДВА
   Участник g john rao пишет в обсуждении 743006 (28 сен 15:27 МСК; не подтверждено): в скрытом тесте два эмбриона, первый — приват, второй — паблик (но сплит может быть и смешанным).
   Если это так, все наши чтения относятся к одному эмбриону. Поэтому разнести рычаги по двум файлам важнее.

Как отметить: страница Submissions → найти два ref из выбранной пары → отметить ровно два → убедиться, что «2 of 2 selected».

=====

## ДЛЯ СЕССИИ: порядок заполнения (не отправлять)

1. Взять последний заголовок `=== <UTC>` из experiments/lb_poll/poll.log (не 429 и не ошибка DNS, не старше 15 мин) → `<HDR_UTC>`.
2. SELECTED прочитать только API: competition_submissions(group=SUBMISSION_GROUP_SELECTED) → `<SELECTED>` (refs + display). Ничего не отмечать.
3. Статус каждого ref взять из poll.log / ledger.md, по токену в `-m` (таблица ниже). Для CI-файлов L_hi взять из ledger (столбец L); L_hi > 10.2 ч → вне пула.
4. UP-тест: tools/uptest.py, S0 = последняя выгрузка ЛБ до окна завершения, S1 = первая после (experiments/lb_poll/_lb/). k = 0, MASKED или BLIND → «не решено», а не «ниже». Если во время окна наш показанный лучший не менялся и у другого файла паблик строго ниже, этот файл UP-тест не маскирует (R26-A4 (b)).
5. Пул и V_pub: максимум display среди COMPLETE; порядок (1)–(4). Число рычагов: #37 = 0; exp75 = 1 (CI); exp70g = 1 (cap 6); exp79a = 2; exp85a = 2 (cap 6, K); exp87a, exp89p, exp89s = 3; exp89q, exp89l = 4; exp89r = 5. Внутри K две ручки, но это один рычаг.
6. V_nonCI и V_CI выбираются тем же порядком внутри своих подмножеств. SEC-файлы: exp89p, exp89q, exp89r, exp89l, exp83c.
7. exp75: чистый = COMPLETE, не ERROR, dL = L_hi − 7.54 ч > 0.5 ч, L_hi ≤ 10.2 ч (при 9.6–10.2 ч добавить сноску «ins-tail?»). Строка `<EXP75_ROW>` по правилу v2: (a) ≥ 0.955 и чистый → «чистый, ≥ 0.955: модель ставит П1 выше П3»; 0.954 и чистый → «почти равный обмен с П3»; (b) V_pub с CI → правило R25; (c) ≤ 0.953 / ERROR / NO-OP → «выпадает, партнёр #37, пометка риска CI».
8. `<PENDING_LINES>`: каждый отправленный ref со статусом PENDING. Окна чтения (в UTC; в карточке писать МСК = UTC+3): не-CI K2 L 6.87–7.67 ч; CI L 9.27–9.45 ч, хвост до 10.9 ч; exp75 8.96–9.72 ч. DIS 2.25 время не меняет (раунд 27: разница dummy — в подготовке окружения, а не в ILP). Замена = «если ≥ display V_pub + 0.001 или равен с приписываемым UP — он становится V_pub; П1/П3 берут его».
9. Числа модели не пересчитывать. Если V_pub ≠ exp85a, оставить фразу «не пересчитывали».
10. Перед отправкой проверить: нет слова «рекомендую»; порядок (1)–(4) дословно; П2 подписана «CI в обоих файлах, CI не застрахован»; строка П4 есть только при отправленном exp89u; 743006 помечено «не подтверждено».

## ТАБЛИЦА ЗАПОЛНЕНИЯ (machine-readable)

```json
{
  "fixed_refs": {
    "#37 exp58 (K2 cap 4)": {"ref": "56563521", "display": "0.954", "ci": false, "sec": false, "levers": 0},
    "#38 exp58n (twin)": {"ref": "56563534", "display": "0.953", "ci": false, "sec": false, "levers": 0},
    "exp70g (cap 6)": {"ref": "56606948", "display": "0.956", "ci": false, "sec": false, "levers": 1},
    "exp79a (cap 6 + CI)": {"ref": "56623105", "display": "0.957", "ci": true, "sec": false, "levers": 2, "L": "(9.27, 9.45]"},
    "exp85a (cap 6 + K)": {"ref": "56629533", "display": "0.958", "ci": false, "sec": false, "levers": 2, "UP": 21},
    "exp87a (cap 6 + K + CI), probe 51": {"ref": "56640366", "display": "PENDING at 15:41Z 28 Sep", "ci": true, "sec": false, "levers": 3}
  },
  "token_refs": {
    "exp89r | exp89q (00:05Z stack)": {"match": "-m starts 'probe 52: exp89r = ' or 'probe 52: exp89q = '", "ci": "exp89r yes / exp89q no", "sec": true, "levers": "5 / 4", "read_window_utc": "exp89q 07:02-07:45; exp89r 09:21-09:32 (tail 11:00)"},
    "exp75 (#37 + CI)": {"match": "'probe 53: exp75 = '", "ci": true, "sec": false, "levers": 1, "read_window_utc": "09:04-09:49 (tail ~10:06)"},
    "exp89p (K + SEC)": {"match": "'probe 54: exp89p = '", "ci": false, "sec": true, "levers": 3, "read_window_utc": "07:38-08:26"},
    "fallback exp83c": {"match": "'exp83c'", "ci": true, "sec": true, "levers": 3},
    "morning M1/M2 (exp89l | exp89s | exp89q | UNUSED)": {"match": "-m 'probe 55: ' / 'probe 56: '", "per_table": "MORNING TABLE v1.1", "exp89l": {"ci": true, "sec": true, "levers": 4}, "exp89s": {"ci": false, "sec": false, "levers": 3}},
    "exp89u (only on the user's yes)": {"match": "'exp89u'", "ci": false, "sec": false, "levers": 1}
  },
  "placeholders": [
    {"ph": "<T_MSK>/<T_UTC>", "source": "wall clock at fill", "fill": ["12:03Z", "18:37Z"]},
    {"ph": "<HDR_UTC>", "source": "last '=== ' header in experiments/lb_poll/poll.log (not 429 / not DNS error, <= 15 min old)"},
    {"ph": "<SELECTED>", "source": "read-only API competition_submissions(group=SUBMISSION_GROUP_SELECTED); expected {56563521, 56563534} unless the user re-ticked"},
    {"ph": "<RANK>/<TEAMS>/<BEST_DISPLAY>/<BLOCK_POS>", "source": "newest experiments/e10_watch/<ts>.txt or experiments/lb_poll/_lb/ download; our TeamId row"},
    {"ph": "<POOL_TABLE>", "source": "all COMPLETE refs at max display (fixed_refs + token_refs) with CI L_hi <= 10.2 h and the insertion gate not fired; UP column from tools/uptest.py"},
    {"ph": "<V_PUB_FILE>/<V_PUB_REF>/<V_PUB_SCORE>/<V_PUB_KIND>", "source": "POOL + tie order (1)-(4); KIND = 'без CI' | 'с CI' (+ ', с SEC')"},
    {"ph": "<V_NONCI_*>", "source": "same order over COMPLETE non-CI refs: exp85a 56629533, exp89q, exp89p, exp89s, E10 copy; exp70g 56606948 as floor"},
    {"ph": "<V_NONCI_NOSEC_*>", "source": "best COMPLETE non-CI non-SEC ref: exp85a 56629533 or exp89s"},
    {"ph": "<V_NONCI_EXTRA>", "source": "extra levers of V_nonCI beyond cap 6 + K: '' (exp85a) | ' + DIS 2.25' (exp89s) | ' + SEC' (exp89p) | ' + SEC + DIS 2.25' (exp89q)"},
    {"ph": "<V_CI_*>", "source": "same order over COMPLETE CI refs: exp87a 56640366, exp89r, exp89l, exp79a 56623105, exp83c"},
    {"ph": "<EXP75_REF>/<EXP75_ROW>", "source": "token 'probe 53: exp75 = '; status + display + L_hi + dL (= L_hi - 7.54 h); row per EXP75 PARTNER RULE v2 (CONTEXT 28 Sep 14:12 UTC)"},
    {"ph": "<EXP89U_REF>", "source": "only if exp89u was submitted (needs the user's yes); else delete row П4"},
    {"ph": "<SEC_READ>", "source": "MORNING TABLE v1.1 code P = exp89p vs exp85a ('+' >= 0.959 / '0u' / '0' / '-' <= 0.957 / '?') with display, ref"},
    {"ph": "<DIS_READ>", "source": "MORNING TABLE v1.1 DIS code (branch B: exp89q vs exp89p; branch A: dd = (exp89r - exp89p) - (exp87a - exp85a), '+' only if dd >= +0.002 and exp89r > max(exp87a, exp89p)); 'не прочитан' if pending"},
    {"ph": "<C51_READ>", "source": "probe 51 code vs exp85a 0.958: '+' >= 0.959 / '0u' / '0' / '-' / '?' with display, ref 56640366"},
    {"ph": "<PENDING_LINES>", "source": "every submitted ref still PENDING at fill; windows from token_refs / ДЛЯ СЕССИИ step 8"},
    {"ph": "<OWN_BEST_FILE>/<OWN_BEST_REF>", "source": "only if V_pub is an E10 copy: best own COMPLETE ref by the same order"}
  ],
  "fill_times": {"proposal_1": "12:03Z = 15:03 MSK", "proposal_2": "18:37Z = 21:37 MSK", "notify_only": ["19:30Z = 22:30 MSK", "19:43Z = 22:43 MSK"], "tick_by": "20:00Z = 23:00 MSK", "kaggle_close": "23:59Z = 02:59 MSK 30 Sep"}
}
```
