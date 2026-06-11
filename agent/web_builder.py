import logging
from string import Template

from agent.config import TEMPLATES_DIR

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = TEMPLATES_DIR / "hero_shot.html"


def generate_player_html(frame_count: int, fps: int = 24, title: str = "Hero Shot") -> str:
    """生成精美展示网页 HTML

    Args:
        frame_count: 帧图片总数
        fps: 播放帧率
        title: 页面标题

    Returns:
        完整的 HTML 字符串
    """
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    if fps <= 0:
        raise ValueError("fps must be positive")

    duration = f"{frame_count // fps}:{frame_count % fps:02d}"

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
    )
