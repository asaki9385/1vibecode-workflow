import json
import logging
from string import Template
from typing import Optional

from agent.config import TEMPLATES_DIR

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = TEMPLATES_DIR / "hero_shot.html"

# Design direction mapping: subject_type → (font_heading, font_body, accent_color, accent_glow, font_import)
DESIGN_DIRECTIONS = {
    "anime_character": (
        "Clash Display", "Satoshi", "#ff00ff", "rgba(255, 0, 255, 0.3)",
        "https://fonts.googleapis.com/css2?family=Satoshi:wght@300;400;500;700&display=swap"
    ),
    "landscape": (
        "Fraunces", "DM Sans", "#8b7355", "rgba(139, 115, 85, 0.3)",
        "https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;700&display=swap"
    ),
    "person": (
        "Playfair Display", "Noto Sans SC", "#7dd3a0", "rgba(125, 211, 160, 0.3)",
        "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Noto+Sans+SC:wght@300;400;500;700&display=swap"
    ),
    "product": (
        "Cormorant Garamond", "Outfit", "#d4a853", "rgba(212, 168, 83, 0.3)",
        "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,700;1,400&family=Outfit:wght@300;400;500;700&display=swap"
    ),
    "abstract": (
        "Space Mono", "Manrope", "#ffffff", "rgba(255, 255, 255, 0.3)",
        "https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Manrope:wght@300;400;500;700&display=swap"
    ),
    "architecture": (
        "Bebas Neue", "Inter", "#6b7280", "rgba(107, 114, 128, 0.3)",
        "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;700&display=swap"
    ),
    "food": (
        "Lora", "Noto Sans SC", "#c2410c", "rgba(194, 65, 12, 0.3)",
        "https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&family=Noto+Sans+SC:wght@300;400;500;700&display=swap"
    ),
}

# Animation presets: style keyword → (ease, duration, stagger, scale, rotation)
ANIMATION_PRESETS = {
    "cyberpunk": ("expo.out", "0.5", "0.15", "0.95", "0"),
    "tech": ("expo.out", "0.5", "0.15", "0.95", "0"),
    "minimalist": ("power1.inOut", "1.2", "0.3", "1", "0"),
    "gallery": ("power1.inOut", "1.2", "0.3", "1", "0"),
    "organic": ("sine.inOut", "0.9", "0.25", "1", "2"),
    "natural": ("sine.inOut", "0.9", "0.25", "1", "2"),
    "luxury": ("power3.out", "1.0", "0.3", "1", "0"),
    "editorial": ("power3.out", "1.0", "0.3", "1", "0"),
}

# Fallback
DEFAULT_ANIMATION = ("power2.out", "0.8", "0.2", "1", "0")


def get_design_direction(subject_type: str) -> tuple[str, str, str, str, str]:
    """根据 subject_type 返回设计方向 (font_heading, font_body, accent_color, accent_glow, font_import)"""
    return DESIGN_DIRECTIONS.get(subject_type, DESIGN_DIRECTIONS.get("person"))


def get_animation_preset(keywords: list[str]) -> tuple[str, str, str, str, str]:
    """根据 style_profile.keywords 返回动画预设 (ease, duration, stagger, scale, rotation)

    取第一个匹配的关键词，若无匹配则返回默认值。
    """
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in ANIMATION_PRESETS:
            return ANIMATION_PRESETS[kw_lower]
    return DEFAULT_ANIMATION


def decide_params(analysis):
    """根据 image_analysis 自动决定参数值"""
    style = analysis.get("style_profile", {})
    keywords = style.get("keywords", [])
    mood = analysis.get("mood", "")

    params = {
        "deco_density": "normal",
        "anim_energy": "moderate",
        "layout_compact": False,
        "text_overlay": False,
        "parallax_depth": "subtle"
    }

    if "minimalist" in keywords:
        params["deco_density"] = "none"
        params["anim_energy"] = "calm"
    elif "cyberpunk" in keywords or "dark art" in keywords:
        params["deco_density"] = "sparse"
        params["anim_energy"] = "high"
        params["text_overlay"] = True

    if "温暖" in mood or "柔和" in mood:
        params["anim_energy"] = "calm"

    return params


def generate_player_html(
    frame_count: int,
    fps: int = 24,
    title: str = "Hero Shot",
    copy: Optional[dict] = None,
    font_heading: Optional[str] = None,
    font_body: Optional[str] = None,
    accent_color: Optional[str] = None,
    accent_glow: Optional[str] = None,
    font_import: Optional[str] = None,
    anim_ease: Optional[str] = None,
    anim_duration: Optional[str] = None,
    anim_stagger: Optional[str] = None,
    gsap_scale: str = "1",
    gsap_rotation: str = "0",
    analysis: Optional[dict] = None,
) -> str:
    """生成精美展示网页 HTML

    Args:
        frame_count: 帧图片总数
        fps: 播放帧率
        title: 页面标题
        copy: 文案字典 {tag, title, subtitle, description, cta_primary, cta_secondary}
        font_heading: 标题字体名称
        font_body: 正文字体名称
        accent_color: 强调色 (hex)
        accent_glow: 强调色发光 (rgba)
        font_import: Google Fonts import URL
        anim_ease: GSAP 缓动函数 (如 "power2.out")
        anim_duration: GSAP 入场动画基础时长 (秒)
        anim_stagger: GSAP 元素间错落延迟 (秒)
        gsap_scale: GSAP h1 入场缩放 (如 "0.95" for cyberpunk)
        gsap_rotation: GSAP h1 入场旋转角度 (如 "2" for organic)
        analysis: 图片分析结果（仅在 copy 未提供时用于回退）

    Returns:
        完整的 HTML 字符串
    """
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    if fps <= 0:
        raise ValueError("fps must be positive")

    duration = f"{frame_count // fps}:{frame_count % fps:02d}"

    # 使用传入的 copy 或回退到 analysis 生成
    if copy:
        page_copy = copy
    elif analysis:
        page_copy = _generate_copy(analysis)
    else:
        page_copy = {
            "tag": "AI-Generated Motion",
            "title": title,
            "subtitle": "",
            "description": "AI-crafted motion art that captures the essence of creativity",
            "cta_primary": "Watch Now",
            "cta_secondary": "Learn More"
        }

    # 设计方向：优先使用传入值，否则从 analysis 获取
    if font_heading and font_body and accent_color and accent_glow and font_import:
        fh, fb, ac, ag, fi = font_heading, font_body, accent_color, accent_glow, font_import
    elif analysis:
        subject_type = analysis.get("subject_type", "other")
        fh, fb, ac, ag, fi = get_design_direction(subject_type)
    else:
        fh, fb, ac, ag, fi = get_design_direction("person")

    # 动画参数：优先使用传入值，否则从 style_profile.keywords 获取
    if anim_ease and anim_duration and anim_stagger:
        ae, ad, ast = anim_ease, anim_duration, anim_stagger
    elif analysis:
        keywords = analysis.get("style_profile", {}).get("keywords", [])
        ae, ad, ast = get_animation_preset(keywords)
    else:
        ae, ad, ast = DEFAULT_ANIMATION

    logger.info(
        "Generating player HTML: frame_count=%d, fps=%d, title=%s, font=%s",
        frame_count, fps, title, fh,
    )

    template_text = _TEMPLATE_PATH.read_text(encoding="utf-8")
    tmpl = Template(template_text)
    return tmpl.safe_substitute(
        title=title,
        frame_count=frame_count,
        fps=fps,
        duration=duration,
        tag=page_copy.get("tag", ""),
        hero_title=page_copy.get("title", title),
        subtitle=page_copy.get("subtitle", ""),
        description=page_copy.get("description", ""),
        cta_primary=page_copy.get("cta_primary", "Watch Now"),
        cta_secondary=page_copy.get("cta_secondary", "Learn More"),
        font_heading=fh,
        font_body=fb,
        accent_color=ac,
        accent_glow=ag,
        font_import=fi,
        anim_ease=ae,
        anim_duration=ad,
        anim_stagger=ast,
        gsap_scale=gsap_scale,
        gsap_rotation=gsap_rotation,
    )


def _generate_copy(analysis: dict) -> dict:
    """基于图片分析生成文案（回退方案，优先使用 agent 传入的 copy）"""
    subject = analysis.get("subject", "创作")
    mood = analysis.get("mood", "独特")
    action = analysis.get("action", "")
    style_keywords = analysis.get("style_keywords", [])

    title = f"Experience {mood}"

    if action:
        description = f"A visual journey capturing {subject} — {action}"
    else:
        description = f"A visual journey through {subject}"

    style_str = " ".join(style_keywords).lower()
    if "photorealistic" in style_str:
        description = f"Photorealistic AI-generated motion art of {subject}"
    elif "anime" in style_str:
        description = f"Anime-style AI motion art: {subject}"
    elif "watercolor" in style_str:
        description = f"Watercolor-inspired AI motion art: {subject}"

    return {
        "tag": "AI-Generated Motion",
        "title": title,
        "subtitle": subject,
        "description": description,
        "cta_primary": "Watch Now",
        "cta_secondary": "Learn More"
    }
