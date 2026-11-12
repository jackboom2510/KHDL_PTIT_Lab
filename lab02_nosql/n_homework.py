#!/usr/bin/env python3
"""Đáp án LAB 02 — PHẦN BỔ SUNG / VỀ NHÀ (N16–N22) trên dữ liệu mở rộng.

Chạy `generate_data.py` trước (≥500 đơn, order_id 2001–2500).

    python3 n_homework.py                  # in kết quả từng câu
    python3 n_homework.py --json out.json  # ghi kết quả ra JSON (dùng cho report/)

N19 có ghi dữ liệu (`discount` trên một phần document) nhưng chạy lặp an toàn: chỉ `$set`
đúng bộ lọc, không đụng toàn bộ collection. N20 có sửa giá tạm thời rồi khôi phục.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows

from connect import get_database

MIN_ORDERS = 100          # dưới ngưỡng này coi như chưa chạy generate_data.py
FIRST_EXTENDED_ORDER = 2001


def _plain_all(cursor) -> list[dict]:
    return [{k: v for k, v in d.items() if k != "_id"} for d in cursor]


def _require_extended(db) -> None:
    if db.orders.count_documents({}) < MIN_ORDERS:
        raise SystemExit(
            f"Chưa có dữ liệu mở rộng (cần >= {MIN_ORDERS} đơn). "
            "Chạy: python3 generate_data.py --force")


# ----------------------------------------------------------------- N16–N18
def n16(db) -> list[dict]:
    """Doanh thu theo thành phố ($lookup customers + $unwind items)."""
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {"_id": "$customer_id",
                    "revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}}},
        {"$lookup": {"from": "customers", "localField": "_id",
                     "foreignField": "customer_id", "as": "customer"}},
        {"$unwind": "$customer"},
        {"$group": {"_id": "$customer.city", "revenue": {"$sum": "$revenue"},
                    "customers": {"$sum": 1}}},
        {"$sort": {"revenue": -1}},
        {"$project": {"_id": 0, "city": "$_id", "revenue": 1, "customers": 1}},
    ]
    return _plain_all(db.orders.aggregate(pipeline))


def n17(db) -> list[dict]:
    """Ba sản phẩm có doanh thu cao nhất."""
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.product_id",
                    "name": {"$first": "$items.name"},
                    "revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}},
                    "quantity": {"$sum": "$items.quantity"}}},
        {"$sort": {"revenue": -1}},
        {"$limit": 3},
        {"$project": {"_id": 0, "product_id": "$_id", "name": 1, "revenue": 1, "quantity": 1}},
    ]
    return _plain_all(db.orders.aggregate(pipeline))


def n18(db) -> list[dict]:
    """Khách chưa đặt hàng nào ($lookup + $match mảng rỗng)."""
    pipeline = [
        {"$lookup": {"from": "orders", "localField": "customer_id",
                     "foreignField": "customer_id", "as": "orders"}},
        {"$match": {"orders": {"$size": 0}}},
        {"$sort": {"customer_id": 1}},
        {"$project": {"_id": 0, "customer_id": 1, "name": 1, "city": 1}},
    ]
    return _plain_all(db.customers.aggregate(pipeline))


# ----------------------------------------------------------------- N19–N20
def n19(db) -> dict:
    """discount không đồng nhất + $ifNull khi tính doanh thu thuần."""
    # 1) thêm discount cho một phần document (idempotent: $set lại cùng giá trị).
    #    Chọn tập con theo order_id đã sắp xếp để không phụ thuộc toán tử $mod.
    ids = [d["order_id"] for d in db.orders
           .find({"order_id": {"$gte": FIRST_EXTENDED_ORDER}}, {"_id": 0, "order_id": 1})
           .sort("order_id", 1)]
    matched = db.orders.update_many({"order_id": {"$in": ids[0::3]}},
                                    {"$set": {"discount": 0.1}}).matched_count
    db.orders.update_many({"order_id": {"$in": ids[1::6]}}, {"$set": {"discount": 0.05}})
    with_discount = db.orders.count_documents({"discount": {"$exists": True}})
    without = db.orders.count_documents({"discount": {"$exists": False}})

    pipeline = [
        {"$unwind": "$items"},
        {"$group": {"_id": "$order_id",
                    "gross": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}},
                    "discount": {"$first": {"$ifNull": ["$discount", 0]}}}},
        {"$project": {"_id": 0, "order_id": "$_id", "gross": 1, "discount": 1,
                      "net": {"$multiply": ["$gross", {"$subtract": [1, "$discount"]}]}}},
        {"$sort": {"net": -1}},
    ]
    rows = _plain_all(db.orders.aggregate(pipeline))
    return {
        "matched_discount_10pct": matched,
        "orders_with_discount": with_discount,
        "orders_without_discount": without,
        "totals": {
            "gross": round(sum(r["gross"] for r in rows), 2),
            "net": round(sum(r["net"] for r in rows), 2),
            "discount_amount": round(sum(r["gross"] - r["net"] for r in rows), 2),
        },
        "top5_net": rows[:5],
    }


def n20(db) -> dict:
    """Nhúng vs tham chiếu: đổi giá trong products KHÔNG cập nhật items.price đơn cũ."""
    product = db.products.find_one({"product_id": 101}, {"_id": 0})
    old_price = product["price"]
    in_orders = [d["items"] for d in db.orders.find({"items.product_id": 101},
                                                    {"_id": 0, "items": 1}).limit(1)]
    price_in_order_before = next((i["price"] for i in in_orders[0] if i["product_id"] == 101),
                                 None)
    new_price = old_price + 1_000_000
    db.products.update_one({"product_id": 101}, {"$set": {"price": new_price}})
    after = db.products.find_one({"product_id": 101}, {"_id": 0})
    order_after = next((d["items"] for d in db.orders.find({"items.product_id": 101},
                                                           {"_id": 0, "items": 1}).limit(1)), [])
    price_in_order_after = next((i["price"] for i in order_after if i["product_id"] == 101),
                                None)
    # khôi phục giá gốc để không làm sai dữ liệu của các câu khác
    db.products.update_one({"product_id": 101}, {"$set": {"price": old_price}})

    return {
        "product_id": 101,
        "product_price_before": old_price,
        "product_price_after_update": after["price"],
        "price_in_old_order_before": price_in_order_before,
        "price_in_old_order_after": price_in_order_after,
        "embedded_copies_price": price_in_order_before == price_in_order_after,
        "restored_price": db.products.find_one({"product_id": 101}, {"_id": 0})["price"],
        "ket_luan": "items.price là bản sao tại thời điểm mua nên đổi giá products không ảnh "
                    "hưởng đơn cũ. Muốn giá luôn mới thì phải tham chiếu (chỉ lưu product_id) "
                    "và $lookup khi đọc, đổi lại là JOIN nhiều hơn và không giữ được lịch sử giá.",
    }


# ----------------------------------------------------------------- N21–N22
def n21(db) -> dict:
    """Tạo index và đọc explain() — COLLSCAN vs IXSCAN."""
    before = [i["name"] for i in db.orders.list_indexes()]
    db.orders.create_index([("customer_id", 1)], name="idx_orders_customer")
    after = [{"name": i["name"], "key": list(i["key"].items())} for i in db.orders.list_indexes()]

    def stage_of(query: dict) -> dict:
        try:
            plan = db.orders.find(query).explain()
        except Exception as exc:                                   # noqa: BLE001
            return {"error": f"explain() không khả dụng: {exc}"}
        winning = plan.get("queryPlanner", {}).get("winningPlan", {})
        stats = plan.get("executionStats", {})
        return {
            "stage": winning.get("stage"),
            "index_name": winning.get("inputStage", {}).get("indexName")
                          or winning.get("indexName"),
            "docs_examined": stats.get("totalDocsExamined"),
            "keys_examined": stats.get("totalKeysExamined"),
            "n_returned": stats.get("nReturned"),
        }

    return {
        "indexes_before": before,
        "indexes_after": after,
        "explain_customer_id": stage_of({"customer_id": 7}),
        "explain_no_index_field": stage_of({"order_date": {"$gte": "2026-01-01"}}),
        "ghi_chu": "Dữ liệu nhỏ (500 đơn) nên chênh lệch thời gian không đáng kể; kết luận dựa "
                   "trên stage của winningPlan (COLLSCAN vs IXSCAN) và số document phải đọc.",
    }


def n22(db) -> dict:
    """Đối chiếu JOIN của SQL với $lookup của MongoDB."""
    join_demo = _plain_all(db.orders.aggregate([
        {"$lookup": {"from": "customers", "localField": "customer_id",
                     "foreignField": "customer_id", "as": "customer"}},
        {"$unwind": "$customer"},
        {"$project": {"_id": 0, "order_id": 1, "name": "$customer.name"}},
        {"$sort": {"order_id": 1}},
    ]))
    return {
        "sql_join": "SELECT o.order_id, c.name FROM orders o "
                    "JOIN customers c ON c.customer_id = o.customer_id ORDER BY o.order_id;",
        "mongo_lookup": [{"$lookup": {"from": "customers", "localField": "customer_id",
                                      "foreignField": "customer_id", "as": "customer"}},
                         {"$unwind": "$customer"},
                         {"$project": {"_id": 0, "order_id": 1, "name": "$customer.name"}}],
        "khac_biet": [
            "JOIN chạy trong một engine quan hệ, tối ưu bằng thống kê và index của cả hai bảng.",
            "$lookup là stage của aggregation: chạy sau khi đã lọc; mỗi document vào stage "
            "đều phát một truy vấn tới collection đích (có thể dùng pipeline con để lọc trước).",
            "JOIN trả bảng phẳng, $lookup nhét mảng kết quả vào document nên cần $unwind "
            "nếu muốn phẳng như JOIN.",
            "Với dữ liệu nhúng sẵn (items), MongoDB không cần $lookup — đó là lợi thế chính.",
        ],
        "ket_qua_ghep": join_demo[:5],
        "so_dong": len(join_demo),
    }


ANSWERS = {f"n{i:02d}": globals()[f"n{i:02d}"] for i in range(16, 23)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đáp án LAB 02 — N16–N22 (bổ sung)")
    ap.add_argument("--json", type=Path, default=None,
                    help="ghi kết quả ra JSON để report/make_report.py dùng")
    args = ap.parse_args()

    db = get_database()
    try:
        _require_extended(db)
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
