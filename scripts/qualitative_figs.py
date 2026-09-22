#!/usr/bin/env python3
"""Create qualitative baseline-versus-DAHP validation examples."""
import json
from pathlib import Path

import cv2

VAL_IMG = Path("data/VisDrone2019/VisDrone2019-DET-val/images")
VAL_LBL = Path("data/VisDrone2019/VisDrone2019-DET-val/labels")
NAMES = ["pedestrian", "people", "bicycle", "car", "van", "truck",
         "tricycle", "awning-tricycle", "bus", "motor"]
HARD = {"awning-tricycle", "tricycle", "bicycle", "people", "bus"}
COLORS = [(230, 159, 0), (86, 180, 233), (0, 158, 115), (240, 228, 66), (0, 114, 178),
          (213, 94, 0), (204, 121, 167), (0, 0, 0), (100, 100, 100), (60, 60, 60)]
OUT = Path("paper/qualitative")
OUT.mkdir(parents=True, exist_ok=True)


def select_images(n=6):
    scored = []
    for lp in sorted(VAL_LBL.glob("*.txt")):
        cls = [int(l.split()[0]) for l in open(lp) if l.strip()]
        hard = sum(1 for c in cls if NAMES[c] in HARD)
        scored.append((hard, len(cls), lp.stem))
    scored.sort(reverse=True)
    return [s[2] for s in scored[:n]]


def draw(img, boxes, with_score=False):
    im = img.copy()
    for b in boxes:
        x1, y1, x2, y2, c = b[:5]
        col = COLORS[int(c)]
        cv2.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), col, 2)
        label = NAMES[int(c)] + (f" {b[5]:.2f}" if with_score and len(b) > 5 else "")
        cv2.putText(im, label, (int(x1), max(12, int(y1) - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, col, 1)
    return im


def main():
    from ultralytics import YOLO
    base = YOLO("runs/baseline_v8mP2/weights/best.pt")
    ours = YOLO("runs/dahp_l_union/weights/best.pt")

    for stem in select_images(6):
        img_path = VAL_IMG / f"{stem}.jpg"
        img = cv2.imread(str(img_path))
        H, W = img.shape[:2]
        gt = []
        for l in open(VAL_LBL / f"{stem}.txt"):
            p = l.split()
            if len(p) < 5:
                continue
            c, cx, cy, bw, bh = int(p[0]), *map(float, p[1:5])
            gt.append([(cx - bw / 2) * W, (cy - bh / 2) * H,
                       (cx + bw / 2) * W, (cy + bh / 2) * H, c])

        def preds(model, imgsz, conf=0.25):
            r = model.predict(str(img_path), imgsz=imgsz, conf=conf, verbose=False)[0]
            out = []
            for b in r.boxes:
                xyxy = b.xyxy.cpu().numpy().tolist()[0]
                out.append(xyxy + [int(b.cls.item()), float(b.conf.item())])
            return out

        row_gt = draw(img, gt)
        row_base = draw(img, preds(base, 1280), True)
        row_ours = draw(img, preds(ours, 1600), True)
        # Concatenate three rows after resizing to a common width.
        h_target = 480
        rows = []
        for r in (row_gt, row_base, row_ours):
            s = h_target / r.shape[0]
            rows.append(cv2.resize(r, (int(r.shape[1] * s), h_target)))
        w_max = max(r.shape[1] for r in rows)
        canvas = [cv2.copyMakeBorder(r, 0, 0, 0, w_max - r.shape[1], cv2.BORDER_CONSTANT,
                                     value=(255, 255, 255)) for r in rows]
        vis = cv2.vconcat(canvas)
        for y, t in ((30, "GT"), (h_target + 30, "Baseline v8m-P2@1280"),
                     (2 * h_target + 30, "Ours DAHP-L (v8l-P2@1600)")):
            cv2.putText(vis, t, (15, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        out_path = OUT / f"qual_{stem}.jpg"
        cv2.imwrite(str(out_path), vis, [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"saved {out_path}")


if __name__ == "__main__":
    main()
