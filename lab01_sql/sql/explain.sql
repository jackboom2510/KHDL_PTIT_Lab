-- =====================================================================
-- LAB 01 — EXPLAIN QUERY PLAN: TRƯỚC / SAU INDEX (S15) và SAU MỞ RỘNG (S20)
-- File tự DROP index rồi CREATE lại, nên chạy được trên cả sales.db và
-- sales_extended.db, ở bất kỳ trạng thái nào:
--   python3 run_sql.py sql/explain.sql
--   python3 run_sql.py sql/explain.sql --db data/sales_extended.db
-- Output copy nguyên từ terminal vào báo cáo, không sửa tay.
-- =====================================================================

-- ---------------------------------------------------------------------
-- S15 — dữ liệu mẫu (data/sales.db, 6 đơn)
-- ---------------------------------------------------------------------

-- S15.1 TRƯỚC index: kỳ vọng SCAN orders
DROP INDEX IF EXISTS idx_orders_customer;
EXPLAIN QUERY PLAN
SELECT order_id FROM orders WHERE customer_id = 1;

-- S15.2 TẠO index trên orders.customer_id
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);

-- S15.3 SAU index: kỳ vọng SEARCH orders USING INDEX idx_orders_customer
EXPLAIN QUERY PLAN
SELECT order_id FROM orders WHERE customer_id = 1;

-- S15.4 Kiểm chứng bằng số dòng thực sự phải đọc (SQLite không in số này trong EXPLAIN,
-- nên đếm thủ công số dòng khớp điều kiện):
SELECT COUNT(*) AS rows_matched FROM orders WHERE customer_id = 1;

-- ---------------------------------------------------------------------
-- S20 — dữ liệu mở rộng (data/sales_extended.db: 100 khách / 500 đơn)
-- Chạy file này với --db data/sales_extended.db để so sánh plan ở quy mô lớn hơn:
-- bảng orders lớn hơn nhiều nên SCAN đọc toàn bộ bảng, còn SEARCH chỉ chạm
-- các dòng có customer_id cần tìm.
-- ---------------------------------------------------------------------

-- S20.1 TRƯỚC index trên bảng lớn
DROP INDEX IF EXISTS idx_orders_customer;
EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 7;

-- S20.2 SAU index trên bảng lớn
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 7;

-- S20.3 Truy vấn tổng hợp có GROUP BY (join + index vẫn hữu ích ở bước lọc orders)
EXPLAIN QUERY PLAN
SELECT o.customer_id, SUM(i.quantity * p.price) AS revenue
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
JOIN products p    ON p.product_id = i.product_id
WHERE o.customer_id >= 1
GROUP BY o.customer_id;

-- Ghi chú đọc kết quả:
--   SCAN orders                          -> đọc tuần tự toàn bộ bảng
--   SEARCH orders USING INDEX ...        -> dùng cây B-tree của index để tìm trực tiếp
--   SEARCH ... USING COVERING INDEX ...  -> như trên nhưng thoả luôn cột cần đọc, không phải
--                                           quay lại bảng (S15 chỉ lấy order_id nên rơi vào
--                                           trường hợp này: index chứa customer_id + rowid)
--   USE TEMP B-TREE FOR ORDER BY         -> SQLite phải sort thêm, cân nhắc index phù hợp
-- Dữ liệu 6 dòng: chênh lệch thời gian không đo được; kết luận phải dựa trên plan.
