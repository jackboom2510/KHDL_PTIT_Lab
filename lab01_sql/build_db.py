#!/usr/bin/env python3
"""Dựng CSDL SQLite của LAB 01 từ `sql/schema.sql` + `sql/seed.sql`.

Máy Cloud Shell có sẵn sqlite3 CLI, nhưng nhiều môi trường khác thì không; script này chỉ dùng
thư viện chuẩn nên chạy được ở mọi nơi.

    python3 build_db.py              # dừng nếu data/sales.db đã tồn tại
    python3 build_db.py --force      # xoá và dựng lại (mất dữ liệu mở rộng đã sinh)
    python3 build_db.py --out data/sales_extended.db --force
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SQL_DIR = BASE / "sql"
DEFAULT_DB = BASE / "data" / "sales.db"
EXPECTED = {"customers": 5, "products": 5, "orders": 6, "order_items": 8}


def build(out: Path, force: bool) -> int:
    if out.exists():
        if not force:
            print(f"[skip] {out} đã tồn tại. Dùng --force để dựng lại.")
            return 0
        out.unlink()
    out.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(out)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        for name in ("schema.sql", "seed.sql"):
            script = (SQL_DIR / name).read_text(encoding="utf-8")
            con.executescript(script)
        con.commit()

        ok = True
        print(f"Đã tạo {out}")
        for table, expected in EXPECTED.items():
            actual = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            flag = "ok" if actual == expected else f"LỆCH (kỳ vọng {expected})"
            if actual != expected:
                ok = False
            print(f"  {table:<12} {actual:>5}  {flag}")
    finally:
        con.close()
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Dựng sales.db cho LAB 01")
    parser.add_argument("--out", type=Path, default=DEFAULT_DB, help="đường dẫn file CSDL")
    parser.add_argument("--force", action="store_true", help="xoá file cũ trước khi dựng")
    args = parser.parse_args()

    out = args.out if args.out.is_absolute() else (BASE / args.out)
    return build(out, args.force)


if __name__ == "__main__":
    sys.exit(main())
