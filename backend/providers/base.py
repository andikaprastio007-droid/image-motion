class VisionProvider:
    name = "base"
    def analyze(self, image_path):
        raise NotImplementedError

class PromptProvider:
    name = "base"
    def generate(self, analysis, stock_safe=True):
        raise NotImplementedError

class VideoProvider:
    name = "base"
    is_ai = False
    def generate(self, image_path, out_path, variation, opts):
        raise NotImplementedError
