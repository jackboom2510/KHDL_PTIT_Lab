# AGENTS.md — LAB 02 (NoSQL / MongoDB Atlas)

Áp dụng cùng `../AGENTS.md`. File này bổ sung quy ước riêng cho lab MongoDB.

## Phạm vi

- Đề: `../Lab_02_NoSQL_MongoDB_Google_Cloud_IntroDataScience.pdf`.
- Task: N01–N22, xem `../PLAN.md` mục 2 và `../docs/lab02_requirements.md`.
- Cluster: MongoDB Atlas **M0 Free**, DB `sales_nosql`, collection `customers`, `products`,
  `orders`. Không nâng gói, không nhập thẻ.

## Bảo mật — bắt buộc

- **Không** hard-code URI, mật khẩu, `mongodb+srv://...` có credential trong bất kỳ file nào.
- `connect.py` lấy URI bằng `getpass('Paste complete Atlas URI: ')` đúng như PDF; nếu có
  `MONGO_URI` trong môi trường thì được phép ưu tiên để chạy CI, nhưng **không** đọc từ file
  được commit.
- Ảnh chụp màn hình phải che phần mật khẩu của URI.
- Trước khi commit: `git diff | grep -iE "mongodb\+srv://|password|api[_-]?key"` phải rỗng.

## File và trách nhiệm

| File | Vai trò | Bắt buộc nộp |
| --- | --- | --- |
| `connect.py` | `get_database()` → `client['sales_nosql']`, có `ping()` và `serverSelectionTimeoutMS=12000` | ✅ |
| `seed.py` | Seed 3 collection với `items` nhúng; dừng nếu collection đã có dữ liệu | ✅ |
| `lab_queries.py` | Các ví dụ CRUD/aggregation đúng như PDF mục 7 và 9 | ✅ |
| `n_answers.py` | Giải **N01–N15** (bắt buộc), mỗi câu một hàm `n01()`, `n02()`… in kết quả | ✅ |
| `n_homework.py` | Giải **N16–N22** (bổ sung/về nhà), cùng quy ước hàm và nhãn `=== N16 ===` | ✅ |
| `generate_data.py` | Sinh ≥500 đơn, mỗi đơn 1–5 sản phẩm, `customer_id`/`product_id` hợp lệ | ✅ |
| `data/` | File JSON trung gian nếu cần — không commit | — |

### Tách phần bắt buộc và phần bổ sung

Giống LAB 01, hai phần **không trộn file**:

| Phần | File | Dữ liệu | Nội dung |
| --- | --- | --- | --- |
| Bắt buộc | `n_answers.py` | bộ seed 5/5/6 của đề | N01–N15 |
| Bổ sung / về nhà | `n_homework.py` | ≥500 đơn do `generate_data.py` sinh | N16–N22 |

## Quy ước dữ liệu

- Giữ nguyên tên trường như PDF: `customer_id`, `name`, `city`; `product_id`, `name`,
  `category`, `price`; `order_id`, `customer_id`, `order_date`, `items[]` với
  `{product_id, name, price, quantity}`.
- `seed.py` chỉ chạy trên DB rỗng:
  `if any(db[c].count_documents({}) for c in ('customers','products','orders')): raise SystemExit(...)`.
- `generate_data.py` dùng `random.seed(2026)`, `order_id` bắt đầu từ 2001 để không đè dữ liệu
  mẫu, ngày trong 12 tháng gần nhất, `quantity` 1–3, `price` copy từ `products` tại thời điểm
  tạo đơn (đây chính là dữ liệu cho phân tích N20/N19).
- Với N19: `discount` chỉ thêm trên một phần document; truy vấn dùng
  `{'$ifNull': ['$discount', 0]}`. Tuyệt đối không `$set` bừa toàn bộ collection.

## Quy ước code Python

- Mọi câu trả lời là hàm nhận `db` (không tự kết nối lại), `n_answers.py` có `main()` chạy
  tuần tự và in nhãn `=== N01 ===` trước mỗi kết quả để dễ copy vào báo cáo.
- `find()` luôn `projection={'_id': 0}` trừ khi cần `_id`.
- `aggregate()` trả về list rồi in, tránh in generator rỗng.
- Tạo index một lần bằng `create_index('customer_id', name='idx_orders_customer')` — kiểm tra
  `list_collection_indexes()` trước khi tạo lại.
- Đóng client ở cuối (`client.close()`), dùng `try/finally` quanh các thao tác dài.

## Explain / index

- N21: `db.orders.find({'customer_id': 1}).explain()` — chụp `winningPlan.stage`
  (`COLLSCAN` vs `IXSCAN`) và `executionStats.totalDocsExamined` / `nReturned`.
- Nêu rõ: Atlas free + dữ liệu nhỏ nên thời gian chênh lệch không đáng kể; kết luận dựa trên
  plan, không dựa trên wall-clock.

## Báo cáo và minh chứng

- `evidence/`: `01_cluster.png`, `02_data_explorer.png` (mở 1 order thấy `items`),
  `03_crud.png`, `04_aggregation_n10.png`, `05_lookup_n12.png`, `06_explain_n21.png`
  (đã che thông tin nhạy cảm).
- Báo cáo `report/lab02_report.md` → PDF 2–3 trang: thiết lập Atlas → mô hình embedded →
  kết quả N01–N14 → homework N16–N22 → so sánh SQL vs MongoDB.

## Kiểm tra trước khi nộp

```bash
python3 -c "import ast,sys;[ast.parse(open(f).read()) for f in ['connect.py','seed.py','lab_queries.py','n_answers.py','generate_data.py']];print('syntax ok')"
grep -rniE "mongodb\+srv://|student_lab:" --exclude-dir=.git . || echo "no secret in repo"
```
