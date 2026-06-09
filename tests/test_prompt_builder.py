import pytest
from agent.prompt_builder import build_image_prompt, build_video_prompt, apply_modification

def test_build_image_prompt_static():
    """Should generate prompt for static product image"""
    product = {"name": "智能门铃", "desc": "高清摄像", "style": "科技感"}
    result = build_image_prompt(product, "static")
    assert "智能门铃" in result
    assert "高清摄像" in result
    assert "悬浮展示" in result

def test_build_image_prompt_dynamic():
    """Should generate prompt for dynamic product image"""
    product = {"name": "智能门铃", "desc": "高清摄像", "style": "科技感"}
    result = build_image_prompt(product, "dynamic")
    assert "智能门铃" in result
    assert "工作状态" in result

def test_build_image_prompt_invalid_type():
    """Should raise ValueError for invalid image_type"""
    product = {"name": "智能门铃", "desc": "高清摄像", "style": "科技感"}
    with pytest.raises(ValueError, match="Invalid image_type"):
        build_image_prompt(product, "invalid")

def test_build_video_prompt():
    """Should generate video transition prompt"""
    result = build_video_prompt("产品悬浮展示", "产品工作状态")
    assert "transition" in result.lower()
    assert len(result) > 50  # Should be detailed enough

def test_apply_modification():
    """Should apply user modification to prompt"""
    original = "A smart doorbell, dark background"
    result = apply_modification(original, "white background")
    assert "white background" in result
    assert "smart doorbell" in result

def test_apply_modification_empty_original():
    """Should raise ValueError for empty original prompt"""
    with pytest.raises(ValueError, match="original_prompt cannot be empty"):
        apply_modification("", "modification")

def test_apply_modification_empty_modification():
    """Should raise ValueError for empty modification"""
    with pytest.raises(ValueError, match="modification cannot be empty"):
        apply_modification("original", "")
