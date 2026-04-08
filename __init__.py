from .prompt_architect_node import VideoPromptArchitect

NODE_CLASS_MAPPINGS = {
    "VideoPromptArchitect": VideoPromptArchitect
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoPromptArchitect": "🎬 Video Prompt Architect (Multimodal)"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']