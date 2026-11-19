"""Sklet x SPC edit: frame-by-frame compositor.

Output time == source time (the speech is never retimed); inserts, cards and
punch-ins only change what is shown. Footage, matte and inserts are streamed
from ffmpeg so memory stays at a few frames.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent.parent
SRC = r"C:\Users\bexru\Downloads\Telegram Desktop\Sklet.mp4"
TRANSCRIPT = P / "assets" / "transcript.json"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else P / "out" / "sklet-v1-picture.mp4"
T_START = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
T_END = float(sys.argv[3]) if len(sys.argv) > 3 else 32.55

W, H, FPS = 1080, 1920, 30
SW, SH = 1620, 2880          # decoded footage size (1.5x headroom for punch-ins)
MW, MH = 810, 1440           # matte size

NAVY = (18, 42, 57)
OXIDE = (156, 73, 50)
MIST = (197, 212, 222)
WHITE = (247, 248, 246)

FONT = {
    "sg_light": str(P / "assets" / "spacegrotesk-Light.ttf"),
    "sg_reg": str(P / "assets" / "spacegrotesk-Regular.ttf"),
    "inter_var": str(P / "assets" / "inter-variable.ttf"),
    "sg_var": str(P / "assets" / "spacegrotesk-variable.ttf"),
}


def font(name, size, weight=None):
    f = ImageFont.truetype(FONT[name], size)
    if weight and name == "inter_var":
        f.set_variation_by_axes([32, weight])     # Inter: (optical size, weight)
    elif weight:
        f.set_variation_by_axes([weight])
    return f


# ---------------------------------------------------------------- easing

def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return 3 * x * x - 2 * x * x * x


def envelope(t, t_in, t_out, fade_in=0.3, fade_out=0.25):
    """0..1 visibility plus entry progress (for slide/scale)."""
    if t < t_in or t >= t_out:
        return 0.0, 0.0
    p_in = ease_out((t - t_in) / fade_in)
    p_out = ease_out((t_out - t) / fade_out)
    return min(p_in, p_out), p_in


# ---------------------------------------------------------------- text layers

_text_cache = {}


def text_layer(text, fnt, fill=WHITE, tracking=0, shadow=0.6):
    """RGBA float layer (h, w, 4) with a soft drop shadow baked in."""
    key = (text, id(fnt), fill, tracking, shadow)
    if key in _text_cache:
        return _text_cache[key]
    pad = 40
    widths = [fnt.getlength(ch) + tracking for ch in text]
    tw = int(sum(widths) - tracking) + 2 * pad
    asc, desc = fnt.getmetrics()
    th = asc + desc + 2 * pad
    img = Image.new("L", (tw, th), 0)
    d = ImageDraw.Draw(img)
    x = pad
    for ch, w in zip(text, widths):
        d.text((x, pad), ch, font=fnt, fill=255)
        x += w
    a = np.asarray(img, np.float32) / 255
    layer = np.zeros((th, tw, 4), np.float32)
    if shadow:
        sh = cv2.GaussianBlur(a, (0, 0), max(3, fnt.size / 14))
        sh = np.clip(np.roll(sh, int(fnt.size / 30) + 1, axis=0) * 1.6, 0, 1) * shadow
        layer[..., 3] = sh  # shadow is black
    rgb = np.array(fill, np.float32) / 255
    out_a = a + layer[..., 3] * (1 - a)
    layer[..., :3] = (rgb * a[..., None]) / np.maximum(out_a[..., None], 1e-6)
    layer[..., 3] = out_a
    _text_cache[key] = layer
    return layer


def over(dst, layer, x, y, opacity=1.0, occluder=None):
    """Composite layer at top-left (x, y). occluder (H, W) in 0..1 hides the layer."""
    if opacity <= 0:
        return
    lh, lw = layer.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + lw), min(H, y + lh)
    if x1 <= x0 or y1 <= y0:
        return
    sub = layer[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3] * opacity
    if occluder is not None:
        a = a * (1 - occluder[y0:y1, x0:x1])
    region = dst[y0:y1, x0:x1]
    region *= (1 - a[..., None])
    region += sub[..., :3] * a[..., None]


def place_text(dst, text, fnt, cx, cy, t, t_in, t_out, fill=WHITE, tracking=0,
               slide=36, occluder=None, shadow=0.6, fade_in=0.3, fade_out=0.25):
    vis, p_in = envelope(t, t_in, t_out, fade_in, fade_out)
    if vis <= 0:
        return
    layer = text_layer(text, fnt, fill, tracking, shadow)
    lh, lw = layer.shape[:2]
    dy = int((1 - p_in) * slide)
    over(dst, layer, int(cx - lw / 2), int(cy - lh / 2) + dy, vis, occluder)


# ---------------------------------------------------------------- pipe contour (brand graphic element)

def snake_path():
    """Centre line of a pipe running in rows with rounded U-turns (brandbook p.20)."""
    pts = []
    rows = [430, 690, 950]
    r = 130
    xl, xr = 210, 870
    pts += [(x, rows[0]) for x in np.linspace(-80, xr, 80)]
    for i in range(len(rows) - 1):
        cy = (rows[i] + rows[i + 1]) / 2
        right = i % 2 == 0
        cx = xr if right else xl
        for a in np.linspace(-math.pi / 2, math.pi / 2, 40):
            pts.append((cx + (r * math.cos(a) if right else -r * math.cos(a)), cy + r * math.sin(a)))
        xs = np.linspace(xr, xl, 70) if right else np.linspace(xl, xr, 70)
        pts += [(x, rows[i + 1]) for x in xs]
    pts += [(x, rows[-1]) for x in np.linspace(xl if len(rows) % 2 == 0 else xr, 1160, 40)]
    return np.array(pts, np.float32)


SNAKE = snake_path()
SNAKE_SEG = np.r_[0, np.cumsum(np.hypot(*np.diff(SNAKE, axis=0).T))]


def offset_path(pts, d):
    tang = np.gradient(pts, axis=0)
    tang /= np.maximum(np.linalg.norm(tang, axis=1, keepdims=True), 1e-6)
    normal = np.stack([-tang[:, 1], tang[:, 0]], 1)
    return pts + normal * d


SNAKE_A, SNAKE_B = offset_path(SNAKE, 30), offset_path(SNAKE, -30)


def draw_pipe_line(dst, progress, color=MIST, width=3):
    n = int(np.searchsorted(SNAKE_SEG, progress * SNAKE_SEG[-1]))
    if n < 2:
        return
    canvas = np.zeros((H, W), np.uint8)
    for path in (SNAKE_A, SNAKE_B):
        cv2.polylines(canvas, [np.round(path[:n] * 4).astype(np.int32)], False, 255, width,
                      cv2.LINE_AA, shift=2)
    a = canvas.astype(np.float32)[..., None] / 255
    dst *= (1 - a)
    dst += a * (np.array(color, np.float32) / 255)


def pipe_bar(dst, x, y, length, color=MIST, width=3, gap=26):
    """Horizontal pipe drawn as two parallel lines with a rounded end."""
    if length < 4:
        return
    canvas = np.zeros((H, W), np.uint8)
    r = gap // 2
    x2 = int(x + length)
    cv2.line(canvas, (x, y - r), (x2 - r, y - r), 255, width, cv2.LINE_AA)
    cv2.line(canvas, (x, y + r), (x2 - r, y + r), 255, width, cv2.LINE_AA)
    cv2.ellipse(canvas, (x2 - r, y), (r, r), 0, -90, 90, 255, width, cv2.LINE_AA)
    a = canvas.astype(np.float32)[..., None] / 255
    dst *= (1 - a)
    dst += a * (np.array(color, np.float32) / 255)


def panel(dst, x0, y0, x1, y1, color=NAVY, opacity=0.82):
    region = dst[y0:y1, x0:x1]
    region *= 1 - opacity
    region += np.array(color, np.float32) / 255 * opacity


# ---------------------------------------------------------------- grade

def make_lut():
    x = np.linspace(0, 1, 256)
    s = x * x * (3 - 2 * x)
    y = x + (s - x) * 0.22
    lut = np.stack([y * 0.985, y, np.clip(y * 1.02, 0, 1)], 1)
    return (lut * 255).clip(0, 255).astype(np.uint8)


LUT = make_lut()


def grade(frame_u8):
    out = np.empty_like(frame_u8)
    for c in range(3):
        out[..., c] = LUT[frame_u8[..., c], c]
    g = out.astype(np.float32)
    lum = g.mean(axis=2, keepdims=True)
    return (lum + (g - lum) * 0.9) / 255


# ---------------------------------------------------------------- readers

class Reader:
    """Sequential ffmpeg frame reader; frames are requested by time, monotonically."""

    def __init__(self, path, w, h, fps, fmt="rgb24", vf_extra=""):
        self.w, self.h, self.fps = w, h, fps
        self.ch = 3 if fmt == "rgb24" else 1
        vf = f"fps={fps},scale={w}:{h}:flags=lanczos" + vf_extra
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", str(path), "-vf", vf, "-f", "rawvideo",
             "-pix_fmt", fmt, "-"], stdout=subprocess.PIPE)
        self.idx = -1
        self.frame = None

    def at(self, t):
        want = max(0, int(round(t * self.fps)))
        size = self.w * self.h * self.ch
        while self.idx < want:
            buf = self.proc.stdout.read(size)
            if len(buf) < size:
                break
            self.idx += 1
            self.frame = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, self.ch)
        return self.frame

    def close(self):
        self.proc.kill()


# ---------------------------------------------------------------- edit decision list

GEN = P / "gen" / "video"
INSERTS = [
    # (t_in, t_out, file, clip_offset, clip_speed)
    (1.20, 2.75, GEN / "v0_statue.mp4", 1.0, 1.0),
    (3.74, 7.74, GEN / "v1_xray.mp4", 0.5, 1.0),
    (9.80, 12.94, GEN / "v2_morph.mp4", 0.9, 1.28),
    (23.30, 25.80, GEN / "v3_tower.mp4", 1.0, 1.0),
]
CARD = (16.60, 20.25)


def camera(t, matte_cx):
    """Return (zoom, cx, cy) in normalised source coordinates."""
    if t < 2.07:                                   # A: crane, slow push
        return 1.0 + 0.06 * ease_in_out(t / 2.07), 0.5, 0.5
    if t < 23.22:                                  # B: pipes, one long take
        for a, b, z, cx, cy in [(7.74, 9.80, 1.35, 0.48, 0.40),
                                (20.25, 23.22, 1.45, 0.48, 0.38)]:
            if a <= t < b:
                return z, cx, cy
        return 1.0, 0.5, 0.5
    if t < 28.92:                                  # C: crane, walking
        if t >= 28.06:
            return 1.55, matte_cx, 0.40
        return 1.0 + 0.08 * ease_in_out((t - 25.8) / 2.2) if t > 25.8 else 1.0, 0.5, 0.5
    return 1.0 + 0.04 * ease_in_out((t - 28.92) / 3.6), 0.5, 0.45   # D: close


def crop(img, z, cx, cy, out_w, out_h, interp=cv2.INTER_AREA):
    h, w = img.shape[:2]
    cw, ch = w / z, h / z
    x0 = min(max(cx * w - cw / 2, 0), w - cw)
    y0 = min(max(cy * h - ch / 2, 0), h - ch)
    m = np.float32([[out_w / cw, 0, -x0 * out_w / cw], [0, out_h / ch, -y0 * out_h / ch]])
    return cv2.warpAffine(img, m, (out_w, out_h), flags=interp if z > 1.01 else cv2.INTER_AREA,
                          borderMode=cv2.BORDER_REPLICATE)


# ---------------------------------------------------------------- captions

FIXES = {(2.12, "Umumi"): "Umumiy", (2.84, "ikki"): "ikki yuz", (8.62, "ikki"): "ikki yuz",
         (29.76, "metalladan"): "metalldan"}


def load_words():
    data = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
    words = []
    for w in data["words"]:
        s, e, txt = w["start_us"] / 1e6, w["end_us"] / 1e6, w["text"]
        txt = FIXES.get((round(s, 2), txt), txt).replace("'", "\u2018")
        if words and words[-1][2] == "Nyu" and txt == "Yorkning":
            words[-1] = (words[-1][0], e, "Nyu-Yorkning")
            continue
        words.append((s, e, txt))
    return words


def caption_chunks(words, max_chars=22):
    chunks, cur = [], []
    for w in words:
        cand = " ".join(x[2] for x in cur + [w])
        if cur and (len(cand) > max_chars or cur[-1][2][-1] in ".,?!"):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


CAP_FONT = font("inter_var", 58, 620)
CAP_Y = 1440


def draw_caption(dst, chunks, t):
    for i, ch in enumerate(chunks):
        start = ch[0][0] - 0.08
        end = chunks[i + 1][0][0] - 0.08 if i + 1 < len(chunks) else ch[-1][1] + 0.4
        end = min(end, ch[-1][1] + 0.6)
        if not (start <= t < end):
            continue
        pieces = [w[2] for w in ch]
        space = CAP_FONT.getlength(" ")
        widths = [CAP_FONT.getlength(p) for p in pieces]
        total = sum(widths) + space * (len(pieces) - 1)
        x = W / 2 - total / 2
        vis, p_in = envelope(t, start, end, 0.12, 0.12)
        for (s, e, _), p, w in zip(ch, pieces, widths):
            active = s - 0.04 <= t < e + 0.06
            if active:
                pad_x, pad_y = 14, 8
                asc, desc = CAP_FONT.getmetrics()
                y0 = int(CAP_Y - (asc + desc) / 2 - pad_y)
                y1 = int(CAP_Y + (asc + desc) / 2 + pad_y - 6)
                x0, x1 = int(x - pad_x), int(x + w + pad_x)
                pill = dst[y0:y1, max(0, x0):min(W, x1)]
                pill *= 1 - 0.92 * vis
                pill += np.array(OXIDE, np.float32) / 255 * 0.92 * vis
            layer = text_layer(p, CAP_FONT, WHITE, 0, 0.0 if active else 0.9)
            lh, lw = layer.shape[:2]
            over(dst, layer, int(x - 40), int(CAP_Y - lh / 2) + int((1 - p_in) * 10), vis)
            x += w + space


# ---------------------------------------------------------------- logo

def load_logo(width=640):
    img = Image.open(P / "assets" / "spc-primary-logo-page09-crop.png").convert("RGB")
    a = np.asarray(img, np.float32) / 255
    lum = a.mean(axis=2)
    alpha = np.clip((0.93 - lum) / (0.93 - 0.25), 0, 1)       # navy ink on off-white paper
    h = int(img.height * width / img.width)
    alpha = cv2.resize(alpha, (width, h), interpolation=cv2.INTER_AREA)
    layer = np.zeros((h, width, 4), np.float32)
    layer[..., :3] = np.array(NAVY, np.float32) / 255
    layer[..., 3] = alpha
    return layer


LOGO = load_logo()


# ---------------------------------------------------------------- graphics per beat

F_HUGE = font("sg_var", 330, 500)
F_BIG = font("sg_var", 210, 500)
F_MID = font("sg_var", 120, 500)
F_LABEL = font("sg_var", 64, 500)
F_SMALL = font("sg_reg", 46)
F_XRAY = font("sg_var", 140, 500)
F_XRAY_L = font("sg_var", 44, 500)
F_MORPH = font("sg_var", 160, 500)


def graphics_behind(dst, t, occ):
    """Big words that sit behind the speaker."""
    place_text(dst, "OZODLIK", F_BIG, W / 2, 600, t, 0.16, 1.20, occluder=occ, tracking=4)
    place_text(dst, "HAYKALI", F_BIG, W / 2, 800, t, 0.68, 1.20, occluder=occ, tracking=4)
    place_text(dst, "200", F_HUGE, W / 2, 380, t, 2.84, 3.74, occluder=occ)
    place_text(dst, "TONNA", F_MID, W / 2, 640, t, 3.12, 3.74, occluder=occ, tracking=18)
    if 14.66 <= t < 16.60:
        n = int(round(4200 * ease_out((t - 14.66) / (15.90 - 14.66)) / 10)) * 10
        label = f"{n:,}".replace(",", "\u2009")
        place_text(dst, label, F_HUGE, W / 2, 400, t, 14.66, 16.60, occluder=occ, slide=0)
    place_text(dst, "12 METRLIK QUVUR", F_LABEL, W / 2, 190, t, 14.12, 16.60, fill=MIST, tracking=6)
    place_text(dst, "\u2248 30\u00d7", F_HUGE, W / 2, 420, t, 25.80, 28.06, fill=NAVY, occluder=occ, shadow=0.0)
    place_text(dst, "OZODLIK HAYKALI", F_LABEL, W / 2, 200, t, 26.32, 28.06, fill=NAVY, tracking=8, shadow=0.0)


def leader(dst, p0, p1, progress, color=MIST, width=2):
    if progress <= 0:
        return
    x = p0[0] + (p1[0] - p0[0]) * progress
    y = p0[1] + (p1[1] - p0[1]) * progress
    canvas = np.zeros((H, W), np.uint8)
    cv2.line(canvas, p0, (int(x), int(y)), 255, width, cv2.LINE_AA)
    if progress >= 1:
        cv2.circle(canvas, p1, 7, 255, -1, cv2.LINE_AA)
    a = canvas.astype(np.float32)[..., None] / 255
    dst *= (1 - a)
    dst += a * (np.array(color, np.float32) / 255)


def graphics_front(dst, t):
    # x-ray insert labels, in the free navy margins either side of the statue
    place_text(dst, "30 t", F_XRAY, 160, 800, t, 4.12, 7.74, shadow=0.0, slide=20)
    place_text(dst, "MIS QOBIQ", F_XRAY_L, 160, 890, t, 4.34, 7.74, fill=OXIDE, tracking=4, shadow=0.0, slide=20)
    if 4.34 <= t < 7.74:
        leader(dst, (250, 940), (390, 1010), ease_out((t - 4.34) / 0.35) * envelope(t, 4.34, 7.74)[0], OXIDE)
    place_text(dst, "TEMIR", F_XRAY_L, 925, 1270, t, 6.60, 7.74, fill=WHITE, tracking=4, shadow=0.0, slide=20)
    place_text(dst, "KARKAS", F_XRAY_L, 925, 1320, t, 6.70, 7.74, fill=WHITE, tracking=4, shadow=0.0, slide=20)
    if 6.70 <= t < 7.74:
        leader(dst, (835, 1295), (580, 1295), ease_out((t - 6.70) / 0.3) * envelope(t, 6.70, 7.74)[0], WHITE)
    # morph label
    place_text(dst, "57 \u00d7 3 MM", F_MORPH, W / 2, 1150, t, 10.50, 12.94, tracking=2)
    place_text(dst, "QUVUR", F_LABEL, W / 2, 1290, t, 11.98, 12.94, fill=MIST, tracking=12)
    # marathon comparison
    if 20.25 <= t < 23.22:
        vis, _ = envelope(t, 20.30, 23.22, 0.25, 0.2)
        if vis > 0:
            panel(dst, 60, 1040, 1020, 1330, opacity=0.84 * vis)
            full = 700
            g1 = ease_out((t - 20.40) / 0.9) * full
            g2 = ease_out((t - 21.42) / 0.9) * full * 42.2 / 50
            place_text(dst, "QUVURLAR", F_SMALL, 200, 1105, t, 20.40, 23.22, fill=MIST, slide=0, shadow=0)
            place_text(dst, "50 km", F_LABEL, 900, 1105, t, 20.80, 23.22, fill=WHITE, slide=0, shadow=0)
            pipe_bar(dst, 110, 1165, g1 * vis, MIST)
            place_text(dst, "MARAFON", F_SMALL, 190, 1225, t, 21.42, 23.22, fill=MIST, slide=0, shadow=0)
            place_text(dst, "42,2 km", F_LABEL, 885, 1225, t, 21.80, 23.22, fill=WHITE, slide=0, shadow=0)
            pipe_bar(dst, 110, 1285, g2 * vis, OXIDE)
    # tower
    place_text(dst, "TOSHKENT", F_MID, W / 2, 1080, t, 23.30, 25.80, tracking=10)
    place_text(dst, "TELEMINORASI", F_LABEL, W / 2, 1200, t, 23.70, 25.80, fill=MIST, tracking=10)
    # question
    place_text(dst, "TASAVVUR", F_MID, W / 2, 330, t, 28.06, 28.92, fill=NAVY, tracking=8, shadow=0.0)
    place_text(dst, "QILAYAPSIZMI?", F_MID, W / 2, 470, t, 28.38, 28.92, fill=NAVY, tracking=4, shadow=0.0)


def draw_card(dst, t):
    a, b = CARD
    dst[:] = np.array(NAVY, np.float32) / 255
    draw_pipe_line(dst, ease_in_out((t - 16.74) / 2.4))
    place_text(dst, "4 200 \u00d7 12 m", F_LABEL, W / 2, 200, t, 16.74, b, fill=MIST, tracking=6, shadow=0)
    if t >= 18.84:
        km = 50 * ease_out((t - 18.84) / 0.62)
        place_text(dst, f"{km:.0f} KM", F_HUGE, W / 2, 1180, t, 18.84, b, slide=0, shadow=0)


def end_card(dst, t):
    vis, p_in = envelope(t, 30.90, 99, 0.6, 0.1)
    if vis <= 0:
        return
    grad = np.linspace(1, 0, 900, dtype=np.float32)[:, None, None] ** 1.4 * 0.88 * vis
    dst[:900] = dst[:900] * (1 - grad) + np.array(WHITE, np.float32) / 255 * grad
    lh, lw = LOGO.shape[:2]
    over(dst, LOGO, (W - lw) // 2, 220 + int((1 - p_in) * 30), vis)
    place_text(dst, "ISHONCH SINOVDAN BOSHLANADI", F_SMALL, W / 2, 560, t, 31.30, 99,
               fill=NAVY, tracking=6, shadow=0)


# ---------------------------------------------------------------- main loop

def main():
    words = load_words()
    chunks = caption_chunks(words)
    src = Reader(SRC, SW, SH, FPS, vf_extra="")
    mat = Reader(P / "work" / "matte.mp4", MW, MH, FPS, fmt="gray")
    readers = {}
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-ss", str(T_START), "-t", str(T_END - T_START), "-i", SRC,
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT)],
        stdin=subprocess.PIPE)
    matte_cx = 0.5
    n0, n1 = int(round(T_START * FPS)), int(round(T_END * FPS))
    for n in range(n0, n1):
        t = n / FPS
        frame = src.at(t)
        m = mat.at(t)
        if frame is None or m is None:
            break
        mf = m[..., 0].astype(np.float32) / 255
        cols = mf.sum(axis=0)
        if cols.sum() > 50:
            matte_cx = 0.85 * matte_cx + 0.15 * float((cols * np.arange(MW)).sum() / cols.sum() / MW)
        z, cx, cy = camera(t, matte_cx)
        pic = grade(crop(frame, z, cx, cy, W, H))
        occ = crop(mf, z, cx, cy, W, H, cv2.INTER_LINEAR)

        insert = next((i for i in INSERTS if i[0] <= t < i[1]), None)
        if CARD[0] <= t < CARD[1]:
            draw_card(pic, t)
        elif insert:
            t_in, t_out, path, off, speed = insert
            r = readers.get(path)
            if r is None:
                r = readers[path] = Reader(path, W, H, 24)
            ct = off + (t - t_in) * speed
            img = r.at(ct)
            k = 1.0 + 0.05 * (1 - ease_out((t - t_in) / 0.35))       # small push on entry
            pic = crop(img, k, 0.5, 0.5, W, H, cv2.INTER_LINEAR).astype(np.float32) / 255
        else:
            graphics_behind(pic, t, occ)
        graphics_front(pic, t)
        end_card(pic, t)
        draw_caption(pic, chunks, t)
        enc.stdin.write((pic * 255).clip(0, 255).astype(np.uint8).tobytes())
        if n % 60 == 0:
            print(f"{t:6.2f}s", flush=True)
    enc.stdin.close()
    enc.wait()
    for r in [src, mat, *readers.values()]:
        r.close()
    print("done", OUT)


if __name__ == "__main__":
    main()
