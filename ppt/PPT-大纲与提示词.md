# VibeCode Agent 教学 PPT 大纲

> 面向学习 Python 开发、AI 应用开发、自动化工作流的学生
> 聚焦「怎么设计、怎么编码、怎么联动」，弱化产品演示

---

## 第1页 封面

**标题**：VibeCode Agent 项目 — 技术实现全过程

**副标题**：基于 Python + 国产 AI 的状态机驱动自动化工作流开发

**底部**：姓名 / 班级 / 课程 / 日期

**讲解重点**：开篇点明本节课核心——不讲产品使用，专注项目架构设计、模块编码、功能落地。

---

## 第2页 目录

```
1. 项目开发目标与整体架构
2. 核心设计：状态机架构实现
3. 开发环境与依赖配置
4. 五大核心模块分步实现
5. 特色功能：结尾帧系统
6. 交互层与全流程调度
7. 关键底层技术细节
8. 联调测试与问题修复
9. 二次开发与总结
```

**讲解重点**：告知学生本节课学习路线，从宏观架构到微观代码逐步拆解。

---

## 第3页 项目开发目标 & 整体架构

### 开发目标

基于 Python 搭建一套**状态机驱动**的自动化工作流，串联「AI 图生图、提示词生成、视频拆帧、静态网页生成」四大能力。

### 四层分层架构

```
┌─────────────────────────────────────┐
│         交互层（Claude Code）         │
│    接收用户指令、反馈运行信息、选项交互    │
├─────────────────────────────────────┤
│         调度层（workflow.py）          │
│   状态机管控10阶段、数据存储、断点续传     │
├─────────────────────────────────────┤
│         功能模块层                    │
│  image_generator / prompt_builder    │
│  frame_extractor / web_builder       │
├─────────────────────────────────────┤
│         外部依赖层                    │
│   火山方舟API / FFmpeg / 本地文件系统    │
└─────────────────────────────────────┘
```

### 项目目录结构

```
vibecode-workflow/
├── agent/
│   ├── workflow.py           ← 状态管理
│   ├── image_generator.py    ← Seedream API
│   ├── prompt_builder.py     ← 提示词生成
│   ├── frame_extractor.py    ← ffmpeg 拆帧
│   └── web_builder.py        ← 网页生成
├── tests/                    ← 45个测试
├── .claude/skills/           ← 技能定义
├── state/                    ← 运行时状态
├── generated/                ← 生成产物
├── projects/                 ← 输出项目
└── input/                    ← 输入图片
```

**讲解重点**：
1. 为什么采用分层架构？（解耦、易维护、单独调试）
2. 先设计架构，再写代码——这是软件开发的第一步。

---

## 第4页 核心设计：状态机架构（项目中枢）

### 设计选型

采用**有限状态机**作为流程调度核心，管控运行阶段、流转顺序、临时数据、断点恢复。

### 10 个标准状态

```
INIT → ANALYZE → CONFIRM_PRODUCT → GENERATE → CONFIRM_IMAGES
  → BUILD_VIDEO_PROMPT → WAIT_VIDEO → EXTRACT_FRAMES
  → BUILD_PROJECT → DONE
```

### 状态流转拓扑

```
        ┌──────────┐
        │   INIT   │
        └────┬─────┘
             ↓
        ┌──────────┐
        │ ANALYZE  │
        └────┬─────┘
             ↓
     ┌───────┴───────┐
     │ CONFIRM_PRODUCT│←───── 用户选择
     └───────┬───────┘
             ↓
     ┌───────────────┐
     │   GENERATE    │──→ 生成图1 → 生成图2
     └───────┬───────┘
             ↓
     ┌───────────────┐
     │ CONFIRM_IMAGES│←───── 用户确认/重做
     └───────┬───────┘
             ↓
     ┌───────────────┐
     │BUILD_VIDEO_   │
     │    PROMPT     │
     └───────┬───────┘
             ↓
     ┌───────────────┐
     │  WAIT_VIDEO   │←───── 等待视频文件
     └───────┬───────┘
             ↓
     ┌───────────────┐
     │EXTRACT_FRAMES │
     └───────┬───────┘
             ↓
     ┌───────────────┐
     │ BUILD_PROJECT │
     └───────┬───────┘
             ↓
     ┌───────────────┐
     │     DONE      │
     └───────────────┘
```

### 核心代码

```python
# agent/workflow.py

STAGES = [
    "INIT", "ANALYZE", "CONFIRM_PRODUCT", "GENERATE",
    "CONFIRM_IMAGES", "BUILD_VIDEO_PROMPT", "WAIT_VIDEO",
    "EXTRACT_FRAMES", "BUILD_PROJECT", "DONE"
]

class Workflow:
    def __init__(self, state_file="state/workflow.json"):
        self._state_file = state_file
        self._data = self._load()

    def set_stage(self, stage: str):
        if stage not in STAGES:
            raise ValueError(f"Invalid stage: {stage}")
        self._data["stage"] = stage
        self.save()

    def set_data(self, key: str, value):
        self._data[key] = value
        self.save()
```

**讲解重点**：
1. 状态机是本项目的**核心中枢**，所有模块都由它调度
2. `STAGES` 列表定义状态空间，`set_stage` 验证合法性
3. 断点续传：每次变更自动 `save()` 到 JSON 文件

---

## 第5页 开发环境 & 依赖配置

### 基础环境

- Python 3.8+
- FFmpeg（视频处理）
- Claude Code（交互终端）

### 依赖安装

```bash
pip install -r requirements.txt
```

### 密钥配置

```env
# .env 文件
ARK_API_KEY=你的火山方舟API密钥
```

### 配置分离设计

```python
# 使用 python-dotenv 自动加载 .env
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("ARK_API_KEY")
```

**讲解重点**：
1. 环境标准化配置的必要性
2. API 密钥分离配置的安全设计思想——密钥不进代码仓库

---

## 第6页 模块一：状态管理 workflow.py

### 模块职责

统一管理运行状态、全局数据、流程重置、断点恢复。

### 核心代码

```python
import json
import os

STAGES = [
    "INIT", "ANALYZE", "CONFIRM_PRODUCT", "GENERATE",
    "CONFIRM_IMAGES", "BUILD_VIDEO_PROMPT", "WAIT_VIDEO",
    "EXTRACT_FRAMES", "BUILD_PROJECT", "DONE"
]

class Workflow:
    def __init__(self, state_file="state/workflow.json"):
        self._state_file = state_file
        self._data = self._load()

    def _load(self):
        """读取本地状态文件，实现断点续传"""
        if os.path.exists(self._state_file):
            with open(self._state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"stage": "INIT"}

    def save(self):
        """持久化到本地 JSON"""
        os.makedirs(os.path.dirname(self._state_file), exist_ok=True)
        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get_stage(self):
        return self._data.get("stage", "INIT")

    def set_stage(self, stage: str):
        if stage not in STAGES:
            raise ValueError(f"Invalid stage: {stage}")
        self._data["stage"] = stage
        self.save()

    def get_data(self, key, default=None):
        return self._data.get(key, default)

    def set_data(self, key: str, value):
        self._data[key] = value
        self.save()

    def reset(self):
        self._data = {"stage": "INIT"}
        self.save()
```

### 设计要点

| 要点 | 实现方式 |
|------|----------|
| 断点续传 | 每次 `save()` 写入 JSON 文件 |
| 状态验证 | `set_stage` 检查是否在 `STAGES` 列表中 |
| 数据存储 | 同一个 `_data` 字典存储状态和业务数据 |
| 重置 | `reset()` 清空数据，回到 INIT |

**讲解重点**：
1. 类的封装思想：状态、数据、读写方法集中管理
2. `load/save` 是断点续传的核心——进程重启后自动恢复

---

## 第7页 模块二：图片生成 image_generator.py

### 模块职责

调用国产豆包 Seedream API，实现「文生图、图生图」两大能力。

### 核心代码

```python
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
SEEDREAM_MODEL = "doubao-seedream-5-0-t2i-250415"

def _image_to_data_url(image_path: str) -> str:
    """本地图片转 Base64 data URL"""
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp"
    }
    mime = mime_map.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def generate_image(prompt: str, output_path: str,
                   reference_image: str = None) -> str:
    """文生图 / 图生图"""
    api_key = os.getenv("ARK_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构建请求参数
    payload = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "size": "2K",
        "response_format": "url",
        "watermark": False
    }

    # 图生图：添加参考图
    if reference_image:
        if reference_image.startswith("http"):
            payload["image"] = reference_image
        else:
            payload["image"] = _image_to_data_url(reference_image)

    # 调用 API
    resp = requests.post(
        f"{BASE_URL}/images/generations",
        headers=headers, json=payload, timeout=60
    )
    resp.raise_for_status()

    # 下载生成的图片
    image_url = resp.json()["data"][0]["url"]
    img_resp = requests.get(image_url, timeout=60)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    return output_path
```

### 图生图流程

```
本地图片 → Base64 编码 → API 请求（prompt + image）
    → API 返回 URL → 下载图片 → 保存到本地
```

**讲解重点**：
1. 图生图（Img2Img）的核心：通过 `image` 参数传递参考图
2. 本地文件必须转 Base64 才能通过网络传输
3. API 返回的是 URL 而非图片本身，需要二次下载

---

## 第8页 模块三：提示词构建 prompt_builder.py

### 模块职责

自动生成三类专业提示词：首尾帧提示词、结尾帧方案、视频过渡提示词。

### 核心代码

```python
def build_regenerate_prompt(effect_type: str, custom_desc: str = "") -> str:
    """生成图1的强约束重绘 Prompt"""
    base = (
        "EXTREMELY IMPORTANT: This is a reference image recreation task. "
        "You MUST extract and preserve EVERY visual element "
        "from the reference image with zero deviation.\n"
        "Strict requirements:\n"
        "- Character features: exact hair color, eye color...\n"
        "- Clothing: exact outfit design, colors, patterns...\n"
        "- Pose: exact body position, hand gestures...\n"
        "- Background: exact elements, colors, atmosphere...\n"
        "Do NOT add new elements. Do NOT change existing elements. "
        "Only improve resolution and rendering quality."
    )

    # 字典派发：根据效果类型添加修饰词
    extras = {
        "wind": "After preserving all reference elements, "
                "add subtle natural wind dynamics: "
                "slight hair movement, gentle fabric flutter.",
        "lighting": "After preserving all reference elements, "
                    "enhance lighting with warm golden hour glow.",
        "scene": "After preserving all reference elements, "
                 "add flowing clouds and dynamic atmosphere.",
        "custom": (f"After preserving all reference elements, "
                   f"{custom_desc}") if custom_desc else ""
    }

    extra = extras.get(effect_type, extras["wind"])
    return f"{base}\n{extra}"


def generate_ending_options(image_analysis: dict) -> list[dict]:
    """基于图1分析结果，生成 3 个结尾方案"""
    subject = image_analysis.get("subject", "主体")
    action = image_analysis.get("action", "存在")
    scene = image_analysis.get("scene", "背景中")
    mood = image_analysis.get("mood", "平静")

    options = [
        {
            "type": "动作完成",
            "description": f"{subject}完成了{action}，满足地休息",
            "prompt": (f"Same {subject} as reference. "
                      f"{subject} has finished {action}, "
                      f"now resting contentedly.")
        },
        {
            "type": "场景拉远",
            "description": f"镜头拉远，展示{subject}在{scene}中的全貌",
            "prompt": (f"Same {subject} as reference. "
                      f"Camera pulls back to reveal the full scene.")
        },
        {
            "type": "情绪变化",
            "description": f"{subject}表情变化，从{mood}变为开心",
            "prompt": (f"Same {subject} as reference. "
                      f"{subject}'s expression changes to happy.")
        }
    ]
    return options
```

### 设计模式

| 模式 | 说明 |
|------|------|
| 字典派发 | 用 `dict.get()` 替代 if/elif，扩展只需加字典条目 |
| 基础+修饰 | 固定 base prompt + 动态 effect modifier |
| 结构化输入 | AI 分析结果 dict → 生成 3 套方案 |

**讲解重点**：
1. 模板化提示词设计：固定模板 + 动态参数，提升复用性
2. 字典派发比 if/elif 更易扩展——新增效果类型只需加一行

---

## 第9页 模块四：视频拆帧 frame_extractor.py

### 模块职责

调用系统工具 FFmpeg，将视频拆解为连续帧图片。

### 核心代码

```python
import os
import shutil
import subprocess

# 自定义 ffmpeg 路径（可选）
FFMPEG_PATH = "ffmpeg-2026-06-08/bin/ffmpeg.exe"

def extract_frames(video_path: str, output_dir: str,
                   fps: int = 24) -> int:
    """从视频提取帧图片，返回总帧数"""
    if fps <= 0:
        raise ValueError("fps must be positive")

    # 1. 查找 ffmpeg（渐进回退）
    ffmpeg_cmd = (FFMPEG_PATH
                  if os.path.exists(FFMPEG_PATH)
                  else shutil.which("ffmpeg"))
    if not ffmpeg_cmd:
        raise RuntimeError(
            "未找到 ffmpeg，请先安装：\n"
            "  macOS:   brew install ffmpeg\n"
            "  Windows: 下载后加入 PATH\n"
            "  Linux:   sudo apt install ffmpeg"
        )

    # 2. 验证视频文件
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")

    # 3. 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")

    # 4. 构建 ffmpeg 命令
    cmd = [
        ffmpeg_cmd,
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-q:v", "2",       # 高质量 JPEG
        "-y",              # 覆盖已有文件
        output_pattern
    ]

    # 5. 执行命令
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg 执行失败：\n{result.stderr[-500:]}"
        )

    # 6. 统计帧数
    frames = sorted([
        f for f in os.listdir(output_dir)
        if f.endswith(".jpg")
    ])
    return len(frames)
```

### 调用链路

```
Python → subprocess.run() → FFmpeg 命令行
    → 按帧率拆分视频 → 输出 frame_0001.jpg ~ frame_XXXX.jpg
```

**讲解重点**：
1. `subprocess.run` 是 Python 调用外部命令的标准方式
2. `shutil.which` 自动查找系统 PATH 中的可执行文件
3. `-q:v 2` 是 ffmpeg 的高质量参数（1-31，越小质量越高）

---

## 第10页 模块五：网页生成 web_builder.py

### 模块职责

接收帧序列信息，动态拼接 HTML，生成英雄镜头风格展示网页。

### 核心代码

```python
def generate_player_html(frame_count: int, fps: int = 24,
                         title: str = "Hero Shot") -> str:
    """生成英雄镜头风格展示网页"""
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    if fps <= 0:
        raise ValueError("fps must be positive")

    duration = f"{frame_count // fps}:{frame_count % fps:02d}"

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  /* 暗色主题 + 磨砂玻璃效果 */
  :root {{
    --bg: #0a0a0a;
    --surface: rgba(255,255,255,0.08);
  }}
  body {{ background: var(--bg); margin: 0; }}
  #bg {{ position: fixed; inset: 0; width: 100%; height: 100%; }}
  /* ... 完整 CSS ... */
</style>
</head>
<body>
<canvas id="bg"></canvas>
<div class="content">
  <h1>{title}</h1>
  <p>AI-Generated Motion · {frame_count} frames · {fps}fps</p>
</div>
<script>
const TOTAL = {frame_count};
const FPS = {fps};
const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');
let frames = [], current = 0, loaded = 0;

// 预加载帧图片
for (let i = 1; i <= TOTAL; i++) {{
  const img = new Image();
  img.onload = () => {{
    loaded++;
    if (loaded === 1) draw(0);
    if (loaded >= 12) startPlayback();
  }};
  img.src = `public/frames/frame_${{String(i).padStart(4, '0')}}.jpg`;
  frames.push(img);
}}

function draw(idx) {{
  const img = frames[idx];
  if (!img || !img.complete) return;
  const scale = Math.max(
    canvas.width / img.naturalWidth,
    canvas.height / img.naturalHeight
  );
  const w = img.naturalWidth * scale;
  const h = img.naturalHeight * scale;
  ctx.drawImage(img,
    (canvas.width - w) / 2,
    (canvas.height - h) / 2, w, h);
}}

function loop(time) {{
  if (time - lastTime >= 1000 / FPS) {{
    current = (current + 1) % TOTAL;
    draw(current);
    lastTime = time;
  }}
  requestAnimationFrame(loop);
}}
</script>
</body>
</html>'''
```

### 关键 JS 逻辑

| 功能 | 实现方式 |
|------|----------|
| 帧预加载 | `new Image()` + `onload` 回调 |
| 渐进播放 | 加载 12 帧后自动开始 |
| Canvas 渲染 | `ctx.drawImage()` cover-fit 铺满 |
| 动画循环 | `requestAnimationFrame` + 时间戳控制帧率 |

**讲解重点**：
1. Python 动态生成前端代码的思路——f-string 拼接 HTML
2. Canvas 比 `<img>` 标签更适合逐帧动画——像素级控制
3. `requestAnimationFrame` 比 `setInterval` 更流畅——与显示器刷新率同步

---

## 第11页 特色功能：智能结尾帧系统

### 设计目标

图2 不再是简单的图1微调，而是有意义的「结尾帧」——支持 AI 自动推断 + 用户指定的混合模式。

### 完整执行链路

```
图1 生成完成
    ↓
AI 分析图1 → 识别主体/动作/场景/情绪
    ↓
generate_ending_options() → 生成 3 套结尾方案
    ↓
展示选项给用户 → 用户选择或自定义
    ↓
build_ending_prompt() → 生成强约束 Prompt
    ↓
generate_image() → 基于图1生成图2
    ↓
图1 + 图2 = 视频首尾帧
```

### 三套结尾方案示例

| # | 类型 | 描述 |
|---|------|------|
| 1 | 动作完成 | 主体完成当前动作，自然收尾 |
| 2 | 场景拉远 | 镜头拉远，展示完整环境 |
| 3 | 情绪变化 | 表情从专注变为开心 |

### 核心代码

```python
def generate_ending_options(image_analysis: dict) -> list[dict]:
    """自动生成 3 种结尾帧方案"""
    subject = image_analysis.get("subject", "主体")
    action = image_analysis.get("action", "存在")
    scene = image_analysis.get("scene", "背景中")
    mood = image_analysis.get("mood", "平静")

    options = [
        {"type": "动作完成",
         "description": f"{subject}完成了{action}，满足地休息",
         "prompt": f"Same {subject} as reference. "
                   f"{subject} has finished {action}."},
        {"type": "场景拉远",
         "description": f"镜头拉远，展示{subject}在{scene}中的全貌",
         "prompt": f"Same {subject} as reference. "
                   f"Camera pulls back to reveal full scene."},
        {"type": "情绪变化",
         "description": f"{subject}表情变化，从{mood}变为开心",
         "prompt": f"Same {subject} as reference. "
                   f"{subject}'s expression changes to happy."}
    ]
    return options

def build_ending_prompt(original_features: str,
                        ending_description: str) -> str:
    """基于图1特征和结尾描述，生成图2 Prompt"""
    if not original_features:
        raise ValueError("original_features cannot be empty")
    if not ending_description:
        raise ValueError("ending_description cannot be empty")

    return (
        f"Same subject as reference image. "
        f"Preserve ALL original features: {original_features}. "
        f"Change: {ending_description}. "
        f"Do NOT add new elements not mentioned above. "
        f"Maintain identical art style, color palette."
    )
```

**讲解重点**：
1. 多模块协同：状态机 → prompt_builder → image_generator
2. AI 分析结果结构化为 dict，驱动方案生成
3. 强约束 Prompt 保证图1→图2的一致性

---

## 第12页 交互层：Claude Code 指令交互

### 技能配置

通过 `.claude/skills/vibecode-agent.md` 配置自定义指令 `/vibecode-agent`。

### 交互流程

```
用户输入 /vibecode-agent
    ↓
读取 state/workflow.json → 获取当前阶段
    ↓
根据阶段执行对应逻辑
    ↓
展示选项给用户（CONFIRM_PRODUCT / CONFIRM_IMAGES）
    ↓
用户选择 → 更新状态 → 继续下一阶段
```

### 支持的用户命令

| 命令 | 效果 |
|------|------|
| 重新开始 | 清空 workflow.json，回到 INIT |
| 暂停 | 保存当前状态，结束会话 |
| 跳过视频 | 直接用 input 图片作为帧 |

### 技能文件结构

```markdown
---
name: vibecode-agent
description: VibeCode 产品视频工作流 Agent
---

# 阶段流程
### INIT
检测 input/ 目录...

### ANALYZE
用视觉分析图片...

### GENERATE
调用 image_generator.py...
```

**讲解重点**：
1. Claude Code 技能系统：Markdown 文件定义 Agent 行为
2. 交互层与 Python 后端的对接——通过 shell 调用 Python 模块

---

## 第13页 全流程调度：状态机串联所有模块

### 模块调用时序

```
用户: /vibecode-agent
    │
    ▼
┌─────────────────────────────────────────────┐
│  INIT: 检测 input/ 目录                      │
│  ANALYZE: 视觉分析图片内容                    │
│  CONFIRM_PRODUCT: 用户选择效果和比例           │
├─────────────────────────────────────────────┤
│  GENERATE:                                   │
│    ├→ prompt_builder.build_regenerate_prompt │
│    ├→ image_generator.generate_image (图1)   │
│    ├→ prompt_builder.generate_ending_options │
│    ├→ prompt_builder.build_ending_prompt     │
│    └→ image_generator.generate_image (图2)   │
├─────────────────────────────────────────────┤
│  CONFIRM_IMAGES: 用户确认首尾帧              │
│  BUILD_VIDEO_PROMPT: 生成视频提示词           │
│  WAIT_VIDEO: 等待 generated/video.mp4        │
│  EXTRACT_FRAMES: frame_extractor 拆帧        │
│  BUILD_PROJECT: web_builder 生成网页          │
├─────────────────────────────────────────────┤
│  DONE: 完成                                  │
└─────────────────────────────────────────────┘
```

### 状态-模块对应表

| 状态 | 调用模块 | 产出 |
|------|----------|------|
| GENERATE | image_generator + prompt_builder | image1.png, image2.png |
| EXTRACT_FRAMES | frame_extractor | frames/*.jpg |
| BUILD_PROJECT | web_builder | index.html |

**讲解重点**：
1. 全局视角：所有独立模块如何被状态机统一调度
2. 每个状态只做一件事，职责清晰

---

## 第14页 技术细节1：图生图 API 异常处理

### 常见异常场景

| 异常 | 原因 | 处理 |
|------|------|------|
| 401 Unauthorized | API 密钥错误 | 检查 .env 配置 |
| Timeout | 网络超时 | 增加 timeout 参数 |
| 400 Bad Request | 图片格式非法 | 验证文件扩展名 |
| 500 Server Error | API 服务异常 | 重试或更换模型 |

### 代码实现

```python
def generate_image(prompt, output_path, reference_image=None):
    try:
        resp = requests.post(
            api_url, headers=headers,
            json=payload, timeout=60
        )
        resp.raise_for_status()  # 自动抛出 HTTP 错误
    except requests.exceptions.Timeout:
        raise RuntimeError("API 请求超时，请检查网络")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise RuntimeError("API 密钥无效，请检查 .env")
        raise RuntimeError(f"API 错误: {e}")

    # 下载图片（二次异常处理）
    try:
        img_resp = requests.get(image_url, timeout=60)
        img_resp.raise_for_status()
    except Exception:
        raise RuntimeError("图片下载失败")

    with open(output_path, "wb") as f:
        f.write(img_resp.content)
```

**讲解重点**：
1. 工业级开发的容错思维——代码不仅要实现功能，还要处理异常
2. `try-except` 分层捕获，给出有针对性的错误提示

---

## 第15页 技术细节2：跨平台 FFmpeg 兼容

### 渐进回退策略

```python
# 1. 优先使用自定义路径
ffmpeg_cmd = FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else None

# 2. 回退到系统 PATH
if not ffmpeg_cmd:
    ffmpeg_cmd = shutil.which("ffmpeg")

# 3. 找不到则抛出友好提示
if not ffmpeg_cmd:
    raise RuntimeError(
        "未找到 ffmpeg，请先安装：\n"
        "  macOS:   brew install ffmpeg\n"
        "  Windows: 下载后加入 PATH\n"
        "  Linux:   sudo apt install ffmpeg"
    )
```

### 跨平台要点

| 平台 | 安装方式 | 路径特点 |
|------|----------|----------|
| macOS | `brew install ffmpeg` | `/usr/local/bin/ffmpeg` |
| Windows | 下载解压 | 需手动加入 PATH |
| Linux | `apt install` | `/usr/bin/ffmpeg` |

**讲解重点**：
1. `shutil.which` 自动查找系统 PATH——跨平台关键
2. 友好的错误提示比报错堆栈更有用

---

## 第16页 技术细节3：断点续传持久化

### 实现原理

```
运行过程中：
    每次状态变更 → save() → 写入 state/workflow.json

进程重启时：
    读取 state/workflow.json → 恢复 stage 和 data → 从断点继续

流程重置时：
    reset() → 清空 JSON → 回到 INIT
```

### 状态文件示例

```json
{
  "stage": "CONFIRM_IMAGES",
  "image_analysis": {
    "subject": "动漫少女",
    "action": "做嘘的手势",
    "scene": "放射线背景",
    "mood": "安静、温柔"
  },
  "effect_type": "wind",
  "aspect_ratio": "16:9"
}
```

### 设计要点

- JSON 格式：人类可读，便于调试
- 自动保存：每次 `set_stage` / `set_data` 自动写入
- 原子性：单文件写入，不存在部分更新问题

**讲解重点**：
1. 本地文件作为简易「数据库」——适合小型项目
2. 数据持久化是「断点续传」的基础

---

## 第17页 联调测试 & 问题修复

### 测试覆盖

```bash
$ pytest tests/ -v
45 passed in 0.11s
```

### 典型问题与修复

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 首尾帧风格不一致 | Prompt 约束不够强 | 强化特征提取 Prompt |
| FFmpeg 命名混乱 | 格式化字符串错误 | 统一使用 `%04d` |
| 状态跳转错乱 | 缺少合法性校验 | `set_stage` 验证 STAGES |
| 图片 Base64 超大 | 大图未压缩 | 限制 size 为 "2K" |

### 测试代码示例

```python
def test_build_regenerate_prompt_wind():
    """Should generate wind regeneration prompt"""
    result = build_regenerate_prompt("wind")
    assert "re-rendering" in result.lower()
    assert "preserve" in result.lower()
    assert "wind" in result.lower()

def test_generate_ending_options_panda():
    """Should generate ending options for panda"""
    analysis = {
        "subject": "卡通熊猫",
        "action": "坐着吃竹子",
        "scene": "白色背景",
        "mood": "可爱、满足"
    }
    options = generate_ending_options(analysis)
    assert len(options) >= 2
    assert "卡通熊猫" in options[0]["prompt"]
```

**讲解重点**：
1. 真实开发流程：编码 → 测试 → 发现问题 → 迭代修复
2. TDD（测试驱动开发）：先写测试，再写实现

---

## 第18页 完整项目运行演示

### 运行效果

**终端输出（简化）：**
```
/vibecode-agent
> 检测到 input/photo.jpg
> 分析：动漫少女，浅绿色长发，做嘘的手势
> 请选择效果：A（风吹）+ C（场景变化），16:9
> 生成图1... ✓
> 结尾方案：
  1. 动作完成
  2. 场景拉远
  3. 情绪变化
> 选择 1
> 生成图2... ✓
> 生成视频提示词... ✓
> 等待 video.mp4... ✓
> 拆帧：123 帧 ✓
> 生成项目文件 ✓
> 工作流完成！
```

**生成产物：**
```
projects/anime-girl/
├── index.html          ← 展示网页
├── public/frames/      ← 123 帧图片
├── PROMPT.md           ← 建站提示词
└── rules.json          ← 编码规范
```

**讲解重点**：
1. 验证：代码逻辑、模块联动、架构设计全部落地
2. 从一张图片到完整展示网页的全自动化流程

---

## 第19页 二次开发拓展

### 拓展方向

| 方向 | 难度 | 说明 |
|------|------|------|
| 新增结尾帧方案 | ⭐ | 修改 `prompt_builder.py` 字典 |
| 添加简易 GUI | ⭐⭐ | 用 tkinter / Flask 做界面 |
| 批量处理 | ⭐⭐ | 循环调用 workflow 处理多张图 |
| 修改网页样式 | ⭐ | 编辑 `web_builder.py` 的 CSS |
| 接入其他 AI API | ⭐⭐ | 替换 `image_generator.py` 的接口 |

### 课堂实操任务

1. **基础**：读懂五大模块代码，标注关键逻辑
2. **实操**：在 `prompt_builder.py` 新增一种结尾帧方案
3. **进阶**：在 `image_generator.py` 补充自定义异常提示

**讲解重点**：
1. 引导学生在现有代码基础上自主修改、创新
2. 从「读懂代码」到「修改代码」到「写出新功能」

---

## 第20页 总结 & 知识点复盘

### 项目实现总结

采用「状态机 + 模块化分层架构」，整合 Python、国产 AI API、子进程调用、前端代码生成等技术。

### 核心知识点

| 类别 | 知识点 |
|------|--------|
| 架构设计 | 分层思想、有限状态机、模块解耦 |
| Python 技术 | 类与对象、subprocess、网络请求、文件读写、JSON 持久化 |
| AI 应用 | 图生图 API 调用、Prompt 工程、Base64 编码 |
| 前端技术 | Canvas 逐帧动画、requestAnimationFrame、CSS 变量 |
| 工程实践 | TDD、异常处理、跨平台兼容、配置分离 |

### 项目代码量

```
agent/workflow.py        71 行
agent/image_generator.py 83 行
agent/prompt_builder.py  157 行
agent/frame_extractor.py 51 行
agent/web_builder.py     459 行
tests/                   45 个测试
─────────────────────────────
总计约 820 行核心代码
```

**讲解重点**：
1. 800 行代码完成一个完整的 AI 自动化工作流
2. 简洁设计的力量——每个模块职责单一，易于理解和修改
3. 答疑环节

---

## 附录：效果展示页配图提示词

> 以下仅在第18页（运行演示）等效果展示页使用

### 首尾帧对比展示

```
Prompt: A side-by-side comparison showing two anime-style images.
Left image: an anime girl with light green hair making a "shh" gesture
with finger on lips, wearing school uniform, on gray radial background.
Right image: the same girl smiling gently with hands down, same outfit
and background. Clean white background, professional presentation style,
labeled "Before" and "After". --ar 16:9 --v 6
```

### 网页成品展示

```
Prompt: A dark-themed web browser mockup showing a full-screen
cinematic animation player. The browser displays an anime character
as background with elegant overlay text "Be Silent for the Future".
Bottom stats bar shows "123 frames · 24fps · 5.1s". Modern UI with
glass-morphism effects. Clean professional screenshot style. --ar 16:9 --v 6
```

---

## 附录：授课技巧

### 讲解顺序

```
架构设计 → 核心中枢（状态机）→ 分模块实现
    → 模块联动 → 技术细节 → 联调测试
```

### 代码讲解原则

- **抓大放小**：只讲核心逻辑，跳过工具类
- **先整体后局部**：先看函数签名，再看内部实现
- **结合已学知识**：衔接 Python 类、文件操作、网络请求

### 页数精简方案（课时不足时）

- 第6-10页五大模块 → 合并为 2 页「核心模块合集」
- 第14-16页技术细节 → 合并为 1 页「底层技术优化」
