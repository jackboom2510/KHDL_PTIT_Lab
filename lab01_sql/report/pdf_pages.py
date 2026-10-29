#!/usr/bin/env python3
"""Đếm số trang của file PDF và cảnh báo nếu vượt giới hạn 2–3 trang của đề bài.

    python3 pdf_pages.py lab01_report_short.pdf            # giới hạn mặc định 1..3
    python3 pdf_pages.py lab01_report_short.pdf --max 3 --min 2
    python3 pdf_pages.py lab01_report.pdf --no-limit        # chỉ in số trang

Ưu tiên `pdfinfo` (poppler-utils) nếu có, nếu không thì đọc trực tiếp cấu trúc PDF
(đếm object /Type /Page, không tính /Pages). Chạy sau khi compile để biết ngay báo cáo
có vừa 3 trang hay không, thay vì mở trình đọc PDF kiểm tra thủ công.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path


def pages_via_pdfinfo(pdf: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    try:
        out = subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, OSError):
        return None
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    return int(m.group(1)) if m else None


def pages_via_regex(pdf: Path) -> int | None:
    data = pdf.read_bytes()
    counts: list[int] = []

    # 1) /Count của cây /Pages thường phản ánh tổng số trang
    for m in re.finditer(rb"/Type\s*/Pages\b[^>]{0,400}?/Count\s+(\d+)", data, re.S):
        counts.append(int(m.group(1)))

    # 2) đếm object trang (không tính /Pages)
    n_page = len(re.findall(rb"/Type\s*/Page[^s]", data))

    # 3) nội dung nén: giải nén các stream rồi tìm lại
    if n_page == 0:
        for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
            try:
                blob = zlib.decompress(m.group(1))
            except zlib.error:
                continue
            n_page += len(re.findall(rb"/Type\s*/Page[^s]", blob))

    candidates = [c for c in counts + [n_page] if c > 0]
    return max(candidates) if candidates else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Đếm số trang PDF")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--min", type=int, default=1)
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--no-limit", action="store_true", help="không kiểm tra giới hạn")
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"[!] Không thấy {args.pdf}")
        return 2

    n = pages_via_pdfinfo(args.pdf)
    method = "pdfinfo"
    if n is None:
        n = pages_via_regex(args.pdf)
        method = "đọc cấu trúc PDF"
    if n is None:
        print(f"[?] Không đếm được số trang của {args.pdf.name}")
        return 2

    print(f"[i] {args.pdf.name}: {n} trang (đếm bằng {method})")
    if args.no_limit:
        return 0
    if n < args.min:
        print(f"[!] Ít hơn {args.min} trang — đề yêu cầu {args.min}–{args.max} trang.")
        return 1
    if n > args.max:
        print(f"[!] VƯỢT {args.max} trang — cần rút gọn. Xem 'Co giãn độ dài' "
              f"trong report/README.md (bỏ mục Lệnh tái lập, giảm \\footnotesize, "
              f"bớt Bảng {args.max}).")
        return 1
    print(f"[ok] Nằm trong giới hạn {args.min}–{args.max} trang.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
