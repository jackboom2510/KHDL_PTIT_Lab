# AGENTS.md — Hướng dẫn cho AI agent / người làm bài

Repo này là bài thực hành môn **Introduction to Data Science (PTIT)**: LAB 01 (SQL trên
SQLite) và LAB 02 (NoSQL trên MongoDB Atlas). Hai đề bài gốc nằm ở thư mục gốc repo:

- `Lab_01_SQL_Google_Cloud_Shell_IntroDataScience.pdf`
- `Lab_02_NoSQL_MongoDB_Google_Cloud_IntroDataScience.pdf`

Đọc `PLAN.md` trước khi sửa bất cứ thứ gì. Kế hoạch và danh sách task nằm ở đó.

## 1. Nguyên tắc bắt buộc

1. **Không commit bí mật.** Không có URI MongoDB, mật khẩu Atlas, connection string, token
   hay API key trong bất kỳ file nào được track. Code MongoDB nhận URI qua `getpass()`
   hoặc biến môi trường; `.env` đã bị `.gitignore`.
2. **Không đổi đề.** Schema, tên bảng/cột, dữ liệu mẫu, mã câu hỏi (`S01…S21`, `N01…N22`)
   phải khớp PDF. Nếu cần thêm cột/collection phụ trợ thì ghi rõ lý do trong báo cáo.
3. **Không sửa tay 2 file PDF** và không xoá chúng.
4. **Chạy được từ đầu đến cuối.** Mọi script phải idempotent hoặc dừng an toàn khi dữ liệu
   đã tồn tại; không được phá dữ liệu của lần chạy trước một cách âm thầm.
5. **Không thêm dependency nặng.** LAB 01 chỉ dùng thư viện chuẩn Python (`sqlite3`,
   `random`, `csv`, `datetime`). LAB 02 chỉ thêm `pymongo[srv]`.
6. **Tiếng Việt** cho nhận xét/báo cáo; tên file, tên biến, SQL keyword dùng tiếng Anh.

## 2. Cấu trúc thư mục

```
.
├── AGENTS.md                  # file này
├── PLAN.md                    # kế hoạch + checklist S01–S21, N01–N22
├── README.md                  # tổng quan, cách chạy, cách nộp
├── docs/
│   ├── lab01_requirements.md  # trích yêu cầu LAB 01 từ PDF
│   └── lab02_requirements.md  # trích yêu cầu LAB 02 từ PDF
├── lab01_sql/
│   ├── AGENTS.md              # quy ước riêng LAB 01
│   ├── sql_console.py         # console SQLite (bắt buộc nộp)
│   ├── schema.sql             # CREATE TABLE
│   ├── seed.sql               # INSERT dữ liệu mẫu trong PDF
│   ├── answers.sql            # S01–S21, mỗi câu bắt đầu bằng `-- Sxx`
│   ├── explain.sql            # EXPLAIN QUERY PLAN trước/sau index (S15, S20)
│   ├── build_db.py            # dựng sales.db từ schema.sql + seed.sql
│   ├── generate_data.py       # sinh dữ liệu mở rộng (100/30/500/1000)
│   ├── data/                  # sales.db — sinh tự động, KHÔNG commit
│   ├── report/                # báo cáo PDF 2–3 trang
│   └── evidence/              # ảnh chụp màn hình minh chứng
├── lab02_nosql/
│   ├── AGENTS.md              # quy ước riêng LAB 02
│   ├── connect.py             # kết nối Atlas qua getpass (bắt buộc nộp)
│   ├── seed.py                # seed 3 collection mẫu (bắt buộc nộp)
│   ├── lab_queries.py         # ví dụ CRUD/aggregation trong PDF
│   ├── n_answers.py           # N01–N22
│   ├── generate_data.py       # sinh 500 đơn, mỗi đơn 1–5 sản phẩm
│   ├── data/                  # JSON/CSV trung gian — KHÔNG commit
│   ├── report/                # báo cáo PDF 2–3 trang
│   └── evidence/              # ảnh Data Explorer, terminal
└── submission/                # ZIP bài nộp — KHÔNG commit
```

## 3. Quy ước code

- Python 3.10+, 4 space, `snake_case`, type hint khi hàm dài; không cần framework.
- SQL viết HOA keyword, mỗi câu kết thúc `;`, comment đánh số câu ngay trước câu lệnh.
- Đường dẫn file trong script dùng `pathlib.Path(__file__).parent` — không hard-code
  `~/data_science/...` để chạy được cả trong repo lẫn Cloud Shell.
- Kết nối SQLite luôn bật `PRAGMA foreign_keys = ON`.
- Kết nối MongoDB luôn đặt `serverSelectionTimeoutMS` và gọi `client.admin.command('ping')`.
- Mọi lần chạy in kết quả ra stdout theo dạng bảng dễ copy vào báo cáo.

## 4. Định nghĩa "xong" cho mỗi lab

- [ ] Chạy lại từ repo sạch tạo được CSDL/dữ liệu không lỗi.
- [ ] Tất cả câu S01–S21 (hoặc N01–N22) có trong file đáp án, đúng mã, có kết quả chạy được.
- [ ] Có tối thiểu 3 ảnh minh chứng trong `evidence/` (tên file mô tả nội dung).
- [ ] Báo cáo 2–3 trang trong `report/` nêu kết quả + nhận xét, không dán code.
- [ ] `README.md` cập nhật lệnh chạy mới nếu có.
- [ ] Không có secret trong `git diff`.

## 5. Git

- Commit nhỏ, message dạng `lab01: add answers.sql for S01-S15`.
- Không commit `*.db`, `.venv/`, `__pycache__/`, `submission/*.zip`, `.env`.
- Trước khi commit chạy `git status` và tự kiểm tra không có dữ liệu lớn/không có mật khẩu.
