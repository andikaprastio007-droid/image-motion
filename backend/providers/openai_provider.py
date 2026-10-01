import base64, json, urllib.request
from .base import VisionProvider
from .local_provider import LocalVision

class OpenAIVision(VisionProvider):
    """Vision via OpenAI-compatible chat API. Falls back to local on any failure."""
    name = "openai"
    def __init__(self, key, model="gpt-4o-mini", url="https://api.openai.com/v1/chat/completions"):
        self.key, self.model, self.url = key, model, url
    def analyze(self, image_path):
        base = LocalVision().analyze(image_path)
        try:
            b64 = base64.b64encode(open(image_path, "rb").read()).decode()
            body = {"model": self.model, "response_format": {"type": "json_object"}, "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Analyze this image for image-to-video. Return JSON with keys: subject, environment, foreground, midground, background, lighting, composition, depth, motion_candidates(list), static_elements(list), risk_elements(list), has_text(bool), has_logo(bool), has_face(bool)."},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
            req = urllib.request.Request(self.url, json.dumps(body).encode(),
                {"Content-Type": "application/json", "Authorization": "Bearer " + self.key})
            out = json.loads(urllib.request.urlopen(req, timeout=60).read())
            base.update(json.loads(out["choices"][0]["message"]["content"]))
            base["source"] = "openai"
        except Exception as e:
            base["source"] += f" (AI gagal: {type(e).__name__})"
        return base
