#!/usr/bin/env python3
"""Build a union-rebalanced VisDrone training directory using image links.

Images containing at least one selected tail or confusion-axis class receive
additional linked copies. Ultralytics consumes the resulting directory without
trainer changes. The outputs are `images/`, `labels/`, and `dahp.yaml`.
"""

import argparse
import random
from pathlib import Path

CLASS_NAMES = [
    "pedestrian", "people", "bicycle", "car", "van",
    "truck", "tricycle", "awning-tricycle", "bus", "motor",
]


def main():
    p = argparse.ArgumentParser(
        description="Build a union-rebalanced dataset using image links"
    )
    p.add_argument("--root", type=str,
                   default="data/VisDrone2019")
    p.add_argument("--out", type=str,
                   default="data/VisDrone2019-dahp-train")
    p.add_argument("--copies", type=int, default=2,
                   help="total copies for selected images")
    p.add_argument("--classes", type=str, default="4,5,6,7,8",
                   help="selected IDs: van,truck,tricycle,awning-tricycle,bus")
    p.add_argument("--random-count", type=int, default=0,
                   help="if >0, duplicate N random images as a volume control")
    p.add_argument("--seed", type=int, default=42,
                   help="random seed for the volume-control experiment")
    args = p.parse_args()
    selected_classes = {int(x) for x in args.classes.split(",")}
    rng = random.Random(args.seed)
    random_targets = set()
    src_img_dir = Path(args.root) / "VisDrone2019-DET-train" / "images"
    if args.random_count > 0:
        all_imgs = sorted(src_img_dir.glob("*.jpg"))
        random_targets = set(rng.sample([p.stem for p in all_imgs], min(args.random_count, len(all_imgs))))

    src_img = Path(args.root) / "VisDrone2019-DET-train" / "images"
    src_lbl = Path(args.root) / "VisDrone2019-DET-train" / "labels"
    val_img = Path(args.root) / "VisDrone2019-DET-val" / "images"
    out = Path(args.out)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "labels").mkdir(parents=True, exist_ok=True)

    n_total = n_tail = 0
    for img in sorted(src_img.glob("*.jpg")):
        lbl = src_lbl / (img.stem + ".txt")
        selected = False
        if random_targets:
            selected = img.stem in random_targets
        elif lbl.exists():
            with open(lbl) as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 5 and int(float(parts[0])) in selected_classes:
                        selected = True
                        break
        copies = args.copies if selected else 1
        for k in range(copies):
            suffix = f"_os{k}" if k else ""
            (out / "images" / f"{img.stem}{suffix}.jpg").symlink_to(img.resolve())
            if lbl.exists():
                (out / "labels" / f"{img.stem}{suffix}.txt").symlink_to(lbl.resolve())
            n_total += 1
        if selected:
            n_tail += 1

    yaml_path = out / "dahp.yaml"
    yaml_path.write_text(
        f"# Union-rebalanced training set ({args.copies}x for selected classes)\n"
        f"train: {out}/images\n"
        f"val: {val_img}\n\n"
        f"nc: 10\n"
        f"names:\n" + "".join(f"  - {n}\n" for n in CLASS_NAMES)
    )
    print(f"images: {n_total} links ({n_tail} selected images x{args.copies})")
    print(f"yaml: {yaml_path}")


if __name__ == "__main__":
    main()
