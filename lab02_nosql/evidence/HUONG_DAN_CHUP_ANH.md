# Hướng dẫn chụp ảnh minh chứng LAB 02 (Atlas + Cloud Shell)

Ảnh minh chứng phải là **ảnh chụp màn hình thật** khi làm trên Atlas và Cloud Shell, không phải
ảnh dựng lại. Tài liệu này liệt kê đúng thao tác/lệnh cần chạy và nội dung cần thấy trong từng
ảnh. Tệp lưu vào `lab02_nosql/evidence/` đúng tên dưới đây (khớp bảng ở mục 7 báo cáo).

| Tệp | Nội dung cần thấy | Mục báo cáo |
| --- | --- | --- |
| `01_cluster.png` | Atlas: cluster `DSCluster` (Free/M0), database `sales_nosql`, 3 collection | 2 — Thiết lập, seed |
| `02_data_explorer.png` | Data Explorer mở một document `orders` thấy mảng `items` | 2 — Thiết lập, seed |
| `03_crud.png` | Terminal: `n_answers.py` in N01–N08 | 3 — CRUD, filter |
| `04_aggregation_n10.png` | Terminal: N10 với `$unwind`/`$group` | 4 — Aggregation |
| `05_lookup_n12.png` | Terminal: N12 `$lookup` + `$unwind` | 4 — Aggregation |
| `06_explain_n21.png` | Terminal: `explain()` ra `IXSCAN` và `COLLSCAN` | 5 — Index, mô hình |
| `07_expanded_counts.png` | Terminal: `generate_data.py` + đếm 100/30/500/1.521 | 6 — Mở rộng |

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

## Ảnh 1 — `01_cluster.png`

Atlas → **Database**: thấy `DSCluster` nhãn *Free*, region đã chọn; mở **Browse Collections**
thấy database `sales_nosql` với `customers`, `products`, `orders`.

## Ảnh 2 — `02_data_explorer.png`

Atlas → Browse Collections → `sales_nosql.orders` → mở document `order_id: 1001`: `items` là
array 2 document `{product_id, name, price, quantity}`. Chụp cả phần đầu document.

## Ảnh 3 — `03_crud.png`

```bash
python3 n_answers.py --json data/lab02_results_n01_n15.json
```

Chụp phần N01–N08 (danh sách khách, khách Hanoi, sản phẩm > 1 triệu, kết quả insert/update/delete).

## Ảnh 4 — `04_aggregation_n10.png`

Cùng màn hình trên, chụp phần **N10** (bảng `order_id` + `total`). Cuộn để thấy đơn 1001 =
15.500.000 và tổng 6 đơn.

## Ảnh 5 — `05_lookup_n12.png`

Chụp phần **N12** (`$lookup` + `$unwind` → `{order_id, name, city}`) — nên thấy 6 dòng ghép.

## Ảnh 6 — `06_explain_n21.png`

```bash
python3 n_homework.py --json data/lab02_results_n16_n22.json
```

Chụp phần **N21**: `explain_customer_id` có `stage: IXSCAN`, `index_name: idx_orders_customer`;
`explain_no_index_field` có `stage: COLLSCAN`.

## Ảnh 7 — `07_expanded_counts.png`

```bash
python3 generate_data.py --force
```

Chụp phần thống kê (100 khách / 30 sản phẩm / 500 đơn / 1.521 dòng items / 8 khách chưa đơn /
4 sản phẩm chưa bán) và phần đếm document sau khi nạp.

---

## Dán ảnh vào bản Word (khung có sẵn)

`lab02_nosql/report/BaoCao_LAB02_B23DCKH105.docx` đã đặt sẵn **7 khung nét đứt** đúng vị trí
của 7 ảnh trong bảng trên; mỗi khung ghi số hiệu hình, tên tệp cần dán và nội dung phải thấy.

- Cách 1 — dán tay: bấm vào trong khung → *Insert > Pictures* → chọn tệp trong `evidence/`.
  Khung nét đứt nằm dưới ảnh, xoá khung sau khi dán nếu muốn (bảng chỉ còn ảnh).
- Cách 2 — chèn tự động khi xuất lại:

```bash
cd lab02_nosql/report
python3 make_docx.py --images ../evidence      # ảnh có tệp thì chèn, thiếu thì để khung
```

## Xuất lại báo cáo và đóng gói

```bash
# từ gốc repo
python3 lab02_nosql/report/make_report.py \
    --images lab02_nosql/evidence \
    --results lab02_nosql/data/lab02_results_n01_n15.json \
              lab02_nosql/data/lab02_results_n16_n22.json

bash lab02_nosql/pack_submission.sh B23DCKH105
```

## Kiểm tra không lộ bí mật trước khi commit/nộp

```bash
grep -rniE "mongodb\+srv://|student_lab:" --exclude-dir=.git . || echo "không có secret"
```

Ảnh chụp cũng phải kiểm tra: không để lộ URI, mật khẩu, email tài khoản Atlas trong khung hình.
