"""Top-level package for save_image_to_webdav."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """ComfyUI_save_image_to_dav"""
__email__ = "goldwins520@gmail.com"
__version__ = "0.0.1"

from .src.save_image_to_webdav.nodes import NODE_CLASS_MAPPINGS
from .src.save_image_to_webdav.nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"
