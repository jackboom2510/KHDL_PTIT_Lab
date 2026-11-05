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
│   ├── sql/
│   │   ├── schema.sql         # 4 bảng + khoá ngoại
│   │   ├── seed.sql           # dữ liệu mẫu đúng đề (5/5/6/8)
│   │   ├── answers.sql        # BẮT BUỘC  — S01–S15
│   │   ├── answers_homework.sql # BỔ SUNG — S16–S21
│   │   └── explain.sql        # EXPLAIN trước/sau index (S15, S20)
│   ├── data/                  # sales.db, sales_extended.db (sinh tự động, không commit)
│   ├── evidence/              # ảnh chụp minh chứng (7 PNG, chụp trên Cloud Shell)
│   │   ├── HUONG_DAN_CHUP_ANH.md  # 7 ảnh: lệnh cần chạy, nội dung cần thấy
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
│   ├── n_answers.py           # BẮT BUỘC  — N01–N15 (sẽ thêm ở M4)
│   ├── n_homework.py          # BỔ SUNG — N16–N22 (sẽ thêm ở M5)
│   ├── data/                  # dữ liệu trung gian (không commit)
│   ├── report/
│   └── evidence/
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

### Ảnh minh chứng (tự chụp) và báo cáo PDF

Ảnh minh chứng phải là **ảnh chụp thật** trên `shell.cloud.google.com`, không dùng ảnh dựng lại
bằng script. Danh sách lệnh cần chạy và nội dung cần thấy của từng ảnh:

```bash
cd lab01_sql/evidence
cat HUONG_DAN_CHUP_ANH.md               # 7 ảnh: lệnh, kết quả kỳ vọng, lưu ý che thông tin
bash capture_commands.sh                # in lần lượt 7 nhóm lệnh
bash capture_commands.sh --only 05      # chỉ nhóm lệnh của ảnh 05
bash capture_commands.sh --run          # chạy luôn chứ không chỉ in
# lưu ảnh theo đúng tên: 01_env.png … 07_s19_rank.png
```

```bash
cd lab01_sql/report
pip install -r requirements.txt         # fpdf2 + pillow
python3 make_report.py                  # báo cáo 4 trang (chưa chèn ảnh)
python3 make_report.py --images ../evidence   # chèn 7 ảnh thật -> 5 trang
```

Báo cáo ngắn 4–5 trang, đen trắng, tổ chức theo 5 tiêu chí chấm; tự thu nhỏ ảnh nếu vượt 5
trang. Chi tiết: [`lab01_sql/report/README.md`](lab01_sql/report/README.md).

### Đóng gói nộp bài

```bash
bash lab01_sql/pack_submission.sh 22CNTT0123
# -> submission/22CNTT0123_SQL.zip: data/sales.db, sql_console.py, sql/answers.sql (S01–S15),
#    sql/answers_homework.sql (S16–S21), sql/explain.sql, generator, report PDF 4–5 trang,
#    7 ảnh minh chứng, README_MAPPING.txt ánh xạ yêu cầu -> file.
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
python3 seed.py           # seed 3 collection mẫu (chỉ chạy trên DB rỗng)
python3 lab_queries.py    # ví dụ CRUD + aggregation trong đề
python3 n_answers.py      # đáp án N01–N22
```

**Không bao giờ** ghi URI có mật khẩu vào file, ảnh chụp hay commit. Nếu IP Cloud Shell đổi:
`curl -4 https://api.ipify.org` rồi cập nhật Atlas → Network Access.

## Nộp bài

- `StudentID_SQL.zip` — `data/sales.db`, `sql_console.py`, `sql/answers.sql` (S01–S15),
  `sql/answers_homework.sql` (S16–S21), `sql/explain.sql`, `build_db.py`, `generate_data.py`,
  `run_sql.py`, báo cáo PDF 4–5 trang, ảnh minh chứng.
- `StudentID_NoSQL.zip` — `connect.py`, `seed.py`, `lab_queries.py`, mã giải N01–N22, báo cáo
  PDF 2–3 trang, ảnh Data Explorer/terminal.

Đóng gói gợi ý (đặt trong `submission/`, thư mục này không được commit):

```bash
cd lab01_sql && zip -r ../submission/StudentID_SQL.zip \
  data/sales.db sql_console.py build_db.py generate_data.py run_sql.py \
  sql/schema.sql sql/seed.sql sql/answers.sql sql/answers_homework.sql sql/explain.sql \
  report evidence
cd ../lab02_nosql && zip -r ../submission/StudentID_NoSQL.zip \
  connect.py seed.py lab_queries.py n_answers.py n_homework.py generate_data.py report evidence
```

## Tài liệu tham khảo

- Google Cloud Shell: https://shell.cloud.google.com/
- SQLite — `sqlite3` module: https://docs.python.org/3/library/sqlite3.html
- SQLite — `EXPLAIN QUERY PLAN`: https://www.sqlite.org/eqp.html
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas/register
- PyMongo: https://pymongo.readthedocs.io/
- MongoDB aggregation `$lookup`: https://www.mongodb.com/docs/manual/reference/operator/aggregation/lookup/
