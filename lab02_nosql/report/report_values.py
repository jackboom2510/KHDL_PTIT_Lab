"""Số liệu dùng chung cho báo cáo LAB 02 (PDF và DOCX).

Tách riêng để `make_report.py` (PDF) và `make_docx.py` (Word) luôn dùng cùng bộ số liệu, cùng
danh sách ảnh và cùng cách định dạng tiền — tránh lệch nội dung giữa hai bản nộp.
"""

from __future__ import annotations

import json
from pathlib import Path

FIGURES = [
    "01_cluster.png", "02_data_explorer.png", "03_connect_seed.png",
    "04_crud_n01_n05.png", "05_crud_n05_n11.png",
    "07_lookup_n12.png", "08_n13_n14_index.png", "09_n15_n20_mo_hinh.png",
    "10_explain_n21.png", "11_expanded_counts.png", "12_n16_n19.png",
    "13_n22_lookup.png",
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
    "n21": {"explain_customer_id": {"stage": "FETCH", "index_name": "idx_orders_customer",
                                    "docs_examined": 7, "keys_examined": 7, "n_returned": 7},
            "explain_no_index_field": {"stage": "COLLSCAN", "index_name": None,
                                       "docs_examined": 506, "keys_examined": 0,
                                       "n_returned": 417}},
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
    # tên tệp -> (chú thích hình trong báo cáo, nội dung phải thấy trong ảnh)
    "01_cluster.png": ("Cluster DSCluster (M0 Free) và database sales_nosql",
                       "Atlas > Data Explorer: DBCluster > sales_nosql với customers, products, "
                       "orders và số document tương ứng"),
    "02_data_explorer.png": ("Data Explorer: document orders có mảng items nhúng",
                             "Mở document order_id 1001, thấy items là array các document "
                             "{product_id, name, price, quantity}"),
    "03_connect_seed.png": ("connect.py và seed.py: kết nối, nạp bộ dữ liệu mẫu 5/5/6",
                            "Terminal: connect.py (Database sales_nosql, 3 collection rỗng) rồi "
                            "seed.py (customers 5, products 5, orders 6, mẫu items nhúng)"),
    "04_crud_n01_n05.png": ("n_answers.py: kết quả N01–N05",
                            "Terminal: N01 danh sách khách, N02 khách Hanoi, N03 sản phẩm > 1 "
                            "triệu, N04 sắp xếp theo giá, N05 insert_one"),
    "05_crud_n05_n11.png": ("n_answers.py: kết quả N05–N11",
                            "Terminal: N05–N07 insert/update/delete, N08 đếm theo thành phố, "
                            "N09 truy vấn mảng items, N10 tổng tiền từng đơn, N11 doanh thu"),
    "07_lookup_n12.png": ("N12 — $lookup + $unwind + $project, 6 dòng ghép",
                          "Terminal: các dòng {order_id, customer_id, name, city}"),
    "08_n13_n14_index.png": ("N13 lọc sau $group và N14 tạo index orders.customer_id",
                             "Terminal: N13 một dòng order_count 2; N14 liệt kê _id_ và "
                             "idx_orders_customer"),
    "09_n15_n20_mo_hinh.png": ("N15 mô hình nhúng/tham chiếu và N20 đổi giá trong products",
                               "Terminal: N15 so sánh embedded vs reference; N20 giá products "
                               "16.000.000 nhưng items.price trong đơn cũ vẫn 15.000.000"),
    "10_explain_n21.png": ("explain(): 7 document khi có index, 506 khi COLLSCAN",
                           "Terminal: N21 explain_customer_id (index idx_orders_customer, "
                           "docs_examined 7) và explain_no_index_field (COLLSCAN, "
                           "docs_examined 506, n_returned 417)"),
    "11_expanded_counts.png": ("generate_data.py: sinh 100 khách / 30 sản phẩm / 500 đơn",
                               "Terminal: seed 2026, 1.521 dòng items, 8 khách chưa đơn, "
                               "bảng đếm document sau khi nạp trên Atlas (orders 506)"),
    "12_n16_n19.png": ("N16–N19 trên dữ liệu mở rộng",
                       "Terminal: N16 doanh thu theo thành phố, N17 ba sản phẩm dẫn đầu, "
                       "N18 8 khách chưa đặt hàng, N19 discount không đồng nhất"),
    "13_n22_lookup.png": ("N22 — đối chiếu JOIN của SQL với $lookup",
                          "Terminal: pipeline $lookup/$unwind/$project, phần khác biệt và "
                          "kết quả ghép với so_dong 506"),
}

# Ảnh nào thuộc mục (tiêu chí) nào của báo cáo
FIGURE_SECTION = {
    "01_cluster.png": 2, "02_data_explorer.png": 2, "03_connect_seed.png": 2,
    "04_crud_n01_n05.png": 3, "05_crud_n05_n11.png": 3, "08_n13_n14_index.png": 3,
    "07_lookup_n12.png": 4,
    "09_n15_n20_mo_hinh.png": 5, "10_explain_n21.png": 5,
    "11_expanded_counts.png": 6, "12_n16_n19.png": 6, "13_n22_lookup.png": 6,
}
