# AGENTS.md — LAB 01 (SQL / SQLite)

Áp dụng cùng `../AGENTS.md`. File này bổ sung quy ước riêng cho lab SQL.

## Phạm vi

- Đề: `../Lab_01_SQL_Google_Cloud_Shell_IntroDataScience.pdf`.
- Task: S01–S21, xem bảng trong `../PLAN.md` mục 1 và `../docs/lab01_requirements.md`.
- Chỉ dùng thư viện chuẩn Python (`sqlite3`, `random`, `csv`, `datetime`, `pathlib`).
  Không cài pandas/SQLAlchemy/Faker.

## File và trách nhiệm

### Tách phần bắt buộc và phần bổ sung

Bài **bắt buộc** (S01–S15) và bài **bổ sung/về nhà** (S16–S21) **luôn nằm ở hai file riêng**,
không trộn chung. Lý do: phần bắt buộc chạy trên `data/sales.db` (dữ liệu mẫu trong đề), phần
bổ sung cần dữ liệu lớn trong `data/sales_extended.db`; tách file còn giúp người chấm thấy ngay
phần nào là yêu cầu tối thiểu, phần nào là mở rộng.

| Phần | File | CSDL đích | Nội dung |
| --- | --- | --- | --- |
| Bắt buộc | `sql/answers.sql` | `data/sales.db` | S01–S15 |
| Bổ sung / về nhà | `sql/answers_homework.sql` | `data/sales_extended.db` | S16–S21 |
| Chứng minh index | `sql/explain.sql` | cả hai | EXPLAIN trước/sau index (S15), sau mở rộng (S20) |

### File và trách nhiệm

| File | Vai trò | Bắt buộc nộp |
| --- | --- | --- |
| `sql_console.py` | Console SQLite tương tác, dừng câu lệnh bằng `;`, thoát bằng `EXIT`, giữ buffer nhiều dòng | ✅ |
| `sql/schema.sql` | `CREATE TABLE` cho 4 bảng, đúng tên cột và ràng buộc như PDF | nên có |
| `sql/seed.sql` | `INSERT` dữ liệu mẫu PDF (5/5/6/8 dòng) | nên có |
| `sql/answers.sql` | **S01–S15** (bắt buộc), mỗi câu mở đầu bằng comment `-- Sxx: <mô tả>` | ✅ |
| `sql/answers_homework.sql` | **S16–S21** (bổ sung), cùng quy ước comment `-- Sxx:` | ✅ |
| `sql/explain.sql` | `EXPLAIN QUERY PLAN` trước/sau index, tự DROP + CREATE index để chạy lại được | ✅ |
| `build_db.py` | Đọc `schema.sql` + `seed.sql`, tạo lại `data/sales.db`, in count để tự kiểm tra | nên có |
| `generate_data.py` | Sinh `data/sales_extended.db` (100 khách / 30 SP / 500 đơn / 1.500 dòng đơn) | ✅ |
| `run_sql.py` | Chạy file `.sql` bằng Python khi máy không có sqlite3 CLI, in kết quả từng câu | nên có |
| `data/sales.db` | CSDL sinh tự động — không commit, nhưng phải có trong file ZIP nộp | ✅ (trong ZIP) |

## Quy ước SQL

- Keyword viết HOA, tên bảng/cột `snake_case` như PDF, mỗi câu kết thúc `;`.
- `answers.sql` chạy được tuần tự bằng:
  `sqlite3 data/sales.db < answers.sql`. Vì vậy S04 (INSERT) và S06 (DELETE) phải đối xứng:
  thêm khách `customer_id = 6` rồi xoá đúng khách đó để chạy lại vẫn sạch.
- S05 tăng giá Mouse 10% là thao tác **có ghi**: dùng `UPDATE` theo `product_id = 102` và
  comment ghi rõ giá gốc, để người chấm hiểu đây là thay đổi dữ liệu có chủ đích.
- Mọi truy vấn đọc nên có `ORDER BY` để kết quả ổn định giữa các lần chạy.
- Với S10, S12, S13 dùng alias rõ nghĩa (`revenue`, `order_count`), không dùng `SUM(...)` trần
  trong `HAVING` nếu đã đặt alias — SQLite cho phép alias trong `HAVING`, ghi chú điểm này.

## Quy ước Python

- Mở kết nối: `sqlite3.connect(path)`, sau đó `con.execute('PRAGMA foreign_keys = ON')`.
- `build_db.py` phải xoá file db cũ trước khi dựng (hoặc dừng nếu đã tồn tại và không có `--force`).
  Không bao giờ dựng đè âm thầm khi người dùng đang có dữ liệu mở rộng.
- `generate_data.py` dùng `random.seed(2026)` để tái lập được; in ra số dòng từng bảng ở cuối.
- Đường dẫn: `BASE = Path(__file__).resolve().parent`, db ở `BASE / 'data' / 'sales.db'`.

## Index và EXPLAIN

- `CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);` trong `answers.sql`
  đặt ngay tại S14 (sau các câu truy vấn, trước S15).
- Trong `explain.sql`, ghi cả output trước và sau index, chú thích `SCAN orders` →
  `SEARCH orders USING INDEX idx_orders_customer`.
- Không được sửa `explain.sql` bằng tay cho đẹp: output phải copy nguyên từ terminal.

## Báo cáo và minh chứng

- Báo cáo viết bằng LaTeX: `report/lab01_report.tex`, biên dịch bằng `bash report/compile.sh`
  (hoặc Overleaf, compiler pdfLaTeX, cần `vntex`). Công tắc `\withappendixtrue|false` ở đầu file
  quyết định có phụ lục hay bản gọn ~3 trang.
- Số liệu trong báo cáo **phải khớp** output thật của `run_sql.py`; khi sửa dữ liệu/seed phải
  chạy lại các lệnh ở mục "Kiểm tra trước khi nộp" và cập nhật bảng trong báo cáo.
- `evidence/` đặt tên `01_env.png`, `02_tables_count.png`, `03_s08_result.png`,
  `04_explain_before_after.png`, `05_expanded_counts.png`, `06_rank.png`…
- Báo cáo `report/lab01_report.md` → xuất PDF 2–3 trang, cấu trúc: môi trường → mô hình dữ
  liệu → kết quả S01–S15 → mở rộng + index → nhận xét S21.

## Kiểm tra trước khi nộp (chạy được trong sandbox)

```bash
cd lab01_sql
python3 build_db.py --force                 # kỳ vọng 5 / 5 / 6 / 8
python3 run_sql.py sql/answers.sql          # S01–S15, kỳ vọng "0 lỗi"
python3 run_sql.py sql/answers.sql          # chạy lần 2: vẫn 0 lỗi (kiểm tra idempotent)
python3 generate_data.py --force            # 100 / 30 / 500 / 1500, foreign_key_check ok
python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db
python3 run_sql.py sql/explain.sql          # SCAN orders -> SEARCH ... INDEX
python3 run_sql.py sql/explain.sql --db data/sales_extended.db
```

Nếu máy có sqlite3 CLI thì các lệnh trên tương đương
`sqlite3 data/sales.db < sql/answers.sql`.
