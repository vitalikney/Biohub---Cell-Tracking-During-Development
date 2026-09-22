"""Resumable orchestration for Friend A B35 step A0.

The authoritative calculations remain in ``tools/audit_b35.py``.  This module
adds notebook-friendly preflight, a division-bearing smoke test, cooperative
stop/resume, conservative parent-fraction selection, and the compact Friend C
package hand-off.  It deliberately does not start daughter recovery or model
training before A0 has produced a complete 199-video report.
"""

from __future__ import annotations

import json
import importlib
import importlib.metadata
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


EXPERIMENT = "local_friend_a_b35_divisions"
CACHE_TAG = "friend_a_b20_exp29"
SMOKE_STEMS = ("44b6_a21120c2", "6bba_09961292")
RECALL_GATE = 0.90


def ensure_graph_runtime() -> dict[str, str]:
    """Import graph dependencies, repairing a partially imported notebook state.

    Interrupting an import in a long-lived Jupyter kernel can leave SQLAlchemy
    submodules in ``sys.modules`` without all attributes populated.  A later
    tracksdata import then fails with ``sqlalchemy.sql has no attribute base``
    even though the installed packages are healthy.  Retry only that known
    poisoned-kernel state; unrelated dependency failures keep their traceback.
    """

    def load() -> None:
        importlib.import_module("tracksdata")
        sqlalchemy_sql = importlib.import_module("sqlalchemy.sql")
        if not hasattr(sqlalchemy_sql, "base"):
            raise AttributeError("module 'sqlalchemy.sql' has no attribute 'base'")

    try:
        load()
    except AttributeError as exc:
        if "sqlalchemy.sql" not in str(exc) or "base" not in str(exc):
            raise
        for module_name in list(sys.modules):
            if module_name in {"tracksdata", "sqlalchemy"} or module_name.startswith(
                ("tracksdata.", "sqlalchemy.")
            ):
                sys.modules.pop(module_name, None)
        importlib.invalidate_caches()
        try:
            load()
        except Exception as retry_exc:
            raise RuntimeError(
                "The notebook kernel contains a broken graph-library import and automatic "
                "recovery failed. Restart the kernel and run all cells once."
            ) from retry_exc
        print("Recovered a partial SQLAlchemy/tracksdata import in the current kernel.", flush=True)

    return {
        "tracksdata": importlib.metadata.version("tracksdata"),
        "sqlalchemy": importlib.metadata.version("SQLAlchemy"),
    }


def truthy(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def json_default(value: Any) -> Any:
    """Convert NumPy scalar values produced by graph counters to JSON scalars."""
    item = getattr(value, "item", None)
    if callable(item):
        converted = item()
        if converted is not value:
            return converted
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=json_default),
    )


def discover_data_dir(repo_root: Path) -> Path:
    explicit = os.environ.get("BIOHUB_DATA_DIR", "").strip()
    candidates = [Path(explicit)] if explicit else []
    candidates.extend((repo_root.parent / "train", repo_root / "train"))
    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("*.zarr")):
            return candidate.resolve()
    raise FileNotFoundError("Set BIOHUB_DATA_DIR to the train directory")


@dataclass
class B35Config:
    repo_root: Path
    data_dir: Path
    cache_dir: Path
    output_dir: Path
    package_path: Path
    run_full_audit: bool = True
    max_videos: int = 0

    @classmethod
    def from_environment(cls, repo_root: Path) -> "B35Config":
        repo_root = Path(repo_root).resolve()
        output = Path(
            os.environ.get("BIOHUB_B35_OUTPUT_DIR", repo_root.parent / "outputs" / EXPERIMENT)
        ).resolve()
        cache = Path(
            os.environ.get(
                "BIOHUB_B35_CACHE",
                repo_root.parent / "outputs" / "local_friend_a_b20_divnet" / "cache" / CACHE_TAG,
            )
        ).resolve()
        package = Path(
            os.environ.get(
                "BIOHUB_FRIEND_C_PACKAGE",
                repo_root.parent / "outputs" / "friend_c_package" / f"{CACHE_TAG}_friend_c.zip",
            )
        ).resolve()
        return cls(
            repo_root=repo_root,
            data_dir=discover_data_dir(repo_root),
            cache_dir=cache,
            output_dir=output,
            package_path=package,
            run_full_audit=truthy(os.environ.get("BIOHUB_B35_RUN"), True),
            max_videos=int(os.environ.get("BIOHUB_B35_MAX_VIDEOS", "0")),
        )

    @property
    def all_stems(self) -> list[str]:
        ckpt = {path.stem for path in (self.cache_dir / "ckpt").glob("*.npz")}
        divnet = {path.stem for path in (self.cache_dir / "divnet").glob("*.npz")}
        gt = {path.stem for path in self.data_dir.glob("*.geff")}
        return sorted(ckpt & divnet & gt)

    @property
    def stems(self) -> list[str]:
        if not self.max_videos:
            return self.all_stems
        each = max(1, self.max_videos // 2)
        stems = [stem for stem in self.all_stems if stem.startswith("44b6")][:each]
        stems += [stem for stem in self.all_stems if stem.startswith("6bba")][:each]
        return sorted(stems[: self.max_videos])

    @property
    def audit_dir(self) -> Path:
        return self.output_dir / (f"a0_{self.max_videos}" if self.max_videos else "a0_full199")

    @property
    def stop_file(self) -> Path:
        return self.audit_dir / "STOP_REQUESTED"

    @property
    def step_a_dir(self) -> Path:
        return self.output_dir / "step_a_fullframe_primary090"

    @property
    def step_a_stop_file(self) -> Path:
        return self.step_a_dir / "STOP_REQUESTED"

    def serialisable(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("repo_root", "data_dir", "cache_dir", "output_dir", "package_path"):
            payload[key] = str(payload[key])
        payload["videos"] = len(self.stems)
        payload["full_dataset_videos"] = len(self.all_stems)
        return payload


def request_stop(cfg: B35Config) -> Path:
    cfg.stop_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.stop_file.write_text("Stop after the current video.\n", encoding="utf-8")
    return cfg.stop_file


def clear_stop(cfg: B35Config) -> None:
    cfg.stop_file.unlink(missing_ok=True)


def request_step_a_stop(cfg: B35Config) -> Path:
    cfg.step_a_stop_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.step_a_stop_file.write_text("Stop before the next video.\n", encoding="utf-8")
    return cfg.step_a_stop_file


def clear_step_a_stop(cfg: B35Config) -> None:
    cfg.step_a_stop_file.unlink(missing_ok=True)


def preflight(cfg: B35Config) -> dict[str, Any]:
    errors: list[str] = []
    graph_runtime = ensure_graph_runtime()
    sets = {
        "ckpt": {p.stem for p in (cfg.cache_dir / "ckpt").glob("*.npz")},
        "divnet": {p.stem for p in (cfg.cache_dir / "divnet").glob("*.npz")},
        "GT": {p.stem for p in cfg.data_dir.glob("*.geff")},
        "images": {p.stem for p in cfg.data_dir.glob("*.zarr")},
    }
    for name, values in sets.items():
        if len(values) != 199:
            errors.append(f"{name}: expected 199 videos, found {len(values)}")
    common = set.intersection(*sets.values()) if sets else set()
    if len(common) != 199:
        errors.append(f"complete ckpt/divnet/GT/image intersection: {len(common)}, expected 199")
    for relative in (
        Path("tools/audit_b35.py"),
        Path("tools/package_friend_c_b31_cache.py"),
        Path("tools/official/src/tracking_cellmot/division_metrics.py"),
    ):
        if not (cfg.repo_root / relative).is_file():
            errors.append(f"missing {relative}")
    for stem in SMOKE_STEMS:
        if stem not in common:
            errors.append(f"division-bearing smoke video is missing: {stem}")
    if errors:
        raise RuntimeError("B35 preflight failed:\n- " + "\n- ".join(errors))
    result = {
        "status": "ready",
        "videos": len(cfg.stems),
        "full_dataset_videos": len(common),
        "cache": str(cfg.cache_dir),
        "data": str(cfg.data_dir),
        "audit_output": str(cfg.audit_dir),
        "smoke_stems": list(SMOKE_STEMS),
        "friend_c_package": str(cfg.package_path),
        "cuda_needed_for_a0": False,
        "graph_runtime": graph_runtime,
    }
    atomic_json(cfg.output_dir / "preflight.json", result)
    return result


def preflight_step_a(cfg: B35Config) -> dict[str, Any]:
    import torch

    errors: list[str] = []
    a0_videos = cfg.audit_dir / "videos"
    required = (
        cfg.repo_root / "tools" / "recover_daughters.py",
        cfg.repo_root / "tools" / "public_local.py",
        cfg.repo_root / "experiments" / "exp29_sjlee947_verbatim" / "exp29-sjlee947-verbatim.ipynb",
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(cfg.repo_root)}")
    if len(list(a0_videos.glob("*.json"))) != 199:
        errors.append("B35 A0 per-video audit is incomplete; expected 199 cached JSON files")
    if not torch.cuda.is_available():
        errors.append("CUDA is required for B35 Step A")
    public_primary = (
        cfg.repo_root
        / "external"
        / "pilkwang__biohub-tracking-support-pack-50ep-v1"
        / "weights"
        / "unet_transformer"
        / "split_0"
        / "edge_predictor_best.pth"
    )
    if not public_primary.is_file():
        errors.append("public primary pack is missing; run tools/get_kaggle_datasets.py")
    if errors:
        raise RuntimeError("B35 Step A preflight failed:\n- " + "\n- ".join(errors))
    result = {
        "status": "ready",
        "videos": len(cfg.all_stems),
        "gpu": torch.cuda.get_device_name(0),
        "det_threshold": 0.90,
        "nms_um": 3.0,
        "parent_um": 20.0,
        "existing_exclusion_um": 3.0,
        "reach_gate": "144/151",
        "candidate_node_ratio_gate_per_video": 0.003,
        "output": str(cfg.step_a_dir),
        "stop_file": str(cfg.step_a_stop_file),
    }
    atomic_json(cfg.step_a_dir / "preflight.json", result)
    return result


def _recommend_fraction(report: dict[str, Any]) -> dict[str, Any]:
    fractions = tuple(f"{value:.2f}" for value in (0.01, 0.03, 0.05, 0.10, 0.20, 0.50, 1.0))
    minimum_by_group: dict[str, float | None] = {}
    curve: dict[str, dict[str, float | None]] = {}
    for group in ("all", "44b6", "6bba"):
        recalls = report["groups"][group]["parent_recall"]
        curve[group] = {key: recalls.get(key) for key in fractions}
        passing = [float(key) for key in fractions if recalls.get(key) is not None and recalls[key] >= RECALL_GATE]
        minimum_by_group[group] = min(passing) if passing else None
    robust_values = [minimum_by_group[group] for group in ("all", "44b6", "6bba")]
    robust = max(robust_values) if all(value is not None for value in robust_values) else None
    counts = report["groups"]["all"]["counts"]
    baseline = int(counts.get("window_detection_necessary", 0))
    total = int(counts.get("gt_divisions", 0))
    return {
        "recall_gate": RECALL_GATE,
        "curve": curve,
        "minimum_fraction_by_group": minimum_by_group,
        "recommended_robust_fraction": robust,
        "window_detection_baseline": baseline,
        "gt_divisions": total,
        "provisional_step_a_target_same_plus14_intent": min(total, baseline + 14),
        "target_note": (
            "The +14 target preserves the old intended gain only; register the final Step A gate "
            "after reviewing this official-window audit."
        ),
    }


def _write_handoff(cfg: B35Config, report: dict[str, Any], recommendation: dict[str, Any]) -> None:
    payload = {"audit": report, "selection": recommendation}
    runtime_json = cfg.audit_dir / "b35_audit.json"
    atomic_json(runtime_json, payload)
    lines = [
        "# B35 Step A0 — official-matcher audit",
        "",
        f"Videos: {report['videos']}. This is a diagnostic, not an achieved competition score.",
        "",
        "| group | GT divisions | direct nodes | window necessary | min fraction for 90% parent recall |",
        "|---|---:|---:|---:|---:|",
    ]
    for group in ("all", "44b6", "6bba"):
        counts = report["groups"][group]["counts"]
        fraction = recommendation["minimum_fraction_by_group"][group]
        fraction_text = "not reached" if fraction is None else f"{fraction:.0%}"
        lines.append(
            f"| {group} | {int(counts.get('gt_divisions', 0))} | "
            f"{int(counts.get('direct_parent_and_daughters', 0))} | "
            f"{int(counts.get('window_detection_necessary', 0))} | {fraction_text} |"
        )
    robust = recommendation["recommended_robust_fraction"]
    lines += [
        "",
        "Robust fraction (must reach 90% in all/44b6/6bba): "
        + ("not reached" if robust is None else f"**{robust:.0%}**"),
        "",
        f"Official-window detection baseline: **{recommendation['window_detection_baseline']}/{recommendation['gt_divisions']}**.",
        f"Provisional same-intent Step A target (+14): **{recommendation['provisional_step_a_target_same_plus14_intent']}**; "
        "Vitalii must register the final gate after reading this audit.",
        "",
        "Limitations: public checkpoints overlap both embryos; the window condition is necessary, not a valid-division score.",
    ]
    text = "\n".join(lines) + "\n"
    atomic_text(cfg.audit_dir / "b35_audit.md", text)
    if not cfg.max_videos and report.get("videos") == 199:
        results = cfg.repo_root / "experiments" / "local_friend_a_b32_divpair" / "results"
        atomic_json(results / "b35_audit.json", payload)
        atomic_text(results / "b35_audit.md", text)


def _run(cfg: B35Config, stems: list[str], output: Path) -> dict[str, Any]:
    ensure_graph_runtime()
    from tools import audit_b35

    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "state.json"
    state = {
        "status": "running",
        "videos": len(stems),
        "started_or_resumed": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "completed": 0,
    }
    atomic_json(state_path, state)
    rows: list[dict[str, Any]] = []
    try:
        for index, stem in enumerate(stems, start=1):
            if (output / "STOP_REQUESTED").is_file():
                state.update(status="stopped_safely", completed=len(rows))
                atomic_json(state_path, state)
                return state
            print(f"A0 [{index}/{len(stems)}] {stem}", flush=True)
            rows.append(audit_b35.audit_video(cfg.cache_dir, cfg.data_dir, stem, output))
            report = audit_b35.summarise(rows, output)
            state.update(completed=len(rows), updated_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
            atomic_json(state_path, state)
        report = audit_b35.summarise(rows, output)
        recommendation = _recommend_fraction(report)
        if output == cfg.audit_dir:
            _write_handoff(cfg, report, recommendation)
        state.update(status="complete", completed=len(rows), recommendation=recommendation)
        atomic_json(state_path, state)
        return state
    except KeyboardInterrupt:
        state.update(status="stopped_safely", completed=len(rows))
        atomic_json(state_path, state)
        print("SAFE STOP: completed video JSON files are reusable.", flush=True)
        return state


def run_smoke(cfg: B35Config) -> dict[str, Any]:
    return _run(cfg, list(SMOKE_STEMS), cfg.output_dir / "smoke_a0_divisions")


def run_a0(cfg: B35Config) -> dict[str, Any]:
    if not cfg.run_full_audit:
        return {"status": "disabled", "reason": "BIOHUB_B35_RUN=0"}
    return _run(cfg, cfg.stems, cfg.audit_dir)


def _run_step_a(cfg: B35Config, stems: list[str], label: str, *, expect_videos: int = 0) -> dict[str, Any]:
    command = [
        sys.executable,
        str(cfg.repo_root / "tools" / "recover_daughters.py"),
        "--data-dir", str(cfg.data_dir),
        "--cache", str(cfg.cache_dir),
        "--output", str(cfg.step_a_dir),
        "--baseline-audit", str(cfg.audit_dir),
        "--stop-file", str(cfg.step_a_stop_file),
        "--det-threshold", "0.90",
        "--nms-um", "3.0",
        "--parent-um", "20.0",
        "--existing-um", "3.0",
        "--stems", *stems,
    ]
    if expect_videos:
        command.extend(["--expect-videos", str(expect_videos)])
    log_path = cfg.step_a_dir / f"{label}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print("STEP A COMMAND:", " ".join(command), flush=True)
    with log_path.open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            command,
            cwd=cfg.repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        try:
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
        except KeyboardInterrupt:
            request_step_a_stop(cfg)
            process.terminate()
            process.wait(timeout=30)
            print("SAFE STOP: completed videos are cached; rerun the cell to resume.", flush=True)
            return compact_step_a_status(cfg)
        return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"{label} failed with exit code {return_code}; see {log_path}")
    return compact_step_a_status(cfg)


def run_step_a_smoke(cfg: B35Config) -> dict[str, Any]:
    return _run_step_a(cfg, list(SMOKE_STEMS), "step_a_smoke2")


def run_step_a(cfg: B35Config) -> dict[str, Any]:
    return _run_step_a(cfg, cfg.all_stems, "step_a_full199", expect_videos=199)


def compact_step_a_status(cfg: B35Config) -> dict[str, Any]:
    state_path = cfg.step_a_dir / "state.json"
    summary_path = cfg.step_a_dir / "summary.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    group = summary.get("groups", {}).get("all", {})
    return {
        "status": state.get("status", "new"),
        "completed": state.get("completed", 0),
        "selected_videos": state.get("selected_videos", len(cfg.all_stems)),
        "baseline_reach": group.get("baseline_window_detection_necessary"),
        "augmented_reach": group.get("augmented_window_detection_necessary"),
        "candidate_node_ratio": group.get("candidate_node_ratio"),
        "max_candidate_node_ratio": group.get("max_candidate_node_ratio"),
        "gate": summary.get("gate"),
        "stop_file": str(cfg.step_a_stop_file),
        "report": str(cfg.step_a_dir / "summary.md"),
    }


def build_friend_c_package(cfg: B35Config) -> Path:
    command = [
        sys.executable,
        str(cfg.repo_root / "tools" / "package_friend_c_b31_cache.py"),
        "--cache-root", str(cfg.cache_dir),
        "--data-dir", str(cfg.data_dir),
        "--output", str(cfg.package_path),
        "--expected-videos", "199",
    ]
    subprocess.run(command, cwd=cfg.repo_root, check=True)
    return cfg.package_path


def compact_status(cfg: B35Config) -> dict[str, Any]:
    state = cfg.audit_dir / "state.json"
    payload = json.loads(state.read_text(encoding="utf-8")) if state.is_file() else {"status": "new"}
    return {
        "status": payload.get("status", "new"),
        "completed": payload.get("completed", 0),
        "videos": len(cfg.stems),
        "stop_file": str(cfg.stop_file),
        "report": str(cfg.audit_dir / "b35_audit.md"),
        "friend_c_package": str(cfg.package_path),
    }
