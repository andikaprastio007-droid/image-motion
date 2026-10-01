import json, shutil, uuid, re, logging
from pathlib import Path
from PIL import Image
import config

log = logging.getLogger("app")

def _dir(pid):
    if not re.fullmatch(r"p_[0-9a-f]{8}", pid or ""):
        raise ValueError("ID project tidak valid")
    return config.PROJECTS / pid

def create(file_storage):
    name = file_storage.filename or ""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in config.ALLOWED_EXT:
        raise ValueError("Format tidak didukung (jpg, png, webp)")
    pid = "p_" + uuid.uuid4().hex[:8]
    d = config.PROJECTS / pid
    (d / "output").mkdir(parents=True)
    dst = d / "input.jpg"
    try:
        im = Image.open(file_storage.stream); im.verify()
        file_storage.stream.seek(0)
        im = Image.open(file_storage.stream).convert("RGB")
        im.thumbnail((2560, 2560))
        im.save(dst, "JPEG", quality=92)
    except Exception:
        shutil.rmtree(d, ignore_errors=True)
        raise ValueError("File bukan gambar yang valid")
    save(pid, "metadata", {"id": pid, "original_name": Path(name).name[:80], "stock_safe": True})
    return pid

def load(pid, name, default=None):
    f = _dir(pid) / f"{name}.json"
    return json.loads(f.read_text()) if f.exists() else default

def save(pid, name, data):
    (_dir(pid) / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

def input_path(pid):
    p = _dir(pid) / "input.jpg"
    if not p.exists(): raise ValueError("Project tidak ditemukan")
    return p

def out_dir(pid): return _dir(pid) / "output"

def listing():
    items = []
    for d in sorted(config.PROJECTS.glob("p_*"), key=lambda p: p.stat().st_mtime, reverse=True):
        m = json.loads((d / "metadata.json").read_text()) if (d / "metadata.json").exists() else {"id": d.name}
        m["has_prompts"] = (d / "prompts.json").exists()
        m["videos"] = len(list((d / "output").glob("*.mp4")))
        items.append(m)
    return items

def delete(pid):
    shutil.rmtree(_dir(pid), ignore_errors=True)
