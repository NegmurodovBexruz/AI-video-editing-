"""Find a style's renderer module: built-in (engine/styles/<name>.py) or shipped with a style plugin
(<styles>/skills/<name>/renderer.py, written by the "Uslub yaratish" agent next to the style's rules).

    from core import styles_loader; st = styles_loader.load("pod_glow")
    python -I engine/core/styles_loader.py check <skill_dir>      -> exit 0 and "ok", or the problem (exit 1)

A renderer module must provide: build_timeline(job, spec, W, H), validate(tl, spec, meta, fonts),
chunk_safe(tl, f), sfx_events(tl, spec), and class Renderer(job, spec, tl, W, H) with render_frame(f, src, matte),
face_box(f), .boxes and .warnings. See engine/styles/in_scene_type.py for the reference implementation.
"""
import importlib
import importlib.util
import os
import re
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
ROOT = ENGINE.parent
REQUIRED_FUNCS = ("build_timeline", "validate", "chunk_safe", "sfx_events")
REQUIRED_METHODS = ("render_frame", "face_box")
NAME = re.compile(r"^[a-z][a-z0-9_]{1,40}$")


def skill_dirs():
    """Where style plugins live: DASH_STYLES (Docker: /data/styles), the repo's styles/, extra dirs (dry runs)."""
    dirs = []
    if os.environ.get("DASH_STYLES"):
        dirs.append(Path(os.environ["DASH_STYLES"]) / "skills")
    dirs.append(ROOT / "styles" / "skills")
    dirs += [Path(p) for p in os.environ.get("ENGINE_STYLE_DIRS", "").split(os.pathsep) if p]
    return list(dict.fromkeys(dirs))


def find(name):
    """Path of a plugin renderer, or None. Built-in renderers are not files here (they import as styles.<name>)."""
    for d in skill_dirs():
        p = d / name / "renderer.py"
        if p.is_file():
            return p
    return None


def _load_file(name, path):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))          # plugin renderers import `from core import ...` like built-in ones
    spec = importlib.util.spec_from_file_location("style_plugin_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def load(name):
    if not NAME.match(name or ""):
        raise SystemExit("bad style name: %r" % name)
    if (ENGINE / "styles" / (name + ".py")).is_file():
        return importlib.import_module("styles." + name)
    p = find(name)
    if p:
        return _load_file(name, p)
    raise SystemExit("style '%s' has no engine renderer (engine/styles/%s.py or <styles>/skills/%s/renderer.py)" % (name, name, name))


def contract_problems(mod):
    out = ["missing function %s()" % f for f in REQUIRED_FUNCS if not callable(getattr(mod, f, None))]
    cls = getattr(mod, "Renderer", None)
    if not isinstance(cls, type):
        out.append("missing class Renderer")
    else:
        out += ["Renderer has no %s()" % m for m in REQUIRED_METHODS if not callable(getattr(cls, m, None))]
    doc = (mod.__doc__ or "")
    if "edit.json" not in doc and "Edit spec" not in doc:
        out.append("module docstring must document the edit.json format")
    return out


def check_dir(skill_dir):
    skill_dir = Path(skill_dir)
    p = skill_dir / "renderer.py"
    if not p.is_file():
        return ["renderer.py yo'q (%s)" % p]
    try:
        mod = _load_file(skill_dir.name, p)
    except Exception as e:  # syntax/import errors: report, never crash the caller
        return ["renderer.py import xatosi: %s: %s" % (type(e).__name__, e)]
    return contract_problems(mod)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        probs = check_dir(sys.argv[2])
        print("ok" if not probs else "\n".join(probs))
        sys.exit(1 if probs else 0)
    raise SystemExit(__doc__)
