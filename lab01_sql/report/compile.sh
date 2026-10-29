#!/usr/bin/env bash
# Biên dịch báo cáo LAB 01 sang PDF.
#
#   bash compile.sh            # bản đầy đủ (có phụ lục)
#   bash compile.sh short      # bản gọn: tắt phụ lục (sửa \withappendixtrue -> false)
#
# Cần TeX Live (hoặc TinyTeX) có các gói: vntex/babel-vietnamese, booktabs, listings,
# tikz, longtable, tabularx, multirow, enumitem, caption, fancyhdr, hyperref.
# Trên Overleaf: upload cả thư mục report/, chọn compiler pdfLaTeX, Recompile.

set -euo pipefail
cd "$(dirname "$0")"

TEX=lab01_report.tex
MODE="${1:-full}"

if [[ "$MODE" == "short" ]]; then
  sed -i.bak 's/^\\withappendixtrue/\\withappendixfalse/' "$TEX"
  echo "[i] đã tắt phụ lục trong $TEX (bản gọn ~3 trang)"
fi

if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error "$TEX"
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error "$TEX"
  pdflatex -interaction=nonstopmode -halt-on-error "$TEX"   # lần 2: mục lục + \ref
else
  echo "[!] Không tìm thấy pdflatex/latexmk." >&2
  echo "    Cài TeX Live:  sudo apt-get install texlive-latex-extra texlive-lang-other latexmk" >&2
  echo "    Hoặc dùng Overleaf: upload thư mục report/ và chọn pdfLaTeX." >&2
  exit 1
fi

if [[ "$MODE" == "short" ]]; then
  mv "$TEX.bak" "$TEX"
fi

echo
echo "[ok] Xong. Kiểm tra:"
ls -lh ./*.pdf 2>/dev/null || echo "    (không thấy PDF — xem log phía trên)"
echo
echo "Lưu ý: các cảnh báo dạng 'Token not allowed in a PDF string' của hyperref khi gặp"
echo "tiếng Việt trong bookmark là vô hại, không ảnh hưởng nội dung PDF."
