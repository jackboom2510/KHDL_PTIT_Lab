#!/usr/bin/env bash
# Đóng gói bài nộp LAB 01 -> submission/StudentID_SQL.zip
#
#   bash lab01_sql/pack_submission.sh                 # MSSV = StudentID
#   bash lab01_sql/pack_submission.sh 22CNTT0123      # đặt tên theo MSSV
#
# Cấu trúc ZIP bám đúng mục 10 của đề:
#   sales.db, sql_console.py, answers.sql (-- S01…S21), chương trình tạo dữ liệu mở rộng,
#   báo cáo PDF 4–5 trang, ảnh minh chứng chụp trên Cloud Shell.
#
# Ghi chú: `answers.sql` trong đề được hiểu là toàn bộ phần trả lời S01–S21; bài làm tách
# thành answers.sql (bắt buộc S01–S15) + answers_homework.sql (bổ sung S16–S21) nên ZIP
# chứa cả hai, kèm README_MAPPING.txt giải thích ánh xạ.

set -euo pipefail
cd "$(dirname "$0")"

MSSV="${1:-StudentID}"
OUT_DIR="../submission"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

ROOT="$STAGE/${MSSV}_SQL"
mkdir -p "$ROOT"/{data,sql,report,evidence}

# --- dữ liệu: dựng lại từ nguồn để ZIP không chứa dữ liệu cũ ---
echo "[i] dựng lại CSDL ..."
python3 build_db.py --force >/dev/null
python3 generate_data.py --force >/dev/null

cp data/sales.db                  "$ROOT/data/sales.db"
cp data/sales_extended.db         "$ROOT/data/sales_extended.db"
cp sql_console.py build_db.py generate_data.py run_sql.py "$ROOT/"
cp sql/schema.sql sql/seed.sql sql/answers.sql sql/answers_homework.sql sql/explain.sql "$ROOT/sql/"

# --- báo cáo PDF 4–5 trang ---
PDF="$(ls report/BaoCao_LAB01_*.pdf 2>/dev/null | head -n1 || true)"
if [[ -z "$PDF" ]]; then
  echo "[i] chưa có PDF, đang xuất bằng report/make_report.py ..."
  python3 report/make_report.py --images evidence >/dev/null || true
  PDF="$(ls report/BaoCao_LAB01_*.pdf 2>/dev/null | head -n1 || true)"
fi
if [[ -n "$PDF" ]]; then
  cp "$PDF" "$ROOT/report/${MSSV}_SQL_report.pdf"
else
  echo "[!] Không xuất được báo cáo PDF (xem report/README.md)." >&2
fi

# --- ảnh minh chứng (ảnh chụp thật trên Google Cloud Shell) ---
if [[ -z "$(ls -A evidence/*.png 2>/dev/null)" ]]; then
  echo "[!] Chưa có ảnh minh chứng — xem evidence/HUONG_DAN_CHUP_ANH.md," >&2
  echo "    chụp 7 ảnh 01_env.png … 07_s19_rank.png rồi chạy lại." >&2
fi
cp evidence/*.png "$ROOT/evidence/" 2>/dev/null || true

# --- bản đồ ánh xạ yêu cầu đề bài -> file ---
cat > "$ROOT/README_MAPPING.txt" <<EOF
LAB 01 — SQL trên Google Cloud Shell với SQLite
Sinh viên: ${MSSV}
Ngày đóng gói: $(date +%F)

ÁNH XẠ YÊU CẦU -> FILE
  data/sales.db ............ CSDL đã nạp dữ liệu mẫu (5 khách · 5 SP · 6 đơn · 8 dòng)
  sql_console.py ........... console SQLite (đúng mẫu trong đề, thêm tham số đường dẫn CSDL)
  sql/answers.sql .......... S01–S15 (phần BẮT BUỘC), chú thích -- S01 … -- S15
  sql/answers_homework.sql . S16–S21 (phần BỔ SUNG/về nhà), chú thích -- S16 … -- S21
  sql/explain.sql .......... EXPLAIN QUERY PLAN trước/sau index (S15) và sau mở rộng (S20)
  build_db.py .............. dựng sales.db từ sql/schema.sql + sql/seed.sql
  generate_data.py ......... sinh dữ liệu mở rộng 100/30/500/1500 (random.seed = 2026)
  run_sql.py ............... chạy file .sql bằng Python khi máy không có sqlite3 CLI
  data/sales_extended.db ... dữ liệu mở rộng (dùng cho S16–S21)
  report/*_report.pdf ...... báo cáo 4–5 trang theo 5 tiêu chí chấm, có ảnh minh chứng
  evidence/*.png ........... 7 ảnh chụp thật trên Google Cloud Shell (xem mục 7 báo cáo)

CHẠY LẠI
  python3 build_db.py --force
  python3 run_sql.py sql/answers.sql
  python3 generate_data.py --force
  python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db
  python3 run_sql.py sql/explain.sql
EOF

mkdir -p "$OUT_DIR"
ZIP="$OUT_DIR/${MSSV}_SQL.zip"
rm -f "$ZIP"
( cd "$STAGE" && zip -qr "$(cd - >/dev/null && pwd)/$ZIP" "${MSSV}_SQL" )

echo
echo "[ok] $ZIP"
python3 - "$ZIP" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
total = sum(i.file_size for i in z.infolist())
print(f"     {len(z.infolist())} tệp, {total/1024/1024:.1f} MB (nén {len(open(sys.argv[1],'rb').read())/1024/1024:.1f} MB)")
for i in z.infolist():
    if not i.is_dir():
        print(f"     - {i.filename}")
PY
