"""Color extraction from images for accent color selection.

Dependencies:
    - Pillow (required): pip install Pillow
    - colorthief (optional): pip install colorthief — improves palette quality

Fallback behavior:
    If Pillow is not installed, all functions raise ImportError.
    If colorthief is not installed, falls back to Pillow-based quantize.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Visual tone -> preset accent color mapping (for grayscale / low-saturation)
_VISUAL_TONE_PRESETS: dict[str, str] = {
    "冷色调": "#3a7bd5",
    "暖色调": "#e07c3e",
    "霓虹": "#ff00ff",
    "高对比": "#ff4444",
    "柔和": "#7dd3a0",
    "自然": "#8b7355",
    "奢华": "#d4a853",
    "极简": "#ffffff",
    "未来感": "#00e5ff",
    "活力": "#ff6b6b",
    "宁静": "#6b9bd2",
}

_DEFAULT_ACCENT = "#7dd3a0"


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def extract_palette(image_path: str, num_colors: int = 5) -> list[str]:
    """Extract dominant palette from an image.

    Args:
        image_path: Path to the image file.
        num_colors: Number of dominant colors to return.

    Returns:
        List of hex color strings, e.g. ["#1a1a2e", "#7dd3a0", ...].
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Try colorthief first (better quantization)
    try:
        from colorthief import ColorThief
        ct = ColorThief(str(path))
        palette = ct.get_palette(color_count=num_colors, quality=1)
        return [_rgb_to_hex(r, g, b) for r, g, b in palette]
    except ImportError:
        logger.debug("colorthief not available, falling back to Pillow quantize")
    except Exception as e:
        logger.warning("colorthief failed: %s, falling back to Pillow", e)

    # Fallback: Pillow quantize
    from PIL import Image
    img = Image.open(path).convert("RGB")
    img.thumbnail((200, 200))
    quantized = img.quantize(colors=num_colors, method=2)
    palette_data = quantized.getpalette()
    if not palette_data:
        raise RuntimeError("Failed to extract palette from image")

    colors = []
    for i in range(num_colors):
        r, g, b = palette_data[i * 3], palette_data[i * 3 + 1], palette_data[i * 3 + 2]
        colors.append(_rgb_to_hex(r, g, b))
    return colors


def pick_accent_color(palette: list[str], visual_tone: str = "") -> str:
    """Pick the best accent color from a palette.

    Strategy:
        1. Filter out near-black and near-white colors.
        2. Among remaining, prefer higher saturation + sufficient contrast
           against dark backgrounds (luminance 0.15-0.7).
        3. If all colors are too dark/light/desaturated (grayscale image),
           fall back to a preset based on visual_tone.

    Args:
        palette: List of hex color strings from extract_palette.
        visual_tone: Description of the image's visual tone (for preset fallback).

    Returns:
        Hex color string for the accent.
    """
    if not palette:
        return _preset_for_tone(visual_tone)

    candidates = []  # (hex, saturation, luminance)
    for hex_color in palette:
        r, g, b = _hex_to_rgb(hex_color)
        h, s, l = _rgb_to_hsl(r, g, b)
        if l < 0.08 or l > 0.92:
            continue
        candidates.append((hex_color, s, l))

    if not candidates:
        logger.info("All palette colors too extreme, using preset for tone=%s", visual_tone)
        return _preset_for_tone(visual_tone)

    # Score: prioritize high saturation and luminance in 0.15-0.7 range
    scored = []
    for hex_color, s, l in candidates:
        sat_score = s
        if 0.15 <= l <= 0.7:
            contrast_score = 1.0 - abs(l - 0.4) / 0.55
        else:
            contrast_score = max(0, 0.3 - abs(l - 0.4))
        score = sat_score * 0.6 + contrast_score * 0.4
        scored.append((hex_color, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[0][0]

    best_hsl = _hex_to_hsl(best)
    if best_hsl[1] < 0.05:
        logger.info("Best color too desaturated (s=%.2f), using preset", best_hsl[1])
        return _preset_for_tone(visual_tone)

    return best


def adjust_for_contrast(hex_color: str, target_luminance_min: float = 0.4) -> str:
    """Adjust a color to ensure minimum luminance for dark backgrounds.

    If the color is too dark, lighten it until it meets the target.
    If already bright enough, return as-is.

    Args:
        hex_color: Input hex color string.
        target_luminance_min: Minimum luminance target (0-1).

    Returns:
        Adjusted hex color string.
    """
    r, g, b = _hex_to_rgb(hex_color)
    h, s, l = _rgb_to_hsl(r, g, b)

    if l >= target_luminance_min:
        return hex_color

    new_l = target_luminance_min
    new_r, new_g, new_b = _hsl_to_rgb(h, s, new_l)
    return _rgb_to_hex(new_r, new_g, new_b)


def hex_to_rgba(hex_color: str, alpha: float = 0.3) -> str:
    """Convert hex color to rgba string.

    Args:
        hex_color: Hex color string (e.g. "#7dd3a0").
        alpha: Alpha value (0-1).

    Returns:
        rgba string (e.g. "rgba(125, 211, 160, 0.3)").
    """
    r, g, b = _hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _preset_for_tone(visual_tone: str) -> str:
    for keyword, color in _VISUAL_TONE_PRESETS.items():
        if keyword in visual_tone:
            return color
    return _DEFAULT_ACCENT


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    r, g, b = _hex_to_rgb(hex_color)
    return _rgb_to_hsl(r, g, b)


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(rf, gf, bf), min(rf, gf, bf)
    l = (mx + mn) / 2.0

    if mx == mn:
        h, s = 0.0, 0.0
    else:
        d = mx - mn
        s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == rf:
            h = (gf - bf) / d + (6 if gf < bf else 0)
        elif mx == gf:
            h = (bf - rf) / d + 2
        else:
            h = (rf - gf) / d + 4
        h /= 6.0

    return h * 360.0, s, l


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    h /= 360.0

    if s == 0:
        r = g = b = l
    else:
        def _hue2rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = _hue2rgb(p, q, h + 1 / 3)
        g = _hue2rgb(p, q, h)
        b = _hue2rgb(p, q, h - 1 / 3)

    return (round(r * 255), round(g * 255), round(b * 255))
