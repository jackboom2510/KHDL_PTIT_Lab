#!/usr/bin/env python3
"""Render khung terminal ra PNG bằng Pillow.

Chỉ là phần "vẽ": nhận tiêu đề + các khối văn bản (đã có output thật), trả về file PNG.
Không chạy lệnh, không đọc CSDL — nhờ vậy có thể render lại từ log đã lưu (--from-log)
mà không cần chạy lại pipeline.

Font: DejaVu Sans Mono (có sẵn trong TeX Live / Debian `fonts-dejavu-core`) để tiếng Việt
và các ký tự `→ ─ │` hiển thị đúng. Nếu không tìm thấy font, tự lùi về font mặc định của
Pillow (ASCII) và báo cảnh báo.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "/Library/Fonts/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/DejaVuSansMono.ttf",
]

FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
]

# DejaVuSansMono thiếu ~46 ký tự tiếng Việt (hook above, hỏi, ngã trên nhiều nguyên âm),
# trong khi DejaVuSans (proportional) phủ đủ 156 ký tự. Dùng DejaVuSans làm font dự phòng
# theo TỪNG ký tự để vẫn giữ lưới monospace mà không bị ô vuông.
FALLBACK_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]

# Bảng màu kiểu terminal sáng, in ra giấy vẫn rõ
BG = (252, 252, 253)
BAR = (238, 241, 246)
BORDER = (205, 210, 220)
FG = (28, 32, 38)
FG_DIM = (110, 118, 130)
ACCENT = (24, 90, 170)
OK = (22, 120, 60)
WARN = (170, 90, 20)
PROMPT_COLOR = (140, 60, 140)


def _first_existing(paths: list[str]) -> str | None:
    for p in paths:
        if Path(p).is_file():
            return p
    for name in ("DejaVuSansMono.ttf",):
        found = shutil.which(name)
        if found:
            return found
    return None


@dataclass
class Segment:
    """Một khối nội dung trong ảnh: tiêu đề phụ (tuỳ chọn) + text."""

    text: str
    caption: str | None = None
    color: tuple[int, int, int] | None = None


@dataclass
class Scene:
    slug: str
    title: str
    subtitle: str = ""
    segments: list[Segment] = field(default_factory=list)
    footnotes: list[str] = field(default_factory=list)


class Renderer:
    def __init__(self, scale: int = 2, font_size: int = 15, width: int = 118):
        self.scale = max(1, scale)
        self.font_size = font_size
        self.cols = width
        self.mono_path = _first_existing(FONT_CANDIDATES)
        self.bold_path = _first_existing(FONT_BOLD_CANDIDATES) or self.mono_path
        self.font = self._load(self.mono_path, font_size)
        self.font_bold = self._load(self.bold_path, font_size)
        self.font_small = self._load(self.mono_path, max(9, font_size - 3))
        self.fallback_path = _first_existing(FALLBACK_CANDIDATES)
        self.fallback = self._load(self.fallback_path, font_size)
        self.fallback_small = self._load(self.fallback_path, max(9, font_size - 3))
        self._missing_cache: dict[tuple[int, str], bool] = {}
        self.line_h = int(font_size * 1.45)
        self.pad = 26
        self.bar_h = 54

    def _load(self, path: str | None, size: int):
        if path:
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
        return ImageFont.load_default()

    # ---------------- glyph thiếu -> font dự phòng ----------------
    def _has_glyph(self, font_id: int, font, ch: str) -> bool:
        key = (font_id, ch)
        cached = self._missing_cache.get(key)
        if cached is not None:
            return not cached
        probe = Image.new("L", (48, 48), 0)
        pd = ImageDraw.Draw(probe)
        pd.text((6, 6), "\ue000", font=font, fill=255)
        notdef = probe.tobytes()
        probe2 = Image.new("L", (48, 48), 0)
        pd2 = ImageDraw.Draw(probe2)
        pd2.text((6, 6), ch, font=font, fill=255)
        missing = probe2.tobytes() == notdef and not ch.isspace()
        self._missing_cache[key] = missing
        return not missing

    def _draw(self, d, x: int, y: int, text: str, font, color, fallback) -> None:
        """Vẽ chuỗi, ký tự nào font mono không có thì lấy từ font dự phòng (giữ nguyên ô)."""
        if self.fallback_path is None:
            d.text((x, y), text, font=font, fill=color)
            return
        cell = self._char_w()
        cx = x
        for ch in text:
            if ch.isspace() or self._has_glyph(id(font), font, ch):
                d.text((cx, y), ch, font=font, fill=color)
            else:
                d.text((cx, y), ch, font=fallback, fill=color)
            cx += cell

    # ---------------- đo và cắt dòng ----------------
    def _text_w(self, text: str, font) -> int:
        return int(font.getlength(text))

    def _char_w(self) -> int:
        return max(1, self._text_w("M", self.font))

    def _wrap(self, line: str) -> list[str]:
        """Cắt dòng theo ranh giới TỪ để không bẻ đôi chữ; từ quá dài mới cắt theo ký tự."""
        if not line:
            return [""]
        if len(line) <= self.cols:
            return [line]

        out: list[str] = []
        cur = ""
        for word in line.split(" "):
            candidate = word if not cur else cur + " " + word
            if len(candidate) <= self.cols:
                cur = candidate
                continue
            if cur:
                out.append(cur)
                cur = ""
            while len(word) > self.cols:          # từ dài hơn cả dòng: cắt cứng
                out.append(word[: self.cols])
                word = word[self.cols :]
            cur = word
        if cur:
            out.append(cur)
        return out

    # ---------------- vẽ ----------------
    def render(self, scene: Scene, out_path: Path, note: str | None = None) -> Path:
        body: list[tuple[str, object, tuple[int, int, int]]] = []
        for seg in scene.segments:
            if seg.caption:
                body.append(("caption", seg.caption, ACCENT))
            for raw in seg.text.rstrip("\n").splitlines():
                for piece in self._wrap(raw):
                    color = seg.color or FG
                    if piece.startswith("$ "):
                        color = PROMPT_COLOR
                    elif piece.lstrip().startswith(("ok", "0 lỗi", "Rows affected", "1 rows")):
                        color = FG
                    body.append(("line", piece, color))
            body.append(("gap", "", FG))

        while body and body[-1][0] == "gap":      # bỏ khoảng trắng thừa ở cuối
            body.pop()

        foot = list(scene.footnotes)
        if note:
            foot.append(note)

        char_w = self._char_w()
        width = self.pad * 2 + max(
            self.cols * char_w,
            self._text_w(scene.title, self.font_bold) + 20,
            max((self._text_w(f, self.font_small) for f in foot), default=0),
        )
        height = (
            self.bar_h
            + self.pad
            + len(body) * self.line_h
            + (len(foot) * (self.line_h - 4) + 10 if foot else 0)
            + self.pad * 2
        )

        img = Image.new("RGB", (width, height), BG)
        d = ImageDraw.Draw(img)

        # thanh tiêu đề
        d.rectangle([0, 0, width, self.bar_h], fill=BAR)
        d.line([0, self.bar_h, width, self.bar_h], fill=BORDER)
        for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            x = 18 + i * 18
            d.ellipse([x, 20, x + 11, 31], fill=color)
        self._draw(d, 78, 15, scene.title, self.font_bold, FG, self.fallback)
        if scene.subtitle:
            self._draw(
                d, 78, 15 + self.font_size + 3, scene.subtitle,
                self.font_small, FG_DIM, self.fallback_small,
            )
        d.text(
            (width - self.pad - self._text_w(scene.slug, self.font_small), 18),
            scene.slug,
            font=self.font_small,
            fill=FG_DIM,
        )

        # thân
        y = self.bar_h + self.pad
        for kind, text, color in body:
            if kind == "gap":
                y += self.line_h // 2
                continue
            if kind == "caption":
                font, fb = self.font_bold, self.fallback
            else:
                font, fb = self.font, self.fallback
            self._draw(d, self.pad, y, text, font, color, fb)
            y += self.line_h

        # chân
        if foot:
            y += 6
            d.line([self.pad, y, width - self.pad, y], fill=BORDER)
            y += 10
            for line in foot:
                self._draw(d, self.pad, y, line, self.font_small, FG_DIM, self.fallback_small)
                y += self.line_h - 4

        d.rectangle([0, 0, width - 1, height - 1], outline=BORDER)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, format="PNG", optimize=True)
        return out_path


def today() -> str:
    return date.today().isoformat()
