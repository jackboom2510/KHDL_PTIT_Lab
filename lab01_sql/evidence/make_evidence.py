#!/usr/bin/env python3
"""Sinh ảnh minh chứng cho LAB 01 — chạy TÁCH RIÊNG khỏi luồng dựng CSDL và làm bài.

Vì sao tách riêng: `build_db.py` / `run_sql.py` / `generate_data.py` chỉ có một việc là tạo
và truy vấn dữ liệu. Việc chụp ảnh minh chứng thay đổi thường xuyên (đổi bố cục, chụp lại
một ảnh, chạy trên Cloud Shell khác) và cần thêm thư viện ngoài (Pillow). Tách thành pipeline
riêng để:

  * không thêm dependency vào bài nộp bắt buộc (đề chỉ yêu cầu sql_console.py, answers.sql…);
  * sinh lại ảnh mà không phải dựng lại CSDL hay chạy lại toàn bộ câu trả lời;
  * dựng CSDL trên bản sao trong thư mục tạm, nên ảnh luôn ở trạng thái sạch (S05 chỉ +10%
    một lần, không bị ảnh hưởng bởi lần chạy trước).

Cách dùng (từ thư mục lab01_sql/evidence/):

    pip install -r requirements.txt        # chỉ cần Pillow
    python3 make_evidence.py               # sinh cả 7 ảnh vào ../evidence/
    python3 make_evidence.py --list        # xem danh sách scene
    python3 make_evidence.py --only 04,06  # chỉ sinh lại vài ảnh
    python3 make_evidence.py --from-log    # render lại từ log đã lưu, không chạy lệnh
    python3 make_evidence.py --scale 3     # ảnh nét hơn (mặc định 2)
    python3 make_evidence.py --out /tmp/x  # đổi thư mục đích

Mỗi lần chạy, nội dung thô của từng scene được lưu vào `evidence/_logs/<slug>.txt` (bị
gitignore) để có thể render lại hoặc đối chiếu; `evidence/manifest.json` ghi lại ảnh nào
được sinh từ lệnh nào.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import runner  # noqa: E402
from render import Renderer, Scene, Segment, today  # noqa: E402
import scenes  # noqa: E402

DEFAULT_OUT = HERE.parent / "evidence"
LOG_DIR = HERE / "_logs"


def scene_text(scene: Scene) -> str:
    parts = []
    for seg in scene.segments:
        if seg.caption:
            parts.append(f"## {seg.caption}")
        parts.append(seg.text.rstrip())
    if scene.footnotes:
        parts.append("## Ghi chú")
        parts += [f"- {f}" for f in scene.footnotes]
    return "\n\n".join(parts) + "\n"


def scene_from_log(slug: str, log: Path) -> Scene:
    """Dựng lại Scene tối thiểu từ log, để render lại không cần chạy lệnh."""
    text = log.read_text(encoding="utf-8")
    body: list[str] = []
    foot: list[str] = []
    section = "body"
    for line in text.splitlines():
        if line.startswith("## Ghi chú"):
            section = "foot"
            continue
        if line.startswith("## "):
            body.append("")
            body.append(line[3:].upper())
            continue
        (foot if section == "foot" else body).append(line)
    titles = {slug_: (fn.__doc__ or "") for slug_, fn in scenes.SCENES}
    return Scene(
        slug=slug,
        title=slug.replace("_", " "),
        subtitle="render lại từ log",
        segments=[Segment("\n".join(body).strip() + "\n")],
        footnotes=[f.lstrip("- ").strip() for f in foot if f.strip().startswith("-")],
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Sinh ảnh minh chứng LAB 01 (tách riêng khỏi build_db/answers)"
    )
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="thư mục chứa ảnh PNG")
    ap.add_argument("--only", default="", help="danh sách slug cách nhau bằng dấu phẩy")
    ap.add_argument("--list", action="store_true", help="in danh sách scene rồi thoát")
    ap.add_argument("--from-log", action="store_true", help="render lại từ evidence/_logs")
    ap.add_argument("--scale", type=int, default=2, help="hệ số phóng to ảnh (mặc định 2)")
    ap.add_argument("--width", type=int, default=118, help="số cột ký tự mỗi dòng")
    ap.add_argument("--keep-workdir", action="store_true", help="giữ thư mục CSDL tạm")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    registry = dict(scenes.SCENES)
    if args.list:
        print("Các scene của LAB 01:")
        for slug, _ in scenes.SCENES:
            print(f"  {slug}")
        return 0

    wanted = [s.strip() for s in args.only.split(",") if s.strip()] or [s for s, _ in scenes.SCENES]
    unknown = [s for s in wanted if s not in registry]
    if unknown:
        print(f"[!] Không có scene: {', '.join(unknown)}", file=sys.stderr)
        print(f"    Chọn trong: {', '.join(registry)}", file=sys.stderr)
        return 2

    out_dir = args.out if args.out.is_absolute() else (HERE.parent / args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    renderer = Renderer(scale=args.scale, width=args.width)

    workdir = scenes.prepare_workdir()
    shared = scenes.shared_extended_db()
    if not shared.exists():
        runner.run(
            ["python3", "generate_data.py", "--force", "--out", str(shared)],
            python=runner.which_python(),
        )

    manifest_path = out_dir / "manifest.json"
    manifest: dict = {"lab": "LAB 01", "generated_by": "make_evidence.py",
                      "generated_on": today(), "images": []}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["generated_on"] = today()
        except json.JSONDecodeError:
            pass
    done = {img["slug"]: img for img in manifest.get("images", [])}

    t0 = time.time()
    failures = 0
    for slug in wanted:
        log_path = LOG_DIR / f"{slug}.txt"
        try:
            if args.from_log:
                if not log_path.exists():
                    print(f"[!] {slug}: chưa có log {log_path.name} — bỏ qua", file=sys.stderr)
                    failures += 1
                    continue
                scene = scene_from_log(slug, log_path)
            else:
                scene = registry[slug](workdir)
                log_path.write_text(scene_text(scene), encoding="utf-8")

            png = renderer.render(scene, out_dir / f"{slug}.png")
            size_kb = png.stat().st_size / 1024
            done[slug] = {
                "slug": slug,
                "file": png.name,
                "title": scene.title,
                "log": f"_logs/{slug}.txt" if log_path.exists() else None,
                "bytes": png.stat().st_size,
                "source": "log" if args.from_log else "live",
            }
            if not args.quiet:
                print(f"[ok] {png.name:<32} {size_kb:6.1f} KB  {scene.title}")
            else:
                print(f"[ok] {png.name}")
        except Exception as exc:                     # noqa: BLE001 - báo rõ scene nào lỗi
            failures += 1
            print(f"[!] {slug}: {type(exc).__name__}: {exc}", file=sys.stderr)

    manifest["images"] = [done[s] for s in sorted(done)]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if not args.keep_workdir:
        import shutil

        shutil.rmtree(workdir, ignore_errors=True)

    print(
        f"\n{len(wanted) - failures}/{len(wanted)} ảnh trong {out_dir} "
        f"({time.time() - t0:.1f}s) — manifest: {manifest_path.name}"
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
