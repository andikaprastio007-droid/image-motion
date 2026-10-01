import shutil, subprocess

MSG = "FFmpeg tidak ditemukan. Install FFmpeg di Termux: pkg install ffmpeg"

def available():
    return shutil.which("ffmpeg") is not None

SIZES = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}

def render(src, dst, motion="push_in", ratio="16:9", duration=8, fps=24):
    if not available():
        raise RuntimeError(MSG)
    w, h = SIZES.get(ratio, SIZES["16:9"])
    frames = int(duration * fps)
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    z = {
        "push_in": f"min(1.0+0.0008*on,1.25)",
        "pull_out": f"max(1.25-0.0008*on,1.0)",
        "pan": "1.15",
        "minimal": f"min(1.0+0.0003*on,1.08)",
    }.get(motion, "min(1.0+0.0008*on,1.25)")
    x = f"(iw-iw/zoom)*on/{frames}" if motion == "pan" else cx
    vf = (f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
          f"zoompan=z='{z}':x='{x}':y='{cy}':d={frames}:s={w}x{h}:fps={fps},"
          f"fade=t=in:d=0.5,fade=t=out:st={duration-0.5}:d=0.5,format=yuv420p")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf,
           "-t", str(duration), "-c:v", "libx264", "-preset", "veryfast",
           "-movflags", "+faststart", str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise RuntimeError(r.stderr[-400:])
