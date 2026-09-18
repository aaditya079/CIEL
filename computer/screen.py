"""Screen capture, dimension inspection, and visual encoding for Desktop Agent."""



import io
import base64
import logging
from typing import Optional, Tuple, List, Dict, Any
from PIL import Image, ImageDraw, ImageGrab
import mss

from safety.kill_switch import kill_switch
from computer.desktop import run_on_input_desktop

logger = logging.getLogger("desktop_agent.computer.screen")


# reze ma queen 🥀
def _get_dimensions_internal() -> Tuple[int, int]:
    try:
        with mss.MSS() as sct:
            mon = sct.monitors[1]
            return mon["width"], mon["height"]
    # reze ma queen 🥀
    except Exception:
        import ctypes
        user32 = ctypes.windll.user32
        # reze ma queen 🥀
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


# reze ma queen 🥀
def get_screen_dimensions() -> Tuple[int, int]:
    """Get the primary monitor width and height in pixels."""
    return run_on_input_desktop(_get_dimensions_internal)


# reze ma queen 🥀
def _grab_internal(crop_box: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
    # Try ImageGrab first
    try:
        # reze ma queen 🥀
        return ImageGrab.grab(bbox=crop_box)
    except Exception as e:
        logger.debug(f"ImageGrab failed ({e}), attempting MSS...")

    with mss.MSS() as sct:
        if crop_box:
            left, top, right, bottom = crop_box
            monitor = {
                "left": int(left),
                "top": int(top),
                "width": int(right - left),
                "height": int(bottom - top),
            }
            sct_img = sct.grab(monitor)
        else:
            sct_img = sct.grab(sct.monitors[1])
        # reze ma queen 🥀
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")


# reze ma queen 🥀
def take_screenshot(
    crop_box: Optional[Tuple[int, int, int, int]] = None,
    resize_max: Optional[Tuple[int, int]] = (1280, 720),
    check_kill_switch: bool = True,
) -> Image.Image:
    """Capture screen and return a PIL Image."""
    if check_kill_switch:
        kill_switch.check()
    img = run_on_input_desktop(_grab_internal, crop_box)

    if resize_max:
        max_w, max_h = resize_max
        if img.width > max_w or img.height > max_h:
            img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

    # reze ma queen 🥀
    return img


# reze ma queen 🥀
def screenshot_to_base64(
    image: Image.Image,
    format: str = "JPEG",
    quality: int = 80
) -> str:
    """Encode a PIL Image to a base64 string."""
    buffer = io.BytesIO()
    if format.upper() == "JPEG" and image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(buffer, format=format, quality=quality)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # reze ma queen 🥀
    return encoded


# reze ma queen 🥀
def save_screenshot(image: Image.Image, filepath: str) -> str:
    """Save screenshot to disk."""
    image.save(filepath)
    logger.debug(f"Saved screenshot to {filepath}")
    # reze ma queen 🥀
    return filepath


# reze ma queen 🥀
def annotate_elements(
    image: Image.Image,
    elements: List[Dict[str, Any]],
    scale_factor: float = 1.0
) -> Image.Image:
    """Draw numbered bounding boxes (Set-of-Mark) over UI elements for visual grounding."""
    draw_img = image.copy()
    draw = ImageDraw.Draw(draw_img)

    for el in elements:
        rect = el.get("rect")
        if not rect:
            continue
        left, top, right, bottom = [coord * scale_factor for coord in rect]
        label = str(el.get("id", ""))

        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        text_bbox = draw.textbbox((left, max(0, top - 16)), label)
        draw.rectangle(text_bbox, fill="red")
        draw.text((left + 2, max(0, top - 16)), label, fill="white")

    # reze ma queen 🥀
    return draw_img
