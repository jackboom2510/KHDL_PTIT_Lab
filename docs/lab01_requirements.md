# LAB 01 — Yêu cầu trích từ đề PDF

Nguồn: `Lab_01_SQL_Google_Cloud_Shell_IntroDataScience.pdf` (4 trang).
Chủ đề: **Thực hành SQL trên Google Cloud Shell với SQLite**.

## 1. Mục tiêu

- Dùng Gmail + trình duyệt + Internet, làm hoàn toàn trên Cloud Shell miễn phí (không bật Billing).
- Tạo CSDL quan hệ, khoá chính/khoá ngoại, CRUD, JOIN, GROUP BY, HAVING, subquery, index và
  đọc kế hoạch truy vấn.

## 2. Môi trường

```bash
whoami
pwd
python3 --version
mkdir -p ~/data_science/sql_lab
cd ~/data_science/sql_lab
```

Cloud Shell có ~5 GB trong `$HOME`. Nên tải code + `sales.db` về máy để tránh mất dữ liệu.

## 3. SQL Console

`schema.sql`/`sales.db` được tạo bằng chương trình `sql_console.py` (nội dung đầy đủ trong PDF
mục 4): đọc từng dòng, dùng `sqlite3.complete_statement()` để gộp câu lệnh nhiều dòng, dừng
bằng `;`, thoát bằng `EXIT`, in tên cột + rows hoặc `Rows affected`, bật
`PRAGMA foreign_keys = ON`.

## 4. Mô hình dữ liệu

`customers (1–N) orders`, `orders (1–N) order_items`, `products (1–N) order_items`.

```sql
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL, city TEXT
);
CREATE TABLE products (
  product_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL, category TEXT,
  price REAL CHECK(price >= 0)
);
CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL, order_date TEXT,
  FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE order_items (
  order_id INTEGER, product_id INTEGER,
  quantity INTEGER CHECK(quantity > 0),
  PRIMARY KEY(order_id, product_id),
  FOREIGN KEY(order_id) REFERENCES orders(order_id),
  FOREIGN KEY(product_id) REFERENCES products(product_id)
);
```

## 5. Dữ liệu mẫu (chạy một lần trên DB mới)

| Bảng | Số dòng |
| --- | --- |
| customers | 5 — An/Binh/Chi/Dung/Ha (Hanoi, Hanoi, Danang, HCMC, Hanoi) |
| products | 5 — Laptop 15.000.000, Mouse 250.000, Keyboard 650.000, Monitor 3.500.000, Headphones 800.000 |
| orders | 6 — 1001…1006, ngày 2026-10-01 → 2026-10-08 |
| order_items | 8 dòng |

`order_items` mẫu: (1001,101,1), (1001,102,2), (1002,103,1), (1002,104,1), (1003,105,2),
(1004,101,1), (1005,102,3), (1006,104,2).

## 6. Bài tập bắt buộc

| Mã | Yêu cầu |
| --- | --- |
| S01 | Hiển thị tên và thành phố khách hàng |
| S02 | Sản phẩm có giá > 1 triệu |
| S03 | Sắp xếp sản phẩm theo giá giảm dần |
| S04 | Thêm một khách hàng mới |
| S05 | Tăng giá Mouse thêm 10% |
| S06 | Xoá khách hàng vừa thêm (chưa có đơn) |
| S07 | Liệt kê mã đơn và tên khách hàng bằng JOIN |
| S08 | Tính tổng tiền từng đơn hàng |
| S09 | Doanh thu từng khách hàng |
| S10 | Khách hàng chi tiêu > 5 triệu (HAVING) |
| S11 | Sản phẩm có giá cao hơn trung bình (subquery) |
| S12 | Khách hàng có từ 2 đơn hàng |
| S13 | Top 3 sản phẩm theo doanh thu |
| S14 | Tạo index trên `orders.customer_id` |
| S15 | Xem `EXPLAIN QUERY PLAN` trước và sau index |

Ví dụ chuẩn cho S08:

```sql
SELECT o.order_id, SUM(i.quantity*p.price) AS total
FROM orders o JOIN order_items i ON i.order_id=o.order_id
JOIN products p ON p.product_id=i.product_id
GROUP BY o.order_id ORDER BY total DESC;
```

## 7. Bài tập về nhà

- Mở rộng dữ liệu tối thiểu: **100 khách, 30 sản phẩm, 500 đơn, 1.000 dòng đơn hàng**; dữ liệu
  giả lập, khoá ngoại hợp lệ.
- S16 doanh thu theo tháng; S17 khách chưa có đơn; S18 sản phẩm chưa từng bán.
- S19 xếp hạng khách hàng theo doanh thu bằng `RANK()` hoặc `DENSE_RANK()`.
- S20 so sánh kế hoạch thực thi sau khi mở rộng dữ liệu và tạo index.
- S21 nêu khác biệt giữa SQL Server `#table` / `##table` / `tempdb` trong slide với SQLite
  `TEMP TABLE`.

## 8. Nộp bài & chấm điểm

`StudentID_SQL.zip`: `sales.db`, `sql_console.py`, `answers.sql` (ghi rõ `-- S01...S21`),
chương trình tạo dữ liệu mở rộng, báo cáo PDF 2–3 trang, ảnh minh chứng.

| Tiêu chí | Điểm |
| --- | --- |
| Cài đặt và tạo dữ liệu | 2.0 |
| CRUD và câu cơ bản | 2.0 |
| Truy vấn nâng cao | 3.0 |
| Index và giải thích | 1.5 |
| Bài mở rộng, báo cáo | 1.5 |
