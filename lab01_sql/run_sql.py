#!/usr/bin/env python3
"""Chạy một file .sql (nhiều câu lệnh) và in kết quả từng câu.

Dùng khi máy không có sqlite3 CLI (ví dụ sandbox CI), hoặc khi muốn output có nhãn rõ ràng để
copy vào báo cáo. Tương đương `sqlite3 data/sales.db < sql/answers.sql`.

    python3 run_sql.py sql/answers.sql                    # chạy trên data/sales.db
    python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db
    python3 run_sql.py --sql "SELECT COUNT(*) FROM customers;"
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DEFAULT_DB = BASE / "data" / "sales.db"
MAX_ROWS = 50


def split_statements(text: str) -> list[str]:
    stmts, buffer = [], ""
    for line in text.splitlines(keepends=True):
        buffer += line
        if line.lstrip().startswith("--"):
            continue
        if sqlite3.complete_statement(buffer):
            stmts.append(buffer)
            buffer = ""
    if buffer.strip() and not all(
        ln.strip() == "" or ln.strip().startswith("--") for ln in buffer.splitlines()
    ):
        stmts.append(buffer)
    return stmts


def run(db_path: Path, statements: list[str], max_rows: int) -> int:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    errors = 0
    try:
        for idx, stmt in enumerate(statements, start=1):
            code = stmt.strip()
            if not code:
                continue
            label = next(
                (ln.split("--", 1)[1].strip() for ln in stmt.splitlines() if ln.strip().startswith("--")),
                code.splitlines()[0][:70],
            )
            print(f"\n--- [{idx}] {label} ---")
            try:
                cur = con.execute(stmt)
                if cur.description:
                    print([d[0] for d in cur.description])
                    rows = cur.fetchall()
                    for row in rows[:max_rows]:
                        print(row)
                    if len(rows) > max_rows:
                        print(f"... ({len(rows) - max_rows} dòng nữa, tổng {len(rows)})")
                    else:
                        print(f"({len(rows)} rows)")
                else:
                    con.commit()
                    print("Rows affected:", cur.rowcount)
            except sqlite3.Error as exc:
                errors += 1
                print("SQL error:", exc)
    finally:
        con.close()
    print(f"\n{len(statements)} câu lệnh, {errors} lỗi trên {db_path}")
    return 0 if errors == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Chạy file .sql bằng Python sqlite3")
    parser.add_argument("file", nargs="?", type=Path, help="file .sql cần chạy")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="file CSDL (mặc định data/sales.db)")
    parser.add_argument("--sql", help="câu lệnh SQL truyền trực tiếp thay vì file")
    parser.add_argument("--max-rows", type=int, default=MAX_ROWS)
    args = parser.parse_args()

    db_path = args.db if args.db.is_absolute() else (BASE / args.db)
    if not db_path.exists() and args.db == DEFAULT_DB:
        # Bài nộp có thể đặt sales.db ngay cạnh script thay vì trong data/
        for alt in (BASE / "sales.db", BASE / "data" / "sales.db"):
            if alt.exists():
                db_path = alt
                break
    if not db_path.exists():
        print(f"Không thấy {db_path}. Chạy: python3 build_db.py")
        return 1

    if args.sql:
        text = args.sql
    elif args.file:
        path = args.file if args.file.is_absolute() else (BASE / args.file)
        text = path.read_text(encoding="utf-8")
    else:
        parser.error("cần một file .sql hoặc --sql")

    return run(db_path, split_statements(text), args.max_rows)


if __name__ == "__main__":
    sys.exit(main())
