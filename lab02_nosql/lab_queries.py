#!/usr/bin/env python3
"""Các ví dụ CRUD / truy vấn đúng như đề PDF mục 7 (PyMongo, không phải mongosh).

    python3 lab_queries.py

Script chỉ in kết quả, và trả dữ liệu về trạng thái ban đầu (thêm rồi xoá khách id 6).
"""

from __future__ import annotations

import sys

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows

from connect import get_database


def main() -> int:
    db = get_database()
    try:
        print("--- Khách hàng ở Hanoi ---")
        for d in db.customers.find({"city": "Hanoi"}, {"_id": 0}):
            print(d)

        print("--- Đơn hàng chứa Laptop (items.product_id = 101) ---")
        for d in db.orders.find({"items.product_id": 101}, {"_id": 0, "order_id": 1}):
            print("Order containing Laptop:", d["order_id"])

        print("--- Thêm / sửa / xoá khách id 6 ---")
        if db.customers.count_documents({"customer_id": 6}) == 0:
            db.customers.insert_one({"customer_id": 6, "name": "Lan", "city": "Hue"})
            print("insert_one: thêm Lan (Hue)")
        db.customers.update_one({"customer_id": 6}, {"$set": {"city": "Danang"}})
        print("update_one:", db.customers.find_one({"customer_id": 6}, {"_id": 0}))
        db.customers.delete_one({"customer_id": 6})
        print("delete_one: đã xoá khách id 6")

        print("Customers:", db.customers.count_documents({}))
    finally:
        db.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
