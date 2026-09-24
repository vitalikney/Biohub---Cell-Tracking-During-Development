# Friend A: захват данных для переобучения coordinate-head (x138 / V1284) на 128 видео 6bba

Статус: готово к запуску. Kaggle делает свою часть (71 видео 44b6, кернелы `biohub-chcap-44b6-s0of2/s1of2`),
твоя часть - **все 128 видео 6bba** (список зафиксирован в `experiments/coordhead_retrain/capture_plan.json`,
ключ `friend_a_6bba`, видео с наибольшим числом GT-узлов идут первыми). Формат выхода идентичен кагловскому,
`tools/train_coordhead.py` читает обе части вместе. НИЧЕГО не сабмитить.

## Что это и зачем

Голова x138 (`anvithpothula/biohub-v1284-head-s075`, публичный 0.953) сдвигает каждый найденный пик на < 2 мкм
по 224-мерным признакам первичного UNet. Мы переобучаем её на всех 199 train-видео. Для этого нужно прогнать ТОЧНО
стек предсказания exp51 (primary + secondary seed314159, D4 TTA детекции, смешивание 0.80 + retention guard 0.90,
8-видовой edge-feature TTA) в режиме `capture`: для каждого кадра сохраняются целочисленные пики и вход головы;
edge-transformer, граф, ILP и хвост не запускаются.

`experiments/coordhead_retrain/local_capture.py` не содержит своей логики предсказания: он генерирует тот же
ноутбук, что и Kaggle-кернел (`build_capture_kernel.make_notebook` из exp51-coordhead.ipynb), выполняет его ячейку
0 (ручки) и код патчей ячейки 5 над оригинальным репо pilkwang, запускает пропатченный
`scripts/predict_unet_transformer.py` на твоих локальных train-видео и проверяет результат кодом сводки из той же
ячейки. Пути `/kaggle/...` подменяются на папки из аргументов; ни пики, ни признаки это не затрагивает.

## Что нужно

- репо на свежем `main` (`git pull`);
- папка train соревнования: `<...>/biohub-cell-tracking-during-development/train` с `<stem>.zarr` и `<stem>.geff`
  (все 199; нужны 128 6bba);
- Python-окружение публичного стека (то же, что для friend_a_b20 cache): torch с CUDA для 5070 Ti (cu128),
  tracksdata, zarr>=3, polars, geff, ilpy, pyscipopt, scikit-image, dask, scipy;
- Kaggle API токен (один раз скачать ~17 МБ моделей + загрузить результат).

Модели скачиваются сами в `--work/assets` и проверяются по тем же sha256, что проверяет Kaggle-кернел
(repo pilkwang support pack `c44e771b...` для predict-скрипта, primary `12f6881e...`, secondary `9bac2fa0...`,
public head `625a0d93...`).

## Шаг 1. Замер на одном видео (полные 100 кадров) = стадия предсказания exp51 на train-видео

```
python experiments/coordhead_retrain/local_capture.py --data-dir D:/data/biohub-cell-tracking-during-development/train --stems 6bba_bb9f20c3 --work D:/chcap
```

- в начале должна быть строка `torch ..., CUDA True (NVIDIA GeForce RTX 5070 Ti)` и `Fold 0: ... device=cuda`;
- в конце строка `COORDHEAD_CAPTURE {... "video_seconds": X ...}` и `COORDHEAD CAPTURE SUMMARY`; X = время одного
  видео. Пришли X. Ожидание: T4 на Kaggle тратит 208 с на видео (пилот `biohub-chcap-pilot`, 6 видео,
  201-214 с), 5070 Ti должна быть в 2-3 раза быстрее (~70-100 с). Полный прогон займёт примерно 128 x X секунд
  (при 100 с на видео ~3.5 ч);
- это видео входит и в пилот на Kaggle, поэтому оно же даёт проверку "5070 Ti vs T4" (признаки совпадут до
  последних бит float, это нормально).

(Если ты уже замерил через сам `exp51-coordhead.ipynb`, шаг всё равно запусти: он проверяет окружение и кладёт
первое видео в выход, повторно оно не считается.)

## Шаг 2. Полный прогон (128 видео 6bba)

```
python experiments/coordhead_retrain/local_capture.py --data-dir D:/data/biohub-cell-tracking-during-development/train --plan friend_a_6bba --work D:/chcap
```

- можно прерывать и перезапускать той же командой: готовые видео (`D:/chcap/capture/<stem>.npz`) пропускаются;
- выход: `D:/chcap/capture/` = `<stem>.npz` (~2 МБ на видео 6bba, всего ~0.3 ГБ), `manifest_local_*.jsonl`,
  `capture_summary_friend_a_6bba.json`; промежуточные файлы в `D:/chcap/run_friend_a_6bba/raw` удаляются по ходу;
- в конце сводка должна сказать `"done": 128, "missing": []`, иначе скрипт падает с `capture incomplete`.

## Шаг 3. Загрузка на Kaggle (приватный датасет) и доступ для vitaliineibauer

1. Создай `D:/chcap/capture/dataset-metadata.json`:
   ```
   {"title": "biohub-chcap-6bba", "id": "<твой_kaggle_username>/biohub-chcap-6bba", "licenses": [{"name": "CC0-1.0"}]}
   ```
2. `python -m kaggle datasets create -p D:/chcap/capture` (датасет создаётся приватным).
3. На странице датасета: Settings -> Sharing -> добавить `vitaliineibauer` (Viewer).
4. Напиши slug датасета. Мы скачаем его и запустим обучение:
   `python -m kaggle datasets download <you>/biohub-chcap-6bba -p experiments/coordhead_retrain/captures/friend_a --unzip`
   `nice -n 19 python tools/train_coordhead.py --capture experiments/coordhead_retrain/captures --out experiments/coordhead_retrain/out_full`

## Если что-то не так

- `no CUDA device` - torch без CUDA в этом окружении; нужен torch cu128 для Blackwell.
- Windows без прав на symlink: скрипт сам делает junction (`mklink /J`) на папку train; если и это падает, запусти
  из консоли с правами администратора или укажи `--work` на том же диске, что и данные.
- `sha256 mismatch` - скачался не тот файл модели: удали `D:/chcap/assets` и запусти снова.
- Нехватка VRAM маловероятна (тот же стек работает на T4 16 ГБ); закрой другие процессы на GPU.
- Код и ручки не менять: признаки должны быть бит-в-бит путём инференса exp51, иначе голова обучится не на том.
- Быстрый CPU-смоук без GPU (4 кадра, ~5 мин): добавить `--frames 4 --work D:/chcap_smoke` к команде шага 1.
