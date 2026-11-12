# Hướng dẫn chụp ảnh minh chứng LAB 02 (Atlas + Cloud Shell)

Ảnh minh chứng phải là **ảnh chụp màn hình thật** khi làm trên Atlas và Cloud Shell, không phải
ảnh dựng lại. Tài liệu này liệt kê đúng thao tác/lệnh cần chạy và nội dung cần thấy trong từng
ảnh. Tệp lưu vào `lab02_nosql/evidence/` đúng tên dưới đây (khớp bảng ở mục 7 báo cáo).

| Tệp | Nội dung cần thấy | Mục báo cáo |
| --- | --- | --- |
| `01_cluster.png` | Atlas: Data Explorer > `DBCluster` > `sales_nosql` với `customers` (100), `products` (30), `orders` (506) | 2 — Thiết lập, seed |
| `02_data_explorer.png` | Mở document `order_id 1001` thấy mảng `items` gồm `{product_id, name, price, quantity}` | 2 — Thiết lập, seed |
| `03_connect_seed.png` | Terminal: `connect.py` (3 collection rỗng) rồi `seed.py` (5/5/6 + mẫu items) | 2 — Thiết lập, seed |
| `04_crud_n01_n05.png` | Terminal: N01–N05 | 3 — CRUD, filter |
| `05_crud_n05_n11.png` | Terminal: N05–N11 (insert/update/delete, N08, N09, N10, N11) | 3, 4 |
| `07_lookup_n12.png` | Terminal: N12 `$lookup` + `$unwind`, 6 dòng ghép | 4 — Aggregation |
| `08_n13_n14_index.png` | Terminal: N13 lọc sau `$group`, N14 tạo `idx_orders_customer` | 3 — CRUD, filter |
| `09_n15_n20_mo_hinh.png` | Terminal: N15 (embedded vs reference) và N20 (đổi giá products) | 5 — Index, mô hình |
| `10_explain_n21.png` | Terminal: N21 `explain_customer_id` (index, `docs_examined` 7) và `explain_no_index_field` (`COLLSCAN`, 506) | 5 — Index, mô hình |
| `11_expanded_counts.png` | Terminal: `generate_data.py --force` — 100/30/500/1.521 + bảng đếm sau khi nạp (`orders` 506) | 6 — Mở rộng |
| `12_n16_n19.png` | Terminal: N16, N17, N18, N19 | 6 — Mở rộng |
| `13_n22_lookup.png` | Terminal: N22 pipeline `$lookup` và `so_dong` 506 | 6 — Mở rộng |

Số hiệu tệp giữ đúng thứ tự câu hỏi, nên có thể ghép nhiều lần chụp của cùng một mục thành một
tệp (xem `prepare_evidence.py`).

**Che thông tin nhạy cảm**: đừng để lộ mật khẩu/URI trong ảnh. `getpass` không hiển thị URI nên
chỉ cần không mở file chứa URI khi chụp.

---

## Bước 0 — chuẩn bị trên Cloud Shell

```bash
cd ~/KHDL_PTIT_Lab/lab02_nosql      # hoặc thư mục bạn clone repo về
python3 -m venv .venv && source .venv/bin/activate
pip install "pymongo[srv]"
curl -4 https://api.ipify.org       # thêm IP này vào Atlas → Network Access
```

Sau đó chạy lần lượt (mỗi lần dán URI khi được hỏi):

```bash
python3 connect.py                  # kỳ vọng: Connected successfully
python3 seed.py                     # customers 5, products 5, orders 6
python3 lab_queries.py
```

## Bước 1 — phần bắt buộc (ảnh 3–5, 7–9)

```bash
python3 n_answers.py --json data/lab02_results_n01_n15.json
```

Chụp màn hình cuộn dần: **N01–N05** → `04_crud_n01_n05.png`; **N05–N11** (thấy cả N10 tổng
44.000.000) → `05_crud_n05_n11.png`; **N12** → `07_lookup_n12.png`; **N13 và N14** →
`08_n13_n14_index.png`; **N15** → phần trên của `09_n15_n20_mo_hinh.png`.

## Bước 2 — dữ liệu mở rộng (làm trước ảnh 6 và ảnh 7)

`n_homework.py` yêu cầu ≥ 100 đơn, nên phải nạp dữ liệu mở rộng **trước**:

```bash
python3 generate_data.py --force
```

## Ảnh 11 — `11_expanded_counts.png`

Chụp ngay phần thống kê của lần chạy trên: `seed = 2026`, 100 khách / 30 sản phẩm / 500 đơn /
1.521 dòng items / 8 khách chưa có đơn / 4 sản phẩm chưa bán, và phần **"Sau khi nạp (trên
Atlas)"** đếm document của 3 collection. (Chỉ xem lại thống kê mà không ghi: `--dry-run`.)

## Bước 3 — phần bổ sung (ảnh 9–13)

```bash
python3 n_homework.py --json data/lab02_results_n16_n22.json
```

Chụp **N16–N19** → `12_n16_n19.png`; **N20** → phần dưới của `09_n15_n20_mo_hinh.png`; **N21**
→ `10_explain_n21.png` (phải thấy `idx_orders_customer`, `docs_examined` 7 so với `COLLSCAN`
`docs_examined` 506); **N22** → `13_n22_lookup.png`.

## Ảnh 1–2 — trên Atlas

Atlas → **Data Explorer**: chụp `DBCluster > sales_nosql` với 3 collection → `01_cluster.png`;
mở `orders` → document `order_id: 1001` thấy `items` là array 2 document → `02_data_explorer.png`.

---

## Chuẩn hoá ảnh trước khi đưa vào báo cáo

`prepare_evidence.py` **không** tạo nội dung ảnh: nó chỉ cắt khoảng trống thừa ở mép, ghép các
lần chụp liên tiếp của cùng một mục và lưu ra đúng tên tệp ở bảng trên.

```bash
python3 prepare_evidence.py --src ~/Pictures/lab02 --dry-run   # kiểm tra đủ ảnh nguồn
python3 prepare_evidence.py --src ~/Pictures/lab02             # ghi ảnh đã chuẩn hoá
```

Sửa bảng `MAP` trong script nếu tên ảnh chụp gốc khác quy ước.

## Xuất lại báo cáo và đóng gói

```bash
# từ gốc repo
python3 lab02_nosql/report/make_report.py --images lab02_nosql/evidence
python3 lab02_nosql/report/make_docx.py   --images lab02_nosql/evidence
bash lab02_nosql/pack_submission.sh B23DCKH105
```

Bản PDF tự chọn tỉ lệ ảnh để không quá 6 trang; bản Word chèn ảnh rộng hết khổ chữ và cao tối
đa 11 cm.

## Kiểm tra không lộ bí mật trước khi commit/nộp

```bash
grep -rniE "mongodb\+srv://|student_lab:" --exclude-dir=.git . || echo "không có secret"
```

Ảnh chụp cũng phải kiểm tra: không để lộ URI, mật khẩu, email tài khoản Atlas trong khung hình.
