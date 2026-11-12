# Báo cáo LAB 02 — bản ngắn 4–5 trang, đen trắng

Sinh **trực tiếp bằng Python (fpdf2)**, không cần LaTeX. Nội dung bám 5 tiêu chí chấm ở mục 11
của đề, không trình bày kiểu đồ án (không bìa riêng, không mục lục, không chương, không phụ lục).

| Tệp | Vai trò |
| --- | --- |
| `make_report.py` | Sinh báo cáo PDF, đọc số liệu JSON và chèn ảnh minh chứng |
| `requirements.txt` | `fpdf2`, `pillow` (tuỳ chọn `pypdfium2` để đếm trang) |
| `pdf_pages.py` | Đếm số trang PDF (dùng nội bộ) |
| `BaoCao_LAB02_B23DCKH105.pdf` | Bản đã xuất, **4 trang** khi chưa chèn ảnh |

## Xuất báo cáo

```bash
cd lab02_nosql/report
pip install -r requirements.txt

# bản chữ, dùng bộ số liệu đã kiểm chứng sẵn trong script
python3 make_report.py

# bản nộp: số liệu từ lần chạy thật + 7 ảnh chụp thật
python3 make_report.py --images ../evidence \
    --results ../data/lab02_results_n01_n15.json \
              ../data/lab02_results_n16_n22.json
```

`--results` nhận nhiều tệp JSON do `n_answers.py --json` và `n_homework.py --json` xuất ra; tệp
nào có khoá nào thì thay số liệu mặc định của khoá đó. `--images` trỏ tới thư mục ảnh (đường dẫn
tìm được từ cwd, `report/`, `lab02_nosql/` hoặc gốc repo); thiếu ảnh nào thì cảnh báo nhưng vẫn
xuất PDF.

## Bố cục

1. Thông tin chung — dịch vụ, dữ liệu, tách phần bắt buộc/bổ sung.
2. Tiêu chí 1 — thiết lập và seed (2,0 điểm): `connect.py`, bảng số document 5/5/6.
3. Tiêu chí 2 — CRUD và truy vấn lọc (2,0 điểm): bảng N01–N08.
4. Tiêu chí 3 — aggregation và `$lookup` (3,0 điểm): N10–N13, bảng tổng tiền từng đơn.
5. Tiêu chí 4 — index và mô hình dữ liệu (1,5 điểm): N14, N15, N20, N21 (IXSCAN vs COLLSCAN).
6. Tiêu chí 5 — bài mở rộng và báo cáo (1,5 điểm): quy mô 100/30/500/1.521, N16–N19, N22.
7. Danh mục ảnh minh chứng — tên tệp, nội dung cần thấy, mục tương ứng.
8. Kết luận — ngắn, hai điểm rút ra.

Toàn bộ chữ màu đen trên nền trắng; xám chỉ cho chú thích ảnh. Không nền tô, không icon, gạch
đầu dòng là `-`, bảng chỉ kẻ đường ngang. Script tự đếm trang và thu nhỏ ảnh dần (1,0 → 0,6) nếu
vượt 5 trang; vẫn vượt thì thoát mã lỗi 1.

## Số liệu

`DEFAULTS` trong `make_report.py` là bộ số liệu đã đo bằng cách chạy chính các pipeline của
`n_answers.py` / `n_homework.py` trên dữ liệu `seed=2026` (qua `check_offline.py`). Bản nộp nên
xuất lại với `--results` từ Atlas thật để số liệu khớp lần chạy của bạn.
