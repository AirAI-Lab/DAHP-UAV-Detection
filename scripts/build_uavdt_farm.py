#!/usr/bin/env python3
"""
UAVDT 尾类+混淆轴过采样符号链接农场 (DAHP-driven)
==================================================
画像结果 (results/uavdt_dahp_profile.json):
  频率尾类: truck(1), bus(2)  — car:bus = 30.7:1
  高混淆对: car<->van .935, car<->truck .888, truck<->van .863

策略映射 (与 VisDrone union 配方同构):
  过采样类集 = 尾类 {truck,bus} ∪ 混淆轴(排除头类 car) {van,truck}
             = {1 truck, 2 bus, 3 van}
  纯 car 图像不过采样 → 保持重平衡语义 (对应 VisDrone 中 car/pedestrian/motor 不入集)

输出: <out>/images, <out>/labels, <out>/uavdt_dahp.yaml
"""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description="Build UAVDT DAHP oversample symlink farm")
    p.add_argument("--root", type=str,
                   default="data/UAVDT/UAVDT-2024-DET")
    p.add_argument("--out", type=str,
                   default="data/UAVDT/uavdt-dahp-train")
    p.add_argument("--copies", type=int, default=2,
                   help="命中类图像总份数 (原1份 + 额外 copies-1)")
    p.add_argument("--classes", type=str, default="1,2,3",
                   help="过采样类集: 1=truck 2=bus 3=van (DAHP 派生)")
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
        # 原图链接 (始终 1 份)
        (out / "images" / img.name).symlink_to(img.resolve())
        (out / "labels" / (img.stem + ".txt")).symlink_to(lbl.resolve())
        # 命中类额外副本
        if hit:
            for k in range(1, args.copies):
                (out / "images" / f"{img.stem}_os{k}.jpg").symlink_to(img.resolve())
                (out / "labels" / f"{img.stem}_os{k}.txt").symlink_to(lbl.resolve())
                n_extra += 1

    yaml_path = out / "uavdt_dahp.yaml"
    yaml_path.write_text(
        f"# UAVDT DAHP union 农场: 尾类+混淆轴 过采样 x{args.copies}\n"
        f"# 过采样类集: {sorted(cls_set)} (1=truck 2=bus 3=van)\n"
        f"train: {out / 'images'}\n"
        f"val: {val_img}\n"
        "nc: 4\n"
        "names:\n  - car\n  - truck\n  - bus\n  - van\n"
    )
    print(f"total={n_total} hit={n_hit} ({n_hit/max(n_total,1)*100:.1f}%) "
          f"extra_links={n_extra} farm_images={n_total + n_extra}")
    print(f"yaml: {yaml_path}")


if __name__ == "__main__":
    main()
