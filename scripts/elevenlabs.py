"""ElevenLabs sound effects and music for the edit.

    python elevenlabs.py sfx <name> "<prompt>" <seconds> [variants]
    python elevenlabs.py music <plan.json> <out_name>

The key is read from ../.env (ELEVENLABS_API_KEY) and never printed.
Outputs land in gen/audio/ as 48 kHz WAV (sfx) or MP3 (music).
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

P = Path(__file__).resolve().parent.parent
OUT = P / "gen" / "audio"


def api_key():
    for line in (P / ".env").read_text(encoding="utf-8-sig").splitlines():
        k, _, v = line.partition("=")
        if k.strip() == "ELEVENLABS_API_KEY":
            v = v.split(" #", 1)[0].split("\t#", 1)[0]      # allow inline comments
            return v.strip().strip('"')
    raise SystemExit("ELEVENLABS_API_KEY missing in .env")


def post(path, body, query=""):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io{path}{query}", data=json.dumps(body).encode(),
        headers={"xi-api-key": api_key(), "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:600]}")


def sfx(name, prompt, seconds, variants=1):
    OUT.mkdir(parents=True, exist_ok=True)
    for v in range(int(variants)):
        body = {"text": prompt, "duration_seconds": float(seconds), "prompt_influence": 0.6,
                "model_id": "eleven_text_to_sound_v2"}
        try:
            audio, _ = post("/v1/sound-generation", body, "?output_format=wav_48000")
            ext = "wav"
        except SystemExit as e:                        # WAV needs a higher tier
            print("wav_48000 refused, falling back to mp3:", str(e)[:120])
            audio, _ = post("/v1/sound-generation", body, "?output_format=mp3_44100_128")
            ext = "mp3"
        out = OUT / f"sfx_{name}_{v}.{ext}"
        out.write_bytes(audio)
        print("saved", out.name, len(audio), "bytes")


def music(plan_path, out_name):
    OUT.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    audio, headers = post("/v1/music", plan, "?output_format=mp3_48000_192")
    out = OUT / f"{out_name}.mp3"
    out.write_bytes(audio)
    song = {k: v for k, v in headers.items() if "song" in k.lower()}
    print("saved", out.name, len(audio), "bytes", song)


def write_wav(path, pcm, rate):
    import wave
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sfx":
        sfx(*sys.argv[2:])
    elif cmd == "music":
        music(*sys.argv[2:])
