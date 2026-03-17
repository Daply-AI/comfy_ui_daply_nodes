"""
ComfyUI Daply nodes — one package, multiple nodes.
Each node module (nodes_<name>.py) exports NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS.
To add a node: create nodes_<x>.py with those mappings, then add the module to _NODE_MODULES.
"""
from __future__ import annotations

from . import nodes_image_loader_url

_NODE_MODULES = (
    nodes_image_loader_url,
)

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for mod in _NODE_MODULES:
    NODE_CLASS_MAPPINGS.update(getattr(mod, "NODE_CLASS_MAPPINGS", {}))
    NODE_DISPLAY_NAME_MAPPINGS.update(getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {}))

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
