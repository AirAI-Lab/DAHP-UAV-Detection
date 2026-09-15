#!/usr/bin/env python3
"""Latency / throughput / VRAM benchmark for trained checkpoints.

Protocol (matches the paper): single GPU, batch 1, FP16, 50 measured images
after 10 warmup images, conf=0.25.
"""
import argparse, json, time
from pathlib import Path

import torch

N_WARMUP, N_MEASURE = 10, 50


def bench_ultralytics(tag, weights, imgsz, val_dir, device=0):
    from ultralytics import YOLO
    m = YOLO(weights)
    imgs = sorted(Path(val_dir).glob("*.jpg"))[: N_WARMUP + N_MEASURE]
    for p in imgs[:N_WARMUP]:
        m.predict(str(p), imgsz=imgsz, conf=0.25, half=True, verbose=False, device=device)
    torch.cuda.synchronize()
    t0 = time.time()
    for p in imgs[N_WARMUP:]:
        m.predict(str(p), imgsz=imgsz, conf=0.25, half=True, verbose=False, device=device)
    torch.cuda.synchronize()
    dt = (time.time() - t0) / N_MEASURE
    vram = torch.cuda.max_memory_allocated() / 1024**3
    n_params = sum(p.numel() for p in m.model.parameters())
    res = {"tag": tag, "imgsz": imgsz, "ms_per_img": dt * 1000, "fps": 1 / dt,
           "params_M": n_params / 1e6, "vram_GB": vram, "half": True}
    print(f"{tag:28s} @{imgsz}: {dt*1000:7.1f} ms/img  {1/dt:6.1f} FPS  "
          f"{n_params/1e6:6.1f}M params  {vram:.1f}GB")
    torch.cuda.reset_peak_memory_stats()
    return res


def main():
    p = argparse.ArgumentParser(description="FPS benchmark (batch 1, FP16)")
    p.add_argument("--val-dir", required=True)
    p.add_argument("--runs", nargs="+", required=True,
                   help="tag=weights.pt:imgsz entries")
    p.add_argument("--device", default="0")
    p.add_argument("--out", default="results/fps_benchmark.json")
    args = p.parse_args()

    out = []
    for spec in args.runs:
        tag, rest = spec.split("=", 1)
        weights, imgsz = rest.rsplit(":", 1)
        out.append(bench_ultralytics(tag, weights, int(imgsz), args.val_dir, args.device))

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(outp, "w"), indent=2)
    print(f"saved {outp}")


if __name__ == "__main__":
    main()
