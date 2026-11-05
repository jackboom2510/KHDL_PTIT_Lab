#!/usr/bin/env python3
"""Tiện ích chạy lệnh / truy vấn và cắt đoạn output cho pipeline ảnh minh chứng.

Không phụ thuộc thư viện ngoài. Mọi lệnh đều chạy với cwd = thư mục `lab01_sql`, nên
đường dẫn tương đối (`sql/answers.sql`, `data/sales.db`) dùng được như khi gõ tay.

Nguyên tắc: ảnh minh chứng phải phản ánh **output thật của lệnh thật**, không viết lại
bằng tay. Vì vậy mọi scene đều đi qua `run()` / `sql()` ở đây.
"""

from __future__ import annotations

import os
import shlex
import sqlite3
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent      # lab01_sql/
SQL_DIR = LAB_DIR / "sql"
PROMPT = "$ "


def run(cmd: list[str] | str, *, timeout: int = 300, python: str | None = None) -> str:
    """Chạy lệnh, trả về chuỗi giống terminal: dòng lệnh có tiền tố `$ ` rồi output."""
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    cmd = list(cmd)
    shown = list(cmd)                      # lệnh hiển thị trong ảnh (người dùng gõ python3)
    if python and cmd and cmd[0] == "python3":
        cmd[0] = python                    # interpreter thực thi (có thể là venv)

    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    try:
        proc = subprocess.run(
            cmd, cwd=LAB_DIR, env=env, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return f"{PROMPT}{' '.join(shown)}\n[timeout sau {timeout}s]"

    out = (proc.stdout or "") + (proc.stderr or "")
    # Đường dẫn tuyệt đối dài làm ảnh khó đọc: hiển thị tương đối so với lab01_sql/
    out = out.replace(str(LAB_DIR) + "/", "").replace(str(LAB_DIR), ".")
    header = f"{PROMPT}{' '.join(shown)}"
    if proc.returncode != 0:
        header += f"    (exit {proc.returncode})"
    return f"{header}\n{out.rstrip()}\n"


SQL_TMP = LAB_DIR / "data" / ".evidence"


def sql(db: Path | str, statement: str, python: str | None = None, name: str = "query") -> str:
    """Chạy một câu SQL qua run_sql.py.

    Câu lệnh được ghi ra `data/.evidence/<name>.sql` và hiển thị bằng đường dẫn ngắn, để
    ảnh minh chứng không bị ngập bởi một dòng lệnh dài hàng trăm ký tự.
    """
    SQL_TMP.mkdir(parents=True, exist_ok=True)
    stmt_path = SQL_TMP / f"{name}.sql"
    stmt_path.write_text(statement.strip() + "\n", encoding="utf-8")
    return run(
        ["python3", "run_sql.py", str(stmt_path.relative_to(LAB_DIR)), "--db", str(db)],
        python=python,
    )


def tables_count(db: Path | str, python: str | None = None) -> str:
    """Đếm số dòng 4 bảng + kiểm tra khoá ngoại trong một lần chạy."""
    stmt = (
        "SELECT 'customers' AS bang, COUNT(*) AS so_dong FROM customers "
        "UNION ALL SELECT 'products', COUNT(*) FROM products "
        "UNION ALL SELECT 'orders', COUNT(*) FROM orders "
        "UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;"
    )
    out = sql(db, stmt, python=python, name="count_tables")
    con = sqlite3.connect(Path(db) if Path(db).is_absolute() else LAB_DIR / db)
    try:
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        con.close()
    status = "ok (không có dòng vi phạm)" if not fk else f"{len(fk)} dòng vi phạm"
    return f"{out}{PROMPT}PRAGMA foreign_key_check;   -> {status}\n"


def slice_block(text: str, start: str, end: str | None = None) -> str:
    """Cắt đoạn output bắt đầu từ dòng chứa `start` đến trước dòng chứa `end`."""
    lines = text.splitlines()
    begin = next((i for i, ln in enumerate(lines) if start in ln), None)
    if begin is None:
        return f"[không tìm thấy đoạn '{start}']\n"
    stop = len(lines)
    if end:
        found = next((i for i in range(begin + 1, len(lines)) if end in lines[i]), None)
        if found is not None:
            stop = found
    return "\n".join(lines[begin:stop]).rstrip() + "\n"


def which_python() -> str:
    """Python đang chạy (để scene dùng đúng interpreter có thư viện cần thiết)."""
    return sys.executable
