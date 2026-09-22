#!/usr/bin/env python3
"""
DAHP evaluation utility
====================
Three inference modes are supported; all emit standard COCO metrics
(AP50-95/AP50/AP75/APs/APm/APl/per-class AP):
  full   : full-image inference (--imgsz)
  slice  : fixed-grid sliced inference (--slice/--overlap/--slice-imgsz)
  hybrid : full-image and sliced predictions merged

Prediction merging uses --merge nms|wbf.
"""

import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

CLASS_NAMES = [
    "pedestrian", "people", "bicycle", "car", "van",
    "truck", "tricycle", "awning-tricycle", "bus", "motor",
]


# ----------------------- Ground-truth construction -----------------------

def build_gt_coco(img_files, lbl_dir):
    """Convert YOLO labels to a COCO ground-truth dictionary."""
    categories = [{"id": i + 1, "name": n} for i, n in enumerate(CLASS_NAMES)]
    images, annotations = [], []
    ann_id = 1
    for img_id, img_path in enumerate(img_files, start=1):
        img = cv2.imread(str(img_path))
        if img is None:
            raise RuntimeError(f"cannot read image: {img_path}")
        ih, iw = img.shape[:2]
        images.append({"id": img_id, "file_name": img_path.name, "width": iw, "height": ih})
        lbl_path = lbl_dir / (img_path.stem + ".txt")
        if not lbl_path.exists():
            continue
        with open(lbl_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                try:
                    c = int(float(parts[0]))
                    cx, cy, w, h = (float(x) for x in parts[1:5])
                except ValueError:
                    continue
                if c < 0 or c >= len(CLASS_NAMES):
                    continue
                bw, bh = w * iw, h * ih
                x, y = (cx - w / 2) * iw, (cy - h / 2) * ih
                annotations.append({
                    "id": ann_id, "image_id": img_id, "category_id": c + 1,
                    "bbox": [x, y, bw, bh], "area": bw * bh, "iscrowd": 0,
                })
                ann_id += 1
    return {"images": images, "annotations": annotations, "categories": categories}


# ------------------------------ Prediction merge -------------------------

def _iou_matrix(boxes1, boxes2):
    """xyxy boxes IoU, [N,M]"""
    if len(boxes1) == 0 or len(boxes2) == 0:
        return np.zeros((len(boxes1), len(boxes2)))
    b1, b2 = boxes1[:, None, :], boxes2[None, :, :]
    ix1 = np.maximum(b1[..., 0], b2[..., 0])
    iy1 = np.maximum(b1[..., 1], b2[..., 1])
    ix2 = np.minimum(b1[..., 2], b2[..., 2])
    iy2 = np.minimum(b1[..., 3], b2[..., 3])
    inter = np.clip(ix2 - ix1, 0, None) * np.clip(iy2 - iy1, 0, None)
    a1 = (b1[..., 2] - b1[..., 0]) * (b1[..., 3] - b1[..., 1])
    a2 = (b2[..., 2] - b2[..., 0]) * (b2[..., 3] - b2[..., 1])
    return inter / np.clip(a1 + a2 - inter, 1e-9, None)


def nms_merge(boxes, scores, classes, iou_thr):
    """Return indices retained by class-aware, score-descending NMS."""
    keep = []
    for c in np.unique(classes):
        idx = np.where(classes == c)[0]
        order = scores[idx].argsort()[::-1]
        idx = idx[order]
        while len(idx) > 0:
            keep.append(idx[0])
            if len(idx) == 1:
                break
            top = boxes[idx[0]:idx[0] + 1]
            ious = _iou_matrix(top, boxes[idx[1:]])[0]
            idx = idx[1:][ious <= iou_thr]
    keep = np.array(keep, dtype=int)
    order = scores[keep].argsort()[::-1]
    return keep[order]


def wbf_merge(boxes, scores, classes, iou_thr):
    """Return merged boxes, scores, and classes using weighted box fusion."""
    out_boxes, out_scores, out_classes = [], [], []
    for c in np.unique(classes):
        idx = np.where(classes == c)[0]
        order = scores[idx].argsort()[::-1]
        idx = idx[order]
        b, s = boxes[idx], scores[idx]
        used = np.zeros(len(idx), dtype=bool)
        clusters = []
        for i in range(len(idx)):
            if used[i]:
                continue
            members = [i]
            used[i] = True
            for j in range(i + 1, len(idx)):
                if used[j]:
                    continue
                if _iou_matrix(b[i:i + 1], b[j:j + 1])[0, 0] > iou_thr:
                    members.append(j)
                    used[j] = True
            clusters.append(members)
        for members in clusters:
            mb, ms = b[members], s[members]
            w = ms / ms.sum()
            fused = (mb * w[:, None]).sum(0)
            out_boxes.append(fused)
            out_scores.append(ms.mean())
            out_classes.append(c)
    if not out_boxes:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0)
    return np.stack(out_boxes), np.array(out_scores), np.array(out_classes)


# -------------------------------- Inference ------------------------------

def slice_offsets(size, slice_, overlap):
    """Generate slice origins that cover the right and bottom borders."""
    if size <= slice_:
        return [0]
    stride = max(int(slice_ * (1 - overlap)), 1)
    offs = list(range(0, size - slice_ + 1, stride))
    if offs[-1] != size - slice_:
        offs.append(size - slice_)
    return offs


def predict_full(model, img_path, imgsz, conf, max_det, augment=False):
    r = model.predict(str(img_path), imgsz=imgsz, conf=conf, iou=0.7,
                      max_det=max_det, augment=augment, verbose=False)[0]
    if r.boxes is None or len(r.boxes) == 0:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0)
    return (r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy(),
            r.boxes.cls.cpu().numpy())


def predict_sliced(model, img, slice_, overlap, slice_imgsz, conf, max_det):
    """Return boxes, scores, and classes in global image coordinates."""
    H, W = img.shape[:2]
    crops, metas = [], []
    for y0 in slice_offsets(H, slice_, overlap):
        for x0 in slice_offsets(W, slice_, overlap):
            crops.append(img[y0:y0 + slice_, x0:x0 + slice_])
            metas.append((x0, y0))
    results = model.predict(crops, imgsz=slice_imgsz, conf=conf, iou=0.7,
                            max_det=max_det, verbose=False)
    all_boxes, all_scores, all_classes = [], [], []
    for (x0, y0), r in zip(metas, results):
        if r.boxes is None or len(r.boxes) == 0:
            continue
        b = r.boxes.xyxy.cpu().numpy()
        b[:, [0, 2]] += x0
        b[:, [1, 3]] += y0
        all_boxes.append(b)
        all_scores.append(r.boxes.conf.cpu().numpy())
        all_classes.append(r.boxes.cls.cpu().numpy())
    if not all_boxes:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0)
    return np.concatenate(all_boxes), np.concatenate(all_scores), np.concatenate(all_classes)


# ------------------------------ COCO evaluation --------------------------

def coco_eval(gt_coco, pred_json, per_class=True, maxdets=300):
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    coco_gt = COCO()
    coco_gt.dataset = gt_coco
    coco_gt.createIndex()
    coco_dt = coco_gt.loadRes(pred_json)

    e = COCOeval(coco_gt, coco_dt, "bbox")
    e.params.maxDets = [1, 10, maxdets]
    e.evaluate()
    e.accumulate()
    e.summarize()
    stats = _stats_from_eval(e)  # Bypass summarize()'s maxDets=100 assumption.

    per_class_ap = {}
    if per_class:
        for cat in gt_coco["categories"]:
            e_c = COCOeval(coco_gt, coco_dt, "bbox")
            e_c.params.maxDets = [1, 10, maxdets]
            e_c.params.catIds = [cat["id"]]
            e_c.evaluate()
            e_c.accumulate()
            e_c.summarize()
            s_c = _stats_from_eval(e_c)
            per_class_ap[cat["name"]] = {
                "AP": s_c[0], "AP50": s_c[1], "AP75": s_c[2],
                "APs": s_c[3], "APm": s_c[4], "APl": s_c[5],
            }
    return {
        "AP50-95": stats[0], "AP50": stats[1], "AP75": stats[2],
        "APs": stats[3], "APm": stats[4], "APl": stats[5],
        "AR100": stats[6],
        "per_class": per_class_ap,
    }


def _stats_from_eval(e):
    """Compute metrics directly from COCOeval precision/recall arrays.

    pycocotools summarize() assumes maxDets=100 and returns -1 for another N,
    so the required summaries are computed explicitly.
    precision: [T,R,K,A,M], recall: [T,K,A,M]; A: 0=all,1=small,2=medium,3=large
    """
    prec = e.eval["precision"]
    rec = e.eval["recall"]
    mi = len(e.params.maxDets) - 1

    def _ap(t_idx=None, a_idx=0):
        s = prec if t_idx is None else prec[t_idx:t_idx + 1]
        s = s[:, :, :, a_idx, mi]
        v = s[s > -1]
        return float(v.mean()) if len(v) else -1.0

    ar = rec[:, 0, mi]
    ar_v = ar[ar > -1]
    return [
        _ap(), _ap(0), _ap(5), _ap(a_idx=1), _ap(a_idx=2), _ap(a_idx=3),
        float(ar_v.mean()) if len(ar_v) else -1.0,
    ]


# -------------------------------- Main flow ------------------------------

def main():
    p = argparse.ArgumentParser(description="DAHP-Slice eval (full/slice/hybrid)")
    p.add_argument("--model", type=str, default="runs/baseline_v8mP2/weights/best.pt")
    p.add_argument("--models", type=str, default=None,
                   help="comma-separated ensemble checkpoints (overrides --model)")
    p.add_argument("--slice-model", type=str, default=None,
                   help="second model for hybrid sliced inference (default: --model)")
    p.add_argument("--img-dir", type=str,
                   default="data/VisDrone2019/VisDrone2019-DET-val/images")
    p.add_argument("--lbl-dir", type=str, default=None)
    p.add_argument("--mode", choices=["full", "slice", "hybrid", "ensemble"], default="full")
    p.add_argument("--imgsz", type=int, default=1280, help="full-image inference size")
    p.add_argument("--slice", type=int, default=640, help="slice size")
    p.add_argument("--overlap", type=float, default=0.2)
    p.add_argument("--slice-imgsz", type=int, default=None, help="sliced inference size (default: slice size)")
    p.add_argument("--conf", type=float, default=0.001)
    p.add_argument("--merge", choices=["nms", "wbf"], default="nms")
    p.add_argument("--merge-iou", type=float, default=0.55)
    p.add_argument("--coco-maxdets", type=int, default=300,
                   help="COCO eval maxDets (300 = ultralytics val protocol)")
    p.add_argument("--tta", action="store_true", help="enable TTA for full-image mode")
    p.add_argument("--max-det", type=int, default=1000)
    p.add_argument("--device", type=str, default="0")
    p.add_argument("--tag", type=str, default=None)
    p.add_argument("--out-dir", type=str, default="results/eval")
    args = p.parse_args()

    slice_imgsz = args.slice_imgsz or args.slice
    img_dir = Path(args.img_dir)
    lbl_dir = Path(args.lbl_dir) if args.lbl_dir else img_dir.parent / "labels"
    img_files = sorted(q for q in img_dir.rglob("*") if q.suffix.lower() in {".jpg", ".jpeg", ".png"})

    from ultralytics import YOLO
    models = None
    if args.mode == "ensemble":
        assert args.models, "--models path1,path2,... is required for ensembles"
        model_paths = [m.strip() for m in args.models.split(",") if m.strip()]
        models = [YOLO(mp) for mp in model_paths]
        print(f"ensemble: {len(models)} models")
    model = models[0] if models else YOLO(args.model)
    slice_model = YOLO(args.slice_model) if args.slice_model else model

    print(f"\n=== DAHP eval: mode={args.mode} model={args.model} ===")
    print(f"images: {len(img_files)}  imgsz={args.imgsz}  slice={args.slice}@{args.overlap}"
          f"  slice_imgsz={slice_imgsz}  merge={args.merge}@{args.merge_iou}")

    gt_coco = build_gt_coco(img_files, lbl_dir)
    print(f"GT: {len(gt_coco['images'])} images, {len(gt_coco['annotations'])} boxes")

    pred_json = []
    n_slices_total, t_inf = 0, 0.0
    t0 = time.time()

    for img_id, img_path in enumerate(tqdm(img_files, desc="infer"), start=1):
        if args.mode in ("slice", "hybrid"):
            img = cv2.imread(str(img_path))
            if img is None:
                raise RuntimeError(f"cannot read image: {img_path}")
            H, W = img.shape[:2]

        if args.mode == "ensemble":
            t1 = time.time()
            eb, es, ec = [], [], []
            for m in models:
                b, s, c = predict_full(m, img_path, args.imgsz,
                                       args.conf, args.max_det,
                                       augment=args.tta)
                if len(b):
                    eb.append(b); es.append(s); ec.append(c)
            if eb:
                boxes = np.concatenate(eb); scores = np.concatenate(es); classes = np.concatenate(ec)
            else:
                boxes = np.zeros((0, 4)); scores, classes = np.zeros(0), np.zeros(0)
            t_inf += time.time() - t1
        elif args.mode == "full":
            t1 = time.time()
            boxes, scores, classes = predict_full(model, img_path, args.imgsz,
                                                  args.conf, args.max_det,
                                                  augment=args.tta)
            t_inf += time.time() - t1
        elif args.mode == "slice":
            t1 = time.time()
            boxes, scores, classes = predict_sliced(
                model, img, args.slice, args.overlap, slice_imgsz,
                args.conf, args.max_det)
            t_inf += time.time() - t1
            n_slices_total += (len(slice_offsets(H, args.slice, args.overlap))
                               * len(slice_offsets(W, args.slice, args.overlap)))
        else:  # hybrid
            t1 = time.time()
            fb, fs, fc = predict_full(model, img_path, args.imgsz,
                                      args.conf, args.max_det,
                                      augment=args.tta)
            sb, ss, sc = predict_sliced(slice_model, img, args.slice, args.overlap,
                                        slice_imgsz, args.conf, args.max_det)
            t_inf += time.time() - t1
            if len(fb) or len(sb):
                boxes = np.concatenate([fb, sb])
                scores = np.concatenate([fs, ss])
                classes = np.concatenate([fc, sc])
            else:
                boxes = np.zeros((0, 4))
                scores, classes = np.zeros(0), np.zeros(0)
            n_slices_total += (len(slice_offsets(H, args.slice, args.overlap))
                               * len(slice_offsets(W, args.slice, args.overlap))) + 1

        # Full-image predictions already use internal NMS at IoU 0.7.
        if args.mode in ("slice", "hybrid", "ensemble") and len(boxes) > 1:
            if args.merge == "nms":
                keep = nms_merge(boxes, scores, classes, args.merge_iou)
                boxes, scores, classes = boxes[keep], scores[keep], classes[keep]
            else:
                boxes, scores, classes = wbf_merge(boxes, scores, classes, args.merge_iou)
        if len(scores) > args.max_det:
            top = scores.argsort()[::-1][:args.max_det]
            boxes, scores, classes = boxes[top], scores[top], classes[top]

        for b, s, c in zip(boxes, scores, classes):
            x1, y1, x2, y2 = b.tolist()
            pred_json.append({
                "image_id": img_id, "category_id": int(c) + 1,
                "bbox": [x1, y1, x2 - x1, y2 - y1], "score": float(s),
            })

    wall = time.time() - t0
    print(f"\ninference: {t_inf:.1f}s  wall: {wall:.1f}s  "
          f"fps(inf)={len(img_files)/max(t_inf,1e-9):.2f}  preds={len(pred_json)}")
    if args.mode != "full":
        print(f"avg slices/image: {n_slices_total/len(img_files):.1f}")

    metrics = coco_eval(gt_coco, pred_json, maxdets=args.coco_maxdets)
    metrics["config"] = vars(args)
    metrics["timing"] = {"infer_s": t_inf, "wall_s": wall,
                         "fps_infer": len(img_files) / max(t_inf, 1e-9),
                         "avg_slices_per_image": n_slices_total / max(len(img_files), 1),
                         "num_predictions": len(pred_json)}

    tag = args.tag or f"{args.mode}_{args.slice}_{args.merge}"
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{tag}.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    with open(out_path.with_suffix(".preds.json"), "w") as f:
        json.dump(pred_json, f)
    print(f"\nsaved: {out_path}")
    print(f"\n===== SUMMARY [{tag}] =====")
    print(f"AP50-95 = {metrics['AP50-95']:.4f}   AP50 = {metrics['AP50']:.4f}   "
          f"AP75 = {metrics['AP75']:.4f}")
    print(f"APs = {metrics['APs']:.4f}  APm = {metrics['APm']:.4f}  APl = {metrics['APl']:.4f}")


if __name__ == "__main__":
    main()
