import pytest
from agent.prompt_builder import build_regenerate_prompt, build_img2img_prompt, build_video_prompt, apply_modification, generate_ending_options


def test_build_regenerate_prompt_wind():
    """Should generate wind regeneration prompt"""
    result = build_regenerate_prompt("wind")
    assert "re-rendering" in result.lower()
    assert "preserve" in result.lower()
    assert "wind" in result.lower()
    assert "hair" in result.lower()


def test_build_regenerate_prompt_lighting():
    """Should generate lighting regeneration prompt"""
    result = build_regenerate_prompt("lighting")
    assert "light" in result.lower()


def test_build_regenerate_prompt_scene():
    """Should generate scene regeneration prompt"""
    result = build_regenerate_prompt("scene")
    assert "cloud" in result.lower()


def test_build_regenerate_prompt_custom():
    """Should generate custom regeneration prompt"""
    result = build_regenerate_prompt("custom", "add rain atmosphere")
    assert "rain" in result.lower()


def test_build_img2img_prompt_wind():
    """Should generate wind effect prompt"""
    result = build_img2img_prompt("wind")
    assert "wind" in result.lower()
    assert "hair" in result.lower()
    assert "cloak" in result.lower()


def test_build_img2img_prompt_lighting():
    """Should generate lighting effect prompt"""
    result = build_img2img_prompt("lighting")
    assert "light" in result.lower()


def test_build_img2img_prompt_scene():
    """Should generate scene effect prompt"""
    result = build_img2img_prompt("scene")
    assert "cloud" in result.lower()


def test_build_img2img_prompt_custom():
    """Should generate custom effect prompt"""
    result = build_img2img_prompt("custom", "add rain effect")
    assert "rain" in result.lower()


def test_build_video_prompt():
    """Should generate video transition prompt"""
    result = build_video_prompt("wind")
    assert "wind" in result.lower()
    assert len(result) > 50


def test_apply_modification():
    """Should apply user modification to prompt"""
    original = "Add wind effect to hair"
    result = apply_modification(original, "make it stronger")
    assert "wind effect" in result
    assert "make it stronger" in result


def test_apply_modification_empty_original():
    """Should raise ValueError for empty original prompt"""
    with pytest.raises(ValueError, match="original_prompt cannot be empty"):
        apply_modification("", "modification")


def test_apply_modification_empty_modification():
    """Should raise ValueError for empty modification"""
    with pytest.raises(ValueError, match="modification cannot be empty"):
        apply_modification("original", "")


def test_generate_ending_options_panda():
    """Should generate ending options for panda eating bamboo"""
    analysis = {
        "subject": "卡通熊猫",
        "action": "坐着吃竹子",
        "scene": "白色背景",
        "mood": "可爱、满足"
    }
    options = generate_ending_options(analysis)
    assert len(options) >= 2
    assert len(options) <= 3
    for opt in options:
        assert "type" in opt
        assert "description" in opt
        assert "prompt" in opt


def test_generate_ending_options_default():
    """Should provide default options when analysis is empty"""
    options = generate_ending_options({})
    assert len(options) >= 2


def test_generate_ending_options_types():
    """Should include different ending types"""
    analysis = {"subject": "人物", "action": "站立", "scene": "户外", "mood": "平静"}
    options = generate_ending_options(analysis)
    types = [opt["type"] for opt in options]
    assert len(set(types)) >= 2  # At least 2 different types
