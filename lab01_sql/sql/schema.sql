-- LAB 01 — Schema quan hệ cho cửa hàng trực tuyến
-- customers (1–N) orders, orders (1–N) order_items, products (1–N) order_items
-- Dùng bởi build_db.py. Chạy lại nhiều lần vẫn an toàn vì có IF NOT EXISTS.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    category   TEXT,
    price      REAL CHECK(price >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date  TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id   INTEGER,
    product_id INTEGER,
    quantity   INTEGER CHECK(quantity > 0),
    PRIMARY KEY(order_id, product_id),
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
