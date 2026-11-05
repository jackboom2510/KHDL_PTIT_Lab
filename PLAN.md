# PLAN — KHDL PTIT Lab 01 & Lab 02

Trạng thái: **LAB 01 đã xong M1–M3** (S01–S21 chạy được, tách file bắt buộc/bổ sung);
LAB 02 còn ở M4.
Nguồn yêu cầu: hai PDF ở thư mục gốc. Chi tiết trích đề: `docs/lab01_requirements.md`,
`docs/lab02_requirements.md`.

## 0. Mốc tiến độ

| Mốc | Nội dung | Trạng thái |
| --- | --- | --- |
| M0 | Cấu trúc repo, AGENTS.md, PLAN.md, tài liệu yêu cầu | ✅ xong |
| M1 | LAB 01 — dựng `sales.db`, console, CRUD, câu cơ bản (S01–S07) | ✅ |
| M2 | LAB 01 — truy vấn nâng cao S08–S13 | ✅ |
| M3 | LAB 01 — index/EXPLAIN S14–S15 + mở rộng dữ liệu S16–S21 | ✅ |
| M4 | LAB 02 — Atlas, seed, CRUD, filter (N01–N09) | ⬜ |
| M5 | LAB 02 — aggregation, `$lookup`, index, homework (N10–N22) | ⬜ |
| M6 | Báo cáo PDF ngắn + ảnh minh chứng + đóng ZIP nộp bài | ✅ (LAB 01: PDF 5 trang + 11 ảnh + ZIP đã kiểm chứng) |

## 1. LAB 01 — SQL / SQLite

Thư mục: `lab01_sql/`. Chi tiết quy ước: `lab01_sql/AGENTS.md`.

**Tách file:** phần bắt buộc (S01–S15) ở `sql/answers.sql` chạy trên `data/sales.db`; phần bổ
sung/về nhà (S16–S21) ở `sql/answers_homework.sql` chạy trên `data/sales_extended.db`; phần
chứng minh index ở `sql/explain.sql`. Chi tiết kết quả đã kiểm chứng: mục 5.

### 1.1 Chuẩn bị môi trường

- [ ] (cần Cloud Shell thật — chưa chụp) Chạy `whoami`, `pwd`, `python3 --version` trên Cloud Shell, chụp ảnh → `evidence/01_env.png`.
- [x] Tạo `sql_console.py` đúng như PDF mục 4 (thêm tham số đường dẫn CSDL), chạy được `SELECT 1;`.
- [x] `sql/schema.sql` chứa 4 bảng `customers`, `products`, `orders`, `order_items` + FK.
- [x] `sql/seed.sql` chứa đúng dữ liệu mẫu PDF (5 khách, 5 sản phẩm, 6 đơn, 8 dòng đơn).
- [x] `build_db.py` dựng lại `data/sales.db` từ 2 file trên; kiểm tra count 5/5/6/8.

### 1.2 Bài bắt buộc (đưa vào `answers.sql`)

| Mã | Yêu cầu | Ghi chú kỹ thuật | Trạng thái |
| --- | --- | --- | --- |
| S01 | Tên + thành phố khách hàng | `SELECT name, city` | ✅ |
| S02 | Sản phẩm giá > 1 triệu | `WHERE price > 1000000` | ✅ |
| S03 | Sắp xếp sản phẩm theo giá giảm dần | `ORDER BY price DESC` | ✅ |
| S04 | Thêm khách hàng mới | `INSERT` (dùng id 6, tên Lan/Hue) | ✅ |
| S05 | Tăng giá Mouse 10% | `UPDATE ... price = price*1.1` | ✅ |
| S06 | Xoá khách vừa thêm | `DELETE`, chỉ xoá id 6 (chưa có đơn) | ✅ |
| S07 | Mã đơn + tên khách (JOIN) | `orders JOIN customers` | ✅ |
| S08 | Tổng tiền từng đơn | mẫu trong PDF: 3 bảng JOIN + `SUM` | ✅ |
| S09 | Doanh thu từng khách hàng | thêm `GROUP BY customer_id` | ✅ |
| S10 | Khách chi tiêu > 5 triệu | `HAVING SUM(...) > 5000000` | ✅ |
| S11 | Sản phẩm giá cao hơn trung bình | subquery `> (SELECT AVG(price) ...)` | ✅ |
| S12 | Khách có từ 2 đơn | `GROUP BY ... HAVING COUNT(*) >= 2` | ✅ |
| S13 | Top 3 sản phẩm theo doanh thu | `ORDER BY revenue DESC LIMIT 3` | ✅ |
| S14 | Index `orders.customer_id` | `CREATE INDEX idx_orders_customer` | ✅ |
| S15 | EXPLAIN QUERY PLAN trước/sau index | ghi cả 2 output vào `explain.sql` + nhận xét SCAN/SEARCH | ✅ |

### 1.3 Bài về nhà

- [x] `generate_data.py`: ≥100 khách, ≥30 sản phẩm, ≥500 đơn, ≥1.000 dòng đơn, FK hợp lệ,
      dữ liệu giả lập nhưng tái lập được (`random.seed`).
- [x] S16 doanh thu theo tháng (`strftime('%Y-%m', order_date)`).
- [x] S17 khách chưa có đơn (`LEFT JOIN ... IS NULL` hoặc `NOT EXISTS`).
- [x] S18 sản phẩm chưa từng bán (`NOT IN` / `NOT EXISTS`).
- [x] S19 xếp hạng khách theo doanh thu bằng `RANK()`/`DENSE_RANK()` (window function).
- [x] S20 so sánh `EXPLAIN QUERY PLAN` sau khi mở rộng dữ liệu + đã tạo index.
- [x] S21 bảng so sánh SQL Server `#table` / `##table` / `tempdb` với SQLite `TEMP TABLE`.

### 1.3b Báo cáo

- [x] `report/make_report.py` — báo cáo **ngắn 4–5 trang, đen trắng**, bám 5 tiêu chí chấm
      (cài đặt/dữ liệu 2,0 · CRUD 2,0 · truy vấn nâng cao 3,0 · index 1,5 · mở rộng + báo cáo 1,5).
      Sinh PDF bằng fpdf2 (**không cần TeX**), tự đếm trang và tự thu nhỏ ảnh nếu vượt 5 trang.
- [x] Bản đã xuất: `report/BaoCao_LAB01_B23DCKH105.pdf` — **4 trang** không ảnh, **5 trang** khi
      chèn đủ 11 ảnh; tác giả **Nguyễn Danh Thái — B23DCKH105**.
- [x] `report/requirements.txt` (`fpdf2`, `pillow`), `report/pdf_pages.py` (đếm trang),
      `report/README.md` (cách xuất báo cáo, quy ước trình bày, vì sao giới hạn 5 trang).
- [x] `evidence/HUONG_DAN_CHUP_ANH.md` + `evidence/capture_commands.sh` — danh sách lệnh cần chạy
      để tự chụp ảnh minh chứng trên Google Cloud Shell.
- [x] **Đã chụp ảnh thật** trên Google Cloud Shell: 7 nhóm / 11 tệp (`01_env.png`,
      `02_tables_count.png`, `03_console.png`, `04_s08_result_01–02`, `05_explain_before_after_01–02`,
      `06_expanded_counts.png`, `07_s19_rank_01–03`); PDF 5 trang đã chèn đủ 11 ảnh.
- [ ] Điền tên lớp và giảng viên hướng dẫn (hằng số `CLASS_NAME`, `INSTRUCTOR` trong
      `make_report.py`), rồi xuất lại PDF.
- [x] `pack_submission.sh` đóng `submission/StudentID_SQL.zip`, đã giải nén và chạy lại độc lập.
- [x] **Đã bỏ** hướng báo cáo đồ án 37 trang (LaTeX + bìa/mục lục/phụ lục) và pipeline sinh ảnh
      giả bằng script — thay bằng báo cáo ngắn + ảnh chụp thật.

### 1.4 Nộp

`StudentID_SQL.zip` = `data/sales.db` (+ `sales_extended.db` nếu dung lượng cho phép),
`sql_console.py`, `sql/schema.sql`, `sql/seed.sql`, `sql/answers.sql` (S01–S15),
`sql/answers_homework.sql` (S16–S21), `sql/explain.sql`, `build_db.py`, `generate_data.py`,
`run_sql.py`, báo cáo PDF 4–5 trang, ảnh minh chứng (ảnh chụp thật).

## 2. LAB 02 — NoSQL / MongoDB Atlas

Thư mục: `lab02_nosql/`. Chi tiết quy ước: `lab02_nosql/AGENTS.md`.
Điều kiện tiên quyết: cluster Atlas M0 `DSCluster`, user `student_lab`, IP Cloud Shell đã
allowlist. **Không lưu URI/mật khẩu vào repo.**

### 2.1 Thiết lập

- [ ] Tạo cluster free, ghi lại provider/region vào báo cáo.
- [ ] `connect.py` dùng `getpass`, ping thành công, trả về db `sales_nosql`.
- [ ] `seed.py` seed `customers`/`products`/`orders` (embedded `items`), chặn chạy lại khi có dữ liệu.
- [ ] `lab_queries.py` chạy đúng các ví dụ trong PDF.
- [ ] Ảnh Data Explorer mở một order thấy mảng `items` → `evidence/02_data_explorer.png`.

### 2.2 Bài bắt buộc (`n_answers.py`)

| Mã | Yêu cầu | Ghi chú kỹ thuật | Trạng thái |
| --- | --- | --- | --- |
| N01 | Liệt kê tất cả customers | `find({}, {'_id':0})` | ⬜ |
| N02 | Khách ở Hanoi | filter `{'city':'Hanoi'}` | ⬜ |
| N03 | Sản phẩm giá > 1 triệu | `{'price':{'$gt':1000000}}` | ⬜ |
| N04 | Sắp xếp giá giảm dần | `.sort('price', -1)` | ⬜ |
| N05 | Thêm khách mới | `insert_one` | ⬜ |
| N06 | Sửa thành phố | `update_one` + `$set` | ⬜ |
| N07 | Xoá khách vừa thêm | `delete_one` | ⬜ |
| N08 | Đếm khách theo thành phố | `$group` + `$sum: 1` | ⬜ |
| N09 | Đơn chứa Laptop | `{'items.product_id':101}` | ⬜ |
| N10 | Tổng tiền từng đơn | `$unwind` + `$group` + `$multiply` | ⬜ |
| N11 | Doanh thu theo khách | `$group` theo `customer_id` | ⬜ |
| N12 | Ghép orders với customers | `$lookup` + `$unwind` + `$project` | ⬜ |
| N13 | Khách có ≥2 đơn | `$group` + `$match` count | ⬜ |
| N14 | Index `orders.customer_id` | `create_index('customer_id')` | ⬜ |
| N15 | Giải thích embedded vs reference | viết trong báo cáo, không chỉ code | ⬜ |

### 2.3 Bài bổ sung

- [ ] `generate_data.py`: ≥500 đơn, mỗi đơn 1–5 sản phẩm; nạp lên Atlas.
- [ ] N16 doanh thu theo thành phố.
- [ ] N17 top 3 sản phẩm theo doanh thu.
- [ ] N18 khách chưa đặt hàng qua `$lookup` + `$match` rỗng.
- [ ] N19 thêm `discount` không đồng nhất giữa các document, xử lý thiếu bằng `$ifNull`.
- [ ] N20 phân tích nhúng vs tham chiếu + hệ quả: đổi `products.price` không cập nhật
      `items.price` trong đơn cũ.
- [ ] N21 tạo index và đọc `explain()` (nêu rõ dữ liệu nhỏ nên chưa kết luận tốc độ).
- [ ] N22 đối chiếu `JOIN` (SQL) với `$lookup` (MongoDB).

### 2.4 Nộp

`StudentID_NoSQL.zip` = `connect.py`, `seed.py`, `lab_queries.py`, file giải N01–N22,
báo cáo PDF 2–3 trang + ảnh Data Explorer và ảnh terminal.

## 3. Rủi ro & lưu ý

| Rủi ro | Cách xử lý |
| --- | --- |
| IP Cloud Shell đổi giữa phiên → timeout | chạy `curl -4 https://api.ipify.org`, cập nhật Network Access; không mở `0.0.0.0/0` lâu dài |
| Mật khẩu chứa `@ % /` | URL-encode hoặc dùng mật khẩu chữ + số |
| Dữ liệu nhỏ nên index không nhanh hơn | nêu rõ trong báo cáo, so sánh bằng EXPLAIN chứ không chỉ thời gian |
| `RANK()` có thể không có trên SQLite cũ | kiểm tra `sqlite3.sqlite_version >= 3.25` |
| Mất dữ liệu Cloud Shell sau thời gian dài | kéo `sales.db` + code về local, commit phần code |
| Lộ URI khi chụp màn hình | che mật khẩu trước khi đưa ảnh vào `evidence/` |

## 4. Thứ tự thực hiện đề xuất

1. M1 → M2 → M3 (SQL chạy local bằng `python3`, không cần mạng).
2. M4 → M5 (MongoDB cần Atlas; làm sau để không bị chặn IP).
3. M6 gộp báo cáo cho cả hai lab, xuất PDF, đóng ZIP vào `submission/`.

## 5. Nhật ký kiểm chứng LAB 01 (đã chạy)

| Lệnh | Kết quả |
| --- | --- |
| `python3 build_db.py --force` | 5 / 5 / 6 / 8 — khớp đề |
| `python3 run_sql.py sql/answers.sql` (2 lần) | 18 câu, 0 lỗi; lần 2 không cộng dồn giá Mouse (vẫn 275.000) |
| `python3 generate_data.py --force` | 100 khách / 30 SP / 500 đơn / 1.500 dòng đơn, `foreign_key_check` ok |
| `python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db` | 13 tháng doanh thu; 8 khách chưa mua; 4 SP chưa bán; RANK/DENSE_RANK khớp; TEMP TABLE chạy được |
| `python3 run_sql.py sql/explain.sql` | trước: `SCAN orders` → sau: `SEARCH orders USING COVERING INDEX idx_orders_customer` |
| `python3 sql_console.py` (qua pipe) | nhận câu lệnh nhiều dòng, in cột + rows, EXIT thoát |

## 6. Nhật ký kiểm chứng bước nộp bài (M6)

| Hạng mục | Kết quả |
| --- | --- |
| `report/make_report.py` | PDF **4 trang** (không ảnh) và **5 trang** khi chèn 11 ảnh; 6 bảng, đen trắng |
| Bố cục PDF | 8 mục theo 5 tiêu chí chấm: thông tin chung · cài đặt/dữ liệu · CRUD · truy vấn nâng cao · index/EXPLAIN · mở rộng + báo cáo · danh mục ảnh · kết luận |
| Ảnh minh chứng | Chụp thật trên Cloud Shell theo `evidence/HUONG_DAN_CHUP_ANH.md` (7 nhóm / 11 tệp); **không** sinh bằng script nữa |
| Kiểm tra trang | Tự đếm bằng `pdf_pages.py` + fallback pypdfium2, thu nhỏ ảnh 1,0 → 0,6, thoát mã 1 nếu vẫn > 5 trang |
| `pack_submission.sh 22CNTT0123` | 21 tệp, 0,9 MB; giải nén chạy lại: `answers.sql` 18 câu 0 lỗi, homework 9 câu 0 lỗi, `sql_console.py` OK |
