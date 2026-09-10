# Промпт для ассистента Friend A (Sasyami, RTX 5070 Ti 16 ГБ) — актуален на 2026-09-10 20:00

Скопировать целиком в ассистента, запущенного в клоне репозитория (ветка `detector-baseline-v2`).

---

Ты работаешь в репозитории соревнования Kaggle «Biohub – Cell Tracking During Development», ветка `detector-baseline-v2`,
машина Friend A (RTX 5070 Ti 16 ГБ, Windows, Python 3.12, данные в `C:\Projects\CellTracker\train`). Сначала `git pull origin main`
в свою ветку, затем прочитай TEAM.md (раздел «Friend A — order of work, revised 2026-09-10 18:00») и CONTEXT.md §10a и §14
(записи от 2026-09-10). План изменился: обучение с нуля больше не делаем, плотные метки идут в ДООБУЧЕНИЕ весов pilkwang.

Сначала определи, на какой стадии сейчас `friend-a-dense-pipeline.ipynb` (по логу и по `outputs/local_friend_a_exp03_loeo_dense_20ep/active/`):
- если ещё считается учитель или сборка `train_dense/` (STEP 1c) — дай им закончить, они нужны;
- если уже идёт обучение STEP 4 с нуля (в логе команда с `--epochs 20` без `--init-weights`) — останови его одним Interrupt,
  результаты не нужны;
- ветку «>= 0.70 -> с нуля на всех 199» не запускать никогда.

Затем перепиши STEP 4 в `step4_train_evaluate.py` под дообучение:
`--init-weights <pilkwang primary: support-pack weights/unet_transformer/split_0/edge_predictor_best.pth>`, `--max-iters 1200`,
`--lr 5e-5` без косинуса, `--det-loss bce`, `--max-detections 0`, `--seed 42`, `BIOHUB_DATA_DIR=train_dense`,
разбиение `experiments/_lib/loeo_train6bba_val44b6.json` (126 6bba в обучение, 12 44b6 в оценку).
Оценка каждого варианта: сырое предсказание на 12 видео 44b6 с
`--det-threshold 0.965 --use-ilp --ilp-appearance-weight 0 --ilp-disappearance-weight 2 --ilp-division-weight 1.2`
и `tools/score_geffs.py`; записывать score, edge_jaccard, node_recall, N_pred/N_est.

Прогоны по порядку, каждый около часа:
0. эталон: то же дообучение на РАЗРЕЖЕННОЙ разметке (обычная папка train) — ожидается около 0.8825, как exp11 B;
1. плотные метки, 1200 итераций;
2. плотные метки, 2400 итераций;
3. плотные метки, 1200 итераций, `--det-neg-weight 0.1`;
4. плотные метки, 1200 итераций, `--aug-intensity`.
Вариант считается победившим, если он лучше эталона 0 на 0.005 и больше.

Папка `experiments/local_friend_a_exp03_dense_ft_primary/`, по строке в experiments/RESULTS.md на каждый прогон, короткая заметка
в CONTEXT.md §14, коммит в свою ветку (без данных, весов и предсказаний в git). Учителя и плотные geff, если ещё не выложены,
залить в датасет `vitaliineibauer/biohub-ft-weights` в папки `teacher_geff/` и `train_dense_geff/` и написать об этом в чат,
чтобы Friend B не дублировал.

Если появился победивший вариант: то же дообучение на 183 видео (список `train` из `experiments/exp03_finetune_ab/config.py`),
веса с config.json в датасет как `friend_a_ft_dense_primary/`, сообщить Виталию. На leaderboard ничего не отправлять.
Если шаг невозможно выполнить как описано, объясни причину и предложи ближайший рабочий вариант, но не меняй рецептуру
без пометки в RESULTS.md.
