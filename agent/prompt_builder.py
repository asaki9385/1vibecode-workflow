"""Prompt generation for img2img and video creation"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Negative constraints helper
# ---------------------------------------------------------------------------

def _build_negative_constraints(
    confirmed_intent: dict | None = None,
    image_analysis: dict | None = None,
) -> str:
    """从 confirmed_intent 和 image_analysis 构建 Avoid: 部分

    来源：
    - confirmed_intent["exclude"]：用户明确说不想要的元素
    - image_analysis["key_features"]：容易被误改的细节（logo、文字、特定配色等）
    """
    items: list[str] = []

    if confirmed_intent:
        exclude = confirmed_intent.get("exclude", "")
        if exclude:
            items.append(exclude)

    if image_analysis:
        key_features = image_analysis.get("key_features", [])
        if key_features:
            items.append(", ".join(key_features))

    if not items:
        return ""
    return f" Avoid: {', '.join(items)}."


# ---------------------------------------------------------------------------
# build_video_prompt
# ---------------------------------------------------------------------------

def build_video_prompt(
    image_analysis: dict,
    transition_analysis: dict,
    camera_motion: str = "",
    fps: int = 24,
    duration: int = 5,
    confirmed_intent: dict | None = None,
) -> str:
    """基于 image_analysis + transition_analysis 生成视频过渡 Prompt

    Args:
        image_analysis: 图片分析结果（含 subject, style_profile 等）
        transition_analysis: 图1→图2 的对比分析（含 changed_elements, change_description）
        camera_motion: 运镜方式；为空时取 style_profile.camera_style
        fps: 帧率
        duration: 时长（秒）
        confirmed_intent: 意图确认结果（用于提取 negative constraints）

    Returns:
        视频过渡 Prompt

    Raises:
        ValueError: transition_analysis 缺失或为空
    """
    if not image_analysis:
        raise ValueError("image_analysis cannot be empty")
    if not transition_analysis:
        raise ValueError(
            "transition_analysis cannot be empty — "
            "run visual comparison between image1 and image2 first"
        )

    subject = image_analysis.get("subject", "the subject")
    change_desc = transition_analysis.get("change_description", "")
    changed_elements = transition_analysis.get("changed_elements", [])
    style_profile = image_analysis.get("style_profile", {})
    keywords = style_profile.get("keywords", [])

    # 运镜：优先用传入值，否则取 style_profile，再否则硬编码默认
    if not camera_motion:
        camera_motion = style_profile.get("camera_style", "slow push in")

    # 动态描述
    if change_desc:
        motion_desc = f"{subject} {change_desc}"
    else:
        motion_desc = f"{subject} transitions smoothly"

    # 元素动作描述
    if changed_elements:
        elements_str = ", ".join(changed_elements)
        action_desc = f"with {elements_str} moving naturally"
    else:
        action_desc = "with subtle ambient movement"

    # 风格词
    style_desc = ""
    if keywords:
        style_desc = f" {', '.join(keywords)} style."

    # 组装
    prompt = (
        f"{motion_desc}, {action_desc}. "
        f"Camera {camera_motion}. "
        f"Smooth {fps}fps animation, {duration}s, cinematic quality.{style_desc}"
    )

    # Negative constraints
    prompt += _build_negative_constraints(confirmed_intent, image_analysis)

    return prompt


# ---------------------------------------------------------------------------
# build_regenerate_prompt
# ---------------------------------------------------------------------------

# subject_type → 特征维度映射
_SUBJECT_TYPE_FEATURES: dict[str, list[str]] = {
    "person": [
        "hair color, hair length, hair style",
        "eye color, eye shape, facial structure",
        "expression, skin tone",
        "outfit design, fabric textures, colors, accessories",
    ],
    "anime_character": [
        "hair color, hair length, hair style",
        "eye color, eye shape, facial structure",
        "expression, anime rendering style",
        "outfit design, fabric textures, colors, accessories",
    ],
    "product": [
        "material texture, surface finish",
        "brand logo, text, labels",
        "shape, proportions, color accents",
        "reflections, highlights, shadows",
    ],
    "landscape": [
        "lighting direction, color temperature",
        "vegetation type, foliage color",
        "sky conditions, cloud formations",
        "terrain features, water elements",
    ],
    "architecture": [
        "building materials, structural details",
        "lighting, shadow patterns",
        "surrounding environment",
        "architectural style, proportions",
    ],
    "food": [
        "texture, surface detail",
        "color gradation, freshness cues",
        "plating arrangement, garnish",
        "steam, moisture, light reflections",
    ],
}

_DEFAULT_FEATURES: list[str] = [
    "exact hair color, hair length, hair style",
    "eye color, eye shape, facial structure, expression",
    "outfit design, fabric textures, colors, patterns, accessories",
    "pose: exact body position, limb angles, head tilt",
    "composition: framing, camera angle, subject placement",
    "color palette: dominant colors, color temperature, saturation",
    "lighting: light direction, shadow placement, highlights",
    "art style: rendering technique, line weight, shading style",
    "background: elements, colors, atmosphere, environmental details",
]


def build_regenerate_prompt(
    effect_type: str,
    custom_desc: str = "",
    analysis: dict = None,
    confirmed_intent: dict | None = None,
) -> str:
    """生成图1的重绘 Prompt — 强约束提取参考图全部特征，高画质重渲染

    Args:
        effect_type: 效果类型 - "wind"/"lighting"/"scene"/"custom"
        custom_desc: 自定义效果描述
        analysis: 图片分析结果（含 subject_type, key_features 等）
        confirmed_intent: 意图确认结果（用于 negative constraints）
    """
    subject_type = (analysis or {}).get("subject_type", "other")
    features = _SUBJECT_TYPE_FEATURES.get(subject_type, _DEFAULT_FEATURES)

    features_block = "\n".join(f"- {f}" for f in features)

    base = (
        "EXTREMELY IMPORTANT: This is a reference image recreation task. "
        "You MUST extract and preserve EVERY visual element from the reference image with zero deviation. "
        f"Strict requirements:\n{features_block}\n"
        "- Mood: exact emotional tone, energy level, atmosphere\n"
        "The output MUST be a higher-quality re-rendering of the reference image. "
        "Do NOT add new elements. Do NOT change existing elements. Do NOT reinterpret the scene. "
        "Only improve resolution, detail clarity, and rendering quality."
    )

    # 如果有 key_features，添加额外约束
    if analysis:
        key_features = analysis.get("key_features", [])
        if key_features:
            features_str = ", ".join(key_features)
            base += f"\n- CRITICAL: Must preserve these key features exactly: {features_str}"

        style_keywords = analysis.get("style_profile", {}).get("keywords", [])
        if style_keywords:
            style_str = ", ".join(style_keywords)
            base += f"\n- Art style must match: {style_str}"

    extras: dict[str, str] = {
        "wind": "After preserving all reference elements, add subtle natural wind dynamics: slight hair movement, gentle fabric flutter.",
        "lighting": "After preserving all reference elements, enhance lighting with soft volumetric rays and atmospheric depth.",
        "scene": "After preserving all reference elements, add flowing clouds and environmental movement in background.",
        "custom": f"After preserving all reference elements, {custom_desc}" if custom_desc else ""
    }

    extra = extras.get(effect_type, "")
    prompt = f"{base} {extra}".strip()

    # Negative constraints
    prompt += _build_negative_constraints(confirmed_intent, analysis)

    return prompt


# ---------------------------------------------------------------------------
# build_img2img_prompt
# ---------------------------------------------------------------------------

def build_img2img_prompt(
    effect_type: str,
    custom_desc: str = "",
    analysis: dict = None,
    confirmed_intent: dict | None = None,
) -> str:
    """根据动态效果类型生成图生图 Prompt

    Args:
        effect_type: 效果类型 - "wind"/"lighting"/"scene"/"custom"
        custom_desc: 自定义效果描述（effect_type="custom" 时使用）
        analysis: 图片分析结果（含 movable_elements 等）
        confirmed_intent: 意图确认结果（用于 negative constraints）
    """
    base = "Same character, same art style, same background, maintain consistent design."

    movable = []
    if analysis:
        movable = analysis.get("movable_elements", [])

    effects: dict[str, str] = {
        "wind": f"{base} Add dynamic wind effect: hair flowing in the wind, fabric rippling with air movement.",
        "lighting": f"{base} Add dramatic lighting change: golden hour sunlight, warm glow, soft shadows, atmospheric light rays.",
        "scene": f"{base} Add scene dynamics: clouds flowing in background, subtle environment movement, atmospheric depth.",
        "custom": f"{base} {custom_desc}" if custom_desc else base
    }

    # 如果有可移动元素，添加到提示词中
    if movable and effect_type in ("wind", "scene"):
        movable_str = ", ".join(movable[:3])
        effects[effect_type] += f" Animate these elements: {movable_str}."

    prompt = effects.get(effect_type, effects["wind"])

    # Negative constraints
    prompt += _build_negative_constraints(confirmed_intent, analysis)

    return prompt


# ---------------------------------------------------------------------------
# build_video_prompt (legacy compat — kept for backward reference)
# ---------------------------------------------------------------------------

def build_video_prompt_legacy(effect_type: str) -> str:
    """旧版 build_video_prompt（已废弃，仅保留向后兼容）"""
    return build_video_prompt.__doc__ or ""


# ---------------------------------------------------------------------------
# apply_modification
# ---------------------------------------------------------------------------

def apply_modification(original_prompt: str, modification: str) -> str:
    """根据用户修改请求调整 Prompt"""
    if not original_prompt:
        raise ValueError("original_prompt cannot be empty")
    if not modification:
        raise ValueError("modification cannot be empty")
    return f"{original_prompt} {modification}"


# ---------------------------------------------------------------------------
# build_ending_prompt
# ---------------------------------------------------------------------------

def build_ending_prompt(original_features: str, ending_description: str) -> str:
    """基于图1特征和结尾描述，生成图2的 Prompt

    Args:
        original_features: 图1需要保留的特征描述
        ending_description: 结尾方案的描述

    Returns:
        图生图 Prompt
    """
    if not original_features:
        raise ValueError("original_features cannot be empty")
    if not ending_description:
        raise ValueError("ending_description cannot be empty")

    return (
        f"Same subject as reference image. Preserve ALL original features: {original_features}. "
        f"Change: {ending_description}. "
        f"Do NOT add new elements not mentioned above. "
        f"Maintain identical art style, color palette, and composition."
    )


# ---------------------------------------------------------------------------
# generate_ending_options
# ---------------------------------------------------------------------------

def generate_ending_options(image_analysis: dict) -> list[dict[str, str]]:
    """基于图1分析结果，根据 subject_type 生成 3 个差异化结尾方案

    Args:
        image_analysis: 图1的分析结果，必须包含 subject_type 字段

    Returns:
        [{"type": "方案类型", "description": "...", "prompt": "..."}, ...]
    """
    if image_analysis is None or not isinstance(image_analysis, dict):
        raise TypeError("image_analysis must be a dict")

    subject = image_analysis.get("subject", "主体")
    action = image_analysis.get("action", "")
    scene = image_analysis.get("scene", "")
    mood = image_analysis.get("mood", "")
    subject_type = image_analysis.get("subject_type", "other")
    movable_elements = image_analysis.get("movable_elements", [])
    key_features = image_analysis.get("key_features", [])

    features_hint = ", ".join(key_features[:3]) if key_features else ""
    elements_hint = ", ".join(movable_elements[:2]) if movable_elements else ""

    if subject_type in ("person", "anime_character"):
        options = _ending_options_character(subject, action, scene, mood, elements_hint)
    elif subject_type == "product":
        options = _ending_options_product(subject, scene, features_hint)
    elif subject_type in ("landscape", "architecture"):
        options = _ending_options_landscape(subject, scene, movable_elements)
    elif subject_type == "food":
        options = _ending_options_food(subject, scene, features_hint)
    else:
        options = _ending_options_abstract(subject, scene, mood, movable_elements)

    return options


def _ending_options_character(subject: str, action: str, scene: str, mood: str, elements: str) -> list[dict[str, str]]:
    """人物/动漫角色的结尾方案"""
    animate_hint = f" including {elements}" if elements else ""

    return [
        {
            "type": "表情/情绪变化",
            "description": f"{subject}的表情从{mood}转变为微笑，眼神变得柔和",
            "prompt": (
                f"Same {subject} as reference. {subject}'s expression gradually shifts from {mood} "
                f"to a gentle smile, eyes softening. Preserve all original features{animate_hint}. "
                "Do NOT add new elements."
            )
        },
        {
            "type": "视角转换",
            "description": f"镜头缓慢移动，从新角度展示{subject}在{scene}中的姿态",
            "prompt": (
                f"Same {subject} as reference. Camera slowly orbits to reveal a new angle of "
                f"{subject} in {scene}. Preserve all original features{animate_hint}. "
                "Do NOT add new elements."
            )
        },
        {
            "type": "动作完成",
            "description": f"{subject}完成{action}，缓缓放下手，自然放松",
            "prompt": (
                f"Same {subject} as reference. {subject} gently lowers their hand, transitioning from "
                f"{action} to a relaxed natural pose. Preserve all original features{animate_hint}. "
                "Do NOT add new elements."
            )
        }
    ]


def _ending_options_product(subject: str, scene: str, features: str) -> list[dict[str, str]]:
    """产品的结尾方案"""
    feat_hint = f", highlighting {features}" if features else ""

    return [
        {
            "type": "旋转展示",
            "description": f"{subject}缓慢旋转，展示全貌和{scene}中的细节",
            "prompt": (
                f"Same {subject} as reference. The product slowly rotates to reveal all angles "
                f"in {scene}{feat_hint}. Preserve all original features. "
                "Do NOT add new elements."
            )
        },
        {
            "type": "细节特写",
            "description": f"镜头推近，聚焦{subject}的关键细节和材质质感",
            "prompt": (
                f"Same {subject} as reference. Camera slowly pushes in to focus on "
                f"the fine details and material texture of {subject}{feat_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        },
        {
            "type": "光影质感",
            "description": f"打光角度变化，{subject}表面呈现不同光泽和质感层次",
            "prompt": (
                f"Same {subject} as reference. Lighting angle gradually shifts, revealing "
                f"different surface reflections and material depth on {subject}{feat_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        }
    ]


def _ending_options_landscape(subject: str, scene: str, movable: list[str]) -> list[dict[str, str]]:
    """风景/建筑的结尾方案"""
    move_hint = ""
    if movable:
        move_hint = f", with {', '.join(movable[:2])} subtly animating"

    return [
        {
            "type": "全景拉远",
            "description": f"镜头缓缓拉远，揭示{subject}在{scene}中的完整全貌",
            "prompt": (
                f"Same {subject} as reference. Camera slowly pulls back to reveal the full "
                f"panorama of {subject} in {scene}{move_hint}. Preserve all original features. "
                "Do NOT add new elements."
            )
        },
        {
            "type": "光照时段变化",
            "description": f"光线从当前时段缓慢过渡，{scene}呈现不同的光照氛围",
            "prompt": (
                f"Same {subject} as reference. Lighting gradually transitions as time of day shifts, "
                f"casting new shadows and warmth across {scene}{move_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        },
        {
            "type": "环境动态",
            "description": f"{scene}中的自然元素开始缓缓运动，增添生命力",
            "prompt": (
                f"Same {subject} as reference. Natural elements in {scene} begin to gently move — "
                f"clouds drifting, light flickering, atmosphere breathing{move_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        }
    ]


def _ending_options_food(subject: str, scene: str, features: str) -> list[dict[str, str]]:
    """食物的结尾方案"""
    feat_hint = f", showing {features}" if features else ""

    return [
        {
            "type": "热气升腾",
            "description": f"{subject}上方升起袅袅热气，营造刚出炉的新鲜感",
            "prompt": (
                f"Same {subject} as reference. Gentle steam rises from {subject}, "
                f"creating a fresh-from-kitchen atmosphere in {scene}{feat_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        },
        {
            "type": "细节特写",
            "description": f"镜头推近，展示{subject}的摆盘纹理和食材质感",
            "prompt": (
                f"Same {subject} as reference. Camera slowly pushes in to reveal the "
                f"intricate plating details and food texture of {subject}{feat_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        },
        {
            "type": "光线变化",
            "description": f"光线角度变换，{subject}表面呈现不同的光泽和色彩层次",
            "prompt": (
                f"Same {subject} as reference. Lighting angle shifts gently, revealing "
                f"different gloss and color depth on {subject}{feat_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        }
    ]


def _ending_options_abstract(subject: str, scene: str, mood: str, movable: list[str]) -> list[dict[str, str]]:
    """抽象/其他的结尾方案"""
    move_hint = ""
    if movable:
        move_hint = f", with {', '.join(movable[:2])} morphing"

    return [
        {
            "type": "色彩/形态渐变",
            "description": f"{subject}的色彩和形态缓缓渐变，呈现{mood}氛围的流动感",
            "prompt": (
                f"Same {subject} as reference. Colors and forms gradually morph and flow, "
                f"enhancing the {mood} atmosphere{move_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        },
        {
            "type": "镜头揭示",
            "description": f"镜头缓慢移动，揭示{scene}中更多构图层次",
            "prompt": (
                f"Same {subject} as reference. Camera slowly moves to reveal deeper "
                f"compositional layers in {scene}{move_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        },
        {
            "type": "氛围转变",
            "description": f"整体氛围从{mood}缓缓过渡到另一种情绪基调",
            "prompt": (
                f"Same {subject} as reference. Overall atmosphere gradually transitions "
                f"from {mood} to a new emotional tone{move_hint}. "
                "Preserve all original features. Do NOT add new elements."
            )
        }
    ]
