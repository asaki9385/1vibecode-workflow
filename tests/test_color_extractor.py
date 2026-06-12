"""Tests for color_extractor module."""

import pytest
from agent.color_extractor import (
    _hex_to_rgb, _rgb_to_hex, _luminance, _saturation,
    _contrast_ratio, pick_accent_color, get_top_accents,
    adjust_for_contrast, hex_to_rgba, _get_fallback_accent,
)


def test_hex_to_rgb():
    assert _hex_to_rgb("#000000") == (0, 0, 0)
    assert _hex_to_rgb("#ffffff") == (255, 255, 255)
    assert _hex_to_rgb("#7dd3a0") == (125, 211, 160)
    assert _hex_to_rgb("ff00ff") == (255, 0, 255)


def test_rgb_to_hex():
    assert _rgb_to_hex(0, 0, 0) == "#000000"
    assert _rgb_to_hex(255, 255, 255) == "#ffffff"
    assert _rgb_to_hex(125, 211, 160) == "#7dd3a0"


def test_luminance():
    assert _luminance(0, 0, 0) == pytest.approx(0.0, abs=0.01)
    assert _luminance(255, 255, 255) == pytest.approx(1.0, abs=0.01)
    assert _luminance(125, 211, 160) > 0.4


def test_saturation():
    assert _saturation(128, 128, 128) == pytest.approx(0.0, abs=0.01)
    assert _saturation(255, 0, 0) == pytest.approx(1.0, abs=0.01)


def test_contrast_ratio():
    assert _contrast_ratio(1.0, 0.0) == pytest.approx(21.0, abs=0.1)
    assert _contrast_ratio(0.5, 0.5) == pytest.approx(1.0, abs=0.1)


def test_pick_accent_color_empty():
    result = pick_accent_color([], "")
    assert result.startswith("#")


def test_pick_accent_color_filters_black_white():
    palette = ["#000000", "#111111", "#eeeeee", "#ffffff", "#7dd3a0"]
    result = pick_accent_color(palette, "")
    assert result == "#7dd3a0"


def test_pick_accent_color_prefers_saturated():
    palette = ["#808080", "#7dd3a0", "#333333"]
    result = pick_accent_color(palette, "")
    assert result == "#7dd3a0"


def test_pick_accent_color_gray_tone():
    palette = ["#404040", "#808080", "#c0c0c0"]
    result = pick_accent_color(palette, "monochrome minimalist")
    assert result in palette


def test_get_top_accents():
    palette = ["#000000", "#7dd3a0", "#ff00ff", "#ffffff"]
    result = get_top_accents(palette, "", top_n=2)
    assert len(result) == 2
    assert "#000000" not in result
    assert "#ffffff" not in result


def test_get_top_accents_empty():
    result = get_top_accents([], "", top_n=3)
    assert len(result) == 1


def test_adjust_for_contrast_bright():
    color = adjust_for_contrast("#7dd3a0", 0.4)
    assert color == "#7dd3a0"


def test_adjust_for_contrast_dark():
    color = adjust_for_contrast("#111111", 0.4)
    assert color != "#111111"


def test_hex_to_rgba():
    result = hex_to_rgba("#7dd3a0", 0.5)
    assert result == "rgba(125, 211, 160, 0.5)"


def test_fallback_accent():
    assert _get_fallback_accent("cyberpunk neon") == "#ff00ff"
    assert _get_fallback_accent("minimalist gallery") == "#ffffff"
    assert _get_fallback_accent("") == "#7dd3a0"
