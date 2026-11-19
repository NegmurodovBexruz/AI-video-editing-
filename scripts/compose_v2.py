"""Sklet x SPC edit, v2: more creative motion on top of the v1 helpers.

New in v2 (all time == source time):
  - pipe cross-section rings replace the letter O; letters rise through a baseline mask
  - iris reveal into the statue, x-ray scan reveal, brand pipe wipes between scenes
  - engineering ring drawing for 57 x 3 mm, fly-through-a-pipe exit from the morph
  - 4 200 pipe-end rings fill the yard behind the speaker, odometer counter
  - 50 km: camera runs along the brand pipe line, pulls back to show the marathon mark
  - tower shrinks aside while 30 statue silhouettes stack up
  - crash zoom on the question, impact shakes on the hits
"""
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compose as v1  # noqa: E402
from compose import (W, H, FPS, SW, SH, MW, MH, NAVY, OXIDE, MIST, WHITE, font, ease_out,  # noqa: E402
                     ease_in_out, clamp01, envelope, text_layer, over, place_text, grade, Reader,
                     crop, load_words, caption_chunks, draw_caption, LOGO)

P = v1.P
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else P / "out" / "sklet-v2-picture.mp4"
T_START = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
T_END = float(sys.argv[3]) if len(sys.argv) > 3 else 32.55
GEN = P / "gen" / "video"

C_NAVY = np.array(NAVY, np.float32) / 255
C_MIST = np.array(MIST, np.float32) / 255
C_OXIDE = np.array(OXIDE, np.float32) / 255
C_WHITE = np.array(WHITE, np.float32) / 255

F_HERO = font("sg_var", 200, 500)
F_HUGE = font("sg_var", 330, 500)
F_MID = font("sg_var", 120, 500)
F_LABEL = font("sg_var", 64, 500)
F_SMALL = font("sg_var", 44, 500)
F_XRAY = font("sg_var", 140, 500)
F_KM = font("sg_var", 300, 500)

# ---------------------------------------------------------------- drawing primitives


def paint(dst, alpha, color, opacity=1.0):
    """alpha: (H, W) float 0..1 coverage."""
    a = alpha[..., None] * opacity
    dst *= 1 - a
    dst += a * color


def stroke_canvas():
    return np.zeros((H, W), np.uint8)


def flush(dst, canvas, color, opacity=1.0):
    paint(dst, canvas.astype(np.float32) / 255, color, opacity)


def ring(canvas, cx, cy, r, gap, width=3, arc=360.0):
    """Brand pipe cross-section: two concentric circles (outer wall, inner wall)."""
    for rr in (r, r - gap):
        if rr <= 0:
            continue
        if arc >= 360:
            cv2.circle(canvas, (int(cx * 4), int(cy * 4)), int(rr * 4), 255, width, cv2.LINE_AA, 2)
        else:
            cv2.ellipse(canvas, (int(cx * 4), int(cy * 4)), (int(rr * 4), int(rr * 4)), -90, 0, arc,
                        255, width, cv2.LINE_AA, 2)


def shake(t):
    """Decaying camera kick after each hit, in pixels."""
    hits = [(2.84, 16), (15.90, 10), (19.46, 14), (26.24, 10), (30.90, 6)]
    dx = dy = 0.0
    for t0, amp in hits:
        if 0 <= t - t0 < 0.35:
            k = amp * math.exp(-(t - t0) * 14)
            dx += k * math.sin((t - t0) * 95)
            dy += k * math.cos((t - t0) * 77)
    return dx, dy


def shift(img, dx, dy):
    if abs(dx) < 0.5 and abs(dy) < 0.5:
        return img
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, m, (W, H), borderMode=cv2.BORDER_REPLICATE)


# ---------------------------------------------------------------- rising words with pipe-ring O


def rise_word(dst, text, fnt, cx, cy, t, t_in, t_out, fill=WHITE, tracking=6, stagger=0.035,
              occluder=None, ring_o=False, shadow=0.6, slam=False):
    """Letters rise through a mask at the baseline, one after another."""
    vis_all, _ = envelope(t, t_in, t_out, 0.01, 0.25)
    if vis_all <= 0:
        return
    asc, desc = fnt.getmetrics()
    widths = [fnt.getlength(ch) + tracking for ch in text]
    total = sum(widths) - tracking
    scale = 1.0
    if slam:
        scale = 1 + 0.22 * (1 - ease_out((t - t_in) / 0.18))
    x = cx - total * scale / 2
    top = int(cy - (asc + desc) / 2)
    clip_y0, clip_y1 = top - 10, int(top + asc + desc * 0.6)
    for i, (ch, w) in enumerate(zip(text, widths)):
        p = ease_out((t - t_in - i * stagger) / 0.32)
        if p <= 0:
            x += w * scale
            continue
        if ring_o and ch == "O":
            r = asc * 0.36 * scale
            ccx, ccy = x + (w - tracking) * scale / 2, top + asc * 0.62 + (1 - p) * asc
            c = stroke_canvas()
            ring(c, ccx, ccy, r, r * 0.2, 4, 360 * p)
            a = c.astype(np.float32) / 255
            if occluder is not None:
                a *= 1 - occluder
            paint(dst, a, np.array(fill, np.float32) / 255, vis_all)
            x += w * scale
            continue
        layer = text_layer(ch, fnt, fill, 0, shadow)
        if scale != 1.0:
            layer = cv2.resize(layer, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        lh, lw = layer.shape[:2]
        ly = int(cy - lh / 2 + (1 - p) * (asc + desc) * 0.9)
        lx = int(x - 40 * scale)
        # clip to the baseline window so letters emerge from a line
        y0 = max(ly, clip_y0)
        y1 = min(ly + lh, clip_y1 + int(desc))
        if y1 > y0:
            sub = layer[y0 - ly:y1 - ly]
            over(dst, sub, lx, y0, vis_all, occluder)
        x += w * scale


# ---------------------------------------------------------------- transitions


def iris_mask(cx, cy, r):
    yy, xx = np.ogrid[:H, :W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    return np.clip(r - d + 1, 0, 1).astype(np.float32)


def iris(dst_old, new, t, t0, dur=0.32, cx=W / 2, cy=H * 0.45):
    """Reveal `new` inside a growing pipe ring."""
    p = ease_in_out((t - t0) / dur)
    rmax = math.hypot(W, H)
    r = 40 + p * rmax
    m = iris_mask(cx, cy, r)[..., None]
    out = dst_old * (1 - m) + new * m
    c = stroke_canvas()
    ring(c, cx, cy, r + 26, 22, 3)
    flush(out, c, C_MIST, 1 - p * 0.6)
    return out


WIPE_LEN = 2500


def wipe(old, new, t, t0, dur=0.42):
    """A giant brand pipe (navy, two contour lines, rounded nose) slides up across the frame.
    Ahead of the nose the old scene stays, behind the tail the new one appears."""
    p = ease_in_out((t - t0) / dur)
    lead = H + 80 - p * (H + WIPE_LEN + 160)          # y of the rounded nose tip
    tail = lead + WIPE_LEN
    r = W / 2
    nose_c = lead + r
    yy, xx = np.ogrid[:H, :W]
    inside_nose = ((xx - W / 2) ** 2 + (yy - nose_c) ** 2) <= r * r
    ahead = (yy < nose_c) & ~inside_nose
    behind = np.broadcast_to(yy > tail, (H, W))
    out = np.empty_like(old)
    out[:] = C_NAVY
    out[ahead] = old[ahead]
    out[behind] = new[behind]
    c = stroke_canvas()
    for inset in (60, 120):
        rr = r - inset
        cv2.ellipse(c, (int(W / 2 * 4), int(nose_c * 4)), (int(rr * 4), int(rr * 4)), 0, 180, 360, 255, 3,
                    cv2.LINE_AA, 2)
        for x in (W / 2 - rr, W / 2 + rr):
            cv2.line(c, (int(x * 4), int(nose_c * 4)), (int(x * 4), int(tail * 4)), 255, 3, cv2.LINE_AA, 2)
    flush(out, c, C_MIST)
    return out


WIPES = [9.59, 23.01]                 # start = scene boundary - 0.21 s; 16.6 shrinks into the map instead


# ---------------------------------------------------------------- 57 x 3 engineering drawing


def pipe_drawing(dst, t, t_in=10.45, t_out=12.55):
    vis, _ = envelope(t, t_in, t_out, 0.2, 0.2)
    if vis <= 0:
        return
    cx, cy, r = W / 2, 900, 230
    gap = r * 3 / 28.5                         # wall 3 mm on a 57 mm diameter
    disk = iris_mask(cx, cy, r + 60)
    paint(dst, disk, C_NAVY, 0.86 * vis)
    c = stroke_canvas()
    ring(c, cx, cy, r, gap, 4, 360 * ease_out((t - t_in) / 0.6))
    p_dim = ease_out((t - t_in - 0.5) / 0.4)
    if p_dim > 0:
        x0, x1 = cx - r, cx - r + 2 * r * p_dim
        y = cy + r + 34
        cv2.line(c, (int(x0 * 4), int(y * 4)), (int(x1 * 4), int(y * 4)), 255, 2, cv2.LINE_AA, 2)
        for xe in (cx - r, cx + r):
            cv2.line(c, (int(xe * 4), int((cy + 10) * 4)), (int(xe * 4), int((y + 14) * 4)), 255, 2,
                     cv2.LINE_AA, 2)
    flush(dst, c, C_MIST, vis)
    place_text(dst, "Ø 57 mm", F_LABEL, cx, cy - 30, t, t_in + 0.6, t_out, fill=WHITE, shadow=0.0)
    place_text(dst, "devor 3 mm", F_SMALL, cx, cy + 60, t, t_in + 1.0, t_out, fill=MIST, shadow=0.0)
    if t >= t_in + 1.0:
        c2 = stroke_canvas()
        cv2.line(c2, (int((cx + r - gap / 2) * 4), int((cy - 40) * 4)), (int((cx + r + 70) * 4), int((cy - 150) * 4)),
                 255, 2, cv2.LINE_AA, 2)
        flush(dst, c2, C_OXIDE, vis)
        place_text(dst, "3", F_LABEL, cx + r + 95, cy - 175, t, t_in + 1.0, t_out, fill=OXIDE, shadow=0.0, slide=0)


# ---------------------------------------------------------------- 4 200 rings + odometer

def ring_grid():
    pts, r, sx = [], 9, 22
    sy = sx * math.sqrt(3) / 2
    row = 0
    y = H - 20
    while y > 60:
        off = sx / 2 if row % 2 else 0
        x = 16 + off
        while x < W - 10:
            pts.append((x, y))
            x += sx
        y -= sy
        row += 1
    pts = np.array(pts, np.float32)
    order = np.argsort(np.hypot(pts[:, 0] - W / 2, (pts[:, 1] - H) * 0.7))
    return pts[order][:4200]


RINGS = ring_grid()


def rings_behind(dst, t, occ):
    if not (13.35 <= t < 16.42):
        return
    vis, _ = envelope(t, 13.35, 16.42, 0.4, 0.2)
    paint(dst, 1 - occ, C_NAVY, 0.58 * vis)
    n = int(len(RINGS) * ease_in_out((t - 14.66) / (15.90 - 14.66)))
    if n > 0:
        c = stroke_canvas()
        for x, y in RINGS[:n]:
            cv2.circle(c, (int(x * 4), int(y * 4)), 36, 255, 1, cv2.LINE_AA, 2)
        a = c.astype(np.float32) / 255 * (1 - occ)
        paint(dst, a, C_MIST, 0.75 * vis)


def odometer(dst, value, cx, cy, fnt, vis, occ=None, fill=WHITE):
    """Rolling digits: each column scrolls like a mechanical counter, clipped to one window."""
    digits = 4
    gx0, gy0, gx1, gy1 = fnt.getbbox("0")
    glyph_h = gy1 - gy0
    step = glyph_h * 1.3
    pad = 40                                    # text_layer padding
    centre_in_layer = pad + (gy0 + gy1) / 2
    win0, win1 = int(cy - step / 2), int(cy + step / 2)
    dw = fnt.getlength("0")
    gapw = dw * 0.3
    x = cx - (digits * dw + gapw) / 2
    for i in range(digits):
        place = 10 ** (digits - 1 - i)
        d = (value / place) % 10
        lo = int(d)
        frac = d - lo if i == digits - 1 else ease_in_out((d - lo - 0.75) / 0.25)   # upper columns flip late
        show_lo = value >= place or i == digits - 1
        for k, dig in ((0, lo), (1, (lo + 1) % 10)):
            if k == 0 and not show_lo:
                continue
            layer = text_layer(str(dig), fnt, fill, 0, 0.6)
            yy = int(cy - centre_in_layer - frac * step + k * step)
            y0, y1 = max(yy, win0), min(yy + layer.shape[0], win1)
            if y1 > y0:
                over(dst, layer[y0 - yy:y1 - yy], int(x - pad), y0, vis, occ)
        x += dw + (gapw if i == 0 else 0)


# ---------------------------------------------------------------- 50 km card

ROWS, ROW_GAP, TURN_R, XL, XR = 14, 250, 125, 150, 930


def world_snake():
    pts = [(x, 300) for x in np.linspace(-120, XR, 60)]
    for i in range(ROWS - 1):
        y0 = 300 + i * ROW_GAP
        cy = y0 + ROW_GAP / 2
        right = i % 2 == 0
        cxx = XR if right else XL
        for a in np.linspace(-math.pi / 2, math.pi / 2, 36):
            pts.append((cxx + (TURN_R * math.cos(a) if right else -TURN_R * math.cos(a)), cy + TURN_R * math.sin(a)))
        xs = np.linspace(XR, XL, 50) if right else np.linspace(XL, XR, 50)
        pts += [(x, y0 + ROW_GAP) for x in xs]
    return np.array(pts, np.float32)


SNAKE = world_snake()
SEG = np.r_[0, np.cumsum(np.hypot(*np.diff(SNAKE, axis=0).T))]
SN_A, SN_B = v1.offset_path(SNAKE, 26), v1.offset_path(SNAKE, -26)
WORLD_H = 300 + (ROWS - 1) * ROW_GAP + 300
MARATHON = 42.195 / 50


def point_at(s):
    i = int(np.clip(np.searchsorted(SEG, s), 1, len(SEG) - 1))
    f = (s - SEG[i - 1]) / max(SEG[i] - SEG[i - 1], 1e-6)
    return SNAKE[i - 1] + (SNAKE[i] - SNAKE[i - 1]) * f, i


def draw_card(t):
    dst = np.empty((H, W, 3), np.float32)
    dst[:] = C_NAVY
    prog = ease_in_out((t - 16.74) / (19.46 - 16.74))
    s_head = prog * SEG[-1]
    head, n = point_at(s_head)
    # camera: follow the head, then pull back to the whole run
    follow_y = max(H * 0.42, head[1])
    pull = ease_in_out((t - 20.30) / 0.8)
    fit = 680 / WORLD_H                         # whole run fits above the counter plate
    scale = 1 + (fit - 1) * pull
    cam_y = follow_y + (WORLD_H / 2 - follow_y) * pull
    cam_x = W / 2
    anchor_y = H * 0.44 + (600 - H * 0.44) * pull

    def tr(p):
        return (p - np.array([cam_x, cam_y])) * scale + np.array([W / 2, anchor_y])

    c = stroke_canvas()
    for path in (SN_A, SN_B):
        pts = tr(path[:n])
        cv2.polylines(c, [np.round(pts * 4).astype(np.int32)], False, 255, 3, cv2.LINE_AA, 2)
    flush(dst, c, C_MIST)
    # extra length beyond the marathon mark, in oxide
    if t >= 21.6:
        k = ease_out((t - 21.6) / 0.6)
        s0 = MARATHON * SEG[-1]
        i0 = int(np.searchsorted(SEG, s0))
        i1 = int(np.searchsorted(SEG, s0 + (SEG[-1] - s0) * k))
        if i1 > i0 + 1:
            c2 = stroke_canvas()
            pts = tr(SNAKE[i0:i1])
            cv2.polylines(c2, [np.round(pts * 4).astype(np.int32)], False, 255, max(3, int(40 * scale)),
                          cv2.LINE_AA, 2)
            flush(dst, c2, C_OXIDE, 0.85)
    # marathon mark
    if t >= 20.9:
        mk, _ = point_at(MARATHON * SEG[-1])
        p = tr(mk)
        v = ease_out((t - 20.9) / 0.35)
        lx = 700
        c3 = stroke_canvas()
        cv2.circle(c3, (int(p[0] * 4), int(p[1] * 4)), 36, 255, -1, cv2.LINE_AA, 2)
        cv2.line(c3, (int(p[0] * 4), int(p[1] * 4)), (int((p[0] + (lx - 20 - p[0]) * v) * 4), int(p[1] * 4)), 255, 3,
                 cv2.LINE_AA, 2)
        flush(dst, c3, C_WHITE)
        place_text(dst, "MARAFON", F_SMALL, lx + 130, p[1] - 28, t, 21.05, 99, fill=WHITE, shadow=0, slide=10)
        place_text(dst, "42,2 km", F_SMALL, lx + 120, p[1] + 28, t, 21.15, 99, fill=MIST, shadow=0, slide=10)
    # head glow
    if t < 20.4:
        hp = tr(head)
        paint(dst, iris_mask(hp[0], hp[1], 34) * 0.35, C_OXIDE)
        paint(dst, iris_mask(hp[0], hp[1], 12), C_OXIDE)
    # counters, on a navy plate so the line never runs through the digits
    place_text(dst, "4 200 × 12 m", F_LABEL, W / 2, 170, t, 16.74, 20.4, fill=MIST, tracking=6, shadow=0)
    km = 50 * prog
    vis_km, _ = envelope(t, 17.0, 99, 0.3, 0.1)
    if vis_km > 0:
        v1.panel(dst, 90, 960, 990, 1370, opacity=0.9 * vis_km)
        layer = text_layer(f"{km:4.1f}".replace(".", ",") if km < 49.95 else "50", F_KM, WHITE, 0, 0.0)
        lh, lw = layer.shape[:2]
        over(dst, layer, int(W / 2 - lw / 2 - 70), int(1130 - lh / 2), vis_km)
        place_text(dst, "KM", F_LABEL, W / 2 + lw / 2 - 20, 1180, t, 17.0, 99, fill=MIST, shadow=0, slide=0)
    place_text(dst, "+7,8 km", F_LABEL, W / 2, 1320, t, 21.7, 99, fill=OXIDE, shadow=0)
    return dst


# ---------------------------------------------------------------- 50 km on the real map (OSM, brand style)

import osm_map as MAP  # noqa: E402

C_WATER = np.array((70, 120, 150), np.float32) / 255
PPK0, PPK1 = 90.0, 26.0                      # px per km: plant close-up -> whole run
CAM1 = np.array([MAP.CENTRE_KM[0] / 2, MAP.CENTRE_KM[1] + 15.38])   # Tashkent lands at y~560
F_PLACE = font("sg_var", 30, 400)
MAP_LABELS = ["Olmaliq", "Nurafshon", "Qibray", "Parkent", "Yangibozor", "Piskent"]


def map_camera(t):
    z = ease_out((t - 16.95) / 2.1)              # pull back early so the pipe head stays in frame
    ppk = math.exp(math.log(PPK0) + (math.log(PPK1) - math.log(PPK0)) * z)
    ppk *= 1 + 0.06 * ease_in_out((t - 19.6) / 3.6)                     # slow drift in afterwards
    cam = CAM1 * z
    return cam, ppk


def map_scene(t, footage):
    cam, ppk = map_camera(t)
    dst = MAP.render(W, H, cam[0], cam[1], ppk, C_NAVY, C_MIST, C_WATER)
    scr = lambda p: MAP.to_screen(p, W, H, cam[0], cam[1], ppk)       # noqa: E731
    plant = scr((0.0, 0.0))
    # route drawn as a brand pipe (two white walls) with an oxide head
    frac = ease_in_out((t - 17.2) / (19.46 - 17.2))
    if frac > 0:
        head, n = MAP.route_point(frac)
        pts = np.vstack([MAP.ROUTE[:n], head[None]])
        sp = scr(pts)
        c = stroke_canvas()
        for d in (4.5, -4.5):
            cv2.polylines(c, [np.round(v1.offset_path(sp, d) * 4).astype(np.int32)], False, 255, 2, cv2.LINE_AA, 2)
        flush(dst, c, C_WHITE)
        if t >= 21.6:                                                    # the 7.8 km beyond the marathon
            k = ease_out((t - 21.6) / 0.6)
            m0 = MAP.route_point(MARATHON)[1]
            m1 = MAP.route_point(MARATHON + (1 - MARATHON) * k)[1]
            if m1 > m0 + 1:
                c2 = stroke_canvas()
                cv2.polylines(c2, [np.round(scr(MAP.ROUTE[m0:m1]) * 4).astype(np.int32)], False, 255, 9,
                              cv2.LINE_AA, 2)
                flush(dst, c2, C_OXIDE, 0.95)
        hp = scr(head)
        if frac < 1:
            paint(dst, iris_mask(hp[0], hp[1], 26) * 0.35, C_OXIDE)
            paint(dst, iris_mask(hp[0], hp[1], 9), C_OXIDE)
        else:                                                            # arrival pulse
            k = clamp01((t - 19.46) / 0.6)
            c3 = stroke_canvas()
            ring(c3, hp[0], hp[1], 14 + 80 * ease_out(k), 10, 3)
            flush(dst, c3, C_OXIDE, 1 - k)
            paint(dst, iris_mask(hp[0], hp[1], 10), C_OXIDE)
    # place names
    for name, x, y, kind in MAP.PLACES:
        if name in MAP_LABELS:
            p = scr((x, y))
            if 40 < p[0] < W - 40 and 120 < p[1] < H - 300:
                place_text(dst, name, F_PLACE, p[0], p[1], t, 18.0, 99, fill=MIST, shadow=0, slide=0)
    tk = scr(MAP.CENTRE_KM)
    place_text(dst, "TOSHKENT", F_LABEL, min(max(tk[0] + 40, 200), W - 200), tk[1] + 70, t, 19.0, 99, fill=WHITE,
               tracking=6, shadow=0.0, slide=12)
    # plant pin + label
    pin_vis, _ = envelope(t, 17.15, 99, 0.25, 0.1)
    if pin_vis > 0:
        paint(dst, iris_mask(plant[0], plant[1], 12), C_WHITE, pin_vis)
        c4 = stroke_canvas()
        ring(c4, plant[0], plant[1], 26, 8, 3)
        flush(dst, c4, C_WHITE, pin_vis)
        place_text(dst, "SPC ZAVODI", F_SMALL, plant[0] - 40, plant[1] + 64, t, 17.25, 99, fill=WHITE, shadow=0)
        place_text(dst, "Ohangaron", F_PLACE, plant[0] - 40, plant[1] + 108, t, 17.35, 99, fill=MIST, shadow=0)
    # marathon mark
    if t >= 20.9:
        mk, _ = MAP.route_point(MARATHON)
        p = scr(mk)
        v = ease_out((t - 20.9) / 0.35)
        lx = p[0] + 140
        c5 = stroke_canvas()
        cv2.circle(c5, (int(p[0] * 4), int(p[1] * 4)), 40, 255, -1, cv2.LINE_AA, 2)
        cv2.line(c5, (int(p[0] * 4), int(p[1] * 4)), (int((p[0] + 120 * v) * 4), int(p[1] * 4)), 255, 3, cv2.LINE_AA, 2)
        flush(dst, c5, C_WHITE)
        place_text(dst, "MARAFON", F_SMALL, lx + 95, p[1] - 26, t, 21.05, 99, fill=WHITE, shadow=0.0, slide=10)
        place_text(dst, "42,2 km", F_SMALL, lx + 85, p[1] + 26, t, 21.15, 99, fill=MIST, shadow=0.0, slide=10)
    # counter plate (top)
    vis_km, _ = envelope(t, 17.2, 99, 0.3, 0.1)
    if vis_km > 0:
        v1.panel(dst, 250, 130, 830, 500, opacity=0.9 * vis_km)
        km = 50 * frac
        layer = text_layer(f"{km:4.1f}".replace(".", ",") if km < 49.95 else "50", F_KM, WHITE, 0, 0.0)
        lh, lw = layer.shape[:2]
        over(dst, layer, int(W / 2 - lw / 2 - 60), int(280 - lh / 2), vis_km)
        place_text(dst, "KM", F_LABEL, W / 2 + lw / 2 - 10, 330, t, 17.2, 99, fill=MIST, shadow=0, slide=0)
        place_text(dst, "+7,8 km", F_LABEL, W / 2, 455, t, 21.7, 99, fill=OXIDE, shadow=0, slide=0)
    place_text(dst, "© OpenStreetMap", F_PLACE, W - 150, H - 40, t, 16.6, 99, fill=MIST, shadow=0, slide=0)
    # the speaker shot shrinks into the plant pin
    e = ease_in_out((t - 16.60) / 0.55)
    if e < 1:
        s = 1 - e * 0.97
        fw, fh = max(2, int(W * s)), max(2, int(H * s))
        small = cv2.resize(footage, (fw, fh), interpolation=cv2.INTER_AREA)
        cxp = W / 2 + (plant[0] - W / 2) * e
        cyp = H / 2 + (plant[1] - H / 2) * e
        x0, y0 = int(cxp - fw / 2), int(cyp - fh / 2)
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + fw), min(H, y0 + fh)
        if xb > xa and yb > ya:
            dst[ya:yb, xa:xb] = small[ya - y0:yb - y0, xa - x0:xb - x0]
            c6 = stroke_canvas()
            cv2.rectangle(c6, (xa * 4, ya * 4), ((xb - 1) * 4, (yb - 1) * 4), 255, 4, cv2.LINE_AA, 2)
            flush(dst, c6, C_WHITE, e)
    return dst


# ---------------------------------------------------------------- tower + 30 statues

SIL = np.asarray(Image.open(P / "assets" / "statue-silhouette.png"), np.float32) / 255
SIL_H = 128
SIL_ICON = cv2.resize(SIL, (int(SIL.shape[1] * SIL_H / SIL.shape[0]), SIL_H), interpolation=cv2.INTER_AREA)


def tower_scene(frame, t):
    """frame: tower insert (H, W, 3). Shrinks left while 30 silhouettes fill the right."""
    k = ease_in_out((t - 24.45) / 0.55)
    if k <= 0:
        return frame
    out = np.empty_like(frame)
    out[:] = C_NAVY
    s = 1 - 0.42 * k
    small = cv2.resize(frame, (int(W * s), int(H * s)), interpolation=cv2.INTER_AREA)
    x0 = int((W - W * s) / 2 * (1 - k) + 40 * k)
    y0 = int((H - H * s) / 2)
    out[y0:y0 + small.shape[0], x0:x0 + small.shape[1]] = small
    # 30 statues: 5 columns x 6 rows on the right
    cols, rows = 5, 6
    gx0, gy0, gw = 700, 570, 72
    for i in range(30):
        appear = 25.18 + i * (26.24 - 25.18) / 29
        p = ease_out((t - appear) / 0.18)
        if p <= 0:
            continue
        r, cidx = divmod(i, cols)
        x = int(gx0 + cidx * gw - SIL_ICON.shape[1] / 2)
        y = int(gy0 + (rows - 1 - r) * (SIL_H + 8) + (1 - p) * 30)
        a = SIL_ICON * p
        hh, ww = a.shape
        region = out[y:y + hh, x:x + ww]
        region *= 1 - a[..., None]
        region += a[..., None] * C_MIST
    return out


# ---------------------------------------------------------------- scene graph

def camera(t, matte_cx):
    if t < 2.07:
        return 1.0 + 0.06 * ease_in_out(t / 2.07), 0.5, 0.5
    if t < 23.22:
        if 7.74 <= t < 9.80:
            return 1.30 + 0.06 * ease_in_out((t - 7.74) / 2.06), 0.48, 0.40
        return 1.0, 0.5, 0.5
    if t < 28.92:
        if t >= 28.06:
            return 1.0 + 0.55 * ease_out((t - 28.06) / 0.16), matte_cx, 0.40
        return 1.0 + 0.08 * ease_in_out((t - 26.7) / 1.4) if t > 26.7 else 1.0, 0.5, 0.5
    return 1.0 + 0.04 * ease_in_out((t - 28.92) / 3.6), 0.5, 0.45


class Clips:
    def __init__(self):
        self.r = {}

    def at(self, name, ct):
        path = GEN / name
        r = self.r.get(name)
        if r is None or ct * 24 < r.idx - 1:
            r = self.r[name] = Reader(path, W, H, 24)
        img = r.at(ct)
        return img.astype(np.float32) / 255

    def close(self):
        for r in self.r.values():
            r.close()


def scene(t, footage, occ, clips):
    """Base picture for time t before captions/end card."""
    # statue hero, entered through an iris
    if 1.20 <= t < 2.75:
        img = clips.at("v0_statue.mp4", 1.0 + (t - 1.20))
        if t < 1.52:
            return iris(footage, img, t, 1.20)
        return img
    # x-ray with scanner reveal
    if 3.74 <= t < 7.74:
        img = clips.at("v1_xray.mp4", 0.5 + (t - 3.74))
        p = ease_in_out((t - 3.74) / 0.7)
        if p < 1:
            line_y = int(H * (1 - p))
            out = img.copy()
            out[:line_y] = C_NAVY
            glow = np.exp(-((np.arange(H) - line_y) / 14.0) ** 2).astype(np.float32)[:, None]
            paint(out, np.repeat(glow, W, 1), C_MIST, 0.9)
            return out
        return img
    # morph (entered by wipe), exits by flying into a pipe end
    if 9.80 <= t < 13.20:
        if t < 12.94:
            ct = 0.9 + (t - 9.80) * 1.28
            img = clips.at("v2_morph.mp4", ct)
            if t >= 12.62:
                z = 1 + 4 * ease_in_out((t - 12.62) / 0.32) ** 2
                img = crop(img, z, 0.5, 0.53, W, H, cv2.INTER_LINEAR)
            return img
        dark = np.zeros((H, W, 3), np.float32)
        dark[:] = C_NAVY * 0.3
        return iris(dark, footage, t, 12.94, 0.26, W / 2, H * 0.4)
    if 16.60 <= t < 23.22:
        return map_scene(t, footage)
    if 23.22 <= t < 26.70:
        return tower_scene(clips.at("v3_tower.mp4", 0.6 + (t - 23.22)), t)
    return footage


def scene_with_wipes(t, footage, occ, clips):
    for t0 in WIPES:
        if t0 <= t < t0 + 0.42:
            mid = t0 + 0.21
            old = scene(min(t, mid - 1e-3), footage, occ, clips)
            new = scene(max(t, mid), footage, occ, clips)
            return wipe(old, new, t, t0), True
    return scene(t, footage, occ, clips), False


def behind_layers(pic, t, occ):
    rise_word(pic, "OZODLIK", F_HERO, W / 2, 600, t, 0.16, 1.20, occluder=occ, ring_o=True)
    rise_word(pic, "HAYKALI", F_HERO, W / 2, 810, t, 0.68, 1.20, occluder=occ)
    rise_word(pic, "200", F_HUGE, W / 2, 380, t, 2.84, 3.74, occluder=occ, slam=True, stagger=0.0)
    rise_word(pic, "TONNA", F_MID, W / 2, 640, t, 3.12, 3.74, occluder=occ, tracking=18)
    rings_behind(pic, t, occ)
    if 14.12 <= t < 16.42:
        vis, _ = envelope(t, 14.12, 16.42, 0.3, 0.2)
        n = 4200 * ease_in_out((t - 14.66) / (15.90 - 14.66))
        odometer(pic, n, W / 2, 400, F_HUGE, vis, occ)
        place_text(pic, "12 METRLIK QUVUR", F_LABEL, W / 2, 175, t, 14.12, 16.42, fill=MIST, tracking=6)


def front_layers(pic, t):
    # x-ray labels
    if 3.74 <= t < 7.74:
        place_text(pic, "30 t", F_XRAY, 160, 800, t, 4.12, 7.74, shadow=0.0, slide=20)
        place_text(pic, "MIS QOBIQ", F_SMALL, 160, 890, t, 4.34, 7.74, fill=OXIDE, tracking=4, shadow=0.0, slide=20)
        if t >= 4.34:
            v1.leader(pic, (250, 940), (390, 1010), ease_out((t - 4.34) / 0.35) * envelope(t, 4.34, 7.74)[0], OXIDE)
        place_text(pic, "TEMIR", F_SMALL, 925, 1270, t, 6.60, 7.74, tracking=4, shadow=0.0, slide=20)
        place_text(pic, "KARKAS", F_SMALL, 925, 1320, t, 6.70, 7.74, tracking=4, shadow=0.0, slide=20)
        if t >= 6.70:
            v1.leader(pic, (835, 1295), (580, 1295), ease_out((t - 6.70) / 0.3) * envelope(t, 6.70, 7.74)[0], WHITE)
    pipe_drawing(pic, t)
    # tower titles
    rise_word(pic, "TOSHKENT", F_MID, W / 2, 1120, t, 23.40, 24.40, tracking=10)
    rise_word(pic, "TELEMINORASI", F_LABEL, W / 2, 1230, t, 23.70, 24.40, fill=MIST, tracking=10, stagger=0.02)
    if 24.9 <= t < 26.70:
        place_text(pic, "og‘irligi ≈", F_SMALL, 845, 400, t, 24.90, 26.70, fill=MIST, shadow=0)
        place_text(pic, "× 30", F_MID, 845, 490, t, 26.24, 26.70, fill=WHITE, shadow=0)
    # question
    rise_word(pic, "TASAVVUR", F_MID, W / 2, 260, t, 28.06, 28.92, fill=NAVY, tracking=8, shadow=0.0)
    rise_word(pic, "QILAYAPSIZMI?", F_MID, W / 2, 400, t, 28.38, 28.92, fill=NAVY, tracking=4, shadow=0.0,
              stagger=0.02)


def end_card(pic, t):
    vis, p_in = envelope(t, 30.90, 99, 0.6, 0.1)
    if vis <= 0:
        return
    grad = np.linspace(1, 0, 900, dtype=np.float32)[:, None, None] ** 1.4 * 0.88 * vis
    pic[:900] = pic[:900] * (1 - grad) + C_WHITE * grad
    lh, lw = LOGO.shape[:2]
    over(pic, LOGO, (W - lw) // 2, 220 + int((1 - p_in) * 30), vis)
    rise_word(pic, "ISHONCH SINOVDAN BOSHLANADI", F_SMALL, W / 2, 560, t, 31.30, 99, fill=NAVY, tracking=6,
              shadow=0.0, stagger=0.018)
    p = ease_out((t - 31.6) / 0.7)
    if p > 0:
        c = stroke_canvas()
        x0, x1 = 160, 160 + (W - 320) * p
        for y in (610, 632):
            cv2.line(c, (int(x0 * 4), y * 4), (int(x1 * 4), y * 4), 255, 3, cv2.LINE_AA, 2)
        flush(pic, c, C_NAVY, vis)


# ---------------------------------------------------------------- main

def main():
    chunks = caption_chunks(load_words())
    src = Reader(v1.SRC, SW, SH, FPS)
    mat = Reader(P / "work" / "matte.mp4", MW, MH, FPS, fmt="gray")
    clips = Clips()
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(OUT)], stdin=subprocess.PIPE)
    matte_cx = 0.5
    for n in range(int(round(T_START * FPS)), int(round(T_END * FPS))):
        t = n / FPS
        frame, m = src.at(t), mat.at(t)
        if frame is None or m is None:
            break
        mf = m[..., 0].astype(np.float32) / 255
        cols = mf.sum(axis=0)
        if cols.sum() > 50:
            matte_cx = 0.85 * matte_cx + 0.15 * float((cols * np.arange(MW)).sum() / cols.sum() / MW)
        z, cx, cy = camera(t, matte_cx)
        footage = grade(crop(frame, z, cx, cy, W, H))
        occ = crop(mf, z, cx, cy, W, H, cv2.INTER_LINEAR)
        pic, wiping = scene_with_wipes(t, footage, occ, clips)
        if pic is footage:
            behind_layers(pic, t, occ)
        if not wiping:
            front_layers(pic, t)
        end_card(pic, t)
        draw_caption(pic, chunks, t)
        pic = shift(pic, *shake(t))
        enc.stdin.write((pic * 255).clip(0, 255).astype(np.uint8).tobytes())
        if n % 90 == 0:
            print(f"{t:6.2f}s", flush=True)
    enc.stdin.close()
    enc.wait()
    src.close()
    mat.close()
    clips.close()
    print("done", OUT)


if __name__ == "__main__":
    main()
