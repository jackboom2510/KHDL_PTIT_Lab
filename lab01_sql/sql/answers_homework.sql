-- =====================================================================
-- LAB 01 — BÀI TẬP VỀ NHÀ / BỔ SUNG (S16–S21)
-- Chạy trên bản dữ liệu mở rộng do generate_data.py sinh ra:
--   python3 generate_data.py --force
--   python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db
-- (chạy được cả trên data/sales.db, chỉ là số liệu nhỏ hơn)
-- =====================================================================

-- S16: Doanh thu theo tháng
SELECT strftime('%Y-%m', o.order_date) AS month,
       COUNT(DISTINCT o.order_id)      AS orders,
       ROUND(SUM(i.quantity * p.price), 0) AS revenue
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
JOIN products p    ON p.product_id = i.product_id
GROUP BY month
ORDER BY month;

-- S17: Khách hàng chưa có đơn hàng nào
SELECT c.customer_id, c.name, c.city
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
ORDER BY c.customer_id;

-- S18: Sản phẩm chưa từng bán được
SELECT p.product_id, p.name, p.category, p.price
FROM products p
WHERE NOT EXISTS (
    SELECT 1 FROM order_items i WHERE i.product_id = p.product_id
)
ORDER BY p.product_id;

-- S19: Xếp hạng khách hàng theo doanh thu (RANK / DENSE_RANK)
-- RANK bỏ số hạng khi hoà, DENSE_RANK thì không — cột rank_gap cho thấy chỗ hai hàm khác nhau.
SELECT c.customer_id,
       c.name,
       ROUND(SUM(i.quantity * p.price), 0) AS revenue,
       RANK()       OVER (ORDER BY SUM(i.quantity * p.price) DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY SUM(i.quantity * p.price) DESC) AS dense_rank
FROM customers c
JOIN orders o      ON o.customer_id = c.customer_id
JOIN order_items i ON i.order_id = o.order_id
JOIN products p    ON p.product_id = i.product_id
GROUP BY c.customer_id, c.name
ORDER BY revenue DESC
LIMIT 10;

-- S20: So sánh kế hoạch thực thi sau khi mở rộng dữ liệu và tạo index
-- Bảng lớn (500 đơn) nên chênh lệch SCAN/SEARCH rõ hơn dữ liệu mẫu 6 đơn.
-- Cặp EXPLAIN chi tiết (trước/sau index, trước/sau khi mở rộng) nằm trong sql/explain.sql.
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);

EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 7
ORDER BY order_date DESC;

-- S21: Khác biệt SQL Server (#table / ##table / tempdb) và SQLite TEMP TABLE
--   * SQL Server `#t`   — bảng tạm cục bộ, chỉ thấy trong session đã tạo, tự xoá khi session
--     hoặc procedure kết thúc; sống trong tempdb (không phải CSDL người dùng).
--   * SQL Server `##t`  — bảng tạm toàn cục, mọi session đều thấy, mất khi session cuối cùng
--     đang tham chiếu nó đóng lại.
--   * SQL Server `tempdb` — CSDL hệ thống dùng chung cho bảng tạm, biến bảng, sort/hash spill;
--     có thể truy vấn trực tiếp `tempdb..#t`.
--   * SQLite `CREATE TEMP TABLE t` — bảng tạm nằm trong CSDL `temp` (gắn với kết nối), chỉ
--     connection tạo ra nó thấy, tự mất khi đóng kết nối; KHÔNG có khái niệm bảng tạm toàn cục
--     `##`.
--   * SQLite không có tempdb tách rời: schema `temp` có thể nằm trong RAM hoặc file tạm, do
--     `PRAGMA temp_store` quyết định (0 = mặc định, 1 = file, 2 = memory).
--   * Cả hai đều ưu tiên tên trong schema tạm khi trùng tên với bảng thường (SQLite: bảng
--     `temp` được tìm trước `main`).
-- Minh hoạ bằng TEMP TABLE (chỉ tồn tại trong phiên chạy run_sql.py này):
CREATE TEMP TABLE revenue_by_month AS
SELECT strftime('%Y-%m', o.order_date) AS month,
       SUM(i.quantity * p.price)       AS revenue
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
JOIN products p    ON p.product_id = i.product_id
GROUP BY month;

SELECT month, ROUND(revenue, 0) AS revenue
FROM revenue_by_month
ORDER BY revenue DESC
LIMIT 3;

DROP TABLE temp.revenue_by_month;
