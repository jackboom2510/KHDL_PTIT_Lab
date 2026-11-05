#!/usr/bin/env python3
"""Sinh dữ liệu mở rộng cho LAB 01 (bài về nhà): ≥100 khách, ≥30 sản phẩm,
≥500 đơn, ≥1.000 dòng đơn hàng — giữ nguyên dữ liệu mẫu trong đề và khoá ngoại hợp lệ.

Kết quả ghi vào `data/sales_extended.db` (mặc định), KHÔNG đụng vào `data/sales.db`:

    python3 generate_data.py            # dừng nếu file đã tồn tại
    python3 generate_data.py --force    # dựng lại từ đầu

Quy ước dữ liệu:
- 100 khách: id 1–5 là dữ liệu mẫu PDF, id 6–100 sinh thêm.
- 30 sản phẩm: id 101–105 mẫu, 106–130 sinh thêm.
- 500 đơn: id 1001–1006 mẫu, 1007–1500 sinh thêm.
- ≥1.000 dòng đơn: 8 dòng mẫu + phần sinh thêm (mỗi đơn 1–5 sản phẩm).
- `random.seed(2026)` → chạy lại cho cùng dữ liệu.
- Khoảng 8% khách không có đơn (dữ liệu cho S17) và 4 sản phẩm không bán được (S18).
"""

from __future__ import annotations

import argparse
import random
import sqlite3
import sys
from datetime import date, timedelta

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows
from pathlib import Path

BASE = Path(__file__).resolve().parent
SQL_DIR = BASE / "sql"
OUT = BASE / "data" / "sales_extended.db"

SEED = 2026
N_CUSTOMERS = 100
N_PRODUCTS = 30
N_ORDERS = 500
MIN_ITEMS, MAX_ITEMS = 1, 5

SURNAMES = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Vu", "Dang", "Bui", "Do", "Ho"]
GIVEN = ["An", "Binh", "Chi", "Dung", "Ha", "Lan", "Minh", "Nam", "Oanh", "Phuc",
         "Quang", "Son", "Trang", "Tuan", "Vy", "Yen", "Khanh", "Linh", "Mai", "Nga"]
CITIES = ["Hanoi", "HCMC", "Danang", "Hue", "Cantho", "Haiphong", "Nhatrang", "Vungtau"]
CITY_WEIGHTS = [30, 25, 12, 8, 8, 9, 4, 4]

CATALOG = [
    ("Laptop", "Electronics", 15000000), ("Mouse", "Accessories", 250000),
    ("Keyboard", "Accessories", 650000), ("Monitor", "Electronics", 3500000),
    ("Headphones", "Accessories", 800000), ("Webcam", "Accessories", 900000),
    ("SSD 1TB", "Storage", 2200000), ("HDD 2TB", "Storage", 1800000),
    ("USB Hub", "Accessories", 350000), ("Docking Station", "Accessories", 2900000),
    ("Tablet", "Electronics", 6500000), ("Smartphone", "Electronics", 9500000),
    ("Printer", "Office", 3100000), ("Scanner", "Office", 2400000),
    ("Projector", "Office", 8700000), ("Router", "Network", 1500000),
    ("Switch 8-port", "Network", 1250000), ("NAS 2-bay", "Storage", 5400000),
    ("Microphone", "Audio", 1200000), ("Speaker", "Audio", 1750000),
    ("Sound Card", "Audio", 2100000), ("Graphics Card", "Component", 7200000),
    ("RAM 16GB", "Component", 1450000), ("CPU Cooler", "Component", 850000),
    ("Power Supply", "Component", 1650000), ("Case", "Component", 950000),
    ("Chair", "Furniture", 3300000), ("Desk", "Furniture", 4100000),
    ("Lamp", "Furniture", 400000), ("Cable HDMI", "Accessories", 150000),
]


def build(out: Path, force: bool) -> int:
    if out.exists():
        if not force:
            print(f"[skip] {out} đã tồn tại. Dùng --force để dựng lại.")
            return 0
        out.unlink()
    out.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)
    con = sqlite3.connect(out)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        for name in ("schema.sql", "seed.sql"):
            con.executescript((SQL_DIR / name).read_text(encoding="utf-8"))

        # --- khách hàng: 6..100 -----------------------------------------------
        used_names = {(r[0], r[1]) for r in con.execute("SELECT name, city FROM customers")}
        customers = []
        while len(customers) < N_CUSTOMERS - 5:
            name = f"{rng.choice(SURNAMES)} {rng.choice(GIVEN)}"
            city = rng.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
            if (name, city) in used_names:
                continue
            used_names.add((name, city))
            customers.append((6 + len(customers), name, city))
        con.executemany("INSERT INTO customers VALUES (?,?,?)", customers)

        # --- sản phẩm: 106..130 ----------------------------------------------
        existing_names = {r[0] for r in con.execute("SELECT name FROM products")}
        products = []
        for i, (name, category, price) in enumerate(CATALOG[: N_PRODUCTS - 5], start=106):
            if name in existing_names:
                name = f"{name} (gen)"
            jitter = rng.choice([0.85, 0.9, 1.0, 1.0, 1.1, 1.2])
            products.append((i, name, category, round(price * jitter, -3)))
        con.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

        product_ids = [r[0] for r in con.execute("SELECT product_id FROM products")]
        # 4 sản phẩm cuối không bao giờ được bán -> dữ liệu cho S18
        sellable = product_ids[:-4]

        # --- đơn hàng: 1007..1500 + dòng đơn --------------------------------
        # ~8% khách không có đơn để S17 có kết quả
        all_customers = [r[0] for r in con.execute("SELECT customer_id FROM customers")]
        no_order = set(rng.sample(all_customers, k=8))
        buyers = [c for c in all_customers if c not in no_order]

        start = date(2025, 10, 1)   # trải 12 tháng để S16 có nhiều nhóm tháng
        span = (date(2026, 10, 1) - start).days

        orders, items = [], []
        next_order_id = 1007
        next_order_id = 1007
        while next_order_id <= 1006 + N_ORDERS - 6:
            customer_id = rng.choice(buyers)
            order_date = (start + timedelta(days=rng.randint(0, span))).isoformat()
            orders.append((next_order_id, customer_id, order_date))
            k = rng.randint(MIN_ITEMS, MAX_ITEMS)
            for product_id in rng.sample(sellable, k=k):
                items.append((next_order_id, product_id, rng.randint(1, 3)))
            next_order_id += 1

        con.executemany("INSERT INTO orders VALUES (?,?,?)", orders)
        con.executemany("INSERT INTO order_items VALUES (?,?,?)", items)
        con.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
        con.commit()

        print(f"Đã tạo {out} (seed={SEED})")
        for table in ("customers", "products", "orders", "order_items"):
            n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:<12} {n:>6}")
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        print(f"  foreign_key_check: {'ok' if not fk else f'{len(fk)} vi phạm'}")
        return 0 if not fk else 1
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sinh dữ liệu mở rộng cho LAB 01")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else (BASE / args.out)
    return build(out, args.force)


if __name__ == "__main__":
    sys.exit(main())
