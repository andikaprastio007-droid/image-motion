from PIL import Image, ImageStat
from .base import VisionProvider, PromptProvider
from ..services import prompt_engine

def _tone(v):
    return "dark low-key" if v < 85 else "bright high-key" if v > 170 else "balanced mid-tone"

class LocalVision(VisionProvider):
    name = "local"
    def analyze(self, image_path):
        im = Image.open(image_path).convert("RGB")
        w, h = im.size
        small = im.resize((64, 64))
        lum = ImageStat.Stat(small.convert("L")).mean[0]
        top = ImageStat.Stat(small.crop((0, 0, 64, 21))).mean
        bot = ImageStat.Stat(small.crop((0, 43, 64, 64))).mean
        q = im.resize((120, 120)).quantize(5).convert("RGB")
        cols = ["#%02x%02x%02x" % c for _, c in sorted(q.getcolors(), reverse=True)[:5]]
        ratio = w / h
        orient = "landscape" if ratio > 1.2 else "portrait" if ratio < 0.85 else "square"
        warm = ImageStat.Stat(small).mean
        temp = "warm" if warm[0] > warm[2] + 12 else "cool" if warm[2] > warm[0] + 12 else "neutral"
        gradient = abs(sum(top) - sum(bot)) > 60
        return {
            "subject": "main subject of the original image (identity preserved)",
            "environment": "scene as shown in the source image",
            "foreground": "closest elements, keep stable",
            "midground": "primary subject area",
            "background": "distant elements, candidates for gentle drift",
            "lighting": f"{_tone(lum)} lighting, {temp} color temperature",
            "colors": cols,
            "composition": f"{orient} {w}x{h}" + (", strong top/bottom tonal gradient" if gradient else ""),
            "camera_perspective": "as in source image",
            "depth": "layered depth with parallax potential" if gradient else "moderate depth",
            "motion_candidates": ["slow camera push-in", "background drift", "light shimmer", "airborne particles"],
            "static_elements": ["main subject geometry", "text and logos", "faces", "architecture lines"],
            "risk_elements": ["fine details may flicker", "hands/faces may deform under motion"],
            "orientation": orient, "width": w, "height": h,
            "source": "local-fallback (no AI vision; edit fields in Prompt Lab for better prompts)",
        }

class LocalPrompt(PromptProvider):
    name = "local"
    def generate(self, analysis, stock_safe=True):
        return prompt_engine.build_variations(analysis, stock_safe)
