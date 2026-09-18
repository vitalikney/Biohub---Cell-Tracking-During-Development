"""One-button, resumable orchestration for Friend A's B20 DivNet task."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


EXPERIMENT = "local_friend_a_b20_divnet"
TAG = "friend_a_b20_exp29"
GRID = tuple((top_k, threshold) for top_k in (1, 2) for threshold in (0.3, 0.5, 0.7))


class StopRequested(RuntimeError):
    """A cooperative or keyboard stop after recoverable output was written."""


def truthy(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def discover_data_dir(repo_root: Path) -> Path:
    candidates: list[Path] = []
    explicit = os.environ.get("BIOHUB_DATA_DIR", "").strip()
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            repo_root.parent / "train",
            repo_root / "train",
            repo_root / "biohub-cell-tracking-during-development" / "train",
        ]
    )
    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("*.zarr")):
            return candidate.resolve()
    raise FileNotFoundError("Set BIOHUB_DATA_DIR to the folder with the 199 *.zarr and *.geff pairs")


@dataclass
class B20Config:
    repo_root: Path
    data_dir: Path
    output_dir: Path
    cache_parent: Path
    tag: str = TAG
    run_pipeline: bool = True
    max_videos: int = 0
    divnet_batch: int = 32
    parent_um: float = 15.0
    candidate_k: int = 64

    @classmethod
    def from_environment(cls, repo_root: Path) -> "B20Config":
        repo_root = repo_root.resolve()
        output = Path(
            os.environ.get(
                "BIOHUB_B20_OUTPUT_DIR",
                repo_root.parent / "outputs" / EXPERIMENT,
            )
        ).resolve()
        return cls(
            repo_root=repo_root,
            data_dir=discover_data_dir(repo_root),
            output_dir=output,
            cache_parent=output / "cache",
            run_pipeline=truthy(os.environ.get("BIOHUB_B20_RUN"), True),
            max_videos=int(os.environ.get("BIOHUB_B20_MAX_VIDEOS", "0")),
            divnet_batch=int(os.environ.get("BIOHUB_B20_DIVNET_BATCH", "32")),
            parent_um=float(os.environ.get("BIOHUB_B20_PARENT_UM", "15")),
            candidate_k=int(os.environ.get("BIOHUB_B20_CANDIDATE_K", "64")),
        )

    @property
    def cache(self) -> Path:
        return self.cache_parent / self.tag

    @property
    def stop_file(self) -> Path:
        return self.output_dir / "STOP_REQUESTED"

    @property
    def score_file(self) -> Path:
        return self.cache / "divnet"

    @property
    def stems(self) -> list[str]:
        zarr = {path.name.removesuffix(".zarr") for path in self.data_dir.glob("*.zarr")}
        geff = {path.name.removesuffix(".geff") for path in self.data_dir.glob("*.geff")}
        return sorted(zarr & geff)

    @property
    def selected_stems(self) -> list[str]:
        return self.stems[: self.max_videos] if self.max_videos else self.stems

    def serialisable(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("repo_root", "data_dir", "output_dir", "cache_parent"):
            payload[key] = str(payload[key])
        payload["n_videos"] = len(self.stems)
        payload["selected_videos"] = len(self.selected_stems)
        return payload

    def fingerprint(self) -> str:
        payload = self.serialisable()
        for key in ("run_pipeline", "max_videos", "output_dir", "cache_parent", "selected_videos"):
            payload.pop(key, None)
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def state_path(cfg: B20Config) -> Path:
    return cfg.output_dir / "state.json"


def load_state(cfg: B20Config) -> dict[str, Any]:
    if not state_path(cfg).is_file():
        return {"version": 1, "fingerprint": cfg.fingerprint(), "stages": {}, "videos": {}}
    state = json.loads(state_path(cfg).read_text(encoding="utf-8"))
    if state.get("fingerprint") != cfg.fingerprint():
        raise RuntimeError("B20 recipe changed. Use another BIOHUB_B20_OUTPUT_DIR or restore the old settings")
    return state


def save_state(cfg: B20Config, state: dict[str, Any]) -> None:
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    atomic_json(state_path(cfg), state)


def request_stop(cfg: B20Config) -> Path:
    cfg.stop_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.stop_file.write_text("Stop after the next safe checkpoint.\n", encoding="utf-8")
    return cfg.stop_file


def clear_stop(cfg: B20Config) -> None:
    cfg.stop_file.unlink(missing_ok=True)


def check_stop(cfg: B20Config) -> None:
    if cfg.stop_file.is_file():
        raise StopRequested(f"Stop requested via {cfg.stop_file}")


def child_environment(cfg: B20Config) -> dict[str, str]:
    return {
        **os.environ,
        "PYTHONUTF8": "1",
        "BIOHUB_DATA_DIR": str(cfg.data_dir),
        "BIOHUB_LOCAL_CACHE": str(cfg.cache_parent),
        "BIOHUB_B20_STOP_FILE": str(cfg.stop_file),
    }


def stream_command(cfg: B20Config, command: list[str], label: str, allow_stop: bool = False) -> int:
    log = cfg.output_dir / "logs" / f"{label}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    print("\n===", label, "===", flush=True)
    process = subprocess.Popen(
        command,
        cwd=cfg.repo_root,
        env=child_environment(cfg),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    try:
        with log.open("a", encoding="utf-8") as output:
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="", flush=True)
                output.write(line)
    except KeyboardInterrupt:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
        raise StopRequested(f"Interrupted during {label}; completed files are reusable")
    code = process.wait()
    if code == 75 and allow_stop:
        raise StopRequested(f"Cooperative stop during {label}; completed files are reusable")
    if code != 0:
        raise RuntimeError(f"{label} failed with exit code {code}; see {log}")
    return code


def ensure_dependencies(cfg: B20Config) -> None:
    required = [
        cfg.repo_root / "external" / "pilkwang__biohub-tracking-support-pack-50ep-v1"
        / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth",
        cfg.repo_root / "external" / "pilkwang__biohub-temporal-unet3d-seed314159-v1"
        / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth",
        cfg.repo_root / "external" / "pilkwang__biohub-deepcenter-unet3d-center-prior-v1"
        / "weights" / "full_frame_center" / "best.pt",
        cfg.repo_root / "external" / "giorgosi__biohub-divnet-v2" / "best_overall.pt",
    ]
    if all(path.exists() for path in required):
        print("External model packs are present")
        return
    stream_command(
        cfg,
        [sys.executable, "tools/get_kaggle_datasets.py", "--only", "pilkwang"],
        "fetch_pilkwang",
    )
    stream_command(
        cfg,
        [sys.executable, "tools/get_kaggle_datasets.py", "--only", "divnet"],
        "fetch_divnet",
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Model downloads are incomplete:\n" + "\n".join(missing))


def preflight(cfg: B20Config, gpu_smoke: bool = True) -> dict[str, Any]:
    import torch

    errors: list[str] = []
    if len(cfg.stems) != 199:
        errors.append(f"expected 199 image/GT pairs, found {len(cfg.stems)}")
    if cfg.parent_um < 12 or cfg.parent_um > 15:
        errors.append("parent_um must stay in the pre-registered 12-15 um range")
    if cfg.candidate_k < 2:
        errors.append("candidate_k must be at least 2")
    if cfg.divnet_batch <= 0:
        errors.append("DivNet batch size must be positive")
    for relative in (
        "tools/public_local.py",
        "tools/score_geffs.py",
        "tools/divnet_infer.py",
        "experiments/local_friend_b_exp02_public_port/pass1_extras.py",
        "experiments/local_friend_a_b20_divnet/score_divnet_candidates.py",
        "experiments/local_friend_a_b20_divnet/pass2_divnet.py",
    ):
        if not (cfg.repo_root / relative).is_file():
            errors.append(f"missing {relative}")
    if cfg.run_pipeline and not torch.cuda.is_available():
        errors.append("CUDA is required for the full run")
    if errors:
        raise RuntimeError("Preflight failed:\n- " + "\n- ".join(errors))

    result = {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "data_dir": str(cfg.data_dir),
        "videos": len(cfg.stems),
        "selected_videos": len(cfg.selected_stems),
        "cache": str(cfg.cache),
    }
    if gpu_smoke:
        sys.path.insert(0, str(cfg.repo_root))
        from tools.divnet_infer import load_divnet_mitosis_model

        bundle = load_divnet_mitosis_model()
        value = torch.zeros((1, 5, 16, 32, 32), device=bundle["device"])
        with torch.inference_mode():
            output = bundle["model"](value)
        if tuple(output.shape) != (1, 1) or not torch.isfinite(output).all():
            raise RuntimeError("DivNet tensor smoke failed")
        result["divnet_checkpoint"] = str(bundle["path"])
        result["divnet_logit"] = float(output.item())
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(cfg.output_dir / "config.json", cfg.serialisable())
    atomic_json(cfg.output_dir / "preflight.json", result)
    return result


def run_pass1_video(cfg: B20Config, stem: str, state: dict[str, Any]) -> None:
    raw = cfg.cache / "raw" / f"{stem}.geff"
    checkpoint = cfg.cache / "ckpt" / f"{stem}.npz"
    deepcenter = cfg.cache / "dc" / f"{stem}.npz"
    if not raw.is_dir():
        stream_command(
            cfg,
            [
                sys.executable,
                "tools/public_local.py",
                "--tag",
                cfg.tag,
                "--stage",
                "infer",
                "--stems",
                stem,
                "--data-dir",
                str(cfg.data_dir),
                "--cache-dir",
                str(cfg.cache_parent),
                "--keep-peak-prob",
            ],
            f"pass1_infer_{stem}",
        )
    check_stop(cfg)
    if not (checkpoint.is_file() and deepcenter.is_file()):
        stream_command(
            cfg,
            [
                sys.executable,
                "experiments/local_friend_b_exp02_public_port/pass1_extras.py",
                "--tag",
                cfg.tag,
                "--stems",
                stem,
            ],
            f"pass1_extras_{stem}",
        )
    state["videos"][stem] = {"raw": True, "checkpoint": True, "deepcenter": True}
    save_state(cfg, state)
    check_stop(cfg)


def run_divnet(cfg: B20Config, stems: list[str], label: str, output: Path | None = None) -> None:
    command = [
            sys.executable,
            "experiments/local_friend_a_b20_divnet/score_divnet_candidates.py",
            "--tag",
            cfg.tag,
            "--data-dir",
            str(cfg.data_dir),
            "--parent-um",
            str(cfg.parent_um),
            "--candidate-k",
            str(cfg.candidate_k),
            "--batch-size",
            str(cfg.divnet_batch),
            "--stems",
            *stems,
        ]
    if output is not None:
        command.extend(["--output", str(output)])
    stream_command(
        cfg,
        command,
        label,
        allow_stop=True,
    )


def run_pass2(
    cfg: B20Config,
    stems: list[str],
    label: str,
    ranker: str,
    top_k: int = 0,
    threshold: float = 0.0,
    scores_file: Path | None = None,
) -> dict[str, Any]:
    if ranker == "public":
        mode, parent_um, candidate_k = "add", 9.0, 3
    else:
        mode, parent_um, candidate_k = "steal", cfg.parent_um, cfg.candidate_k
    command = [
        sys.executable,
        "experiments/local_friend_a_b20_divnet/pass2_divnet.py",
        "--tag",
        cfg.tag,
        "--ranker",
        ranker,
        "--mode",
        mode,
        "--parent-um",
        str(parent_um),
        "--candidate-k",
        str(candidate_k),
        "--score-top-k",
        str(top_k),
        "--min-score",
        str(threshold),
        "--label",
        label,
        "--data-dir",
        str(cfg.data_dir),
        "--resume",
        "--stems",
        *stems,
    ]
    if scores_file is not None:
        command.extend(["--scores-file", str(scores_file)])
    stream_command(cfg, command, f"pass2_{label}", allow_stop=True)
    result = cfg.cache / "pp" / f"{label}.json"
    return json.loads(result.read_text(encoding="utf-8"))


def run_smoke(cfg: B20Config, state: dict[str, Any]) -> None:
    if state["stages"].get("smoke"):
        return
    stem = cfg.selected_stems[0]
    print(f"Smoke test on {stem}", flush=True)
    run_pass1_video(cfg, stem, state)
    run_divnet(cfg, [stem], "smoke_divnet")
    control = run_pass2(cfg, [stem], "smoke_public", "public")
    candidate = run_pass2(cfg, [stem], "smoke_divnet_k1_t05", "divnet", 1, 0.5, cfg.score_file)
    for name, result in (("control", control), ("divnet", candidate)):
        score = float(result["summary"]["score"])
        if not 0 <= score <= 1.2:
            raise RuntimeError(f"Smoke {name} produced an invalid score: {score}")
    state["stages"]["smoke"] = True
    save_state(cfg, state)


def build_report(cfg: B20Config, results: list[dict[str, Any]]) -> dict[str, Any]:
    control = next(item for item in results if item["label"] == "control_public")
    base = control["summary"]
    rows = []
    for result in results:
        summary = result["summary"]
        row = {
            "variant": result["label"],
            "score": float(summary["score"]),
            "delta": float(summary["score"] - base["score"]),
            "adj_edge": float(summary["adj_edge_jaccard"]),
            "adj_edge_delta": float(summary["adj_edge_jaccard"] - base["adj_edge_jaccard"]),
            "division_jaccard": float(summary["division_jaccard"]),
            "division_tp": int(summary["division_tp"]),
            "division_fp": int(summary["division_fp"]),
            "division_fn": int(summary["division_fn"]),
        }
        row["passes_gate"] = bool(
            row["variant"] != "control_public"
            and row["delta"] >= 0.005
            and row["division_tp"] > int(base["division_tp"])
            and row["adj_edge_delta"] >= -0.001
        )
        rows.append(row)
    report = {
        "experiment": EXPERIMENT,
        "videos": len(cfg.selected_stems),
        "gate": "score >= control + 0.005, division TP up, adj_edge delta >= -0.001",
        "rows": rows,
        "winners": [row["variant"] for row in rows if row["passes_gate"]],
    }
    atomic_json(cfg.output_dir / "results.json", report)
    lines = [
        "# Friend A B20 DivNet results",
        "",
        f"Videos: {len(cfg.selected_stems)}. Gate: {report['gate']}.",
        "",
        "| variant | score | delta | adj edge | edge delta | div J | TP/FP/FN | gate |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variant']} | {row['score']:.4f} | {row['delta']:+.4f} | "
            f"{row['adj_edge']:.4f} | {row['adj_edge_delta']:+.4f} | "
            f"{row['division_jaccard']:.4f} | {row['division_tp']}/{row['division_fp']}/{row['division_fn']} | "
            f"{'PASS' if row['passes_gate'] else '-'} |"
        )
    lines.extend(["", "Winners: " + (", ".join(report["winners"]) or "none"), ""])
    text = "\n".join(lines)
    (cfg.output_dir / "result.md").write_text(text, encoding="utf-8")
    tracked = cfg.repo_root / "experiments" / EXPERIMENT / "results"
    tracked.mkdir(parents=True, exist_ok=True)
    atomic_json(tracked / "b20_final.json", report)
    (tracked / "b20_final.md").write_text(text, encoding="utf-8")
    return report


def run_pipeline(cfg: B20Config) -> dict[str, Any]:
    state = load_state(cfg)
    if not cfg.run_pipeline:
        print("BIOHUB_B20_RUN=0: preflight only")
        return state
    try:
        run_smoke(cfg, state)
        for index, stem in enumerate(cfg.selected_stems, start=1):
            print(f"\nPASS 1 [{index}/{len(cfg.selected_stems)}] {stem}", flush=True)
            run_pass1_video(cfg, stem, state)
        state["stages"]["pass1"] = True
        save_state(cfg, state)

        run_divnet(cfg, cfg.selected_stems, "divnet_all")
        state["stages"]["divnet"] = True
        save_state(cfg, state)
        check_stop(cfg)

        results = [run_pass2(cfg, cfg.selected_stems, "control_public", "public")]
        state["stages"]["control"] = True
        save_state(cfg, state)
        for top_k, threshold in GRID:
            label = f"divnet_k{top_k}_t{threshold:.1f}".replace(".", "p")
            results.append(
                run_pass2(
                    cfg,
                    cfg.selected_stems,
                    label,
                    "divnet",
                    top_k,
                    threshold,
                    cfg.score_file,
                )
            )
            state["stages"][label] = True
            save_state(cfg, state)
            check_stop(cfg)
        report = build_report(cfg, results)
        state["stages"]["complete"] = True
        state["report"] = report
        save_state(cfg, state)
        return state
    except StopRequested as exc:
        state["status"] = "stopped_safely"
        state["message"] = str(exc)
        save_state(cfg, state)
        print(f"\nSAFE STOP: {exc}\nRun All again to resume.", flush=True)
        return state
    except KeyboardInterrupt:
        state["status"] = "stopped_safely"
        state["message"] = "KeyboardInterrupt"
        save_state(cfg, state)
        print("\nSAFE STOP: completed files are reusable. Run All again to resume.", flush=True)
        return state


def compact_status(cfg: B20Config) -> dict[str, Any]:
    state = load_state(cfg)
    selected = cfg.selected_stems
    status = {
        "selected": len(selected),
        "raw": sum((cfg.cache / "raw" / f"{stem}.geff").is_dir() for stem in selected),
        "checkpoint": sum((cfg.cache / "ckpt" / f"{stem}.npz").is_file() for stem in selected),
        "deepcenter": sum((cfg.cache / "dc" / f"{stem}.npz").is_file() for stem in selected),
        "divnet": sum((cfg.cache / "divnet" / f"{stem}.npz").is_file() for stem in selected),
        "stages": state.get("stages", {}),
        "stop_file": str(cfg.stop_file),
        "output": str(cfg.output_dir),
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return status
