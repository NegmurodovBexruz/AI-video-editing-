"""Frame geometry: working copy -> 1080x1920 output (cover crop around the head), digital zoom, camera curves."""
import math

import numpy as np


class View:
    """Maps normalised working-copy coordinates to output pixels.

    base: the working copy is scaled to cover the output (K) and cropped around the head's median x.
    zoom: scale s about the screen-normalised anchor (ax, ay).
    """

    def __init__(self, out_w, out_h, src_w, src_h, cx=0.5, cy=0.5):
        self.W, self.H, self.sw, self.sh = out_w, out_h, src_w, src_h
        self.K = max(out_w / src_w, out_h / src_h)
        vw, vh = out_w / self.K, out_h / self.K
        self.ox = min(max(cx * src_w - vw / 2, 0), src_w - vw)
        self.oy = min(max(cy * src_h - vh / 2, 0), src_h - vh)

    def base(self, xn, yn):
        """Normalised source -> output px at zoom 1."""
        return (xn * self.sw - self.ox) * self.K, (yn * self.sh - self.oy) * self.K

    def screen(self, xn, yn, s, ax, ay):
        bx, by = self.base(xn, yn)
        return self.W * ax + (bx - self.W * ax) * s, self.H * ay + (by - self.H * ay) * s

    def px(self, wn):
        """Normalised source width -> output px at zoom 1."""
        return wn * self.sw * self.K

    def matrix(self, plate_w, plate_h, s, ax, ay):
        """2x3 affine for cv2.warpAffine of a plate (working copy or matte at its own size)."""
        k = self.K * self.sw / plate_w
        ky = self.K * self.sh / plate_h
        oxp, oyp = self.ox * plate_w / self.sw, self.oy * plate_h / self.sh
        A, B = self.W * ax, self.H * ay
        return np.float32([[s * k, 0, A * (1 - s) - s * k * oxp],
                           [0, s * ky, B * (1 - s) - s * ky * oyp]])


def ease(kind, p):
    p = min(1.0, max(0.0, p))
    if kind == "out":
        return 1 - (1 - p) ** 3
    if kind == "in":
        return p ** 2.2
    if kind == "inout":
        return 3 * p * p - 2 * p * p * p
    return p


def scale_curve(n, fps, events, start_scale=1.0, setup_frames=()):
    """events: [{"t": s, "frames": n, "scale": target, "ease": out|in|inout|lin}] -> per-frame scale.
    A set-up cut resets the scale to 1.0 and drops any move still running."""
    fv = lambda t: int(math.floor(t * fps)) + 1 if t > 0 else 0
    keys = sorted(((fv(e["t"]), int(e.get("frames", 6)), float(e["scale"]), e.get("ease", "out")) for e in events))
    cuts = set(setup_frames)
    scale, s_cur, seg, ki = [1.0] * n, float(start_scale), None, 0
    for f in range(n):
        if f in cuts:
            s_cur, seg = 1.0, None
        while ki < len(keys) and keys[ki][0] <= f:
            f0, k, s1, e = keys[ki]
            seg = (f0, max(1, k), s_cur, s1, e)
            ki += 1
        if seg:
            f0, k, sa, sb, e = seg
            p = (f - f0 + 1) / k if e != "lin" else (f - f0) / k
            s_cur = sa + (sb - sa) * ease(e, p)
            if f - f0 + 1 >= k:
                s_cur, seg = sb, None
        scale[f] = round(s_cur, 5)
    return scale


def anchors(scale, track, view, setup_frames=()):
    """Zoom anchor = the head's screen position when the scale leaves 1.0 (or at a set-up cut), held until 1.0."""
    cuts = set(setup_frames)
    out, cur = [], None
    for f, s in enumerate(scale):
        if s <= 1.0001 or f in cuts:
            cur = None
        if cur is None and s > 1.0001:
            bx, by = view.base(track["hx"][f], track["hy"][f])
            cur = (bx / view.W, by / view.H)
        out.append(cur if cur else (0.5, 0.5))
    return out
