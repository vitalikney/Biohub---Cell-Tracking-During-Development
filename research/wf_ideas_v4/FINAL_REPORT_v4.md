# Итог идей v4 (финальный судья), пт 25 сентября 2026, ~18:20 UTC (21:20 МСК)

Входы лежат в `research/wf_ideas_v4/`:
- `intel_browser.json` и `.notes.md`: браузер и CLI Kaggle, 16:51–17:21 UTC;
- `lens_*.json`: 6 линз;
- `v_*.json`: по два скептика на каждую из 21 идеи;
- `final.notes.md`: лог судьи, включая свежий LB на 18:08 UTC.

План v3 (`research/wf_ideas_v3/FINAL_REPORT.md` §e/§f, копия в `CONTEXT.md` от 13:38 UTC) остаётся предрегистрацией. R1–R10 не переписываются. Ниже только добавки: проверки, уточнения двусмысленного текста и одна новая стадия. Всё, что меняет §f или ослабляет ворота, помечено **[нужен OK]**.

---

## 1. Итог

1. **Ветка A и K2 не меняются.** K2 = x138 + safetail + lowrefine + вставка идёт в 00:01 UTC 26.09, все 18/18 ворот дамми зелёные.
2. **Нового рычага на +0.002 без переобучения не нашлось.**
   - Плечо 0.954–0.956 на LB, похоже, дают переобученные модели. Единственный двигатель с публичным кодом, y3uanm (0.949 → 0.956), дообучает вторичный детектор seed314159 с дистилляцией. Это закрыто R9.
   - Все стадии хвоста, которые можно проверить без обучения, либо уже есть в x138, либо на наших данных ничего не делают:
     - RE-AIM команды Corwin (#17) правит 2 ребра из 117 077 на дамми K2, TP/FP/FN не меняются;
     - pair-LightGBM — это та же ловушка in-sample, что и edge filter;
     - полифазный TTA — закрытый класс TTA.
3. **Главная поправка касается финалов: F2 = двойник без вставки (exp58n) вместо exp52.**
   - exp52 на public на 0.003 ниже x138. У него тот же V1284-head и та же вставка, что у F1, поэтому он проваливается в тех же мирах, что и F1.
   - Двойник exp58n = x138 + C01 + lowrefine, то есть K2 без вставки. Он страхует самый неопределённый компонент F1, вставку DaughterNet. Её +0.001 на LB — примерно одно событие деления на public, измеренное дважды на одних и тех же клипах.
   - По MC обоих скептиков P(private max(F1, F2) > x138) растёт на +0.01…+0.05 против exp52, а в мире «вставка на private хуже» до +0.15. Средний счёт на private не меняется. Это страховка ранга у обрыва «бронза / без медали».
4. **Сегодня вечером есть одно срочное дело.** Правила чтения лаборатории exp60 надо записать в CONTEXT **до первого `python tools/trainlab.py score`**. Шарды A/B в 18:08 UTC ещё RUNNING, выход ожидается ~19:15–20:30 UTC. Готовый текст — в Приложении A. Там же найден дефект в коде ворот K3b: точность добавленных вилок делится на все новые вилки, включая игнорируемые метрикой. Из-за этого ворота при понижении порога почти непроходимы, а при повышении проходят пусто.
5. **Новая стадия одна: forkblob (L1).**
   - Что делает: снимает безопасную вилку, если на t+1 обе дочери лежат на одном пятне (сёстры ≤ 5 мкм, долина ≥ 0.95).
   - Узлы не трогает, работает < 1–2 с на клип.
   - Независимая проверка на старой базе по 199 клипам: в клетку попали 3 FP, 0 TP и 65 свободных вилок.
   - Центр оценки +0.0005 public, P(< 0) ~0.2. На x138 это по сути пост-фильтр «сёстры ≥ 5 мкм». Априор: проба 18 (такой же порог до линковки) дала ничью 0.946 против 0.947.
   - Едет в K3 рядом с forkmid, если пройдёт собственный лабораторный гейт вреда. **[нужен OK]** на класс R3.
6. **Честный прогноз.**
   - Public F1 ~0.954 (80%: 0.953–0.955), P(≥ 0.955) ~0.15.
   - Private: P(хотя бы один финал > x138) ~0.9 с двойником (догадка по MC).
   - Бронзы это уже может не гарантировать. Команд выше сырого x138 на public сейчас ~229 (195 с ≥ 0.954 и ~34 в блоке 0.953 выше копии Kunal Desale). Число команд с ≥ 0.954 растёт на ~2–3 в час: 92 → 192 → 195 за 32 ч. Граница бронзы (~390) к 29.09, вероятно, уйдёт выше x138. P(бронза) грубо ~0.5, P(серебро) ~0.1–0.2. Это догадки.

## 2. Новые факты Kaggle

- **LB 18:08 UTC** (CLI, мой снимок; `final.notes.md`):
  - всего 3 905 команд;
  - блоки по рангам: 0.957 — 66–77, 0.956 — 78–98 (21 команда), 0.955 — 99–133 (35), 0.954 — 134–195 (62), 0.953 — 196–456 (261);
  - **мы #151, 0.954**, 37 сабмитов;
  - граница серебра (ранг ~195) совпадает с последней строкой блока 0.954, граница бронзы (ранг ~390) лежит внутри блока 0.953, золото (ранг ~17) = 0.966;
  - Kunal Desale (побайтовый x138) на #230; автор x138 Anvith Pothula — 0.956 (#83).
- **Порядок внутри одного показанного счёта идёт по неокруглённому счёту, а не по времени:** 34 из 43 команд ниже нас в блоке 0.954 сабмитили раньше нашего #35. Время решает только среди побайтовых копий (Rules 3.7.b). Поэтому предупреждение v3 «поздняя копия встанет в конец блока» касается только побайтовых копий.
- **Медали дают** (в сайдбаре «Awards Points & Medals»).
- **Публичного ноутбука выше 0.953 нет.** В обсуждениях с 11:40 UTC нет ни новых тем, ни новых комментариев. Темы про время работы старые: 724914 — таймаут при видимом прогоне ~5.6 ч; 724917 — скоринг занимает ~1 мин.
- **corwin1979/biocel-aux-4d9e2c17** (CC0, Corwin #17, 0.965): RE-AIM, пара-LightGBM, MITO3, HOCT-вето. На x138 RE-AIM ничего не делает (замерено). Остальное либо обучено на train GT (in-sample), либо относится к закрытым линиям. Код лежит в `experiments/ext_corwin-biocel-aux/`.
- **y3uanm** (0.949 → 0.956): дообучение вторичного детектора с учителем плюс синтетика José (`experiments/ext_y3uanm-secondary-ft/`). Закрыто R9. Команда easonyanyan (0.954) включает georgexue666, автора pool2-детектора.
- **Операционное.**
  - Лаборатория exp60 A/B: RUNNING в 18:08 UTC.
  - P36 (exp57, диагностика leaf prune): PENDING в 17:58 UTC.
  - Квота GPU: ~21:13 из 30 ч к ~18:10. Сброс ожидается в сб 00:00 UTC, но это не подтверждено.

## 3. Поправки к плану по приоритету

| # | Поправка | Когда / слот | Ворота | Реальный выигрыш | OK |
|---|---|---|---|---|---|
| 1 | **Дописка к предрегистрации лаборатории** (Приложение A, п. L1–L2, L5): чтение плато DC = «без контрольного соседа»; точность K3b считается только по оцениваемым вилкам и дополняется условием И (n ≥ 6, нижняя граница Уилсона 80% > 0.265); вставочные рукава помечены как «in-sample верхняя граница»; nosteal0 закрыт | **до ~19:00 UTC сегодня**, до первого `trainlab.py score` | метка времени в CONTEXT раньше выхода exp60 | 0 на счёт; убирает развилку и баг гейта K3b; освобождает S5 почти наверняка | L1 — уточнение, **[нужен OK]** утром, до утра действует как записано |
| 2 | **F2 = двойник без вставки exp58n** (правка §f «f2»). exp52 остаётся только запасным | сборка и дамми сегодня ночью (после сброса квоты); сабмит 26.09 в S3 (~07:00–09:00 UTC, после OK) | `dummy_gates.py --insertion 0`; строки узлов (без столбца id) == дамми K2; рёбра отличаются только в местах вставок и краж K2; нет FAILED/DEADLINE | 0 на public; private +0.01…+0.05 P(> x138) против exp52 | **[нужен OK]** на правку §f и на сабмит |
| 3 | **forkmid: гейт с учётом мощности** (Приложение A, п. L3): считаем по всем 56 клипам вместе; снято 0 TP; снято ≥ 3 FP; убрано мёртвое условие «≥ 1 на 44b6»; условие на максимум заменено на «не больше 1 TP-вилки с серединой в [3.8, 4.5)»; adj_edge по всем клипам ≥ −0.0002; поправка на базу без lowrefine | текст — до скоринга; K3 в S4 | старый гейт T9 тоже считается и отчитывается | public ~+0.0001, private +0.0001; P(K3 с forkmid) 0.08 → ~0.3 | **[нужен OK]**; без OK действует старый гейт |
| 4 | **forkblob (L1)**: пороги заморожены сейчас (Приложение A, п. L4); патч `--patch forkblob` (выключен по умолчанию, при выключении побайтно, fail-soft), рукав в trainlab, гейт вреда | патч и тесты 20:00–23:00 UTC; лаборатория ночью; дамми K3 после сброса; S4 26.09 (запас S7 ≤ 27.09 12:00) | лаборатория: вето TP ≤ 1 и (TP = 0 или FP ≥ 3·TP), доза ≥ 10%, div_J по всем клипам ≥ контроля, adj_edge ≥ −0.0002; дамми: узлы == K2, набор снятых рёбер == офлайн-функции, счётчики > 0 на 6bba_05db0fb1, sha при ENABLE=0 == K2 | public +0.0005 центр (−0.0035…+0.003), private +0.0005…+0.001; с учётом P(гейт) ~+0.0003 | **[нужен OK]** на класс R3 и на сабмит K3 |
| 5 | **Журнал времени и триггеры** (слияние H1, L2, D4 и RT4a): `dummy_gates.py` пишет только отчёт (WARN, не FAIL) — Δ починки на клип против K2 и прогноз F = L(K2) + 97·Δ·1.15; дедлайны остаются 28 800 / 34 200; **опросчик LB живёт 07:00–08:30 UTC** (COMPLETE до 08:01 доказывает, что гейт вставки не сработал) | до 07:00 UTC 26.09 | триггер: L(K2) > 8.0 ч или F > 7.9 ч → D4 (точный двухэтапный скоринг, sha == K2) и/или перенос ОБОИХ дедлайнов 32 400 / 37 800; никогда не двигать только DIVINS | ~0 в ожидании (~1e-5); защищает от молчаливой потери вставки в медленном мире | журнал — нет; триггер — **[нужен OK]** |
| 6 | **Запас на случай ошибки K2 и уточнение §f:** если K2 упал, K1 (exp58t v1, уже прошёл ворота) идёт в следующий слот 26.09, K3 пересобирается на K1. Пункт 4 запасного списка §f (#34) остаётся последним средством перед exp52 | 26.09 после счёта K2 | счёт K2 = ошибка | сохраняет день в мире P ~0.02–0.03 | **[нужен OK]** |
| 7 | **Закрыть в CONTEXT** RE-AIM, pair-GBM и E13/C08 (формулировки — Приложение A, п. L7); записать ловушку FD (0.9249 против 0.9180 локально — in-sample, как #21/#29); отменить шаг 0 C08 у друга C | сегодня | — | 0; экономит 4–8 агент-ч и 1–2 слота | нет |
| 8 | **Наблюдение за рангом:** строка в статусе — наш ранг, края блоков 0.953/0.954, число команд ≥ 0.954 и выше X, пороги 5%/10% по текущему числу команд; снимки LB 26.09 и 27.09 ~09:00 UTC | ежедневно | только информация, ничего не решает | 0; не даёт перепутать public-серебро с private и спутать «чуть выше x138» с бронзой | нет |
| 9 | **Расширение 6bba для K3b (M2), условно:** только если 39-клиповая дуга прошла E5 (п. L1–L2), 78 чистых клипов 6bba (17 делений, head-стемы исключены, честная база 105 делений) — 2 шарда, только вето | 26.09 00:05–10:00 UTC, если квота сбросилась; иначе не делаем | вето, если дельта по объединённым CONF+EXT при t* < 0 или точность оцениваемых новых вилок < 0.35; результат к 10:00 UTC, иначе решаем без него | ~0 (ценность информации ≤ 2e-5); P(понадобится) ~0.3 | нет (входит в одобренные ~5 GPU-ч на exp60) |
| 10 | **Ворота K4 (tempfuse), только если его всё же соберут до 26.09 12:00:** точный зажим top-K по кадру; сырые узлы == двойнику с TEMPFUSE=0; финальные узлы ≤ +0.3% на клип; detected+readmitted ±0.3%; readmit/gapfill в отчёт, но не в гейт; GPU ≤ двойник + max(2%, 20 с); LOWDET ±10% вместо «== exp56» | до пуша дамми exp61 (≤ 27.09 06:00) | как в описании | условно +0.0002; безусловно ~+0.0001 | нет (ворота только строже R7) |

**Слоты 26–27.09 после поправок:**
- S2: K2, 00:01.
- S3: двойник exp58n (после OK).
- S4: K3 = K2 + [forkmid, если его гейт прошёл] + [forkblob, если его гейт прошёл]. Если не прошёл ни один, слота нет.
- S5: K3b, только если E5 проходит с условиями L1–L2 (ожидаем «нет»).
- S6: K4 или пусто.
- S7: сдвинувшийся K3.
- S9–S11: резерв, в том числе K1 по п. 6.
- S12: консолидация, как в v3. Консолидированный файл добавляется к кандидатам, прежние K-файлы остаются.

Чего не делать:
- не ставить отдельную вилочную стадию во второй слот того же дня, если ни одна не прошла гейт;
- не выбирать между почти-копиями по 0.001 (R7);
- не пересобирать двойник под F1-final: exp58n без вилочных наездников уже и есть максимальная страховка.

## 4. Отвергнутое (одна строка: причина, файл)

- **RE-AIM (Corwin):** 2 правки из 117 077 рёбер на дамми K2, TP/FP/FN = 2 047 / 101 / 80, то же, что без него. Дублирует глобальную flow-перелинковку x138. `_rewrite` дублирует id. `v_intel_reaim-*`.
- **pair-GBM как бонус перелинковки:** обучен на train GT, поэтому in-sample, как edge filter. Потолок ≤ +0.0018, P(LB ≥ +0.002) ~0.05–0.1. В x138 нужны ещё 2 прохода перелинковки. `v_intel_pair-gbm-*`.
- **H1 по умолчанию (дедлайн починки 10.5 ч):** ровно 0 при любом прогоне быстрее ~1.2–1.4× от #35. Оставлен только как триггер в п. 5. `v_headroom_h1-*`.
- **H2, полифазный вид детекции + tempfuse:** вес вида 1/9 даёт ~0.4 от шумоподавления полной полифазы. Это закрытый класс TTA, честной лаборатории нет, и он выталкивает прогноз за гейт вставки 8.0 ч. `v_headroom_h2-*`.
- **D4 безусловно (двухэтапный скоринг + гейт 9.5 ч):** EV ~1e-5. Перенос гейта отдельно вреден. Оставлен только как триггер в п. 5. `v_divisions-x138_d4-*`.
- **L2, DIVINS 32 400 без REPAIR:** в медленном мире вставка съедает бюджет починки следующих клипов, при s ≥ 1.2–1.3 это −0.0006…−0.002. `v_literature_l2-*`, `v_redteam-plan_rt4-*`.
- **L3, спасение вилок, отвергнутых DeepCenter, по картинке:** в пуле ~2% GT-делений, точность 4–15% против безубыточности 0.265. Через фильтр коротких треков меняет узлы. `v_literature_l3-*`.
- **Калькулятор пар как MC-решатель финалов:** ложная точность, калибровка на in-sample лаборатории. Правило (1) «стек + вариант» проигрывает двойнику при sd вставки ≥ 0.001. Заменён фиксированным правилом п. 2. `v_private-finals_finals-pair-calculator_*`.
- **pair-aware-slot-use:** пункты (1) и (3) уже есть в плане. «Не консолидировать» неверно, потому что S12 добавляет опцию, а не убирает. `v_private-finals_pair-aware-*`.
- **RT1, сабмит K1 в 00:01 без условий:** одобрения нет, ни одно правило не использует его счёт, это последний резервный слот дня. Оставлен запасной вариант п. 6. `v_redteam-plan_rt1-*`.
- **RT2 п. (1) и (2):** переклассификация lowrefine/forkmid из R3 переписывает R3 по шуму округления (эффект ~1e-4). Удаление #34 из запасного списка теряет последнее средство. `v_redteam-plan_rt2-*`.
- **RT3, два лишних GPU-шарда лаборатории на базе с lowrefine:** ценность информации ~2e-5. Заменены проверкой без GPU (п. L3). `v_redteam-plan_rt3-*`.
- **RT4, ворота времени как FAIL и пересборка только с DIVINS:** порог GPU внутри шума одинакового кода (+25 с/клип между exp56 и K2), EV пересборки отрицательный. Остались журнал в режиме отчёта и заметка о ловушке FD. `v_redteam-plan_rt4-*`.
- **D1, OOF-пересчёт вставки как вход решения:** ни одно решение от него не зависит (R2 уже решён по LB, R4). Оставлены метки и закрытие nosteal0. Пересчёт — диагностика, если GPU простаивает. `v_divisions-x138_d1-*`.
- **D3 как замена гейта T9:** местами он мягче закодированного гейта. Принят как дополнительное условие И (п. 1). `v_divisions-x138_d3-*`.
- **M2 без условий (3 шарда):** в счёте ошибка (честная база 105 делений, а не 128), ценность информации ~2e-5. Оставлен условный вариант (п. 9). `v_mine-old_m2-*`.

## 5. Что нужно от пользователя (утром 26.09, до ~09:00 UTC = 12:00 МСК)

1. **OK на правку §f «f2»:** F2 = exp58n (двойник K2 без вставки) вместо exp52 и сабмит exp58n в свободный слот 26.09. Без OK F2 остаётся exp52 по §f.
2. **OK на уточнения лабораторных ворот из Приложения A.** Оба варианта посчитаны; до OK действуют исходные ворота T9.
   - L1: плато DeepCenter читается «без контрольного соседа».
   - L3: гейт forkmid с учётом мощности.
3. **OK на forkblob** как наездника класса R3 (как C04) и на сабмит K3 с ним, если пройдут лаборатория и дамми.
4. **OK на запасной вариант:** если K2 упал, K1 идёт в следующий слот 26.09.
5. **Только если сработает триггер п. 5** (L(K2) > 8.0 ч): OK на перенос обоих дедлайнов или на D4.
6. **Другу C:** шаг 0 C08 в `TASK_FRIEND_C.md` отменён.
7. Напоминание: финалы отмечаются вручную до 29.09 20:00 UTC. Кандидаты: F1 = самая полная принятая K-сборка, F2 = exp58n (или exp52 по §f).

---

## Приложение A. Текст для CONTEXT.md (коммитить ДО первого `trainlab.py score` на выходе exp60)

```
- 2026-09-25 <HH:MM> UTC, PRE-REGISTRATION v3 ADDENDUM L (lab reading of exp60; written before any exp60 output was
  downloaded or scored; source research/wf_ideas_v4/FINAL_REPORT_v4.md). Items marked [OK] take effect only with the
  user's morning OK; until then the original T9 text applies. Both versions are computed and reported.
  L1 [OK, clarification] DeepCenter plateau (T9 "M1"): neighbours = non-control grid neighbours of t* (the control 0.25
     has delta 0 by definition); i.e. trainlab 'pass_noncontrol_plateau', ANDed with L2.
  L2 [bug fix + tightening] "precision of added forks >= 0.35" is computed over EVALUABLE new forks only
     (TP/(TP+FP) on 6bba CONFIRMATION; trainlab _fork_precision currently divides by all new forks). Added AND clauses:
     n_evaluable_added >= 6 and one-sided Wilson 80% (z = 1.2816) lower bound > 0.265. Existing checks stay (conf >=
     +0.002 at t*, plateau per L1, 44b6 >= -0.0005, forks <= +50%, nodes unchanged). t* > 0.25: no build (removal
     branch unreachable). Report (info only) the share of marginal forks that fall in the forkblob cell (L4).
  L3 [OK, power fix] forkmid C04 audit, pooled over all 56 clips: 0 TP safe-division forks removed; removed evaluable
     FP >= 3; <= 1 lab TP fork with midpoint in [3.8, 4.5) um (replaces the max-margin clause); pooled adj_edge delta
     >= -0.0002; nodes and inserted forks unchanged. The '>= 1 FP on 44b6' clause is dropped (lambda_44b6 ~0.1-0.4).
     Sensitivity (lab base has no lowrefine): the gate must still pass when fork rows touching a readmitted lowdet node
     are counted as adverse. exp39's 0/23 is never used in any bound (4.5 um was chosen on it).
  L4 [rule frozen now; R3 class needs OK] forkblob: for every 2-child fork with safe_division == 1 and not
     div_inserted, at t+1: sister distance <= 5.0 um AND valley >= 0.95, valley = min of the interior 20-80% of 41
     samples of the gaussian-blurred (sigma zyx 0.6/1.5/1.5 vox, local crop, margin >= 4 sigma) intensity on c1->c2,
     divided by min(I(c1), I(c2)); drop the ILP-side edge if edge_prob == 0.0 else the added edge; runs after
     forkmid; nodes untouched. Lab harm gate (pooled 56 clips): vetoed evaluable TP <= 1 and (TP == 0 or FP >= 3*TP);
     pooled div_J(arm) >= control; >= 10% of control safe-division forks fall in the cell (dose); pooled adj_edge
     delta >= -0.0002; nodes unchanged. Log per vetoed fork: dropped edge, its edge label, the fork's division label.
     Thresholds come from GT sister statistics of all 151 train divisions (no fork labels seen). Prior: on the old
     base (exp39 graphs, 199 clips) the cell holds 3 FP / 0 TP / 65 free; probe 18 (pre-link 5 um floor) tied 0.946 vs
     0.947 -> an LB tie is not a failure, +0.001 is not a confirmation.
  L5 ins35 / ins35_nosteal0 / ins35_forkmid45 arms are 'IN-SAMPLE UPPER BOUND (4/5 DaughterNet v1 folds saw these
     clips)'; the T9 insertion check is a warning only; nosteal0 is CLOSED under R2 whatever the lab shows.
  L6 [conditional] 6bba extension: only if the 39-clip 6bba bed passes the full E5 gate (L1+L2), push the 78 clean
     6bba clips outside exp60 (17 GT divisions; the 10 head-train stems incl. 05db0fb1 excluded; honest pooled bed
     105 divisions) as 2 shards after the K3/twin dummies; veto K3b if the pooled 6bba CONFIRMATION+EXT delta at t* < 0
     or the evaluable new-fork precision < 0.35. Result not in by 10:00 UTC 26 Sep -> decide on the 39-clip bed.
  L7 closures: RE-AIM on x138/K2 = no-op (K2 dummies: 2 of 117,077 edges re-pointed; TP/FP/FN 2,047/101/80 with and
     without it); pair-GBM relink bonus closed (in-sample booster; reopen only on a full-stack public delta >= +0.002
     or an honest OOS check); E13/C08 closed on schedule (R8) plus small ceiling (5/82 end-anchored node misses);
     births/optional nodes stay closed on the LB anchors (gapfill 0, readmit -0.001, det 0.95 flat, MIN_TRACK_LEN 4
     -0.002), not on the anatomy share. FD dummy 0.9249 vs K1 0.9180 locally is an in-sample artefact (one clip
     +0.023; probes 21/29 show this 'trust ILP over relink' pattern gives 0 or less on LB): never act on it.
```

## Приложение B. Текст правки §f «f2» (коммитить до первого счёта наездника, т.е. до ~09:00 UTC 26.09)

```
- PRE-REGISTRATION v3 AMENDMENT f2 [needs the user's OK]: F2 = exp58n (x138 + safetail + lowrefine = K2 minus the
  DaughterNet insertion; no fork riders) if scored without error, R5-admissible and public >= 0.953; its dummy gate:
  tools/dummy_gates.py --insertion 0, node rows (id column stripped) == K2 dummy, edges differ from K2 only at K2's
  inserted/steal forks, no DIVINS/DEADLINE/REPAIR FAILED/LOWREFINE FAILED lines. exp52 only if the twin is unscored,
  failed, or in branch D. A DeepCenter/tempfuse variant that R4 makes an 'F2 candidate' does not displace the twin.
  The twin's score never reopens R2 unless twin - K2 >= +0.002 (R7). The S12 consolidated file joins the candidate
  set; earlier scored K files stay candidates. §f fallback item 4 (#34) stays as the last resort before exp52 ('never
  tick exp56' applies while any admissible non-copy x138-family file exists). Never tick two files with identical
  components. The finals objective is P(private > raw x138) first, silver second.
```
