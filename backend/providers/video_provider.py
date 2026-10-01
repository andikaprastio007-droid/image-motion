from .base import VideoProvider
from ..utils import ffmpeg

class MockVideo(VideoProvider):
    """FFmpeg motion preview (Ken Burns). BUKAN AI video generation."""
    name = "mock-ffmpeg"
    is_ai = False
    def generate(self, image_path, out_path, variation, opts):
        ffmpeg.render(image_path, out_path, variation.get("ffmpeg_motion", "push_in"),
                      opts["ratio"], opts["duration"], opts["fps"])

class ExternalVideo(VideoProvider):
    """Tempat menyambungkan API image-to-video. Isi generate() sesuai provider."""
    name = "external"
    is_ai = True
    def __init__(self, key): self.key = key
    def generate(self, image_path, out_path, variation, opts):
        raise RuntimeError("Adapter video eksternal belum diimplementasikan. Gunakan mock mode.")

def get_video_provider(name, key):
    return ExternalVideo(key) if name and key else MockVideo()
