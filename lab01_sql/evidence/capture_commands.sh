#!/usr/bin/env bash
# In ra (hoặc chạy) lần lượt các lệnh cần thực hiện trên Google Cloud Shell để chụp 7 ảnh
# minh chứng. Mặc định chỉ IN hướng dẫn; thêm --run để chạy thật và dừng giữa các bước cho
# bạn chụp màn hình.
#
#   bash capture_commands.sh              # in danh sách lệnh theo từng ảnh
#   bash capture_commands.sh --run        # chạy và dừng sau mỗi bước (Enter để tiếp)
#   bash capture_commands.sh --only 05    # chỉ bước có số 05
#
# Chạy từ thư mục lab01_sql (hoặc script tự cd về đúng chỗ).

set -uo pipefail
cd "$(dirname "$0")/.."

MODE="print"
ONLY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) MODE="run" ;;
    --only) ONLY="$2"; shift ;;
    *) echo "[!] Tham số không hợp lệ: $1" >&2; exit 2 ;;
  esac
  shift
done

COUNT_SQL='SELECT '"'"'customers'"'"' AS bang, COUNT(*) FROM customers
UNION ALL SELECT '"'"'products'"'"', COUNT(*) FROM products
UNION ALL SELECT '"'"'orders'"'"', COUNT(*) FROM orders
UNION ALL SELECT '"'"'order_items'"'"', COUNT(*) FROM order_items;'

# Mỗi bước: số | tên tệp ảnh | mô tả | các lệnh (phân tách bằng \n)
step() {
  local num="$1" file="$2" desc="$3"
  shift 3
  if [[ -n "$ONLY" && "$num" != "$ONLY" ]]; then return; fi
  echo
  echo "=============================================================="
  echo " ẢNH $num — $file"
  echo " $desc"
  echo "=============================================================="
  for cmd in "$@"; do
    echo "$cmd"
    if [[ "$MODE" == "run" ]]; then
      echo "--------------------------------------------------------------"
      bash -c "$cmd"
      echo "--------------------------------------------------------------"
      read -r -p "[chụp màn hình phần trên rồi nhấn Enter để tiếp] " _
    fi
  done
}

step 01 01_env.png "Môi trường thực hành: tài khoản, thư mục, phiên bản Python/SQLite" \
  'whoami; pwd; python3 --version' \
  'python3 -c "import sqlite3; print(\"SQLite\", sqlite3.sqlite_version)"' \
  'sqlite3 --version 2>/dev/null || echo "(không có sqlite3 CLI — bỏ qua dòng này)"'

step 02 02_tables_count.png "Tạo 4 bảng, số dòng 5/5/6/8, kiểm tra khoá ngoại" \
  'python3 build_db.py --force' \
  "python3 run_sql.py --sql \"$COUNT_SQL\"" \
  'python3 run_sql.py --sql "PRAGMA foreign_key_check;"'

step 03 03_console.png "sql_console.py: câu nhiều dòng, một câu sai, EXIT (tự gõ trong console)" \
  'python3 sql_console.py'

step 04 04_s08_result.png "Kết quả S08 (tổng tiền từng đơn) và S09 (doanh thu từng khách)" \
  'python3 run_sql.py sql/answers.sql'

step 05 05_explain_before_after.png "EXPLAIN QUERY PLAN trước index (SCAN) và sau index (SEARCH)" \
  'python3 run_sql.py sql/explain.sql'

step 06 06_expanded_counts.png "Dữ liệu mở rộng 100/30/500/1500 và kiểm tra khoá ngoại" \
  'python3 generate_data.py --force' \
  "python3 run_sql.py --sql \"$COUNT_SQL\" --db data/sales_extended.db"

step 07 07_s19_rank.png "S19: xếp hạng khách hàng với RANK và DENSE_RANK" \
  'python3 run_sql.py sql/answers_homework.sql --db data/sales_extended.db'

echo
echo "Xong. Lưu ảnh vào lab01_sql/evidence/ đúng tên tệp ở trên,"
echo "rồi xuất báo cáo:  python3 lab01_sql/report/make_report.py --images lab01_sql/evidence"
