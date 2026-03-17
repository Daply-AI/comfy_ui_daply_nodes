# Comfy UI Daply Nodes

ComfyUI custom nodes by Daply. One package, multiple nodes — install once, get all.

**Nodes included**
- **Daply Image Loader URL** — Load images from URLs or local paths (one per line), batched IMAGE + MASK. WebP→PNG, animated support, RGB/RGBA/Grayscale.

---

## Installation

**ComfyUI Manager**  
Manager → Install Custom Nodes → search **Comfy UI Daply Nodes** (or **Daply Image Loader URL**) → Install.

**Manual**

1. Clone into your ComfyUI custom nodes folder so this repo is **the** node folder:
   ```text
   cd ComfyUI/custom_nodes
   git clone https://github.com/Daply-AI/comfy_ui_daply_nodes.git
   ```
2. Install dependencies:
   ```bash
   pip install -r comfy_ui_daply_nodes/requirements.txt
   ```
3. Restart ComfyUI. Nodes appear under **image** (and any other categories you add).

---

## Adding more nodes

1. Create `nodes_<name>.py` with your node class and at the end:
   ```python
   NODE_CLASS_MAPPINGS = {"YourNodeName": YourNodeClass}
   NODE_DISPLAY_NAME_MAPPINGS = {"YourNodeName": "Display Name"}
   ```
2. In `__init__.py`, add your module to `_NODE_MODULES`:
   ```python
   from . import nodes_image_loader_url
   from . import nodes_my_tool
   _NODE_MODULES = (nodes_image_loader_url, nodes_my_tool)
   ```
3. Restart ComfyUI.

---

## License

MIT — see [LICENSE.txt](LICENSE.txt).
