# AGENTS.md — LAB 01 (SQL / SQLite)

Áp dụng cùng `../AGENTS.md`. File này bổ sung quy ước riêng cho lab SQL.

## Phạm vi

- Đề: `../Lab_01_SQL_Google_Cloud_Shell_IntroDataScience.pdf`.
- Task: S01–S21, xem bảng trong `../PLAN.md` mục 1 và `../docs/lab01_requirements.md`.
- Chỉ dùng thư viện chuẩn Python (`sqlite3`, `random`, `csv`, `datetime`, `pathlib`).
  Không cài pandas/SQLAlchemy/Faker.

## File và trách nhiệm

| File | Vai trò | Bắt buộc nộp |
| --- | --- | --- |
| `sql_console.py` | Console SQLite tương tác, dừng câu lệnh bằng `;`, thoát bằng `EXIT`, giữ buffer nhiều dòng | ✅ |
| `schema.sql` | `CREATE TABLE` cho 4 bảng, đúng tên cột và ràng buộc như PDF | nên có |
| `seed.sql` | `INSERT` dữ liệu mẫu PDF (5/5/6/8 dòng) | nên có |
| `answers.sql` | Toàn bộ S01–S21, mỗi câu mở đầu bằng comment `-- Sxx: <mô tả>` | ✅ |
| `explain.sql` | Cặp `EXPLAIN QUERY PLAN` trước/sau index cho S15 và S20, kèm comment nhận xét | ✅ |
| `build_db.py` | Đọc `schema.sql` + `seed.sql`, tạo lại `data/sales.db` | nên có |
| `generate_data.py` | Sinh dữ liệu mở rộng (100 khách / 30 sản phẩm / 500 đơn / 1.000 dòng đơn) | ✅ |
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

- `evidence/` đặt tên `01_env.png`, `02_tables_count.png`, `03_s08_result.png`,
  `04_explain_before_after.png`, `05_expanded_counts.png`, `06_rank.png`…
- Báo cáo `report/lab01_report.md` → xuất PDF 2–3 trang, cấu trúc: môi trường → mô hình dữ
  liệu → kết quả S01–S15 → mở rộng + index → nhận xét S21.

## Kiểm tra trước khi nộp (chạy được trong sandbox)

```bash
python3 build_db.py --force
python3 -c "import sqlite3;print(sqlite3.connect('data/sales.db').execute('select count(*) from order_items').fetchone())"
sqlite3 data/sales.db < answers.sql   # nếu có sqlite3 CLI; nếu không dùng sql_console.py
python3 generate_data.py --force
sqlite3 data/sales.db < explain.sql
```
