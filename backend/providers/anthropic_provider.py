import base64, json, urllib.request
from .base import VisionProvider
from .local_provider import LocalVision

class AnthropicVision(VisionProvider):
    name = "anthropic"
    def __init__(self, key, model="claude-sonnet-4-6"):
        self.key, self.model = key, model
    def analyze(self, image_path):
        base = LocalVision().analyze(image_path)
        try:
            b64 = base64.b64encode(open(image_path, "rb").read()).decode()
            mt = "image/png" if str(image_path).lower().endswith("png") else "image/jpeg"
            body = {"model": self.model, "max_tokens": 1000, "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mt, "data": b64}},
                {"type": "text", "text": "Analyze for image-to-video. Reply ONLY JSON keys: subject, environment, foreground, midground, background, lighting, composition, depth, motion_candidates(list), static_elements(list), risk_elements(list), has_text(bool), has_logo(bool), has_face(bool)."}]}]}
            req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
                {"Content-Type": "application/json", "x-api-key": self.key, "anthropic-version": "2023-06-01"})
            txt = json.loads(urllib.request.urlopen(req, timeout=60).read())["content"][0]["text"]
            base.update(json.loads(txt.replace("```json", "").replace("```", "").strip()))
            base["source"] = "anthropic"
        except Exception as e:
            base["source"] += f" (AI gagal: {type(e).__name__})"
        return base
