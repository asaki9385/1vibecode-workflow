import pytest
from agent.web_builder import generate_player_html


def test_generate_player_html_basic():
    """Should generate valid HTML with frame count and fps"""
    html = generate_player_html(frame_count=123, fps=24)
    assert "<!DOCTYPE html>" in html
    assert "123" in html
    assert "24" in html
    assert "<canvas" in html


def test_generate_player_html_custom_fps():
    """Should use custom fps value"""
    html = generate_player_html(frame_count=60, fps=30)
    assert "60" in html
    assert "30" in html


def test_generate_player_html_has_controls():
    """Should include play button and progress bar"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "playBtn" in html
    assert "progress" in html


def test_generate_player_html_zero_frames():
    """Should raise ValueError for zero frames"""
    with pytest.raises(ValueError, match="frame_count must be positive"):
        generate_player_html(frame_count=0, fps=24)


def test_generate_player_html_negative_fps():
    """Should raise ValueError for negative fps"""
    with pytest.raises(ValueError, match="fps must be positive"):
        generate_player_html(frame_count=10, fps=-1)


def test_generate_player_html_is_complete_html():
    """Should return complete HTML document"""
    html = generate_player_html(frame_count=5, fps=24)
    assert html.strip().startswith("<!DOCTYPE html>")
    assert html.strip().endswith("</html>")
