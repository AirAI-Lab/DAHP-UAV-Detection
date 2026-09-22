#!/usr/bin/env python3
"""Convert a YOLO detection split to a COCO-style JSON annotation file."""
import argparse
import json
from pathlib import Path

from PIL import Image

DEFAULT_CLASSES = [
    "pedestrian", "people", "bicycle", "car", "van",
    "truck", "tricycle", "awning-tricycle", "bus", "motor",
]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--image-dir", type=Path, required=True)
    p.add_argument("--label-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--classes", default=",".join(DEFAULT_CLASSES))
    p.add_argument("--dedupe", action="store_true",
                   help="Drop exact duplicate YOLO lines in one image (recommended for training).")
    p.add_argument("--allow-missing-labels", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    names = [x.strip() for x in args.classes.split(",") if x.strip()]
    if not names:
        raise ValueError("At least one class name is required")
    images, annotations = [], []
    ann_id = 1
    duplicate_boxes = invalid_boxes = missing_labels = 0

    image_files = sorted(p for p in args.image_dir.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)
    if not image_files:
        raise FileNotFoundError(f"No images under {args.image_dir}")

    for image_id, image_path in enumerate(image_files, 1):
        label_path = args.label_dir / f"{image_path.stem}.txt"
        if not label_path.exists():
            if not args.allow_missing_labels:
                raise FileNotFoundError(label_path)
            missing_labels += 1
        with Image.open(image_path) as image:
            width, height = image.size
        images.append({"id": image_id, "file_name": image_path.name, "width": width, "height": height})

        seen = set()
        if label_path.exists():
            for line_number, line in enumerate(label_path.read_text().splitlines(), 1):
                fields = line.split()
                if not fields:
                    continue
                if len(fields) < 5:
                    invalid_boxes += 1
                    continue
                try:
                    class_id = int(fields[0])
                    cx, cy, w, h = map(float, fields[1:5])
                except ValueError:
                    invalid_boxes += 1
                    continue
                if class_id < 0 or class_id >= len(names):
                    raise ValueError(f"{label_path}:{line_number}: class {class_id} outside [0,{len(names)-1}]")
                if not all(0.0 <= v <= 1.0 for v in (cx, cy, w, h)):
                    invalid_boxes += 1
                    continue
                key = (class_id, round(cx, 12), round(cy, 12), round(w, 12), round(h, 12))
                if args.dedupe and key in seen:
                    duplicate_boxes += 1
                    continue
                seen.add(key)
                box_w, box_h = w * width, h * height
                x, y = (cx - w / 2) * width, (cy - h / 2) * height
                annotations.append({
                    "id": ann_id,
                    "image_id": image_id,
                    "category_id": class_id + 1,
                    "bbox": [round(x, 6), round(y, 6), round(box_w, 6), round(box_h, 6)],
                    "area": round(box_w * box_h, 6),
                    "iscrowd": 0,
                })
                ann_id += 1

    categories = [{"id": i + 1, "name": name} for i, name in enumerate(names)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "info": {"description": "Converted from YOLO labels", "dedupe": bool(args.dedupe)},
        "images": images,
        "annotations": annotations,
        "categories": categories,
    }
    args.output.write_text(json.dumps(payload))
    print(json.dumps({
        "images": len(images), "annotations": len(annotations), "categories": len(categories),
        "duplicate_boxes_removed": duplicate_boxes, "invalid_boxes": invalid_boxes,
        "missing_label_images": missing_labels, "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
