import logging, traceback, shutil, time
from flask import Flask, jsonify, request, send_from_directory
import config
from backend.utils import ffmpeg
from backend.services import projects as P, stock
from backend import providers as prov

logging.basicConfig(filename=config.LOGS / "app.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("app")
app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = config.MAX_BYTES

def ok(**kw): return jsonify({"status": "success", **kw})
def fail(msg, code=400): return jsonify({"status": "error", "message": msg}), code

def safe(fn):
    def w(*a, **k):
        try:
            return fn(*a, **k)
        except (ValueError, RuntimeError) as e:
            log.warning("%s: %s", fn.__name__, e)
            return fail(str(e))
        except Exception as e:
            log.error("%s\n%s", fn.__name__, traceback.format_exc())
            if config.DEBUG: traceback.print_exc()
            return fail("Terjadi kesalahan internal. Cek logs/app.log", 500)
    w.__name__ = fn.__name__
    return w

@app.errorhandler(413)
def too_big(e): return fail("File terlalu besar (maks 15MB)", 413)

@app.get("/")
def index(): return app.send_static_file("index.html")

@app.get("/api/health")
def health():
    return ok(ffmpeg=ffmpeg.available(), ffmpeg_message=None if ffmpeg.available() else ffmpeg.MSG,
              vision=prov.get_vision().name, video=prov.get_video().name,
              video_is_ai=prov.get_video().is_ai, debug=config.DEBUG)

@app.post("/api/upload")
@safe
def upload():
    f = request.files.get("image")
    if not f: raise ValueError("Tidak ada file")
    return ok(project_id=P.create(f))

@app.post("/api/analyze")
@safe
def analyze():
    pid = (request.json or {}).get("project_id")
    a = prov.get_vision().analyze(P.input_path(pid))
    P.save(pid, "analysis", a)
    return ok(analysis=a, stock_check=stock.check(a))

@app.post("/api/generate-prompts")
@safe
def gen_prompts():
    d = request.json or {}
    pid = d.get("project_id")
    a = d.get("analysis") or P.load(pid, "analysis")
    if not a: raise ValueError("Jalankan analisis dulu")
    P.input_path(pid)
    if d.get("analysis"): P.save(pid, "analysis", a)
    safe_mode = bool(d.get("stock_safe", True))
    dur = int(d.get("duration", config.DEFAULT_DURATION))
    from backend.services import prompt_engine
    v = prompt_engine.build_variations(a, safe_mode, dur)
    P.save(pid, "prompts", v)
    m = P.load(pid, "metadata", {}); m["stock_safe"] = safe_mode
    m["stock_metadata"] = stock.metadata(a); P.save(pid, "metadata", m)
    return ok(variations=v, stock_check=stock.check(a), stock_metadata=m["stock_metadata"])

@app.post("/api/save-prompts")
@safe
def save_prompts():
    d = request.json or {}
    P.input_path(d.get("project_id"))
    P.save(d["project_id"], "prompts", d.get("variations", []))
    return ok()

@app.post("/api/generate-video")
@safe
def gen_video():
    d = request.json or {}
    pid = d.get("project_id")
    src = P.input_path(pid)
    vs = P.load(pid, "prompts") or []
    v = next((x for x in vs if x["id"] == int(d.get("variation_id", 1))), None)
    if not v: raise ValueError("Variasi tidak ditemukan")
    ratio = d.get("ratio", "16:9"); dur = int(d.get("duration", config.DEFAULT_DURATION)); fps = int(d.get("fps", 24))
    if ratio not in ffmpeg.SIZES or dur not in (5, 8, 10) or fps not in (24, 30): raise ValueError("Opsi tidak valid")
    name = f"v{v['id']}_{ratio.replace(':','x')}_{dur}s_{int(time.time())}.mp4"
    provider = prov.get_video()
    provider.generate(src, P.out_dir(pid) / name, v, {"ratio": ratio, "duration": dur, "fps": fps})
    note = "AI video" if provider.is_ai else "Preview FFmpeg (mock). Ini bukan AI video generation."
    return ok(video=f"/api/projects/{pid}/output/{name}", note=note)

@app.get("/api/projects")
@safe
def list_projects(): return ok(projects=P.listing())

@app.get("/api/projects/<pid>")
@safe
def get_project(pid):
    P.input_path(pid)
    outs = sorted(p.name for p in P.out_dir(pid).glob("*.mp4"))
    return ok(metadata=P.load(pid, "metadata"), analysis=P.load(pid, "analysis"),
              variations=P.load(pid, "prompts"), videos=[f"/api/projects/{pid}/output/{o}" for o in outs])

@app.delete("/api/projects/<pid>")
@safe
def del_project(pid):
    P.delete(pid); return ok()

@app.get("/api/projects/<pid>/image")
@safe
def project_image(pid):
    return send_from_directory(config.PROJECTS / pid, "input.jpg") if P.input_path(pid) else None

@app.get("/api/projects/<pid>/output/<name>")
@safe
def project_video(pid, name):
    P.input_path(pid)
    return send_from_directory(P.out_dir(pid), name)

if __name__ == "__main__":
    if not ffmpeg.available(): print("⚠", ffmpeg.MSG)
    print(f"IMAGE → MOTION STUDIO: http://{config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
