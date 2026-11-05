#!/usr/bin/env python3
"""Sinh báo cáo bài thực hành LAB 01 — bản ngắn 4–5 trang, bám 5 tiêu chí chấm điểm.

Đặc điểm trình bày (theo yêu cầu):
    - chỉ dùng chữ đen trên nền trắng, không màu nhấn, không icon, không khung tô nền;
    - bố cục một cột, cỡ chữ 11, giãn dòng thoáng, tiêu đề mục in đậm;
    - nội dung chia theo đúng 5 tiêu chí của mục 10 trong đề bài + danh mục ảnh minh chứng.

    pip install -r requirements.txt          # fpdf2 + pillow
    python3 make_report.py                    # bản 4–5 trang, không chèn ảnh
    python3 make_report.py --images evidence
                                              # chèn ảnh minh chứng thật đã chụp
    python3 make_report.py --out /tmp/x.pdf

Ảnh minh chứng do người làm tự chụp trên Google Cloud Shell theo
`../evidence/HUONG_DAN_CHUP_ANH.md`; tên tệp phải khớp bảng ở mục 7 của báo cáo.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
SQL_DIR = LAB / "sql"

# ----------------------------------------------------------------- thông tin người làm
AUTHOR = "Nguyễn Danh Thái"
STUDENT_ID = "B23DCKH105"

# ----------------------------------------------------------------- khổ chữ (đen trắng)
BODY = 11.0
LH = 5.4
INDENT = 7.0
INK = (0, 0, 0)          # chỉ dùng màu đen
GRAY = (90, 90, 90)      # xám trung tính cho chú thích ảnh, không phải màu nhấn


FIGURES = [
    "01_env.png", "02_tables_count.png", "03_console.png",
    "04_s08_result_01.png", "04_s08_result_02.png",
    "05_explain_before_after_01.png", "05_explain_before_after_02.png",
    "06_expanded_counts.png", "07_s19_rank_01.png",
    "07_s19_rank_02.png", "07_s19_rank_03.png",
]


def ascii_only(text: str) -> str:
    """Bỏ dấu tiếng Việt cho khối mã (font mono thiếu một số glyph dựng sẵn)."""
    text = text.replace("đ", "d").replace("Đ", "D")
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if not unicodedata.combining(c))


class Report(FPDF):
    def __init__(self, image_dir: Path | None = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.image_dir = image_dir
        self.fig_no = 0
        self.tab_no = 0
        self.fig_scale = 1.0     # tự thu nhỏ ảnh nếu báo cáo vượt 5 trang
        self.set_margins(left=25, top=20, right=20)
        self.set_auto_page_break(auto=True, margin=18)
        self.alias_nb_pages()   # cho phép dùng {nb} trong footer

        self.add_font("Serif", "", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
        self.add_font("Serif", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
        self.add_font("Mono", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
        self.set_title("Báo cáo bài thực hành LAB 01 - SQL với SQLite")
        self.set_author(f"{AUTHOR} - {STUDENT_ID}")
        self.set_text_color(*INK)

    # -------------------------------------------------------------- trang
    def footer(self) -> None:
        if self.page_no() == 1:
            return
        self.set_y(-13)
        self.set_font("Serif", "", 9)
        self.set_text_color(*GRAY)
        self.cell(0, 5, "Báo cáo LAB 01 — SQL với SQLite", align="L")
        self.set_y(-13)
        self.cell(0, 5, f"{self.page_no()}/{{nb}}", align="R")
        self.set_text_color(*INK)
        self.set_font("Serif", "", BODY)

    def need(self, h: float) -> None:
        if self.get_y() + h > self.h - self.b_margin:
            self.add_page()

    # -------------------------------------------------------------- tiêu đề
    def h1(self, text: str) -> None:
        self.need(18)
        self.ln(2.0)
        self.set_font("Serif", "B", 12.0)
        self.set_text_color(*INK)
        self.multi_cell(0, 6.4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.8)

    def h2(self, text: str) -> None:
        self.need(12)
        self.ln(0.6)
        self.set_font("Serif", "B", 11.0)
        self.multi_cell(0, LH, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.4)

    # -------------------------------------------------------------- văn bản
    def p(self, text: str, indent: bool = True, size: float = BODY, lh: float = LH) -> None:
        self.set_font("Serif", "", size)
        self.set_text_color(*INK)
        x = self.l_margin + (INDENT if indent else 0)
        self.set_x(x)
        self.multi_cell(self.epw - (INDENT if indent else 0), lh, text, align="J",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.9)

    def lead(self, bold: str, text: str) -> None:
        self.need(12)
        self.set_font("Serif", "B", BODY)
        self.set_x(self.l_margin + INDENT)
        self.write(LH, bold + " ")
        self.set_font("Serif", "", BODY)
        self.write(LH, text)
        self.ln(LH + 0.9)

    def items(self, rows: list[str]) -> None:
        """Danh sách gạch đầu dòng bằng dấu gạch ngang (không dùng biểu tượng)."""
        self.set_font("Serif", "", BODY)
        for row in rows:
            self.need(LH * 2)
            x0 = self.l_margin + INDENT
            self.set_x(x0)
            self.cell(4, LH, "-")
            self.set_x(x0 + 4)
            self.multi_cell(self.epw - INDENT - 4, LH, row, align="J",
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(0.5)

    # -------------------------------------------------------------- khối mã
    def code(self, text: str, size: float = 8.2) -> None:
        self.set_font("Mono", "", size)
        char_w = self.get_string_width("M") or 1.6
        max_chars = max(40, int(self.epw / char_w))
        lines: list[str] = []
        for raw in ascii_only(text).rstrip("\n").splitlines():
            if not raw:
                lines.append("")
                continue
            while len(raw) > max_chars:
                cut = raw.rfind(" ", 0, max_chars)
                cut = cut if cut > max_chars // 2 else max_chars
                lines.append(raw[:cut])
                raw = "    " + raw[cut:].lstrip()
            lines.append(raw)

        lh = size * 0.46
        self.need(lh * min(len(lines), 4) + 3)
        self.set_text_color(*INK)
        for line in lines:
            if self.get_y() + lh > self.h - self.b_margin:
                self.add_page()
            self.set_x(self.l_margin + 4)
            self.cell(self.epw - 4, lh, line)
            self.ln(lh)
        self.ln(1.6)
        self.set_font("Serif", "", BODY)

    # -------------------------------------------------------------- bảng
    def table(self, headers: list[str], rows: list[list[str]], widths: list[float],
              caption: str, size: float = 8.8, aligns: str = "") -> None:
        total = sum(widths)
        if total > self.epw:
            widths = [w * self.epw / total for w in widths]
        row_h = size * 0.55
        self.need(row_h * (min(len(rows), 5) + 2) + 9)

        self.tab_no += 1
        self.set_font("Serif", "", size - 0.4)
        self.multi_cell(0, 4.8, f"Bảng {self.tab_no}. {caption}", align="C",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.8)

        def header() -> None:
            self.set_font("Serif", "B", size)
            self.set_draw_color(0, 0, 0)
            self.set_line_width(0.15)
            for i, head in enumerate(headers):
                al = aligns[i] if i < len(aligns) else "L"
                self.cell(widths[i], row_h + 1.4, head, border="B", align=al)
            self.ln(row_h + 1.4)

        header()
        self.set_font("Serif", "", size)
        for row in rows:
            if self.get_y() + row_h > self.h - self.b_margin:
                self.add_page()
                header()
                self.set_font("Serif", "", size)
            for i, cell in enumerate(row):
                al = aligns[i] if i < len(aligns) else "L"
                self.cell(widths[i], row_h, cell, align=al)
            self.ln(row_h)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.15)
        y = self.get_y()
        self.line(self.l_margin, y, self.l_margin + sum(widths), y)
        self.ln(2.8)
        self.set_font("Serif", "", BODY)

    # -------------------------------------------------------------- hình
    def _fit(self, filename: str, max_w: float, max_h: float):
        """Kích thước ảnh vừa khung, trả về (đường dẫn, rộng, cao) hoặc None."""
        path = (self.image_dir / filename) if self.image_dir else None
        if path is None or not path.exists():
            return None
        from PIL import Image

        with Image.open(path) as im:
            iw, ih = im.size
        max_h = max_h * self.fig_scale
        w = min(max_w, self.epw)
        h = w * ih / iw
        if h > max_h:
            h = max_h
            w = h * iw / ih
        return path, w, h

    def _draw(self, path, x: float, y: float, w: float, h: float) -> None:
        self.image(str(path), x=x, y=y, w=w, h=h)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.15)
        self.rect(x, y, w, h)

    def _caption(self, label: str, width: float, x: float, y: float) -> None:
        self.set_xy(x, y + 1.2)
        self.set_font("Serif", "", 8.8)
        self.set_text_color(*GRAY)
        self.multi_cell(width, 4.4, label, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*INK)

    def figure(self, filename: str, caption: str, max_h: float = 52.0,
               max_w: float = 118.0) -> None:
        """Chèn một ảnh minh chứng (nếu người làm đã cung cấp thư mục ảnh)."""
        fitted = self._fit(filename, max_w, max_h)
        if fitted is None:
            return
        path, w, h = fitted
        self.need(h + 8)
        y = self.get_y()
        x = self.l_margin + (self.epw - w) / 2
        self._draw(path, x, y, w, h)
        self.fig_no += 1
        self._caption(f"Hình {self.fig_no}. {caption}", self.epw, self.l_margin, y + h)
        self.ln(2.4)
        self.set_font("Serif", "", BODY)

    def figure_pair(self, left: tuple[str, str], right: tuple[str, str],
                    max_h: float = 46.0) -> None:
        """Đặt hai ảnh cạnh nhau để báo cáo gọn trong 4–5 trang."""
        gap = 6.0
        cell_w = (self.epw - gap) / 2
        fitted = [(self._fit(f, cell_w, max_h), c) for f, c in (left, right)]
        if all(f is None for f, _ in fitted):
            return
        h_max = max((f[2] for f, _ in fitted if f), default=0)
        self.need(h_max + 12)
        y = self.get_y()
        numbers = []
        for i, (fit, caption) in enumerate(fitted):
            x = self.l_margin + i * (cell_w + gap)
            if fit is None:
                numbers.append(None)
                continue
            path, w, h = fit
            self._draw(path, x + (cell_w - w) / 2, y, w, h)
            self.fig_no += 1
            numbers.append(self.fig_no)
        self.set_xy(self.l_margin, y + h_max)
        for i, (fit, caption) in enumerate(fitted):
            x = self.l_margin + i * (cell_w + gap)
            label = f"Hình {numbers[i]}. {caption}" if numbers[i] else caption
            self._caption(label, cell_w, x, y + h_max)
        self.set_text_color(*INK)
        self.set_xy(self.l_margin, y + h_max + 11)
        self.set_font("Serif", "", BODY)


# =============================================================== nội dung báo cáo
def title_block(r: Report) -> None:
    r.add_page()
    r.set_font("Serif", "B", 14)
    r.multi_cell(0, 7.4, "BÁO CÁO BÀI THỰC HÀNH LAB 01", align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.set_font("Serif", "B", 11.5)
    r.multi_cell(0, 6.2, "SQL trên Google Cloud Shell với SQLite", align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.ln(1.6)
    r.set_font("Serif", "", 10)
    for line in (
        "Môn: Introduction to Data Science — Học viện Công nghệ Bưu chính Viễn thông",
        f"Sinh viên: {AUTHOR}    MSSV: {STUDENT_ID}",
    ):
        r.multi_cell(0, 5.0, line, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.ln(1.6)
    r.set_draw_color(0, 0, 0)
    r.set_line_width(0.3)
    y = r.get_y()
    r.line(r.l_margin, y, r.w - r.r_margin, y)
    r.ln(4)


def section1(r: Report) -> None:
    r.h1("1. Thông tin chung")
    r.p("Bài thực hành xây dựng cơ sở dữ liệu bán hàng trực tuyến gồm bốn bảng trên SQLite, thực "
        "hiện CRUD, truy vấn nhiều bảng, tổng hợp, truy vấn con, hàm cửa sổ, rồi tạo chỉ mục và "
        "phân tích kế hoạch thực thi. Toàn bộ 21 yêu cầu S01–S21 đã cài đặt và chạy kiểm chứng.")
    r.items([
        "Môi trường: Google Cloud Shell, Python 3.12.3, SQLite 3.45.1 (thư viện chuẩn sqlite3, "
        "cơ sở dữ liệu dạng tệp); không dùng dịch vụ tính phí.",
        "Phần bắt buộc S01–S15: sql/answers.sql trên data/sales.db (dữ liệu mẫu 5/5/6/8). Phần "
        "bổ sung S16–S21: sql/answers_homework.sql trên data/sales_extended.db.",
        "Kịch bản hỗ trợ: build_db.py, generate_data.py, run_sql.py, sql_console.py.",
    ])


def criterion1(r: Report) -> None:
    r.h1("2. Tiêu chí 1 — Cài đặt và tạo dữ liệu (2,0 điểm)")
    r.p("Lược đồ được định nghĩa trong sql/schema.sql với bốn bảng, khoá chính, khoá ngoại và "
        "ràng buộc miền giá trị. Khoá chính của order_items là tổ hợp (order_id, product_id) nên "
        "mỗi sản phẩm chỉ xuất hiện một lần trong một đơn. Mọi kết nối đều bật "
        "PRAGMA foreign_keys = ON vì SQLite không kiểm tra khoá ngoại mặc định.")
    r.code(
        "CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);\n"
        "CREATE TABLE products  (product_id INTEGER PRIMARY KEY, name TEXT NOT NULL,\n"
        "                        category TEXT, price REAL CHECK(price >= 0));\n"
        "CREATE TABLE orders    (order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL,\n"
        "                        order_date TEXT,\n"
        "                        FOREIGN KEY(customer_id) REFERENCES customers(customer_id));\n"
        "CREATE TABLE order_items (order_id INTEGER, product_id INTEGER,\n"
        "                        quantity INTEGER CHECK(quantity > 0),\n"
        "                        PRIMARY KEY(order_id, product_id),\n"
        "                        FOREIGN KEY(order_id)   REFERENCES orders(order_id),\n"
        "                        FOREIGN KEY(product_id) REFERENCES products(product_id));")
    r.table(["Bảng", "Kỳ vọng của đề", "Thực tế", "Kết quả"],
            [["customers", "5", "5", "khớp"],
             ["products", "5", "5", "khớp"],
             ["orders", "6", "6", "khớp"],
             ["order_items", "8", "8", "khớp"]],
            [42, 38, 30, 45], "Số dòng sau khi nạp dữ liệu mẫu", aligns="LRRR")
    r.p("Sau khi nạp, PRAGMA foreign_key_check trả về rỗng, nghĩa là mọi khoá ngoại đều trỏ tới "
        "bản ghi tồn tại. Kịch bản build_db.py in trực tiếp bảng đối chiếu trên nên việc kiểm "
        "tra không phụ thuộc vào thao tác thủ công; ảnh chụp màn hình tương ứng nằm ở mục 7.")
    r.figure("01_env.png", "Môi trường thực hành: tài khoản, thư mục, Python và SQLite",
             max_h=44, max_w=150)
    r.figure("02_tables_count.png", "Tạo bốn bảng: số dòng 5/5/6/8 và foreign_key_check rỗng",
             max_h=46, max_w=120)


def criterion2(r: Report) -> None:
    r.h1("3. Tiêu chí 2 — CRUD và câu cơ bản (2,0 điểm)")
    r.p("Nhóm S01–S07 gồm ba truy vấn đọc và bốn thao tác có ghi; các thao tác ghi được viết để "
        "tệp đáp án chạy lặp an toàn.")
    r.table(["Mã", "Nội dung", "Cách thực hiện", "Kết quả"],
            [["S01", "Tên và thành phố khách hàng", "SELECT, ORDER BY", "5 dòng"],
             ["S02", "Sản phẩm giá trên 1 triệu", "WHERE price > 1000000", "2 dòng"],
             ["S03", "Sắp xếp sản phẩm theo giá giảm dần", "ORDER BY DESC", "5 dòng"],
             ["S04", "Thêm khách hàng mới (Lan, Hue)", "INSERT … ON CONFLICT", "1 dòng"],
             ["S05", "Tăng giá Mouse thêm 10%", "UPDATE có điều kiện", "1 dòng"],
             ["S06", "Xoá khách vừa thêm", "DELETE + NOT EXISTS", "1 dòng"],
             ["S07", "Mã đơn và tên khách hàng", "INNER JOIN", "6 dòng"]],
            [12, 62, 48, 20], "Các câu S01–S07 và kết quả thực tế", aligns="LLLR")
    r.figure("03_console.png", "sql_console.py: câu nhiều dòng, GROUP BY, một lỗi SQL, EXIT",
             max_h=42, max_w=100)
    r.items([
        "S04 dùng INSERT … ON CONFLICT(customer_id) DO NOTHING; S05 dùng UPDATE … WHERE "
        "product_id = 102 AND price = 250000 nên lần chạy thứ hai không khớp dòng nào (Rows "
        "affected: 0) và giá giữ 275.000 thay vì nhân 10% lần nữa.",
        "S06 dùng DELETE … AND NOT EXISTS (SELECT 1 FROM orders …) — đúng nghĩa “khách vừa thêm "
        "chưa có đơn”, không vi phạm khoá ngoại. Sau hai lần chạy vẫn 5 khách hàng.",
    ])


def criterion3(r: Report) -> None:
    r.h1("4. Tiêu chí 3 — Truy vấn nâng cao (3,0 điểm)")
    r.p("S08 nối ba bảng tính tổng tiền từng đơn; S09 gom theo khách hàng; S10 lọc kết quả tổng "
        "hợp bằng HAVING; S11 dùng truy vấn con vô hướng; S12 đếm số đơn; S13 lấy top 3 theo "
        "doanh thu.")
    r.code(
        "SELECT o.order_id, SUM(i.quantity * p.price) AS total\n"
        "FROM orders o\n"
        "JOIN order_items i ON i.order_id = o.order_id\n"
        "JOIN products p    ON p.product_id = i.product_id\n"
        "GROUP BY o.order_id\n"
        "ORDER BY total DESC;")
    r.table(["Mã đơn", "Tổng tiền (đồng)", "Khách hàng", "Doanh thu (đồng)"],
            [["1001", "15.550.000", "An (id 1)", "17.150.000"],
             ["1004", "15.000.000", "Chi (id 3)", "15.000.000"],
             ["1006", "7.000.000", "Ha (id 5)", "7.000.000"],
             ["1002", "4.150.000", "Binh (id 2)", "4.150.000"],
             ["1003", "1.600.000", "Dung (id 4)", "825.000"],
             ["1005", "825.000", "—", "—"],
             ["Tổng", "44.125.000", "—", "—"]],
            [22, 40, 40, 38], "Kết quả S08 (hai cột đầu) và S09 (hai cột sau)", aligns="LRlR")
    r.items([
        "Kiểm tra chéo đơn 1001: 1 Laptop 15.000.000 + 2 Mouse 275.000 = 15.550.000, khớp kết "
        "quả máy (giá 275.000 vì S05 chạy trước S08).",
        "S10 trả về 3 khách vượt 5 triệu (An, Chi, Ha); S11 chỉ Laptop vượt giá trung bình "
        "4.045.000; S12 đúng 1 khách (An, 2 đơn); S13 top 3: Laptop 30.000.000, Monitor "
        "10.500.000, Headphones 1.600.000.",
    ])
    r.figure_pair(("04_s08_result_01.png", "Chạy sql/answers.sql: kết quả S01–S04"),
                  ("04_s08_result_02.png", "S09–S12: gom nhóm, HAVING, truy vấn con, đếm đơn"))


def criterion4(r: Report) -> None:
    r.h1("5. Tiêu chí 4 — Index và giải thích (1,5 điểm)")
    r.p("S15 cần so sánh kế hoạch trước và sau khi có chỉ mục, nên sql/explain.sql tự xoá chỉ "
        "mục, chạy EXPLAIN, tạo chỉ mục rồi chạy EXPLAIN lần hai (S20 lặp lại trên dữ liệu lớn).")
    r.code(
        "DROP INDEX IF EXISTS idx_orders_customer;\n"
        "EXPLAIN QUERY PLAN SELECT order_id FROM orders WHERE customer_id = 1;\n"
        "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);\n"
        "EXPLAIN QUERY PLAN SELECT order_id FROM orders WHERE customer_id = 1;")
    r.table(["Thời điểm", "Kế hoạch thực thi"],
            [["Trước khi tạo chỉ mục", "SCAN orders"],
             ["Sau khi tạo chỉ mục",
              "SEARCH orders USING COVERING INDEX idx_orders_customer (customer_id=?)"]],
            [40, 105], "Kế hoạch thực thi trước và sau khi tạo chỉ mục", aligns="LL")
    r.items([
        "SCAN đọc tuần tự toàn bảng rồi lọc nên chi phí tăng theo số dòng; SEARCH đi xuống cây "
        "B-tree của chỉ mục nên chi phí tỉ lệ với logarit số dòng cộng số dòng khớp.",
        "Kế hoạch ghi COVERING INDEX vì truy vấn chỉ cần order_id — với khoá chính INTEGER, chỉ "
        "mục trên customer_id đã chứa sẵn rowid nên không phải đọc lại bảng. Với 6 dòng, chênh "
        "lệch thời gian dưới ngưỡng đo, nên kết luận dựa trên kế hoạch thực thi.",
    ])
    r.figure_pair(("05_explain_before_after_01.png", "sales.db: SCAN orders trước và sau index"),
                  ("05_explain_before_after_02.png",
                   "S20.2–S20.3: SEARCH … USING INDEX trên dữ liệu lớn"))


def criterion5(r: Report) -> None:
    r.h1("6. Tiêu chí 5 — Bài mở rộng và báo cáo (1,5 điểm)")
    r.p("Dữ liệu mở rộng sinh bằng generate_data.py với random.seed(2026) nên tái lập được, ghi "
        "vào tệp riêng data/sales_extended.db, không ghi đè dữ liệu mẫu.")
    r.table(["Đối tượng", "Yêu cầu tối thiểu", "Thực tế"],
            [["Khách hàng", "100", "100"],
             ["Sản phẩm", "30", "30"],
             ["Đơn hàng", "500", "500"],
             ["Dòng đơn hàng", "1.000", "1.500"]],
            [52, 48, 45], "Quy mô dữ liệu mở rộng so với yêu cầu của đề", aligns="LRR")
    r.items([
        "S16 doanh thu theo tháng bằng strftime('%Y-%m', order_date): 13 nhóm từ 10/2025 đến "
        "10/2026, cao nhất 2025-10 với 1.142.485.000 đồng; tháng cuối chỉ 7 đơn vì dữ liệu kết "
        "thúc giữa tháng.",
        "S17 khách chưa có đơn (LEFT JOIN … IS NULL): 8 khách. S18 sản phẩm chưa từng bán "
        "(NOT EXISTS): 4 sản phẩm.",
        "S19 xếp hạng bằng RANK và DENSE_RANK; dữ liệu không có đồng hạng nên hai cột trùng "
        "nhau, khi có đồng hạng RANK cho 2, 2, 4 còn DENSE_RANK cho 2, 2, 3.",
        "S20 trên dữ liệu lớn: SEARCH orders USING INDEX kèm USE TEMP B-TREE FOR ORDER BY do "
        "sắp xếp theo order_date. S21: SQL Server có #t (session), ##t (toàn cục) và tempdb; "
        "SQLite chỉ có TEMP TABLE gắn với kết nối.",
    ])
    r.figure_pair(("06_expanded_counts.png", "Sinh dữ liệu mở rộng: 100/30/500/1500 dòng"),
                  ("07_s19_rank_01.png", "S16 doanh thu 13 tháng và S17 khách chưa có đơn"))
    r.figure_pair(("07_s19_rank_02.png", "S18 bốn sản phẩm chưa bán, S19 RANK/DENSE_RANK, S20"),
                  ("07_s19_rank_03.png", "S21 TEMP TABLE và truy vấn tổng hợp trên bảng tạm"))


def evidence_list(r: Report) -> None:
    r.h1("7. Danh mục ảnh minh chứng")
    if r.image_dir:
        r.p("Toàn bộ ảnh dưới đây được chụp trực tiếp trên Google Cloud Shell và đã chèn vào "
            "đúng mục 2–6 của báo cáo; bảng này để đối chiếu tệp với nội dung minh chứng.")
    else:
        r.p("Ảnh được chụp trực tiếp trên Google Cloud Shell và lưu trong thư mục evidence với "
            "tên như bảng dưới; bản PDF có ảnh được xuất bằng make_report.py --images "
            "../evidence.")
    r.table(["Tệp trong evidence/", "Nội dung cần thấy", "Mục"],
            [["01_env.png", "whoami, pwd, Python 3.12.3, SQLite 3.45.1", "2"],
             ["02_tables_count.png", "Số dòng 5/5/6/8, foreign_key_check rỗng", "2"],
             ["03_console.png", "Console: câu nhiều dòng, một lỗi SQL, EXIT", "3"],
             ["04_s08_result_01, _02", "Kết quả S01–S04 và S09–S12", "4"],
             ["05_explain_before_after_01, _02", "SCAN orders → SEARCH … USING INDEX", "5"],
             ["06_expanded_counts.png", "100/30/500/1500 dòng, khoá ngoại hợp lệ", "6"],
             ["07_s19_rank_01, _02, _03", "S16, S17, S18, S19, S20, S21", "6"]],
            [50, 76, 12], "Các ảnh minh chứng kèm theo bài nộp", aligns="LLR", size=8.4)


def conclusion(r: Report) -> None:
    r.h1("8. Kết luận")
    r.p("Đã hoàn thành đủ 21 yêu cầu của đề: lược đồ bốn bảng có ràng buộc, dữ liệu mẫu đúng "
        "5/5/6/8 dòng, truy vấn từ cơ bản đến nâng cao, chỉ mục có phân tích kế hoạch thực thi; "
        "các tệp đáp án chạy lặp an toàn và dữ liệu mở rộng tái lập được nhờ hạt giống cố định. "
        "Hai điểm rút ra: SQLite phải bật PRAGMA foreign_keys = ON ở mọi kết nối, và đánh giá "
        "chỉ mục nên dựa trên kế hoạch thực thi thay vì thời gian chạy khi dữ liệu còn nhỏ.")


def build(out: Path, images: Path | None, fig_scale: float = 1.0) -> Report:
    r = Report(image_dir=images)
    r.fig_scale = fig_scale
    title_block(r)
    section1(r)
    criterion1(r)
    criterion2(r)
    criterion3(r)
    criterion4(r)
    criterion5(r)
    evidence_list(r)
    conclusion(r)
    out.parent.mkdir(parents=True, exist_ok=True)
    r.output(str(out))
    return r


def count_pages(path: Path) -> int:
    try:
        sys.path.insert(0, str(HERE))
        from pdf_pages import pages_via_regex

        n = pages_via_regex(path)
        if n:
            return n
    except Exception:                                    # noqa: BLE001
        pass
    try:
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(str(path))
        n = len(doc)
        doc.close()
        return n
    except Exception:                                    # noqa: BLE001
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Xuất báo cáo LAB 01 ngắn 4–5 trang (đen trắng)")
    ap.add_argument("--out", type=Path,
                    default=HERE / f"BaoCao_LAB01_{STUDENT_ID}.pdf")
    ap.add_argument("--images", type=Path, default=None,
                    help="thư mục chứa ảnh minh chứng đã chụp (mặc định: không chèn ảnh)")
    args = ap.parse_args()

    images = None
    if args.images:
        # chấp nhận đường dẫn tính từ thư mục hiện tại, từ report/ hoặc từ gốc repo
        cands = [args.images] if args.images.is_absolute() else [
            Path.cwd() / args.images, HERE / args.images,
            LAB / args.images, LAB.parent / args.images]
        images = next((c for c in cands if c.is_dir()), None)
        if images is None:
            print(f"[!] Không thấy thư mục ảnh: {args.images}", file=sys.stderr)
            return 2
        missing = [n for n in FIGURES
                   if not (images / n).exists()]
        if missing:
            print("[!] Thiếu ảnh: " + ", ".join(missing), file=sys.stderr)
            print("    Xem evidence/HUONG_DAN_CHUP_ANH.md để chụp lại.", file=sys.stderr)

    # Ảnh minh chứng làm báo cáo dài thêm, nên tự thu nhỏ dần cho vừa 5 trang.
    scales = [1.0, 0.9, 0.8, 0.7, 0.6] if images else [1.0]
    report, pages = None, 0
    for scale in scales:
        report = build(args.out, images, fig_scale=scale)
        pages = count_pages(args.out)
        if pages and pages <= 5:
            break

    print(f"[ok] {args.out}")
    print(f"     {pages} trang · {report.fig_no if images else 0} ảnh · "
          f"{report.tab_no} bảng · tỉ lệ ảnh {report.fig_scale:g} · "
          f"{args.out.stat().st_size / 1024:.0f} KB")
    if pages > 5:
        print("[!] Dài hơn 5 trang — giảm bớt gạch đầu dòng hoặc bảng.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
