-- =====================================================================
-- LAB 01 — BÀI TẬP BẮT BUỘC (S01–S15)
-- Chạy trên data/sales.db. File được viết để chạy lại nhiều lần vẫn sạch:
--   S04 thêm khách id 6, S06 xoá đúng khách đó; S05 chỉ tăng giá khi Mouse
--   còn ở giá gốc 250.000 (không cộng dồn 10% mỗi lần chạy).
--   python3 run_sql.py sql/answers.sql
--   hoặc: sqlite3 data/sales.db < sql/answers.sql
-- =====================================================================

-- S01: Hiển thị tên và thành phố khách hàng
SELECT name, city
FROM customers
ORDER BY customer_id;

-- S02: Sản phẩm có giá > 1 triệu
SELECT product_id, name, price
FROM products
WHERE price > 1000000
ORDER BY price DESC;

-- S03: Sắp xếp sản phẩm theo giá giảm dần
SELECT product_id, name, category, price
FROM products
ORDER BY price DESC;

-- S04: Thêm một khách hàng mới (Lan — Hue)
-- ON CONFLICT DO NOTHING để file chạy lại không báo lỗi khoá chính.
INSERT INTO customers (customer_id, name, city)
VALUES (6, 'Lan', 'Hue')
ON CONFLICT(customer_id) DO NOTHING;

SELECT * FROM customers WHERE customer_id = 6;

-- S05: Tăng giá Mouse thêm 10% (250.000 -> 275.000)
-- Điều kiện price = 250000 giữ phép nhân không bị cộng dồn khi chạy lại file.
UPDATE products
SET price = ROUND(price * 1.1, 0)
WHERE product_id = 102 AND price = 250000;

SELECT product_id, name, price FROM products WHERE product_id = 102;

-- S06: Xoá khách hàng vừa thêm (chưa có đơn hàng nào)
DELETE FROM customers
WHERE customer_id = 6
  AND NOT EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.customer_id);

SELECT COUNT(*) AS customers_after_delete FROM customers;

-- S07: Liệt kê mã đơn và tên khách hàng bằng JOIN
SELECT o.order_id, c.name AS customer_name, o.order_date
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_id;

-- S08: Tính tổng tiền từng đơn hàng
SELECT o.order_id,
       SUM(i.quantity * p.price) AS total
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
JOIN products p    ON p.product_id = i.product_id
GROUP BY o.order_id
ORDER BY total DESC;

-- S09: Doanh thu từng khách hàng
SELECT c.customer_id,
       c.name,
       SUM(i.quantity * p.price) AS revenue
FROM customers c
LEFT JOIN orders o      ON o.customer_id = c.customer_id
LEFT JOIN order_items i ON i.order_id = o.order_id
LEFT JOIN products p    ON p.product_id = i.product_id
GROUP BY c.customer_id, c.name
ORDER BY revenue DESC;

-- S10: Khách hàng chi tiêu > 5 triệu (HAVING)
SELECT c.customer_id,
       c.name,
       SUM(i.quantity * p.price) AS revenue
FROM customers c
JOIN orders o           ON o.customer_id = c.customer_id
JOIN order_items i      ON i.order_id = o.order_id
JOIN products p         ON p.product_id = i.product_id
GROUP BY c.customer_id, c.name
HAVING SUM(i.quantity * p.price) > 5000000
ORDER BY revenue DESC;

-- S11: Sản phẩm có giá cao hơn giá trung bình (subquery)
SELECT product_id, name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;

-- S12: Khách hàng có từ 2 đơn hàng
SELECT c.customer_id, c.name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) >= 2
ORDER BY order_count DESC, c.customer_id;

-- S13: Top 3 sản phẩm theo doanh thu
SELECT p.product_id,
       p.name,
       SUM(i.quantity * p.price) AS revenue
FROM products p
JOIN order_items i ON i.product_id = p.product_id
GROUP BY p.product_id, p.name
ORDER BY revenue DESC
LIMIT 3;

-- S14: Tạo index trên orders.customer_id
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);

-- S15: Xem EXPLAIN QUERY PLAN trước và sau index
-- Phần "trước index" cần chạy khi index chưa tồn tại, nên xem toàn bộ cặp
-- before/after trong sql/explain.sql (file đó tự DROP rồi CREATE index).
-- Ở đây chạy sau index để thấy SEARCH ... USING INDEX:
EXPLAIN QUERY PLAN
SELECT order_id FROM orders WHERE customer_id = 1;
