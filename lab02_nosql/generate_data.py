#!/usr/bin/env python3
"""Sinh dữ liệu mở rộng cho LAB 02 (phần về nhà) và nạp lên Atlas.

Quy mô: 100 khách, 30 sản phẩm, 500 đơn, mỗi đơn 1–5 sản phẩm (≥1.000 dòng hàng).

    python3 generate_data.py            # dừng nếu đã có dữ liệu mở rộng
    python3 generate_data.py --force    # xoá dữ liệu mở rộng cũ rồi sinh lại
    python3 generate_data.py --dry-run  # chỉ in thống kê, không ghi lên Atlas

Quy ước (khớp `lab02_nosql/AGENTS.md`):
- `random.seed(2026)` → chạy lại cho cùng dữ liệu.
- Giữ nguyên bộ mẫu 5 khách / 5 sản phẩm / 6 đơn của đề; phần sinh thêm dùng
  `customer_id` 6–100, `product_id` 106–130, `order_id` 2001–2500.
- ~8 khách không có đơn (dữ liệu cho N18) và 4 sản phẩm không bán được.
- `items` nhúng `{product_id, name, price, quantity}`; `price` chụp từ `products` lúc tạo đơn
  (đây là dữ liệu để phân tích N20).
- Không đặt `discount` ở bước này: N19 trong `n_homework.py` tự thêm không đồng nhất.
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, timedelta

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows

from connect import get_database

SEED = 2026
N_CUSTOMERS, N_PRODUCTS, N_ORDERS = 100, 30, 500
FIRST_ORDER_ID = 2001

CITIES = ["Hanoi", "HCMC", "Danang", "Hue", "Cantho", "Nhatrang", "Haiphong"]
FAMILY = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Vu", "Dang", "Bui", "Do", "Ho"]
MIDDLE = ["Van", "Thi", "Minh", "Duc", "Thu", "Quang", "Ngoc", "Hai", "Lan", "Anh"]
GIVEN = ["An", "Binh", "Chi", "Dung", "Ha", "Hoang", "Khanh", "Linh", "Mai", "Nam",
         "Oanh", "Phuong", "Quan", "Son", "Trang", "Tuan", "Vy", "Yen", "Hung", "Thao"]
PRODUCT_NAMES = [
    ("Laptop Pro", "Electronics", 22_000_000), ("Ultrabook", "Electronics", 18_500_000),
    ("Tablet", "Electronics", 7_200_000), ("Smartphone", "Electronics", 9_800_000),
    ("Monitor 27", "Electronics", 5_400_000), ("Webcam", "Electronics", 890_000),
    ("SSD 1TB", "Component", 2_450_000), ("RAM 16GB", "Component", 1_450_000),
    ("CPU Cooler", "Component", 720_000), ("Power Supply", "Component", 1_980_000),
    ("Graphics Card", "Component", 7_200_000), ("Case Fan", "Component", 210_000),
    ("Mechanical Keyboard", "Accessories", 1_250_000), ("Wireless Mouse", "Accessories", 390_000),
    ("Headset", "Accessories", 950_000), ("USB Hub", "Accessories", 320_000),
    ("Laptop Sleeve", "Accessories", 280_000), ("Desk Lamp", "Accessories", 430_000),
    ("Mousepad", "Accessories", 120_000), ("Cable HDMI", "Accessories", 150_000),
    ("Chair", "Furniture", 2_900_000), ("Desk", "Furniture", 3_600_000),
    ("Shelf", "Furniture", 1_150_000), ("Drawer", "Furniture", 1_750_000),
    ("Projector", "Office", 8_400_000),
]


def build_customers() -> list[dict]:
    rng = random.Random(SEED)
    base = [
        {"customer_id": 1, "name": "An", "city": "Hanoi"},
        {"customer_id": 2, "name": "Binh", "city": "Hanoi"},
        {"customer_id": 3, "name": "Chi", "city": "Danang"},
        {"customer_id": 4, "name": "Dung", "city": "HCMC"},
        {"customer_id": 5, "name": "Ha", "city": "Hanoi"},
    ]
    extra = []
    for cid in range(6, N_CUSTOMERS + 1):
        name = f"{rng.choice(FAMILY)} {rng.choice(MIDDLE)} {rng.choice(GIVEN)}"
        extra.append({"customer_id": cid, "name": name, "city": rng.choice(CITIES)})
    return base + extra


def build_products() -> list[dict]:
    base = [
        {"product_id": 101, "name": "Laptop", "category": "Electronics", "price": 15_000_000},
        {"product_id": 102, "name": "Mouse", "category": "Accessories", "price": 250_000},
        {"product_id": 103, "name": "Keyboard", "category": "Accessories", "price": 650_000},
        {"product_id": 104, "name": "Monitor", "category": "Electronics", "price": 3_500_000},
        {"product_id": 105, "name": "Headphones", "category": "Accessories", "price": 800_000},
    ]
    extra = [
        {"product_id": 106 + i, "name": name, "category": category, "price": price}
        for i, (name, category, price) in enumerate(PRODUCT_NAMES)
    ]
    return base + extra


def build_orders(customers: list[dict], products: list[dict]) -> list[dict]:
    rng = random.Random(SEED + 1)
    by_id = {p["product_id"]: p for p in products}
    # 8 khách cuối không có đơn; 4 sản phẩm cuối (127–130) không bán được
    buyers = [c["customer_id"] for c in customers][:-8]
    sellable = [p["product_id"] for p in products if p["product_id"] <= 126]

    start = date(2025, 11, 1)
    end = date(2026, 10, 31)
    span = (end - start).days

    orders = []
    for i in range(N_ORDERS):
        order_id = FIRST_ORDER_ID + i
        customer_id = rng.choice(buyers)
        order_date = (start + timedelta(days=rng.randint(0, span))).isoformat()
        picked = rng.sample(sellable, rng.randint(1, 5))
        items = []
        for product_id in picked:
            product = by_id[product_id]
            items.append({
                "product_id": product_id,
                "name": product["name"],
                "price": product["price"],
                "quantity": rng.randint(1, 3),
            })
        orders.append({"order_id": order_id, "customer_id": customer_id,
                       "order_date": order_date, "items": items})
    orders.sort(key=lambda o: (o["order_date"], o["order_id"]))
    return orders


def summarise(customers, products, orders) -> dict:
    return {
        "customers": len(customers),
        "products": len(products),
        "orders": len(orders),
        "items": sum(len(o["items"]) for o in orders),
        "customers_without_orders": len(customers) - len({o["customer_id"] for o in orders}),
        "products_never_sold": len(products) - len({i["product_id"] for o in orders for i in o["items"]}),
        "date_from": min(o["order_date"] for o in orders),
        "date_to": max(o["order_date"] for o in orders),
        "seed": SEED,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh dữ liệu mở rộng LAB 02 (500 đơn)")
    ap.add_argument("--force", action="store_true", help="xoá dữ liệu mở rộng cũ rồi sinh lại")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in thống kê, không ghi lên Atlas")
    args = ap.parse_args()

    customers, products, orders = build_customers(), build_products(), build_orders(
        build_customers(), build_products())
    stats = summarise(customers, products, orders)

    print(f"seed = {SEED}")
    print(f"  customers           {stats['customers']:>5}")
    print(f"  products            {stats['products']:>5}")
    print(f"  orders              {stats['orders']:>5}")
    print(f"  dòng items          {stats['items']:>5}")
    print(f"  khách chưa có đơn   {stats['customers_without_orders']:>5}")
    print(f"  sản phẩm chưa bán   {stats['products_never_sold']:>5}")
    print(f"  khoảng ngày         {stats['date_from']} → {stats['date_to']}")
    if args.dry_run:
        print("[i] --dry-run: không ghi lên Atlas")
        return 0

    db = get_database()
    try:
        existing = db.orders.count_documents({"order_id": {"$gte": FIRST_ORDER_ID}})
        if existing and not args.force:
            raise SystemExit(
                f"Đã có {existing} đơn mở rộng (order_id >= {FIRST_ORDER_ID}). "
                "Dùng --force để xoá và sinh lại.")
        if existing:
            db.orders.delete_many({"order_id": {"$gte": FIRST_ORDER_ID}})
            db.customers.delete_many({"customer_id": {"$gt": 5}})
            db.products.delete_many({"product_id": {"$gt": 105}})

        db.customers.insert_many([c for c in customers if c["customer_id"] > 5])
        db.products.insert_many([p for p in products if p["product_id"] > 105])
        db.orders.insert_many(orders)

        print("\nSau khi nạp (trên Atlas):")
        for name in ("customers", "products", "orders"):
            print(f"  {name:<10} {db[name].count_documents({}):>5}")
        sample = db.orders.find_one({"order_id": FIRST_ORDER_ID}, {"_id": 0})
        print(f"  mẫu đơn {FIRST_ORDER_ID}: {len(sample['items'])} items, "
              f"ngày {sample['order_date']}")
    finally:
        db.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
