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
    """Should include play button"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "toggle()" in html
    assert "btn-primary" in html


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


def test_generate_player_html_has_head_and_body():
    """Should contain proper head and body sections"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "<head>" in html
    assert "</head>" in html
    assert "<body>" in html
    assert "</body>" in html


def test_generate_player_html_has_meta_charset():
    """Should include UTF-8 charset meta tag"""
    html = generate_player_html(frame_count=10, fps=24)
    assert '<meta charset="UTF-8">' in html


def test_generate_player_html_has_viewport_meta():
    """Should include responsive viewport meta tag"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "viewport" in html
    assert "width=device-width" in html


def test_generate_player_html_has_script_tag():
    """Should contain a script tag with player logic"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "<script>" in html
    assert "</script>" in html
    assert "requestAnimationFrame" in html


def test_generate_player_html_has_style_tag():
    """Should contain a style tag with CSS"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "<style>" in html
    assert "</style>" in html


def test_generate_player_html_has_canvas_element():
    """Should include a canvas element for rendering"""
    html = generate_player_html(frame_count=10, fps=24)
    assert '<canvas id="bg">' in html


def test_generate_player_html_has_stats():
    """Should display frame count, fps, and duration in stats"""
    html = generate_player_html(frame_count=48, fps=24)
    assert "Frames" in html
    assert "Frame Rate" in html
    assert "Duration" in html
    assert "48" in html
    assert "24fps" in html


def test_generate_player_html_custom_title():
    """Should use custom title in header and document title"""
    html = generate_player_html(frame_count=10, fps=24, title="My Project")
    assert "<title>My Project</title>" in html
    assert 'class="logo">My Project<' in html


def test_generate_player_html_has_loader():
    """Should include a loading overlay"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "loader" in html
    assert "Loading" in html


def test_generate_player_html_has_hero_section():
    """Should include hero section with content"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "hero" in html
    assert "hero-tag" in html
    assert "hero-actions" in html


def test_generate_player_html_has_stats_bar():
    """Should include fixed stats bar at bottom"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "stat-value" in html
    assert "stat-label" in html
    assert "AI" in html
    assert "Generated" in html


def test_generate_player_html_duration_calculation():
    """Should calculate correct duration string from frame_count and fps"""
    html = generate_player_html(frame_count=50, fps=24)
    assert "2:02" in html


def test_generate_player_html_with_analysis():
    """Should use analysis data to generate contextual content"""
    analysis = {
        "subject": "蓝紫色短发动漫少女",
        "action": "手指轻触嘴唇",
        "scene": "抽象泼墨背景",
        "mood": "神秘"
    }
    html = generate_player_html(frame_count=10, fps=24, title="Test", analysis=analysis)
    assert "神秘" in html
    assert "蓝紫色短发动漫少女" in html


def test_generate_player_html_has_glass_effects():
    """Should include glass morphism effects"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "backdrop-filter" in html
    assert "blur(12px)" in html


def test_generate_player_html_has_animations():
    """Should include CSS animations"""
    html = generate_player_html(frame_count=10, fps=24)
    assert "@keyframes" in html
    assert "fadeUp" in html
    assert "animation:" in html
