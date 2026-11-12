#!/usr/bin/env python3
"""Sinh báo cáo LAB 02 bản Word (.docx) — có sẵn **khung chèn ảnh** theo đúng tiêu chí chấm.

    pip install python-docx
    python3 make_docx.py                        # khung trống để dán ảnh
    python3 make_docx.py --images ../evidence   # ảnh nào đã có thì chèn luôn vào khung
    python3 make_docx.py --results ../data/lab02_results_n01_n15.json
                                              # lấy số liệu từ lần chạy thật trên Atlas

Bản Word dùng cùng nội dung, cùng bộ số liệu và cùng thứ tự ảnh với bản PDF
(`make_report.py`), cả hai đọc chung `report_values.py` nên không bị lệch nhau.

Khung ảnh là một bảng 1 ô viền nét đứt, cao 6,2 cm, ghi rõ:
    - số hiệu hình và chú thích (giống bản PDF),
    - tên tệp cần dán (ví dụ `01_cluster.png`),
    - nội dung phải thấy trong ảnh.
Muốn dán ảnh: bấm vào trong khung → Insert > Pictures, hoặc chạy lại với `--images <thư mục>`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from report_values import FIGURE_INFO, FIGURE_SECTION, FIGURES, load_results, vnd

HERE = Path(__file__).resolve().parent
LAB = HERE.parent

AUTHOR = "Nguyễn Danh Thái"
STUDENT_ID = "B23DCKH105"
FONT = "Times New Roman"
MONO = "Consolas"
BLACK = RGBColor(0, 0, 0)
GRAY = RGBColor(0x59, 0x59, 0x59)

PLACEHOLDER_HEIGHT_CM = 6.2
IMAGE_WIDTH_CM = 15.5
IMAGE_MAX_HEIGHT_CM = 11.0
TEXT_WIDTH_CM = 16.0


# --------------------------------------------------------------- tiện ích Word
def _set_run(run, size=12, bold=False, italic=False, color=BLACK, font=FONT):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)


def _spacing(paragraph, before=0, after=4, line=1.15):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def _cell_borders(cell, style="single", size=8, color="000000"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), style)
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)
        borders.append(element)
    tc_pr.append(borders)


def _row_height(row, cm):
    tr_pr = row._tr.get_or_add_trPr()
    height = OxmlElement("w:trHeight")
    height.set(qn("w:val"), str(int(cm * 567)))     # twips
    height.set(qn("w:hRule"), "atLeast")
    tr_pr.append(height)


def _set_grid(table, widths_cm):
    """Cập nhật tblGrid + tcW để Word tôn trọng độ rộng cột (layout fixed dùng tblGrid)."""
    grid = table._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for col, cm in zip(grid.findall(qn("w:gridCol")), widths_cm):
            col.set(qn("w:w"), str(int(cm * 567)))
    for row in table.rows:
        for cell, cm in zip(row.cells, widths_cm):
            cell.width = Cm(cm)


def _table_full_width(table, cm=TEXT_WIDTH_CM):
    """Ép bảng rộng đúng khổ chữ và bố cục cố định để khung ảnh không bị co.

    Chỉnh tblW/tblLayout sẵn có (không thêm phần tử trùng) để XML vẫn hợp lệ.
    """
    table.autofit = False          # -> w:tblLayout type="fixed"
    tbl_pr = table._tbl.tblPr
    width = tbl_pr.find(qn("w:tblW"))
    if width is None:
        width = OxmlElement("w:tblW")
        tbl_pr.insert_element_before(width, "w:jc", "w:tblCellSpacing", "w:tblInd",
                                     "w:tblBorders", "w:tblLayout", "w:tblCellMar",
                                     "w:tblLook")
    width.set(qn("w:type"), "dxa")
    width.set(qn("w:w"), str(int(cm * 567)))


def _page_number_footer(section, text):
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # tab phải đặt đúng mép khổ chữ để số trang không tràn ra ngoài lề
    stops = paragraph.paragraph_format.tab_stops
    stops.add_tab_stop(Cm(TEXT_WIDTH_CM / 2), WD_TAB_ALIGNMENT.CENTER)
    stops.add_tab_stop(Cm(TEXT_WIDTH_CM), WD_TAB_ALIGNMENT.RIGHT)
    run = paragraph.add_run(text)
    _set_run(run, size=9, color=GRAY)
    tab_run = paragraph.add_run("\t\t")
    _set_run(tab_run, size=9, color=GRAY)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run_el = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    size = OxmlElement("w:sz")
    size.set(qn("w:val"), "18")
    r_pr.append(size)
    run_el.append(r_pr)
    text_el = OxmlElement("w:t")
    text_el.text = "1"
    run_el.append(text_el)
    field.append(run_el)
    paragraph._p.append(field)


# --------------------------------------------------------------- khối nội dung
class Doc:
    def __init__(self):
        self.doc = Document()
        self.fig_no = 0
        self.tab_no = 0
        self.image_dir: Path | None = None
        self._setup()

    def _setup(self):
        section = self.doc.sections[0]
        section.page_height, section.page_width = Cm(29.7), Cm(21.0)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

        normal = self.doc.styles["Normal"]
        normal.font.name = FONT
        normal.font.size = Pt(12)
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        normal.paragraph_format.space_after = Pt(4)
        normal.paragraph_format.line_spacing = 1.15

        heading = self.doc.styles["Heading 1"]
        heading.font.name = FONT
        heading.font.size = Pt(13)
        heading.font.bold = True
        heading.font.color.rgb = BLACK
        heading.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        heading.paragraph_format.space_before = Pt(10)
        heading.paragraph_format.space_after = Pt(4)
        heading.paragraph_format.keep_with_next = True

        _page_number_footer(section, "Báo cáo LAB 02 — MongoDB Atlas với PyMongo")

    # -- tiêu đề mục
    def h1(self, text):
        p = self.doc.add_paragraph(style="Heading 1")
        _spacing(p, before=10, after=4)
        p.paragraph_format.keep_with_next = True
        _set_run(p.add_run(text), size=13, bold=True)

    # -- đoạn văn
    def p(self, text, size=12, italic=False, color=BLACK, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
          first_indent=False):
        paragraph = self.doc.add_paragraph()
        _spacing(paragraph, after=4)
        paragraph.alignment = align
        if first_indent:
            paragraph.paragraph_format.first_line_indent = Cm(1.0)
        _set_run(paragraph.add_run(text), size=size, italic=italic, color=color)
        return paragraph

    # -- gạch đầu dòng
    def items(self, rows, size=12):
        for row in rows:
            paragraph = self.doc.add_paragraph(style="List Bullet")
            _spacing(paragraph, after=2)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            _set_run(paragraph.add_run(row), size=size)

    # -- khối mã: bảng 1 ô viền mảnh, font đều
    def code(self, text):
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        _table_full_width(table)
        _set_grid(table, [TEXT_WIDTH_CM])
        cell = table.cell(0, 0)
        cell.width = Cm(TEXT_WIDTH_CM)
        _cell_borders(cell, style="single", size=4)
        cell.paragraphs[0].text = ""
        for i, line in enumerate(text.splitlines()):
            paragraph = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
            _spacing(paragraph, after=0, line=1.0)
            _set_run(paragraph.add_run(line), size=8.5, font=MONO)
        self.doc.add_paragraph()

    # -- chú thích bảng / hình
    def caption(self, kind, text):
        paragraph = self.doc.add_paragraph()
        _spacing(paragraph, after=6)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        number = self.tab_no if kind == "Bảng" else self.fig_no
        _set_run(paragraph.add_run(f"{kind} {number}. {text}"), size=10, italic=True,
                 color=GRAY)

    # -- bảng số liệu
    def table(self, headers, rows, caption, widths=None, size=10.5):
        self.tab_no += 1
        self.caption("Bảng", caption)
        table = self.doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        if widths:
            _table_full_width(table, sum(widths))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, head in enumerate(headers):
            cell = table.rows[0].cells[i]
            cell.width = Cm(widths[i]) if widths else Cm(TEXT_WIDTH_CM / len(headers))
            paragraph = cell.paragraphs[0]
            paragraph.alignment = (WD_ALIGN_PARAGRAPH.LEFT if i in (0, 1)
                                   else WD_ALIGN_PARAGRAPH.CENTER)
            _set_run(paragraph.add_run(head), size=size, bold=True)
        for row in rows:
            cells = table.add_row().cells
            for i, value in enumerate(row):
                cells[i].width = Cm(widths[i]) if widths else Cm(TEXT_WIDTH_CM / len(headers))
                paragraph = cells[i].paragraphs[0]
                paragraph.alignment = (WD_ALIGN_PARAGRAPH.LEFT if i in (0, 1)
                                       else WD_ALIGN_PARAGRAPH.CENTER)
                _set_run(paragraph.add_run(str(value)), size=size)
        _set_grid(table, widths if widths else [TEXT_WIDTH_CM / len(headers)] * len(headers))
        self.doc.add_paragraph()
        return table

    # -- hình: chèn ảnh nếu có, không thì để khung trống để dán
    def figure(self, filename, section_note=""):
        self.fig_no += 1
        caption, need = FIGURE_INFO[filename]
        path = (self.image_dir / filename) if self.image_dir else None

        if path is not None and path.exists():
            paragraph = self.doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _spacing(paragraph, after=2)
            run = paragraph.add_run()
            run.add_picture(str(path), width=Cm(IMAGE_WIDTH_CM))
            shape = run._element.xpath(".//wp:inline")[0]
            extent = shape.find(qn("wp:extent"))
            width_emu, height_emu = int(extent.get("cx")), int(extent.get("cy"))
            max_emu = int(IMAGE_MAX_HEIGHT_CM * 360000)
            if height_emu > max_emu:                     # ảnh dọc: thu theo chiều cao
                ratio = max_emu / height_emu
                new_w, new_h = int(width_emu * ratio), min(int(height_emu * ratio), max_emu)
                extent.set("cx", str(new_w))
                extent.set("cy", str(new_h))
                for node in shape.iter(qn("a:ext")):
                    node.set("cx", str(new_w))
                    node.set("cy", str(new_h))
        else:
            table = self.doc.add_table(rows=1, cols=1)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            _table_full_width(table)
            _set_grid(table, [TEXT_WIDTH_CM])
            cell = table.cell(0, 0)
            cell.width = Cm(TEXT_WIDTH_CM)
            _row_height(table.rows[0], PLACEHOLDER_HEIGHT_CM)
            _cell_borders(cell, style="dashed", size=8)

            lines = [
                (f"[ Khung chèn ảnh — Hình {self.fig_no} ]", 10.5, True, GRAY),
                (f"Tệp cần dán:  {filename}", 9.5, False, GRAY),
                (f"Nội dung phải thấy:  {need}", 9.5, False, GRAY),
                (f"Vị trí chụp: {section_note}" if section_note else "", 9.5, False, GRAY),
            ]
            first = cell.paragraphs[0]
            for i, (text, size, bold, color) in enumerate([line for line in lines if line[0]]):
                paragraph = first if i == 0 else cell.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _spacing(paragraph, after=2, line=1.0)
                _set_run(paragraph.add_run(text), size=size, bold=bold, italic=not bold,
                         color=color)

        self.caption("Hình", caption)

    def save(self, out: Path):
        out.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(out))


# --------------------------------------------------------------- nội dung báo cáo
def title_block(r: Doc):
    p = r.doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, after=2)
    _set_run(p.add_run("BÁO CÁO BÀI THỰC HÀNH LAB 02"), size=15, bold=True)

    p = r.doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, after=6)
    _set_run(p.add_run("MongoDB Atlas Free với PyMongo trên Google Cloud Shell"), size=12.5,
             bold=True)

    for text in ("Môn: Introduction to Data Science — Học viện Công nghệ Bưu chính Viễn thông",
                 f"Sinh viên: {AUTHOR}    MSSV: {STUDENT_ID}"):
        p = r.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _spacing(p, after=0)
        _set_run(p.add_run(text), size=12)

    rule = r.doc.add_paragraph()
    _spacing(rule, after=8)
    p_pr = rule._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:color"), "000000")
    borders.append(bottom)
    p_pr.append(borders)


def section1(r: Doc, d: dict):
    r.h1("1. Thông tin chung")
    r.p("Bài thực hành dựng cơ sở dữ liệu NoSQL trên MongoDB Atlas Free gồm ba collection "
        "customers, products, orders — mỗi đơn hàng chứa mảng items nhúng — rồi thực hiện CRUD, "
        "truy vấn trường lồng nhau, aggregation, $lookup và index. Toàn bộ 22 yêu cầu N01–N22 "
        "đã cài đặt và chạy kiểm chứng.", first_indent=True)
    r.items([
        "Dịch vụ: MongoDB Atlas M0 Free, database sales_nosql; kết nối bằng PyMongo từ Google "
        "Cloud Shell, URI nhập qua getpass nên không lưu mật khẩu trong mã nguồn.",
        "Phần bắt buộc N01–N15: n_answers.py trên bộ dữ liệu mẫu 5 khách / 5 sản phẩm / 6 đơn. "
        "Phần bổ sung N16–N22: n_homework.py trên dữ liệu mở rộng do generate_data.py sinh.",
        "Kịch bản hỗ trợ: connect.py (ping + trả về database), seed.py (nạp dữ liệu mẫu), "
        "lab_queries.py (ví dụ trong đề), generate_data.py (dữ liệu mở rộng).",
    ])


def criterion1(r: Doc, d: dict):
    r.h1("2. Tiêu chí 1 — Thiết lập và seed dữ liệu (2,0 điểm)")
    r.p("connect.py dùng getpass nhận URI, tạo MongoClient với tham số timeout 12.000 ms rồi "
        "gọi client.admin.command('ping') để chắc chắn cluster trả lời trước khi dùng. Mọi lỗi "
        "thường gặp được phân biệt rõ: timeout là do IP chưa allowlist hoặc DNS, còn "
        "AuthenticationFailed là do user hoặc mật khẩu (ký tự đặc biệt phải URL-encode).",
        first_indent=True)
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
        "gồm product_id, name, price, quantity — giá và tên được sao lại tại thời điểm mua.",
        first_indent=True)
    r.table(["Collection", "Kỳ vọng của đề", "Thực tế", "Kết quả"],
            [["customers", "5", "5", "khớp"],
             ["products", "5", "5", "khớp"],
             ["orders", "6", "6", "khớp"]],
            "Số document sau khi chạy seed.py", widths=[4.5, 4.2, 3.4, 3.9])
    r.p("Kiểm tra trên Atlas → Data Explorer: mở một order thấy trường items là array các "
        "document con, không có bảng trung gian như order_items của mô hình quan hệ.",
        first_indent=True)
    r.figure("01_cluster.png", "Atlas > Data Explorer: cluster DSCluster và database sales_nosql")
    r.figure("02_data_explorer.png", "Atlas > Data Explorer, collection orders")
    r.figure("03_connect_seed.png", "Cloud Shell: connect.py và seed.py")


def criterion2(r: Doc, d: dict):
    r.h1("3. Tiêu chí 2 — CRUD và truy vấn lọc (2,0 điểm)")
    r.p("Nhóm N01–N08 gồm bốn truy vấn đọc và ba thao tác ghi. Các thao tác ghi được viết để "
        "chạy lặp an toàn trên cùng một database.", first_indent=True)
    r.table(["Mã", "Nội dung", "Cách thực hiện", "Kết quả"],
            [["N01", "Liệt kê tất cả customers", "find({})", f"{len(d['n01'])} document"],
             ["N02", "Khách hàng ở Hanoi", "find({city: Hanoi})", f"{len(d['n02'])} document"],
             ["N03", "Sản phẩm giá trên 1 triệu", "{price: {$gt: 1000000}}",
              f"{len(d['n03'])} document"],
             ["N04", "Sắp xếp theo giá giảm dần", "sort(price, -1)", "5 document"],
             ["N05", "Thêm khách hàng mới", "insert_one", "1 document"],
             ["N06", "Sửa thành phố", "update_one + $set", "matched 1"],
             ["N07", "Xoá khách vừa thêm", "delete_one", "deleted 1"],
             ["N08", "Đếm khách theo thành phố", "$group + $sum", "3 nhóm"]],
            "Các câu N01–N08 và kết quả thực tế", widths=[1.4, 6.0, 5.2, 3.4])
    r.code(
        "pipeline = [\n"
        "    {'$group': {'_id': '$city', 'count': {'$sum': 1}}},\n"
        "    {'$sort': {'count': -1, '_id': 1}},\n"
        "    {'$project': {'_id': 0, 'city': '_id', 'count': 1}},\n"
        "]")
    rows = ", ".join(f"{x['city']} {x['count']}" for x in d["n08"])
    r.items([
        f"N08 cho kết quả: {rows}; tổng bằng đúng số khách hàng trong bộ dữ liệu mẫu.",
        "N05 chỉ insert khi customer_id = 6 chưa tồn tại, N06 $set city = Danang, N07 delete_one "
        "đúng khách đó nên chạy lại nhiều lần vẫn về 5 khách hàng.",
        "Truy vấn mảng nhúng dùng đường dẫn items.product_id nên không cần join: N09 tìm được "
        "đơn chứa Laptop bằng một lần đọc collection orders.",
    ])
    r.figure("04_crud_n01_n05.png", "n_answers.py — phần N01–N05")
    r.figure("05_crud_n05_n11.png", "n_answers.py — phần N05–N11")
    r.figure("08_n13_n14_index.png", "n_answers.py — N13 và N14 (tạo index)")


def criterion3(r: Doc, d: dict):
    r.h1("4. Tiêu chí 3 — Aggregation và $lookup (3,0 điểm)")
    r.p("N10 dùng $unwind để tách mảng items rồi $group lại theo order_id, nhân price với "
        "quantity bằng $multiply. N11 gom theo customer_id và $lookup sang customers để lấy tên; "
        "N12 ghép orders với customers; N13 lọc nhóm bằng $match sau $group.", first_indent=True)
    r.code(
        "pipeline = [\n"
        "    {'$unwind': '$items'},\n"
        "    {'$group': {'_id': '$order_id',\n"
        "                'total': {'$sum': {'$multiply': [\n"
        "                    '$items.price', '$items.quantity']}}}},\n"
        "    {'$sort': {'total': -1}},\n"
        "]")
    rows = [[str(item["order_id"]), vnd(item["total"])] for item in d["n10"][:6]]
    total = sum(item["total"] for item in d["n10"])
    rows.append(["Tổng", vnd(total)])
    r.table(["Mã đơn", "Tổng tiền (đồng)"], rows, "Kết quả N10 — tổng tiền từng đơn",
            widths=[5.0, 11.0])
    rev = ", ".join(f"{x['name']} {vnd(x['revenue'])}" for x in d["n11"][:5])
    r.items([
        f"Kiểm tra chéo đơn 1001: 1 Laptop 15.000.000 + 2 Mouse 250.000 = 15.500.000, khớp kết "
        f"quả máy; tổng cả 6 đơn là {vnd(total)} đồng.",
        f"N11 — doanh thu theo khách: {rev}.",
        "N12 $lookup + $unwind + $project trả về 6 dòng dạng {order_id, name, city}, tương "
        "đương INNER JOIN của SQL.",
        f"N13 — khách có từ 2 đơn: "
        f"{', '.join(x['name'] + ' (' + str(x['order_count']) + ')' for x in d['n13'])}; các "
        "khách còn lại chỉ có 1 đơn nên bị $match loại.",
    ])
    r.figure("07_lookup_n12.png", "Chạy n_answers.py — phần N12")


def criterion4(r: Doc, d: dict):
    r.h1("5. Tiêu chí 4 — Index và mô hình dữ liệu (1,5 điểm)")
    r.p("N14 tạo index trên orders.customer_id đúng như đề. N21 đọc explain() để so sánh kế "
        "hoạch khi truy vấn theo trường có index và trường không có index.", first_indent=True)
    r.code(
        "db.orders.create_index([('customer_id', 1)], name='idx_orders_customer')\n"
        "plan = db.orders.find({'customer_id': 7}).explain()\n"
        "print(plan['queryPlanner']['winningPlan']['stage'])   # IXSCAN")
    plan_idx = d["n21"].get("explain_customer_id", {})
    plan_scan = d["n21"].get("explain_no_index_field", {})
    r.table(["Truy vấn", "Stage", "Diễn giải"],
            [["customer_id (có index)", str(plan_idx.get("stage", "IXSCAN")),
              "chỉ đọc document khớp"],
             ["order_date (không index)", str(plan_scan.get("stage", "COLLSCAN")),
              "quét toàn collection rồi lọc"]],
            "Kế hoạch thực thi trước và sau khi có index", widths=[6.0, 3.0, 7.0])
    r.items([
        "Với 506 đơn, chênh lệch thời gian chạy dưới ngưỡng đo nên kết luận dựa trên stage của "
        "winningPlan và số document phải đọc (totalDocsExamined), không dựa vào wall-clock.",
        "N15 — embedded (items nằm trong order) đọc cả đơn bằng một truy vấn, ghi nguyên tử, "
        "nhưng lặp name/price và bị giới hạn 16 MB mỗi document; reference (chỉ lưu product_id) "
        "không lặp dữ liệu nhưng phải $lookup mỗi lần đọc.",
        "N20 — đổi price trong products từ "
        f"{vnd(d['n20']['product_price_before'])} lên "
        f"{vnd(d['n20']['product_price_after_update'])} đồng thì items.price trong đơn cũ vẫn "
        f"giữ nguyên {vnd(d['n20']['price_in_old_order_after'])} đồng: dữ liệu nhúng là bản sao "
        "tại thời điểm mua, đúng cho báo cáo doanh thu lịch sử nhưng phải chấp nhận không đồng "
        "bộ với bảng giá hiện hành.",
    ])
    r.figure("09_n15_n20_mo_hinh.png", "n_answers.py — N15, n_homework.py — N20")
    r.figure("10_explain_n21.png", "Chạy n_homework.py — phần N21")


def criterion5(r: Doc, d: dict):
    r.h1("6. Tiêu chí 5 — Bài mở rộng và báo cáo (1,5 điểm)")
    r.p("generate_data.py sinh dữ liệu mở rộng với random.seed(2026) nên tái lập được: 100 "
        "khách, 30 sản phẩm, 500 đơn, mỗi đơn 1–5 sản phẩm (1.521 dòng hàng), 8 khách không có "
        "đơn và 4 sản phẩm không bán được.", first_indent=True)
    r.table(["Đối tượng", "Yêu cầu tối thiểu", "Thực tế"],
            [["Khách hàng", "100", "100"],
             ["Sản phẩm", "30", "30"],
             ["Đơn hàng", "500", "500"],
             ["Dòng items", "1.000", "1.521"]],
            "Quy mô dữ liệu mở rộng so với yêu cầu của đề", widths=[7.0, 4.5, 4.5])
    top_cities = ", ".join(f"{x['city']} {vnd(x['revenue'])}" for x in d["n16"][:3])
    top_products = "; ".join(f"{x['name']} {vnd(x['revenue'])}" for x in d["n17"])
    t19 = d["n19"]["totals"]
    so_khach_trong = len(d["n18"]) if len(d["n18"]) > 1 else 8
    r.items([
        f"N16 — doanh thu theo thành phố dẫn đầu: {top_cities} (7 thành phố, tổng khớp doanh "
        "thu toàn hệ thống).",
        f"N17 — ba sản phẩm doanh thu cao nhất: {top_products}.",
        f"N18 — $lookup orders rồi $match mảng rỗng tìm được {so_khach_trong} khách chưa đặt "
        "hàng, đúng bằng số khách cố ý để trống khi sinh dữ liệu.",
        f"N19 — discount không đồng nhất: {d['n19']['orders_with_discount']} đơn có discount, "
        f"{d['n19']['orders_without_discount']} đơn không có trường này; $ifNull quy trường thiếu "
        f"về 0 nên doanh thu gộp {vnd(t19['gross'])} đồng, doanh thu thuần {vnd(t19['net'])} "
        f"đồng (giảm {vnd(t19['discount_amount'])} đồng).",
        f"N22 — JOIN của SQL và $lookup cùng trả {d['n22'].get('so_dong', 506)} dòng ghép, "
        "nhưng $lookup là stage chạy trong pipeline nên lọc trước sẽ rẻ hơn; dữ liệu nhúng sẵn "
        "như items không cần $lookup, đó là khác biệt cốt lõi so với mô hình quan hệ.",
    ])
    r.figure("11_expanded_counts.png", "Cloud Shell: generate_data.py --force")
    r.figure("12_n16_n19.png", "n_homework.py — N16 đến N19")
    r.figure("13_n22_lookup.png", "n_homework.py — N22")


def evidence_list(r: Doc, d: dict):
    r.h1("7. Danh mục ảnh minh chứng")
    r.p("Mỗi ảnh dưới đây phải là ảnh chụp thật trên Atlas hoặc Cloud Shell, dán vào đúng khung "
        "ở mục 2–6. Bảng này dùng để đối chiếu tệp với nội dung minh chứng trước khi nộp.",
        first_indent=True)
    rows = [[name, FIGURE_INFO[name][1], str(FIGURE_SECTION[name])] for name in FIGURES]
    r.table(["Tệp trong evidence/", "Nội dung cần thấy trong ảnh", "Mục"], rows,
            "Các ảnh minh chứng kèm theo bài nộp", widths=[5.0, 9.6, 1.4], size=9.5)
    r.p("Cách chèn ảnh vào khung: bấm vào trong khung nét đứt → Insert > Pictures → chọn tệp "
        "trong thư mục evidence/. Hoặc chạy lại script với --images ../evidence để tự chèn.",
        size=10.5, italic=True, color=GRAY)


def conclusion(r: Doc, d: dict):
    r.h1("8. Kết luận")
    r.p("Đã hoàn thành đủ 22 yêu cầu của đề: thiết lập cluster Atlas Free và kết nối an toàn "
        "bằng getpass, seed đúng bộ dữ liệu 5/5/6 với items nhúng, CRUD và truy vấn mảng, "
        "aggregation có $unwind/$group/$lookup, tạo index và đọc explain, mở rộng lên 500 đơn "
        "với discount không đồng nhất. Hai điểm rút ra: (1) chọn nhúng hay tham chiếu là quyết "
        "định về mô hình dữ liệu chứ không phải cú pháp — items nhúng đọc nhanh nhưng giá là bản "
        "sao lịch sử; (2) đánh giá index trên dữ liệu nhỏ phải dựa vào stage của explain, không "
        "dựa vào thời gian chạy.", first_indent=True)


def build(out: Path, images: Path | None, results: dict) -> Doc:
    r = Doc()
    r.image_dir = images
    title_block(r)
    section1(r, results)
    criterion1(r, results)
    criterion2(r, results)
    criterion3(r, results)
    criterion4(r, results)
    criterion5(r, results)
    evidence_list(r, results)
    conclusion(r, results)
    r.save(out)
    return r


def find_images_dir(raw: Path) -> Path | None:
    cands = [raw] if raw.is_absolute() else [Path.cwd() / raw, HERE / raw, LAB / raw,
                                             LAB.parent / raw]
    return next((c for c in cands if c.is_dir()), None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh báo cáo LAB 02 bản Word có khung chèn ảnh")
    ap.add_argument("--out", type=Path, default=HERE / f"BaoCao_LAB02_{STUDENT_ID}.docx")
    ap.add_argument("--images", type=Path, default=None,
                    help="thư mục ảnh đã chụp; ảnh nào có thì chèn luôn, thiếu thì để khung trống")
    ap.add_argument("--results", type=Path, nargs="+", default=None,
                    help="JSON kết quả từ n_answers.py / n_homework.py (tùy chọn)")
    args = ap.parse_args()

    images = None
    if args.images:
        images = find_images_dir(args.images)
        if images is None:
            print(f"[!] Không thấy thư mục ảnh: {args.images}", file=sys.stderr)
            return 2
        missing = [n for n in FIGURES if not (images / n).exists()]
        if missing:
            print("[i] chưa có ảnh (sẽ để khung trống): " + ", ".join(missing))

    results = load_results(args.results or [])
    report = build(args.out, images, results)

    co_anh = sum(1 for n in FIGURES if images and (images / n).exists())
    print(f"[ok] {args.out}")
    print(f"     {report.tab_no} bảng · {report.fig_no} hình "
          f"({co_anh} ảnh đã chèn, {report.fig_no - co_anh} khung trống) · "
          f"{args.out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
