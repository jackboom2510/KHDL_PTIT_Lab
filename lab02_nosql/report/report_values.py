"""Số liệu dùng chung cho báo cáo LAB 02 (PDF và DOCX).

Tách riêng để `make_report.py` (PDF) và `make_docx.py` (Word) luôn dùng cùng bộ số liệu, cùng
danh sách ảnh và cùng cách định dạng tiền — tránh lệch nội dung giữa hai bản nộp.
"""

from __future__ import annotations

import json
from pathlib import Path

FIGURES = [
    "01_cluster.png", "02_data_explorer.png", "03_crud.png",
    "04_aggregation_n10.png", "05_lookup_n12.png",
    "06_explain_n21.png", "07_expanded_counts.png",
]

# Số liệu dự phòng: đo bằng cách chạy chính các pipeline trong n_answers.py / n_homework.py
# trên cùng bộ dữ liệu seed 2026. Khi có JSON từ Atlas, mọi con số dưới đây được thay thế.
DEFAULTS = {
    "n01": [{"customer_id": 1, "name": "An", "city": "Hanoi"},
            {"customer_id": 2, "name": "Binh", "city": "Hanoi"},
            {"customer_id": 3, "name": "Chi", "city": "Danang"},
            {"customer_id": 4, "name": "Dung", "city": "HCMC"},
            {"customer_id": 5, "name": "Ha", "city": "Hanoi"}],
    "n02": [{"customer_id": 1, "name": "An", "city": "Hanoi"},
            {"customer_id": 2, "name": "Binh", "city": "Hanoi"},
            {"customer_id": 5, "name": "Ha", "city": "Hanoi"}],
    "n03": [{"product_id": 101, "name": "Laptop", "price": 15000000},
            {"product_id": 104, "name": "Monitor", "price": 3500000}],
    "n08": [{"city": "Hanoi", "count": 3}, {"city": "Danang", "count": 1},
            {"city": "HCMC", "count": 1}],
    "n09": [{"order_id": 1001}, {"order_id": 1004}],
    "n10": [{"order_id": 1001, "total": 15500000}, {"order_id": 1004, "total": 15000000},
            {"order_id": 1006, "total": 7000000}, {"order_id": 1002, "total": 4150000},
            {"order_id": 1003, "total": 1600000}, {"order_id": 1005, "total": 750000}],
    "n11": [{"customer_id": 1, "name": "An", "revenue": 17100000},
            {"customer_id": 3, "name": "Chi", "revenue": 15000000},
            {"customer_id": 5, "name": "Ha", "revenue": 7000000},
            {"customer_id": 2, "name": "Binh", "revenue": 4150000},
            {"customer_id": 4, "name": "Dung", "revenue": 750000}],
    "n12": [{"order_id": 1001, "name": "An", "city": "Hanoi"}],
    "n13": [{"customer_id": 1, "name": "An", "order_count": 2}],
    "n14": {"created": "idx_orders_customer",
            "indexes_after": [{"name": "_id_"}, {"name": "idx_orders_customer"}]},
    "n16": [{"city": "Cantho", "revenue": 2318630000, "customers": 16},
            {"city": "Hue", "revenue": 2291320000, "customers": 15}],
    "n17": [{"product_id": 106, "name": "Laptop Pro", "revenue": 2728000000, "quantity": 124},
            {"product_id": 107, "name": "Ultrabook", "revenue": 2090500000, "quantity": 113},
            {"product_id": 101, "name": "Laptop", "revenue": 2070000000, "quantity": 138}],
    "n18": [{"customer_id": 93, "name": "Bui Anh Thao", "city": "Hanoi"}],
    "n19": {"orders_with_discount": 251, "orders_without_discount": 255,
            "totals": {"gross": 12758940000, "net": 12210157000, "discount_amount": 548783000}},
    "n20": {"product_price_before": 15000000, "product_price_after_update": 16000000,
            "price_in_old_order_before": 15000000, "price_in_old_order_after": 15000000,
            "embedded_copies_price": True},
    "n21": {"explain_customer_id": {"stage": "IXSCAN", "index_name": "idx_orders_customer"},
            "explain_no_index_field": {"stage": "COLLSCAN"}},
    "n22": {"so_dong": 506},
}


def load_results(paths: list[Path]) -> dict:
    data = json.loads(json.dumps(DEFAULTS))          # deep copy
    for path in paths:
        data.update(json.loads(Path(path).read_text(encoding="utf-8")))
    return data


def vnd(value) -> str:
    try:
        return f"{int(round(float(value))):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(value)



# Tên tệp ảnh -> (chú thích hình, nội dung cần thấy khi chụp)
FIGURE_INFO = {
    "01_cluster.png": ("Cluster DSCluster (M0 Free) và database sales_nosql",
                       "Atlas > Database: cluster DSCluster nhãn Free; Browse Collections có "
                       "sales_nosql với customers, products, orders"),
    "02_data_explorer.png": ("Data Explorer: document orders có mảng items nhúng",
                             "Mở một document orders, thấy items là array các document "
                             "{product_id, name, price, quantity}"),
    "03_crud.png": ("Chạy n_answers.py: kết quả N01–N08 trên terminal Cloud Shell",
                    "Terminal: python3 n_answers.py, phần N01–N08"),
    "04_aggregation_n10.png": ("Kết quả N10 với $unwind và $group",
                               "Terminal: bảng order_id + total của N10"),
    "05_lookup_n12.png": ("Kết quả N12 với $lookup và $unwind",
                          "Terminal: các dòng {order_id, name, city} sau khi ghép"),
    "06_explain_n21.png": ("explain(): IXSCAN khi có index, COLLSCAN khi không có",
                           "Terminal: N21 in stage IXSCAN và COLLSCAN"),
    "07_expanded_counts.png": ("Sinh dữ liệu mở rộng và đếm document trên Atlas",
                               "Terminal: generate_data.py --force và số document "
                               "100 / 30 / 500 / 1.521"),
}

# Ảnh nào thuộc mục (tiêu chí) nào của báo cáo
FIGURE_SECTION = {
    "01_cluster.png": 2, "02_data_explorer.png": 2, "03_crud.png": 3,
    "04_aggregation_n10.png": 4, "05_lookup_n12.png": 4,
    "06_explain_n21.png": 5, "07_expanded_counts.png": 6,
}

# Thứ tự chèn ảnh trong báo cáo: (sau đoạn nào, ảnh nào)
# dùng trong make_docx.py; make_report.py chèn trực tiếp trong từng hàm tiêu chí.
