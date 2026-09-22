"""Resumable orchestration for Friend A B35 step A0.

The authoritative calculations remain in ``tools/audit_b35.py``.  This module
adds notebook-friendly preflight, a division-bearing smoke test, cooperative
stop/resume, conservative parent-fraction selection, and the compact Friend C
package hand-off.  It deliberately does not start daughter recovery or model
training before A0 has produced a complete 199-video report.
"""

from __future__ import annotations

import json
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


def truthy(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


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


def preflight(cfg: B35Config) -> dict[str, Any]:
    errors: list[str] = []
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
    }
    atomic_json(cfg.output_dir / "preflight.json", result)
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
