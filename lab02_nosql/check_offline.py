#!/usr/bin/env python3
"""Kiểm tra N01–N22 mà **không cần Atlas**: chạy đúng các pipeline thật trên MongoDB giả lập.

    pip install mongomock
    python3 check_offline.py                 # chạy toàn bộ, in tóm tắt
    python3 check_offline.py --json data/lab02_results_n01_n15.json
    python3 check_offline.py --keep          # giữ dữ liệu trong bộ nhớ để xem kỹ

Mục đích: bắt lỗi cú pháp pipeline, sai tên trường, sai thứ tự stage trước khi chạy trên Atlas
(vốn tốn thời gian vì phải dán URI mỗi lần). Script **không** thay thế lần chạy thật trên Atlas:
`số liệu nộp bài phải xuất từ lần chạy thật`.

Lưu ý: mongomock không hỗ trợ `explain()`, nên N21 chỉ kiểm tra index được tạo và pipeline liên
quan; phần `stage` (IXSCAN/COLLSCAN) chỉ có khi chạy trên Atlas thật.
"""

from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))


def fake_connect() -> tuple[object, types.ModuleType]:
    """Tạo connect giả trỏ về MongoClient trong bộ nhớ (mongomock)."""
    try:
        import mongomock
    except ImportError:
        raise SystemExit("Cần mongomock: pip install mongomock")

    client = mongomock.MongoClient()
    db = client["sales_nosql"]

    module = types.ModuleType("connect")
    module.DB_NAME = "sales_nosql"
    module.get_database = lambda uri=None: db
    module.get_client = lambda uri=None: client
    sys.modules["connect"] = module
    return db, module


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra N01–N22 bằng mongomock (không cần Atlas)")
    ap.add_argument("--json", type=Path, default=None,
                    help="ghi kết quả N01–N22 ra JSON cho report/make_report.py")
    ap.add_argument("--outdir", type=Path, default=LAB / "data",
                    help="thư mục ghi JSON (mặc định lab02_nosql/data)")
    args = ap.parse_args()

    db, _ = fake_connect()

    import generate_data
    import n_answers
    import n_homework
    import seed

    # --- bộ dữ liệu mẫu của đề ---
    db.customers.insert_many(seed.CUSTOMERS)
    db.products.insert_many(seed.PRODUCTS)
    db.orders.insert_many(seed.build_order_docs())
    counts = {c: db[c].count_documents({}) for c in ("customers", "products", "orders")}
    assert counts == {"customers": 5, "products": 5, "orders": 6}, counts
    print(f"[ok] seed mẫu: {counts}")

    # --- N01–N15 ---
    answers = {}
    for code, fn in n_answers.ANSWERS.items():
        answers[code] = fn(db)
        size = len(answers[code]) if isinstance(answers[code], list) else 1
        print(f"  {code.upper()} ok ({size})")
    assert db.customers.count_documents({}) == 5, "N05–N07 phải trả dữ liệu về 5 khách"
    assert len(answers["n02"]) == 3, "Hanoi phải có 3 khách"
    assert sum(x["total"] for x in answers["n10"]) == 44_000_000, "N10 tổng phải là 44.000.000"
    print("[ok] N01–N15")

    # --- dữ liệu mở rộng ---
    customers = generate_data.build_customers()
    products = generate_data.build_products()
    orders = generate_data.build_orders(customers, products)
    stats = generate_data.summarise(customers, products, orders)
    assert stats["customers"] == 100 and stats["products"] == 30, stats
    assert stats["orders"] == 500 and stats["items"] >= 1000, stats
    assert stats["customers_without_orders"] == 8, stats
    assert stats["products_never_sold"] == 4, stats
    db.customers.insert_many([c for c in customers if c["customer_id"] > 5])
    db.products.insert_many([p for p in products if p["product_id"] > 105])
    db.orders.insert_many(orders)
    print(f"[ok] dữ liệu mở rộng: {stats}")

    # --- N16–N22 ---
    homework = {}
    for code, fn in n_homework.ANSWERS.items():
        homework[code] = fn(db)
        size = len(homework[code]) if isinstance(homework[code], list) else 1
        print(f"  {code.upper()} ok ({size})")
    assert len(homework["n18"]) == 8, "N18 phải tìm đúng 8 khách chưa đặt hàng"
    assert homework["n20"]["embedded_copies_price"] is True, "N20: items.price phải là bản sao"
    assert homework["n20"]["restored_price"] == 15_000_000, "N20 phải khôi phục giá gốc"
    assert len(homework["n17"]) == 3, "N17 phải trả top 3 sản phẩm"
    print("[ok] N16–N22")

    if args.json or True:
        outdir = args.outdir
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "lab02_results_n01_n15.json").write_text(
            json.dumps(answers, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        (outdir / "lab02_results_n16_n22.json").write_text(
            json.dumps(homework, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(f"[ok] đã ghi {outdir}/lab02_results_*.json")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps({**answers, **homework}, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8")

    print("\nTất cả 22 câu chạy được. Nhớ chạy lại trên Atlas thật để lấy số liệu nộp bài.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
