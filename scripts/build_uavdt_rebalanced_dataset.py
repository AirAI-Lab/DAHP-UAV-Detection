#!/usr/bin/env python3
"""Build a union-rebalanced UAVDT training directory using image links.

The default selected set follows the label profile: tail classes {truck, bus}
plus the head-anchored confusion-axis class {van}. The outputs are `images/`,
`labels/`, and `uavdt_dahp.yaml`.
"""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(
        description="Build a UAVDT union-rebalanced dataset using image links"
    )
    p.add_argument("--root", type=str,
                   default="data/UAVDT/UAVDT-2024-DET")
    p.add_argument("--out", type=str,
                   default="data/UAVDT/uavdt-dahp-train")
    p.add_argument("--copies", type=int, default=2,
                   help="total copies for selected images")
    p.add_argument("--classes", type=str, default="1,2,3",
                   help="selected classes: 1=truck, 2=bus, 3=van")
    args = p.parse_args()

    cls_set = {int(x) for x in args.classes.split(",")}
    root = Path(args.root)
    src_img = root / "train" / "images"
    src_lbl = root / "train" / "labels"
    val_img = root / "val" / "images"
    out = Path(args.out)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "labels").mkdir(parents=True, exist_ok=True)

    n_total = n_hit = n_extra = 0
    for img in sorted(src_img.glob("*.jpg")):
        lbl = src_lbl / (img.stem + ".txt")
        hit = False
        if lbl.exists():
            with open(lbl) as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 5 and int(parts[0]) in cls_set:
                        hit = True
                        break
        n_total += 1
        if hit:
            n_hit += 1
        # Original image link.
        (out / "images" / img.name).symlink_to(img.resolve())
        (out / "labels" / (img.stem + ".txt")).symlink_to(lbl.resolve())
        # Additional copies for selected images.
        if hit:
            for k in range(1, args.copies):
                (out / "images" / f"{img.stem}_os{k}.jpg").symlink_to(img.resolve())
                (out / "labels" / f"{img.stem}_os{k}.txt").symlink_to(lbl.resolve())
                n_extra += 1

    yaml_path = out / "uavdt_dahp.yaml"
    yaml_path.write_text(
        f"# UAVDT union-rebalanced training set (x{args.copies})\n"
        f"# selected classes: {sorted(cls_set)} (1=truck, 2=bus, 3=van)\n"
        f"train: {out / 'images'}\n"
        f"val: {val_img}\n"
        "nc: 4\n"
        "names:\n  - car\n  - truck\n  - bus\n  - van\n"
    )
    print(f"total={n_total} hit={n_hit} ({n_hit/max(n_total,1)*100:.1f}%) "
          f"extra_links={n_extra} total_images={n_total + n_extra}")
    print(f"yaml: {yaml_path}")


if __name__ == "__main__":
    main()
