"""Sound + master + mux: speech, the style's accent sounds (and an optional ducked bed) -> out/final.mp4.

usage: python -I engine/finish.py <job> [--picture work/picture.mp4] [--out out/final.mp4]
Accent sounds come from the style's sound rules (edit.json "sound": {"auto", "extra", "bed", "bed_db"}).
Master: -14 LUFS integrated, true peak <= -1 dBTP measured on the final file.
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import audio, config, styles_loader  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--picture", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    job = Path(a.job)
    spec = json.loads((job / "edit.json").read_text(encoding="utf-8"))
    st = styles_loader.load(spec["style"])
    tl = st.build_timeline(job, spec)
    events, dropped = st.sfx_events(tl, spec)
    snd = spec.get("sound") or {}
    bed = snd.get("bed")
    if bed and not Path(bed).is_absolute():
        bed = job / bed
    out = Path(a.out or job / "out" / "final.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    rep = audio.finish(job, Path(a.picture or job / "work" / "picture.mp4"), events, out, bed=bed,
                       bed_db=snd.get("bed_db", -31.0))
    rep["dropped_for_spacing"] = dropped
    (job / "work" / "sound.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("final %s: %.1f LUFS, true peak %.1f dBTP, %d accents (%d dropped for spacing)"
          % (out, rep["integrated_lufs"], rep["true_peak_dbtp"], len(events), len(dropped)))


if __name__ == "__main__":
    main()
