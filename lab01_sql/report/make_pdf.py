#!/usr/bin/env python3
"""Xuất báo cáo LAB 01 ngắn (2–3 trang) ra PDF, có chèn ảnh minh chứng thật.

Dùng khi máy KHÔNG có TeX (sandbox, máy chỉ có Python) — đây là đường biên dịch thay thế
cho `compile.sh` (vốn cần pdfLaTeX + vntex). Nội dung bám đúng đề bài: cài đặt & tạo dữ
liệu, CRUD, truy vấn nâng cao, index, mở rộng + báo cáo.

    pip install -r requirements.txt          # fpdf2 + pillow
    python3 make_pdf.py                      # -> lab01_report_short.pdf (3 trang)
    python3 make_pdf.py --no-images          # bản không ảnh (nhẹ hơn)
    python3 make_pdf.py --out /tmp/x.pdf

Ảnh lấy từ ../evidence/*.png do pipeline `evidence/make_evidence.py` sinh ra. Nếu chưa có
ảnh, script tự gọi pipeline đó (nếu đã cài pillow) hoặc bỏ qua phần ảnh kèm ghi chú.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
CV = LAB / "data" / ".evidence" / "charts"
EVID = LAB / "evidence"

try:
    from fpdf import FPDF
except ImportError:                                    # pragma: no cover
    print("[!] Thiếu fpdf2. Cài: pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(2)

# --- font: DejaVu có đủ glyph tiếng Việt; fpdf2 cần file .ttf ---
FONTS = {
    "DejaVu": ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    "DejaVuMono": ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
}

INK = (26, 30, 36)
DIM = (110, 118, 130)
ACCENT = (18, 74, 150)
RULE = (200, 206, 216)
SHADE = (242, 245, 249)


def fmt(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


class Report(FPDF):
    def __init__(self, with_images: bool, img_factor: float = 1.0, with_console: bool = True):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.with_images = with_images
        self.img_factor = max(0.35, img_factor)
        self.with_console = with_console
        self.set_margins(16, 14, 16)
        self.set_auto_page_break(True, margin=14)
        self.add_font("DejaVu", "", FONTS["DejaVu"][0])
        self.add_font("DejaVu", "B", FONTS["DejaVu"][1])
        self.add_font("Mono", "", FONTS["DejaVuMono"][0])
        self.set_title("Báo cáo LAB 01 - SQL trên Google Cloud Shell với SQLite")

    # ---------- chân trang ----------
    def footer(self) -> None:
        if self.page_no() == 1:
            return
        self.set_y(-11)
        self.set_font("DejaVu", "", 7.2)
        self.set_text_color(*DIM)
        self.cell(0, 4, f"Báo cáo LAB 01 — SQL với SQLite   ·   trang {self.page_no()}",
                  align="C")
        self.set_text_color(*INK)

    # ---------- thành phần ----------
    def h1(self, text: str) -> None:
        self.ln(1.5)
        self.set_font("DejaVu", "B", 11.5)
        self.set_text_color(*ACCENT)
        self.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*RULE)
        self.set_line_width(0.25)
        y = self.get_y() + 0.6
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(2.2)
        self.set_text_color(*INK)

    def p(self, text: str, size: float = 8.9, h: float = 4.2, bold_lead: str | None = None) -> None:
        self.set_font("DejaVu", "", size)
        self.set_text_color(*INK)
        if bold_lead:
            self.set_font("DejaVu", "B", size)
            w = self.get_string_width(bold_lead + " ")
            self.write(h, bold_lead + " ")
            self.set_font("DejaVu", "", size)
            self.write(h, text)
        else:
            self.write(h, text)
        self.ln(h)

    def bullet(self, text: str, size: float = 8.9, h: float = 4.1) -> None:
        self.set_font("DejaVu", "", size)
        self.set_text_color(*INK)
        x = self.get_x()
        self.cell(4, h, "•")
        self.set_x(x + 4)
        self.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.4)

    def code(self, text: str, size: float = 7.4, pad: float = 2.0) -> None:
        self.set_font("Mono", "", size)
        lines = text.rstrip("\n").splitlines()
        h = size * 0.42
        self.set_fill_color(*SHADE)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        y0 = self.get_y()
        width = self.w - self.l_margin - self.r_margin
        for i, line in enumerate(lines):
            if self.get_y() > self.h - self.b_margin - 12:
                self.add_page()
            self.set_xy(self.l_margin, self.get_y() if i else y0)
            yy = self.get_y()
            self.rect(self.l_margin, yy, width, h * 1.28, style="F")
            self.set_xy(self.l_margin + pad, yy + h * 0.16)
            self.set_text_color(*INK)
            self.cell(width - 2 * pad, h, line[:118])
            self.set_y(yy + h * 1.28)
        self.ln(1.6)

    def need(self, h: float) -> None:
        """Sang trang nếu còn ít hơn h mm (tránh tách bảng khỏi tiêu đề)."""
        if self.get_y() + h > self.h - self.b_margin:
            self.add_page()

    def table(self, headers: list[str], rows: list[list[str]], widths: list[float],
              size: float = 7.8, align_right: set[int] | None = None,
              row_h: float = 4.4) -> None:
        align_right = align_right or set()
        self.need(5 + row_h * min(len(rows), 8) + 6)
        def draw_header() -> None:
            self.set_font("DejaVu", "B", size)
            self.set_draw_color(*RULE)
            self.set_line_width(0.2)
            self.set_fill_color(*SHADE)
            for i, head in enumerate(headers):
                self.cell(widths[i], 5, head, border="B",
                          align="R" if i in align_right else "L", fill=True)
            self.ln(5)
            self.set_font("DejaVu", "", size)

        draw_header()
        for row in rows:
            if self.get_y() + row_h > self.h - self.b_margin:
                self.add_page()
                draw_header()
            for i, cell in enumerate(row):
                self.cell(widths[i], row_h, cell, align="R" if i in align_right else "L")
            self.ln(row_h)
        self.ln(1.6)

    def labeled(self, items: list[tuple[str, str]], size: float = 7.8, h: float = 4.0) -> None:
        """Danh sách nhãn + nội dung dài, tự động xuống dòng và sang trang."""
        for label, text in items:
            self.set_font("DejaVu", "B", size)
            self.set_text_color(*ACCENT)
            w = self.get_string_width(label) + 2.5
            self.cell(w, h, label)
            self.set_font("DejaVu", "", size)
            self.set_text_color(*INK)
            self.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")
            self.ln(0.7)

    def image_block(self, path: Path, caption: str, max_h: float = 62) -> None:
        if not self.with_images or not path.exists():
            return
        max_h = max_h * self.img_factor
        from PIL import Image

        with Image.open(path) as im:
            w, h = im.size
        avail_w = self.w - self.l_margin - self.r_margin
        draw_w = avail_w
        draw_h = draw_w * h / w
        if draw_h > max_h:
            draw_h = max_h
            draw_w = draw_h * w / h
        if self.get_y() + draw_h + 8 > self.h - self.b_margin:
            self.add_page()
        x = self.l_margin + (avail_w - draw_w) / 2
        y = self.get_y()
        self.set_draw_color(*RULE)
        self.image(str(path), x=x, y=y, w=draw_w, h=draw_h)
        self.set_line_width(0.2)
        self.rect(x, y, draw_w, draw_h)
        self.set_xy(self.l_margin, y + draw_h + 1)
        self.set_font("DejaVu", "", 7.4)
        self.set_text_color(*DIM)
        self.cell(0, 3.6, caption, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(2)


def ensure_evidence() -> None:
    if (EVID / "manifest.json").exists() and list(EVID.glob("0*.png")):
        return
    script = EVID / "make_evidence.py"
    print("[i] Chưa có ảnh minh chứng — chạy pipeline evidence/make_evidence.py ...")
    try:
        subprocess.run([sys.executable, str(script)], cwd=EVID, check=True)
    except Exception as exc:                            # noqa: BLE001
        print(f"[!] Không sinh được ảnh ({exc}) — báo cáo sẽ bỏ phần ảnh.", file=sys.stderr)


def header_block(pdf: Report) -> None:
    pdf.set_font("DejaVu", "B", 15)
    pdf.set_text_color(*INK)
    pdf.cell(0, 8, "BÁO CÁO THỰC HÀNH LAB 01", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 10.5)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 6, "SQL trên Google Cloud Shell với SQLite", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 7.6)
    pdf.set_text_color(*DIM)
    pdf.cell(0, 4, "Môn: Introduction to Data Science · PTIT   |   "
                   "Họ tên: ................   MSSV: ............   Lớp: ...........",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 7.4)
    pdf.cell(0, 4, f"Ngày thực hiện: {date.today().isoformat()}   |   "
                   f"Python 3.11 · SQLite 3.40 · ảnh minh chứng sinh tự động từ kết quả chạy thật",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.4)
    y = pdf.get_y() + 1.5
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.set_y(y + 3)
    pdf.set_text_color(*INK)


def build(out: Path, with_images: bool, img_factor: float = 1.0,
          with_console: bool = True) -> Path:
    pdf = Report(with_images=with_images, img_factor=img_factor, with_console=with_console)
    pdf.add_page()
    header_block(pdf)

    # ---------------- Tóm tắt ----------------
    pdf.p("Xây dựng cơ sở dữ liệu quan hệ bán hàng trực tuyến bốn bảng (customers, products, "
          "orders, order_items) trên SQLite trong Google Cloud Shell; thực hiện CRUD, JOIN, "
          "GROUP BY/HAVING, subquery, window function; tạo index và đọc EXPLAIN QUERY PLAN để "
          "chứng minh ảnh hưởng của index tới kế hoạch thực thi. Cả 21 yêu cầu S01–S21 đã cài "
          "đặt và chạy kiểm chứng: 0 lỗi, khoá ngoại hợp lệ, kế hoạch chuyển từ SCAN orders "
          "sang SEARCH orders USING COVERING INDEX sau khi tạo index.",
          bold_lead="Tóm tắt.")

    # ---------------- 1. Môi trường ----------------
    pdf.h1("1. Môi trường và cách tổ chức bài làm")
    pdf.table(
        ["Thành phần", "Giá trị"],
        [["Nền tảng", "Google Cloud Shell, chế độ $HOME bền vững (không bật Billing)"],
         ["Python / CSDL", "Python 3.11.2 · thư viện chuẩn sqlite3 · SQLite 3.40.1"],
         ["Công cụ trong bài", "sql_console.py, build_db.py, generate_data.py, run_sql.py"],
         ["Chi phí", "0 đồng — chỉ dùng tài nguyên miễn phí"]],
        widths=[38, 140], size=7.8)
    pdf.p("Đề có hai khối yêu cầu với điều kiện dữ liệu khác nhau nên bài làm tách hai tệp đáp "
          "án riêng: phần BẮT BUỘC S01–S15 trong sql/answers.sql chạy trên data/sales.db (dữ "
          "liệu mẫu của đề); phần BỔ SUNG/về nhà S16–S21 trong sql/answers_homework.sql chạy "
          "trên data/sales_extended.db (dữ liệu mở rộng); phần chứng minh index ở "
          "sql/explain.sql.", bold_lead="Tổ chức.")

    # ---------------- 2. Mô hình dữ liệu ----------------
    pdf.h1("2. Mô hình dữ liệu")
    pdf.code(
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
    pdf.bullet("Khoá chính tổ hợp (order_id, product_id) ngăn một sản phẩm xuất hiện hai lần "
               "trong cùng đơn — muốn mua thêm thì tăng quantity.")
    pdf.bullet("CHECK chặn giá âm và số lượng ≤ 0 ngay tại tầng CSDL, không phụ thuộc ứng dụng.")
    pdf.bullet("SQLite KHÔNG kiểm tra khoá ngoại mặc định, nên mọi kết nối trong bài đều chạy "
               "PRAGMA foreign_keys = ON ngay sau khi mở CSDL — thiếu bước này ràng buộc chỉ là "
               "chú thích.")
    pdf.image_block(EVID / "02_tables_count.png",
                    "Hình 1 — Nạp dữ liệu mẫu: 5 khách · 5 sản phẩm · 6 đơn · 8 dòng đơn, "
                    "PRAGMA foreign_key_check rỗng")

    # ---------------- 3. S01–S15 ----------------
    pdf.h1("3. Kết quả phần bắt buộc (S01–S15)")
    pdf.p("Chạy python3 run_sql.py sql/answers.sql thực thi 18 câu lệnh với 0 lỗi; chạy lần thứ "
          "hai vẫn 0 lỗi và cho kết quả giống hệt. Bảng dưới tóm tắt kỹ thuật và số dòng thực tế "
          "của từng câu.")
    pdf.table(
        ["Mã", "Kỹ thuật", "Dòng", "Mã", "Kỹ thuật", "Dòng"],
        [["S01", "SELECT + ORDER BY", "5", "S09", "LEFT JOIN + GROUP BY", "5"],
         ["S02", "WHERE price > 1.000.000", "2", "S10", "HAVING SUM(...) > 5tr", "3"],
         ["S03", "ORDER BY price DESC", "5", "S11", "subquery AVG(price)", "1"],
         ["S04", "INSERT ... ON CONFLICT", "1", "S12", "HAVING COUNT(đơn) ≥ 2", "1"],
         ["S05", "UPDATE price = price*1.1", "1", "S13", "ORDER BY + LIMIT 3", "3"],
         ["S06", "DELETE + NOT EXISTS", "1", "S14", "CREATE INDEX", "—"],
         ["S07", "INNER JOIN 2 bảng", "6", "S15", "EXPLAIN QUERY PLAN", "1"],
         ["S08", "JOIN 3 bảng + SUM", "6", "—", "", ""]],
        widths=[12, 52, 12, 12, 52, 12], size=7.6, align_right={2, 5})
    pdf.image_block(EVID / "04_s08_result.png",
                    "Hình 2 — S08 tổng tiền từng đơn và S09 doanh thu từng khách (giá Mouse đã "
                    "tăng 10% ở S05)")
    pdf.p("Ba câu có ghi (S04–S06) được viết để file chạy lại không sai dữ liệu: INSERT có ON "
          "CONFLICT DO NOTHING; UPDATE kèm điều kiện AND price = 250000 nên lần chạy thứ hai trả "
          "về Rows affected: 0 (giá vẫn 275.000, không cộng dồn 10%); DELETE kèm NOT EXISTS đúng "
          "nghĩa “khách vừa thêm chưa có đơn” và bảo vệ khoá ngoại. S10 lọc theo kết quả tổng hợp "
          "nên dùng HAVING (3 khách vượt 5 triệu); S11 so với giá trung bình 4.045.000 nên chỉ "
          "Laptop vượt; S12 đúng 1 khách (An, 2 đơn); S13 top 3 là Laptop 30.000.000, Monitor "
          "10.500.000, Headphones 1.600.000 — LIMIT không xử lý đồng hạng nên muốn đúng phải dùng "
          "RANK() như S19.", bold_lead="CRUD lặp an toàn.")

    # ---------------- 4. Index ----------------
    pdf.h1("4. Index và kế hoạch thực thi (S14–S15)")
    pdf.p("explain.sql tự DROP rồi CREATE index nên luôn đo được cả hai trạng thái: "
          "DROP INDEX IF EXISTS → EXPLAIN → CREATE INDEX IF NOT EXISTS → EXPLAIN.")
    pdf.image_block(EVID / "05_explain_before_after.png",
                    "Hình 3 — Trước index: SCAN orders; sau index: SEARCH orders USING COVERING "
                    "INDEX idx_orders_customer")
    pdf.bullet("SCAN đọc tuần tự toàn bảng rồi mới lọc — chi phí tăng tuyến tính theo số dòng.")
    pdf.bullet("SEARCH đi xuống cây B-tree của index — chi phí ~log n cộng số dòng khớp.")
    pdf.bullet("COVERING INDEX: câu chỉ cần order_id, mà index trên customer_id của bảng có "
               "INTEGER PRIMARY KEY đã chứa rowid (chính là order_id), nên SQLite trả lời hoàn "
               "toàn từ index; nếu lấy thêm order_date (S20) thì kế hoạch là SEARCH ... USING "
               "INDEX.")
    pdf.bullet("Không kết luận bằng thời gian chạy: với 6 đơn, chênh lệch nằm dưới ngưỡng đo của "
               "đồng hồ hệ thống — phải đọc plan (kiểu truy cập, có phải sort thêm hay không).")

    # ---------------- 5. S16–S21 ----------------
    pdf.h1("5. Kết quả phần bổ sung (S16–S21)")
    pdf.image_block(EVID / "06_expanded_counts.png",
                    "Hình 4 — Dữ liệu mở rộng: 100 khách · 30 sản phẩm · 500 đơn · 1.500 dòng "
                    "đơn, khoá ngoại ok, trải 13 tháng")
    pdf.labeled([
        ("S16", "Doanh thu theo tháng (strftime('%Y-%m')): 13 nhóm tháng 10/2025–10/2026; cao nhất "
                "2025-10 với 1.142.485.000 đ / 53 đơn; tháng cuối chỉ 7 đơn (tháng dở dang)."),
        ("S17", "Khách chưa có đơn (LEFT JOIN ... IS NULL): 8 khách — id 37, 38, 43, 56, 83, 89, "
                "92, 94."),
        ("S18", "Sản phẩm chưa từng bán (NOT EXISTS): 4 sản phẩm — Graphics Card, RAM 16GB, CPU "
                "Cooler, Power Supply."),
        ("S19", "Xếp hạng bằng window function: top 3 Ha 314.565.000 · Ho Mai 281.910.000 · Hoang "
                "Chi 267.400.000. Dữ liệu không đồng hạng nên RANK = DENSE_RANK; khi đồng hạng, "
                "RANK cho 2, 2, 4 còn DENSE_RANK cho 2, 2, 3."),
        ("S20", "Sau khi mở rộng: chưa index là SCAN orders, có index là SEARCH orders USING INDEX "
                "kèm USE TEMP B-TREE FOR ORDER BY (do ORDER BY order_date). Nếu truy vấn chạy "
                "thường xuyên, index tổ hợp (customer_id, order_date) sẽ bỏ được bước sort."),
        ("S21", "SQL Server: #t là bảng tạm cục bộ theo session, ##t là bảng tạm toàn cục dùng "
                "chung giữa các session, cả hai sống trong tempdb (CSDL hệ thống, chứa cả biến "
                "bảng và sort/hash spill). SQLite chỉ có CREATE TEMP TABLE gắn với kết nối, nằm "
                "trong schema temp (RAM hoặc tệp tạm tuỳ PRAGMA temp_store) và KHÔNG có bảng tạm "
                "toàn cục; bảng temp được tìm trước main nên trùng tên sẽ che bảng thường."),
    ])
    pdf.image_block(EVID / "07_s19_rank.png",
                    "Hình 5 — S19 xếp hạng khách hàng theo doanh thu bằng RANK / DENSE_RANK")

    # ---------------- 6. Kết luận ----------------
    pdf.h1("6. Kết luận và bài học")
    pdf.p("Cả 21 yêu cầu đã hoàn thành. Bốn bài học: (i) khoá ngoại SQLite là tuỳ chọn — phải bật "
          "pragma; (ii) script có ghi phải lặp an toàn (ON CONFLICT, điều kiện chặt trong UPDATE, "
          "NOT EXISTS trong DELETE); (iii) index không miễn phí — chỉ tạo cho cột thường lọc/nối; "
          "(iv) đọc plan thay vì đo thời gian, chú ý COVERING INDEX và USE TEMP B-TREE FOR ORDER "
          "BY vì chúng chỉ ra chi phí ẩn.")
    if with_images and pdf.with_console:
        pdf.image_block(EVID / "03_console.png",
                        "Hình 6 — SQL Console: câu lệnh nhiều dòng, thông báo lỗi và tiếp tục "
                        "nhận câu lệnh mới", max_h=46)

    out.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Xuất báo cáo LAB 01 ngắn ra PDF (không cần TeX)")
    ap.add_argument("--out", type=Path, default=HERE / "lab01_report_short_pdf.pdf")
    ap.add_argument("--no-images", action="store_true", help="không chèn ảnh minh chứng")
    args = ap.parse_args()
    if not args.no_images:
        ensure_evidence()

    # Đề yêu cầu 2–3 trang: thử co ảnh dần, cuối cùng bỏ Hình 6 (console) nếu vẫn quá dài.
    attempts = [
        (1.00, True), (0.88, True), (0.78, True), (0.70, False), (0.60, False),
    ]
    path = args.out
    for factor, console in attempts:
        path = build(args.out, with_images=not args.no_images,
                     img_factor=factor, with_console=console)
        pages = count_pages(path)
        if pages <= 3 or args.no_images:
            note = "" if factor == 1.0 else f" (co ảnh ×{factor:.2f}"
            if factor != 1.0:
                note += "" if console else ", bỏ Hình 6"
                note += ")"
            print(f"[ok] {path}  ({pages} trang, {path.stat().st_size / 1024:.0f} KB)"
                  f"{note}")
            return 0
    print(f"[!] Vẫn {count_pages(path)} trang — giảm thêm ảnh hoặc dùng --no-images",
          file=sys.stderr)
    return 1


def count_pages(path: Path) -> int:
    try:
        sys.path.insert(0, str(HERE))
        from pdf_pages import pages_via_regex

        return pages_via_regex(path) or 0
    except Exception:                                   # noqa: BLE001
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
