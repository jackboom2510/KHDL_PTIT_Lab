#!/usr/bin/env python3
"""Đáp án LAB 02 — PHẦN BẮT BUỘC (N01–N15) trên bộ dữ liệu mẫu 5/5/6.

    python3 n_answers.py                  # in kết quả từng câu
    python3 n_answers.py --json out.json  # ghi kết quả ra JSON (dùng cho report/)

Mỗi câu là một hàm `nNN(db)` trả về dữ liệu thuần Python (dict/list) để vừa in được, vừa ghi
JSON, vừa đưa vào báo cáo. Hàm không tự kết nối — nhận `db` từ `connect.get_database()`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows

from connect import get_database

NEW_CUSTOMER = {"customer_id": 6, "name": "Lan", "city": "Hue"}


def _plain(doc: dict) -> dict:
    """Bỏ `_id` để in/ghi JSON gọn (ObjectId không serialize được)."""
    return {k: v for k, v in doc.items() if k != "_id"}


def _plain_all(cursor) -> list[dict]:
    return [_plain(d) for d in cursor]


# ----------------------------------------------------------------- N01–N04: đọc
def n01(db) -> list[dict]:
    """Liệt kê tất cả customers."""
    return _plain_all(db.customers.find({}, {"_id": 0}).sort("customer_id", 1))


def n02(db) -> list[dict]:
    """Khách hàng ở Hanoi."""
    return _plain_all(db.customers.find({"city": "Hanoi"}, {"_id": 0}).sort("customer_id", 1))


def n03(db) -> list[dict]:
    """Sản phẩm giá trên 1 triệu ($gt)."""
    return _plain_all(db.products.find({"price": {"$gt": 1_000_000}}, {"_id": 0}).sort("price", -1))


def n04(db) -> list[dict]:
    """Sắp xếp sản phẩm theo giá giảm dần."""
    return _plain_all(db.products.find({}, {"_id": 0}).sort("price", -1))


# ----------------------------------------------------------------- N05–N07: CRUD
def n05(db) -> dict:
    """Thêm khách hàng mới (insert_one) — chạy lặp an toàn."""
    if db.customers.count_documents({"customer_id": NEW_CUSTOMER["customer_id"]}) == 0:
        db.customers.insert_one(dict(NEW_CUSTOMER))
        action = "inserted"
    else:
        action = "already_exists"
    return {"action": action, "document": dict(NEW_CUSTOMER),
            "customers_total": db.customers.count_documents({})}


def n06(db) -> dict:
    """Sửa thành phố của khách vừa thêm (update_one + $set)."""
    result = db.customers.update_one({"customer_id": NEW_CUSTOMER["customer_id"]},
                                     {"$set": {"city": "Danang"}})
    doc = db.customers.find_one({"customer_id": NEW_CUSTOMER["customer_id"]}, {"_id": 0})
    return {"matched": result.matched_count, "modified": result.modified_count,
            "document": _plain(doc) if doc else None}


def n07(db) -> dict:
    """Xoá khách vừa thêm (delete_one)."""
    result = db.customers.delete_one({"customer_id": NEW_CUSTOMER["customer_id"]})
    return {"deleted": result.deleted_count,
            "customers_total": db.customers.count_documents({}),
            "price_mouse": db.products.find_one({"product_id": 102}, {"_id": 0})["price"]}


# ----------------------------------------------------------------- N08–N13: aggregation
def n08(db) -> list[dict]:
    """Đếm khách theo thành phố ($group + $sum)."""
    pipeline = [
        {"$group": {"_id": "$city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1, "_id": 1}},
        {"$project": {"_id": 0, "city": "$_id", "count": 1}},
    ]
    return _plain_all(db.customers.aggregate(pipeline))


def n09(db) -> list[dict]:
    """Đơn hàng chứa Laptop — truy vấn mảng items nhúng."""
    cursor = db.orders.find({"items.product_id": 101},
                            {"_id": 0, "order_id": 1, "customer_id": 1}).sort("order_id", 1)
    return _plain_all(cursor)


def n10(db) -> list[dict]:
    """Tổng tiền từng đơn ($unwind + $group + $multiply)."""
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {"_id": "$order_id",
                    "total": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}}},
        {"$sort": {"total": -1}},
        {"$project": {"_id": 0, "order_id": "$_id", "total": 1}},
    ]
    return _plain_all(db.orders.aggregate(pipeline))


def n11(db) -> list[dict]:
    """Doanh thu theo từng khách hàng (kèm tên qua $lookup)."""
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {"_id": "$customer_id",
                    "revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}}},
        {"$lookup": {"from": "customers", "localField": "_id",
                     "foreignField": "customer_id", "as": "customer"}},
        {"$unwind": "$customer"},
        {"$sort": {"revenue": -1}},
        {"$project": {"_id": 0, "customer_id": "$_id", "name": "$customer.name",
                      "revenue": 1}},
    ]
    return _plain_all(db.orders.aggregate(pipeline))


def n12(db) -> list[dict]:
    """Ghép orders với customers ($lookup + $unwind + $project)."""
    pipeline = [
        {"$lookup": {"from": "customers", "localField": "customer_id",
                     "foreignField": "customer_id", "as": "customer"}},
        {"$unwind": "$customer"},
        {"$sort": {"order_id": 1}},
        {"$project": {"_id": 0, "order_id": 1, "customer_id": 1, "name": "$customer.name",
                      "city": "$customer.city"}},
    ]
    return _plain_all(db.orders.aggregate(pipeline))


def n13(db) -> list[dict]:
    """Khách có ít nhất 2 đơn ($group + $match)."""
    pipeline = [
        {"$group": {"_id": "$customer_id", "order_count": {"$sum": 1}}},
        {"$match": {"order_count": {"$gte": 2}}},
        {"$lookup": {"from": "customers", "localField": "_id",
                     "foreignField": "customer_id", "as": "customer"}},
        {"$unwind": "$customer"},
        {"$sort": {"order_count": -1, "_id": 1}},
        {"$project": {"_id": 0, "customer_id": "$_id", "name": "$customer.name",
                      "order_count": 1}},
    ]
    return _plain_all(db.orders.aggregate(pipeline))


# ----------------------------------------------------------------- N14–N15: index & mô hình
def n14(db) -> dict:
    """Tạo index orders.customer_id (chạy lặp an toàn)."""
    before = [i["name"] for i in db.orders.list_indexes()]
    db.orders.create_index([("customer_id", 1)], name="idx_orders_customer")
    after = [{"name": i["name"], "key": list(i["key"].items())} for i in db.orders.list_indexes()]
    return {"indexes_before": before, "indexes_after": after,
            "created": "idx_orders_customer" if "idx_orders_customer" not in before else "existed"}


def n15(db) -> dict:
    """Giải thích embedded vs reference (phần chữ nằm trong báo cáo, mục 4)."""
    return {
        "embedded": {
            "mô_hình": "items[] nằm ngay trong document orders",
            "ưu_điểm": ["đọc cả đơn bằng một lần truy vấn, không JOIN",
                        "ghi nguyên tử (atomic) trên một document",
                        "giá và tên sản phẩm được 'chụp' tại thời điểm mua"],
            "hạn_chế": ["document tối đa 16 MB", "dữ liệu lặp lại (name, price) trong mọi đơn",
                        "đổi giá trong products không tự cập nhật đơn cũ"],
        },
        "reference": {
            "mô_hình": "order_items chỉ lưu product_id, đọc thêm bảng products",
            "ưu_điểm": ["không lặp dữ liệu, sửa giá một chỗ", "phù hợp dữ liệu lớn / dùng chung"],
            "hạn_chế": ["cần $lookup/JOIN mỗi lần đọc", "nhiều round-trip hơn"],
        },
        "lựa_chọn": "LAB 02 dùng embedded cho items vì mỗi đơn chỉ 1–5 dòng và luôn đọc kèm đơn; "
                    "customers/products để riêng và tham chiếu bằng customer_id/product_id.",
    }


ANSWERS = {f"n{i:02d}": globals()[f"n{i:02d}"] for i in range(1, 16)}


def run_all(db) -> dict:
    return {code: fn(db) for code, fn in ANSWERS.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đáp án LAB 02 — N01–N15 (bắt buộc)")
    ap.add_argument("--json", type=Path, default=None,
                    help="ghi kết quả ra JSON để report/make_report.py dùng")
    args = ap.parse_args()

    db = get_database()
    try:
        results = {}
        for code, fn in ANSWERS.items():
            value = fn(db)
            results[code] = value
            print(f"\n=== {code.upper()} === {fn.__doc__.splitlines()[0]}")
            if isinstance(value, list):
                for row in value:
                    print(" ", row)
                print(f"  ({len(value)} dòng)")
            else:
                print(json.dumps(value, ensure_ascii=False, indent=2, default=str))
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str),
                                 encoding="utf-8")
            print(f"\n[ok] đã ghi {args.json}")
    finally:
        db.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
