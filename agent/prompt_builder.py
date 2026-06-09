"""Prompt generation for image and video creation"""


def build_image_prompt(product: dict, image_type: str) -> str:
    """生成图片 Prompt 初稿

    Args:
        product: 产品信息 {"name": "...", "desc": "...", "style": "..."}
        image_type: "static" (静态展示) 或 "dynamic" (动态/工作状态)
    """
    name = product.get("name", "产品")
    desc = product.get("desc", "")
    style = product.get("style", "商业产品摄影")

    if image_type not in ("static", "dynamic"):
        raise ValueError(f"Invalid image_type: {image_type}. Must be 'static' or 'dynamic'")

    if image_type == "static":
        return (
            f"Ultra realistic product photography, {name}, {desc}, "
            f"悬浮展示, dark cinematic background, "
            f"studio lighting, premium technology aesthetic, 8k, {style}"
        )
    else:  # dynamic
        return (
            f"{name} in working state, {desc}, "
            f"工作状态, modern apartment entrance, subtle glowing indicator, "
            f"premium lifestyle scene, cinematic composition, 8k, {style}"
        )


def build_video_prompt(img1_desc: str, img2_desc: str) -> str:
    """生成视频过渡 Prompt

    Args:
        img1_desc: 首帧描述
        img2_desc: 尾帧描述
    """
    return (
        f"A premium product slowly rotates in a dark cinematic environment. "
        f"The camera pushes forward as the device transitions naturally from {img1_desc} "
        f"toward {img2_desc}. "
        f"Soft blue lighting accents appear. The product activates and glows subtly. "
        f"Smooth motion. High-end commercial style. 5 seconds."
    )


def apply_modification(original_prompt: str, modification: str) -> str:
    """根据用户修改请求调整 Prompt

    Args:
        original_prompt: 原始 Prompt
        modification: 用户修改描述（如"换白色背景"）
    """
    if not original_prompt:
        raise ValueError("original_prompt cannot be empty")
    if not modification:
        raise ValueError("modification cannot be empty")
    return f"{original_prompt}, {modification}"
