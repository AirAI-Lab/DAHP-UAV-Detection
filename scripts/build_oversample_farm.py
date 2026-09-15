#!/usr/bin/env python3
"""
T1 尾类过采样符号链接农场
=========================
为包含尾类 (awning-tricycle/tricycle/bus) 的图像创建额外符号链接副本,
实现数据层静态过采样 (ultralytics 目录扫描自然生效, 无需改训练器)。

输出:
  <out>/images/  — 全部原图符号链接 + 尾类图像的 _os1 副本
  <out>/labels/  — 对应标签符号链接 (labels 查找基于路径字符串, 符号链接可用)
  <out>/dahp.yaml
"""

import argparse
import random
from pathlib import Path

CLASS_NAMES = [
    "pedestrian", "people", "bicycle", "car", "van",
    "truck", "tricycle", "awning-tricycle", "bus", "motor",
]


def main():
    p = argparse.ArgumentParser(description="Build tail-oversample symlink farm")
    p.add_argument("--root", type=str,
                   default="data/VisDrone2019")
    p.add_argument("--out", type=str,
                   default="data/VisDrone2019-dahp-train")
    p.add_argument("--copies", type=int, default=2, help="尾类图像总份数 (原1份+额外copies-1)")
    p.add_argument("--classes", type=str, default="6,7,8",
                   help="过采样类集 (逗号分隔 id; 频率尾类=6,7,8; "
                        "混淆轴=1,2,4,5,7 people,bicycle,van,truck,awning)")
    p.add_argument("--random-count", type=int, default=0,
                   help=">0 时改为随机过采样 N 张图 (与类无关, 用作数据量对照)")
    args = p.parse_args()
    tail_classes = {int(x) for x in args.classes.split(",")}
    rng = random.Random(args.seed if hasattr(args, "seed") else 42)
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
        has_tail = False
        if random_targets:
            has_tail = img.stem in random_targets
        elif lbl.exists():
            with open(lbl) as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 5 and int(float(parts[0])) in tail_classes:
                        has_tail = True
                        break
        copies = args.copies if has_tail else 1
        for k in range(copies):
            suffix = f"_os{k}" if k else ""
            (out / "images" / f"{img.stem}{suffix}.jpg").symlink_to(img.resolve())
            if lbl.exists():
                (out / "labels" / f"{img.stem}{suffix}.txt").symlink_to(lbl.resolve())
            n_total += 1
        if has_tail:
            n_tail += 1

    yaml_path = out / "dahp.yaml"
    yaml_path.write_text(
        f"# T1 tail-oversampled train farm ({args.copies}x for tail classes)\n"
        f"train: {out}/images\n"
        f"val: {val_img}\n\n"
        f"nc: 10\n"
        f"names:\n" + "".join(f"  - {n}\n" for n in CLASS_NAMES)
    )
    print(f"images: {n_total} links ({n_tail} tail images x{args.copies})")
    print(f"yaml: {yaml_path}")


if __name__ == "__main__":
    main()
