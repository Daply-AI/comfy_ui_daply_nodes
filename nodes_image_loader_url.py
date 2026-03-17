"""Image Loader URL node — load images from URLs or local paths."""
from __future__ import annotations

from io import BytesIO
import os

import numpy as np
import requests
import torch
from PIL import Image, ImageOps, ImageSequence


def _convert_webp_to_png(img: Image.Image) -> Image.Image:
    buf = BytesIO()
    save_mode = "RGBA" if "A" in img.getbands() else "RGB"
    img.convert(save_mode).save(buf, format="PNG")
    buf.seek(0)
    return Image.open(buf)


def _normalise(img: Image.Image, output_format: str) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    if output_format == "RGBA":
        return img.convert("RGBA")
    if output_format == "Grayscale":
        return img.convert("L")
    return img.convert("RGB")


def pil2tensor(
    img: Image.Image,
    output_format: str = "RGB",
) -> tuple[torch.Tensor, torch.Tensor]:
    output_images: list[torch.Tensor] = []
    output_masks: list[torch.Tensor] = []
    for frame in ImageSequence.Iterator(img):
        if frame.mode == "I":
            frame = frame.point(lambda v: v * (1 / 255))
        if getattr(img, "format", "") == "WEBP":
            frame = _convert_webp_to_png(frame)
        if "A" in frame.getbands():
            alpha = np.array(frame.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(alpha)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32)
        frame = _normalise(frame, output_format)
        arr = np.array(frame).astype(np.float32) / 255.0
        output_images.append(torch.from_numpy(arr)[None,])
        output_masks.append(mask.unsqueeze(0))
    if len(output_images) > 1:
        return torch.cat(output_images, dim=0), torch.cat(output_masks, dim=0)
    return output_images[0], output_masks[0]


def load_image(source: str) -> tuple[Image.Image, str]:
    source = source.strip()
    if not source:
        raise ValueError("Empty image source.")
    if source.startswith("http://") or source.startswith("https://"):
        resp = requests.get(source, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        img.load()
        name = source.split("?")[0].rstrip("/").split("/")[-1] or "image"
    else:
        if not os.path.isfile(source):
            raise FileNotFoundError(f"Local file not found: {source}")
        img = Image.open(source)
        name = os.path.basename(source)
    return img, name


def _effective_name(name: str, did_convert: bool) -> str:
    if did_convert and name.lower().endswith(".webp"):
        return name[:-5] + ".png"
    return name


class DaplyImageLoaderUrl:
    OUTPUT_FORMATS = ["RGB", "RGBA", "Grayscale"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "urls_or_paths": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                        "placeholder": (
                            "One source per line:\n"
                            "https://example.com/photo.jpg\n"
                            "/absolute/local/path/image.png"
                        ),
                    },
                ),
                "output_format": (cls.OUTPUT_FORMATS, {"default": "RGB"}),
                "convert_webp_to_png": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "STRING")
    RETURN_NAMES = ("image", "mask", "count", "filenames")
    FUNCTION = "load"
    CATEGORY = "image"
    DESCRIPTION = (
        "Load one or more images from URLs or local paths (one per line). "
        "Supports WebP→PNG conversion, animated frames, RGB/RGBA/Grayscale."
    )

    def load(
        self,
        urls_or_paths: str,
        output_format: str = "RGB",
        convert_webp_to_png: bool = True,
    ):
        sources = [s.strip() for s in urls_or_paths.splitlines() if s.strip()]
        if not sources:
            raise ValueError("No image sources provided.")
        all_images: list[torch.Tensor] = []
        all_masks: list[torch.Tensor] = []
        names: list[str] = []
        for src in sources:
            img, raw_name = load_image(src)
            is_webp = (
                getattr(img, "format", "").upper() == "WEBP"
                or raw_name.lower().endswith(".webp")
            )
            did_convert = False
            if convert_webp_to_png and is_webp:
                img = _convert_webp_to_png(img)
                did_convert = True
            img_t, mask_t = pil2tensor(img, output_format)
            all_images.append(img_t)
            all_masks.append(mask_t)
            display_name = _effective_name(raw_name, did_convert)
            frame_count = img_t.shape[0]
            names.extend([display_name] * frame_count)
        batched_images = torch.cat(all_images, dim=0)
        batched_masks = torch.cat(all_masks, dim=0)
        total = batched_images.shape[0]
        filenames_str = "\n".join(names)
        return (batched_images, batched_masks, total, filenames_str)


NODE_CLASS_MAPPINGS = {"DaplyImageLoaderUrl": DaplyImageLoaderUrl}
NODE_DISPLAY_NAME_MAPPINGS = {"DaplyImageLoaderUrl": "Daply Image Loader URL"}
