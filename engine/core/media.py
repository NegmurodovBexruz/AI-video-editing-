"""ffmpeg / ffprobe helpers: probe, frame readers, encoders, memory check."""
import ctypes
import json
import os
import subprocess

import numpy as np


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def probe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)]).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    rot = int(v.get("tags", {}).get("rotate", rot))
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = v.get("avg_frame_rate", "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    return {"w": w, "h": h, "fps": round(fps, 4), "duration": float(d["format"].get("duration", 0)),
            "rotation": rot, "has_audio": bool(a), "codec": v.get("codec_name"),
            "pix_fmt": v.get("pix_fmt"), "color_transfer": v.get("color_transfer")}


def frames(path, w, h, fmt="bgr24", start_frame=0, count=None, scale=None):
    """Yield raw frames (H x W x C uint8, or H x W for gray). start_frame is exact (trim filter)."""
    ch = {"bgr24": 3, "rgb24": 3, "gray": 1}[fmt]
    vf = []
    if start_frame:
        vf.append("trim=start_frame=%d" % start_frame)
    if scale:
        vf.append("scale=%d:%d:flags=%s" % (w, h, scale))
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd += ["-f", "rawvideo", "-pix_fmt", fmt, "-"]
    # stderr off: closing a reader early (count=) makes ffmpeg report a harmless broken pipe
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 7)
    n = w * h * ch
    k = 0
    try:
        while count is None or k < count:
            b = p.stdout.read(n)
            if len(b) < n:
                break
            a = np.frombuffer(b, np.uint8)
            yield a.reshape(h, w, ch) if ch > 1 else a.reshape(h, w)
            k += 1
    finally:
        p.stdout.close()
        p.kill()
        p.wait()


def encoder(path, w, h, fps=30, fmt="bgr24", crf=14, preset="fast", extra=None):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", fmt, "-s", "%dx%d" % (w, h),
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-x264-params", "rc-lookahead=20", "-pix_fmt", "yuv420p"] + (extra or []) + [str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def frame_at(path, t, w=None, h=None, fmt="bgr24"):
    vf = ["-vf", "scale=%d:%d:flags=lanczos" % (w, h)] if w else []
    b = run(["ffmpeg", "-v", "error", "-ss", "%.4f" % t, "-i", str(path), "-frames:v", "1"] + vf +
            ["-f", "rawvideo", "-pix_fmt", fmt, "-"]).stdout
    return b


def free_ram_gb():
    if os.name != "nt":
        return 8.0

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 30


def loudness(path):
    """Integrated loudness (LUFS) and true peak (dBTP) via ebur128."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = p.stderr[p.stderr.rfind("Summary:"):]
    I = tp = None
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            I = float(line.split()[1])
        elif line.startswith("Peak:"):
            tp = float(line.split()[1])
    return I, tp
