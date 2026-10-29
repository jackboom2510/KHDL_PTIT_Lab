# KHDL_PTIT_Lab — Introduction to Data Science

Repo bài thực hành môn **Introduction to Data Science (PTIT)**:

| Lab | Chủ đề | Thư mục | Đề bài |
| --- | --- | --- | --- |
| LAB 01 | SQL trên Google Cloud Shell với SQLite (S01–S21) | [`lab01_sql/`](lab01_sql/) | [PDF](Lab_01_SQL_Google_Cloud_Shell_IntroDataScience.pdf) |
| LAB 02 | NoSQL — MongoDB Atlas Free + PyMongo (N01–N22) | [`lab02_nosql/`](lab02_nosql/) | [PDF](Lab_02_NoSQL_MongoDB_Google_Cloud_IntroDataScience.pdf) |

> Trạng thái hiện tại: **đã dựng khung repo** (cấu trúc thư mục, tài liệu yêu cầu, kế hoạch).
> Bài giải sẽ được thêm theo các mốc trong [`PLAN.md`](PLAN.md).

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
│   ├── data/                  # sales.db (sinh tự động, không commit)
│   ├── sql/                   # schema.sql, seed.sql, answers.sql, explain.sql
│   ├── report/                # báo cáo PDF 2–3 trang
│   └── evidence/              # ảnh minh chứng
├── lab02_nosql/
│   ├── AGENTS.md
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
python3 build_db.py --force          # dựng data/sales.db từ sql/schema.sql + sql/seed.sql
python3 sql_console.py               # console tương tác: gõ SQL kết thúc bằng ';', EXIT để thoát
python3 generate_data.py --force     # sinh dữ liệu mở rộng 100 khách / 30 SP / 500 đơn / 1000 dòng
sqlite3 data/sales.db < sql/answers.sql   # chạy toàn bộ S01–S21 (nếu có sqlite3 CLI)
```

Kiểm tra nhanh dữ liệu mẫu: `customers = 5`, `products = 5`, `orders = 6`, `order_items = 8`.

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

- `StudentID_SQL.zip` — `sales.db`, `sql_console.py`, `answers.sql` (S01–S21), script sinh dữ
  liệu mở rộng, báo cáo PDF 2–3 trang, ảnh minh chứng.
- `StudentID_NoSQL.zip` — `connect.py`, `seed.py`, `lab_queries.py`, mã giải N01–N22, báo cáo
  PDF 2–3 trang, ảnh Data Explorer/terminal.

Đóng gói gợi ý (đặt trong `submission/`, thư mục này không được commit):

```bash
cd lab01_sql && zip -r ../submission/StudentID_SQL.zip \
  data/sales.db sql_console.py sql/schema.sql sql/seed.sql sql/answers.sql \
  sql/explain.sql build_db.py generate_data.py report evidence
cd ../lab02_nosql && zip -r ../submission/StudentID_NoSQL.zip \
  connect.py seed.py lab_queries.py n_answers.py generate_data.py report evidence
```

## Tài liệu tham khảo

- Google Cloud Shell: https://shell.cloud.google.com/
- SQLite — `sqlite3` module: https://docs.python.org/3/library/sqlite3.html
- SQLite — `EXPLAIN QUERY PLAN`: https://www.sqlite.org/eqp.html
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas/register
- PyMongo: https://pymongo.readthedocs.io/
- MongoDB aggregation `$lookup`: https://www.mongodb.com/docs/manual/reference/operator/aggregation/lookup/
