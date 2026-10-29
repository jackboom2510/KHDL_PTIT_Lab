-- LAB 01 — Dữ liệu mẫu đúng theo đề PDF (mục 6)
-- Kỳ vọng: customers = 5, products = 5, orders = 6, order_items = 8
-- Chỉ chạy MỘT lần trên database mới (dùng INSERT OR IGNORE để chạy lại vẫn an toàn).

INSERT OR IGNORE INTO customers (customer_id, name, city) VALUES
    (1, 'An',   'Hanoi'),
    (2, 'Binh', 'Hanoi'),
    (3, 'Chi',  'Danang'),
    (4, 'Dung', 'HCMC'),
    (5, 'Ha',   'Hanoi');

INSERT OR IGNORE INTO products (product_id, name, category, price) VALUES
    (101, 'Laptop',     'Electronics', 15000000),
    (102, 'Mouse',      'Accessories',   250000),
    (103, 'Keyboard',   'Accessories',   650000),
    (104, 'Monitor',    'Electronics',  3500000),
    (105, 'Headphones', 'Accessories',   800000);

INSERT OR IGNORE INTO orders (order_id, customer_id, order_date) VALUES
    (1001, 1, '2026-10-01'),
    (1002, 2, '2026-10-02'),
    (1003, 1, '2026-10-05'),
    (1004, 3, '2026-10-06'),
    (1005, 4, '2026-10-07'),
    (1006, 5, '2026-10-08');

INSERT OR IGNORE INTO order_items (order_id, product_id, quantity) VALUES
    (1001, 101, 1),
    (1001, 102, 2),
    (1002, 103, 1),
    (1002, 104, 1),
    (1003, 105, 2),
    (1004, 101, 1),
    (1005, 102, 3),
    (1006, 104, 2);
