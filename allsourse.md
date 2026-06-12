# VibeCode Agent — All Source Code

Complete source code of all workflow modules.

---

## agent/config.py

Centralized configuration, working directories, and archive logic.

```python
"""Centralized configuration for the agent package."""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ARK_API_KEY: str = os.getenv("ARK_API_KEY", "")
SEEDREAM_MODEL: str = os.getenv("SEEDREAM_MODEL", "doubao-seedream-5-0-260128")
BASE_URL: str = os.getenv("BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "60"))
FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "")

# Working directories (current session)
INPUT_DIR: Path = PROJECT_ROOT / "input"
GENERATED_DIR: Path = PROJECT_ROOT / "generated"
STATE_DIR: Path = PROJECT_ROOT / "state"
TEMP_DIR: Path = PROJECT_ROOT / "temp"

# Archive directory (completed workflows)
DATA_DIR: Path = PROJECT_ROOT / "data"

# Projects output directory (built websites)
PROJECTS_DIR: Path = PROJECT_ROOT / "projects"

# Templates
TEMPLATES_DIR: Path = PROJECT_ROOT / "templates"

# State files
WORKFLOW_STATE_FILE: Path = STATE_DIR / "workflow.json"
BATCH_STATE_FILE: Path = STATE_DIR / "batch.json"
CACHE_STATE_DIR: Path = STATE_DIR / "cache"
PROGRESS_STATE_DIR: Path = STATE_DIR / "progress"
CACHE_IMAGE_DIR: Path = GENERATED_DIR / "cache"


def get_archive_dir(project_name: str) -> Path:
    """Get archive directory for a completed project."""
    return DATA_DIR / project_name


def archive_completed_workflow(project_name: str):
    """Archive a completed workflow to data/{project_name}/
    
    Called when workflow reaches DONE stage.
    Copies input/, generated/, state/ to data/{project_name}/
    """
    archive_dir = get_archive_dir(project_name)
    archive_input = archive_dir / "input"
    archive_generated = archive_dir / "generated"
    archive_state = archive_dir / "state"
    
    # Create directories
    for d in [archive_dir, archive_input, archive_generated, archive_state]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy input files
    if INPUT_DIR.exists():
        for f in INPUT_DIR.iterdir():
            if f.is_file():
                dest = archive_input / f.name
                if not dest.exists():
                    shutil.copy2(str(f), str(dest))
    
    # Copy generated files
    if GENERATED_DIR.exists():
        for f in GENERATED_DIR.iterdir():
            if f.is_file():
                dest = archive_generated / f.name
                if not dest.exists():
                    shutil.copy2(str(f), str(dest))
        # Copy frames subdirectory
        frames_dir = GENERATED_DIR / "frames"
        if frames_dir.exists():
            archive_frames = archive_generated / "frames"
            archive_frames.mkdir(exist_ok=True)
            for f in frames_dir.iterdir():
                if f.is_file():
                    dest = archive_frames / f.name
                    if not dest.exists():
                        shutil.copy2(str(f), str(dest))
    
    # Copy state files
    if STATE_DIR.exists():
        for f in STATE_DIR.iterdir():
            if f.is_file():
                dest = archive_state / f.name
                if not dest.exists():
                    shutil.copy2(str(f), str(dest))
    
    print(f"Workflow archived to data/{project_name}/")


def ensure_working_dirs():
    """Ensure working directories exist."""
    for d in [INPUT_DIR, GENERATED_DIR, STATE_DIR, TEMP_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / "frames").mkdir(exist_ok=True)
    (GENERATED_DIR / "cache").mkdir(exist_ok=True)
```

---

## agent/workflow.py

State machine with JSON persistence and portalocker file locking.

```python
import os
import json
import logging
from pathlib import Path
from typing import Any, Optional
import portalocker

logger = logging.getLogger(__name__)

STAGES = [
    "INIT",
    "ANALYZE",
    "CONFIRM_PRODUCT",
    "GENERATE",
    "CONFIRM_IMAGES",
    "BUILD_VIDEO_PROMPT",
    "WAIT_VIDEO",
    "EXTRACT_FRAMES",
    "BUILD_PROJECT",
    "DONE"
]

class Workflow:
    def __init__(self, state_file: str = None):
        """Initialize workflow using working directories."""
        from agent.config import STATE_DIR, WORKFLOW_STATE_FILE, ensure_working_dirs
        
        ensure_working_dirs()
        self.state_file = state_file or str(WORKFLOW_STATE_FILE)
        self._data = self._load()

    def _load(self) -> dict:
        """Load state from file or create default"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    portalocker.lock(f, portalocker.LOCK_SH)
                    try:
                        data = json.load(f)
                        if not isinstance(data, dict):
                            return {"stage": "INIT"}
                        return data
                    finally:
                        portalocker.unlock(f)
            except (json.JSONDecodeError, IOError):
                return {"stage": "INIT"}
        return {"stage": "INIT"}

    def save(self):
        """Persist current state to file"""
        dir_name = os.path.dirname(self.state_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        with open(self.state_file, "w", encoding="utf-8") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            try:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            finally:
                portalocker.unlock(f)

    def get_stage(self) -> str:
        """Get current workflow stage"""
        return self._data.get("stage", "INIT")

    def set_stage(self, stage: str):
        """Set current workflow stage"""
        if stage not in STAGES:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {STAGES}")
        current = self.get_stage()
        current_idx = STAGES.index(current)
        target_idx = STAGES.index(stage)
        if target_idx > current_idx + 1:
            raise ValueError(
                f"Cannot skip stages: {current} -> {stage}. "
                f"Must complete intermediate stages first."
            )
        logger.info("Stage transition: %s -> %s", current, stage)
        self._data["stage"] = stage
        self.save()
        
        # Archive workflow when DONE
        if stage == "DONE":
            self._archive()

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data by key"""
        return self._data.get(key, default)

    def set_data(self, key: str, value: Any):
        """Set data by key and auto-save"""
        self._data[key] = value
        self.save()

    def reset(self):
        """Reset workflow to initial state"""
        logger.info("Workflow reset from stage %s", self.get_stage())
        self._data = {"stage": "INIT"}
        self.save()
    
    def _archive(self):
        """Archive completed workflow to data/{project_name}/"""
        from agent.config import archive_completed_workflow
        
        # Use product name from image_analysis or default
        analysis = self._data.get("image_analysis", {})
        subject = analysis.get("subject", "project")
        # Clean subject for use as directory name
        project_name = subject.replace(" ", "_").replace("/", "_")[:50]
        
        archive_completed_workflow(project_name)
    
    def get_input_path(self, filename: str) -> str:
        """Get full path for input file."""
        from agent.config import INPUT_DIR
        return str(INPUT_DIR / filename)
    
    def get_generated_path(self, filename: str) -> str:
        """Get full path for generated file."""
        from agent.config import GENERATED_DIR
        return str(GENERATED_DIR / filename)
    
    def get_frames_dir(self) -> str:
        """Get frames directory path."""
        from agent.config import GENERATED_DIR
        return str(GENERATED_DIR / "frames")
```

---

## agent/image_generator.py

Seedream API image generation with retry, format validation, and img2img support.

```python
import os
import time
import base64
import logging
from typing import Optional

import requests

from agent.config import ARK_API_KEY, SEEDREAM_MODEL, BASE_URL, API_TIMEOUT
from agent.exceptions import ImageGenerationError
from agent.prompt_builder import apply_modification  # noqa: F401 – re-export for backward compat

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0


def validate_image_format(image_path: str) -> bool:
    """验证图片格式是否受支持"""
    ext = os.path.splitext(image_path)[1].lower()
    return ext in SUPPORTED_FORMATS


def _image_to_data_url(image_path: str) -> str:
    """将本地图片转换为 base64 data URL"""
    ext = os.path.splitext(image_path)[1].lower()
    mime_map: dict[str, str] = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
    }
    mime = mime_map.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """Execute an HTTP request with retry and exponential backoff.

    Only retries on transient errors (connection, timeout). HTTP status errors
    are raised immediately.
    """
    func = getattr(requests, method)
    last_exc: Optional[Exception] = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = func(url, **kwargs)
            resp.raise_for_status()
            return resp
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
    raise last_exc  # type: ignore[misc]


def generate_image(prompt: str, output_path: str, reference_image: Optional[str] = None) -> str:
    """调用 Seedream API 生成图片，返回保存路径

    Args:
        prompt: 图片描述
        output_path: 保存路径
        reference_image: 参考图URL或本地路径（用于图生图模式）
    """
    logger.info("Generating image: output=%s, has_reference=%s", output_path, reference_image is not None)

    if not ARK_API_KEY:
        raise ValueError("缺少 ARK_API_KEY，请在 .env 文件中配置")

    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload: dict = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "size": "2K",
        "response_format": "url",
        "sequential_image_generation": "disabled",
        "watermark": False,
        "stream": False
    }

    if reference_image:
        if not reference_image.startswith("http") and not validate_image_format(reference_image):
            raise ValueError(f"不支持的图片格式: {os.path.splitext(reference_image)[1]}。支持的格式: {', '.join(sorted(SUPPORTED_FORMATS))}")
        if reference_image.startswith("http"):
            payload["image"] = reference_image
        else:
            payload["image"] = _image_to_data_url(reference_image)

    resp = _request_with_retry(
        "post",
        f"{BASE_URL}/images/generations",
        headers=headers,
        json=payload,
        timeout=API_TIMEOUT,
    )

    if resp.status_code != 200:
        raise ImageGenerationError(f"图片生成失败 [{resp.status_code}]: {resp.text}")

    image_url = resp.json()["data"][0]["url"]

    img_resp = _request_with_retry("get", image_url, timeout=API_TIMEOUT)

    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    logger.info("Image saved: %s", output_path)
    return output_path
```

---

## agent/prompt_builder.py

Prompt generation for img2img, video creation, and ending options.

```python
"""Prompt generation for img2img and video creation"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


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

    extras: dict[str, str] = {
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

    effects: dict[str, str] = {
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
    transitions: dict[str, str] = {
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

    options: list[dict[str, str]] = [
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
```

---

## agent/frame_extractor.py

ffmpeg frame extraction with auto-detect and error handling.

```python
import os
import shutil
import subprocess
import logging

from agent.config import FFMPEG_PATH
from agent.exceptions import FFmpegNotFoundError, FFmpegExecutionError

logger = logging.getLogger(__name__)


def _find_ffmpeg() -> str:
    """Locate ffmpeg binary: env var → hardcoded path → system PATH."""
    if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
        return FFMPEG_PATH
    found = shutil.which("ffmpeg")
    if found:
        return found
    return ""


def extract_frames(video_path: str, output_dir: str, fps: int = 24) -> int:
    """将视频拆解为 JPEG 帧序列，返回总帧数

    Args:
        video_path: 视频文件路径
        output_dir: 帧输出目录
        fps: 提取帧率，必须大于0
    """
    logger.info("Extracting frames: video=%s, output=%s, fps=%d", video_path, output_dir, fps)

    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")

    ffmpeg_cmd = _find_ffmpeg()
    if not ffmpeg_cmd:
        raise FFmpegNotFoundError(
            "未找到 ffmpeg，请先安装：\n"
            "  macOS:   brew install ffmpeg\n"
            "  Windows: https://www.gyan.dev/ffmpeg/builds/\n"
            "  Linux:   sudo apt install ffmpeg\n"
            "  或设置环境变量 FFMPEG_PATH 指向 ffmpeg 可执行文件"
        )

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在：{video_path}")

    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    cmd = [
        ffmpeg_cmd,
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-q:v", "2",
        "-y",
        output_pattern
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise FFmpegExecutionError(f"ffmpeg 执行失败：\n{result.stderr[-500:]}")

    frames = sorted([f for f in os.listdir(output_dir) if f.endswith(".jpg")])
    logger.info("Extracted %d frames to %s", len(frames), output_dir)
    return len(frames)
```

---

## agent/web_builder.py

HTML generation from hero_shot.html template with copy generation.

```python
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
```

---

## agent/cache.py

Image cache with MD5 key hashing and TTL support.

```python
import os
import json
import time
import hashlib
import shutil
import logging

logger = logging.getLogger(__name__)


class ImageCache:
    """Cache generated images based on prompt + reference_image hash."""

    def __init__(self, state_dir: str = "state/cache", image_dir: str = "generated/cache"):
        self.state_dir = state_dir
        self.image_dir = image_dir
        os.makedirs(state_dir, exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)

    def make_key(self, prompt: str, reference_image: str = None) -> str:
        """Create MD5 hash from prompt and optional reference_image."""
        content = prompt
        if reference_image:
            content += f"\n{reference_image}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def set(self, prompt: str, image_path: str = None, reference_image: str = None,
            output_ext: str = None, ttl: int = None) -> str:
        """Store image and metadata in cache.

        Args:
            prompt: The generation prompt
            image_path: Path to image file to cache (None for metadata-only)
            reference_image: Reference image path used during generation
            output_ext: File extension for cached image
            ttl: Time-to-live in seconds (None = never expires)

        Returns:
            Cache key (MD5 hash)
        """
        key = self.make_key(prompt, reference_image)

        if image_path and os.path.exists(image_path):
            cached_image = os.path.join(self.image_dir, f"{key}{output_ext or ''}")
            shutil.copy2(image_path, cached_image)

        metadata = {
            "prompt": prompt,
            "reference_image": reference_image,
            "output_ext": output_ext,
            "cached_at": time.time(),
            "ttl": ttl,
        }

        meta_path = os.path.join(self.state_dir, f"{key}.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return key

    def get(self, prompt: str, reference_image: str = None):
        """Retrieve cached metadata if entry exists and is not expired.

        Returns:
            Metadata dict or None if miss/expired
        """
        key = self.make_key(prompt, reference_image)
        meta_path = os.path.join(self.state_dir, f"{key}.json")

        if not os.path.exists(meta_path):
            return None

        with open(meta_path, "r") as f:
            meta = json.load(f)

        ttl = meta.get("ttl")
        if ttl is not None:
            if time.time() - meta["cached_at"] > ttl:
                self._remove(key)
                return None

        return meta

    def clear(self):
        """Remove all cached entries."""
        for filename in os.listdir(self.state_dir):
            if filename.endswith(".json"):
                key = filename[:-5]
                self._remove(key)

    def _remove(self, key: str):
        """Remove a single cache entry by key."""
        meta_path = os.path.join(self.state_dir, f"{key}.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            ext = meta.get("output_ext", "")
            img_path = os.path.join(self.image_dir, f"{key}{ext or ''}")
            if os.path.exists(img_path):
                os.remove(img_path)
            os.remove(meta_path)
```

---

## agent/batch.py

Batch processing workflow with queue management and progress tracking.

```python
import os
import json
import logging
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

DEFAULT_STATE_FILE = "state/batch.json"

class BatchStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class BatchItem:
    image_path: str
    status: BatchStatus = BatchStatus.PENDING

class BatchWorkflow:
    def __init__(self, state_file: str = DEFAULT_STATE_FILE):
        self.state_file = state_file
        self._items: List[BatchItem] = []
        self._load()

    def _load(self):
        """Load state from file or initialize empty"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "items" in data:
                        self._items = [
                            BatchItem(
                                image_path=item["image_path"],
                                status=BatchStatus(item["status"])
                            )
                            for item in data["items"]
                        ]
                    else:
                        self._items = []
            except (json.JSONDecodeError, IOError):
                self._items = []
        else:
            self._items = []

    def _save(self):
        """Persist current state to file"""
        dir_name = os.path.dirname(self.state_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        data = {
            "items": [asdict(item) for item in self._items]
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create(self, images: List[str]) -> List[BatchItem]:
        """Create a new batch with list of image paths"""
        if not images:
            raise ValueError("At least one image required")
        self._items = [BatchItem(image_path=img) for img in images]
        self._save()
        return self._items

    def get_next(self) -> Optional[BatchItem]:
        """Get next pending item in order"""
        for item in self._items:
            if item.status == BatchStatus.PENDING:
                return item
        return None

    def get_item(self, image_path: str) -> Optional[BatchItem]:
        """Get specific item by image path"""
        for item in self._items:
            if item.image_path == image_path:
                return item
        return None

    def complete(self, image_path: str) -> bool:
        """Mark item as completed"""
        item = self.get_item(image_path)
        if item is None:
            return False
        item.status = BatchStatus.COMPLETED
        self._save()
        return True

    def skip(self, image_path: str) -> bool:
        """Mark item as skipped"""
        item = self.get_item(image_path)
        if item is None:
            return False
        item.status = BatchStatus.SKIPPED
        self._save()
        return True

    def get_total(self) -> int:
        """Return total number of items in batch"""
        return len(self._items)

    def get_completed(self) -> int:
        """Return count of completed and skipped items"""
        return sum(
            1 for item in self._items
            if item.status in (BatchStatus.COMPLETED, BatchStatus.SKIPPED)
        )

    def progress(self) -> float:
        """Return fraction of completed items (0.0 to 1.0)"""
        total = self.get_total()
        if total == 0:
            return 0.0
        return self.get_completed() / total
```

---

## agent/progress.py

Progress tracker for polling task status.

```python
import os
import json
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    CANCELLED = "cancelled"


DEFAULT_STATE_DIR = "state/progress"


class ProgressTracker:
    def __init__(self, state_dir: str = DEFAULT_STATE_DIR):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)

    def _task_path(self, task_id: str) -> str:
        return os.path.join(self.state_dir, f"{task_id}.json")

    def _load(self, task_id: str) -> Optional[dict]:
        path = self._task_path(task_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _save(self, task_id: str, data: dict):
        path = self._task_path(task_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create(self, message: str, total: Optional[int] = None) -> str:
        task_id = uuid.uuid4().hex[:12]
        data = {
            "id": task_id,
            "status": TaskStatus.PENDING,
            "message": message,
            "total": total,
            "current": 0,
            "percent": None,
        }
        self._save(task_id, data)
        return task_id

    def get(self, task_id: str) -> Optional[dict]:
        return self._load(task_id)

    def update(self, task_id: str, current: Optional[int] = None, message: Optional[str] = None):
        data = self._load(task_id)
        if data is None:
            return
        if current is not None:
            data["current"] = current
        if message is not None:
            data["message"] = message
        if data["status"] == TaskStatus.PENDING:
            data["status"] = TaskStatus.RUNNING
        total = data.get("total")
        if total and total > 0:
            data["percent"] = round(data["current"] / total * 100, 1)
        self._save(task_id, data)

    def complete(self, task_id: str):
        data = self._load(task_id)
        if data is None:
            return
        data["status"] = TaskStatus.DONE
        if data.get("total"):
            data["current"] = data["total"]
        self._save(task_id, data)

    def cancel(self, task_id: str):
        data = self._load(task_id)
        if data is None:
            return
        data["status"] = TaskStatus.CANCELLED
        self._save(task_id, data)

    def list_tasks(self, status: Optional[str] = None) -> list:
        tasks = []
        for filename in os.listdir(self.state_dir):
            if not filename.endswith(".json"):
                continue
            task_id = filename[:-5]
            data = self._load(task_id)
            if data is None:
                continue
            if status and data.get("status") != status:
                continue
            tasks.append(data)
        return tasks
```

---

## agent/exceptions.py

Custom exception hierarchy.

```python
"""Custom exceptions for the agent package."""


class AgentError(Exception):
    """Base exception for all agent errors."""


class ImageGenerationError(AgentError):
    """Raised when image generation fails."""


class FFmpegNotFoundError(AgentError):
    """Raised when ffmpeg binary cannot be found."""


class FFmpegExecutionError(AgentError):
    """Raised when ffmpeg command fails."""
```

---

## agent/__init__.py

```python
"""VibeCode Agent - Python modules for product video workflow"""
```

---

## Workflow Stages

| Stage | Description |
|-------|-------------|
| INIT | Detect input images |
| ANALYZE | Visual analysis of image |
| CONFIRM_PRODUCT | User selects effect type and aspect ratio |
| GENERATE | Generate image1 (首帧) and image2 (尾帧) via Seedream API |
| CONFIRM_IMAGES | User confirms generated images |
| BUILD_VIDEO_PROMPT | Build video transition prompt |
| WAIT_VIDEO | Wait for user to place video.mp4 |
| EXTRACT_FRAMES | ffmpeg extracts JPEG frames |
| BUILD_PROJECT | Generate hero shot HTML showcase |
| DONE | Archive workflow to data/{project}/ |