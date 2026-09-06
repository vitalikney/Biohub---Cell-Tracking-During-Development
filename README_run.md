# Biohub Cell Tracking

Рабочее окружение создаётся в `.venv`; все команды запускаются через него.

## Первый запуск

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name celltracker-biohub --display-name "CellTracker Biohub (.venv)"
```

Откройте `biohub_cell_tracking.ipynb`, выберите ядро `CellTracker Biohub (.venv)` и выполните ячейки сверху вниз.

## Данные

В корне проекта должны быть `train/<dataset>.zarr`, `train/<dataset>.geff` и `test/<dataset>.zarr`. Ноутбук обнаруживает фактические ID, не использует захардкоженный список.

## Текущий этап: detector

`biohub_cell_tracking.ipynb` реализует воспроизводимое обучение detector центров клеток: ленивые окна из двух кадров, отдельно нормированный sparse-GT loss с защитой от all-positive collapse, AMP, корректное gradient accumulation, checkpoint/resume и независимую проверку на втором эмбрионе. Validation использует физический Euclidean NMS и оптимальное one-to-one сопоставление в микронах с учётом downsampling. Во время обучения прямо в output ячейки обновляются progress-bar, loss, VRAM и SVG-график; после validation добавляется точка holdout recall. История и `last.pt` сохраняются до validation, а лучший проверенный checkpoint — как `best.pt`. По умолчанию долгий training и validation отключены до явного изменения `cfg.run_training` / `cfg.run_validation`. Linker, граф и submission — следующие этапы, ещё не реализованные в основном ноутбуке.

## Режимы для дальнейшей работы

- `smoke` — короткая проверка окружения, аудита, формы модели и loss; выполняется с `run_training=False`, `run_validation=False`.
- `train` — установите `cfg.run_training=True`; сохраняются `last.pt`, `best.pt` (после validation), `train_history.csv`, `epoch_history.csv` и runtime. Исправленный baseline по умолчанию пишет в `outputs/detector_44b6_to_6bba_v2`; checkpoint старой версии намеренно несовместим.
- `validate` — установите `cfg.run_validation=True`; при совместном запуске с training целый holdout оценивается каждые `validate_every_n_epochs` эпох и строится кривая recall. Отдельный запуск автоматически загружает `RUN/last.pt` или явно заданный `cfg.detector_checkpoint_path`.
- `report` — последняя ячейка сохраняет `training_curves.svg` и `run_report.json` с конфигурацией, кривыми, validation и списком артефактов.

`smoke` не доказывает качество и не создаёт submission. Sparse-GT recall и ошибка локализации — диагностика detector, не официальная graph-метрика и не полный precision: разметка клеток неполная.

## Provenance

Официальный код сохранён в `vendor/kaggle-cell-tracking-competition` на commit `075fc5f5a52d11077f9dc2b074644618f26939e2` с лицензией BSD-3-Clause. `tracksdata` закреплён в `requirements-lock.txt` на commit `63a1912f3b6ebd1536a2e8a8adfdf7f5eb84efa4`.
