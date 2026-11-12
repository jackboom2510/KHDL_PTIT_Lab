# KHDL_PTIT_Lab — Introduction to Data Science

Repo bài thực hành môn **Introduction to Data Science (PTIT)**:

| Lab | Chủ đề | Thư mục | Đề bài |
| --- | --- | --- | --- |
| LAB 01 | SQL trên Google Cloud Shell với SQLite (S01–S21) | [`lab01_sql/`](lab01_sql/) | [PDF](Lab_01_SQL_Google_Cloud_Shell_IntroDataScience.pdf) |
| LAB 02 | NoSQL — MongoDB Atlas Free + PyMongo (N01–N22) | [`lab02_nosql/`](lab02_nosql/) | [PDF](Lab_02_NoSQL_MongoDB_Google_Cloud_IntroDataScience.pdf) |

> Trạng thái hiện tại: **LAB 01 đã hoàn thành và chạy kiểm chứng** (S01–S21); LAB 02 đang ở bước
> thiết lập. Tiến độ chi tiết: [`PLAN.md`](PLAN.md).

## Cấu trúc

```
.
├── AGENTS.md                  # quy ước chung khi làm bài / cho AI agent
├── PLAN.md                    # kế hoạch, checklist S01–S21 và N01–N22
├── README.md
├── docs/
│   ├── lab01_requirements.md  # trích yêu cầu LAB 01 từ PDF
│   └── lab02_requirements.md  # trích yêu cầu LAB 02 từ PDF
├── lab01_sql/
│   ├── AGENTS.md
│   ├── sql_console.py         # console SQLite (bắt buộc nộp)
│   ├── build_db.py            # dựng data/sales.db từ sql/ + kiểm tra count
│   ├── generate_data.py       # sinh data/sales_extended.db (100/30/500/1500)
│   ├── run_sql.py             # chạy file .sql bằng Python (khi không có sqlite3 CLI)
│   ├── utf8_console.py        # ép stdout UTF-8 (bắt buộc trên Windows cp1252)
│   ├── sql/
│   │   ├── schema.sql         # 4 bảng + khoá ngoại
│   │   ├── seed.sql           # dữ liệu mẫu đúng đề (5/5/6/8)
│   │   ├── answers.sql        # BẮT BUỘC  — S01–S15
│   │   ├── answers_homework.sql # BỔ SUNG — S16–S21
│   │   └── explain.sql        # EXPLAIN trước/sau index (S15, S20)
│   ├── data/                  # sales.db, sales_extended.db (sinh tự động, không commit)
│   ├── evidence/              # ảnh chụp minh chứng (11 PNG, chụp trên Cloud Shell)
│   │   ├── HUONG_DAN_CHUP_ANH.md  # 7 nhóm ảnh: lệnh cần chạy, nội dung cần thấy
│   │   └── capture_commands.sh    # in/chạy lần lượt các lệnh để chụp
│   ├── pack_submission.sh     # đóng gói submission/StudentID_SQL.zip
│   ├── report/                # báo cáo PDF 4–5 trang, đen trắng
│   │   ├── make_report.py     # sinh PDF theo 5 tiêu chí chấm (fpdf2, không cần TeX)
│   │   ├── requirements.txt   # fpdf2 + pillow
│   │   ├── pdf_pages.py       # đếm số trang PDF
│   │   ├── BaoCao_LAB01_B23DCKH105.pdf  # bản đã xuất (4 trang, 5 trang khi có ảnh)
│   │   └── README.md          # cách xuất báo cáo, quy ước trình bày
├── lab02_nosql/
│   ├── AGENTS.md
│   ├── connect.py             # getpass + ping -> database sales_nosql
│   ├── seed.py                # nạp 5 khách / 5 SP / 6 đơn, items nhúng
│   ├── lab_queries.py         # ví dụ CRUD / truy vấn trong đề
│   ├── n_answers.py           # BẮT BUỘC  — N01–N15
│   ├── n_homework.py          # BỔ SUNG — N16–N22
│   ├── generate_data.py       # 100 khách / 30 SP / 500 đơn / 1.521 dòng items
│   ├── check_offline.py       # chạy thử N01–N22 bằng mongomock (không cần Atlas)
│   ├── utf8_console.py        # ép stdout UTF-8 (Windows)
│   ├── pack_submission.sh     # đóng gói submission/StudentID_NoSQL.zip
│   ├── data/                  # JSON kết quả chạy (không commit)
│   ├── report/                # make_report.py (PDF) + make_docx.py (Word có khung ảnh)
│   └── evidence/              # 7 ảnh chụp Atlas/Cloud Shell + hướng dẫn chụp
└── submission/                # ZIP bài nộp (không commit)
```

Quy ước chi tiết: [`AGENTS.md`](AGENTS.md), [`lab01_sql/AGENTS.md`](lab01_sql/AGENTS.md),
[`lab02_nosql/AGENTS.md`](lab02_nosql/AGENTS.md).

## Chạy LAB 01 (SQL) — local hoặc Cloud Shell

Chỉ cần Python 3 (thư viện chuẩn `sqlite3`), không cần cài thêm gì.

```bash
cd lab01_sql

# 1) Dữ liệu mẫu trong đề
python3 build_db.py --force            # 5 khách / 5 SP / 6 đơn / 8 dòng đơn
python3 sql_console.py                 # console: gõ SQL kết thúc bằng ';', EXIT để thoát

# 2) Phần BẮT BUỘC — S01–S15 (data/sales.db)
python3 run_sql.py sql/answers.sql
# hoặc nếu máy có sqlite3 CLI:
# sqlite3 data/sales.db < sql/answers.sql

# 3) Dữ liệu mở rộng + phần BỔ SUNG — S16–S21
python3 generate_data.py --force       # 100 khách / 30 SP / 500 đơn / 1.500 dòng đơn
python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db

# 4) Chứng minh index: SCAN orders -> SEARCH ... USING INDEX
python3 run_sql.py sql/explain.sql
python3 run_sql.py sql/explain.sql --db data/sales_extended.db
```

Kiểm tra nhanh dữ liệu mẫu: `customers = 5`, `products = 5`, `orders = 6`, `order_items = 8`.

### Chạy trên Windows

Nếu console mặc định không phải UTF-8 (cp1252/cp437), Python sẽ chết khi in tiếng Việt:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u0110' in position 0
```

Các script (`build_db.py`, `generate_data.py`, `run_sql.py`, `sql_console.py`,
`report/make_report.py`) đã tự gọi `utf8_console.enable_utf8()` — bật code page 65001 và ép
`stdout`/`stderr` sang UTF-8. Không cần đặt biến môi trường. Nếu vẫn gặp lỗi font, chạy
`chcp 65001` trước hoặc dùng Windows Terminal / Git Bash.

`pack_submission.sh` chạy được trong Git Bash: tự chọn `python3`/`python`/`py` và dùng Python
`zipfile` khi máy không có lệnh `zip`.

### Ảnh minh chứng (tự chụp) và báo cáo PDF

Ảnh minh chứng phải là **ảnh chụp thật** trên `shell.cloud.google.com`, không dùng ảnh dựng lại
bằng script. Danh sách lệnh cần chạy và nội dung cần thấy của từng ảnh:

```bash
cd lab01_sql/evidence
cat HUONG_DAN_CHUP_ANH.md               # 7 nhóm ảnh: lệnh, kết quả kỳ vọng, lưu ý che thông tin
bash capture_commands.sh                # in lần lượt 7 nhóm lệnh
bash capture_commands.sh --only 05      # chỉ nhóm lệnh của ảnh 05
bash capture_commands.sh --run          # chạy luôn chứ không chỉ in
# lưu ảnh theo đúng tên: 01_env.png … 07_s19_rank_03.png (nhóm dài chụp nhiều ảnh _01, _02)
```

```bash
cd lab01_sql/report
pip install -r requirements.txt         # fpdf2 + pillow
python3 make_report.py                  # báo cáo 4 trang (chưa chèn ảnh)
python3 make_report.py --images ../evidence   # chèn 11 ảnh thật -> 5 trang
```

Báo cáo ngắn 4–5 trang, đen trắng, tổ chức theo 5 tiêu chí chấm; tự thu nhỏ ảnh nếu vượt 5
trang. Chi tiết: [`lab01_sql/report/README.md`](lab01_sql/report/README.md).

### Đóng gói nộp bài

```bash
bash lab01_sql/pack_submission.sh 22CNTT0123
# -> submission/22CNTT0123_SQL.zip: data/sales.db, sql_console.py, sql/answers.sql (S01–S15),
#    sql/answers_homework.sql (S16–S21), sql/explain.sql, generator, report PDF 4–5 trang,
#    11 ảnh minh chứng, README_MAPPING.txt ánh xạ yêu cầu -> file.
```

Không cần TeX: PDF sinh bằng Python (fpdf2). `answers.sql` chạy lại nhiều lần vẫn sạch: S05 chỉ nhân 10% khi Mouse còn ở giá gốc 250.000,
S06 xoá đúng khách vừa thêm.

## Chạy LAB 02 (MongoDB Atlas)

Cần cluster Atlas **M0 Free**, user `student_lab`, và IP Cloud Shell đã được allowlist.

```bash
cd lab02_nosql
python3 -m venv .venv && source .venv/bin/activate
pip install "pymongo[srv]"

python3 connect.py        # dán URI mongodb+srv://... khi được hỏi (ký tự không hiển thị)
python3 seed.py           # seed 3 collection mẫu 5/5/6 (chỉ chạy trên DB rỗng)
python3 lab_queries.py    # ví dụ CRUD + truy vấn trong đề

# Phần BẮT BUỘC — N01–N15 (n_answers.py), xuất kèm JSON cho báo cáo
python3 n_answers.py --json data/lab02_results_n01_n15.json

# Phần BỔ SUNG — dữ liệu mở rộng rồi N16–N22 (n_homework.py)
python3 generate_data.py --force
python3 n_homework.py --json data/lab02_results_n16_n22.json

# Kiểm tra nhanh không cần Atlas (mongomock) — bắt lỗi pipeline trước khi chạy thật
pip install mongomock
python3 check_offline.py
```

Báo cáo PDF 4–5 trang, đen trắng, theo 5 tiêu chí chấm (giống LAB 01):

```bash
python3 lab02_nosql/report/make_report.py \
    --images lab02_nosql/evidence \
    --results lab02_nosql/data/lab02_results_n01_n15.json \
              lab02_nosql/data/lab02_results_n16_n22.json
```

Bản Word để tự dán ảnh chụp (7 khung nét đứt đặt đúng vị trí ảnh, mỗi khung ghi tên tệp và
nội dung phải thấy):

```bash
pip install python-docx
python3 lab02_nosql/report/make_docx.py                      # khung trống để dán ảnh
python3 lab02_nosql/report/make_docx.py --images lab02_nosql/evidence   # chèn ảnh đã chụp
```

Bản Word không nằm trong ZIP nộp bài (ZIP chỉ cần báo cáo PDF); chi tiết:
[`lab02_nosql/report/README.md`](lab02_nosql/report/README.md).

Ảnh minh chứng (7 ảnh chụp thật trên Atlas + Cloud Shell) xem
[`lab02_nosql/evidence/HUONG_DAN_CHUP_ANH.md`](lab02_nosql/evidence/HUONG_DAN_CHUP_ANH.md).

**Không bao giờ** ghi URI có mật khẩu vào file, ảnh chụp hay commit. Nếu IP Cloud Shell đổi:
`curl -4 https://api.ipify.org` rồi cập nhật Atlas → Network Access.

## Nộp bài

- `StudentID_SQL.zip` — `data/sales.db`, `sql_console.py`, `sql/answers.sql` (S01–S15),
  `sql/answers_homework.sql` (S16–S21), `sql/explain.sql`, `build_db.py`, `generate_data.py`,
  `run_sql.py`, báo cáo PDF 4–5 trang, ảnh minh chứng.
- `StudentID_NoSQL.zip` — `connect.py`, `seed.py`, `lab_queries.py`, `n_answers.py` (N01–N15),
  `n_homework.py` (N16–N22), `generate_data.py`, `check_offline.py`, báo cáo PDF 4–5 trang, 7 ảnh
  minh chứng, `README_MAPPING.txt`.

Đóng gói bằng script (tự kiểm tra secret, tự chọn `zip`/`zipfile`, đặt trong `submission/` —
thư mục này không được commit):

```bash
bash lab01_sql/pack_submission.sh B23DCKH105    # -> submission/B23DCKH105_SQL.zip
bash lab02_nosql/pack_submission.sh B23DCKH105  # -> submission/B23DCKH105_NoSQL.zip
```

## Tài liệu tham khảo

- Google Cloud Shell: https://shell.cloud.google.com/
- SQLite — `sqlite3` module: https://docs.python.org/3/library/sqlite3.html
- SQLite — `EXPLAIN QUERY PLAN`: https://www.sqlite.org/eqp.html
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas/register
- PyMongo: https://pymongo.readthedocs.io/
- MongoDB aggregation `$lookup`: https://www.mongodb.com/docs/manual/reference/operator/aggregation/lookup/
