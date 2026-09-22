#!/usr/bin/env python3
"""Stage-wise FPS/latency/memory benchmark for Ultralytics detectors.

Protocol:
  * sorted VisDrone-val JPEGs, batch size 1, FP16, confidence 0.25;
  * configurable warmup and at least 200 measured images for final runs;
  * end-to-end wall time plus Ultralytics preprocess/inference/postprocess
    timings from ``Results.speed``;
  * peak CUDA active allocation and reserved memory after warmup;
  * an exclusive-GPU check so shared-GPU smoke tests are not accidentally
    used as paper evidence.
"""

from __future__ import annotations

import argparse
import csv
import gc
import io
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

import numpy as np
import torch


DEFAULT_VAL_DIR = (
    os.environ.get(
        "DAHP_VISDRONE_VAL_DIR",
        "data/VisDrone2019/VisDrone2019-DET-val/images",
    )
)

DEFAULT_BENCHMARKS = {
    "baseline_v8mP2_1280": ("runs/baseline_v8mP2_1280/weights/best.pt", 1280),
    "v8lP2_1600": ("runs/v8lP2_1600/weights/best.pt", 1600),
    "dahpL_1600": ("runs/dahpL_1600/weights/best.pt", 1600),
    "vanilla_v8l_1600": (
        "runs/vanilla_v8l_1600/weights/best.pt",
        1600,
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--val-dir", type=Path, default=Path(DEFAULT_VAL_DIR))
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--measure", type=int, default=300)
    parser.add_argument(
        "--tags",
        default=",".join(DEFAULT_BENCHMARKS),
        help="comma-separated benchmark tags",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/eval/fps_benchmark_300.json"),
    )
    parser.add_argument(
        "--require-exclusive",
        action="store_true",
        help="fail if another compute process or substantial GPU memory use exists",
    )
    parser.add_argument(
        "--allow-shared",
        action="store_true",
        help="permit a short shared-GPU smoke test; result is marked non-paper",
    )
    args = parser.parse_args()
    if args.measure < 1:
        parser.error("--measure must be positive")
    if args.allow_shared and args.require_exclusive:
        parser.error("--allow-shared and --require-exclusive are mutually exclusive")
    return args


def run_nvidia_smi(query: str) -> list[list[str]]:
    proc = subprocess.run(
        ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [row for row in csv.reader(io.StringIO(proc.stdout)) if row]


def gpu_snapshot(device: int, own_pid: int | None = None) -> dict:
    gpu_rows = run_nvidia_smi(
        "index,uuid,name,utilization.gpu,memory.used,memory.total"
    )
    gpu = next((row for row in gpu_rows if row[0].strip() == str(device)), None)
    if gpu is None:
        raise RuntimeError(f"GPU {device} is not visible to nvidia-smi")

    apps_query = "gpu_uuid,pid,process_name,used_memory"
    apps_proc = subprocess.run(
        [
            "nvidia-smi",
            f"--query-compute-apps={apps_query}",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    apps = [row for row in csv.reader(io.StringIO(apps_proc.stdout)) if row]
    uuid = gpu[1].strip()
    matching_apps = [row for row in apps if row[0].strip() == uuid]
    external_apps = [
        row for row in matching_apps if int(row[1]) != own_pid
    ]
    own_apps = [row for row in matching_apps if int(row[1]) == own_pid]
    used_mib = int(gpu[4].strip())
    no_external_compute_process = not external_apps
    exclusive = used_mib < 500 and no_external_compute_process
    if own_pid is not None and own_apps:
        # Once this long-lived benchmark process has created a CUDA context,
        # its residual context memory is expected. Exclusivity therefore means
        # no process other than this benchmark; the initial model call still
        # applies the strict <500 MiB device-memory check.
        exclusive = no_external_compute_process
    return {
        "index": int(gpu[0]),
        "uuid": uuid,
        "name": gpu[2].strip(),
        "utilization_percent": float(gpu[3]),
        "memory_used_MiB": used_mib,
        "memory_total_MiB": int(gpu[5]),
        "compute_processes": [
            {
                "pid": int(row[1]),
                "process_name": row[2].strip(),
                "used_memory_MiB": int(row[3]),
            }
            for row in matching_apps
        ],
        "external_compute_processes": [
            {
                "pid": int(row[1]),
                "process_name": row[2].strip(),
                "used_memory_MiB": int(row[3]),
            }
            for row in external_apps
        ],
        "exclusive": exclusive,
    }


def summarize(values: list[float]) -> dict:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean_ms": float(array.mean()),
        "std_ms": float(array.std(ddof=0)),
        "min_ms": float(array.min()),
        "p50_ms": float(np.percentile(array, 50)),
        "p95_ms": float(np.percentile(array, 95)),
        "max_ms": float(array.max()),
    }


def cumulative_normal_timing_stats(values: list[float]) -> dict:
    """Return mean/std in the same units as Ultralytics Results.speed (ms)."""
    return {
        "mean_ms": float(mean(values)),
        "std_ms": float(pstdev(values)) if len(values) > 1 else 0.0,
    }


def portable_loadavg() -> list[float] | None:
    try:
        return list(os.getloadavg())
    except (AttributeError, NotImplementedError, OSError):
        return None


def benchmark_one(
    tag: str,
    weights: str,
    imgsz: int,
    image_paths: list[Path],
    args: argparse.Namespace,
) -> dict:
    from ultralytics import YOLO

    before = gpu_snapshot(args.device, own_pid=os.getpid())
    if args.require_exclusive and not before["exclusive"]:
        raise RuntimeError(
            f"GPU {args.device} is not exclusive: {before['compute_processes']}; "
            "shared-GPU results must not be used in the paper"
        )

    model = YOLO(weights)
    warmup_paths = image_paths[: args.warmup]
    measure_paths = image_paths[args.warmup : args.warmup + args.measure]
    if len(measure_paths) != args.measure:
        raise RuntimeError(
            f"only {len(measure_paths)} measurement images available; need {args.measure}"
        )

    predict_kwargs = {
        "imgsz": imgsz,
        "conf": 0.25,
        "half": True,
        "verbose": False,
        "device": args.device,
        "profile": True,
    }

    for path in warmup_paths:
        model.predict(str(path), **predict_kwargs)
    # Ultralytics remaps a non-zero physical device index by setting
    # CUDA_VISIBLE_DEVICES and exposing it to PyTorch as local device 0.
    # Use the post-selection current device for synchronization and allocator
    # statistics while continuing to audit the requested physical GPU with
    # nvidia-smi.
    local_device = torch.cuda.current_device()
    torch.cuda.synchronize(local_device)
    torch.cuda.reset_peak_memory_stats(local_device)

    wall_times_ms: list[float] = []
    preprocess_ms: list[float] = []
    inference_ms: list[float] = []
    postprocess_ms: list[float] = []
    detections: list[int] = []

    overall_start = time.perf_counter()
    for path in measure_paths:
        image_start = time.perf_counter()
        results = model.predict(str(path), **predict_kwargs)
        torch.cuda.synchronize(local_device)
        wall_times_ms.append((time.perf_counter() - image_start) * 1000.0)
        if len(results) != 1:
            raise RuntimeError(f"expected one result for {path}, got {len(results)}")
        speed = results[0].speed
        preprocess_ms.append(float(speed["preprocess"]))
        inference_ms.append(float(speed["inference"]))
        postprocess_ms.append(float(speed["postprocess"]))
        detections.append(int(len(results[0].boxes)))
    overall_seconds = time.perf_counter() - overall_start

    peak_active = torch.cuda.max_memory_allocated(local_device) / 1024**3
    peak_reserved = torch.cuda.max_memory_reserved(local_device) / 1024**3
    after = gpu_snapshot(args.device, own_pid=os.getpid())

    parameter_count = sum(parameter.numel() for parameter in model.model.parameters())
    parameter_bytes = sum(
        parameter.numel() * parameter.element_size()
        for parameter in model.model.parameters()
    )
    end_to_end_ms = overall_seconds * 1000.0 / args.measure
    stage_means = {
        stage: cumulative_normal_timing_stats(values)["mean_ms"]
        for stage, values in {
            "preprocess": preprocess_ms,
            "inference": inference_ms,
            "postprocess": postprocess_ms,
        }.items()
    }
    stage_sum_ms = sum(stage_means.values())

    result = {
        "tag": tag,
        "weights": weights,
        "checkpoint_size_MB": Path(weights).stat().st_size / 1024**2,
        "imgsz": imgsz,
        "n_warmup": args.warmup,
        "n_measure": args.measure,
        "batch_size": 1,
        "precision": "fp16",
        "confidence_threshold": 0.25,
        "sync_per_image": True,
        "torch_local_device_after_ultralytics_selection": local_device,
        "params_M": parameter_count / 1e6,
        "parameter_memory_GB_after_half": parameter_bytes / 1024**3,
        "detections": {
            "total": int(sum(detections)),
            "mean_per_image": float(mean(detections)),
        },
        "latency_ms": {
            "end_to_end_wall": summarize(wall_times_ms),
            "ultralytics_preprocess": summarize(preprocess_ms),
            "ultralytics_inference": summarize(inference_ms),
            "ultralytics_postprocess": summarize(postprocess_ms),
            "stage_sum_mean_ms": stage_sum_ms,
            "file_io_and_pipeline_overhead_mean_ms": end_to_end_ms - stage_sum_ms,
        },
        "aggregate_end_to_end_ms_per_image": end_to_end_ms,
        "fps_end_to_end": args.measure / overall_seconds,
        "memory": {
            "peak_cuda_active_alloc_GB": peak_active,
            "peak_cuda_reserved_GB": peak_reserved,
            "device_used_after_MiB": after["memory_used_MiB"],
            "device_total_MiB": after["memory_total_MiB"],
        },
        "gpu": {
            "before": before,
            "after": after,
            "exclusive_at_start": before["exclusive"],
            "no_external_process_at_end": not after["external_compute_processes"],
            "paper_eligible": (
                before["exclusive"]
                and not after["external_compute_processes"]
                and args.measure >= 200
            ),
        },
    }

    print(
        f"{tag:24s} @{imgsz:4d}: "
        f"{end_to_end_ms:7.2f} ms/img {result['fps_end_to_end']:6.2f} FPS | "
        f"pre={stage_means['preprocess']:6.2f} "
        f"inf={stage_means['inference']:6.2f} "
        f"post={stage_means['postprocess']:6.2f} ms | "
        f"VRAM act/res={peak_active:.2f}/{peak_reserved:.2f} GB"
    )

    del model, results
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize(local_device)
    return result


def main() -> None:
    args = parse_args()
    if not args.allow_shared and args.measure < 200:
        raise SystemExit("final benchmark requires --measure >= 200")

    image_paths = sorted(args.val_dir.glob("*.jpg"))
    required = args.warmup + args.measure
    if len(image_paths) < required:
        raise RuntimeError(
            f"{args.val_dir} has {len(image_paths)} images; needs {required}"
        )

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    unknown = sorted(set(tags) - set(DEFAULT_BENCHMARKS))
    if unknown:
        raise SystemExit(f"unknown benchmark tags: {unknown}")

    import ultralytics

    loadavg_start = portable_loadavg()
    results = []
    for tag in tags:
        weights, imgsz = DEFAULT_BENCHMARKS[tag]
        results.append(
            benchmark_one(tag, weights, imgsz, image_paths, args)
        )

    output = {
        "schema_version": 2,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "dataset": "VisDrone2019-DET-val",
            "image_selection": "first sorted JPEGs after warmup",
            "batch_size": 1,
            "precision": "fp16",
            "confidence_threshold": 0.25,
            "n_warmup": args.warmup,
            "n_measure": args.measure,
            "stage_time_source": "Ultralytics Results.speed",
            "wall_time_source": "time.per_counter with CUDA synchronization per image",
            "exclusive_required_for_paper": True,
        },
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "ultralytics": ultralytics.__version__,
            "gpu_name": gpu_snapshot(args.device)["name"],
            "cpu_count": os.cpu_count(),
            "cpu_loadavg_start": loadavg_start,
            "cpu_loadavg_end": portable_loadavg(),
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(f"saved {args.output}")


if __name__ == "__main__":
    main()
