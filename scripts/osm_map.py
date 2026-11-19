"""Brand-styled map of the Akhangaran -> Tashkent area from OpenStreetMap data.

Coordinates are km relative to the SPC plant (x east, y south), equirectangular.
Map data (c) OpenStreetMap contributors, ODbL.
"""
import json
import math
from pathlib import Path

import cv2
import numpy as np

P = Path(__file__).resolve().parent.parent
PLANT = (40.9155, 69.6503)          # SPC, SEZ Angren, Akhangaran (approx.)
CENTRE = (41.3111, 69.2797)         # Tashkent, Amir Temur square (approx.)
KX = 111.32 * math.cos(math.radians(41.1))
KY = 110.57


def to_km(lat, lon):
    return (lon - PLANT[1]) * KX, -(lat - PLANT[0]) * KY


CLASSES = {"trunk": 0, "primary": 1, "secondary": 2, "tertiary": 3, "river": 4, "canal": 5}


def load():
    cache = P / "work" / "osm" / "map.npz"
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        return list(z["lines"]), list(z["cls"]), list(z["places"])
    d = json.loads((P / "work" / "osm" / "osm.json").read_text(encoding="utf-8"))
    lines, cls, places = [], [], []
    for e in d["elements"]:
        if e["type"] == "way":
            k = e["tags"].get("highway") or e["tags"].get("waterway")
            g = e.get("geometry") or []
            if k in CLASSES and len(g) > 1:
                lines.append(np.array([to_km(p["lat"], p["lon"]) for p in g], np.float32))
                cls.append(CLASSES[k])
        elif e["type"] == "node":
            t = e["tags"]
            name = t.get("name:uz") or t.get("name")
            if name:
                places.append((name.split(" (")[0], *to_km(e["lat"], e["lon"]), t.get("place")))
    np.savez(cache, lines=np.array(lines, dtype=object), cls=np.array(cls), places=np.array(places, dtype=object))
    return lines, cls, places


LINES, CLS, PLACES = load()
CLS = np.array(CLS)
BOUNDS = [(l[:, 0].min(), l[:, 1].min(), l[:, 0].max(), l[:, 1].max()) for l in LINES]
CENTRE_KM = to_km(*CENTRE)


def pipe_route():
    """Gently curved route plant -> centre (quadratic Bezier)."""
    p0 = np.array([0.0, 0.0])
    p2 = np.array(CENTRE_KM)
    mid = (p0 + p2) / 2
    normal = np.array([-(p2 - p0)[1], (p2 - p0)[0]])
    normal /= np.linalg.norm(normal)
    p1 = mid + normal * 4.0
    s = np.linspace(0, 1, 400)[:, None]
    pts = (1 - s) ** 2 * p0 + 2 * (1 - s) * s * p1 + s ** 2 * p2
    return pts.astype(np.float32)


ROUTE = pipe_route()
ROUTE_SEG = np.r_[0, np.cumsum(np.hypot(*np.diff(ROUTE, axis=0).T))]


def route_point(frac):
    s = frac * ROUTE_SEG[-1]
    i = int(np.clip(np.searchsorted(ROUTE_SEG, s), 1, len(ROUTE) - 1))
    f = (s - ROUTE_SEG[i - 1]) / max(ROUTE_SEG[i] - ROUTE_SEG[i - 1], 1e-6)
    return ROUTE[i - 1] + (ROUTE[i] - ROUTE[i - 1]) * f, i


STYLE = {   # class: (min px/km to draw, alpha, width)
    0: (0, 0.85, 3), 1: (0, 0.55, 2), 2: (6, 0.38, 1), 3: (30, 0.30, 1), 4: (0, 0.55, 2), 5: (8, 0.30, 1),
}


def render(w, h, cx, cy, ppk, navy, mist, water):
    """Draw the map: centre (cx, cy) km, ppk pixels per km. Returns float RGB."""
    out = np.empty((h, w, 3), np.float32)
    out[:] = navy
    half_w, half_h = w / 2 / ppk, h / 2 / ppk
    x0, x1, y0, y1 = cx - half_w, cx + half_w, cy - half_h, cy + half_h
    layers = {}
    for line, c, (bx0, by0, bx1, by1) in zip(LINES, CLS, BOUNDS):
        min_ppk, alpha, width = STYLE[c]
        if ppk < min_ppk or bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
            continue
        key = (alpha, width, c >= 4)
        layers.setdefault(key, []).append(np.round(((line - (cx, cy)) * ppk + (w / 2, h / 2)) * 4).astype(np.int32))
    for (alpha, width, is_water), polys in sorted(layers.items(), key=lambda kv: kv[0][2], reverse=True):
        canvas = np.zeros((h, w), np.uint8)
        cv2.polylines(canvas, polys, False, 255, width, cv2.LINE_AA, 2)
        a = canvas.astype(np.float32)[..., None] / 255 * alpha
        col = water if is_water else mist
        out *= 1 - a
        out += a * col
    return out


def to_screen(p, w, h, cx, cy, ppk):
    return (np.asarray(p) - (cx, cy)) * ppk + (w / 2, h / 2)


if __name__ == "__main__":
    from PIL import Image
    navy = np.array((18, 42, 57), np.float32) / 255
    mist = np.array((197, 212, 222), np.float32) / 255
    water = np.array((70, 120, 150), np.float32) / 255
    mid = (np.array(CENTRE_KM) / 2)
    img = render(1080, 1920, mid[0], mid[1], 26, navy, mist, water)
    canvas = np.zeros((1920, 1080), np.uint8)
    pts = np.round(to_screen(ROUTE, 1080, 1920, mid[0], mid[1], 26) * 4).astype(np.int32)
    cv2.polylines(canvas, [pts], False, 255, 6, cv2.LINE_AA, 2)
    a = canvas[..., None].astype(np.float32) / 255
    img = img * (1 - a) + a * np.array((156, 73, 50), np.float32) / 255
    Image.fromarray((img * 255).astype(np.uint8)).save(P / "work" / "map-test.jpg", quality=90)
    print("route km", round(float(ROUTE_SEG[-1]), 1), "centre", CENTRE_KM, "places", len(PLACES))
