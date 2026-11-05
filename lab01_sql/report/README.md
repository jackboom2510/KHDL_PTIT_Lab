# Báo cáo LAB 01 — bản ngắn 4–5 trang, đen trắng

Báo cáo được sinh **trực tiếp bằng Python (fpdf2)**, không cần LaTeX. Nội dung bám đúng
5 tiêu chí chấm ở mục 10 của đề, không trình bày theo kiểu đồ án (không bìa riêng, không mục
lục, không chương, không phụ lục).

| Tệp | Vai trò |
| --- | --- |
| `make_report.py` | Sinh báo cáo PDF. Tự kiểm tra số trang và trả mã lỗi nếu > 5 trang |
| `requirements.txt` | `fpdf2`, `pillow` (và tuỳ chọn `pypdfium2` để đếm trang) |
| `pdf_pages.py` | Đếm số trang PDF (dùng nội bộ trong `make_report.py`) |
| `BaoCao_LAB01_B23DCKH105.pdf` | Bản đã xuất, **4 trang** khi chưa chèn ảnh, **5 trang** khi chèn đủ 11 ảnh |

## Xuất báo cáo

```bash
cd lab01_sql/report
pip install -r requirements.txt

python3 make_report.py                 # bản chữ, 4 trang
python3 make_report.py --images evidence   # chèn ảnh chụp thật (11 tệp), 5 trang
python3 make_report.py --images evidence --out /tmp/bao-cao.pdf
```

`--images` trỏ tới thư mục chứa ảnh (đường dẫn được tìm lần lượt từ thư mục hiện tại, từ
`report/`, từ `lab01_sql/` và từ gốc repo). Danh sách 11 tệp nằm ở hằng số `FIGURES`; thiếu ảnh
nào thì in cảnh báo nhưng vẫn xuất PDF, và mục 7 luôn liệt kê danh mục ảnh cần nộp.

## Bố cục và quy ước trình bày

1. Thông tin chung — môi trường, dữ liệu, cách tách phần bắt buộc/bổ sung.
2. Tiêu chí 1 — cài đặt và tạo dữ liệu (2,0 điểm): schema, bảng đối chiếu số dòng.
3. Tiêu chí 2 — CRUD và câu cơ bản (2,0 điểm): bảng S01–S07 và các lưu ý an toàn khi chạy lặp.
4. Tiêu chí 3 — truy vấn nâng cao (3,0 điểm): S08–S13 kèm bảng kết quả đối chiếu.
5. Tiêu chí 4 — index và giải thích (1,5 điểm): EXPLAIN trước/sau, giải thích SCAN → SEARCH.
6. Tiêu chí 5 — bài mở rộng và báo cáo (1,5 điểm): quy mô dữ liệu, S16–S21.
7. Danh mục ảnh minh chứng — tên tệp, nội dung cần thấy, mục tương ứng.
8. Kết luận — ngắn, hai điểm rút ra.

Toàn bộ chữ màu đen trên nền trắng; xám chỉ dùng cho chú thích ảnh. Không có nền tô, không
icon, không bullet ký tự đặc biệt (gạch đầu dòng là dấu `-`). Bảng chỉ kẻ đường ngang.

## Vì sao giới hạn 5 trang

Ảnh chụp Cloud Shell rất "tốn" chiều cao trang, nên `make_report.py`:

- đặt hai ảnh cạnh nhau khi hai ảnh cùng một tiêu chí (`figure_pair`), ảnh lẻ thu nhỏ tối đa
  42–46 mm chiều cao; ảnh rộng như `01_env.png` được để full chiều ngang cho dễ đọc;
- nếu vẫn vượt 5 trang thì tự giảm tỉ lệ ảnh 1,0 → 0,9 → 0,8 → 0,7 → 0,6 và xuất lại;
- thoát với mã lỗi 1 và in cảnh báo nếu sau tất cả các lần thử vẫn > 5 trang.

Nếu báo cáo bị đẩy quá dài, nên cắt bớt gạch đầu dòng ở mục 4–6 thay vì thu nhỏ ảnh hơn nữa
(ảnh quá nhỏ sẽ không đọc được khi in).

## Ảnh minh chứng

Ảnh phải là ảnh chụp **thật** trên `shell.cloud.google.com`. Danh sách lệnh cần chạy và nội
dung cần thấy của từng ảnh nằm ở [`../evidence/HUONG_DAN_CHUP_ANH.md`](../evidence/HUONG_DAN_CHUP_ANH.md);
`bash ../evidence/capture_commands.sh` in lại lần lượt các lệnh đó.
