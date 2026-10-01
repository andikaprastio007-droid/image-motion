import config
from .local_provider import LocalVision, LocalPrompt
from .openai_provider import OpenAIVision
from .anthropic_provider import AnthropicVision
from .video_provider import get_video_provider

def get_vision():
    if config.AI_API_KEY and config.AI_PROVIDER == "openai": return OpenAIVision(config.AI_API_KEY)
    if config.AI_API_KEY and config.AI_PROVIDER == "anthropic": return AnthropicVision(config.AI_API_KEY)
    return LocalVision()

def get_prompter():
    return LocalPrompt()

def get_video():
    return get_video_provider(config.VIDEO_PROVIDER, config.VIDEO_API_KEY)
