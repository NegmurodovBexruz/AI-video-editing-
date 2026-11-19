"""faster-whisper worker (runs in the ASR venv): word timings for one audio/video file.
usage: python -I asr_worker.py <src> <out.json> [lang] [model]
"""
import json
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] not in ("", "auto") else None
name = sys.argv[4] if len(sys.argv) > 4 else "large-v3"
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
model = WhisperModel(name, device="cpu", compute_type="int8", cpu_threads=6)
segments, info = model.transcribe(audio, language=lang, word_timestamps=True, vad_filter=False,
                                  condition_on_previous_text=False)
words, segs = [], []
for seg in segments:
    segs.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
    for w in seg.words or []:
        if w.word.strip():
            words.append({"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                          "p": round(w.probability, 3)})
with open(out, "w", encoding="utf-8") as f:
    json.dump({"language": info.language, "model": name, "segments": segs, "words": words}, f,
              ensure_ascii=False, indent=1)
print("%d words, language %s (%.2f)" % (len(words), info.language, info.language_probability))
