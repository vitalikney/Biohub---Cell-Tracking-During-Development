# Промпт для ассистента Friend A (Sasyami, RTX 5070 Ti 16 ГБ) — актуален на 2026-09-11 00:00

Скопировать целиком в ассистента, запущенного в клоне репозитория (ветка `detector-baseline-v2`).

---

Ты работаешь в репозитории соревнования Kaggle «Biohub – Cell Tracking During Development», ветка `detector-baseline-v2`,
машина Friend A (RTX 5070 Ti 16 ГБ, Windows, Python 3.12, данные в `C:\Projects\CellTracker\train`). Сначала `git pull origin main`
в свою ветку, затем прочитай TEAM.md (раздел «Friend A — order of work, revised 2026-09-10 18:00», включая блок STEP 1b RESULT и
варианты (a)–(e) в STEP 2) и CONTEXT.md §10a и §14 (записи от 2026-09-10, особенно «REVIEW of the dense fine-tune» 23:30).

Контекст: обучение с нуля закрыто (STEP 1: честные 0.680 на 44b6; STEP 1b: 0.833 на своих 6bba, значит главная проблема — сдвиг
между эмбрионами). Плотные метки идут в ДООБУЧЕНИЕ весов pilkwang. Проверка по коду показала, что плотные метки не меняют
обучение линкера (teacher-узлы без рёбер были нулевыми столбцами и при разреженной разметке), поэтому обычное совместное
дообучение — корректный A/B, а двухстадийный вариант — эксперимент, не исправление.

Твой конвейер `experiments/local_friend_a_exp03_dense_ft_primary/` (step1c → step2_variants → step3_winner) уже переведён
на дообучение primary. Задача:
1. Если где-то ещё крутится старое обучение с нуля (команда с `--epochs 20` без `--init-weights`) — останови, результаты не нужны.
2. STEP 1c: учитель для 126 видео 6bba + 12 видео 44b6 и сборка `train_dense/` через `tools/build_dense_gt.py`, если папок
   `teacher_geff/` и `train_dense_geff/` ещё нет в датасете `vitaliineibauer/biohub-ft-weights`. Выложить их и написать в чат.
3. STEP 2: сверь `step2_variants.py` с этим списком и прогони по порядку, каждый вариант около часа. Общие параметры:
   `--init-weights <pilkwang primary: support-pack weights/unet_transformer/split_0/edge_predictor_best.pth>`, `--max-iters 1200`,
   `--lr 5e-5` без косинуса, `--det-loss bce`, `--max-detections 0`, `--seed 42`, разбиение `experiments/_lib/loeo_train6bba_val44b6.json`.
   Оценка: сырое предсказание на 12 видео 44b6 с `--det-threshold 0.965 --use-ilp --ilp-appearance-weight 0
   --ilp-disappearance-weight 2 --ilp-division-weight 1.2` и `tools/score_geffs.py`; записывать score, edge_jaccard, node_recall, N_pred/N_est.
   0. эталон: то же дообучение на РАЗРЕЖЕННОЙ разметке (обычная папка train) — ожидается около 0.8825, как exp11 B;
   1. плотные метки (`BIOHUB_DATA_DIR=train_dense`), 1200 итераций;
   2. плотные метки, 2400 итераций;
   3. плотные метки, 1200 итераций, `--det-neg-weight 0.1`;
   4. плотные метки, 1200 итераций, `--aug-intensity` с уменьшенными вдвое диапазонами (в `experiments/_lib/train_patches.py`
      поправить константы: gain 0.8–1.25, offset ±0.1, gamma 0.8–1.25, без haze; закоммитить как отдельный флаг или пометить в RESULTS);
   5. двухстадийный: стадия A `--freeze linker --edge-loss-weight 0 --max-iters 1200` на train_dense, затем стадия B
      `--init-weights <лучший чекпоинт стадии A> --freeze detector --max-iters 600 --lr 5e-5` на обычной папке train
      (флаги `--freeze` и `--edge-loss-weight` уже есть в `experiments/_lib/train_patches.py` после `git pull`).
   Вариант считается победившим, если он лучше эталона 0 на 0.005 и больше.
4. STEP 3 только для победившего варианта: то же дообучение на 183 видео (список `train` из `experiments/exp03_finetune_ab/config.py`),
   веса с config.json в датасет как `friend_a_ft_dense_primary/`, сообщить Виталию — он ставит одну пробу на LB как primary.

Каждый прогон: строка в experiments/RESULTS.md, короткая заметка в CONTEXT.md §14, коммит в свою ветку (без данных, весов
и предсказаний в git). Перед долгим запуском — smoke-тест на 1–2 видео. На leaderboard ничего не отправлять. Если шаг невозможно
выполнить как описано, объясни причину и предложи ближайший рабочий вариант, но не меняй рецептуру без пометки в RESULTS.md.
