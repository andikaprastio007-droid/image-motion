import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE = Path(__file__).parent
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "3000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
AI_PROVIDER = os.getenv("AI_PROVIDER", "").lower()
AI_API_KEY = os.getenv("AI_API_KEY", "")
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "").lower()
VIDEO_API_KEY = os.getenv("VIDEO_API_KEY", "")
DEFAULT_DURATION = int(os.getenv("DEFAULT_DURATION", "8"))
PROJECTS = BASE / "projects"
LOGS = BASE / "logs"
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp"}
MAX_BYTES = 15 * 1024 * 1024
for d in (PROJECTS, LOGS):
    d.mkdir(exist_ok=True)
