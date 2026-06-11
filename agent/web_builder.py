import json
import logging
from string import Template
from typing import Optional

from agent.config import TEMPLATES_DIR

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = TEMPLATES_DIR / "hero_shot.html"


def _generate_copy(analysis: dict) -> dict:
    """基于图片分析生成文案"""
    subject = analysis.get("subject", "创作")
    mood = analysis.get("mood", "独特")
    action = analysis.get("action", "")
    scene = analysis.get("scene", "")
    
    # 生成标题
    title = f"Experience {mood}"
    
    # 生成描述
    if action:
        description = f"A visual journey capturing {subject} — {action}"
    else:
        description = f"A visual journey through {subject}"
    
    return {
        "tag": "AI-Generated Motion",
        "title": title,
        "subtitle": subject,
        "description": description,
        "cta_primary": "Watch Now",
        "cta_secondary": "Learn More"
    }


def generate_player_html(
    frame_count: int, 
    fps: int = 24, 
    title: str = "Hero Shot",
    analysis: Optional[dict] = None
) -> str:
    """生成精美展示网页 HTML

    Args:
        frame_count: 帧图片总数
        fps: 播放帧率
        title: 页面标题
        analysis: 图片分析结果（用于生成文案）

    Returns:
        完整的 HTML 字符串
    """
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    if fps <= 0:
        raise ValueError("fps must be positive")

    duration = f"{frame_count // fps}:{frame_count % fps:02d}"
    
    # 生成文案
    if analysis:
        copy = _generate_copy(analysis)
    else:
        copy = {
            "tag": "AI-Generated Motion",
            "title": title,
            "subtitle": "",
            "description": "AI-crafted motion art that captures the essence of creativity",
            "cta_primary": "Watch Now",
            "cta_secondary": "Learn More"
        }

    logger.info(
        "Generating player HTML: frame_count=%d, fps=%d, title=%s",
        frame_count, fps, title,
    )

    template_text = _TEMPLATE_PATH.read_text(encoding="utf-8")
    tmpl = Template(template_text)
    return tmpl.safe_substitute(
        title=title,
        frame_count=frame_count,
        fps=fps,
        duration=duration,
        tag=copy["tag"],
        hero_title=copy["title"],
        subtitle=copy["subtitle"],
        description=copy["description"],
        cta_primary=copy["cta_primary"],
        cta_secondary=copy["cta_secondary"],
    )
