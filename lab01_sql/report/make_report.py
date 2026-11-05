#!/usr/bin/env python3
"""Sinh BÁO CÁO ĐỒ ÁN MÔN HỌC (LAB 01 — SQL với SQLite) trực tiếp ra PDF.

Khác với `make_pdf.py` (bản tóm tắt 3 trang để nộp kèm), script này dựng báo cáo theo **văn
phong đồ án** thông thường:

    Trang bìa → Tóm tắt → Mục lục → Danh mục từ viết tắt → Danh mục hình vẽ →
    Danh mục bảng biểu → Chương 1…6 → Tài liệu tham khảo → Phụ lục A–C

Không cần TeX (chỉ fpdf2 + Pillow), chạy được trên máy chỉ có Python:

    pip install -r ../evidence/requirements.txt      # fpdf2 + pillow
    python3 make_report.py
    python3 make_report.py --out BaoCao_LAB01.pdf --no-images

Số liệu trong báo cáo lấy từ lần chạy thật của `build_db.py`, `run_sql.py`,
`generate_data.py`; ảnh lấy từ pipeline `../evidence/make_evidence.py`.
Mục lục, danh mục hình/bảng và số trang được tính tự động (chạy 2–3 lượt để hội tụ).
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from datetime import date
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
EVID = LAB / "evidence"
SQL_DIR = LAB / "sql"

# ---------------------------------------------------------------- thông tin đồ án
AUTHOR = "Nguyễn Danh Thái"
STUDENT_ID = "B23DCKH105"
CLASS_NAME = "...................."
INSTRUCTOR = "...................."
SUBJECT = "Introduction to Data Science"
SCHOOL = "HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG"
FACULTY = "KHOA CÔNG NGHỆ THÔNG TIN"
REPORT_TITLE = ("XÂY DỰNG CƠ SỞ DỮ LIỆU QUAN HỆ VÀ KHAI THÁC\nDỮ LIỆU BÁN HÀNG TRÊN SQLITE\nVỚI GOOGLE CLOUD SHELL")
REPORT_SUBTITLE = "Báo cáo đồ án môn học — LAB 01"

# ---------------------------------------------------------------- màu & cỡ chữ
INK = (20, 22, 26)
DIM = (100, 106, 116)
ACCENT = (15, 62, 120)
RULE = (170, 178, 190)
SHADE = (243, 245, 248)
CODE_BG = (246, 246, 248)

BODY_SIZE = 12.0
LINE_H = 6.2
INDENT = 10.0


def _strip_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt (dùng cho khối mã: font mono trong bộ font này thiếu một số glyph)."""
    text = text.replace("đ", "d").replace("Đ", "D")
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if not unicodedata.combining(c))


class Report(FPDF):
    def __init__(self, with_images: bool, front: dict | None = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.with_images = with_images
        self.front = front or {"figures": [], "tables": []}
        self.figures: list[tuple[str, str, int]] = []
        self.tables: list[tuple[str, str, int]] = []
        self.chapter_label = "1"
        self.fig_no = 0
        self.tab_no = 0
        self.sec_no = 0
        self.sub_no = 0

        self.set_margins(left=30, top=22, right=20)
        self.set_auto_page_break(auto=True, margin=20)
        self.alias_nb_pages()

        self.add_font("Serif", "", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
        self.add_font("Serif", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
        self.add_font("Sans", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        self.add_font("Sans", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        self.add_font("Mono", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
        self.add_font("Mono", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
        self.set_title("Báo cáo đồ án LAB 01 - SQL với SQLite")
        self.set_author(f"{AUTHOR} - {STUDENT_ID}")
        self.set_subject(SUBJECT)
        self.set_creator("make_report.py (fpdf2)")

    # ------------------------------------------------------------ khung trang
    def footer(self) -> None:
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_y(-13)
        self.set_font("Serif", "", 9)
        self.set_text_color(*DIM)
        self.cell(0, 5, f"Báo cáo đồ án — LAB 01: SQL với SQLite", align="L")
        self.set_y(-13)
        self.cell(0, 5, f"Trang {self.page_no()}", align="R")
        self.set_text_color(*INK)
        self.set_font("Serif", "", BODY_SIZE)

    def need(self, h: float) -> None:
        if self.get_y() + h > self.h - self.b_margin:
            self.add_page()

    # ------------------------------------------------------------ tiêu đề
    def chapter(self, num: str, title: str) -> None:
        self.add_page()
        self.start_section(f"CHƯƠNG {num}. {title}", 0)
        self.chapter_label = num
        self.fig_no = 0
        self.tab_no = 0
        self.sec_no = 0
        self.sub_no = 0
        self.ln(4)
        self.set_font("Sans", "B", 15)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 8, f"CHƯƠNG {num}. {title.upper()}", align="C",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.5)
        y = self.get_y() + 1
        self.line(self.l_margin + 35, y, self.w - self.r_margin - 35, y)
        self.ln(7)
        self.set_text_color(*INK)

    def front_heading(self, title: str) -> None:
        """Tiêu đề khối đầu báo cáo (mục lục, danh mục…)."""
        self.start_section(title, 0)
        self.set_font("Sans", "B", 14)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 8, title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_text_color(*INK)

    def h2(self, title: str) -> None:
        self.sec_no += 1
        self.sub_no = 0
        label = f"{self.chapter_label}.{self.sec_no}"
        self.need(24)
        self.ln(2.5)
        self.start_section(f"{label}. {title}", 1)
        self.set_font("Sans", "B", 12.5)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 6.4, f"{label}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.6)
        self.set_text_color(*INK)

    def h3(self, title: str) -> None:
        self.sub_no += 1
        label = f"{self.chapter_label}.{self.sec_no}.{self.sub_no}"
        self.need(20)
        self.ln(1.4)
        self.set_font("Sans", "B", 11.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 6, f"{label}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.2)

    # ------------------------------------------------------------ văn bản
    def p(self, text: str, indent: bool = True, size: float = BODY_SIZE,
          align: str = "J", lh: float = LINE_H) -> None:
        self.set_font("Serif", "", size)
        self.set_text_color(*INK)
        x = self.l_margin + (INDENT if indent else 0)
        w = self.epw - (INDENT if indent else 0)
        self.set_x(x)
        self.multi_cell(w, lh, text, align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.4)

    def lead(self, bold: str, text: str) -> None:
        """Đoạn mở đầu bằng cụm in đậm (kiểu 'Kết luận. ...')."""
        self.need(12)
        self.set_font("Serif", "B", BODY_SIZE)
        self.set_text_color(*INK)
        self.set_x(self.l_margin + INDENT)
        self.write(LINE_H, bold + " ")
        self.set_font("Serif", "", BODY_SIZE)
        self.write(LINE_H, text)
        self.ln(LINE_H + 1.4)

    def bullets(self, items: list[str], size: float = BODY_SIZE, lh: float = LINE_H) -> None:
        self.set_font("Serif", "", size)
        for item in items:
            self.need(lh * 2)
            x0 = self.l_margin + INDENT
            self.set_x(x0)
            self.cell(5, lh, "–", align="L")
            self.set_x(x0 + 5)
            self.multi_cell(self.epw - INDENT - 5, lh, item, align="J",
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(0.9)
        self.ln(0.8)

    def numbered(self, items: list[str], size: float = BODY_SIZE, lh: float = LINE_H) -> None:
        self.set_font("Serif", "", size)
        for i, item in enumerate(items, 1):
            self.need(lh * 2)
            x0 = self.l_margin + INDENT
            self.set_x(x0)
            self.cell(7, lh, f"{i}.", align="L")
            self.set_x(x0 + 7)
            self.multi_cell(self.epw - INDENT - 7, lh, item, align="J",
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(0.9)
        self.ln(0.8)

    def note(self, title: str, text: str) -> None:
        """Ô ghi chú có viền (nhấn mạnh nhận xét quan trọng)."""
        self.need(24)
        self.set_font("Serif", "", 11)
        lines_h = len(self.multi_cell(self.epw - 10, 5.6, text, dry_run=True, output="LINES"))
        h = lines_h * 5.6 + 11
        y = self.get_y()
        self.set_fill_color(*SHADE)
        self.set_draw_color(*RULE)
        self.set_line_width(0.25)
        self.rect(self.l_margin, y, self.epw, h, style="DF")
        self.set_fill_color(70, 110, 170)
        self.rect(self.l_margin, y, 1.6, h, style="F")
        self.set_xy(self.l_margin + 5, y + 2.5)
        self.set_font("Sans", "B", 10)
        self.set_text_color(*ACCENT)
        self.cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(self.l_margin + 5)
        self.set_font("Serif", "", 11)
        self.set_text_color(*INK)
        self.multi_cell(self.epw - 10, 5.6, text, align="J", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(y + h + 3)

    # ------------------------------------------------------------ khối mã
    def code(self, text: str, size: float = 8.0, ascii_only: bool = True) -> None:
        if ascii_only:
            text = _strip_accents(text)
        self.set_font("Mono", "", size)
        char_w = self.get_string_width("M")
        pad = 2.6
        usable = self.epw - 2 * pad
        max_chars = max(20, int(usable / char_w)) if char_w else 100
        lines: list[str] = []
        for raw in text.rstrip("\n").splitlines():
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
        self.need(14)
        for line in lines:
            if self.get_y() + lh > self.h - self.b_margin:
                self.add_page()
            y = self.get_y()
            self.set_fill_color(*CODE_BG)
            self.rect(self.l_margin, y, self.epw, lh, style="F")
            self.set_xy(self.l_margin + pad, y + lh * 0.12)
            self.set_text_color(*INK)
            self.cell(usable, lh, self._escape(line), align="L")
            self.set_y(y + lh)
        self.ln(2.4)
        self.set_font("Serif", "", BODY_SIZE)

    @staticmethod
    def _escape(line: str) -> str:
        return line.replace("\t", "    ")

    # ------------------------------------------------------------ bảng
    def table(self, headers: list[str], rows: list[list[str]], widths: list[float],
              caption: str | None = None, font_size: float = 9.0,
              align_right: set[int] | None = None, header_align: str = "C") -> None:
        align_right = align_right or set()
        total = sum(widths)
        if total > self.epw:
            k = self.epw / total
            widths = [w * k for w in widths]
        row_h = font_size * 0.52
        need = row_h * (min(len(rows), 6) + 2) + (8 if caption else 0)
        self.need(need)

        if caption:
            self.tab_no += 1
            label = f"Bảng {self.chapter_label}.{self.tab_no}"
            self.set_font("Sans", "B", 10)
            self.set_text_color(*INK)
            self.multi_cell(0, 5.4, f"{label}. {caption}", align="C",
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1.6)
            self.tables.append((label, caption, self.page_no()))

        def draw_header() -> None:
            self.set_font("Sans", "B", font_size)
            self.set_fill_color(*SHADE)
            self.set_draw_color(*RULE)
            self.set_line_width(0.2)
            for i, head in enumerate(headers):
                self.cell(widths[i], row_h + 1.6, head, border="1", align=header_align, fill=True)
            self.ln(row_h + 1.6)

        draw_header()
        self.set_font("Serif", "", font_size)
        for r_i, row in enumerate(rows):
            if self.get_y() + row_h + 1.0 > self.h - self.b_margin:
                self.add_page()
                draw_header()
                self.set_font("Serif", "", font_size)
            for i, cell in enumerate(row):
                self.cell(widths[i], row_h + 1.0, cell, border="1",
                          align="R" if i in align_right else "L")
            self.ln(row_h + 1.0)
        self.ln(3.0)
        self.set_font("Serif", "", BODY_SIZE)

    # ------------------------------------------------------------ hình
    def figure(self, path: Path, caption: str, max_h: float = 78.0) -> None:
        if not (self.with_images and path.exists()):
            return
        from PIL import Image

        with Image.open(path) as im:
            iw, ih = im.size
        draw_w = self.epw
        draw_h = draw_w * ih / iw
        if draw_h > max_h:
            draw_h = max_h
            draw_w = draw_h * iw / ih
        self.need(draw_h + 14)
        x = self.l_margin + (self.epw - draw_w) / 2
        y = self.get_y()
        self.image(str(path), x=x, y=y, w=draw_w, h=draw_h)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.rect(x, y, draw_w, draw_h)
        self.set_xy(self.l_margin, y + draw_h + 1.4)
        self.fig_no += 1
        label = f"Hình {self.chapter_label}.{self.fig_no}"
        self.set_font("Sans", "B", 10)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, f"{label}. {caption}", align="C",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.figures.append((label, caption, self.page_no()))
        self.ln(4)
        self.set_font("Serif", "", BODY_SIZE)

    # ------------------------------------------------------------ sơ đồ ERD
    def erd(self, caption: str) -> None:
        self.need(74)
        x0, y0 = self.l_margin + 4, self.get_y() + 2
        bw, bh = 42, 34
        gap = (self.epw - 8 - 3 * bw) / 2

        def box(x: float, y: float, title: str, fields: list[str], pk: str) -> None:
            self.set_fill_color(238, 243, 251)
            self.set_draw_color(60, 90, 140)
            self.set_line_width(0.35)
            self.rect(x, y, bw, bh, style="DF")
            self.set_fill_color(60, 90, 140)
            self.rect(x, y, bw, 7, style="F")
            self.set_xy(x, y)
            self.set_font("Sans", "B", 8.6)
            self.set_text_color(255, 255, 255)
            self.cell(bw, 7, title, align="C")
            self.set_text_color(*INK)
            yy = y + 8.6
            self.set_font("Mono", "", 7.4)
            for f in fields:
                self.set_xy(x + 2, yy)
                txt = f"* {f}" if f == pk else f"   {f}"
                self.cell(bw - 4, 4.4, _strip_accents(txt))
                yy += 4.6

        xt = [x0, x0 + bw + gap, x0 + 2 * (bw + gap)]
        box(xt[0], y0 + 12, "customers", ["customer_id", "name", "city"], "customer_id")
        box(xt[1], y0 + 12, "orders", ["order_id", "customer_id", "order_date"], "order_id")
        box(xt[2], y0 + 12, "order_items", ["order_id", "product_id", "quantity"], "order_id")
        box(xt[2], y0 + 12 + bh + 12, "products", ["product_id", "name", "category", "price"],
            "product_id")

        def arrow(x1: float, y1: float, x2: float, y2: float, label: str, dy: float = -3) -> None:
            self.set_draw_color(60, 90, 140)
            self.set_line_width(0.4)
            self.line(x1, y1, x2, y2)
            # đầu mũi tên
            import math

            ang = math.atan2(y2 - y1, x2 - x1)
            for d in (0.45, -0.45):
                self.line(x2, y2, x2 - 3 * math.cos(ang + d), y2 - 3 * math.sin(ang + d))
            self.set_font("Sans", "", 7.6)
            self.set_text_color(*DIM)
            self.set_xy((x1 + x2) / 2 - 4, (y1 + y2) / 2 + dy)
            self.cell(8, 3.6, label, align="C")
            self.set_text_color(*INK)

        arrow(xt[0] + bw, y0 + 12 + bh / 2, xt[1], y0 + 12 + bh / 2, "1 : N")
        arrow(xt[1] + bw, y0 + 12 + bh / 2, xt[2], y0 + 12 + bh / 2, "1 : N")
        arrow(xt[2] + bw * 0.55, y0 + 12 + bh, xt[2] + bw * 0.55, y0 + 12 + bh + 12, "1 : N", 0)

        self.set_y(y0 + 12 + 2 * bh + 16)
        self.fig_no += 1
        label = f"Hình {self.chapter_label}.{self.fig_no}"
        self.set_font("Sans", "B", 10)
        self.multi_cell(0, 5.2, f"{label}. {caption}", align="C",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.figures.append((label, caption, self.page_no()))
        self.ln(4)
        self.set_font("Serif", "", BODY_SIZE)

    # ------------------------------------------------------------ danh mục
    def list_entry(self, text: str, page: int, size: float = 10.4) -> None:
        """Một dòng trong danh mục hình/bảng: tự xuống dòng khi caption dài."""
        self.set_font("Serif", "", size)
        avail = self.epw
        num = str(page)
        w_num = self.get_string_width(num) + 2
        text_w = avail - w_num - 6
        lines = self.multi_cell(text_w, 5.6, text, dry_run=True, output="LINES")
        line_h = 5.6
        for i, line in enumerate(lines):
            self.set_x(self.l_margin)
            if i == len(lines) - 1:
                w_line = self.get_string_width(line) + 1
                w_dots = max(2.0, text_w - w_line)
                self.cell(w_line, line_h, line)
                self.cell(w_dots, line_h,
                          "." * int(w_dots / max(0.1, self.get_string_width(".")) - 1),
                          align="R")
                self.cell(w_num, line_h, num, align="R",
                          new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                self.multi_cell(text_w, line_h, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.0)

    # ------------------------------------------------------------ mục lục
    def render_toc(self, pdf: "Report", outline) -> None:
        pdf.set_font("Sans", "B", 14)
        pdf.set_text_color(*ACCENT)
        pdf.cell(0, 9, "MỤC LỤC", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)
        for sec in outline:
            ind = 0 if sec.level == 0 else 9
            pdf.set_font("Sans" if sec.level == 0 else "Serif",
                         "B" if sec.level == 0 else "", 10.2 if sec.level == 0 else 9.8)
            pdf.set_text_color(*(INK if sec.level == 0 else (60, 66, 76)))
            page = str(sec.page_number)
            name = sec.name
            avail = pdf.epw - ind
            w_name = pdf.get_string_width(name)
            w_page = pdf.get_string_width(page)
            w_dots = max(2.0, avail - w_name - w_page - 6)
            link = pdf.add_link(page=sec.page_number)
            pdf.set_x(pdf.l_margin + ind)
            pdf.cell(w_name + 2, 5.3, name, link=link)
            pdf.cell(w_dots, 5.3, "." * int(w_dots / max(0.1, pdf.get_string_width(".")) - 1),
                     align="R", link=link)
            pdf.cell(w_page + 4, 5.3, page, align="R", link=link,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*INK)


# =====================================================================================
#  NỘI DUNG BÁO CÁO
# =====================================================================================
def cover(r: Report) -> None:
    r.add_page()
    r.set_font("Sans", "", 11)
    r.set_text_color(*INK)
    r.multi_cell(0, 5.6, "BỘ THÔNG TIN VÀ TRUYỀN THÔNG", align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.set_font("Sans", "B", 12.5)
    r.multi_cell(0, 6.4, SCHOOL, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.set_font("Sans", "B", 12)
    r.multi_cell(0, 6.2, FACULTY, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.ln(6)
    r.set_draw_color(*ACCENT)
    r.set_line_width(0.6)
    y = r.get_y()
    r.line(r.l_margin + 20, y, r.w - r.r_margin - 20, y)
    r.ln(30)

    r.set_font("Sans", "", 12)
    r.multi_cell(0, 6.4, REPORT_SUBTITLE, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.ln(6)
    r.set_font("Sans", "B", 17)
    r.set_text_color(*ACCENT)
    r.multi_cell(0, 9.4, "BÁO CÁO ĐỒ ÁN MÔN HỌC", align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.ln(8)

    # khung tên đề tài
    r.set_draw_color(*ACCENT)
    r.set_line_width(0.5)
    r.set_fill_color(*SHADE)
    title_lines = REPORT_TITLE.split("\n")
    line_h = 8.0
    box_h = 12 + len(title_lines) * line_h
    y0 = r.get_y()
    r.rect(r.l_margin + 6, y0, r.epw - 12, box_h, style="DF")
    r.set_xy(r.l_margin + 10, y0 + 5)
    r.set_font("Sans", "B", 12.4)
    r.set_text_color(*INK)
    for ln in title_lines:
        r.set_x(r.l_margin + 10)
        r.cell(r.epw - 20, line_h, ln, align="C")
        r.ln(line_h)
    r.set_y(y0 + box_h + 12)

    r.set_font("Serif", "", 12)
    rows = [
        ("Giảng viên hướng dẫn", f": {INSTRUCTOR}"),
        ("Sinh viên thực hiện", f": {AUTHOR}"),
        ("Mã sinh viên", f": {STUDENT_ID}"),
        ("Lớp", f": {CLASS_NAME}"),
        ("Ngành", ": Công nghệ thông tin"),
    ]
    for k, v in rows:
        r.set_x(r.l_margin + 32)
        r.set_font("Serif", "B", 12)
        r.cell(52, 8, k)
        r.set_font("Serif", "", 12)
        r.cell(0, 8, v, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    r.set_y(-55)
    r.set_font("Serif", "", 11.5)
    r.set_text_color(*DIM)
    r.multi_cell(0, 6, SUBJECT, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    r.ln(2)
    r.set_text_color(*INK)
    r.set_font("Serif", "B", 12)
    d = date.today()
    r.multi_cell(0, 6, f"HÀ NỘI, THÁNG {d.month} NĂM {d.year}", align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def abstract(r: Report) -> None:
    r.add_page()
    r.front_heading("TÓM TẮT ĐỒ ÁN")
    r.p("Đồ án trình bày quá trình xây dựng và khai thác một cơ sở dữ liệu quan hệ cho bài toán "
        "bán hàng trực tuyến, thực hiện hoàn toàn trên nền tảng miễn phí: Google Cloud Shell "
        "cung cấp môi trường dòng lệnh, Python cung cấp thư viện sqlite3, và SQLite đóng vai trò "
        "hệ quản trị cơ sở dữ liệu nhúng.", indent=False)
    r.p("Cơ sở dữ liệu gồm bốn bảng customers, products, orders và order_items với khoá chính, "
        "khoá ngoại và các ràng buộc CHECK. Đồ án cài đặt đầy đủ 21 yêu cầu của đề bài: nhóm "
        "truy vấn cơ bản và thao tác dữ liệu (S01–S07), nhóm truy vấn tổng hợp nhiều bảng "
        "(S08–S13), nhóm chỉ mục và phân tích kế hoạch thực thi (S14–S15), và nhóm mở rộng "
        "(S16–S21) trên bộ dữ liệu sinh tự động gồm 100 khách hàng, 30 sản phẩm, 500 đơn hàng "
        "và 1.500 dòng đơn hàng.", indent=False)
    r.p("Kết quả thực nghiệm cho thấy toàn bộ câu lệnh thực thi không lỗi và có thể chạy lặp an "
        "toàn; kế hoạch thực thi của truy vấn lọc theo khách hàng chuyển từ SCAN (đọc tuần tự "
        "toàn bảng) sang SEARCH dùng chỉ mục, ở dạng covering index. Đồ án cũng chỉ ra giới hạn "
        "của việc đánh giá chỉ mục bằng thời gian chạy trên dữ liệu nhỏ và đề xuất cách đọc "
        "EXPLAIN QUERY PLAN thay thế.", indent=False)
    r.ln(3)
    r.set_font("Serif", "B", 11)
    r.cell(32, 6, "Từ khoá:")
    r.set_font("Serif", "", 11)
    r.multi_cell(0, 6, "cơ sở dữ liệu quan hệ, SQLite, SQL, khoá ngoại, chỉ mục, "
                       "EXPLAIN QUERY PLAN, Google Cloud Shell.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def abbreviation_list(r: Report) -> None:
    r.add_page()
    r.front_heading("DANH MỤC TỪ VIẾT TẮT")
    rows = [
        ["CSDL", "Cơ sở dữ liệu"],
        ["HQTCSDL", "Hệ quản trị cơ sở dữ liệu"],
        ["DDL", "Data Definition Language — ngôn ngữ định nghĩa dữ liệu"],
        ["DML", "Data Manipulation Language — ngôn ngữ thao tác dữ liệu"],
        ["DQL", "Data Query Language — ngôn ngữ truy vấn dữ liệu"],
        ["PK", "Primary Key — khoá chính"],
        ["FK", "Foreign Key — khoá ngoại"],
        ["SQL", "Structured Query Language — ngôn ngữ truy vấn có cấu trúc"],
        ["EQP", "EXPLAIN QUERY PLAN — lệnh xem kế hoạch thực thi của SQLite"],
        ["CLI", "Command Line Interface — giao diện dòng lệnh"],
        ["B-tree", "Cấu trúc cây cân bằng dùng để lưu chỉ mục"],
        ["CSDLQT", "Cơ sở dữ liệu quan hệ"],
    ]
    r.table(["Từ viết tắt", "Diễn giải"], rows, [34, 106], font_size=10)
    r.p("Ngoài các từ viết tắt trên, báo cáo giữ nguyên tên bảng, tên cột và tên câu lệnh theo "
        "đúng quy ước của đề bài (ví dụ customers, customer_id, S01…S21).", indent=False)


def figure_list(r: Report) -> None:
    r.add_page()
    r.front_heading("DANH MỤC HÌNH VẼ")
    entries = r.front.get("figures", [])
    if not entries:
        r.p("(Danh mục được điền tự động ở lượt sinh thứ hai.)", indent=False)
        return
    for label, caption, page in entries:
        r.list_entry(f"{label}. {caption}", page)


def table_list(r: Report) -> None:
    r.add_page()
    r.front_heading("DANH MỤC BẢNG BIỂU")
    entries = r.front.get("tables", [])
    if not entries:
        r.p("(Danh mục được điền tự động ở lượt sinh thứ hai.)", indent=False)
        return
    for label, caption, page in entries:
        r.list_entry(f"{label}. {caption}", page)


def chapter1(r: Report) -> None:
    r.chapter("1", "Mở đầu")
    r.h2("Lý do chọn đề tài")
    r.p("Dữ liệu là trung tâm của mọi hệ thống thông tin hiện đại. Với một cửa hàng trực tuyến, "
        "việc trả lời được các câu hỏi như “đơn hàng nào có giá trị cao nhất”, “khách hàng nào "
        "chi tiêu nhiều nhất”, “sản phẩm nào bán chạy” hay “doanh thu từng tháng thay đổi ra sao” "
        "đòi hỏi dữ liệu phải được tổ chức theo một mô hình chặt chẽ và truy vấn bằng ngôn ngữ "
        "phù hợp. SQL là ngôn ngữ chuẩn cho công việc này, còn mô hình quan hệ là nền tảng lý "
        "thuyết đứng sau nó.")
    r.p("Trong điều kiện học tập, sinh viên thường gặp trở ngại về môi trường: cài đặt hệ quản "
        "trị như SQL Server hay MySQL tốn tài nguyên, đôi khi phát sinh chi phí hoặc yêu cầu cấu "
        "hình phức tạp. Đề bài LAB 01 giải quyết trở ngại đó bằng một lựa chọn gọn nhẹ: dùng "
        "SQLite — hệ quản trị nhúng nằm trong thư viện chuẩn của Python — và Google Cloud Shell "
        "làm môi trường thực hành miễn phí, chỉ cần tài khoản Gmail và trình duyệt.")
    r.p("Vì vậy đồ án chọn đề tài xây dựng cơ sở dữ liệu quan hệ và khai thác dữ liệu bán hàng "
        "trên SQLite, nhằm rèn luyện đồng thời ba nhóm kỹ năng: thiết kế lược đồ có ràng buộc, "
        "viết truy vấn từ cơ bản đến nâng cao, và đánh giá hiệu năng truy vấn thông qua chỉ mục "
        "cùng kế hoạch thực thi.")

    r.h2("Mục tiêu của đồ án")
    r.p("Đồ án đặt ra các mục tiêu cụ thể sau:")
    r.numbered([
        "Thiết kế và tạo lập được cơ sở dữ liệu bán hàng gồm bốn bảng với khoá chính, khoá ngoại "
        "và ràng buộc miền giá trị đúng theo yêu cầu của đề bài.",
        "Thực hiện thành thạo các thao tác thêm, đọc, sửa, xoá (CRUD) và các truy vấn nền tảng "
        "SELECT, WHERE, ORDER BY.",
        "Viết được các truy vấn tổng hợp nhiều bảng: JOIN, GROUP BY, HAVING, truy vấn con và hàm "
        "cửa sổ (window function).",
        "Tạo chỉ mục và đọc được kế hoạch thực thi do EXPLAIN QUERY PLAN trả về, từ đó giải thích "
        "được ảnh hưởng của chỉ mục tới truy vấn.",
        "Sinh được bộ dữ liệu kiểm thử quy mô lớn hơn (100 khách hàng, 30 sản phẩm, 500 đơn "
        "hàng, 1.000 dòng đơn hàng trở lên) và đánh giá lại kế hoạch thực thi trên bộ dữ liệu đó.",
    ])

    r.h2("Đối tượng và phạm vi nghiên cứu")
    r.p("Đối tượng nghiên cứu là mô hình dữ liệu quan hệ của một cửa hàng trực tuyến giả định, "
        "cùng các kỹ thuật truy vấn và tối ưu truy vấn trên SQLite. Phạm vi của đồ án được giới "
        "hạn như sau:")
    r.bullets([
        "Về dữ liệu: chỉ gồm bốn bảng customers, products, orders, order_items với dữ liệu giả "
        "lập, không sử dụng dữ liệu cá nhân thật.",
        "Về hệ quản trị: SQLite phiên bản trong thư viện chuẩn Python, không dùng máy chủ cơ sở "
        "dữ liệu riêng.",
        "Về môi trường: Google Cloud Shell và máy cá nhân, không bật dịch vụ tính phí.",
        "Về nội dung: 21 yêu cầu S01–S21 của đề bài; không mở rộng sang giao diện web hay báo "
        "cáo trực quan hoá.",
    ])

    r.h2("Phương pháp thực hiện")
    r.p("Đồ án được thực hiện theo trình tự sau: (i) nghiên cứu lý thuyết về mô hình quan hệ, "
        "ngôn ngữ SQL và chỉ mục; (ii) phân tích yêu cầu của đề, thiết kế lược đồ và kiến trúc "
        "các tệp mã nguồn; (iii) cài đặt lần lượt theo từng nhóm yêu cầu, sau mỗi nhóm đều chạy "
        "kiểm thử; (iv) đo và phân tích kế hoạch thực thi trước và sau khi tạo chỉ mục; (v) sinh "
        "dữ liệu mở rộng, đánh giá lại và viết báo cáo.")
    r.p("Một yêu cầu kỹ thuật được đặt ra xuyên suốt quá trình cài đặt: mọi tệp kịch bản phải "
        "chạy lặp được. Cụ thể, khi chạy lại toàn bộ đáp án, dữ liệu phải trở về trạng thái ban "
        "đầu thay vì bị cộng dồn hay sinh lỗi trùng khoá. Yêu cầu này được kiểm chứng bằng cách "
        "chạy mỗi tệp hai lần liên tiếp và so sánh kết quả.")

    r.h2("Bố cục báo cáo")
    r.p("Báo cáo gồm sáu chương và ba phụ lục, được trình bày trong Bảng 1.1.", indent=False)
    r.table(
        ["Chương", "Nội dung chính"],
        [["1. Mở đầu", "Lý do chọn đề tài, mục tiêu, phạm vi và phương pháp thực hiện"],
         ["2. Cơ sở lý thuyết", "Mô hình quan hệ, SQL, chỉ mục B-tree và công cụ kế hoạch thực thi"],
         ["3. Phân tích và thiết kế", "Yêu cầu, lược đồ dữ liệu, kiến trúc chương trình, dữ liệu kiểm thử"],
         ["4. Triển khai và thực nghiệm", "Cài đặt schema, các nhóm truy vấn, chỉ mục, dữ liệu mở rộng, kiểm thử"],
         ["5. Kết quả và đánh giá", "Đối chiếu tiêu chí, đánh giá hiệu quả chỉ mục, hạn chế và bài học"],
         ["6. Kết luận", "Tổng kết kết quả và hướng phát triển"],
         ["Phụ lục A–C", "Cấu trúc bài nộp, mã nguồn chính, kết quả đo và ảnh minh chứng"]],
        [46, 106], caption="Bố cục của báo cáo", font_size=9.6)


def chapter2(r: Report) -> None:
    r.chapter("2", "Cơ sở lý thuyết")
    r.h2("Cơ sở dữ liệu quan hệ")
    r.h3("Khái niệm cơ bản")
    r.p("Mô hình quan hệ do E. F. Codd đề xuất năm 1970 tổ chức dữ liệu thành các bảng (quan hệ). "
        "Mỗi bảng gồm các cột (thuộc tính) và các hàng (bộ). Mỗi ô là một giá trị nguyên tử; "
        "quan hệ giữa các bảng được biểu diễn bằng giá trị khoá chứ không bằng con trỏ vật lý. "
        "Cách tổ chức này cho phép truy vấn dữ liệu bằng đại số quan hệ và ngôn ngữ khai báo SQL.")
    r.h3("Khoá và ràng buộc toàn vẹn")
    r.p("Khoá chính (primary key) là một cột hoặc tổ hợp cột xác định duy nhất mỗi hàng, đồng "
        "thời không được nhận giá trị NULL. Khoá ngoại (foreign key) là cột tham chiếu tới khoá "
        "chính của bảng khác, dùng để bảo đảm tính toàn vẹn tham chiếu: không thể tồn tại đơn "
        "hàng của một khách hàng không có trong bảng khách hàng. Ngoài ra ràng buộc CHECK giới "
        "hạn miền giá trị của cột, còn NOT NULL bắt buộc phải có giá trị.")
    r.p("Trong SQLite, khoá ngoại chỉ được kiểm tra khi bật cờ PRAGMA foreign_keys = ON. Đây là "
        "khác biệt quan trọng so với nhiều hệ quản trị khác: nếu lập trình viên quên bật, khai "
        "báo FOREIGN KEY trong câu lệnh CREATE TABLE chỉ mang ý nghĩa tài liệu chứ không có tác "
        "dụng chặn dữ liệu sai [2].")

    r.h2("Hệ quản trị cơ sở dữ liệu SQLite")
    r.p("SQLite là hệ quản trị cơ sở dữ liệu nhúng: toàn bộ cơ sở dữ liệu nằm trong một tệp duy "
        "nhất, không có tiến trình máy chủ, không cần cấu hình và không phát sinh chi phí bản "
        "quyền. Thư viện này có sẵn trong thư viện chuẩn của Python thông qua mô-đun sqlite3, "
        "nhờ đó một chương trình Python có thể vừa tạo, vừa truy vấn cơ sở dữ liệu mà không cần "
        "cài đặt thêm gói nào [4].")
    r.p("SQLite dùng hệ kiểu dữ liệu động (type affinity): kiểu khai báo chỉ là gợi ý, giá trị "
        "thực tế được lưu theo kiểu phù hợp. Vì không có kiểu ngày riêng, cột ngày thường được "
        "lưu dạng chuỗi YYYY-MM-DD — cách này vẫn cho phép so sánh, sắp xếp đúng thứ tự thời "
        "gian và dùng được hàm strftime() để nhóm theo tháng.")

    r.h2("Ngôn ngữ SQL và các kỹ thuật truy vấn")
    r.h3("Nhóm lệnh DDL, DML và DQL")
    r.p("SQL được chia thành ba nhóm lệnh chính dùng trong đồ án: DDL (CREATE TABLE, CREATE "
        "INDEX) định nghĩa cấu trúc; DML (INSERT, UPDATE, DELETE) thay đổi dữ liệu; DQL (SELECT) "
        "truy vấn dữ liệu. Mỗi nhóm có ngữ nghĩa giao dịch riêng: DML cần commit để ghi thay đổi "
        "vĩnh viễn, còn DDL trong SQLite cũng tham gia giao dịch.")
    r.h3("Kết nối bảng (JOIN)")
    r.p("Phép nối kết hợp các hàng của hai bảng dựa trên điều kiện liên quan. INNER JOIN chỉ giữ "
        "các cặp hàng thoả điều kiện, trong khi LEFT JOIN giữ toàn bộ hàng của bảng bên trái và "
        "điền NULL cho phần không khớp. Chính khác biệt này khiến LEFT JOIN trở thành công cụ "
        "chuẩn để tìm các bản ghi “không có quan hệ”, ví dụ khách hàng chưa từng đặt hàng.")
    r.h3("Tổng hợp nhóm (GROUP BY và HAVING)")
    r.p("GROUP BY gom các hàng thành nhóm theo giá trị của một hoặc nhiều cột, sau đó các hàm "
        "tổng hợp như COUNT, SUM, AVG tính toán trên từng nhóm. WHERE lọc ở mức từng hàng trước "
        "khi gom nhóm, còn HAVING lọc ở mức nhóm sau khi đã tổng hợp — vì vậy muốn lọc theo "
        "doanh thu tính bằng SUM thì bắt buộc phải dùng HAVING.")
    r.h3("Truy vấn con (subquery)")
    r.p("Truy vấn con là một câu SELECT lồng trong câu khác. Nếu truy vấn con trả về một giá trị "
        "duy nhất (truy vấn vô hướng), nó có thể dùng trực tiếp trong biểu thức so sánh, ví dụ "
        "tìm sản phẩm có giá cao hơn giá trung bình. Truy vấn con không tương quan như trường "
        "hợp này chỉ cần tính một lần, nên chi phí không tăng theo số hàng của truy vấn ngoài.")
    r.h3("Hàm cửa sổ (window function)")
    r.p("Hàm cửa sổ tính toán trên một tập hàng liên quan nhưng không làm mất chi tiết từng "
        "hàng, khác với GROUP BY. RANK() trả về thứ hạng có bỏ qua các hạng trùng (1, 2, 2, 4), "
        "còn DENSE_RANK() không bỏ qua (1, 2, 2, 3). SQLite hỗ trợ hàm cửa sổ từ phiên bản 3.25 "
        "(2018) [7].")

    r.h2("Chỉ mục và kế hoạch thực thi")
    r.h3("Cấu trúc B-tree")
    r.p("Chỉ mục (index) là một cấu trúc dữ liệu phụ trợ giúp tìm hàng nhanh hơn. SQLite cài đặt "
        "chỉ mục dưới dạng cây B-tree: mỗi nút chứa nhiều khoá đã sắp xếp và con trỏ tới nút "
        "con, cho phép tìm kiếm theo thời gian tỉ lệ với logarit của số hàng thay vì quét toàn "
        "bảng. Đổi lại, mỗi chỉ mục chiếm thêm dung lượng và làm chậm các thao tác ghi vì phải "
        "cập nhật cây.")
    r.h3("EXPLAIN QUERY PLAN")
    r.p("Lệnh EXPLAIN QUERY PLAN cho biết cách SQLite sẽ thực hiện một truy vấn mà không thực "
        "sự chạy nó [1]. Kết quả thường gặp gồm SCAN (đọc tuần tự toàn bảng), SEARCH (tìm qua "
        "chỉ mục hoặc khoá chính), USE TEMP B-TREE FOR ORDER BY (phải sắp xếp thêm bằng cấu trúc "
        "tạm) và COVERING INDEX (chỉ mục đã chứa đủ cột cần đọc nên không phải quay lại bảng).")
    r.h3("Covering index")
    r.p("Khi mọi cột mà truy vấn cần đọc đều nằm trong chỉ mục, SQLite trả lời hoàn toàn từ chỉ "
        "mục. Trong SQLite, bảng có khoá chính INTEGER được lưu theo rowid, nên chỉ mục trên một "
        "cột bất kỳ thực chất chứa cả rowid — đây là lý do truy vấn chỉ lấy order_id theo "
        "customer_id có thể dùng covering index.")

    r.h2("Môi trường thực hành: Google Cloud Shell")
    r.p("Google Cloud Shell là môi trường dòng lệnh chạy trên trình duyệt, cung cấp sẵn Python, "
        "các công cụ phát triển và 5 GB lưu trữ trong thư mục $HOME mà không cần thanh toán [5]. "
        "Môi trường này phù hợp với bài thực hành vì không phải cài đặt gì, đồng thời vẫn cho "
        "phép lưu lại mã nguồn và tệp cơ sở dữ liệu giữa các phiên làm việc. Hạn chế cần lưu ý "
        "là vùng lưu trữ có thể bị thu hồi nếu thời gian dài không đăng nhập, nên mã nguồn và "
        "cơ sở dữ liệu cần được sao lưu về máy cá nhân hoặc kho lưu trữ Git.")


def chapter3(r: Report) -> None:
    r.chapter("3", "Phân tích và thiết kế")
    r.h2("Yêu cầu của bài toán")
    r.p("Đề bài đặt ra 21 yêu cầu, chia thành bốn nhóm theo mức độ và theo điều kiện dữ liệu. "
        "Bảng 3.1 liệt kê toàn bộ yêu cầu và kỹ thuật SQL tương ứng được sử dụng.")
    r.table(
        ["Mã", "Yêu cầu", "Kỹ thuật chính"],
        [["S01", "Hiển thị tên và thành phố khách hàng", "SELECT, ORDER BY"],
         ["S02", "Sản phẩm có giá trên 1 triệu", "WHERE so sánh số"],
         ["S03", "Sắp xếp sản phẩm theo giá giảm dần", "ORDER BY DESC"],
         ["S04", "Thêm một khách hàng mới", "INSERT … ON CONFLICT"],
         ["S05", "Tăng giá Mouse thêm 10%", "UPDATE có điều kiện"],
         ["S06", "Xoá khách hàng vừa thêm", "DELETE + NOT EXISTS"],
         ["S07", "Liệt kê mã đơn và tên khách hàng", "INNER JOIN"],
         ["S08", "Tính tổng tiền từng đơn hàng", "JOIN 3 bảng, GROUP BY, SUM"],
         ["S09", "Doanh thu từng khách hàng", "LEFT JOIN, GROUP BY"],
         ["S10", "Khách chi tiêu trên 5 triệu", "HAVING SUM(…) > ngưỡng"],
         ["S11", "Sản phẩm giá cao hơn trung bình", "Truy vấn con vô hướng"],
         ["S12", "Khách có từ 2 đơn hàng", "GROUP BY + HAVING COUNT"],
         ["S13", "Top 3 sản phẩm theo doanh thu", "ORDER BY + LIMIT"],
         ["S14", "Tạo chỉ mục trên orders.customer_id", "CREATE INDEX"],
         ["S15", "Xem kế hoạch thực thi trước và sau chỉ mục", "EXPLAIN QUERY PLAN"],
         ["S16", "Doanh thu theo tháng", "strftime + GROUP BY"],
         ["S17", "Khách chưa có đơn hàng", "LEFT JOIN … IS NULL"],
         ["S18", "Sản phẩm chưa từng bán", "NOT EXISTS"],
         ["S19", "Xếp hạng khách theo doanh thu", "RANK, DENSE_RANK"],
         ["S20", "So sánh kế hoạch thực thi sau khi mở rộng dữ liệu", "EXPLAIN trên dữ liệu lớn"],
         ["S21", "So sánh bảng tạm SQL Server và SQLite", "TEMP TABLE, kiến thức hệ quản trị"]],
        [12, 92, 48], caption="Danh sách 21 yêu cầu của đề bài", font_size=9.0)

    r.p("Một điểm cần phân tích kỹ là điều kiện dữ liệu: nhóm S01–S15 chạy trên bộ dữ liệu mẫu "
        "nhỏ (5 khách, 5 sản phẩm, 6 đơn), còn nhóm S16–S21 cần bộ dữ liệu lớn hơn nhiều. Nếu "
        "đặt tất cả trong một tệp đáp án duy nhất thì người chấm buộc phải tự chuyển đổi cơ sở "
        "dữ liệu giữa hai phần. Vì vậy đồ án tách thành hai tệp riêng và ghi rõ tệp nào chạy "
        "trên cơ sở dữ liệu nào, như trình bày ở mục 3.3.")

    r.h2("Thiết kế mô hình dữ liệu")
    r.h3("Sơ đồ quan hệ")
    r.p("Cơ sở dữ liệu gồm bốn bảng với ba quan hệ một–nhiều: một khách hàng có nhiều đơn hàng, "
        "một đơn hàng có nhiều dòng đơn, một sản phẩm có thể xuất hiện trong nhiều dòng đơn. "
        "Sơ đồ được thể hiện ở Hình 3.1.")
    r.erd("Sơ đồ quan hệ của cơ sở dữ liệu bán hàng")
    r.h3("Chi tiết các bảng")
    r.p("Bảng 3.2 mô tả chi tiết từng cột, kiểu dữ liệu và ràng buộc của bốn bảng. Các ràng buộc "
        "được đặt ngay trong câu lệnh CREATE TABLE để cơ sở dữ liệu tự bảo vệ tính toàn vẹn, "
        "không phụ thuộc vào việc chương trình ứng dụng có kiểm tra hay không.")
    r.table(
        ["Bảng", "Cột", "Kiểu", "Ràng buộc"],
        [["customers", "customer_id", "INTEGER", "PRIMARY KEY"],
         ["", "name", "TEXT", "NOT NULL"],
         ["", "city", "TEXT", "—"],
         ["products", "product_id", "INTEGER", "PRIMARY KEY"],
         ["", "name", "TEXT", "NOT NULL"],
         ["", "category", "TEXT", "—"],
         ["", "price", "REAL", "CHECK(price >= 0)"],
         ["orders", "order_id", "INTEGER", "PRIMARY KEY"],
         ["", "customer_id", "INTEGER", "NOT NULL, FK → customers"],
         ["", "order_date", "TEXT", "—"],
         ["order_items", "order_id", "INTEGER", "PK tổ hợp, FK → orders"],
         ["", "product_id", "INTEGER", "PK tổ hợp, FK → products"],
         ["", "quantity", "INTEGER", "CHECK(quantity > 0)"]],
        [30, 40, 26, 64], caption="Chi tiết các bảng trong cơ sở dữ liệu", font_size=9.0)
    r.h3("Các quyết định thiết kế")
    r.p("Ba quyết định thiết kế đáng chú ý trong lược đồ:")
    r.bullets([
        "Khoá chính của order_items là tổ hợp (order_id, product_id). Nhờ vậy mỗi sản phẩm chỉ "
        "xuất hiện một lần trong một đơn; muốn mua thêm thì tăng giá trị quantity thay vì thêm "
        "dòng mới. Thiết kế này cũng tránh được dữ liệu trùng lặp.",
        "Ràng buộc CHECK(price >= 0) và CHECK(quantity > 0) chặn ngay tại tầng cơ sở dữ liệu các "
        "giá trị vô nghĩa như giá âm hoặc số lượng bằng không.",
        "Cột order_date lưu dạng TEXT theo chuỗi YYYY-MM-DD, phù hợp với SQLite (không có kiểu "
        "ngày riêng) và vẫn cho phép sắp xếp, so sánh, đồng thời dùng được strftime() để nhóm "
        "theo tháng cho yêu cầu S16.",
    ])

    r.h2("Thiết kế kiến trúc chương trình")
    r.p("Thay vì dồn toàn bộ thao tác vào một tệp, đồ án tổ chức thành các tệp có trách nhiệm "
        "riêng, mỗi tệp chạy độc lập từ dòng lệnh. Cách tổ chức này giúp dễ kiểm thử, dễ chạy "
        "lại từng bước và phù hợp với yêu cầu nộp kèm mã nguồn của đề bài. Bảng 3.3 mô tả các "
        "tệp chính.")
    r.table(
        ["Tệp", "Trách nhiệm"],
        [["sql/schema.sql", "Định nghĩa bốn bảng, khoá và ràng buộc"],
         ["sql/seed.sql", "Nạp bộ dữ liệu mẫu đúng theo đề bài"],
         ["sql/answers.sql", "Đáp án nhóm bắt buộc S01–S15 (chạy trên sales.db)"],
         ["sql/answers_homework.sql", "Đáp án nhóm mở rộng S16–S21 (chạy trên sales_extended.db)"],
         ["sql/explain.sql", "Cặp EXPLAIN QUERY PLAN trước và sau khi tạo chỉ mục"],
         ["build_db.py", "Dựng sales.db từ schema và seed, in số dòng để đối chiếu"],
         ["generate_data.py", "Sinh dữ liệu mở rộng 100/30/500/1500 với seed cố định"],
         ["run_sql.py", "Chạy tệp .sql bằng Python, in kết quả từng câu lệnh"],
         ["sql_console.py", "Console SQLite tương tác theo mẫu của đề bài"]],
        [52, 100], caption="Kiến trúc các tệp mã nguồn", font_size=9.4)
    r.p("Luồng thực hiện tổng quát gồm bốn bước: dựng cơ sở dữ liệu và nạp dữ liệu mẫu; chạy "
        "tệp đáp án phần bắt buộc; sinh dữ liệu mở rộng và chạy tệp đáp án phần bổ sung; chạy "
        "tệp kế hoạch thực thi để thu thập bằng chứng về chỉ mục.")

    r.h2("Thiết kế dữ liệu kiểm thử")
    r.p("Đồ án sử dụng hai bộ dữ liệu. Bộ thứ nhất là dữ liệu mẫu của đề bài, đủ nhỏ để có thể "
        "kiểm tra kết quả bằng tay. Bộ thứ hai là dữ liệu sinh tự động, đủ lớn để quan sát sự "
        "khác biệt về kế hoạch thực thi. Bảng 3.4 tổng hợp quy mô hai bộ dữ liệu.")
    r.table(
        ["Đối tượng", "Dữ liệu mẫu (đề bài)", "Dữ liệu mở rộng", "Yêu cầu tối thiểu"],
        [["Khách hàng", "5", "100", "100"],
         ["Sản phẩm", "5", "30", "30"],
         ["Đơn hàng", "6", "500", "500"],
         ["Dòng đơn hàng", "8", "1.500", "1.000"],
         ["Khoảng thời gian", "01–08/10/2026", "10/2025 – 10/2026", "—"]],
        [40, 42, 40, 30], caption="Quy mô hai bộ dữ liệu kiểm thử", font_size=9.2,
        align_right={1, 2, 3})
    r.p("Dữ liệu mở rộng được sinh bằng bộ sinh số giả ngẫu nhiên có hạt giống cố định "
        "(random.seed(2026)), nên chạy lại cho đúng cùng một bộ dữ liệu — điều kiện cần để kết "
        "quả trong báo cáo có thể tái lập. Kịch bản sinh cố ý để khoảng 8% khách hàng không phát "
        "sinh đơn và bốn sản phẩm cuối danh mục không xuất hiện trong đơn nào, nhằm bảo đảm hai "
        "truy vấn S17 và S18 có kết quả để kiểm chứng.")


def chapter4(r: Report) -> None:
    r.chapter("4", "Triển khai và thực nghiệm")
    r.h2("Môi trường thực hành")
    r.table(
        ["Thành phần", "Giá trị sử dụng"],
        [["Nền tảng", "Google Cloud Shell (chế độ lưu trữ $HOME), không bật dịch vụ tính phí"],
         ["Ngôn ngữ", "Python 3.11.2, chỉ dùng thư viện chuẩn sqlite3"],
         ["Hệ quản trị", "SQLite 3.40.1, cơ sở dữ liệu dạng tệp sales.db"],
         ["Công cụ hỗ trợ", "build_db.py, run_sql.py, generate_data.py, sql_console.py"],
         ["Chi phí", "0 đồng"]],
        [36, 116], caption="Môi trường thực hành", font_size=9.6)

    r.h2("Khởi tạo cơ sở dữ liệu")
    r.p("Lược đồ được viết trong schema.sql với bốn câu lệnh CREATE TABLE, mỗi câu khai báo đầy "
        "đủ khoá và ràng buộc như thiết kế ở Chương 3.")
    r.code((SQL_DIR / "schema.sql").read_text(encoding="utf-8").split("PRAGMA", 1)[-1]
           .split("\n", 1)[-1].strip(), size=7.8)
    r.p("Dữ liệu mẫu được nạp bằng seed.sql. Để tệp có thể chạy lại an toàn, các câu lệnh dùng "
        "INSERT OR IGNORE: nếu bản ghi đã tồn tại thì bỏ qua thay vì báo lỗi trùng khoá chính. "
        "Sau khi nạp, kịch bản build_db.py đếm số dòng từng bảng và so sánh với kỳ vọng của đề "
        "bài (5, 5, 6, 8), đồng thời chạy PRAGMA foreign_key_check để phát hiện khoá ngoại mồ côi.")
    r.figure(EVID / "02_tables_count.png",
             "Kết quả khởi tạo: số dòng bốn bảng và kiểm tra khoá ngoại", max_h=72)

    r.h2("Cài đặt nhóm truy vấn cơ bản và CRUD (S01–S07)")
    r.p("Nhóm đầu tiên gồm ba truy vấn đọc đơn giản và bốn thao tác có ghi. Ba thao tác ghi là "
        "điểm cần xử lý cẩn thận nhất, vì nếu viết ngây thơ thì mỗi lần chạy lại tệp đáp án sẽ "
        "làm sai dữ liệu: khách hàng bị thêm hai lần, giá sản phẩm bị nhân 10% nhiều lần. Đồ án "
        "áp dụng ba biện pháp tương ứng, trình bày ở đoạn mã dưới đây.")
    r.code(
        "-- S04: them khach hang, chay lai khong loi khoa chinh\n"
        "INSERT INTO customers (customer_id, name, city)\n"
        "VALUES (6, 'Lan', 'Hue')\n"
        "ON CONFLICT(customer_id) DO NOTHING;\n"
        "\n"
        "-- S05: tang gia Mouse 10%, chi khi con o gia goc 250000\n"
        "UPDATE products\n"
        "SET price = ROUND(price * 1.1, 0)\n"
        "WHERE product_id = 102 AND price = 250000;\n"
        "\n"
        "-- S06: xoa dung khach vua them, va chi khi chua co don\n"
        "DELETE FROM customers\n"
        "WHERE customer_id = 6\n"
        "  AND NOT EXISTS (SELECT 1 FROM orders\n"
        "                  WHERE orders.customer_id = customers.customer_id);",
        size=8.0)
    r.p("Điểm mấu chốt là điều kiện AND price = 250000 trong câu UPDATE. Ở lần chạy thứ hai, giá "
        "Mouse đã là 275.000 nên câu lệnh không khớp dòng nào và trả về Rows affected: 0; nhờ vậy "
        "phép nhân 10% không bị cộng dồn. Tương tự, điều kiện NOT EXISTS trong câu DELETE vừa "
        "diễn đạt đúng yêu cầu “khách vừa thêm chưa có đơn hàng”, vừa bảo vệ khoá ngoại: nếu "
        "khách đã có đơn, câu lệnh không xoá gì thay vì gây lỗi ràng buộc.")
    r.p("Kết quả kiểm chứng sau hai lần chạy liên tiếp: giá Mouse giữ nguyên 275.000 và số khách "
        "hàng trở về 5. Truy vấn S07 dùng INNER JOIN để ghép orders với customers, trả về đủ 6 "
        "đơn hàng kèm tên khách.")

    r.h2("Cài đặt truy vấn tổng hợp nhiều bảng (S08–S13)")
    r.p("S08 là truy vấn trung tâm của nhóm này: doanh thu của một đơn bằng tổng của tích số "
        "lượng và đơn giá trên từng dòng đơn, nên phải nối ba bảng orders, order_items và "
        "products rồi gom nhóm theo mã đơn.")
    r.code(
        "-- S08: tong tien tung don hang\n"
        "SELECT o.order_id,\n"
        "       SUM(i.quantity * p.price) AS total\n"
        "FROM orders o\n"
        "JOIN order_items i ON i.order_id = o.order_id\n"
        "JOIN products p    ON p.product_id = i.product_id\n"
        "GROUP BY o.order_id\n"
        "ORDER BY total DESC;\n"
        "\n"
        "-- S10: khach chi tieu tren 5 trieu (loc theo ket qua tong hop)\n"
        "SELECT c.customer_id, c.name,\n"
        "       SUM(i.quantity * p.price) AS revenue\n"
        "FROM customers c\n"
        "JOIN orders o      ON o.customer_id = c.customer_id\n"
        "JOIN order_items i ON i.order_id = o.order_id\n"
        "JOIN products p    ON p.product_id = i.product_id\n"
        "GROUP BY c.customer_id, c.name\n"
        "HAVING SUM(i.quantity * p.price) > 5000000\n"
        "ORDER BY revenue DESC;",
        size=8.0)
    r.table(
        ["Mã đơn", "Tổng tiền (đồng)", "Khách hàng", "Doanh thu (đồng)"],
        [["1001", "15.550.000", "An (id 1)", "17.150.000"],
         ["1004", "15.000.000", "Chi (id 3)", "15.000.000"],
         ["1006", "7.000.000", "Ha (id 5)", "7.000.000"],
         ["1002", "4.150.000", "Binh (id 2)", "4.150.000"],
         ["1003", "1.600.000", "Dung (id 4)", "825.000"],
         ["1005", "825.000", "—", "—"],
         ["Tổng", "44.125.000", "—", "—"]],
        [26, 42, 48, 42], caption="Kết quả S08 và S09 trên dữ liệu mẫu", font_size=9.2,
        align_right={1, 3})
    r.p("Có thể kiểm tra chéo bằng tay đối với đơn 1001: đơn gồm một Laptop giá 15.000.000 và "
        "hai Mouse giá 275.000, tổng 15.550.000 — khớp với kết quả máy trả về. Con số này cũng "
        "cho thấy thứ tự thực hiện các câu lệnh có ảnh hưởng tới kết quả: do S05 đã tăng giá "
        "Mouse trước khi chạy S08, tổng tiền dùng giá 275.000 chứ không phải 250.000. Báo cáo ghi "
        "rõ điểm này để tránh nhầm lẫn khi đối chiếu số liệu.")
    r.figure(EVID / "04_s08_result.png",
             "Kết quả truy vấn S08 và S09 trên dữ liệu mẫu", max_h=74)
    r.p("Ba truy vấn còn lại thể hiện ba kỹ thuật khác nhau. S11 dùng truy vấn con vô hướng để so "
        "sánh với giá trung bình; sau khi S05 đổi giá, giá trung bình của 5 sản phẩm là 4.045.000 "
        "nên chỉ Laptop (15.000.000) vượt trung bình. S12 đếm số đơn theo khách rồi lọc bằng "
        "HAVING COUNT(o.order_id) >= 2, kết quả đúng một khách là An với hai đơn. S13 sắp xếp "
        "giảm dần theo doanh thu và lấy LIMIT 3, cho ba sản phẩm dẫn đầu là Laptop (30.000.000), "
        "Monitor (10.500.000) và Headphones (1.600.000).")
    r.note("Hạn chế của LIMIT khi có đồng hạng",
           "S13 dùng LIMIT 3 nên nếu hai sản phẩm cùng đứng ở vị trí thứ ba, kết quả chỉ trả về "
           "một trong hai. Muốn xử lý đúng trường hợp đồng hạng phải dùng hàm cửa sổ RANK() như "
           "ở yêu cầu S19. Đây là ví dụ cho thấy cùng một câu hỏi nghiệp vụ có thể cần kỹ thuật "
           "phức tạp hơn tuỳ yêu cầu về tính đầy đủ của kết quả.")

    r.h2("Chỉ mục và phân tích kế hoạch thực thi (S14–S15)")
    r.p("Yêu cầu S15 đòi hỏi so sánh kế hoạch thực thi trước và sau khi có chỉ mục, nên không thể "
        "chỉ chạy một lần sau khi đã tạo chỉ mục. Tệp explain.sql được viết để tự đưa cơ sở dữ "
        "liệu về trạng thái cần thiết theo trình tự: xoá chỉ mục nếu tồn tại, xem kế hoạch, tạo "
        "chỉ mục, rồi xem kế hoạch lần hai. Nhờ vậy tệp chạy đúng trên bất kỳ bản sao nào của "
        "cơ sở dữ liệu, ở bất kỳ trạng thái nào.")
    r.code(
        "DROP INDEX IF EXISTS idx_orders_customer;\n"
        "EXPLAIN QUERY PLAN\n"
        "SELECT order_id FROM orders WHERE customer_id = 1;\n"
        "\n"
        "CREATE INDEX IF NOT EXISTS idx_orders_customer\n"
        "    ON orders(customer_id);\n"
        "\n"
        "EXPLAIN QUERY PLAN\n"
        "SELECT order_id FROM orders WHERE customer_id = 1;",
        size=8.2)
    r.table(
        ["Thời điểm", "Kế hoạch thực thi (cột detail)"],
        [["Trước khi tạo chỉ mục", "SCAN orders"],
         ["Sau khi tạo chỉ mục",
          "SEARCH orders USING COVERING INDEX idx_orders_customer (customer_id=?)"]],
        [44, 108], caption="Kế hoạch thực thi trước và sau khi tạo chỉ mục", font_size=9.0)
    r.p("Kết quả cho thấy hai thay đổi. Thứ nhất, kiểu truy cập đổi từ SCAN — đọc tuần tự toàn "
        "bảng rồi mới lọc — sang SEARCH, tức đi xuống cây B-tree của chỉ mục để tìm trực tiếp các "
        "dòng cần thiết. Thứ hai, kế hoạch ghi COVERING INDEX: câu truy vấn chỉ cần cột order_id, "
        "mà chỉ mục trên customer_id của bảng có khoá chính INTEGER đã chứa sẵn rowid (chính là "
        "order_id), nên SQLite trả lời hoàn toàn từ chỉ mục mà không phải đọc lại bảng.")
    r.figure(EVID / "05_explain_before_after.png",
             "Kế hoạch thực thi trước và sau khi tạo chỉ mục trên cột customer_id", max_h=78)

    r.h2("Sinh dữ liệu mở rộng và các yêu cầu S16–S21")
    r.p("Kịch bản generate_data.py sinh dữ liệu mở rộng vào một tệp riêng sales_extended.db, "
        "không ghi đè sales.db, để bộ dữ liệu mẫu vẫn giữ nguyên trạng thái ban đầu. Sau khi "
        "sinh, kịch bản in số dòng từng bảng và kiểm tra khoá ngoại; kết quả đạt 100 khách hàng, "
        "30 sản phẩm, 500 đơn hàng và 1.500 dòng đơn hàng, vượt mức tối thiểu của đề bài.")
    r.figure(EVID / "06_expanded_counts.png",
             "Kết quả sinh dữ liệu mở rộng và kiểm tra tính toàn vẹn", max_h=78)
    r.p("Trên bộ dữ liệu mở rộng, yêu cầu S16 tính doanh thu theo tháng bằng cách nhóm theo "
        "strftime('%Y-%m', order_date). Dữ liệu trải 13 tháng nên kết quả có 13 nhóm, trong đó "
        "nhóm cuối chỉ có 7 đơn vì dữ liệu kết thúc giữa tháng — hiện tượng “tháng dở dang” cần "
        "nêu rõ khi báo cáo doanh thu. Bảng 4.4 trình bày kết quả đầy đủ.")
    r.table(
        ["Tháng", "Số đơn", "Doanh thu (đồng)"],
        [["2025-10", "53", "1.142.485.000"],
         ["2025-11", "39", "978.725.000"],
         ["2025-12", "36", "797.655.000"],
         ["2026-01", "38", "780.995.000"],
         ["2026-02", "37", "870.780.000"],
         ["2026-03", "46", "1.051.310.000"],
         ["2026-04", "47", "947.890.000"],
         ["2026-05", "42", "838.505.000"],
         ["2026-06", "35", "813.970.000"],
         ["2026-07", "40", "696.115.000"],
         ["2026-08", "44", "899.005.000"],
         ["2026-09", "36", "853.310.000"],
         ["2026-10", "7", "48.400.000"]],
        [34, 34, 84], caption="Doanh thu theo tháng trên dữ liệu mở rộng (S16)", font_size=9.0,
        align_right={1, 2})
    r.p("Hai yêu cầu S17 và S18 đều là bài toán tìm bản ghi không có quan hệ tương ứng, nhưng "
        "được cài đặt bằng hai kỹ thuật khác nhau để so sánh: S17 dùng LEFT JOIN kết hợp điều "
        "kiện IS NULL, S18 dùng NOT EXISTS. Cả hai cho kế hoạch thực thi tương đương trên SQLite; "
        "NOT EXISTS thường được ưu tiên vì diễn đạt trực tiếp ngữ nghĩa và không sinh thêm cột "
        "NULL trung gian. Kết quả tìm được 8 khách hàng chưa có đơn (id 37, 38, 43, 56, 83, 89, "
        "92, 94) và 4 sản phẩm chưa từng bán (Graphics Card, RAM 16GB, CPU Cooler, Power Supply).")
    r.code(
        "-- S17: khach hang chua co don hang nao\n"
        "SELECT c.customer_id, c.name, c.city\n"
        "FROM customers c\n"
        "LEFT JOIN orders o ON o.customer_id = c.customer_id\n"
        "WHERE o.order_id IS NULL\n"
        "ORDER BY c.customer_id;\n"
        "\n"
        "-- S19: xep hang khach hang theo doanh thu\n"
        "SELECT c.customer_id, c.name,\n"
        "       ROUND(SUM(i.quantity * p.price), 0) AS revenue,\n"
        "       RANK()       OVER (ORDER BY SUM(i.quantity * p.price) DESC) AS rank,\n"
        "       DENSE_RANK() OVER (ORDER BY SUM(i.quantity * p.price) DESC) AS dense_rank\n"
        "FROM customers c\n"
        "JOIN orders o      ON o.customer_id = c.customer_id\n"
        "JOIN order_items i ON i.order_id = o.order_id\n"
        "JOIN products p    ON p.product_id = i.product_id\n"
        "GROUP BY c.customer_id, c.name\n"
        "ORDER BY revenue DESC;",
        size=7.8)
    r.p("Yêu cầu S19 xếp hạng khách hàng bằng hàm cửa sổ. Trên bộ dữ liệu mở rộng, ba vị trí dẫn "
        "đầu là Ha (314.565.000 đồng), Ho Mai (281.910.000 đồng) và Hoang Chi (267.400.000 đồng). "
        "Do không có hai khách nào trùng doanh thu, hai cột rank và dense_rank trùng nhau; khác "
        "biệt chỉ xuất hiện khi có đồng hạng — khi đó RANK nhảy từ 2 sang 4 còn DENSE_RANK đi "
        "liền sang 3.")
    r.figure(EVID / "07_s19_rank.png",
             "Kết quả xếp hạng khách hàng theo doanh thu với RANK và DENSE_RANK", max_h=76)
    r.p("Yêu cầu S20 lặp lại phân tích kế hoạch thực thi trên bộ dữ liệu lớn. Kết quả vẫn là "
        "SCAN khi chưa có chỉ mục và SEARCH khi có chỉ mục, nhưng lần này xuất hiện thêm dòng "
        "USE TEMP B-TREE FOR ORDER BY vì truy vấn lấy thêm cột order_date và sắp xếp theo cột "
        "này — cột không nằm trong chỉ mục nên SQLite phải dựng cấu trúc sắp xếp tạm. Nếu truy "
        "vấn được chạy thường xuyên, một chỉ mục tổ hợp trên (customer_id, order_date) sẽ loại "
        "bỏ được bước sắp xếp này.")
    r.p("Yêu cầu S21 là câu hỏi lý thuyết, yêu cầu so sánh bảng tạm của SQL Server với TEMP TABLE "
        "của SQLite. Bảng 4.5 tổng hợp nội dung so sánh.")
    r.table(
        ["Tiêu chí", "SQL Server", "SQLite"],
        [["Bảng tạm cục bộ", "#t — chỉ session tạo ra nó thấy, tự xoá khi session kết thúc",
          "CREATE TEMP TABLE — gắn với kết nối, mất khi đóng kết nối"],
         ["Bảng tạm toàn cục", "##t — mọi session đều thấy, mất khi session cuối cùng đóng",
          "Không có khái niệm tương đương"],
         ["Nơi lưu trữ", "tempdb — cơ sở dữ liệu hệ thống dùng chung, chứa cả biến bảng và dữ "
          "liệu sắp xếp tạm", "Schema temp của kết nối, ở RAM hoặc tệp tạm tuỳ PRAGMA temp_store"],
         ["Phạm vi tên", "Phân biệt bằng tiền tố # nên không đụng bảng thường",
          "Bảng temp được tìm trước main nên trùng tên sẽ che bảng thường"],
         ["Cú pháp xoá", "DROP TABLE #t", "DROP TABLE temp.t"]],
        [30, 64, 58], caption="So sánh bảng tạm giữa SQL Server và SQLite (S21)", font_size=8.6)

    r.h2("Kiểm thử")
    r.p("Sau khi hoàn thiện, đồ án thực hiện các kiểm thử tổng hợp được liệt kê trong Bảng 4.6. "
        "Mỗi kiểm thử đều có tiêu chí đạt rõ ràng để có thể chạy lại và xác nhận.")
    r.table(
        ["Kiểm thử", "Cách thực hiện", "Kết quả"],
        [["Tạo dữ liệu mẫu", "python3 build_db.py --force", "5 / 5 / 6 / 8 dòng, khớp đề bài"],
         ["Chạy lặp đáp án", "Chạy answers.sql hai lần liên tiếp", "0 lỗi, giá Mouse vẫn 275.000"],
         ["Toàn vẹn khoá ngoại", "PRAGMA foreign_key_check sau khi nạp", "Không có dòng vi phạm"],
         ["Dữ liệu mở rộng", "python3 generate_data.py --force", "100 / 30 / 500 / 1500 dòng"],
         ["Đáp án mở rộng", "Chạy answers_homework.sql", "9 câu lệnh, 0 lỗi"],
         ["Kế hoạch thực thi", "Chạy explain.sql", "SCAN chuyển thành SEARCH dùng chỉ mục"],
         ["Console tương tác", "Nhập câu lệnh nhiều dòng, câu sai, EXIT", "Báo lỗi đúng, không thoát"]],
        [40, 66, 46], caption="Các kiểm thử đã thực hiện", font_size=8.8)


def chapter5(r: Report) -> None:
    r.chapter("5", "Kết quả và đánh giá")
    r.h2("Kết quả đạt được theo tiêu chí")
    r.p("Bảng 5.1 đối chiếu kết quả thực hiện với năm tiêu chí chấm điểm của đề bài, kèm vị trí "
        "trình bày trong báo cáo để thuận tiện đối chiếu khi đánh giá.")
    r.table(
        ["Tiêu chí", "Điểm", "Nội dung đã thực hiện", "Vị trí"],
        [["Cài đặt và tạo dữ liệu", "2,0", "Lược đồ 4 bảng có ràng buộc; dữ liệu mẫu đúng 5/5/6/8; "
          "kịch bản dựng cơ sở dữ liệu tự kiểm tra", "Mục 4.2"],
         ["CRUD và câu cơ bản", "2,0", "S01–S07 đầy đủ, CRUD chạy lặp an toàn", "Mục 4.3"],
         ["Truy vấn nâng cao", "3,0", "S08–S13 với JOIN nhiều bảng, HAVING, truy vấn con, LIMIT; "
          "S16–S19 với window function", "Mục 4.4, 4.6"],
         ["Index và giải thích", "1,5", "S14–S15, phân tích SCAN/SEARCH/COVERING INDEX, giải thích "
          "vì sao không đo bằng thời gian", "Mục 4.5, 5.2"],
         ["Bài mở rộng, báo cáo", "1,5", "Dữ liệu 100/30/500/1500 tái lập được; S16–S21 đầy đủ; "
          "báo cáo và ảnh minh chứng", "Chương 4, Phụ lục C"]],
        [34, 12, 82, 24], caption="Đối chiếu kết quả với tiêu chí chấm điểm của đề bài",
        font_size=8.8, align_right={1})

    r.h2("Đánh giá hiệu quả của chỉ mục")
    r.p("Kết quả thực nghiệm cho thấy chỉ mục thay đổi rõ rệt kế hoạch thực thi, nhưng không đo "
        "được khác biệt về thời gian trên bộ dữ liệu nhỏ. Bảng 5.2 tổng hợp hai kiểu truy cập và "
        "ý nghĩa của chúng.")
    r.table(
        ["Kiểu truy cập", "Cách thực hiện", "Chi phí", "Khi nào xuất hiện"],
        [["SCAN", "Đọc tuần tự toàn bảng rồi lọc", "Tỉ lệ với số hàng của bảng",
          "Không có chỉ mục phù hợp với điều kiện lọc"],
         ["SEARCH (index)", "Đi xuống cây B-tree để tìm trực tiếp", "Tỉ lệ với log(số hàng) cộng "
          "số dòng khớp", "Có chỉ mục trên cột trong điều kiện lọc hoặc nối"],
         ["SEARCH (covering)", "Đọc hoàn toàn từ chỉ mục", "Như SEARCH, không phải đọc lại bảng",
          "Mọi cột cần đọc đều có trong chỉ mục"]],
        [30, 48, 40, 34], caption="So sánh các kiểu truy cập dữ liệu trong SQLite", font_size=8.6)
    r.p("Với bảng 6 dòng, chênh lệch thời gian giữa SCAN và SEARCH nằm dưới ngưỡng đo của đồng hồ "
        "hệ thống, nên nếu đánh giá bằng thời gian chạy sẽ dễ kết luận sai rằng chỉ mục không có "
        "tác dụng. Cách đánh giá đúng là đọc kế hoạch thực thi: kiểu truy cập, số bước thực hiện "
        "và sự xuất hiện của các bước phụ như sắp xếp tạm. Đây cũng là lưu ý mà đề bài nêu rõ.")
    r.p("Một quan sát khác là chỉ mục không miễn phí. Mỗi chỉ mục làm tăng dung lượng tệp cơ sở "
        "dữ liệu và làm chậm các thao tác ghi, vì cây B-tree phải được cập nhật. Vì vậy chỉ nên "
        "tạo chỉ mục cho các cột thường xuyên xuất hiện trong điều kiện lọc hoặc điều kiện nối, "
        "như orders.customer_id trong bài toán này, thay vì tạo cho mọi cột.")

    r.h2("Đánh giá tính đúng đắn và khả năng tái lập")
    r.p("Ba yếu tố sau bảo đảm kết quả trong báo cáo có thể kiểm chứng lại. Thứ nhất, dữ liệu mẫu "
        "được nạp từ tệp seed.sql có nội dung đúng như đề bài, và kịch bản dựng cơ sở dữ liệu in "
        "ra số dòng để so sánh trực tiếp với kỳ vọng. Thứ hai, dữ liệu mở rộng được sinh với hạt "
        "giống cố định nên chạy lại cho đúng cùng một bộ dữ liệu. Thứ ba, các tệp đáp án được "
        "viết để chạy lặp an toàn, nên người đánh giá có thể chạy nhiều lần mà không làm hỏng "
        "trạng thái dữ liệu.")
    r.p("Ngoài ra, phần kết quả đều được đối chiếu chéo: tổng tiền từng đơn trong S08 được kiểm "
        "tra bằng tay với đơn 1001; tổng doanh thu theo khách trong S09 được so với tổng theo "
        "đơn; số khách chưa có đơn ở S17 khớp với số khách được kịch bản sinh cố ý bỏ trống.")

    r.h2("Hạn chế")
    r.bullets([
        "Bộ dữ liệu mẫu quá nhỏ để đánh giá định lượng hiệu năng, nên các kết luận về chỉ mục "
        "chủ yếu mang tính định tính dựa trên kế hoạch thực thi.",
        "Dữ liệu mở rộng vẫn ở mức vài nghìn dòng, chưa đủ lớn để quan sát rõ ảnh hưởng của "
        "chỉ mục tổ hợp hoặc ảnh hưởng của việc sắp xếp tạm.",
        "Đồ án chưa có giao diện người dùng hay báo cáo trực quan hoá; kết quả được trình bày "
        "dưới dạng bảng và ảnh chụp màn hình.",
        "Chưa xử lý các tình huống đồng thời (nhiều tiến trình cùng ghi) vì SQLite ở cấu hình mặc "
        "định chỉ cho phép một tiến trình ghi tại một thời điểm.",
    ])

    r.h2("Bài học kinh nghiệm")
    r.numbered([
        "Khoá ngoại của SQLite là tuỳ chọn: phải bật PRAGMA foreign_keys = ON ở mọi kết nối, nếu "
        "không ràng buộc trong lược đồ chỉ mang tính tài liệu.",
        "Kịch bản có thao tác ghi phải được thiết kế để chạy lặp an toàn bằng ON CONFLICT, điều "
        "kiện chặt trong UPDATE và NOT EXISTS trong DELETE.",
        "Chỉ mục là con dao hai lưỡi: tăng tốc truy vấn đọc nhưng làm chậm ghi và tốn dung lượng, "
        "nên phải chọn cột để đánh chỉ mục dựa trên truy vấn thực tế.",
        "Đọc kế hoạch thực thi là cách đánh giá ổn định hơn đo thời gian, nhất là khi dữ liệu nhỏ "
        "hoặc máy chạy khác nhau.",
        "Báo cáo số liệu phải ghi rõ trạng thái dữ liệu tại thời điểm đo, vì thứ tự thực hiện các "
        "câu lệnh có ghi ảnh hưởng trực tiếp tới kết quả truy vấn sau đó.",
    ])


def chapter6(r: Report) -> None:
    r.chapter("6", "Kết luận và hướng phát triển")
    r.h2("Kết luận")
    r.p("Đồ án đã hoàn thành đầy đủ 21 yêu cầu của đề bài LAB 01. Cơ sở dữ liệu bán hàng gồm bốn "
        "bảng được thiết kế đúng theo mô hình quan hệ với khoá chính, khoá ngoại và ràng buộc "
        "miền giá trị; dữ liệu mẫu được nạp đúng 5 khách hàng, 5 sản phẩm, 6 đơn hàng và 8 dòng "
        "đơn hàng như kỳ vọng.")
    r.p("Về kỹ năng truy vấn, đồ án đã cài đặt và kiểm chứng các nhóm lệnh từ cơ bản đến nâng cao: "
        "truy vấn một bảng, thao tác dữ liệu, nối nhiều bảng, tổng hợp nhóm có lọc bằng HAVING, "
        "truy vấn con và hàm cửa sổ. Các thao tác có ghi đều được xử lý để chạy lặp an toàn, và "
        "điều này đã được kiểm chứng bằng cách chạy hai lần liên tiếp.")
    r.p("Về tối ưu truy vấn, đồ án đã chứng minh được bằng kế hoạch thực thi rằng việc tạo chỉ mục "
        "trên orders.customer_id chuyển truy vấn từ SCAN sang SEARCH, ở mức covering index; đồng "
        "thời chỉ ra giới hạn của việc suy luận hiệu năng trên dữ liệu nhỏ và cách khắc phục bằng "
        "cách đọc kế hoạch thay vì đo thời gian.")
    r.p("Về kỹ năng công cụ, đồ án đã sử dụng thành thạo Google Cloud Shell, Python và SQLite "
        "trong một quy trình làm việc hoàn toàn miễn phí, có thể tái lập và có kiểm thử tự động "
        "cho từng bước.")

    r.h2("Hướng phát triển")
    r.bullets([
        "Bổ sung tầng giao diện: một ứng dụng web nhỏ hoặc giao diện dòng lệnh có menu để thao "
        "tác dữ liệu thay vì gõ SQL trực tiếp.",
        "Xây dựng các view và báo cáo tổng hợp (doanh thu theo tháng, theo thành phố, theo danh "
        "mục) để tái sử dụng thay vì viết lại truy vấn mỗi lần.",
        "Thử nghiệm chỉ mục tổ hợp trên (customer_id, order_date) và đo lại kế hoạch thực thi "
        "cho truy vấn ở yêu cầu S20 để loại bỏ bước sắp xếp tạm.",
        "Mở rộng quy mô dữ liệu lên hàng trăm nghìn dòng và đo thời gian thực thi thực tế để có "
        "kết luận định lượng về hiệu quả của chỉ mục.",
        "So sánh với mô hình tài liệu trên MongoDB ở LAB 02 để làm rõ đánh đổi giữa mô hình chuẩn "
        "hoá (quan hệ) và mô hình nhúng (tài liệu) đối với cùng một bài toán bán hàng.",
    ])


def references(r: Report) -> None:
    r.add_page()
    r.front_heading("TÀI LIỆU THAM KHẢO")
    items = [
        "SQLite Consortium. EXPLAIN QUERY PLAN. https://www.sqlite.org/eqp.html",
        "SQLite Consortium. Foreign Key Support. https://www.sqlite.org/foreignkeys.html",
        "SQLite Consortium. CREATE TABLE — temporary tables. https://www.sqlite.org/lang_createtable.html",
        "Python Software Foundation. sqlite3 — DB-API 2.0 interface for SQLite databases. "
        "https://docs.python.org/3/library/sqlite3.html",
        "Google Cloud. Cloud Shell documentation. https://cloud.google.com/shell/docs",
        "Microsoft. CREATE TABLE (Transact-SQL) — temporary tables and tempdb. "
        "https://learn.microsoft.com/sql/t-sql/statements/create-table-transact-sql",
        "SQLite Consortium. Window Functions. https://www.sqlite.org/windowfunctions.html",
        "SQLite Consortium. Query Planning. https://www.sqlite.org/optoverview.html",
    ]
    for i, item in enumerate(items, 1):
        r.set_font("Serif", "", 11)
        r.set_x(r.l_margin)
        r.cell(9, 6.2, f"[{i}]")
        r.set_x(r.l_margin + 9)
        r.multi_cell(r.epw - 9, 6.2, item, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        r.ln(1.6)


def appendix(r: Report) -> None:
    r.chapter("A", "Cấu trúc bài nộp và hướng dẫn tái lập")
    r.p("Bài nộp được đóng gói thành một tệp ZIP theo quy định của đề bài. Bảng A.1 mô tả nội "
        "dung từng thư mục và tệp trong gói nộp.")
    r.table(
        ["Tệp / thư mục", "Nội dung"],
        [["data/sales.db", "Cơ sở dữ liệu đã nạp dữ liệu mẫu"],
         ["data/sales_extended.db", "Cơ sở dữ liệu mở rộng dùng cho S16–S21"],
         ["sql_console.py", "Console SQLite tương tác (bắt buộc theo đề)"],
         ["sql/answers.sql", "Đáp án nhóm bắt buộc S01–S15"],
         ["sql/answers_homework.sql", "Đáp án nhóm mở rộng S16–S21"],
         ["sql/explain.sql", "Kế hoạch thực thi trước và sau chỉ mục"],
         ["build_db.py, generate_data.py, run_sql.py", "Các kịch bản hỗ trợ"],
         ["report/*.pdf", "Báo cáo đồ án (tệp này) và bản tóm tắt 3 trang"],
         ["evidence/*.png", "Ảnh minh chứng sinh từ kết quả chạy thật"],
         ["README_MAPPING.txt", "Bảng ánh xạ yêu cầu của đề sang tệp tương ứng"]],
        [62, 90], caption="Cấu trúc gói bài nộp", font_size=9.0)
    r.p("Để tái lập toàn bộ kết quả trong báo cáo, chạy lần lượt các lệnh dưới đây từ thư mục "
        "lab01_sql.", indent=False)
    r.code(
        "# 1) Du lieu mau theo de: ky vong 5 / 5 / 6 / 8\n"
        "python3 build_db.py --force\n"
        "\n"
        "# 2) Phan bat buoc S01-S15\n"
        "python3 run_sql.py sql/answers.sql\n"
        "\n"
        "# 3) Du lieu mo rong va phan bo sung S16-S21\n"
        "python3 generate_data.py --force\n"
        "python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db\n"
        "\n"
        "# 4) Chung minh chi muc: SCAN orders -> SEARCH ... USING INDEX\n"
        "python3 run_sql.py sql/explain.sql\n"
        "python3 run_sql.py sql/explain.sql --db data/sales_extended.db\n"
        "\n"
        "# 5) Sinh lai anh minh chung va bao cao\n"
        "cd evidence && python3 make_evidence.py && cd ..\n"
        "python3 report/make_report.py        # bao cao do an (tep nay)\n"
        "python3 report/make_pdf.py           # ban tom tat 3 trang\n",
        size=8.0)

    r.chapter("B", "Mã nguồn chính")
    r.p("Phụ lục này trích nội dung hai tệp quan trọng nhất của bài làm: lược đồ cơ sở dữ liệu và "
        "toàn bộ đáp án nhóm bắt buộc. Các tệp còn lại nằm trong gói nộp kèm theo báo cáo.")
    r.h2("Lược đồ cơ sở dữ liệu (schema.sql)")
    r.code((SQL_DIR / "schema.sql").read_text(encoding="utf-8"), size=7.4)
    r.h2("Đáp án nhóm bắt buộc (answers.sql, S01–S15)")
    r.code((SQL_DIR / "answers.sql").read_text(encoding="utf-8"), size=7.2)
    r.h2("Đáp án nhóm mở rộng (answers_homework.sql, S16–S21)")
    r.code((SQL_DIR / "answers_homework.sql").read_text(encoding="utf-8"), size=7.2)

    r.chapter("C", "Kết quả đo và ảnh minh chứng")
    r.p("Bảy ảnh dưới đây được sinh tự động từ kết quả chạy thật của các kịch bản, không chỉnh "
        "sửa nội dung. Mỗi ảnh tương ứng một nhóm bằng chứng được nêu trong Chương 4.")
    shots = [
        ("01_env.png", "Môi trường thực hành: phiên bản Python và SQLite", 58),
        ("03_console.png", "Console SQLite: câu lệnh nhiều dòng, xử lý lỗi và thoát", 62),
        ("02_tables_count.png", "Số dòng bốn bảng sau khi nạp dữ liệu mẫu", 62),
        ("06_expanded_counts.png", "Sinh dữ liệu mở rộng và kiểm tra khoá ngoại", 66),
        ("04_s08_result.png", "Kết quả S08 và S09", 62),
        ("05_explain_before_after.png", "Kế hoạch thực thi trước và sau khi tạo chỉ mục", 66),
        ("07_s19_rank.png", "Kết quả xếp hạng khách hàng với RANK và DENSE_RANK", 64),
    ]
    for name, caption, h in shots:
        r.figure(EVID / name, caption, max_h=h)


# =====================================================================================
#  LẮP RÁP
# =====================================================================================
def build(out: Path, with_images: bool = True, front: dict | None = None) -> Report:
    r = Report(with_images=with_images, front=front)
    cover(r)
    abstract(r)
    r.add_page()
    r.insert_toc_placeholder(r.render_toc, pages=1, allow_extra_pages=True)
    abbreviation_list(r)
    figure_list(r)
    table_list(r)
    for fn in (chapter1, chapter2, chapter3, chapter4, chapter5, chapter6):
        fn(r)
    references(r)
    appendix(r)
    out.parent.mkdir(parents=True, exist_ok=True)
    r.output(str(out))
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh báo cáo đồ án LAB 01 ra PDF")
    ap.add_argument("--out", type=Path,
                    default=HERE / "BaoCaoDoAn_LAB01_NguyenDanhThai_B23DCKH105.pdf")
    ap.add_argument("--no-images", action="store_true", help="không chèn ảnh minh chứng")
    args = ap.parse_args()

    if not args.no_images and not any(EVID.glob("0*.png")):
        print("[!] Chưa có ảnh minh chứng. Chạy trước: cd ../evidence && python3 make_evidence.py",
              file=sys.stderr)

    # Lượt 1: thu thập danh mục hình/bảng và số trang. Lượt 2+: vẽ danh mục rồi kiểm tra hội tụ.
    front: dict = {"figures": [], "tables": []}
    report = build(args.out, not args.no_images, front)
    prev = None
    for attempt in range(4):
        figures = report.figures
        tables = report.tables
        if prev == (figures, tables):
            break
        prev = (figures, tables)
        front = {"figures": figures, "tables": tables}
        report = build(args.out, not args.no_images, front)

    pages = _count_pages(args.out)
    print(f"[ok] {args.out}")
    print(f"     {pages} trang · {len(report.figures)} hình · {len(report.tables)} bảng · "
          f"{args.out.stat().st_size / 1024:.0f} KB")
    if [f[2] for f in report.figures] != [f[2] for f in front.get("figures", [])]:
        print("[!] Số trang trong danh mục hình chưa hội tụ — chạy lại script.", file=sys.stderr)
        return 1
    return 0


def _count_pages(path: Path) -> int:
    try:
        sys.path.insert(0, str(HERE))
        from pdf_pages import pages_via_regex

        return pages_via_regex(path) or 0
    except Exception:                                   # noqa: BLE001
        try:
            import pypdfium2 as pdfium

            return len(pdfium.PdfDocument(str(path)))
        except Exception:                               # noqa: BLE001
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
