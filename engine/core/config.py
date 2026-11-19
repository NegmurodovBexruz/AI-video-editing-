"""Shared paths and constants of the editing engine."""
import os
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
ROOT = ENGINE.parent                                   # D:\projects\higgsfield test01
FONTS = ENGINE / "fonts"
RVM_MODEL = ROOT / "models" / "rvm_mobilenetv3_fp32.onnx"

# faster-whisper lives in its own venv on the PC (large-v3 is cached there); in Docker it is the image's Python.
# The engine calls it as a subprocess.
ASR_PYTHON = Path(os.environ.get("ENGINE_ASR_PYTHON") or os.environ.get("DASH_ASR_PYTHON") or
                  (r"D:\projects\plugin_style\.venv\Scripts\python.exe" if os.name == "nt" else sys.executable))

FPS = 30
OUT_W, OUT_H = 1080, 1920
WORK_MAX_H = 2560          # working copy: long side capped (keeps zoom headroom, limits RAM)
MATTE_H = 1280             # person matte height
TRACK_W = 360              # head-track proxy width
