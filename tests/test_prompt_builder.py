import pytest
from agent.prompt_builder import build_image_prompt, build_video_prompt, apply_modification

def test_build_image_prompt_static():
    """Should generate prompt for static product image"""
    product = {"name": "智能门铃", "desc": "高清摄像", "style": "科技感"}
    result = build_image_prompt(product, "static")
    assert "智能门铃" in result
    assert "高清摄像" in result
    assert "悬浮展示" in result or "精致状态" in result

def test_build_image_prompt_dynamic():
    """Should generate prompt for dynamic product image"""
    product = {"name": "智能门铃", "desc": "高清摄像", "style": "科技感"}
    result = build_image_prompt(product, "dynamic")
    assert "智能门铃" in result
    assert "工作状态" in result or "爆炸" in result

def test_build_video_prompt():
    """Should generate video transition prompt"""
    result = build_video_prompt("产品悬浮展示", "产品工作状态")
    assert "过渡" in result or "transition" in result.lower()
    assert len(result) > 50  # Should be detailed enough

def test_apply_modification():
    """Should apply user modification to prompt"""
    original = "A smart doorbell, dark background"
    result = apply_modification(original, "换成白色背景")
    assert "白色背景" in result or "white background" in result.lower()
