"""Type rendering: fonts, alpha sprites, blending, glyph coverage. Sizes are output pixels."""
import logging

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import config

logging.getLogger("fontTools").setLevel(logging.CRITICAL)

FONT_FILES = {
    "condensed": "Anton-Regular.ttf",
    "sans": "inter-Regular.ttf",
    "sans_bold": "Inter-Bold.ttf",
    "serif_italic": "PlayfairDisplay-Italic-var.ttf",
    "script": "caveat-latin-700-normal.woff2",
}


def font_path(role, overrides=None):
    p = (overrides or {}).get(role)
    return str(p) if p else str(config.FONTS / FONT_FILES[role])


_font = {}
_cap = {}
_spr = {}
_cmap = {}


def font(path, size):
    key = (path, int(size))
    if key not in _font:
        _font[key] = ImageFont.truetype(path, max(6, int(size)))
    return _font[key]


def cap_ratio(path):
    if path not in _cap:
        b = ImageFont.truetype(path, 200).getbbox("H", anchor="ls")
        _cap[path] = (b[3] - b[1]) / 200.0
    return _cap[path]


def size_for_cap(path, cap_px):
    return cap_px / cap_ratio(path)


def text_width(text, path, size):
    return font(path, round(size)).getlength(text)


def missing_glyphs(path, text):
    """Characters of text that the font has no glyph for (fontTools cmap; PIL notdef comparison as fallback,
    e.g. for .woff2 without the brotli module)."""
    if path not in _cmap:
        try:
            from fontTools.ttLib import TTFont
            _cmap[path] = set(TTFont(path, fontNumber=0).getBestCmap().keys())
        except Exception:
            _cmap[path] = None
    cm = _cmap[path]
    if cm is not None:
        return sorted({ch for ch in text if not ch.isspace() and ord(ch) not in cm})
    f = ImageFont.truetype(path, 48)

    def sig(ch):
        m = f.getmask(ch)
        return (m.size, bytes(m))
    notdef = sig("\U0010FFFD")
    return sorted({ch for ch in text if not ch.isspace() and sig(ch) == notdef})


def sprite(text, path, size, tracking=0.0):
    """(alpha HxW float32, pad, baseline_y, advance)"""
    key = (text, path, int(round(size)), tracking)
    if key in _spr:
        return _spr[key]
    f = font(path, round(size))
    pad = int(size * 0.5) + 4
    widths = [f.getlength(ch) for ch in text] if tracking else None
    adv = (sum(widths) + tracking * size * (len(text) - 1)) if tracking else f.getlength(text)
    asc, desc = f.getmetrics()
    im = Image.new("L", (int(adv + 2 * pad), int(asc + desc + 2 * pad)), 0)
    d = ImageDraw.Draw(im)
    base = pad + asc
    if tracking:
        x = pad
        for ch, cw in zip(text, widths):
            d.text((x, base), ch, font=f, fill=255, anchor="ls")
            x += cw + tracking * size
    else:
        d.text((pad, base), text, font=f, fill=255, anchor="ls")
    r = (np.asarray(im, np.float32) / 255.0, pad, base, adv)
    if len(_spr) > 4000:
        _spr.clear()
    _spr[key] = r
    return r


def blur(a, sigma):
    if sigma < 0.3:
        return a
    k = int(sigma * 3) * 2 + 1
    return cv2.GaussianBlur(a, (k, k), sigma)


def paste(dst, alpha, x, y, color, opacity=1.0, mask=None):
    """Blend colour with coverage alpha at top-left (x, y); returns the drawn box or None."""
    if opacity <= 0.003:
        return None
    H, W = dst.shape[:2]
    h, w = alpha.shape
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return None
    a = alpha[y0 - y:y1 - y, x0 - x:x1 - x] * opacity
    if mask is not None:
        a = a * mask[y0:y1, x0:x1]
    a = a[..., None]
    reg = dst[y0:y1, x0:x1]
    reg *= 1 - a
    reg += a * color
    return (x0, y0, x1, y1)


def draw_text(dst, text, path, size, x, y_base, color, opacity=1.0, blur_px=0.0, scale=1.0, align="l",
              mask=None, tracking=0.0, wipe=None, rot=0.0, grey_mix=0.0, grey=0.55):
    """x = left edge / centre / right edge of the advance box (align l/c/r); y_base = baseline.
    Returns the ink box (x0, y0, x1, y1) in output px, or None if nothing was drawn."""
    W = dst.shape[1]
    a, pad, base, adv = sprite(text, path, size * scale, tracking)
    if wipe is not None:
        a = a.copy()
        xs = np.arange(a.shape[1], dtype=np.float32)
        edge = pad + wipe * (adv + 0.06 * W) - 0.03 * W
        a = a * np.clip((edge - xs) / (0.03 * W), 0, 1)[None, :]
        if wipe < 1:
            a = np.maximum(a, blur(a, 4) * 0.8)
    if rot:
        M = cv2.getRotationMatrix2D((pad, base), rot, 1.0)
        a = cv2.warpAffine(a, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR)
    if blur_px > 0.3:
        a = blur(a, blur_px)
    lx = x - adv / 2 if align == "c" else (x - adv if align == "r" else x)
    col = color if grey_mix <= 0 else color * (1 - grey_mix) + np.float32(grey) * grey_mix
    box = paste(dst, a, lx - pad, y_base - base, col, opacity, mask)
    if box is None:
        return None
    # ink box (tighter than the sprite): from the glyph metrics
    asc = size * scale * cap_ratio(path) * 1.05
    return (int(lx), int(y_base - asc), int(lx + adv), int(y_base + 0.25 * size * scale))


def hex_bgr(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return np.array([b, g, r], np.float32) / 255
