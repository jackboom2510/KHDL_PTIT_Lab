#!/usr/bin/env python3
"""Chuẩn hoá ảnh chụp minh chứng LAB 02 trước khi đưa vào báo cáo.

Script **không** tạo ra nội dung ảnh: nó chỉ nhận các ảnh chụp màn hình thật (Cloud Shell,
Atlas) do người làm chụp, rồi:

1. cắt khoảng trống thừa ở mép (nền terminal/Atlas là một màu phẳng),
2. ghép nhiều lần chụp liên tiếp của cùng một mục thành một hình (nền nối liền nhau),
3. lưu ra đúng tên tệp mà `report/report_values.py` đang dùng.

    python3 prepare_evidence.py --src ~/Pictures/lab02 --dry-run
    python3 prepare_evidence.py --src ~/Pictures/lab02

`--src` chứa ảnh chụp gốc; có thể truyền `--map` để đổi quy ước tên tệp gốc → tên đích.
Mặc định tự nhận theo thứ tự chụp (00:phút) nếu tên tệp không khớp bảng MAP.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:                       # pragma: no cover - thông báo thân thiện
    raise SystemExit("Cần Pillow: pip install pillow")

HERE = Path(__file__).resolve().parent
PAD = 8                                     # viền nối giữa các ảnh ghép (px)
BG = (34, 34, 34)                           # nền terminal mặc định khi ghép

# (tệp đích, [ảnh nguồn theo đúng thứ tự ghép trên xuống]) — sửa tên nguồn cho khớp
# với ảnh chụp của bạn rồi chạy lại.
MAP: dict[str, list[str]] = {
    "01_cluster.png": ["Screenshot 2026-11-12 171517.png"],
    "02_data_explorer.png": ["Screenshot 2026-11-12 171547.png"],
    "03_connect_seed.png": ["Screenshot 2026-11-12 170707.png",
                            "Screenshot 2026-11-12 170817.png"],
    "04_crud_n01_n05.png": ["Screenshot 2026-11-12 170939.png",
                            "Screenshot 2026-11-12 170949.png"],
    "05_crud_n05_n11.png": ["Screenshot 2026-11-12 171023.png"],
    "06_aggregation_n10.png": ["Screenshot 2026-11-12 171608.png"],
    "07_lookup_n12.png": ["Screenshot 2026-11-12 171652.png"],
    "08_n13_n14_index.png": ["Screenshot 2026-11-12 171031.png"],
    "09_n15_n20_mo_hinh.png": ["Screenshot 2026-11-12 171040.png",
                               "Screenshot 2026-11-12 172228.png"],
    "10_explain_n21.png": ["Screenshot 2026-11-12 172235.png"],
    "11_expanded_counts.png": ["Screenshot 2026-11-12 172615.png"],
    "12_n16_n19.png": ["Screenshot 2026-11-12 172155.png",
                       "Screenshot 2026-11-12 172219.png"],
    "13_n22_lookup.png": ["Screenshot 2026-11-12 172315.png",
                          "Screenshot 2026-11-12 172325.png"],
}


def trim(img: Image.Image, tolerance: int = 18, keep: int = 4) -> Image.Image:
    """Cắt mép trên/dưới/trái/phải chỉ gồm một màu nền phẳng (giữ lại `keep` px)."""
    img = img.convert("RGB")
    w, h = img.size
    px = img.load()
    bg = px[2, 2]

    def row_empty(y: int) -> bool:
        return all(abs(px[x, y][i] - bg[i]) <= tolerance for x in range(0, w, 3) for i in (0, 1, 2))

    def col_empty(x: int) -> bool:
        return all(abs(px[x, y][i] - bg[i]) <= tolerance for y in range(0, h, 3) for i in (0, 1, 2))

    top, bottom, left, right = 0, h - 1, 0, w - 1
    while top < bottom and row_empty(top):
        top += 1
    while bottom > top and row_empty(bottom):
        bottom -= 1
    while left < right and col_empty(left):
        left += 1
    while right > left and col_empty(right):
        right -= 1
    return img.crop((max(left - keep, 0), max(top - keep, 0),
                     min(right + keep + 1, w), min(bottom + keep + 1, h)))


def stack(parts: list[Image.Image]) -> Image.Image:
    """Ghép các ảnh theo chiều dọc, canh trái, nền liền mạch."""
    width = max(p.width for p in parts)
    height = sum(p.height for p in parts) + PAD * (len(parts) - 1)
    out = Image.new("RGB", (width, height), BG)
    y = 0
    for part in parts:
        out.paste(part, (0, y))
        y += part.height + PAD
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Cắt/ghép ảnh minh chứng LAB 02")
    ap.add_argument("--src", type=Path, required=True, help="thư mục chứa ảnh chụp gốc")
    ap.add_argument("--out", type=Path, default=HERE, help="thư mục ghi ảnh đích (mặc định: đây)")
    ap.add_argument("--dry-run", action="store_true", help="chỉ kiểm tra tệp nguồn, không ghi")
    args = ap.parse_args()

    missing = [src for srcs in MAP.values() for src in srcs
               if not (args.src / src).exists()]
    if missing:
        print("[!] thiếu ảnh nguồn:", file=sys.stderr)
        for name in missing:
            print(f"    {name}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"[i] đủ {sum(len(v) for v in MAP.values())} ảnh nguồn cho {len(MAP)} ảnh đích")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    for name, sources in MAP.items():
        parts = [trim(Image.open(args.src / src)) for src in sources]
        img = parts[0] if len(parts) == 1 else stack(parts)
        img.save(args.out / name, optimize=True)
        print(f"[ok] {name:26s} {img.width}x{img.height}  "
              f"({len(sources)} ảnh nguồn, {(args.out / name).stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
