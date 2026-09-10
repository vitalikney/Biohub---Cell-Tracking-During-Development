# Промпт для ассистента Friend B (gsfatakhov, RTX 5070 12 ГБ) — актуален на 2026-09-10 20:00

Скопировать целиком в ассистента, запущенного в клоне репозитория (своя ветка `friend-b`).

---

Ты работаешь в репозитории соревнования Kaggle «Biohub – Cell Tracking During Development». Сначала прочитай TEAM.md целиком
(особенно «Friend B start kit» и «Friend B — order of work, revised 2026-09-10 18:00»), затем CONTEXT.md разделы §1, §4, §10a и §14.
Я — Friend B (Kaggle gsfatakhov), видеокарта RTX 5070 12 ГБ, Windows, Python 3.12. Данные лежат в
`biohub-cell-tracking-during-development/train` (для начала достаточно 12 видео 44b6 и 126 видео 6bba из
`experiments/_lib/loeo_train6bba_val44b6.json`). Веса скачивай через `kaggle datasets download` (ссылки в TEAM.md).

Выполняй раздел «Friend B — order of work» строго по порядку:
- STEP 1: детекции-учителя на всех 199 видео (ансамбль exp03B + seed314159, порог 0.965, без ILP). Перед стартом проверь в датасете
  `vitaliineibauer/biohub-ft-weights` и в чате, не сделал ли это уже Friend A (папки `teacher_geff/`, `train_dense_geff/`);
  если сделал — пропусти STEP 1 и STEP 2 и используй его файлы. Готовый сборщик плотных меток уже есть: `tools/build_dense_gt.py`.
- STEP 2: плотный набор `train_dense/` (узлы = учитель ∪ GT с дедупликацией 5 мкм, GT главнее; рёбра только GT; zarr через junction;
  `dense_stats.csv`).
- STEP 3: дообучение ВТОРИЧНОЙ модели pilkwang seed314159 на плотных метках только 6bba (1200 итераций, lr 5e-5, bce,
  `--max-detections 0`, batch 4 с gradient checkpointing для 12 ГБ), плюс такое же дообучение на разреженной разметке;
  скор обоих на 12 видео 44b6. Плотный вариант принимаем, если он лучше разреженного на 0.005 и больше.
- STEP 4 (параллельно, CPU): локальный порт пост-обработки публичного ноутбука по «Friend B start kit» с кэшем GPU-стадий; первые
  сравнения на нём — варианты TTA-стека из CONTEXT §14 (Z-виды, вес secondary edge-TTA 0.5/0.75/1.0, порог DeepCenter,
  замена поворотов на осевые отражения).
- STEP 5 только если всё выше сделано.

Перед долгим запуском делай короткий smoke-тест на 1–2 видео. Каждый шаг завершай так: строка в experiments/RESULTS.md,
короткая заметка в CONTEXT.md §14, коммит в ветку `friend-b` (без данных, весов и предсказаний в git), веса и geff в датасет
`vitaliineibauer/biohub-ft-weights` в папки с именами из TEAM.md. На leaderboard ничего не отправлять. Если шаг невозможно
выполнить как описано, объясни причину и предложи ближайший рабочий вариант, но не меняй рецептуру без пометки в RESULTS.md.
