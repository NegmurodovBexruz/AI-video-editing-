"""Person alpha matte for the whole source with Robust Video Matting (ONNX, CPU).

Streams frames from ffmpeg and writes the matte as a grayscale video, so only one
frame is in memory at a time. Output geometry matches the source frame (scaled).
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort

SRC = sys.argv[1]
OUT = sys.argv[2]
MODEL = Path(__file__).resolve().parent.parent / "models" / "rvm_mobilenetv3_fp32.onnx"
W, H, FPS = 810, 1440, 30

dec = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"fps={FPS},scale={W}:{H}:flags=area",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
    stdout=subprocess.PIPE)
enc = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
     "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "8",
     "-pix_fmt", "yuv420p", OUT],
    stdin=subprocess.PIPE)

sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
ratio = np.array([0.375], np.float32)
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    src = np.frombuffer(buf, np.uint8).reshape(H, W, 3).transpose(2, 0, 1)[None].astype(np.float32) / 255
    _, pha, *rec = sess.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2],
                                   "r4i": rec[3], "downsample_ratio": ratio})
    enc.stdin.write((pha[0, 0] * 255).clip(0, 255).astype(np.uint8).tobytes())
    n += 1
    if n % 100 == 0:
        print(n, flush=True)
enc.stdin.close()
enc.wait()
dec.wait()
print("frames", n)
