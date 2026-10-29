#!/usr/bin/env python3
"""Kiểm tra cú pháp LaTeX cơ bản khi máy không có TeX để compile.

    python3 check_tex.py lab01_report_short.tex
    python3 check_tex.py lab01_report.tex lab01_report_short.tex

Bắt các lỗi hay gặp khi viết báo cáo tiếng Việt bằng pdfLaTeX:
1. \\begin/\\end môi trường không cân bằng hoặc đóng sai thứ tự;
2. ngoặc nhọn không cân bằng (bỏ qua comment, escape, verbatim);
3. ký tự đặc biệt chưa escape ( _ # % $ & ) trong \\code{...} và trong văn bản;
4. \\ref không có \\label tương ứng;
5. \\if...\\fi không cân bằng;
6. số ô trong tabular/tabularx không khớp khai báo cột (lỗi "Extra alignment tab").

Đây là kiểm tra tĩnh, KHÔNG thay thế việc compile thật.
"""

from __future__ import annotations

import re
import sys
from collections import Counter

VERBATIM_ENVS = ("lstlisting", "verbatim", "Verbatim", "minted")


def strip_verbatim(src: str) -> str:
    """Thay nội dung các môi trường verbatim bằng khoảng trắng (giữ số dòng)."""
    out = src
    for env in VERBATIM_ENVS:
        out = re.sub(
            rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}",
            lambda m: re.sub(r"[^\n]", " ", m.group(0)),
            out,
            flags=re.S,
        )
    return out


def line_of(src: str, pos: int) -> int:
    return src.count("\n", 0, pos) + 1


def check_environments(src: str) -> list[str]:
    problems, stack = [], []
    for m in re.finditer(r"\\(begin|end)\{([^}]+)\}", src):
        kind, name = m.group(1), m.group(2)
        line = line_of(src, m.start())
        if kind == "begin":
            stack.append((name, line))
        else:
            if not stack:
                problems.append(f"dòng {line}: \\end{{{name}}} không có \\begin tương ứng")
            elif stack[-1][0] != name:
                top, top_line = stack[-1]
                problems.append(
                    f"dòng {line}: \\end{{{name}}} nhưng đang mở {top} (từ dòng {top_line})"
                )
            else:
                stack.pop()
    problems += [f"\\begin{{{n}}} (dòng {l}) không có \\end" for n, l in stack]
    return problems


def check_braces(src: str) -> list[str]:
    problems, depth, i, line = [], 0, 0, 1
    while i < len(src):
        c = src[i]
        if c == "\n":
            line += 1
        elif c == "\\":
            i += 2
            continue
        elif c == "%":
            nl = src.find("\n", i)
            i = len(src) if nl == -1 else nl
            continue
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                problems.append(f"dòng {line}: thừa dấu }}")
                depth = 0
        i += 1
    if depth:
        problems.append(f"thiếu {depth} dấu }}")
    return problems


def check_escapes(src: str) -> list[str]:
    """Ký tự đặc biệt chưa escape, cả trong \\code{...} và văn bản thường."""
    problems = []
    text = strip_verbatim(src)
    text = re.sub(r"\\url\{[^}]*\}", lambda m: " " * len(m.group(0)), text)

    for m in re.finditer(r"\\code\{((?:[^{}]|\{[^{}]*\})*)\}", text):
        body = m.group(1)
        for ch in ("_", "#", "&", "%", "$"):
            for mm in re.finditer(re.escape(ch), body):
                if mm.start() > 0 and body[mm.start() - 1] == "\\":
                    continue
                problems.append(
                    f"dòng {line_of(text, m.start())}: '{ch}' chưa escape trong "
                    f"\\code{{...}} -> {body[:60]}"
                )
    # văn bản ngoài \code: bỏ các vùng đã xử lý và vùng toán học
    rest = re.sub(r"\\code\{[^{}]*\}", lambda m: " " * len(m.group(0)), text)
    rest = re.sub(r"\$[^$]*\$", lambda m: " " * len(m.group(0)), rest)
    for i, line in enumerate(rest.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        # #1, #2... trong định nghĩa macro là hợp lệ, không phải lỗi escape
        if re.match(r"\\(re)?newcommand|\\def|\\ProvideTextCommand", stripped):
            continue
        for ch in ("_", "#"):
            for mm in re.finditer(re.escape(ch), line):
                if mm.start() > 0 and line[mm.start() - 1] == "\\":
                    continue
                problems.append(f"dòng {i}: '{ch}' chưa escape -> {line.strip()[:70]}")
    return problems


def check_refs(src: str) -> list[str]:
    labels = set(re.findall(r"\\label\{([^}]+)\}", src))
    problems = []
    for ref in sorted(set(re.findall(r"\\ref\{([^}]+)\}", src))):
        if ref not in labels:
            problems.append(f"\\ref{{{ref}}} không có \\label tương ứng")
    return problems


def check_conditionals(src: str) -> list[str]:
    """Chỉ xét các \\if do người viết tự định nghĩa (\\newif) để tránh nhiễu."""
    body = strip_verbatim(src)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("%"))
    newifs = set(re.findall(r"\\newif\\if([A-Za-z@]+)", body))
    problems = []
    for name in newifs:
        opens = len(re.findall(rf"\\if{name}\b", body))
        closes = len(re.findall(r"\\fi\b", body))
        if opens and closes < 1:
            problems.append(f"\\if{name} xuất hiện {opens} lần nhưng không có \\fi")
    return problems


def column_count(spec: str) -> int:
    """Đếm số cột từ khai báo cột của tabular/tabularx."""
    s = re.sub(r"@\{[^{}]*\}", "", spec)          # bỏ @{...}
    s = re.sub(r"[><!]\{[^{}]*\}", "", s)         # bỏ >{...} <{...}
    s = re.sub(r"\*\{(\d+)\}\{[^{}]*\}", "", s)   # bỏ *{n}{...} (đếm thô)
    s = re.sub(r"[pmb]\{[^{}]*\}", "c", s)        # p{..}/m{..}/b{..} là 1 cột
    return len(re.findall(r"[lcrX]", s))


def check_tables(src: str) -> list[str]:
    """So số ô (&) mỗi hàng với số cột khai báo."""
    problems = []
    body = strip_verbatim(src)
    for m in re.finditer(
        r"\\begin\{(tabularx?)\}(\{[^{}]*\})\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", body
    ):
        spec = m.group(3)
        ncols = column_count(spec)
        start = m.end()
        end_m = re.search(r"\\end\{" + m.group(1) + r"\}", body[start:])
        if not end_m:
            continue
        inner = body[start : start + end_m.start()]
        for raw in inner.split(r"\\"):
            row = re.sub(r"\\(toprule|midrule|bottomrule|hline|addlinespace|endhead)", "", raw)
            row = row.strip()
            if not row:
                continue
            cells = len(re.findall(r"(?<!\\)&", row)) + 1
            multi = re.findall(r"\\multicolumn\{(\d+)\}", row)
            if multi:
                cells += sum(int(n) - 1 for n in multi)
            if cells != ncols:
                first = " ".join(row.split())[:60]
                problems.append(
                    f"dòng {line_of(body, start)}: hàng có {cells} ô nhưng khai báo "
                    f"{ncols} cột -> {first}"
                )
    return problems


def check_file(path: str) -> int:
    src = open(path, encoding="utf-8").read()
    body = strip_verbatim(src)
    print(f"== {path} ==")
    print(f"   {src.count(chr(10)) + 1} dòng, "
          f"{len(body.split())} từ, "
          f"{len(body.splitlines())} dòng văn bản")
    envs = Counter(re.findall(r"\\begin\{([^}]+)\}", src))
    print("   môi trường:", dict(envs))
    problems = (
        check_environments(body)
        + check_braces(body)
        + check_escapes(src)
        + check_refs(src)
        + check_conditionals(src)
        + check_tables(src)
    )
    if problems:
        print(f"   CÓ {len(problems)} VẤN ĐỀ:")
        for p in problems:
            print("    -", p)
        return 1
    print("   KHÔNG PHÁT HIỆN VẤN ĐỀ CÚ PHÁP")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    return max(check_file(p) for p in argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
