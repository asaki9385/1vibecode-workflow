"""Prompt generation for img2img and video creation"""


def build_regenerate_prompt(effect_type: str, custom_desc: str = "") -> str:
    """生成图1的重绘Prompt — 强约束提取参考图全部特征，高画质重渲染

    Args:
        effect_type: 效果类型 - "wind"/"lighting"/"scene"/"custom"
        custom_desc: 自定义效果描述
    """
    base = (
        "EXTREMELY IMPORTANT: This is a reference image recreation task. "
        "You MUST extract and preserve EVERY visual element from the reference image with zero deviation. "
        "Strict requirements:\n"
        "- Character features: exact hair color, hair length, hair style, eye color, eye shape, facial structure, expression, ear shape\n"
        "- Clothing: exact outfit design, fabric textures, colors, patterns, accessories, armor details\n"
        "- Pose: exact body position, limb angles, hand gestures, head tilt\n"
        "- Composition: exact framing, camera angle, subject placement, depth of field\n"
        "- Color palette: exact dominant colors, color temperature, saturation levels\n"
        "- Lighting: exact light direction, shadow placement, highlights, ambient glow\n"
        "- Art style: exact rendering technique, line weight, shading style, texture detail level\n"
        "- Background: exact elements, colors, atmosphere, environmental details\n"
        "- Mood: exact emotional tone, energy level, atmosphere\n"
        "The output MUST be a higher-quality re-rendering of the reference image. "
        "Do NOT add new elements. Do NOT change existing elements. Do NOT reinterpret the scene. "
        "Only improve resolution, detail clarity, and rendering quality."
    )

    extras = {
        "wind": "After preserving all reference elements, add subtle natural wind dynamics: slight hair movement, gentle fabric flutter.",
        "lighting": "After preserving all reference elements, enhance lighting with soft volumetric rays and atmospheric depth.",
        "scene": "After preserving all reference elements, add flowing clouds and environmental movement in background.",
        "custom": f"After preserving all reference elements, {custom_desc}" if custom_desc else ""
    }

    extra = extras.get(effect_type, "")
    return f"{base} {extra}".strip()


def build_img2img_prompt(effect_type: str, custom_desc: str = "") -> str:
    """根据动态效果类型生成图生图 Prompt

    Args:
        effect_type: 效果类型 - "wind"/"lighting"/"scene"/"custom"
        custom_desc: 自定义效果描述（effect_type="custom" 时使用）
    """
    base = "Same character, same art style, same background, maintain consistent design."

    effects = {
        "wind": f"{base} Add dynamic wind effect: hair flowing in the wind, green cloak billowing dramatically, fabric rippling with air movement.",
        "lighting": f"{base} Add dramatic lighting change: golden hour sunlight, warm glow on character, soft shadows, atmospheric light rays.",
        "scene": f"{base} Add scene dynamics: clouds flowing in background, subtle environment movement, atmospheric depth.",
        "custom": f"{base} {custom_desc}" if custom_desc else base
    }

    return effects.get(effect_type, effects["wind"])


def build_video_prompt(effect_type: str) -> str:
    """根据效果类型生成视频过渡 Prompt

    Args:
        effect_type: 动态效果类型
    """
    transitions = {
        "wind": (
            "The anime character stands heroically. Wind begins to blow, "
            "hair and cloak gradually flow with increasing intensity. "
            "Clouds drift across the sky. Camera slowly orbits around the character. "
            "Smooth 24fps animation, 5 seconds, cinematic quality."
        ),
        "lighting": (
            "The anime character is silhouetted against the sky. "
            "Light gradually shifts from dawn to golden hour, "
            "casting warm rays across the character's face and cloak. "
            "Subtle lens flare effects. Camera slowly pushes in. "
            "Smooth 24fps animation, 5 seconds, cinematic quality."
        ),
        "scene": (
            "The anime character stands against a dynamic sky. "
            "Clouds flow and shift, atmosphere changes subtly. "
            "Background elements move with parallax depth. "
            "Camera slowly pans across the scene. "
            "Smooth 24fps animation, 5 seconds, cinematic quality."
        ),
    }
    return transitions.get(effect_type, transitions["wind"])


def apply_modification(original_prompt: str, modification: str) -> str:
    """根据用户修改请求调整 Prompt"""
    if not original_prompt:
        raise ValueError("original_prompt cannot be empty")
    if not modification:
        raise ValueError("modification cannot be empty")
    return f"{original_prompt} {modification}"


def generate_ending_options(image_analysis: dict) -> list[dict[str, str]]:
    """基于图1分析结果，生成 3 个结尾方案

    Args:
        image_analysis: 图1的分析结果 {"subject": ..., "action": ..., "scene": ..., "mood": ...}

    Returns:
        [{"type": "动作完成", "description": "...", "prompt": "..."}, ...]
    """
    if image_analysis is None or not isinstance(image_analysis, dict):
        raise TypeError("image_analysis must be a dict")
    subject = image_analysis.get("subject", "主体")
    action = image_analysis.get("action", "存在")
    scene = image_analysis.get("scene", "背景中")
    mood = image_analysis.get("mood", "平静")

    options = [
        {
            "type": "动作完成",
            "description": f"{subject}完成了{action}，满足地休息",
            "prompt": f"Same {subject} as reference. {subject} has finished {action}, now resting contentedly. Preserve all original features. Do NOT add new elements."
        },
        {
            "type": "场景拉远",
            "description": f"镜头拉远，展示{subject}在{scene}中的全貌",
            "prompt": f"Same {subject} as reference. Camera pulls back to reveal the full scene: {subject} in {scene}. Preserve all original features. Do NOT add new elements."
        },
        {
            "type": "情绪变化",
            "description": f"{subject}表情变化，从{mood}变为更加开心",
            "prompt": f"Same {subject} as reference. {subject}'s expression changes from {mood} to happy and joyful. Preserve all original features. Do NOT add new elements."
        }
    ]

    return options
