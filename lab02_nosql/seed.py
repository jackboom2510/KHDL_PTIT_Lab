#!/usr/bin/env python3
"""Nạp bộ dữ liệu mẫu của LAB 02 (5 khách, 5 sản phẩm, 6 đơn) — đúng đề PDF mục 6.

Mỗi order chứa mảng `items` là các document nhúng `{product_id, name, price, quantity}`.
Chỉ chạy trên database rỗng để không trộn với dữ liệu mở rộng của `generate_data.py`.

    python3 seed.py

Kỳ vọng: customers 5, products 5, orders 6.
"""

from __future__ import annotations

import sys

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows

from connect import get_database

CUSTOMERS = [
    {"customer_id": 1, "name": "An", "city": "Hanoi"},
    {"customer_id": 2, "name": "Binh", "city": "Hanoi"},
    {"customer_id": 3, "name": "Chi", "city": "Danang"},
    {"customer_id": 4, "name": "Dung", "city": "HCMC"},
    {"customer_id": 5, "name": "Ha", "city": "Hanoi"},
]

PRODUCTS = [
    {"product_id": 101, "name": "Laptop", "category": "Electronics", "price": 15000000},
    {"product_id": 102, "name": "Mouse", "category": "Accessories", "price": 250000},
    {"product_id": 103, "name": "Keyboard", "category": "Accessories", "price": 650000},
    {"product_id": 104, "name": "Monitor", "category": "Electronics", "price": 3500000},
    {"product_id": 105, "name": "Headphones", "category": "Accessories", "price": 800000},
]

ORDERS = [
    (1001, 1, "2026-10-01", [(101, 1), (102, 2)]),
    (1002, 2, "2026-10-02", [(103, 1), (104, 1)]),
    (1003, 1, "2026-10-05", [(105, 2)]),
    (1004, 3, "2026-10-06", [(101, 1)]),
    (1005, 4, "2026-10-07", [(102, 3)]),
    (1006, 5, "2026-10-08", [(104, 2)]),
]


def already_has_data(db) -> bool:
    return any(db[c].count_documents({}) for c in ("customers", "products", "orders"))


def build_order_docs(orders=ORDERS, products=PRODUCTS) -> list[dict]:
    """Chuyển (order_id, customer_id, date, [(product_id, qty)]) thành document có items nhúng."""
    by_id = {p["product_id"]: p for p in products}
    docs = []
    for order_id, customer_id, order_date, lines in orders:
        items = [
            {
                "product_id": product_id,
                "name": by_id[product_id]["name"],
                "price": by_id[product_id]["price"],   # giá sao lại tại thời điểm mua
                "quantity": quantity,
            }
            for product_id, quantity in lines
        ]
        docs.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "items": items,
        })
    return docs


def main() -> int:
    db = get_database()
    try:
        if already_has_data(db):
            raise SystemExit("Data already exists. Use a fresh database.")

        db.customers.insert_many(CUSTOMERS)
        db.products.insert_many(PRODUCTS)
        db.orders.insert_many(build_order_docs())

        for name in ("customers", "products", "orders"):
            print(name, db[name].count_documents({}))
        order = db.orders.find_one({"order_id": 1001}, {"_id": 0})
        print("Mẫu document orders (items nhúng):")
        for item in order["items"]:
            print("  ", item)
    finally:
        db.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
