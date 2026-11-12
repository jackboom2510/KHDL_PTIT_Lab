#!/usr/bin/env bash
# Đóng gói bài nộp LAB 02 -> submission/StudentID_NoSQL.zip
#
#   bash lab02_nosql/pack_submission.sh                 # MSSV = StudentID
#   bash lab02_nosql/pack_submission.sh B23DCKH105      # đặt tên theo MSSV
#
# Cấu trúc ZIP bám đúng mục 11 của đề:
#   connect.py, seed.py, lab_queries.py, mã giải N01–N22 (n_answers.py + n_homework.py),
#   generate_data.py, báo cáo PDF 4–5 trang, ảnh minh chứng.
#
# Không bao giờ đóng gói URI/mật khẩu: script quét toàn bộ tệp trước khi nén và dừng nếu
# thấy chuỗi giống credential.

set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  for cand in python3 python py; do
    if command -v "$cand" >/dev/null 2>&1; then PYTHON="$cand"; break; fi
  done
fi
if [[ -z "$PYTHON" ]]; then
  echo "[!] Không tìm thấy Python. Cài Python 3 rồi chạy lại." >&2
  exit 2
fi

MSSV="${1:-StudentID}"
OUT_DIR="../submission"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

ROOT="$STAGE/${MSSV}_NoSQL"
mkdir -p "$ROOT"/{report,evidence}

# --- chặn secret trước khi đóng gói ---
echo "[i] kiểm tra không có URI/mật khẩu trong tệp nộp ..."
# chỉ quét tệp sẽ nộp; bỏ qua placeholder dạng <db_password> và chính dòng lệnh grep trong tài liệu
if grep -rniE "mongodb\+srv://[^<[:space:]\"]+:[^<@[:space:]\"]+@|student_lab:[^ <]" \
      connect.py seed.py lab_queries.py n_answers.py n_homework.py generate_data.py \
      check_offline.py data/*.json 2>/dev/null | grep -v "<db_password>" >/dev/null 2>&1; then
  echo "[!] Phát hiện chuỗi giống URI có mật khẩu — dừng đóng gói." >&2
  echo "    Kiểm tra: grep -rniE 'mongodb\\+srv://' --exclude-dir=.git ." >&2
  exit 3
fi

cp connect.py seed.py lab_queries.py n_answers.py n_homework.py generate_data.py \
   check_offline.py utf8_console.py "$ROOT/"

# --- báo cáo PDF 4–5 trang ---
PDF="$(ls report/BaoCao_LAB02_*.pdf 2>/dev/null | head -n1 || true)"
if [[ -z "$PDF" ]]; then
  echo "[i] chưa có PDF, đang xuất bằng report/make_report.py ..."
  "$PYTHON" report/make_report.py >/dev/null || true
  PDF="$(ls report/BaoCao_LAB02_*.pdf 2>/dev/null | head -n1 || true)"
fi
if [[ -n "$PDF" ]]; then
  cp "$PDF" "$ROOT/report/${MSSV}_NoSQL_report.pdf"
else
  echo "[!] Không xuất được báo cáo PDF (xem report/README.md)." >&2
fi

# --- ảnh minh chứng (ảnh chụp thật) ---
if [[ -z "$(ls -A evidence/*.png 2>/dev/null)" ]]; then
  echo "[!] Chưa có ảnh minh chứng — xem evidence/HUONG_DAN_CHUP_ANH.md," >&2
  echo "    chụp 7 ảnh 01_cluster.png … 07_expanded_counts.png rồi chạy lại." >&2
fi
cp evidence/*.png "$ROOT/evidence/" 2>/dev/null || true

# --- ánh xạ yêu cầu đề bài -> tệp ---
cat > "$ROOT/README_MAPPING.txt" <<EOF
LAB 02 — MongoDB Atlas Free + PyMongo trên Google Cloud Shell
Sinh viên: Nguyễn Danh Thái — MSSV: ${MSSV}
Môn: Introduction to Data Science — Học viện Công nghệ Bưu chính Viễn thông
Ngày đóng gói: $(date +%F)

ÁNH XẠ YÊU CẦU -> FILE
  connect.py ............... getpass nhận URI, MongoClient timeout 12s, ping, DB sales_nosql
  seed.py .................. nạp customers/products/orders (items nhúng), dừng nếu đã có dữ liệu
  lab_queries.py ........... các ví dụ CRUD/truy vấn đúng mục 7 của đề
  n_answers.py ............. N01–N15 (phần BẮT BUỘC), hàm n01() … n15()
  n_homework.py ............ N16–N22 (phần BỔ SUNG), hàm n16() … n22()
  generate_data.py ......... sinh 100 khách / 30 SP / 500 đơn / 1.521 dòng items (seed 2026)
  check_offline.py ......... chạy thử N01–N22 bằng mongomock, không cần Atlas
  utf8_console.py .......... ép stdout UTF-8 để in tiếng Việt trên Windows (cp1252)
  report/*_report.pdf ...... báo cáo 4–5 trang theo 5 tiêu chí chấm, có ảnh minh chứng
  evidence/*.png ........... 7 ảnh chụp Atlas + Cloud Shell (xem mục 7 báo cáo)

CHẠY LẠI
  pip install "pymongo[srv]"
  python3 connect.py
  python3 seed.py
  python3 lab_queries.py
  python3 n_answers.py --json data/lab02_results_n01_n15.json
  python3 generate_data.py --force
  python3 n_homework.py --json data/lab02_results_n16_n22.json

GHI CHÚ
  Không có URI/mật khẩu Atlas trong bài nộp; URI được nhập bằng getpass khi chạy.
EOF

mkdir -p "$OUT_DIR"
ZIP="$OUT_DIR/${MSSV}_NoSQL.zip"
rm -f "$ZIP"
ABS_ZIP="$(cd "$(dirname "$OUT_DIR")" && pwd)/${OUT_DIR##*/}/${MSSV}_NoSQL.zip"
ZIP_BIN="${ZIP_BIN-$(command -v zip || true)}"   # ZIP_BIN="" để buộc dùng Python zipfile
if [[ -n "$ZIP_BIN" ]]; then
  ( cd "$STAGE" && "$ZIP_BIN" -qr "$ABS_ZIP" "${MSSV}_NoSQL" )
else
  echo "[i] không có lệnh zip — dùng Python zipfile"
  "$PYTHON" - "$STAGE" "${MSSV}_NoSQL" "$ABS_ZIP" <<'PYZIP'
import sys, zipfile
from pathlib import Path

stage, folder, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for path in sorted((stage / folder).rglob("*")):
        if path.is_file():
            z.write(path, path.relative_to(stage).as_posix())
PYZIP
fi

echo
echo "[ok] $ZIP"
"$PYTHON" - "$ZIP" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
total = sum(i.file_size for i in z.infolist())
print(f"     {len(z.infolist())} tệp, {total/1024/1024:.1f} MB (nén {len(open(sys.argv[1],'rb').read())/1024/1024:.1f} MB)")
for i in z.infolist():
    if not i.is_dir():
        print(f"     - {i.filename}")
PY
