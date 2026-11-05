# Báo cáo LAB 01 — LaTeX

Thư mục này có **hai báo cáo**, phục vụ hai tình huống khác nhau của đề bài:

| File | Số trang | Khi nào dùng |
| --- | --- | --- |
| **`BaoCaoDoAn_LAB01_NguyenDanhThai_B23DCKH105.pdf`** | **37 trang** | **Báo cáo đồ án đầy đủ** — bìa, mục lục, danh mục, 6 chương, tham khảo, 3 phụ lục. Sinh bằng `make_report.py` |
| `lab01_report_short_pdf.pdf` | 3 trang | Bản tóm tắt ngắn (đề yêu cầu "báo cáo PDF 2–3 trang") — sinh bằng `make_pdf.py` |
| `make_pdf.py` | — | Xuất PDF trực tiếp bằng Python (**không cần TeX**) — dùng khi máy không có pdflatex |
| `lab01_report_short.tex` | 2–3 trang | Bản LaTeX tương đương (2 cột) — dùng khi có TeX hoặc nộp trên Overleaf |
| `lab01_report.tex` | ~10 trang | Bản đầy đủ (9 mục + 4 phụ lục), tham khảo/đối chiếu |

### Báo cáo đồ án (văn phong đồ án, 37 trang)

```bash
cd lab01_sql/report
python3 make_report.py            # -> BaoCaoDoAn_LAB01_NguyenDanhThai_B23DCKH105.pdf
python3 make_report.py --no-images
```

Cấu trúc theo văn phong đồ án thông thường: **trang bìa** (trường, khoa, tên đề tài, GVHD,
sinh viên, MSSV, lớp, năm) → **tóm tắt** → **mục lục** → **danh mục từ viết tắt** → **danh mục
hình vẽ** → **danh mục bảng biểu** → **Chương 1 Mở đầu** (lý do, mục tiêu, đối tượng/phạm vi,
phương pháp, bố cục) → **Chương 2 Cơ sở lý thuyết** → **Chương 3 Phân tích và thiết kế** (yêu
cầu, ERD, chi tiết bảng, kiến trúc, dữ liệu kiểm thử) → **Chương 4 Triển khai và thực nghiệm**
(schema, CRUD, truy vấn tổng hợp, chỉ mục, dữ liệu mở rộng, kiểm thử) → **Chương 5 Kết quả và
đánh giá** (đối chiếu tiêu chí, hiệu quả chỉ mục, hạn chế, bài học) → **Chương 6 Kết luận** →
**Tài liệu tham khảo** → **Phụ lục A–C** (cấu trúc bài nộp, mã nguồn, ảnh minh chứng).

Điểm kỹ thuật: mục lục dùng `insert_toc_placeholder` của fpdf2 (có link, số trang tự động);
danh mục hình/bảng được thu thập ở lượt sinh thứ nhất rồi chạy lại đến khi số trang hội tụ;
ERD vẽ trực tiếp bằng fpdf (hộp + mũi tên + nhãn 1:N) nên không cần TikZ.

### Xuất bản tóm tắt 3 trang (không cần TeX)

```bash
cd lab01_sql/report
pip install -r ../evidence/requirements.txt     # fpdf2 + pillow
python3 make_pdf.py            # -> lab01_report_short_pdf.pdf, tự co ảnh cho vừa 3 trang
python3 make_pdf.py --no-images # bản không ảnh (nhẹ hơn, ~4 trang chữ)
```

`make_pdf.py` đọc ảnh từ `../evidence/*.png`; nếu chưa có thì tự gọi
`evidence/make_evidence.py`. Script thử co ảnh dần (×1.0 → ×0.88 → ×0.78 …), cuối cùng bỏ
Hình 6 (console) để luôn ra ≤ 3 trang, và in số trang sau khi xuất.

Cả hai đều dùng pdfLaTeX + `vntex` (tiếng Việt có ngắt từ đúng).

## Biên dịch

```bash
cd lab01_sql/report

bash compile.sh          # = 2p: bản gọn 2–3 trang (mặc định) + tự kiểm tra số trang
bash compile.sh full     # bản đầy đủ có phụ lục
bash compile.sh short    # bản đầy đủ nhưng tắt phụ lục
bash compile.sh check     # chỉ kiểm tra cú pháp, không compile
```

Hoặc thủ công (2 lần để có mục lục / `\ref`):

```bash
pdflatex lab01_report_short.tex && pdflatex lab01_report_short.tex
python3 pdf_pages.py lab01_report_short.pdf --max 3
```

**Overleaf:** tạo project → upload thư mục `report/` → *Menu → Compiler = pdfLaTeX* →
Recompile. Đặt `lab01_report_short.tex` làm main document (Menu → Main document). Overleaf có
sẵn `vntex` nên không cần cài gì.

## Ba script kiểm tra / xuất PDF (không cần TeX)

| Script | Việc nó làm |
| --- | --- |
| `python3 check_tex.py *.tex` | Kiểm tra tĩnh: cân bằng `\begin/\end`, ngoặc nhọn, ký tự `_ # & % $` chưa escape, `\ref` ↔ `\label`, `\if`/`\fi`, **số ô mỗi hàng bảng so với khai báo cột** (lỗi `Extra alignment tab`). `compile.sh` chạy bước này trước khi compile. |
| `python3 pdf_pages.py <pdf> [--max 3]` | Đếm số trang PDF (ưu tiên `pdfinfo`, không có thì đọc cấu trúc PDF) và **cảnh báo nếu vượt 3 trang**. `compile.sh 2p` tự gọi với `--max 3`. |
| `python3 make_pdf.py` | Xuất `lab01_report_short_pdf.pdf` bằng fpdf2 + DejaVu (đủ glyph tiếng Việt), chèn 6 ảnh minh chứng, tự co cho vừa 3 trang. |

Nhờ vậy sau khi compile bạn biết ngay báo cáo có vừa giới hạn hay không, thay vì mở trình đọc
PDF đếm thủ công.

## Cấu trúc bản gọn 2–3 trang (`lab01_report_short.tex`)

Bố cục **2 cột, 10pt, lề 1.5–1.6cm**, bảng `\scriptsize` — đủ chỗ cho cả 5 tiêu chí chấm điểm mà
không cần cắt nội dung chuyên môn:

1. Tiêu đề + Tóm tắt (trải hết chiều ngang)
2. Mục tiêu và môi trường — bảng môi trường + giải thích **tách bắt buộc (S01–S15) / bổ sung (S16–S21)**
3. Mô hình dữ liệu — listing schema rút gọn + 3 quyết định thiết kế (khoá tổ hợp, `CHECK`, `PRAGMA foreign_keys`)
4. Kết quả S01–S15 — bảng tổng hợp 15 câu, CRUD lặp an toàn, bảng S08/S09, nhóm truy vấn nâng cao
5. Index & EXPLAIN — bảng trước/sau (`SCAN` → `COVERING INDEX`) + vì sao không đo bằng wall-clock
6. S16–S21 — 6 gạch đầu dòng, mỗi câu kèm **số liệu thật** (13 tháng, 8 khách, 4 sản phẩm, top 3, S20, bảng tạm)
7. Kết luận + 4 bài học + listing lệnh tái lập

## Co giãn độ dài (nếu ra 4 trang)

Sửa theo thứ tự, dừng khi vừa 3 trang:

1. **Bỏ mục "Lệnh tái lập"** ở cuối (listing `bash`) — tiết kiệm ~0.3 trang.
2. Đổi `\scriptsize` của các bảng thành `\tiny`, hoặc bỏ Bảng "Tổng hợp 15 câu bắt buộc" và giữ
   lại nội dung quan trọng nhất dưới dạng câu văn.
3. Giảm lề: `top=1.2cm,bottom=1.2cm,left=1.3cm,right=1.3cm,columnsep=0.5cm`.
4. Rút mục 6 (S16–S21): gộp S21 còn 2 câu, bỏ phần giải thích `RANK` vs `DENSE_RANK`.
5. Cuối cùng mới đổi `article` → `extarticle` (gói `extsizes`) với `9pt`:
   `\documentclass[9pt,a4paper,twocolumn]{extarticle}`.

Nếu **ít hơn 2 trang** thì thêm lại bảng `S16` theo tháng và đoạn thảo luận về `COVERING INDEX`
từ bản đầy đủ (`lab01_report.tex`, mục 6).

## Yêu cầu gói TeX

`vntex` (kèm `babel-vietnamese`), `booktabs`, `tabularx`, `array`, `enumitem`, `caption`,
`float`, `listings`, `xcolor`, `titlesec` (bản gọn), `tikz` (chỉ bản đầy đủ), `fancyhdr` (bản đầy
đủ), `hyperref`.

Debian/Ubuntu:

```bash
sudo apt-get install texlive-latex-extra texlive-lang-other texlive-fonts-recommended \
                     texlive-pictures latexmk poppler-utils
```

`poppler-utils` cung cấp `pdfinfo` để `pdf_pages.py` đếm trang chính xác hơn.

## Công tắc phụ lục của bản đầy đủ

Trong `lab01_report.tex`:

```latex
\newif\ifwithappendix
\withappendixtrue    % \withappendixfalse để bỏ toàn bộ phụ lục
```

`bash compile.sh short` tự đổi sang `false`, compile, rồi khôi phục file như ban đầu.

## Phương án XeLaTeX (khi máy không có `vntex`)

Thay ba dòng phần "Tiếng Việt" (`inputenc`, `fontenc T5`, `babel vietnamese`) bằng:

```latex
\usepackage{fontspec}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
```

rồi compile bằng `xelatex` (2 lần) hoặc `latexmk -xelatex`. DejaVu có đủ glyph tiếng Việt và đi
kèm TeX Live; nhược điểm là không có ngắt từ tiếng Việt như `vntex`.

## Ghi chú

- Toàn bộ số liệu trong cả hai báo cáo lấy từ lần chạy thật trong repo (`build_db.py`,
  `run_sql.py`, `generate_data.py`, `explain.sql`) — xem `../PLAN.md` mục 5.
- Cảnh báo `Token not allowed in a PDF string` của hyperref khi gặp tiếng Việt trong bookmark là
  **vô hại**.
- Trước khi nộp: điền thông tin sinh viên trên dòng tiêu đề, dán ảnh minh chứng (danh mục ở phụ
  lục B của bản đầy đủ) hoặc nộp kèm thư mục `../evidence/`.
