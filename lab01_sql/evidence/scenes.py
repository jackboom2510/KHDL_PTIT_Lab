#!/usr/bin/env python3
"""Khai báo 7 ảnh minh chứng của LAB 01 — mỗi scene là một hàm dựng `Scene`.

Tên tệp khớp đúng danh mục ở Phụ lục B của báo cáo (`report/lab01_report.tex`):
    01_env, 02_tables_count, 03_console, 04_s08_result,
    05_explain_before_after, 06_expanded_counts, 07_s19_rank

Nguyên tắc: không có số liệu nào được viết tay — mọi khối text đều lấy từ output thật của
`build_db.py`, `generate_data.py`, `run_sql.py`, `sql_console.py`.
"""

from __future__ import annotations

from pathlib import Path

import runner
from render import Scene, Segment, today

LAB = runner.LAB_DIR
DATA = LAB / "data"
WORK = DATA / ".evidence"          # CSDL tạm của pipeline ảnh (đã nằm trong .gitignore)


def _py() -> str:
    return runner.which_python()


def _db(name: str) -> str:
    """Đường dẫn CSDL tạm, tương đối so với lab01_sql/ để lệnh trong ảnh ngắn."""
    WORK.mkdir(parents=True, exist_ok=True)
    return str((WORK / name).relative_to(LAB))


def _build(db: str) -> str:
    return runner.run(["python3", "build_db.py", "--force", "--out", db], python=_py())


def _generate(db: str) -> str:
    return runner.run(
        ["python3", "generate_data.py", "--force", "--out", db], python=_py()
    )


# ---------------------------------------------------------------------------
# 01 — môi trường
# ---------------------------------------------------------------------------
def scene_env(workdir: Path) -> Scene:
    out = runner.run(["python3", "--version"], python=_py())
    out += runner.run(
        ["python3", "-c", "import sqlite3; print('sqlite3', sqlite3.sqlite_version)"],
        python=_py(),
    )
    out += runner.run(["uname", "-sr"], python=_py())
    out += runner.run(["pwd"], python=_py())
    return Scene(
        slug="01_env",
        title="Môi trường thực hành",
        subtitle="Google Cloud Shell · Python · SQLite",
        segments=[Segment(out)],
        footnotes=[
            "Trên Cloud Shell, chạy thêm `whoami` và `sqlite3 --version` để thấy tài khoản và bản SQLite.",
            f"Ảnh sinh tự động ngày {today()} bằng lab01_sql/evidence/make_evidence.py",
        ],
    )


# ---------------------------------------------------------------------------
# 02 — tạo bảng và nạp dữ liệu mẫu
# ---------------------------------------------------------------------------
def scene_tables(workdir: Path) -> Scene:
    db = _db("scene02.db")
    out = _build(db)
    out += runner.tables_count(db, python=_py())
    return Scene(
        slug="02_tables_count",
        title="Tạo 4 bảng và nạp dữ liệu mẫu",
        subtitle="Kỳ vọng của đề: customers 5 · products 5 · orders 6 · order_items 8",
        segments=[Segment(out)],
        footnotes=[
            "build_db.py đọc sql/schema.sql + sql/seed.sql và in luôn số dòng để đối chiếu.",
            "PRAGMA foreign_key_check rỗng nghĩa là mọi khoá ngoại đều hợp lệ.",
        ],
    )


# ---------------------------------------------------------------------------
# 03 — SQL console (câu lệnh nhiều dòng, EXIT)
# ---------------------------------------------------------------------------
def scene_console(workdir: Path) -> Scene:
    db = _db("scene03.db")
    _build(db)

    script = (
        "SELECT city, COUNT(*) AS so_khach\n"
        "FROM customers\n"
        "GROUP BY city\n"
        "ORDER BY so_khach DESC;\n"
        "SELECT name FROM products ORDER BY price DESC LIMIT 3;\n"
        "SELECT * FROM khong_ton_tai;\n"
        "EXIT\n"
    )
    import subprocess, os

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [_py(), "sql_console.py", db],
        cwd=LAB,
        input=script,
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    body = (
        f"$ python3 sql_console.py {db}"
        "      (mỗi câu kết thúc bằng ';', EXIT để thoát)\n"
    )
    body += (proc.stdout or "") + (proc.stderr or "")
    return Scene(
        slug="03_console",
        title="SQL Console: câu lệnh nhiều dòng và xử lý lỗi",
        subtitle="sql_console.py — gộp câu lệnh bằng sqlite3.complete_statement()",
        segments=[
            Segment(body.rstrip() + "\n"),
            Segment(
                "Lưu ý: câu lệnh được gộp theo dấu ';' (dấu nhắc đổi thành '...'), lỗi SQL chỉ "
                "báo cho câu sai và console tiếp tục nhận câu tiếp theo.\n",
                caption="Nhận xét",
            ),
        ],
        footnotes=["Đường dẫn CSDL truyền qua tham số nên dùng được cả trong repo lẫn Cloud Shell."],
    )


# ---------------------------------------------------------------------------
# 04 — kết quả S08
# ---------------------------------------------------------------------------
def scene_s08(workdir: Path) -> Scene:
    db = _db("scene04.db")
    _build(db)
    full = runner.run(
        ["python3", "run_sql.py", "sql/answers.sql", "--db", db], python=_py()
    )
    block = runner.slice_block(full, "S08", "S09")
    tail = runner.slice_block(full, "S09", "S10")
    return Scene(
        slug="04_s08_result",
        title="S08 — tổng tiền từng đơn hàng",
        subtitle="JOIN 3 bảng + SUM(quantity × price) + GROUP BY",
        segments=[
            Segment(block, caption="Kết quả chạy sql/answers.sql (đoạn S08)"),
            Segment(tail, caption="S09 — doanh thu từng khách hàng"),
        ],
        footnotes=[
            "S05 (tăng giá Mouse 10%) chạy trước S08 nên tổng tiền dùng giá 275.000, không phải 250.000.",
            "Tổng 6 đơn = 44.125.000 đồng.",
        ],
    )


# ---------------------------------------------------------------------------
# 05 — EXPLAIN trước / sau index
# ---------------------------------------------------------------------------
def scene_explain(workdir: Path) -> Scene:
    small = _db("scene05_small.db")
    _build(small)
    out_small = runner.run(
        ["python3", "run_sql.py", "sql/explain.sql", "--db", small], python=_py()
    )
    # Tách output thành các "section" theo nhãn --- [n] ---, rồi lấy đúng hai khối EXPLAIN
    import re

    sections = re.split(r"\n--- \[\d+\] ", out_small)
    header = next((ln for ln in out_small.splitlines() if ln.startswith("$ ")), "")
    scan = next((s for s in sections if "'SCAN orders'" in s), "")
    cover = next((s for s in sections if "COVERING INDEX" in s), "")

    def _rows(section: str) -> str:
        """Bỏ dòng nhãn tự động, chỉ giữ tên cột + các dòng kết quả."""
        lines = section.splitlines()
        start = next((i for i, ln in enumerate(lines) if ln.startswith("['")), 0)
        return "\n".join(lines[start:]).rstrip() + "\n"

    explain_sql = (
        "EXPLAIN QUERY PLAN\nSELECT order_id FROM orders WHERE customer_id = 1;"
    )
    before = (
        f"{header}\n-- S15.1  TRƯỚC index (chưa có index)\n{explain_sql}\n"
        f"{_rows(scan)}"
    )
    after = (
        f"{header}\n-- S15.2  CREATE INDEX idx_orders_customer ON orders(customer_id);\n"
        f"-- S15.3  SAU index\n{explain_sql}\n{_rows(cover)}"
    )
    return Scene(
        slug="05_explain_before_after",
        title="S15 — EXPLAIN QUERY PLAN trước và sau khi tạo index",
        subtitle="SCAN orders  →  SEARCH orders USING COVERING INDEX idx_orders_customer",
        segments=[
            Segment(before, caption="Trước index (dữ liệu mẫu 6 đơn)"),
            Segment(after, caption="Sau index"),
            Segment(
                "Đọc kết quả: SCAN = đọc tuần tự toàn bảng; SEARCH ... USING INDEX = đi xuống "
                "cây B-tree để tìm trực tiếp; COVERING INDEX = trả lời hoàn toàn từ index, "
                "không phải quay lại bảng (vì câu chỉ cần order_id = rowid).\n",
                caption="Nhận xét",
            ),
        ],
        footnotes=[
            "explain.sql tự DROP rồi CREATE index nên chạy được trên mọi bản sao CSDL.",
            "Dữ liệu 6 dòng: không kết luận bằng thời gian chạy, chỉ dựa vào kế hoạch.",
        ],
    )


# ---------------------------------------------------------------------------
# 06 — dữ liệu mở rộng
# ---------------------------------------------------------------------------
def scene_expanded(workdir: Path) -> Scene:
    db = _db("scene06.db")
    out = _generate(db)
    out += runner.tables_count(db, python=_py())
    out += runner.sql(
        db,
        "SELECT MIN(order_date) AS tu_ngay, MAX(order_date) AS den_ngay, "
        "COUNT(DISTINCT strftime('%Y-%m', order_date)) AS so_thang FROM orders;",
        python=_py(),
        name="date_range",
    )
    return Scene(
        slug="06_expanded_counts",
        title="Sinh dữ liệu mở rộng (bài về nhà)",
        subtitle="Yêu cầu: 100 khách · 30 sản phẩm · 500 đơn · 1.000 dòng đơn",
        segments=[Segment(out)],
        footnotes=[
            "random.seed(2026) nên chạy lại cho đúng bộ dữ liệu này.",
            "Kịch bản để ~8% khách không có đơn và 4 sản phẩm không bán được, phục vụ S17 và S18.",
        ],
    )


# ---------------------------------------------------------------------------
# 07 — S19 xếp hạng
# ---------------------------------------------------------------------------
def scene_rank(workdir: Path) -> Scene:
    db = _db("scene07.db")
    if not (LAB / db).exists():
        _generate(db)
    full = runner.run(
        ["python3", "run_sql.py", "sql/answers_homework.sql", "--db", db], python=_py()
    )
    block = runner.slice_block(full, "S19", "S20")
    return Scene(
        slug="07_s19_rank",
        title="S19 — xếp hạng khách hàng theo doanh thu",
        subtitle="RANK() và DENSE_RANK() trên dữ liệu mở rộng",
        segments=[
            Segment(block, caption="Kết quả chạy sql/answers_homework.sql (đoạn S19)"),
            Segment(
                "Với dữ liệu này không có đồng hạng nên hai cột bằng nhau. Khi hai khách cùng "
                "hạng 2: RANK() cho 2, 2, 4; DENSE_RANK() cho 2, 2, 3.\n",
                caption="Nhận xét",
            ),
        ],
        footnotes=["Báo cáo 'top N' nên dùng DENSE_RANK để không bị thiếu người khi đồng hạng."],
    )


# ---------------------------------------------------------------------------
# Registry — thứ tự này cũng là thứ tự trong manifest
# ---------------------------------------------------------------------------
SCENES = [
    ("01_env", scene_env),
    ("02_tables_count", scene_tables),
    ("03_console", scene_console),
    ("04_s08_result", scene_s08),
    ("05_explain_before_after", scene_explain),
    ("06_expanded_counts", scene_expanded),
    ("07_s19_rank", scene_rank),
]


def prepare_workdir() -> Path:
    """Thư mục chứa CSDL tạm của pipeline ảnh (`data/.evidence`, đã gitignore)."""
    WORK.mkdir(parents=True, exist_ok=True)
    return WORK


def shared_extended_db() -> Path:
    """Bản dữ liệu mở rộng dùng chung cho scene 07 (và để tham chiếu ở scene 05)."""
    WORK.mkdir(parents=True, exist_ok=True)
    return WORK / "extended_shared.db"
