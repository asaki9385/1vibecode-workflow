# VibeCode Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a state machine + multi-turn dialogue Agent for VibeCode product video workflow, with Claude Code skill orchestration and Python backend modules.

**Architecture:** Claude Code skill handles conversation flow and user interaction, Python modules handle API calls (Seedream, ffmpeg) and state persistence via workflow.json.

**Tech Stack:** Python 3.11+, requests, python-dotenv, Claude Code Skills

---

## File Structure

```
vibecode-workflow/
├── agent/
│   ├── __init__.py           ← Package init, exports all modules
│   ├── workflow.py           ← State management (load/save/get/set stage)
│   ├── image_generator.py    ← Seedream API wrapper
│   ├── frame_extractor.py    ← ffmpeg wrapper
│   └── prompt_builder.py     ← Prompt generation logic
├── state/
│   └── workflow.json         ← Runtime state (auto-created)
├── generated/                ← Runtime output (auto-created)
├── tests/
│   ├── test_workflow.py
│   ├── test_image_generator.py
│   ├── test_prompt_builder.py
│   └── test_frame_extractor.py
├── .claude/
│   └── skills/
│       └── vibecode-agent.md ← Claude Code skill
├── scripts/                  ← (保留原有脚本作为独立工具)
├── .env
└── requirements.txt
```

---

### Task 1: workflow.py — State Management (P0)

**Files:**
- Create: `agent/__init__.py`
- Create: `agent/workflow.py`
- Create: `tests/test_workflow.py`

- [ ] **Step 1: Write failing test for workflow module**

```python
# tests/test_workflow.py
import os
import json
import pytest
import tempfile
from agent.workflow import Workflow

@pytest.fixture
def tmp_workflow(tmp_path):
    """Create workflow with temporary state file"""
    state_file = tmp_path / "state" / "workflow.json"
    return Workflow(state_file=str(state_file))

def test_init_creates_state_dir(tmp_workflow):
    """INIT stage should be default when no state file exists"""
    assert tmp_workflow.get_stage() == "INIT"

def test_set_stage(tmp_workflow):
    """set_stage should update current stage"""
    tmp_workflow.set_stage("ANALYZE")
    assert tmp_workflow.get_stage() == "ANALYZE"

def test_save_and_load(tmp_workflow):
    """Data should persist across save/load cycles"""
    tmp_workflow.set_stage("CONFIRM_PRODUCT")
    tmp_workflow.set_data("product", {"name": "Test Product"})
    tmp_workflow.save()

    # Create new workflow instance to test persistence
    new_wf = Workflow(state_file=tmp_workflow.state_file)
    assert new_wf.get_stage() == "CONFIRM_PRODUCT"
    assert new_wf.get_data("product") == {"name": "Test Product"}

def test_reset(tmp_workflow):
    """reset should clear all state back to INIT"""
    tmp_workflow.set_stage("DONE")
    tmp_workflow.set_data("product", {"name": "Test"})
    tmp_workflow.reset()
    assert tmp_workflow.get_stage() == "INIT"
    assert tmp_workflow.get_data("product") is None

def test_get_data_default(tmp_workflow):
    """get_data should return default for missing keys"""
    assert tmp_workflow.get_data("nonexistent") is None
    assert tmp_workflow.get_data("nonexistent", "default") == "default"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_workflow.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agent.workflow'"

- [ ] **Step 3: Create agent package**

```python
# agent/__init__.py
"""VibeCode Agent - Python modules for product video workflow"""
```

- [ ] **Step 4: Implement workflow.py**

```python
# agent/workflow.py
import os
import json
from pathlib import Path
from typing import Any, Optional

DEFAULT_STATE_FILE = "state/workflow.json"

STAGES = [
    "INIT",
    "ANALYZE",
    "CONFIRM_PRODUCT",
    "PLAN_IMAGES",
    "GENERATE_IMAGES",
    "CONFIRM_IMAGES",
    "BUILD_VIDEO_PROMPT",
    "WAIT_VIDEO",
    "EXTRACT_FRAMES",
    "BUILD_PROJECT",
    "DONE"
]

class Workflow:
    def __init__(self, state_file: str = DEFAULT_STATE_FILE):
        self.state_file = state_file
        self._data = self._load()

    def _load(self) -> dict:
        """Load state from file or create default"""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"stage": "INIT"}

    def save(self):
        """Persist current state to file"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get_stage(self) -> str:
        """Get current workflow stage"""
        return self._data.get("stage", "INIT")

    def set_stage(self, stage: str):
        """Set current workflow stage"""
        if stage not in STAGES:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {STAGES}")
        self._data["stage"] = stage
        self.save()

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data by key"""
        return self._data.get(key, default)

    def set_data(self, key: str, value: Any):
        """Set data by key and auto-save"""
        self._data[key] = value
        self.save()

    def reset(self):
        """Reset workflow to initial state"""
        self._data = {"stage": "INIT"}
        self.save()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_workflow.py -v`
Expected: All 5 tests PASS

- [ ] **Step 6: Commit**

```bash
cd D:/1vibecode-workflow
git init
git add agent/__init__.py agent/workflow.py tests/test_workflow.py
git commit -m "feat: add workflow state management module"
```

---

### Task 2: image_generator.py — Seedream API (P0)

**Files:**
- Create: `agent/image_generator.py`
- Create: `tests/test_image_generator.py`

- [ ] **Step 1: Write failing test for image generator**

```python
# tests/test_image_generator.py
import os
import pytest
from unittest.mock import patch, MagicMock
from agent.image_generator import generate_image, apply_modification

@pytest.fixture
def mock_env(monkeypatch):
    """Set test API key"""
    monkeypatch.setenv("ARK_API_KEY", "test-key")

@patch("agent.image_generator.requests.post")
@patch("agent.image_generator.requests.get")
def test_generate_image_success(mock_get, mock_post, tmp_path, mock_env):
    """Should download and save image on success"""
    # Mock API response
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"data": [{"url": "https://example.com/img.png"}]}
    )
    mock_get.return_value = MagicMock(
        status_code=200,
        content=b"fake-image-data"
    )

    output_path = str(tmp_path / "test.png")
    result = generate_image("test prompt", output_path)

    assert result == output_path
    assert os.path.exists(output_path)
    with open(output_path, "rb") as f:
        assert f.read() == b"fake-image-data"

@patch("agent.image_generator.requests.post")
def test_generate_image_api_error(mock_post, tmp_path, mock_env):
    """Should raise on API error"""
    mock_post.return_value = MagicMock(
        status_code=400,
        text="Bad request"
    )

    with pytest.raises(Exception, match="图片生成失败"):
        generate_image("test", str(tmp_path / "fail.png"))

def test_apply_modification():
    """Should merge original prompt with modification"""
    original = "A smart doorbell, dark background, cinematic"
    modification = "white background"
    result = apply_modification(original, modification)
    assert "white background" in result
    assert "smart doorbell" in result
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_image_generator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agent.image_generator'"

- [ ] **Step 3: Implement image_generator.py**

```python
# agent/image_generator.py
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

ARK_API_KEY = os.getenv("ARK_API_KEY")
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


def generate_image(prompt: str, output_path: str) -> str:
    """调用 Seedream API 生成图片，返回保存路径"""
    if not ARK_API_KEY:
        raise ValueError("缺少 ARK_API_KEY，请在 .env 文件中配置")

    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "size": "2K",
        "response_format": "url",
        "sequential_image_generation": "disabled",
        "watermark": False,
        "stream": False
    }

    resp = requests.post(
        f"{BASE_URL}/images/generations",
        headers=headers,
        json=payload,
        timeout=60
    )

    if resp.status_code != 200:
        raise Exception(f"图片生成失败 [{resp.status_code}]: {resp.text}")

    image_url = resp.json()["data"][0]["url"]

    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    return output_path


def apply_modification(original_prompt: str, modification: str) -> str:
    """合并原 Prompt 和修改描述，生成新 Prompt"""
    return f"{original_prompt}, {modification}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_image_generator.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
cd D:/1vibecode-workflow
git add agent/image_generator.py tests/test_image_generator.py
git commit -m "feat: add Seedream image generator module"
```

---

### Task 3: prompt_builder.py — Prompt Generation (P1)

**Files:**
- Create: `agent/prompt_builder.py`
- Create: `tests/test_prompt_builder.py`

- [ ] **Step 1: Write failing test for prompt builder**

```python
# tests/test_prompt_builder.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_prompt_builder.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement prompt_builder.py**

```python
# agent/prompt_builder.py
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

    if image_type == "static":
        return (
            f"Ultra realistic product photography, {name}, {desc}, "
            f"floating in air, dark cinematic background, "
            f"studio lighting, premium technology aesthetic, 8k, {style}"
        )
    else:
        return (
            f"{name} in working state, {desc}, "
            f"modern apartment entrance, subtle glowing indicator, "
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
    return f"{original_prompt}, {modification}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_prompt_builder.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd D:/1vibecode-workflow
git add agent/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add prompt builder module"
```

---

### Task 4: frame_extractor.py — ffmpeg Wrapper (P2)

**Files:**
- Create: `agent/frame_extractor.py`
- Create: `tests/test_frame_extractor.py`

- [ ] **Step 1: Write failing test for frame extractor**

```python
# tests/test_frame_extractor.py
import os
import pytest
from unittest.mock import patch, MagicMock
from agent.frame_extractor import extract_frames

@patch("agent.frame_extractor.subprocess.run")
@patch("agent.frame_extractor.shutil.which", return_value="/usr/bin/ffmpeg")
def test_extract_frames_success(mock_which, mock_run, tmp_path):
    """Should call ffmpeg and return frame count"""
    # Create fake frame files
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    for i in range(5):
        (frames_dir / f"frame_{i:04d}.jpg").touch()

    mock_run.return_value = MagicMock(returncode=0)

    video_path = str(tmp_path / "test.mp4")
    output_dir = str(frames_dir)

    # Create fake video file
    with open(video_path, "w") as f:
        f.write("fake video")

    count = extract_frames(video_path, output_dir, fps=24)
    assert count == 5

@patch("agent.frame_extractor.shutil.which", return_value=None)
def test_extract_frames_no_ffmpeg(mock_which):
    """Should raise when ffmpeg not found"""
    with pytest.raises(SystemExit):
        extract_frames("test.mp4", "output", fps=24)

def test_extract_frames_no_video():
    """Should raise when video file doesn't exist"""
    with pytest.raises(SystemExit):
        extract_frames("nonexistent.mp4", "output", fps=24)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_frame_extractor.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement frame_extractor.py**

```python
# agent/frame_extractor.py
import os
import sys
import shutil
import subprocess


def extract_frames(video_path: str, output_dir: str, fps: int = 24) -> int:
    """将视频拆解为 JPEG 帧序列，返回总帧数

    Args:
        video_path: 视频文件路径
        output_dir: 帧输出目录
        fps: 提取帧率
    """
    if not shutil.which("ffmpeg"):
        print("❌ 未找到 ffmpeg，请先安装：")
        print("   macOS:   brew install ffmpeg")
        print("   Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("   Linux:   sudo apt install ffmpeg")
        sys.exit(1)

    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在：{video_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-q:v", "2",
        "-y",
        output_pattern
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise Exception(f"ffmpeg 执行失败：\n{result.stderr[-500:]}")

    frames = sorted([f for f in os.listdir(output_dir) if f.endswith(".jpg")])
    return len(frames)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/test_frame_extractor.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
cd D:/1vibecode-workflow
git add agent/frame_extractor.py tests/test_frame_extractor.py
git commit -m "feat: add ffmpeg frame extractor module"
```

---

### Task 5: Claude Code Skill — vibecode-agent (P0)

**Files:**
- Create: `.claude/skills/vibecode-agent.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p D:/1vibecode-workflow/.claude/skills
```

- [ ] **Step 2: Create vibecode-agent skill**

```markdown
# .claude/skills/vibecode-agent.md
---
name: vibecode-agent
description: VibeCode 产品视频工作流 Agent，支持多轮对话、断点续传、局部修改
---

# VibeCode Agent

你是一个产品视频工作流助手，帮助用户完成从产品图片到网站的完整流程。

## 状态管理

每次启动时，首先读取 `state/workflow.json` 获取当前阶段：
- 文件不存在 → INIT 阶段
- 文件存在 → 读取 stage 字段，从对应阶段继续

## 阶段流程

### INIT
检测 `input/product.jpg` 是否存在：
- 存在 → 进入 ANALYZE
- 不存在 → 提示用户放入产品图

### ANALYZE
用视觉分析产品图片，输出产品特征摘要：
- 产品类型
- 材质/外观
- 使用场景
- 目标用户
- 适合的风格

然后进入 CONFIRM_PRODUCT。

### CONFIRM_PRODUCT
展示选项让用户确认：
1. 面向消费者还是企业？
2. 偏科技风还是生活风？
3. 是否需要模特？
4. 视频比例：16:9 / 9:16 / 1:1

收集用户选择，保存到 workflow.json，进入 PLAN_IMAGES。

### PLAN_IMAGES
生成图1/图2方案选项：

图1（首帧）：
A. 产品悬浮展示
B. 产品包装状态
C. 产品特写

图2（尾帧）：
A. 产品工作状态
B. 产品爆炸图
C. 产品场景图

用户选择后，调用 `agent/prompt_builder.py` 生成 Prompt 初稿，进入 GENERATE_IMAGES。

### GENERATE_IMAGES
展示 Prompt 初稿，提供选项：
1. 直接使用
2. 编辑后使用
3. 重新生成

如果用户选择"编辑"，让用户粘贴修改后的 Prompt。

调用 `agent/image_generator.py` 生成图片，保存到 `generated/image1.png` 和 `generated/image2.png`。

进入 CONFIRM_IMAGES。

### CONFIRM_IMAGES
展示生成的图片（用 Read 工具读取图片），提供选项：
1. 满意，继续
2. 修改图1
3. 修改图2
4. 全部重做

如果用户选择"修改"：
- 询问修改内容（如"换白色背景"）
- 调用 `apply_modification()` 生成新 Prompt
- 重新生成图片
- 回到 CONFIRM_IMAGES

用户满意后，进入 BUILD_VIDEO_PROMPT。

### BUILD_VIDEO_PROMPT
根据图1/图2描述，生成视频过渡 Prompt 初稿。

展示初稿，提供选项：
1. 直接使用
2. 编辑后使用

同时生成 VIDEO_GUIDE.md，包含：
- 即梦AI/Seedance 使用步骤
- 上传图片路径
- 建议参数（时长、比例、分辨率）

进入 WAIT_VIDEO。

### WAIT_VIDEO
提示用户：
"请将生成的视频放入 generated/video.mp4"

轮询检测文件是否存在：
- 存在 → 进入 EXTRACT_FRAMES
- 不存在 → 提示等待

### EXTRACT_FRAMES
调用 `agent/frame_extractor.py` 拆帧：
- 输入：generated/video.mp4
- 输出：generated/frames/
- 显示进度

进入 BUILD_PROJECT。

### BUILD_PROJECT
生成 AI IDE 项目文件：
- 复制帧图片到 projects/{产品名}/public/frames/
- 生成 PROMPT.md（建站提示词）
- 生成 rules.json（编码规范）

进入 DONE。

### DONE
输出完成信息：
"工作流完成！项目文件在 projects/{产品名}/，用 Cursor 打开后按 PROMPT.md 操作。"

## 用户命令

- "重新开始" → 清空 workflow.json，回到 INIT
- "暂停" → 保存当前状态，结束会话
- "跳过视频" → 直接用 input/ 中的图片作为帧

## 错误处理

- API 调用失败 → 保留原 Prompt，提示重试
- ffmpeg 失败 → 检查视频文件，提示重新放入
- 任何错误不更新 workflow.json，保持上一状态
```

- [ ] **Step 3: Commit**

```bash
cd D:/1vibecode-workflow
git add .claude/skills/vibecode-agent.md
git commit -m "feat: add vibecode-agent Claude Code skill"
```

---

### Task 6: Integration Test (P1)

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
# tests/test_integration.py
import os
import json
import pytest
from agent.workflow import Workflow

def test_full_workflow_cycle(tmp_path):
    """Test complete workflow state transitions"""
    state_file = tmp_path / "state" / "workflow.json"
    wf = Workflow(state_file=str(state_file))

    # INIT
    assert wf.get_stage() == "INIT"

    # ANALYZE
    wf.set_stage("ANALYZE")
    assert wf.get_stage() == "ANALYZE"

    # CONFIRM_PRODUCT
    wf.set_stage("CONFIRM_PRODUCT")
    wf.set_data("product", {"name": "Test", "desc": "Test desc", "style": "科技感"})
    assert wf.get_data("product")["name"] == "Test"

    # PLAN_IMAGES
    wf.set_stage("PLAN_IMAGES")
    wf.set_data("images", {
        "img1": {"type": "static", "prompt": "test prompt 1"},
        "img2": {"type": "dynamic", "prompt": "test prompt 2"}
    })

    # GENERATE_IMAGES
    wf.set_stage("GENERATE_IMAGES")
    wf.set_data("images", {
        "img1": {"prompt": "test", "path": "generated/image1.png"},
        "img2": {"prompt": "test", "path": "generated/image2.png"}
    })

    # CONFIRM_IMAGES
    wf.set_stage("CONFIRM_IMAGES")

    # BUILD_VIDEO_PROMPT
    wf.set_stage("BUILD_VIDEO_PROMPT")
    wf.set_data("video_prompt", "test video prompt")

    # WAIT_VIDEO
    wf.set_stage("WAIT_VIDEO")

    # EXTRACT_FRAMES
    wf.set_stage("EXTRACT_FRAMES")

    # BUILD_PROJECT
    wf.set_stage("BUILD_PROJECT")

    # DONE
    wf.set_stage("DONE")
    assert wf.get_stage() == "DONE"

def test_workflow_persistence(tmp_path):
    """Test workflow persists across instances"""
    state_file = tmp_path / "state" / "workflow.json"

    # First instance
    wf1 = Workflow(state_file=str(state_file))
    wf1.set_stage("CONFIRM_PRODUCT")
    wf1.set_data("product", {"name": "Test"})

    # Second instance
    wf2 = Workflow(state_file=str(state_file))
    assert wf2.get_stage() == "CONFIRM_PRODUCT"
    assert wf2.get_data("product")["name"] == "Test"

def test_workflow_reset(tmp_path):
    """Test workflow reset clears all data"""
    state_file = tmp_path / "state" / "workflow.json"
    wf = Workflow(state_file=str(state_file))

    wf.set_stage("DONE")
    wf.set_data("product", {"name": "Test"})
    wf.reset()

    assert wf.get_stage() == "INIT"
    assert wf.get_data("product") is None
```

- [ ] **Step 2: Run all tests**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
cd D:/1vibecode-workflow
git add tests/test_integration.py
git commit -m "test: add integration tests for workflow"
```

---

### Task 7: Final Cleanup and Docs

**Files:**
- Update: `requirements.txt`
- Create: `.gitignore`

- [ ] **Step 1: Update requirements.txt**

```
requests>=2.28.0
python-dotenv>=1.0.0
pytest>=7.0.0
```

- [ ] **Step 2: Create .gitignore**

```
# Python
__pycache__/
*.pyc
.env

# Runtime
state/
generated/
temp/

# IDE
.vscode/
.idea/
```

- [ ] **Step 3: Run all tests one final time**

Run: `cd D:/1vibecode-workflow && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Final commit**

```bash
cd D:/1vibecode-workflow
git add requirements.txt .gitignore
git commit -m "chore: add gitignore and update requirements"
```

---

## Summary

| Task | Component | Priority | Tests |
|------|-----------|----------|-------|
| 1 | workflow.py | P0 | 5 |
| 2 | image_generator.py | P0 | 3 |
| 3 | prompt_builder.py | P1 | 4 |
| 4 | frame_extractor.py | P2 | 3 |
| 5 | Claude Code skill | P0 | - |
| 6 | Integration tests | P1 | 3 |
| 7 | Cleanup | - | - |

**Total: 7 tasks, 18 tests**
