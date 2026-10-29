# Báo cáo LAB 01 — LaTeX

`lab01_report.tex` là báo cáo đầy đủ của LAB 01 (SQL/SQLite), viết bằng pdfLaTeX + `vntex`
(hỗ trợ tiếng Việt chuẩn, có ngắt từ đúng).

## Nội dung báo cáo

| Phần | Nội dung |
| --- | --- |
| Trang bìa | điền tay: giảng viên, họ tên, MSSV, lớp, nhóm |
| Tóm tắt | mục tiêu + kết quả chính |
| 1 | Giới thiệu, mục tiêu, bảng phân chia bắt buộc/bổ sung |
| 2 | Môi trường, quy trình, yêu cầu "chạy lặp an toàn" |
| 3 | Mô hình dữ liệu: sơ đồ quan hệ (TikZ), schema, phân tích ràng buộc |
| 4 | Dữ liệu mẫu, đối chiếu 5/5/6/8, kiểm tra khoá ngoại |
| 5 | Kết quả S01–S15 (bảng kết quả thật, giải thích từng nhóm) |
| 6 | Index + EXPLAIN: SCAN → SEARCH / COVERING INDEX, vì sao không đo bằng thời gian |
| 7 | Kết quả S16–S21 trên dữ liệu mở rộng, gồm bảng so sánh `#table`/`##table`/`tempdb` |
| 8 | Thảo luận, bài học |
| 9 | Kết luận |
| Phụ lục A–D | cấu trúc bài nộp, lệnh tái lập, danh mục ảnh minh chứng, trích mã, bảng đối chiếu rubric |

## Biên dịch

```bash
cd lab01_sql/report
bash compile.sh          # bản đầy đủ
bash compile.sh short    # bản gọn ~3 trang (tắt phụ lục)
```

Hoặc thủ công (chạy 2 lần để có mục lục và `\ref`):

```bash
pdflatex lab01_report.tex && pdflatex lab01_report.tex
```

Trên **Overleaf**: tạo project → upload thư mục `report/` → chọn compiler **pdfLaTeX** →
Recompile. Không cần cài gì thêm vì Overleaf có sẵn `vntex`.

## Yêu cầu gói TeX

`vntex` (đi kèm `babel-vietnamese`), `booktabs`, `tabularx`, `longtable`, `multirow`,
`enumitem`, `caption`, `fancyhdr`, `hyperref`, `listings`, `tikz` (`arrows.meta`).

Trên Debian/Ubuntu:

```bash
sudo apt-get install texlive-latex-extra texlive-lang-other texlive-fonts-recommended latexmk
```

## Công tắc phụ lục

Ở đầu file có:

```latex
\newif\ifwithappendix
\withappendixtrue    % đổi thành \withappendixfalse để bỏ toàn bộ phụ lục
```

Đề bài ghi báo cáo 2–3 trang; phần thân báo cáo (mục 1–9) đã chứa đủ nội dung chấm điểm, còn
phụ lục dùng để nộp kèm khi không giới hạn số trang. Nếu cần đúng 2–3 trang, dùng
`bash compile.sh short` và cân nhắc bỏ bớt Bảng 4–5 nếu vẫn quá dài.

## Phương án XeLaTeX (khi máy không có `vntex`)

Thay ba dòng đầu phần "Tiếng Việt" bằng:

```latex
% bỏ: inputenc, fontenc T5, babel vietnamese
\usepackage{fontspec}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
```

rồi biên dịch bằng `xelatex` (2 lần) hoặc `latexmk -xelatex`. DejaVu có đủ glyph tiếng Việt và
đi kèm TeX Live; đổi `DejaVu Serif` thành font khác nếu muốn (Noto Serif, Liberation Serif…).
Nhược điểm: không có ngắt từ tiếng Việt như `vntex`.

## Ghi chú

- Mọi số liệu trong báo cáo được lấy từ lần chạy thật trong repo
  (`build_db.py`, `run_sql.py`, `generate_data.py`, `explain.sql`) — xem `../PLAN.md` mục 5.
- Cảnh báo `Token not allowed in a PDF string` của hyperref khi gặp tiếng Việt trong bookmark là
  **vô hại**, không ảnh hưởng nội dung PDF.
- Trước khi nộp: điền trang bìa, dán ảnh minh chứng (danh mục ở Phụ lục B) hoặc nộp kèm thư mục
  `../evidence/`, và đặt tên PDF theo MSSV nếu giảng viên yêu cầu.
