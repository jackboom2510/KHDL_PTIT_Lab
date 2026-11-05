# Hướng dẫn chụp ảnh minh chứng trên Google Cloud Shell

Mục đích: ảnh minh chứng phải là ảnh chụp màn hình **thật** khi chạy trên
https://shell.cloud.google.com, không phải ảnh dựng lại. Tài liệu này liệt kê đúng lệnh cần
chạy và nội dung cần thấy trong từng ảnh.

Bài nộp cần 7 ảnh, đặt trong `lab01_sql/evidence/` với tên tệp như bảng dưới. Tên tệp khớp với
danh mục ảnh trong báo cáo (`report/make_report.py`).

| Tệp | Nội dung ảnh | Mục trong báo cáo |
| --- | --- | --- |
| `01_env.png` | `whoami`, `pwd`, phiên bản Python và SQLite | 2 — Tiêu chí 1 (cài đặt, dữ liệu) |
| `02_tables_count.png` | Tạo 4 bảng + số dòng 5/5/6/8 + `foreign_key_check` | 2 — Tiêu chí 1 (cài đặt, dữ liệu) |
| `03_console.png` | `sql_console.py`: câu lệnh nhiều dòng, một câu sai, `EXIT` | 3 — Tiêu chí 2 (CRUD) |
| `04_s08_result.png` | Kết quả S08 và S09 | 4 — Tiêu chí 3 (truy vấn nâng cao) |
| `05_explain_before_after.png` | `EXPLAIN QUERY PLAN` trước và sau index | 5 — Tiêu chí 4 (index) |
| `06_expanded_counts.png` | Sinh dữ liệu mở rộng 100/30/500/1500 | 6 — Tiêu chí 5 (mở rộng) |
| `07_s19_rank.png` | S19 với cột `rank` và `dense_rank` | 6 — Tiêu chí 5 (mở rộng) |

---

## Bước 0 — Chuẩn bị môi trường (làm một lần)

Mở https://shell.cloud.google.com, đăng nhập bằng Gmail cá nhân, chờ terminal hiện ra. Không cần
bật Billing. Chọn chế độ lưu trữ `$HOME` (không chọn Ephemeral).

Trên Cloud Shell, lấy mã nguồn về (thay `<repo>` bằng đường dẫn repo của bạn), rồi vào thư mục
lab:

```bash
git clone <repo-url> KHDL_PTIT_Lab
cd KHDL_PTIT_Lab/lab01_sql
pwd            # phải kết thúc bằng .../lab01_sql
```

Nếu không dùng Git, có thể upload cả thư mục `lab01_sql` bằng nút Upload trong Cloud Shell.

Kiểm tra nhanh trước khi chụp ảnh (không cần chụp bước này):

```bash
python3 --version
python3 -c "import sqlite3; print('SQLite', sqlite3.sqlite_version)"
```

---

## Ảnh 1 — `01_env.png` (môi trường thực hành)

```bash
whoami
pwd
python3 --version
python3 -c "import sqlite3; print('SQLite', sqlite3.sqlite_version)"
sqlite3 --version
```

Cần thấy trong ảnh: tên tài khoản, đường dẫn có `lab01_sql`, phiên bản Python, phiên bản SQLite.
Nếu máy không có `sqlite3` CLI thì bỏ dòng cuối, chỉ cần phiên bản từ Python.

Chụp: chọn vùng terminal (không cần cả thanh trình duyệt), lưu thành `01_env.png`.

---

## Ảnh 2 — `02_tables_count.png` (cài đặt và tạo dữ liệu)

```bash
python3 build_db.py --force
python3 run_sql.py --sql "SELECT 'customers' AS bang, COUNT(*) FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;"
python3 run_sql.py --sql "PRAGMA foreign_key_check;"
```

Cần thấy: 4 dòng `customers 5`, `products 5`, `orders 6`, `order_items 8` và kết quả
`foreign_key_check` rỗng (không có dòng vi phạm).

Nếu muốn ảnh gọn, chụp phần output của `build_db.py` và phần bảng kết quả, không cần chụp lệnh
`UNION ALL` quá dài.

---

## Ảnh 3 — `03_console.png` (console SQL, CRUD và câu cơ bản)

```bash
python3 sql_console.py
```

Trong console, nhập lần lượt (dấu nhắc `SQL>` và `...` cho câu nhiều dòng):

```sql
SELECT city, COUNT(*) AS so_khach
FROM customers
GROUP BY city
ORDER BY so_khach DESC;
SELECT name, price FROM products ORDER BY price DESC LIMIT 3;
SELECT * FROM bang_khong_ton_tai;
EXIT
```

Cần thấy: câu lệnh nhiều dòng được gộp đúng, một thông báo `SQL error: no such table: ...` cho
câu sai (console không bị thoát), và thoát bằng `EXIT`.

---

## Ảnh 4 — `04_s08_result.png` (truy vấn nâng cao)

```bash
python3 run_sql.py sql/answers.sql
```

Chụp đoạn output của **S08** (tổng tiền từng đơn) và **S09** (doanh thu từng khách). Kỳ vọng:
6 đơn, đơn 1001 = 15550000.0; tổng 6 đơn = 44125000; khách An (id 1) = 17150000.0.

Nếu ảnh quá dài, chạy riêng hai câu để chụp:

```bash
python3 run_sql.py --sql "SELECT o.order_id, SUM(i.quantity*p.price) AS total
FROM orders o JOIN order_items i ON i.order_id=o.order_id
JOIN products p ON p.product_id=i.product_id
GROUP BY o.order_id ORDER BY total DESC;"
```

---

## Ảnh 5 — `05_explain_before_after.png` (index và giải thích)

```bash
python3 run_sql.py sql/explain.sql
```

Cần thấy hai kế hoạch trong cùng một màn hình:

- Trước index: `SCAN orders`
- Sau index: `SEARCH orders USING COVERING INDEX idx_orders_customer (customer_id=?)`

Đây là ảnh quan trọng nhất của tiêu chí "Index và giải thích", nên chụp đủ cả hai lần
`EXPLAIN QUERY PLAN`. Nếu màn hình ngắn, kéo để thấy cả phần `S15.2 CREATE INDEX`.

---

## Ảnh 6 — `06_expanded_counts.png` (bài mở rộng)

```bash
python3 generate_data.py --force
python3 run_sql.py --sql "SELECT 'customers' AS bang, COUNT(*) FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;" --db data/sales_extended.db
```

Cần thấy: 100 khách hàng, 30 sản phẩm, 500 đơn, 1500 dòng đơn và dòng
`foreign_key_check: ok` do `generate_data.py` in ra.

---

## Ảnh 7 — `07_s19_rank.png` (xếp hạng, window function)

```bash
python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db
```

Chụp đoạn **S19**: bảng có 4 cột `customer_id`, `name`, `revenue`, `rank`, `dense_rank`. Kỳ vọng
3 dòng đầu: `Ha 314565000.0 1 1`, `Ho Mai 281910000.0 2 2`, `Hoang Chi 267400000.0 3 3`.

---

## Sau khi chụp xong

1. Đưa 7 ảnh vào `lab01_sql/evidence/` đúng tên tệp ở bảng đầu tài liệu.
2. Kiểm tra danh sách:

   ```bash
   ls -l lab01_sql/evidence/*.png
   ```

3. Xuất lại báo cáo có chèn ảnh thật:

   ```bash
   pip install -r lab01_sql/report/requirements.txt
   python3 lab01_sql/report/make_report.py --images lab01_sql/evidence
   ```

   Báo cáo không có ảnh (chỉ văn bản, có bảng danh mục ảnh ở mục 7) dùng lệnh không tham số:

   ```bash
   python3 lab01_sql/report/make_report.py
   ```

4. Đóng gói bài nộp (ZIP sẽ gồm cả ảnh thật):

   ```bash
   bash lab01_sql/pack_submission.sh B23DCKH105
   ```

## Lưu ý khi chụp

- Che thông tin cá nhân nếu ảnh có email tài khoản ở góc màn hình.
- Không chụp khi terminal còn hiển thị đường dẫn tuyệt đối chứa tên tài khoản nếu không muốn công
  khai; có thể `cd ~/KHDL_PTIT_Lab/lab01_sql` để đường dẫn tương đối.
- Ảnh phải đọc được chữ: chụp ở chế độ phóng to terminal (`Ctrl` + `+`) nếu chữ nhỏ.
- Giữ đúng tên tệp: báo cáo và script đóng gói dựa vào tên tệp để chèn ảnh đúng vị trí.
