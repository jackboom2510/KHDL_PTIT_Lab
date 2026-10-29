#!/usr/bin/env bash
# Biên dịch báo cáo LAB 01 và tự kiểm tra số trang.
#
#   bash compile.sh 2p        # (MẶC ĐỊNH) báo cáo GỌN 2–3 trang — bản nộp chính
#   bash compile.sh full      # báo cáo đầy đủ + phụ lục (không giới hạn trang)
#   bash compile.sh short     # báo cáo đầy đủ nhưng TẮT phụ lục
#   bash compile.sh check     # chỉ kiểm tra cú pháp LaTeX, không compile
#
# Yêu cầu: pdflatex hoặc latexmk (TeX Live có vntex/babel-vietnamese, hoặc TinyTeX).
# Nếu không có TeX, dùng Overleaf: upload thư mục report/, chọn compiler pdfLaTeX.
# Kiểm tra số trang riêng:  python3 pdf_pages.py <file>.pdf [--max 3]

set -euo pipefail
cd "$(dirname "$0")"

MODE="${1:-2p}"

# --- chỉ kiểm tra cú pháp ---
if [[ "$MODE" == "check" ]]; then
  exec python3 check_tex.py lab01_report_short.tex lab01_report.tex
fi

# --- chọn file và giới hạn trang ---
case "$MODE" in
  2p)    TEX=lab01_report_short.tex;  LIMIT="--max 3" ;;
  full)  TEX=lab01_report.tex;        LIMIT="--no-limit" ;;
  short) TEX=lab01_report.tex;        LIMIT="--no-limit" ;;
  *)     echo "[!] Chế độ không hợp lệ: $MODE (dùng: 2p | full | short | check)" >&2
         exit 2 ;;
esac

# --- kiểm tra cú pháp trước khi compile ---
python3 check_tex.py "$TEX" || {
  echo "[!] Còn lỗi cú pháp — dừng trước khi compile." >&2
  exit 1
}

# --- chế độ short: tắt phụ lục tạm thời rồi khôi phục ---
RESTORE=0
if [[ "$MODE" == "short" ]]; then
  sed -i.bak 's/^\\withappendixtrue/\\withappendixfalse/' "$TEX"
  RESTORE=1
  echo "[i] đã tắt phụ lục trong $TEX (bản không phụ lục)"
fi

cleanup() {
  if [[ "$RESTORE" == "1" && -f "$TEX.bak" ]]; then
    mv "$TEX.bak" "$TEX"
    echo "[i] đã khôi phục $TEX như ban đầu"
  fi
}
trap cleanup EXIT

# --- compile ---
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error "$TEX"
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error "$TEX"
  pdflatex -interaction=nonstopmode -halt-on-error "$TEX"   # lần 2: mục lục + \ref
else
  cat >&2 <<'MSG'
[!] Không tìm thấy pdflatex/latexmk.
    Cài TeX Live:  sudo apt-get install texlive-latex-extra texlive-lang-other latexmk
    Hoặc Overleaf: upload thư mục report/, chọn compiler pdfLaTeX, Recompile.
MSG
  exit 1
fi

PDF="${TEX%.tex}.pdf"
echo
if [[ -f "$PDF" ]]; then
  ls -lh "$PDF"
  # shellcheck disable=SC2086
  python3 pdf_pages.py "$PDF" $LIMIT || true
else
  echo "[!] Không thấy $PDF — xem log phía trên" >&2
  exit 1
fi

[[ "$MODE" == "2p" ]] && cat <<'MSG'

[i] Bản 2p dùng bố cục 2 cột / 10pt. Nếu ra 4 trang, xem mục "Co giãn độ dài"
    trong report/README.md (bỏ mục "Lệnh tái lập", giảm bảng xuống \scriptsize,
    hoặc chuyển sang extarticle 9pt).
MSG

cat <<'MSG'

Lưu ý: cảnh báo "Token not allowed in a PDF string" của hyperref khi gặp tiếng
Việt trong bookmark là vô hại, không ảnh hưởng nội dung PDF.
MSG
