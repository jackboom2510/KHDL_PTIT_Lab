#!/usr/bin/env python3
"""SQL Console — LAB 01 (Introduction to Data Science, PTIT).

Console SQLite tương tác đúng theo đề PDF mục 4:
- Mỗi câu lệnh kết thúc bằng dấu `;` (có thể nhập nhiều dòng, dấu nhắc đổi thành `...`).
- `EXIT` (hoặc Ctrl+D / Ctrl+C) để thoát.
- Có kết quả SELECT thì in tên cột + các dòng; ngược lại in `Rows affected`.
- Bật khoá ngoại bằng `PRAGMA foreign_keys = ON`.

Khác biệt so với bản trong PDF: file CSDL mặc định là `data/sales.db` (tương đối theo vị trí
file này) và có thể truyền đường dẫn khác ở tham số đầu tiên, để chạy được cả trong repo lẫn
Cloud Shell:

    python3 sql_console.py                      # mở data/sales.db
    python3 sql_console.py data/sales_extended.db
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows

BASE = Path(__file__).resolve().parent
DEFAULT_DB = BASE / "data" / "sales.db"


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        db_path = Path(argv[1])
    elif DEFAULT_DB.exists() or not (BASE / "sales.db").exists():
        db_path = DEFAULT_DB
    else:
        db_path = BASE / "sales.db"        # bài nộp đặt CSDL ngay cạnh script
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")

    print(f"SQL Console — {db_path}")
    print("End each statement with ;  (EXIT to quit)")
    buffer = ""

    while True:
        try:
            line = input("SQL> " if not buffer else "... ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip().upper() == "EXIT":
            break

        buffer += line + "\n"
        if not sqlite3.complete_statement(buffer):
            continue

        try:
            cur = con.execute(buffer)
            if cur.description:
                print([x[0] for x in cur.description])
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                print(f"({len(rows)} rows)")
            else:
                con.commit()
                print("Rows affected:", cur.rowcount)
        except sqlite3.Error as exc:
            print("SQL error:", exc)
        buffer = ""

    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
