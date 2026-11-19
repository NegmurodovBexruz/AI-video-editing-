"""In-Scene Type renderer: layered type inside the presenter's shot, head-locked clusters, zoom pulses,
cellophane / glow-silhouette transitions. Rules: styles/skills/in_scene_type (type.md, camera.md, motion.md,
devices.md, look.md, sound.md). Nothing in here belongs to one video: positions are shares of W/H or of the
face width (FW) measured per frame; everything video-specific comes from the edit spec (edit.json).

Edit spec (job/edit.json), written by the agent:
{
  "style": "in_scene_type",
  "accent": "#E8A33C",                       optional, brand colour for sub-lines
  "fonts": {"condensed": "path.ttf", ...},   optional overrides (roles: condensed, sans, sans_bold, serif_italic, script)
  "word_fixes": {"173": {"onset": 41.2, "text": "launchpad"}},   optional, word index -> fields
  "phrases": [{"words": [first, last], "key": [i, ...], "layer": "front|back|back_grey|chest|figure|script|null",
               "sub": [i, ...], "key_text": "100"}],             key_text optional (figures, spelling)
  "camera": {"start": 1.16, "events": [{"t": 2.38, "frames": 6, "scale": 1.08, "ease": "out|in|inout|lin"}]},
  "setups": [5.28, 27.96],                   set-up changes (s): the camera resets to 1.0 here
  "transitions": [{"type": "cellophane|glow", "t": 5.28}],
  "overlays": {"cellophane": "gen/video/cello.mp4"},            optional; procedural fallback otherwise
  "extra": "scripts/devices.py",             optional hook: draw(renderer, f, img, matte) per frame
  "sound": {"bed": "path.mp3", "bed_db": -31, "extra": [{"sound": "thump", "t": 12.3}], "auto": true}
}
"""
import importlib.util
import json
import math
from pathlib import Path

import cv2
import numpy as np

from core import config, geometry, media, text as T

NAME = "in_scene_type"

# ---- static rules (shares of W / H / FW) ----
R = {
    "cluster_cap": 0.021, "cluster_cap_min": 0.0165, "sub_cap": 0.019, "chest_cap": 0.055, "fig_cap": 0.072,
    "front_cap": 0.13, "front_cap_max": 0.15, "front_w": (0.70, 0.80), "front_y": 0.645, "chest_y": 0.655,
    "fig_y": 0.635, "back_cap": 0.11, "script_h": 0.075, "line_h": 1.15,
    # cluster placement candidates, tried in order: eye level beside the head (type.md), then chin level
    # closer to the neck when the side of the head is too narrow. (kx FW + kw W) from the face centre, ky FW below it.
    "cluster_eye": [(1.00, 0.0, -0.15), (0.85, 0.0, -0.15), (0.70, 0.0, -0.15)],
    "cluster_chin": [(0.30, 0.05, 0.76), (0.25, 0.05, 0.76), (0.20, 0.05, 0.76)],
    "cluster_room_min": 0.22, "edge": 0.04, "pause_clear": 0.8, "exit_f": 5,
    # platform action rail (Reels/TikTok/Shorts): nothing right of 0.86 W between 0.40 and 0.90 H
    "rail_x": 0.86, "rail_y": (0.40, 0.90),
}
TRANS_SPAN = {"cellophane": (-3, 3), "glow": (-4, 1)}


def fv(t, fps=30):
    """First visible frame of something whose audio starts at t (0-1 f after the onset)."""
    return int(math.floor(t * fps)) + 1


def _clean(w):
    return w.strip(",.?!;:\"“”«»…")


def _case(word, role, sentence_start):
    t = _clean(word)
    if role in ("front", "back", "back_grey"):
        return t.upper()
    keep = (len(t) > 1 and t.isupper()) or t == "I" or t.startswith("I'") or t.startswith("I’")
    if keep:
        return t
    if t[:1].isupper() and not sentence_start:      # capital inside a sentence: a name, keep it
        return t
    return t.lower()


# ================================================================ timeline

def build_timeline(job, spec, out_w=config.OUT_W, out_h=config.OUT_H):
    wd = Path(job) / "work"
    meta = json.loads((wd / "meta.json").read_text(encoding="utf-8"))
    words = json.loads((wd / "words.json").read_text(encoding="utf-8"))
    track = json.loads((wd / "track.json").read_text(encoding="utf-8"))
    for i, fx in (spec.get("word_fixes") or {}).items():
        i = int(i)
        if "onset" in fx:
            words[i]["onset"] = float(fx["onset"])
        if "text" in fx:
            words[i]["word"] = fx["text"]
    fps, N = config.FPS, min(meta["n"], track["n"])
    starts = {0} | {i + 1 for i, w in enumerate(words) if w["word"].rstrip("\"”»").endswith((".", "?", "!"))}
    comps = []
    for ci, p in enumerate(spec["phrases"]):
        a, b = p["words"]
        keys, subs, layer = list(p.get("key") or []), list(p.get("sub") or []), p.get("layer")
        if not keys:
            layer = None
        items = []
        if keys:
            txt = p.get("key_text") or " ".join(_case(words[k]["word"], layer, k in starts) for k in keys)
            if layer in ("front", "back", "back_grey"):
                txt = txt.upper()
            items.append({"role": layer, "text": txt, "f": fv(words[keys[0]]["onset"]), "words": keys})
        for k in subs:
            items.append({"role": "sub", "text": _case(words[k]["word"], "sub", k in starts),
                          "f": fv(words[k]["onset"]), "words": [k]})
        for k in range(a, b + 1):
            if k in keys or k in subs:
                continue
            items.append({"role": "cluster", "text": _case(words[k]["word"], "cluster", k in starts),
                          "f": fv(words[k]["onset"]), "words": [k]})
        items = [it for it in items if it["text"]]
        comps.append({"id": ci + 1, "a": a, "b": b, "layer": layer, "items": items,
                      "f_start": fv(words[a]["onset"]),
                      "last_onset_f": fv(max(words[k]["onset"] for k in range(a, b + 1))),
                      "key_f": items[0]["f"] if keys else None,
                      "text": " ".join(_clean(words[k]["word"]) for k in range(a, b + 1))})
    for i, c in enumerate(comps):
        last_end = max(words[k]["end"] for k in range(c["a"], c["b"] + 1))
        if i + 1 < len(comps):
            nxt = comps[i + 1]
            x0 = nxt["f_start"] - R["exit_f"]
            if words[nxt["a"]]["onset"] - last_end > R["pause_clear"]:
                x0 = min(x0, int(last_end * fps) + 5)
            small = max(x0, c["last_onset_f"] + 4)
            c["exit_small_f"] = small
            c["exit_f"] = max(small, (c["key_f"] or 0) + 15)
            if nxt["key_f"] is not None and c["key_f"] is not None:
                # never two key words on screen (type.md) beats "key word leaves last": when phrases are back
                # to back the key word goes (exit + 4 f fade) before the next one lands, its small words stay
                c["exit_f"] = max(c["key_f"] + 8, min(c["exit_f"], nxt["key_f"] - 5))
        else:
            c["exit_f"] = c["exit_small_f"] = N + 100
        c["end_f"] = max(c["exit_f"], c["exit_small_f"])

    setup_f = [int(math.ceil(t * fps - 1e-6)) for t in spec.get("setups", [])]
    cam = spec.get("camera") or {}
    scale = geometry.scale_curve(N, fps, cam.get("events", []), cam.get("start", 1.0), setup_f)
    cx = float(np.median(track["hx"][:N]))
    view = geometry.View(out_w, out_h, meta["work_w"], meta["work_h"], cx=cx, cy=0.5)
    anchor = geometry.anchors(scale, track, view, setup_f)
    for c in comps:
        if c["layer"] in ("back", "back_grey"):
            f = c["key_f"]
            hl, hr, top = track["hl"][f], track["hr"][f], track["top"][f]
            fw = track["fw"][f]
            ar = meta["work_h"] / meta["work_w"]
            c["head_l"] = hl if hl is not None else track["hx"][f] - 0.6 * fw
            c["head_r"] = hr if hr is not None else track["hx"][f] + 0.6 * fw
            c["head_top"] = top if top is not None else track["hy"][f] - 0.7 * fw / ar
    trans = [{"type": t["type"], "f": int(math.ceil(t["t"] * fps - 1e-6)), "t": t["t"]}
             for t in spec.get("transitions", [])]
    return {"fps": fps, "n": N, "comps": comps, "scale": scale, "anchor": anchor, "setup_f": setup_f,
            "transitions": trans, "cx": cx, "words": words}


# ================================================================ renderer

class Renderer:
    def __init__(self, job, spec, tl, out_w=config.OUT_W, out_h=config.OUT_H):
        self.job, self.spec, self.TL = Path(job), spec, tl
        wd = self.job / "work"
        self.meta = json.loads((wd / "meta.json").read_text(encoding="utf-8"))
        self.TR = json.loads((wd / "track.json").read_text(encoding="utf-8"))
        self.W, self.H = out_w, out_h
        self.u = out_w / 1080.0
        self.N = tl["n"]
        self.view = geometry.View(out_w, out_h, self.meta["work_w"], self.meta["work_h"], cx=tl["cx"], cy=0.5)
        fo = spec.get("fonts")
        self.F = {r: T.font_path(r, fo) for r in T.FONT_FILES}
        self.WHITE = np.array([1, 1, 1], np.float32)
        self.ACC = T.hex_bgr(spec.get("accent", "#E8A33C"))
        self.LAY, self.cello, self.glow_prev = {}, None, {}
        self.boxes = []
        k_eff = self.view.K
        self.sharpen = 0.30 * min(1.0, max(0.0, (k_eff - 1.05) / 0.45))
        self.extra = None
        if spec.get("extra"):
            p = self.job / spec["extra"]
            sp = importlib.util.spec_from_file_location("job_extra", p)
            mod = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(mod)
            self.extra = mod
        self.warnings = []
        self._prepare_back()

    # ---- camera helpers
    def cam(self, f):
        s = self.TL["scale"][f]
        ax, ay = self.TL["anchor"][f]
        return s, ax, ay

    def to_screen(self, xn, yn, f):
        s, ax, ay = self.cam(f)
        return self.view.screen(xn, yn, s, ax, ay)

    def fwpx(self, f):
        return self.view.px(self.TR["fw"][f])

    # ---- back words: placement measured on the matte of the key frame (deterministic for chunked renders)
    def _prepare_back(self):
        mw, mh = self.meta["matte_w"], self.meta["matte_h"]
        for c in self.TL["comps"]:
            if c["layer"] not in ("back", "back_grey"):
                continue
            f = c["key_f"]
            m = next(media.frames(self.job / "work" / "matte.mp4", mw, mh, "gray", start_frame=f, count=1))
            s, ax, ay = self.cam(f)
            M = self.view.matrix(mw, mh, s, ax, ay)
            mm = cv2.warpAffine(m, M, (self.W, self.H), flags=cv2.INTER_LINEAR).astype(np.float32) / 255
            c["_matte_key"] = mm

    def right_limit(self, y0, y1):
        """Right edge for text spanning rows y0..y1 (px): the platform action rail where it applies."""
        a, b = R["rail_y"]
        return R["rail_x"] * self.W if (y0 < b * self.H and y1 > a * self.H) else (1 - R["edge"]) * self.W

    def fit_x(self, cx, w, y0, y1):
        lo, hi = R["edge"] * self.W, self.right_limit(y0, y1)
        return min(max(cx, lo + w / 2), hi - w / 2), hi - lo

    def layout(self, c):
        if c["id"] in self.LAY:
            return self.LAY[c["id"]]
        W, H, TR, N = self.W, self.H, self.TR, self.N
        f0 = min(N - 1, c["f_start"])
        L = {}
        cl = [it for it in c["items"] if it["role"] == "cluster"]
        if cl:
            life = range(max(0, c["f_start"]), min(N - 1, c["exit_small_f"] + 4) + 1)
            fw0 = self.fwpx(f0)          # the offset is fixed at the composition's first frame (type.md)
            best = None
            for level, cands in (("eye", R["cluster_eye"]), ("chin", R["cluster_chin"])):
                for kx, kw, ky in cands:
                    rr, rl = [], []
                    for g in life:
                        sg = self.TL["scale"][g]
                        hs, vs = self.to_screen(TR["hx"][g], TR["hy"][g], g)
                        dxp = (kx * fw0 + kw * W) * sg
                        ytop = vs + ky * fw0 * sg
                        rr.append((self.right_limit(ytop, ytop + 0.08 * H * sg) - (hs + dxp)) / sg)
                        rl.append(((hs - dxp) - R["edge"] * W) / sg)
                    room_r, room_l = min(rr), min(rl)
                    side = 1 if room_r >= room_l else -1
                    room = max(room_r, room_l)
                    cand = (room, level, kx, kw, ky, side)
                    if best is None or room > best[0]:
                        best = cand
                    if room >= R["cluster_room_min"] * W:
                        best = cand
                        break
                else:
                    continue
                break
            room, level, kx, kw, ky, side = best
            if room < R["cluster_room_min"] * W:
                self.warnings.append("comp %d: narrow room for the cluster (%.2f W)" % (c["id"], room / W))
            room = max(room, 0.12 * W)
            cap = R["cluster_cap"] * H
            while True:
                size = T.size_for_cap(self.F["sans"], cap)
                sp = T.text_width(" ", self.F["sans"], size)
                lines, cur, cw = [], [], 0
                for it in cl:
                    ww = T.text_width(it["text"], self.F["sans"], size)
                    if cur and cw + sp + ww > room:
                        lines.append(cur)
                        cur, cw = [], 0
                    cur.append((it, ww))
                    cw = cw + (sp if len(cur) > 1 else 0) + ww
                if cur:
                    lines.append(cur)
                widest = max(sum(w for _, w in ln) + sp * (len(ln) - 1) for ln in lines)
                if (len(lines) <= 3 and widest <= room) or cap <= R["cluster_cap_min"] * H:
                    break
                cap -= 0.001 * H
            lh = size * R["line_h"]
            place = []
            for li, ln in enumerate(lines):
                lw = sum(w for _, w in ln) + sp * (len(ln) - 1)
                x = 0 if side > 0 else -lw
                for it, ww in ln:
                    place.append((id(it), x, li * lh + cap))
                    x += ww + sp
            L["cluster"] = {"side": side, "kx": kx, "kw": kw, "ky": ky, "level": level, "size": size,
                            "place": place, "wmax": widest, "fw0": fw0, "lines": len(lines)}
        key = [it for it in c["items"] if it["role"] not in ("cluster", "sub")]
        subs = [it for it in c["items"] if it["role"] == "sub"]
        if key:
            k = key[0]
            r = k["role"]
            life = range(max(0, c["f_start"]), min(N - 1, c["exit_f"]) + 1)
            hx_med = float(np.median([self.to_screen(TR["hx"][g], TR["hy"][g], g)[0] for g in life]))
            CX = min(max(hx_med, 0.40 * W), 0.60 * W)
            if r == "front":
                fnt = self.F["condensed"]
                size = T.size_for_cap(fnt, R["front_cap"] * H)
                w = T.text_width(k["text"], fnt, size)
                lo, hi = R["front_w"]
                if w > hi * W:
                    size *= hi * W / w
                elif w < lo * W:
                    size = min(T.size_for_cap(fnt, R["front_cap_max"] * H), size * lo * W / w)
                w = T.text_width(k["text"], fnt, size) * 1.08      # widest moment: the 1.08 -> 1.00 entry
                capk = size * T.cap_ratio(fnt)
                base = R["front_y"] * H + capk / 2
                x, span = self.fit_x(CX, w, base - capk, base)
                if w > span:
                    size *= span / w
                    capk = size * T.cap_ratio(fnt)
                    x, _ = self.fit_x(CX, span, base - capk, base)
                L["key"] = {"size": size, "x": x, "base": base, "cap": capk}
            elif r == "chest":
                fnt = self.F["sans_bold"]
                size = T.size_for_cap(fnt, R["chest_cap"] * H)
                w = T.text_width(k["text"], fnt, size)
                capk = size * T.cap_ratio(fnt)
                base = R["chest_y"] * H + capk / 2
                span = self.right_limit(base - capk, base) - R["edge"] * W
                if w > min(0.80 * W, span):
                    size *= min(0.80 * W, span) / w
                    w = min(0.80 * W, span)
                    capk = size * T.cap_ratio(fnt)
                x, _ = self.fit_x(CX, w, base - capk, base)
                L["key"] = {"size": size, "x": x, "base": base, "cap": capk}
            elif r == "figure":
                fnt = self.F["serif_italic"]
                size = T.size_for_cap(fnt, R["fig_cap"] * H)
                capk = size * T.cap_ratio(fnt)
                base = R["fig_y"] * H + capk / 2
                x, _ = self.fit_x(CX, T.text_width(k["text"], fnt, size), base - capk, base)
                L["key"] = {"size": size, "x": x, "base": base, "cap": capk}
            elif r == "script":
                fnt = self.F["script"]
                fw0 = self.fwpx(f0)
                # 0.05-0.08 H (devices.md); smaller when the person is small in frame, so it stays on the body
                size = T.size_for_cap(fnt, (R["script_h"] if fw0 >= 0.30 * W else 0.055) * H)
                capk = size * T.cap_ratio(fnt)
                ar = self.meta["work_w"] / self.meta["work_h"]
                hx, hy, fw = TR["hx"][f0], TR["hy"][f0], TR["fw"][f0]
                to_n = 1.0 / (self.meta["work_h"] * self.view.K)          # output px (zoom 1) -> normalised y
                y = hy + max(1.42 * fw * ar, (0.80 * fw0 + 1.1 * capk) * to_n)   # baseline below chin + 0.15 FW
                L["key"] = {"size": size, "src_pt": (hx + 0.04 * fw, y), "rot": 6.0}
            elif r in ("back", "back_grey"):
                L["key"] = self._back_layout(c, k)
            if subs and "key" in L:
                ssz = T.size_for_cap(self.F["sans"], R["sub_cap"] * H)
                sp = T.text_width(" ", self.F["sans"], ssz)
                ws = [T.text_width(s_["text"], self.F["sans"], ssz) for s_ in subs]
                tot = sum(ws) + sp * (len(ws) - 1)
                kk = L["key"]
                xc = kk.get("x", kk.get("xl", CX) + kk.get("w", 0) / 2)
                sbase = kk.get("base", R["chest_y"] * H) + 0.045 * H
                hi = self.right_limit(sbase - ssz, sbase)
                x = min(max(xc - tot / 2, R["edge"] * W), hi - tot)
                pl = []
                for s_, w_ in zip(subs, ws):
                    pl.append((id(s_), x))
                    x += w_ + sp
                L["sub"] = {"size": ssz, "base": sbase, "place": pl}
        self.LAY[c["id"]] = L
        return L

    def _back_layout(self, c, k):
        W, H = self.W, self.H
        fnt = self.F["condensed"]
        fk = k["f"]
        sl, _ = self.to_screen(c["head_l"], 0, fk)
        sr, _ = self.to_screen(c["head_r"], 0, fk)
        size = T.size_for_cap(fnt, R["back_cap"] * H)
        capk = size * T.cap_ratio(fnt)
        _, ytop = self.to_screen(0, c["head_top"], fk)
        _, yh = self.to_screen(0, self.TR["hy"][fk], fk)
        cy = max(0.06 * H + capk / 2, (ytop + yh) / 2 - 0.01 * H)
        base = cy + capk / 2
        # free strip beside the head on the key frame's matte: the head may cover only 0.02 W of the inner letter
        m = c["_matte_key"]
        for _ in range(3):
            capk = size * T.cap_ratio(fnt)
            y0, y1 = int(max(0, base - capk)), int(min(H, base))
            cols = np.where((m[y0:y1] > 0.5).any(axis=0))[0]
            hl, hr = (cols.min(), cols.max()) if len(cols) else (sl, sr)
            avail_r = 0.97 * W - (hr - 0.02 * W)
            avail_l = (hl + 0.02 * W) - 0.03 * W
            side = 1 if avail_r >= avail_l else -1
            avail = max(avail_r, avail_l)
            w = T.text_width(k["text"], fnt, size)
            if w > avail:
                size *= avail / w
            else:
                break
        w = T.text_width(k["text"], fnt, size)
        if w < 0.5 * W:
            self.warnings.append("comp %d: back word '%s' only %.2f W wide (head fills the frame); "
                                 "a front word may read better" % (c["id"], k["text"], w / W))
        xl = (hr - 0.02 * W) if side > 0 else (hl + 0.02 * W - w)
        return {"size": size, "xl": xl, "base": base, "cap": size * T.cap_ratio(fnt), "side": side, "w": w}

    # ---- drawing
    def _rec(self, role, txt, box):
        if box:
            self.boxes.append((role, txt, box))

    def draw_comp(self, f, c, img, matte_inv):
        if f < c["f_start"] or f > c["end_f"] + 6:
            return
        # a set-up change cuts a finished composition with it (hard cut with the transition, devices.md);
        # a phrase still being spoken across the cut keeps its words
        if any(c["last_onset_f"] < sf <= f for sf in self.TL["setup_f"]):
            return
        L = self.layout(c)
        s, _, _ = self.cam(f)
        u, W, H = self.u, self.W, self.H
        for it in c["items"]:
            r, fi = it["role"], it["f"]
            if f < fi:
                continue
            fx = c["exit_small_f"] if r in ("cluster", "sub") else c["exit_f"]
            ek = 1 - min(1.0, max(0.0, (f - fx + 1) / 5))
            if ek <= 0:
                continue
            if r == "cluster":
                Lc = L["cluster"]
                hxs, hys = self.to_screen(self.TR["hx"][f], self.TR["hy"][f], f)
                ax_ = hxs + Lc["side"] * (Lc["kx"] * Lc["fw0"] + Lc["kw"] * W) * s
                ay_ = hys + Lc["ky"] * Lc["fw0"] * s
                xl_ = ax_ - (Lc["wmax"] * s if Lc["side"] < 0 else 0)
                hi = self.right_limit(ay_, ay_ + Lc["lines"] * Lc["size"] * R["line_h"] * s)
                ax_ += max(0.0, 0.03 * W - xl_) - max(0.0, xl_ + Lc["wmax"] * s - hi)   # last-resort clamp
                for (pid, px, pb) in Lc["place"]:
                    if pid == id(it):
                        p = min(1.0, max(0.0, (f - fi + 1) / 3))
                        gm = 1 - min(1.0, max(0.0, (f - fi + 1) / 4))
                        box = T.draw_text(img, it["text"], self.F["sans"], Lc["size"], ax_ + px * s, ay_ + pb * s,
                                          self.WHITE, opacity=p * ek, blur_px=(3 * (1 - p) + 4 * (1 - ek)) * u,
                                          scale=s, grey_mix=gm)
                        self._rec("cluster", it["text"], box)
            elif r == "sub":
                Ls = L.get("sub")
                if not Ls:
                    continue
                for (pid, px) in Ls["place"]:
                    if pid == id(it):
                        p = min(1.0, max(0.0, (f - fi + 1) / 3))
                        box = T.draw_text(img, it["text"], self.F["sans"], Ls["size"], px, Ls["base"], self.ACC,
                                          opacity=p * ek, blur_px=3 * (1 - ek) * u)
                        self._rec("sub", it["text"], box)
            elif r == "front":
                k = L["key"]
                op = min(1.0, (f - fi + 1) / 4)
                p = geometry.ease("out", (f - fi + 1) / 9)
                sc = 1.08 - 0.08 * p
                box = T.draw_text(img, it["text"], self.F["condensed"], k["size"], k["x"],
                                  k["base"] + (sc - 1) * k["cap"] / 2, self.WHITE, opacity=op * ek,
                                  blur_px=(12 * (1 - p) + 8 * (1 - ek)) * u, scale=sc, align="c")
                self._rec("front", it["text"], box)
            elif r == "chest":
                k = L["key"]
                p = min(1.0, (f - fi + 1) / 5)
                box = T.draw_text(img, it["text"], self.F["sans_bold"], k["size"], k["x"], k["base"], self.WHITE,
                                  opacity=p * ek, blur_px=(6 * (1 - p) + 4 * (1 - ek)) * u, align="c")
                self._rec("chest", it["text"], box)
            elif r == "figure":
                k = L["key"]
                p = geometry.ease("out", (f - fi + 1) / 11)
                box = T.draw_text(img, it["text"], self.F["serif_italic"], k["size"], k["x"], k["base"], self.WHITE,
                                  opacity=ek, blur_px=4 * (1 - ek) * u, align="c", wipe=p)
                self._rec("figure", it["text"], box)
            elif r == "script":
                k = L["key"]
                x, y = self.to_screen(k["src_pt"][0], k["src_pt"][1], f)
                p = min(1.0, (f - fi + 1) / 13)
                box = T.draw_text(img, it["text"], self.F["script"], k["size"], x, y, self.WHITE, opacity=ek,
                                  scale=s, align="c", wipe=p, rot=k["rot"])
                self._rec("script", it["text"], box)
            elif r in ("back", "back_grey"):
                k = L["key"]
                p = geometry.ease("out", (f - fi + 1) / 10)
                slide = -k["side"] * 0.18 * W * (1 - p)
                box = T.draw_text(img, it["text"], self.F["condensed"], k["size"], k["xl"] + slide, k["base"],
                                  self.WHITE, opacity=(1.0 if r == "back" else 0.55) * ek,
                                  blur_px=8 * (1 - ek) * u, mask=matte_inv)
                self._rec(r, it["text"], box)

    # ---- transitions
    def _cello_frames(self):
        if self.cello is not None:
            return self.cello
        W, H = self.W, self.H
        ov = (self.spec.get("overlays") or {}).get("cellophane")
        self.cello = {}
        if ov and (self.job / ov).exists():
            path = self.job / ov
            pr = media.probe(path)
            pw, ph = 64, 114
            lum = [float(fr.mean()) for fr in media.frames(path, pw, ph, "gray", scale="area")]
            fps = pr["fps"] or 30
            k = int(np.argmax(lum))
            peak, base = lum[k], min(lum)
            want = {-3: 0.25, -2: 0.55, -1: 0.85, 0: 1.0, 1: 0.85, 2: 0.55, 3: 0.25}
            for dt, lvl in want.items():
                rng = range(0, k + 1) if dt < 0 else range(k, len(lum))
                if dt == 0:
                    j = k
                else:
                    tgt = base + lvl * (peak - base)
                    j = min(rng, key=lambda q: abs(lum[q] - tgt))
                b = media.frame_at(path, j / fps + 0.001, W, H)
                o = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
                l_ = o.mean(axis=2, keepdims=True)
                self.cello[dt] = np.clip((l_ ** 1.25) * 1.35, 0, 1) * np.ones(3, np.float32)
        else:
            # procedural fallback: a crumpled clear sheet = ridged noise creases with broad specular sheen,
            # sweeping right -> left, densest on the cut frame
            rng = np.random.default_rng(3)

            def octave(div):
                n = rng.random((max(2, H // div), max(2, W // div))).astype(np.float32)
                return cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
            n = 0.55 * octave(90) + 0.30 * octave(40) + 0.15 * octave(18)
            n = (n - n.min()) / (n.max() - n.min() + 1e-6)
            crease = (1 - np.abs(2 * n - 1)) ** 7                     # thin bright fold lines
            sheen = np.clip((octave(160) - 0.55) * 3.0, 0, 1) ** 1.5   # broad soft reflections
            sheet = np.clip(crease * 1.3 + sheen * 0.55, 0, 1)
            xs = np.linspace(0, 1, W, dtype=np.float32)[None, :]
            for dt in range(-3, 4):
                c = 1.25 - (dt + 3) / 6.0 * 1.5
                band = np.clip(1.0 - np.abs(xs - c) / 0.55, 0, 1) ** 0.7
                dens = 1.0 - abs(dt) / 4.5
                shift = np.roll(sheet, int(dt * 0.04 * W), axis=1)
                self.cello[dt] = (np.clip(shift * band * dens * 1.2 + band * 0.10 * dens, 0, 1))[..., None] \
                    * np.ones(3, np.float32)
            self.warnings.append("cellophane: no overlay clip, procedural fallback used")
        return self.cello

    def transitions(self, f, img, matte):
        u = self.u
        for tr in self.TL["transitions"]:
            dt = f - tr["f"]
            if tr["type"] == "cellophane" and -3 <= dt <= 3:
                ov = self._cello_frames()[dt]
                img[:] = 1 - (1 - img) * (1 - ov)
            elif tr["type"] == "glow":
                if -4 <= dt <= -1:
                    if dt == -4:
                        edge = cv2.morphologyEx((matte > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT,
                                                np.ones((7, 7), np.uint8))
                        e = np.clip(T.blur(edge.astype(np.float32), 6 * u) * 3, 0, 1)[..., None]
                        img[:] = img * (1 - e) + e
                    else:
                        sil = T.blur(matte, 2 * u)[..., None]
                        bloom = np.clip(T.blur(matte, 40 * u) * 1.3 + T.blur(matte, 90 * u) * 0.8, 0, 1)[..., None]
                        out = img * 0.40 * (1 - bloom * 0.7) + bloom * 0.7
                        img[:] = out * (1 - sil) + sil
                        self.glow_prev[tr["f"]] = bloom
                elif dt in (0, 1) and tr["f"] in self.glow_prev:
                    b = self.glow_prev[tr["f"]] * (0.32 if dt == 0 else 0.12)
                    img[:] = 1 - (1 - img) * (1 - b)

    # ---- one frame
    def render_frame(self, f, src, mat):
        W, H = self.W, self.H
        s, ax, ay = self.cam(f)
        sh_, sw_ = src.shape[:2]
        sp = self.TL["scale"][f - 1] if f > 0 else s
        if abs(s - sp) / s > 0.015 and f not in self.TL["setup_f"]:
            acc = None
            for k in (0.0, 0.5, 1.0):
                ss = sp + (s - sp) * (0.5 + 0.5 * k)
                w_ = cv2.warpAffine(src, self.view.matrix(sw_, sh_, ss, ax, ay), (W, H), flags=cv2.INTER_CUBIC,
                                    borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
                acc = w_ if acc is None else acc + w_
            img = acc / (3 * 255)
        else:
            img = cv2.warpAffine(src, self.view.matrix(sw_, sh_, s, ax, ay), (W, H), flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE).astype(np.float32) / 255
        if self.sharpen > 0.01:
            img = np.clip(img + self.sharpen * (img - cv2.GaussianBlur(img, (0, 0), 1.3 * self.u)), 0, 1)
        mh, mw = mat.shape[:2]
        m = cv2.warpAffine(mat, self.view.matrix(mw, mh, s, ax, ay), (W, H), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_REPLICATE).astype(np.float32) / 255
        m = np.clip((m - 0.04) / 0.92, 0, 1)
        matte_inv = 1 - m
        self.boxes = []
        for c in self.TL["comps"]:
            if c["f_start"] - 2 <= f <= c["end_f"] + 6:
                self.draw_comp(f, c, img, matte_inv)
        if self.extra is not None:
            self.extra.draw(self, f, img, m)
        self.transitions(f, img, m)
        return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

    def face_box(self, f):
        hx, hy = self.to_screen(self.TR["hx"][f], self.TR["hy"][f], f)
        s = self.cam(f)[0]
        fw = self.fwpx(f) * s
        return (hx - fw / 2, hy - 0.65 * fw, hx + fw / 2, hy + 0.65 * fw)


def chunk_safe(tl, f):
    """True if a render chunk may start at frame f (no transition state crosses it)."""
    for tr in tl["transitions"]:
        a, b = TRANS_SPAN.get(tr["type"], (-4, 3))
        if tr["f"] + a <= f <= tr["f"] + b + 1:
            return False
    return True


# ================================================================ sound + checks

def sfx_events(tl, spec):
    """Accent sounds from the style's sound rules (sound.md), spaced >= 1.5 s by priority."""
    fps = tl["fps"]
    ev = []
    for tr in tl["transitions"]:
        if tr["type"] == "cellophane":
            ev.append({"sound": "crinkle", "t": tr["f"] / fps, "prio": 10, "why": "cellophane"})
        elif tr["type"] == "glow":
            ev.append({"sound": "shimmer", "t": tr["f"] / fps, "prio": 10, "why": "glow flash"})
    cam = (spec.get("camera") or {})
    st = cam.get("start", 1.0)
    evs = sorted(cam.get("events", []), key=lambda e: e["t"])
    prev = st
    for i, e in enumerate(evs):
        d = e["scale"] - prev
        n = e.get("frames", 6)
        if i == 0 and e["t"] <= 0.05 and d <= -0.10:
            ev.append({"sound": "whoosh_down", "t": 0.0, "prio": 8, "why": "opening zoom-out"})
        elif d <= -0.10 and n >= 10 and e.get("ease") == "inout":
            ev.append({"sound": "whoosh", "t": e["t"] + n / fps, "prio": 7, "why": "zoom-out reveal"})
        elif d >= 0.10 and n <= 8:
            ev.append({"sound": "whoosh", "t": e["t"] + 0.05, "length": 0.22, "f0": 700, "f1": 3500,
                       "lead": 0.05, "gain": -30, "prio": 3, "why": "big punch"})
        prev = e["scale"]
    last_thump = -99
    for c in tl["comps"]:
        if c["layer"] == "script":
            ev.append({"sound": "scribble", "t": c["key_f"] / fps, "prio": 6, "pan": -0.2, "why": "script"})
        if c["layer"] in ("back", "back_grey") and c["key_f"] / fps - last_thump >= 15:
            ev.append({"sound": "thump", "t": c["key_f"] / fps, "prio": 5, "why": "back word"})
            last_thump = c["key_f"] / fps
    snd = spec.get("sound") or {}
    if snd.get("auto", True) is False:
        ev = []
    for e in snd.get("extra", []):
        ev.append(dict(e, prio=e.get("prio", 9)))
    from core.audio import space_events
    return space_events(ev, 1.5)


def validate(tl, spec, meta, fonts):
    """Plan checks before rendering: coverage, pace, zoom limits, glyphs."""
    out = []
    words, fps, N = tl["words"], tl["fps"], tl["n"]
    shown = set()
    for c in tl["comps"]:
        for it in c["items"]:
            shown.update(it["words"])
    miss = [i for i in range(len(words)) if i not in shown]
    if miss:
        out.append("words not on screen: %s" % ", ".join("%d:%s" % (i, words[i]["word"]) for i in miss[:30]))
    spans = sorted((c["a"], c["b"], c["id"]) for c in tl["comps"])
    for (a1, b1, i1), (a2, b2, i2) in zip(spans, spans[1:]):
        if a2 <= b1:
            out.append("phrases %d and %d overlap (words %d-%d / %d-%d)" % (i1, i2, a1, b1, a2, b2))
    dur = N / fps
    big = [c["key_f"] / fps for c in tl["comps"] if c["layer"] in ("front", "back", "back_grey", "figure")]
    # a camera "move" = a punch, push or reveal; the release back is part of the same unit (camera.md)
    cam = spec.get("camera") or {}
    prev, moves = cam.get("start", 1.0), []
    for e in sorted(cam.get("events", []), key=lambda e: e["t"]):
        if e["scale"] > prev + 0.005 or (e["scale"] < prev - 0.10 and e.get("frames", 6) >= 10):
            moves.append(e)
        prev = e["scale"]
    for t0 in np.arange(0, max(dur - 9.99, 0.01), 10):
        nb = sum(t0 <= t < t0 + 10 for t in big)
        nm = sum(t0 <= e["t"] < t0 + 10 for e in moves)
        nt = sum(t0 <= tr["f"] / fps < t0 + 10 for tr in tl["transitions"])
        if nb > 2 or nm > 6 or nt > 1:
            out.append("pace %.0f-%.0f s: %d big words, %d camera moves, %d transitions (target 1-2 / 3-5 / <=1)"
                       % (t0, t0 + 10, nb, nm, nt))
    smax = max(tl["scale"])
    src_h = meta["src"]["h"]
    up = smax * 1920 / min(src_h, meta["work_h"])
    if up > 1.5:
        out.append("max zoom %.2f on a %dp source = %.2fx upscale: soft" % (smax, src_h, up))
    if tl["setup_f"]:
        last = max(tl["setup_f"])
        if max(tl["scale"][last:]) > 1.05:
            out.append("final set-up moves more than 5 %% (max %.2f)" % max(tl["scale"][last:]))
    role_font = {"front": "condensed", "back": "condensed", "back_grey": "condensed", "chest": "sans_bold",
                 "figure": "serif_italic", "script": "script", "cluster": "sans", "sub": "sans"}
    for c in tl["comps"]:
        for it in c["items"]:
            mg = T.missing_glyphs(fonts[role_font[it["role"]]], it["text"])
            if mg:
                out.append("font %s lacks %s for '%s'" % (role_font[it["role"]], "".join(mg), it["text"]))
    return out
