# LAB 02 — Yêu cầu trích từ đề PDF

Nguồn: `Lab_02_NoSQL_MongoDB_Google_Cloud_IntroDataScience.pdf` (4 trang).
Chủ đề: **MongoDB Atlas Free + Google Cloud Shell (Python / PyMongo)**.

## 1. Mục tiêu

- Tạo database/collection/document MongoDB; phân biệt embedded document (NoSQL) với bảng
  quan hệ (SQL).
- Dùng CRUD, truy vấn trường lồng nhau, aggregation, `$lookup`, index.

## 2. Thiết lập Atlas (miễn phí)

1. Đăng ký https://www.mongodb.com/cloud/atlas/register (Sign up with Google).
2. Project `DataScienceLab` → Create/Build a Database → **Free (M0)**. Không chọn Flex/Dedicated.
3. Provider Google Cloud + region có Free nếu khả dụng (nếu không, provider khác có Free và ghi
   rõ trong báo cáo). Tên cluster: `DSCluster`.
4. Tạo DB user `student_lab` với mật khẩu mạnh; **không** đưa mật khẩu vào bài nộp.
5. Cluster → Connect → Drivers → Python: lấy URI `mongodb+srv://...`.
6. Cloud Shell: `curl -4 https://api.ipify.org` → Atlas → Security → Network Access → add IP
   (hoặc /32). "Add My Current IP" trên trình duyệt có thể khác IP Cloud Shell. Không mở
   `0.0.0.0/0` lâu dài.

```bash
curl -4 https://api.ipify.org
mkdir -p ~/data_science/nosql_lab
cd ~/data_science/nosql_lab
python3 -m venv .venv
source .venv/bin/activate
pip install "pymongo[srv]"
```

## 3. Kết nối

`connect.py`: `getpass` nhận URI, `MongoClient(uri, serverSelectionTimeoutMS=12000)`,
`client.admin.command('ping')`, trả về `client['sales_nosql']`.

- Mật khẩu có ký tự đặc biệt (`@ % /`) phải URL-encode.
- Timeout → kiểm tra IP/DNS/cluster; `AuthenticationFailed` → kiểm tra user/password.

## 4. Dữ liệu mẫu (embedded items)

`customers` và `products` giống hệt LAB 01. `orders` mỗi document gồm `order_id`,
`customer_id`, `order_date`, `items[]` với `{product_id, name, price, quantity}`.

| Collection | Số document |
| --- | --- |
| customers | 5 |
| products | 5 |
| orders | 6 |

`seed.py` phải dừng nếu đã có dữ liệu:
`raise SystemExit('Data already exists. Use a fresh database.')`.
Kiểm tra trên Atlas → Data Explorer: mở một order, thấy `items` là array document.

## 5. Bài tập bắt buộc

| Mã | Yêu cầu |
| --- | --- |
| N01 | Liệt kê tất cả customers (`find`) |
| N02 | Khách hàng ở Hanoi |
| N03 | Sản phẩm giá > 1 triệu (`$gt`) |
| N04 | Sắp xếp theo giá giảm dần |
| N05 | Thêm khách hàng mới (`insert_one`) |
| N06 | Sửa thành phố (`update_one`) |
| N07 | Xoá khách vừa thêm (`delete_one`) |
| N08 | Đếm khách theo thành phố (`$group`) |
| N09 | Đơn hàng chứa Laptop (mảng `items`) |
| N10 | Tổng tiền từng đơn (`$unwind`, `$group`) |
| N11 | Doanh thu theo khách hàng |
| N12 | Ghép orders với customers (`$lookup`) |
| N13 | Khách có ít nhất 2 đơn |
| N14 | Tạo index `orders.customer_id` |
| N15 | Giải thích embedded vs reference |

## 6. Ví dụ aggregation

```python
pipeline = [
    {'$unwind': '$items'},
    {'$group': {'_id': '$order_id',
                'total': {'$sum': {'$multiply': ['$items.price', '$items.quantity']}}}},
    {'$sort': {'total': -1}}
]
for x in db.orders.aggregate(pipeline): print(x)
```

```python
pipeline = [
    {'$lookup': {'from': 'customers', 'localField': 'customer_id',
                 'foreignField': 'customer_id', 'as': 'customer'}},
    {'$unwind': '$customer'},
    {'$project': {'_id': 0, 'order_id': 1, 'name': '$customer.name'}}
]
```

Index mẫu: `db.orders.create_index('customer_id')`. Kiểm tra bằng `explain` nếu dịch vụ cho phép;
dữ liệu mẫu nhỏ nên chưa kết luận được về tốc độ.

## 7. Bài tập bổ sung (homework)

- Dữ liệu giả lập ≥500 đơn, mỗi đơn 1–5 sản phẩm.
- N16 doanh thu theo thành phố; N17 top 3 sản phẩm theo doanh thu; N18 khách chưa đặt hàng
  qua `$lookup`.
- N19 thêm `discount` không đồng nhất giữa các document, xử lý trường thiếu bằng `$ifNull`.
- N20 phân tích nhúng dữ liệu so với tham chiếu, và việc giá ở `products` thay đổi **không**
  cập nhật `items.price` trong đơn hàng cũ.
- N21 tạo index, phân tích kết quả `explain` nếu có.
- N22 đối chiếu `JOIN` của SQL và `$lookup` của MongoDB.

## 8. Nộp bài & chấm điểm

`StudentID_NoSQL.zip`: `connect.py`, `seed.py`, `lab_queries.py`, file mã giải N01–N22,
báo cáo PDF 2–3 trang có ảnh Data Explorer và ảnh chụp màn hình minh chứng.

| Tiêu chí | Điểm |
| --- | --- |
| Thiết lập, seed | 2.0 |
| CRUD và filter | 2.0 |
| Aggregation, lookup | 3.0 |
| Index, giải thích mô hình | 1.5 |
| Mở rộng, báo cáo | 1.5 |
