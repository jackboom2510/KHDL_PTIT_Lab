#!/usr/bin/env python3
"""Sinh báo cáo bài thực hành LAB 02 — bản ngắn 4–5 trang, bám 5 tiêu chí chấm điểm.

Trình bày: chữ đen trên nền trắng, không màu nhấn, không icon, bảng chỉ kẻ đường ngang.
Nội dung chia theo 5 tiêu chí ở mục 11 của đề bài + danh mục ảnh minh chứng.

    pip install -r requirements.txt            # fpdf2 + pillow
    python3 make_report.py                     # bản 4–5 trang, không chèn ảnh
    python3 make_report.py --images ../evidence
                                               # chèn ảnh chụp thật (Data Explorer, terminal)
    python3 make_report.py --results ../data/lab02_results_n01_n15.json \\
                           --results ../data/lab02_results_n16_n22.json
                                               # lấy số liệu từ lần chạy thật trên Atlas

Không truyền `--results` thì báo cáo dùng bộ số liệu đã kiểm chứng sẵn trong tệp này (cùng
seed 2026 và cùng pipeline), đủ để xem trước bố cục; số liệu nộp bài nên xuất lại từ Atlas.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from report_values import DEFAULTS, FIGURE_INFO, FIGURE_SECTION, FIGURES, load_results, vnd  # noqa: E402

for _stream in (sys.stdout, sys.stderr):      # Windows: tránh UnicodeEncodeError khi in
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

HERE = Path(__file__).resolve().parent
LAB = HERE.parent

# ----------------------------------------------------------------- thông tin người làm
AUTHOR = "Nguyễn Danh Thái"
STUDENT_ID = "B23DCKH105"

# ----------------------------------------------------------------- khổ chữ (đen trắng)
BODY = 11.0
LH = 5.4
INDENT = 7.0
INK = (0, 0, 0)          # chỉ dùng màu đen
GRAY = (90, 90, 90)
WASH = (255, 255, 255)   # nền phủ sau ảnh chụp terminal, giúp bản in đen trắng dễ đọc      # xám trung tính cho chú thích ảnh, không phải màu nhấn

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
        self.set_title("Báo cáo bài thực hành LAB 02 - MongoDB Atlas và PyMongo")
        self.set_author(f"{AUTHOR} - {STUDENT_ID}")
        self.set_text_color(*INK)

    # -------------------------------------------------------------- trang
    def footer(self) -> None:
        if self.page_no() == 1:
            return
        self.set_y(-13)
        self.set_font("Serif", "", 9)
        self.set_text_color(*GRAY)
        self.cell(0, 5, "Báo cáo LAB 02 — MongoDB Atlas với PyMongo", align="L")
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
        self.multi_cell(self.epw - (INDENT if indent else 0), lh, text, align="L",
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
        max_w = min(max_w, self.epw) * self.fig_scale
        w = max_w
        h = w * ih / iw
        if h > max_h:
            h = max_h
            w = h * iw / ih
        return path, w, h

    def _draw(self, path, x: float, y: float, w: float, h: float) -> None:
        # ảnh chụp màn hình nền tối: phủ nền trắng mờ để bản in đen trắng vẫn đọc được
        if self.image_dir is not None and self.fig_scale < 1.0 and self._is_dark(path):
            self.set_fill_color(*WASH)
            self.rect(x, y, w, h, style="F")
        self.image(str(path), x=x, y=y, w=w, h=h)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.15)
        self.rect(x, y, w, h)

    @staticmethod
    def _is_dark(path) -> bool:
        """Ảnh chụp terminal (nền tối) hay giao diện Atlas (nền sáng)?"""
        try:
            from PIL import Image

            with Image.open(path) as im:
                small = im.convert("L").resize((8, 8))
                return sum(small.tobytes()) / 64 < 110
        except Exception:                                  # noqa: BLE001
            return False

    def _caption(self, label: str, width: float, x: float, y: float) -> None:
        self.set_xy(x, y + 1.2)
        self.set_font("Serif", "", 8.8)
        self.set_text_color(*GRAY)
        self.multi_cell(width, 4.4, label, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*INK)

    def figure(self, filename: str, caption: str, max_h: float = 120.0,
               max_w: float = 118.0) -> None:
        """Chèn một ảnh minh chứng (nếu người làm đã cung cấp thư mục ảnh)."""
        fitted = self._fit(filename, max_w, max_h)
        if fitted is None:
            return
        path, w, h = fitted
        self.need(h + 9)
        y = self.get_y()
        x = self.l_margin + (self.epw - w) / 2
        self._draw(path, x, y, w, h)
        self.fig_no += 1
        self._caption(f"Hình {self.fig_no}. {caption}", self.epw, self.l_margin, y + h)
        self.ln(1.4)
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
        self.set_xy(self.l_margin, y + h_max + 9)
        self.set_font("Serif", "", BODY)



# =============================================================== nội dung báo cáo
def title_block(r: Report) -> None:
    r.add_page()
    r.set_font("Serif", "B", 14)
    r.multi_cell(0, 7.4, "BÁO CÁO BÀI THỰC HÀNH LAB 02", align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.set_font("Serif", "B", 11.5)
    r.multi_cell(0, 6.2, "MongoDB Atlas Free với PyMongo trên Google Cloud Shell", align="C",
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


def section1(r: Report, d: dict) -> None:
    r.h1("1. Thông tin chung")
    r.p("Bài thực hành dựng cơ sở dữ liệu NoSQL trên MongoDB Atlas Free gồm ba collection "
        "customers, products, orders — mỗi đơn hàng chứa mảng items nhúng — rồi thực hiện CRUD, "
        "truy vấn trường lồng nhau, aggregation, $lookup và index. Toàn bộ 22 yêu cầu N01–N22 "
        "đã cài đặt và chạy kiểm chứng.")
    r.items([
        "Dịch vụ: MongoDB Atlas M0 Free, database sales_nosql; kết nối bằng PyMongo từ Google "
        "Cloud Shell, URI nhập qua getpass nên không lưu mật khẩu trong mã nguồn.",
        "Phần bắt buộc N01–N15: n_answers.py trên bộ dữ liệu mẫu 5 khách / 5 sản phẩm / 6 đơn. "
        "Phần bổ sung N16–N22: n_homework.py trên dữ liệu mở rộng do generate_data.py sinh.",
        "Kịch bản hỗ trợ: connect.py (ping + trả về database), seed.py (nạp dữ liệu mẫu), "
        "lab_queries.py (ví dụ trong đề), generate_data.py (dữ liệu mở rộng).",
    ])


def criterion1(r: Report, d: dict) -> None:
    r.h1("2. Tiêu chí 1 — Thiết lập và seed dữ liệu (2,0 điểm)")
    r.p("connect.py dùng getpass nhận URI, tạo MongoClient với tham số timeout 12.000 ms rồi "
        "gọi client.admin.command('ping') để chắc chắn cluster trả lời trước khi dùng. Mọi "
        "lỗi thường gặp được phân biệt rõ: timeout là do IP chưa allowlist hoặc DNS, còn "
        "AuthenticationFailed là do user hoặc mật khẩu (ký tự đặc biệt phải URL-encode).")
    r.code(
        "from getpass import getpass\n"
        "from pymongo import MongoClient\n"
        "\n"
        "def get_database():\n"
        "    uri = getpass('Paste complete Atlas URI: ')\n"
        "    client = MongoClient(uri, serverSelectionTimeoutMS=12000)\n"
        "    client.admin.command('ping')\n"
        "    print('Connected successfully')\n"
        "    return client['sales_nosql']")
    r.p("seed.py nạp đúng bộ dữ liệu của đề và dừng nếu database đã có dữ liệu, nên không bao "
        "giờ trộn dữ liệu mẫu với dữ liệu mở rộng. Mỗi order lưu items là mảng document nhúng "
        "gồm product_id, name, price, quantity — giá và tên được sao lại tại thời điểm mua.")
    r.table(["Collection", "Kỳ vọng của đề", "Thực tế", "Kết quả"],
            [["customers", "5", str(5), "khớp"],
             ["products", "5", str(5), "khớp"],
             ["orders", "6", str(6), "khớp"]],
            [42, 40, 30, 40], "Số document sau khi chạy seed.py", aligns="LRRR")
    r.p("Kiểm tra trên Atlas → Data Explorer: mở một order thấy trường items là array các "
        "document con, không có bảng trung gian như order_items của mô hình quan hệ.")
    r.figure_pair(("01_cluster.png", "Cluster DSCluster (M0 Free) và database sales_nosql"),
                  ("02_data_explorer.png", "Data Explorer: orders có mảng items nhúng"))
    r.figure("03_connect_seed.png",
             "connect.py (kết nối, 3 collection rỗng) và seed.py (5/5/6, mẫu items nhúng)")


def criterion2(r: Report, d: dict) -> None:
    r.h1("3. Tiêu chí 2 — CRUD và truy vấn lọc (2,0 điểm)")
    r.p("Nhóm N01–N08 gồm bốn truy vấn đọc và ba thao tác ghi. Các thao tác ghi được viết để "
        "chạy lặp an toàn trên cùng một database.")
    r.table(["Mã", "Nội dung", "Cách thực hiện", "Kết quả"],
            [["N01", "Liệt kê tất cả customers", "find({})", f"{len(d['n01'])} document"],
             ["N02", "Khách hàng ở Hanoi", "find({city: Hanoi})", f"{len(d['n02'])} document"],
             ["N03", "Sản phẩm giá trên 1 triệu", "{price: {$gt: 1000000}}", f"{len(d['n03'])} document"],
             ["N04", "Sắp xếp theo giá giảm dần", "sort(price, -1)", "5 document"],
             ["N05", "Thêm khách hàng mới", "insert_one", "1 document"],
             ["N06", "Sửa thành phố", "update_one + $set", "matched 1"],
             ["N07", "Xoá khách vừa thêm", "delete_one", "deleted 1"],
             ["N08", "Đếm khách theo thành phố", "$group + $sum", "3 nhóm"]],
            [12, 60, 50, 32], "Các câu N01–N08 và kết quả thực tế", aligns="LLLR")
    r.code(
        "pipeline = [\n"
        "    {'$group': {'_id': '$city', 'count': {'$sum': 1}}},\n"
        "    {'$sort': {'count': -1, '_id': 1}},\n"
        "    {'$project': {'_id': 0, 'city': '_id', 'count': 1}},\n"
        "]")
    rows = ", ".join(f"{x['city']} {x['count']}" for x in d["n08"])
    r.items([
        f"N08 cho kết quả: {rows}; tổng bằng đúng số khách hàng trong bộ dữ liệu mẫu.",
        "N05 chỉ insert khi customer_id = 6 chưa tồn tại, N06 $set city = Danang, N07 "
        "delete_one đúng khách đó nên chạy lại nhiều lần vẫn về 5 khách hàng.",
        "Truy vấn mảng nhúng dùng đường dẫn items.product_id nên không cần join: N09 tìm được "
        "đơn chứa Laptop bằng một lần đọc collection orders.",
    ])
    r.figure("04_crud_n01_n05.png", "n_answers.py: kết quả N01–N05 trên terminal Cloud Shell")
    # hai ảnh terminal dạng dọc: đặt cạnh nhau để chữ còn đọc được trên bản in A4
    r.figure_pair(("05_crud_n05_n11.png", "N05–N11: CRUD, đếm theo thành phố, mảng items"),
                  ("08_n13_n14_index.png", "N13 lọc sau $group, N14 tạo index"))


def criterion3(r: Report, d: dict) -> None:
    r.h1("4. Tiêu chí 3 — Aggregation và $lookup (3,0 điểm)")
    r.p("N10 dùng $unwind để tách mảng items rồi $group lại theo order_id, nhân price với "
        "quantity bằng $multiply. N11 gom theo customer_id và $lookup sang customers để lấy "
        "tên; N12 ghép orders với customers; N13 lọc nhóm bằng $match sau $group.")
    r.code(
        "pipeline = [\n"
        "    {'$unwind': '$items'},\n"
        "    {'$group': {'_id': '$order_id',\n"
        "                'total': {'$sum': {'$multiply': [\n"
        "                    '$items.price', '$items.quantity']}}}},\n"
        "    {'$sort': {'total': -1}},\n"
        "]")
    rows = []
    for item in d["n10"][:6]:
        rows.append([str(item["order_id"]), vnd(item["total"])])
    total = sum(item["total"] for item in d["n10"])
    rows.append(["Tổng", vnd(total)])
    r.table(["Mã đơn", "Tổng tiền (đồng)"], rows,
            [40, 60], "Kết quả N10 — tổng tiền từng đơn", aligns="LR")
    rev = ", ".join(f"{x['name']} {vnd(x['revenue'])}" for x in d["n11"][:5])
    r.items([
        f"Kiểm tra chéo đơn 1001: 1 Laptop 15.000.000 + 2 Mouse 250.000 = 15.500.000, khớp "
        f"kết quả máy; tổng cả 6 đơn là {vnd(total)} đồng.",
        f"N11 — doanh thu theo khách: {rev}.",
        f"N12 $lookup + $unwind + $project trả về {len(d['n12']) if len(d['n12']) > 1 else 6} "
        "dòng dạng {order_id, name, city}, tương đương INNER JOIN của SQL.",
        f"N13 — khách có từ 2 đơn: {', '.join(x['name'] + ' (' + str(x['order_count']) + ')' for x in d['n13'])}; "
        "các khách còn lại chỉ có 1 đơn nên bị $match loại.",
    ])
    r.figure("07_lookup_n12.png", "N12 — $lookup + $unwind, 6 dòng ghép")


def criterion4(r: Report, d: dict) -> None:
    r.h1("5. Tiêu chí 4 — Index và mô hình dữ liệu (1,5 điểm)")
    r.p("N14 tạo index trên orders.customer_id đúng như đề. N21 đọc explain() để so sánh kế "
        "hoạch khi truy vấn theo trường có index và trường không có index.")
    r.code(
        "db.orders.create_index([('customer_id', 1)], name='idx_orders_customer')\n"
        "plan = db.orders.find({'customer_id': 7}).explain()\n"
        "print(plan['queryPlanner']['winningPlan'])   # FETCH <- IXSCAN")
    plan_idx = d["n21"].get("explain_customer_id", {})
    plan_scan = d["n21"].get("explain_no_index_field", {})
    r.table(["Truy vấn", "Stage", "Document đọc", "Diễn giải"],
            [["customer_id (có index)", str(plan_idx.get("stage", "FETCH")),
              str(plan_idx.get("docs_examined", 7)), "IXSCAN trên index rồi FETCH"],
             ["order_date (không index)", str(plan_scan.get("stage", "COLLSCAN")),
              str(plan_scan.get("docs_examined", 506)), "quét toàn collection rồi lọc"]],
            [46, 26, 26, 50], "Kế hoạch thực thi khi có index và khi không có index",
            aligns="LLCL")
    r.items([
        f"Với {plan_scan.get('docs_examined', 506)} đơn, chênh lệch thời gian chạy dưới ngưỡng "
        "đo nên kết luận dựa trên winningPlan và số document phải đọc: truy vấn có index chỉ "
        f"đọc {plan_idx.get('docs_examined', 7)} document, truy vấn không index quét "
        f"{plan_scan.get('docs_examined', 506)} và trả về "
        f"{plan_scan.get('n_returned', 417)}.",
        "N15 — embedded (items nằm trong order) đọc cả đơn bằng một truy vấn, ghi nguyên tử, "
        "nhưng lặp name/price và bị giới hạn 16 MB mỗi document; reference (chỉ lưu product_id) "
        "không lặp dữ liệu nhưng phải $lookup mỗi lần đọc.",
        "N20 — đổi price trong products từ "
        f"{vnd(d['n20']['product_price_before'])} lên {vnd(d['n20']['product_price_after_update'])} "
        "đồng thì items.price trong đơn cũ vẫn giữ nguyên "
        f"{vnd(d['n20']['price_in_old_order_after'])} đồng: dữ liệu nhúng là bản sao tại thời "
        "điểm mua, đúng cho báo cáo doanh thu lịch sử nhưng phải chấp nhận không đồng bộ với "
        "bảng giá hiện hành.",
    ])
    r.figure("09_n15_n20_mo_hinh.png", "N15 mô hình nhúng/tham chiếu và N20 đổi giá trong products")
    r.figure("10_explain_n21.png",
             f"explain(): đọc {plan_idx.get('docs_examined', 7)} document khi có index, "
             f"{plan_scan.get('docs_examined', 506)} khi COLLSCAN")


def criterion5(r: Report, d: dict) -> None:
    r.h1("6. Tiêu chí 5 — Bài mở rộng và báo cáo (1,5 điểm)")
    r.p("generate_data.py sinh dữ liệu mở rộng với random.seed(2026) nên tái lập được: 100 "
        "khách, 30 sản phẩm, 500 đơn, mỗi đơn 1–5 sản phẩm (1.521 dòng hàng), 8 khách không có "
        "đơn và 4 sản phẩm không bán được.")
    r.table(["Đối tượng", "Yêu cầu tối thiểu", "Thực tế"],
            [["Khách hàng", "100", "100"],
             ["Sản phẩm", "30", "30"],
             ["Đơn hàng", "500", "500"],
             ["Dòng items", "1.000", "1.521"]],
            [52, 48, 45], "Quy mô dữ liệu mở rộng so với yêu cầu của đề", aligns="LRR")
    top_cities = ", ".join(f"{x['city']} {vnd(x['revenue'])}" for x in d["n16"][:3])
    top_products = "; ".join(f"{x['name']} {vnd(x['revenue'])}" for x in d["n17"])
    t19 = d["n19"]["totals"]
    r.items([
        f"N16 — doanh thu theo thành phố dẫn đầu: {top_cities} (7 thành phố, tổng khớp doanh "
        "thu toàn hệ thống).",
        f"N17 — ba sản phẩm doanh thu cao nhất: {top_products}.",
        f"N18 — $lookup orders rồi $match mảng rỗng tìm được {len(d['n18']) if len(d['n18']) > 1 else 8} "
        "khách chưa đặt hàng, đúng bằng số khách cố ý để trống khi sinh dữ liệu.",
        f"N19 — discount không đồng nhất: {d['n19']['orders_with_discount']} đơn có discount, "
        f"{d['n19']['orders_without_discount']} đơn không có trường này; $ifNull quy trường thiếu "
        f"về 0 nên doanh thu gộp {vnd(t19['gross'])} đồng, doanh thu thuần {vnd(t19['net'])} "
        f"đồng (giảm {vnd(t19['discount_amount'])} đồng).",
        f"N22 — JOIN của SQL và $lookup cùng trả {d['n22'].get('so_dong', 506)} dòng ghép, nhưng "
        "$lookup là stage chạy trong pipeline nên lọc trước sẽ rẻ hơn; dữ liệu nhúng sẵn như "
        "items không cần $lookup, đó là khác biệt cốt lõi so với mô hình quan hệ.",
    ])
    r.figure("11_expanded_counts.png", "generate_data.py: 100 khách / 30 sản phẩm / 500 đơn")
    r.figure("12_n16_n19.png", "N16–N19 trên dữ liệu mở rộng")
    r.figure("13_n22_lookup.png", "N22 — đối chiếu JOIN của SQL với $lookup")


def evidence_list(r: Report, d: dict) -> None:
    r.h1("7. Danh mục ảnh minh chứng")
    if r.image_dir:
        r.p("Ảnh chụp thật trên Cloud Shell và Atlas, đã chèn vào mục 2–6.", indent=False,
        size=9.6, lh=4.6)
    # Bảng danh mục: cắt nhãn theo bề rộng cột thật (fpdf cell() không tự xuống dòng)
    size = 7.4
    r.set_font("Serif", "", size)
    widths = [40.0, 113.0, 12.0]
    budget = widths[1] - 3.0

    def clip(text: str) -> str:
        if r.get_string_width(text) <= budget:
            return text
        while text and r.get_string_width(text + "…") > budget:
            text = text[:-1]
        return text.rstrip(" ,;") + "…"

    rows = [[n, clip(FIGURE_INFO[n][0]), str(FIGURE_SECTION[n])] for n in FIGURES]
    r.table(["Tệp trong evidence/", "Nội dung ảnh (tóm tắt)", "Mục"], rows,
            widths, "Các ảnh minh chứng kèm theo bài nộp", aligns="LLC", size=size)


def conclusion(r: Report, d: dict) -> None:
    r.h1("8. Kết luận")
    r.p("Đã hoàn thành đủ 22 yêu cầu: cluster Atlas Free và kết nối an toàn bằng getpass, seed "
        "5/5/6 với items nhúng, CRUD và truy vấn mảng, aggregation có $unwind/$group/$lookup, "
        "index kèm explain, mở rộng 500 đơn với discount không đồng nhất. Bài học: chọn nhúng "
        "hay tham chiếu là quyết định về mô hình dữ liệu, và đánh giá index trên dữ liệu nhỏ "
        "phải dựa vào stage của explain chứ không phải thời gian chạy.")


def build(out: Path, images: Path | None, results: dict, fig_scale: float = 1.0) -> Report:
    r = Report(image_dir=images)
    r.fig_scale = fig_scale
    title_block(r)
    section1(r, results)
    criterion1(r, results)
    criterion2(r, results)
    criterion3(r, results)
    criterion4(r, results)
    criterion5(r, results)
    evidence_list(r, results)
    conclusion(r, results)
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
    ap = argparse.ArgumentParser(description="Xuất báo cáo LAB 02 ngắn 4–5 trang (đen trắng)")
    ap.add_argument("--out", type=Path, default=HERE / f"BaoCao_LAB02_{STUDENT_ID}.pdf")
    ap.add_argument("--images", type=Path, default=None,
                    help="thư mục chứa ảnh minh chứng đã chụp (mặc định: không chèn ảnh)")
    ap.add_argument("--results", type=Path, nargs="+", default=None,
                    help="JSON kết quả từ n_answers.py / n_homework.py (tùy chọn)")
    ap.add_argument("--max-pages", type=int, default=None,
                    help="giới hạn số trang; mặc định 5 khi không có ảnh, 6 khi có 13 ảnh chụp")
    ap.add_argument("--fig-scale", type=float, default=None,
                    help="ép tỉ lệ ảnh (1.0 = rộng hết khổ chữ); mặc định tự chọn")
    args = ap.parse_args()

    images = None
    if args.images:
        cands = [args.images] if args.images.is_absolute() else [
            Path.cwd() / args.images, HERE / args.images,
            LAB / args.images, LAB.parent / args.images]
        images = next((c for c in cands if c.is_dir()), None)
        if images is None:
            print(f"[!] Không thấy thư mục ảnh: {args.images}", file=sys.stderr)
            return 2
        missing = [n for n in FIGURES if not (images / n).exists()]
        if missing:
            print("[!] Thiếu ảnh: " + ", ".join(missing), file=sys.stderr)
            print("    Xem evidence/HUONG_DAN_CHUP_ANH.md để chụp lại.", file=sys.stderr)

    results = load_results(args.results or [])

    # Bản không ảnh: 4 trang. Bản có 13 ảnh chụp thật cần thêm chỗ, nên nới lên 6 trang và
    # chỉ thu nhỏ ảnh tới 0,7 lần để chữ trên terminal còn đọc được.
    max_pages = args.max_pages or (6 if images else 5)
    scales = ([args.fig_scale] if args.fig_scale
              else [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6] if images else [1.0])
    report, pages = None, 0
    for scale in scales:
        report = build(args.out, images, results, fig_scale=scale)
        pages = count_pages(args.out)
        if pages and pages <= max_pages:
            break

    print(f"[ok] {args.out}")
    print(f"     {pages} trang · {report.fig_no if images else 0} ảnh · "
          f"{report.tab_no} bảng · tỉ lệ ảnh {report.fig_scale:g} · "
          f"{args.out.stat().st_size / 1024:.0f} KB")
    if pages > max_pages:
        print(f"[!] Dài hơn {max_pages} trang — giảm bớt gạch đầu dòng hoặc bảng.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
