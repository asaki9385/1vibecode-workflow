# VibeCode Agent 设计文档

## 概述

将 VibeCode 工作流从固定脚本升级为**状态机 + 多轮对话 Agent**，支持断点续传、局部修改、选项驱动交互。

## 架构方案

**方案 A：轻量 Skill + Python 工具包**

- Claude Code skill 负责对话流和编排
- Python 脚本封装 API 调用（Seedream、ffmpeg）
- `workflow.json` 存储阶段 + 最近结果

## 目录结构

```
vibecode-workflow/
├── .env                    ← API 密钥
├── state/
│   └── workflow.json       ← 状态持久化
├── generated/
│   ├── image1.png          ← 生成的图片
│   ├── image2.png
│   └── video.mp4           ← 用户放入的视频
├── agent/
│   ├── image_generator.py  ← Seedream API 封装
│   ├── frame_extractor.py  ← ffmpeg 拆帧
│   ├── prompt_builder.py   ← Prompt 生成
│   └── workflow.py         ← 状态管理
├── scripts/
│   └── (保留原有脚本作为独立工具)
└── input/
    └── product.jpg         ← 用户产品图
```

## workflow.json 结构

```json
{
  "stage": "CONFIRM_IMAGES",
  "product": {
    "name": "智能门铃",
    "desc": "...",
    "style": "科技感"
  },
  "images": {
    "img1": {"prompt": "...", "path": "generated/image1.png"},
    "img2": {"prompt": "...", "path": "generated/image2.png"}
  },
  "video_prompt": "...",
  "config": {
    "ratio": "9:16",
    "has_model": false
  }
}
```

## 状态流转

```
INIT → ANALYZE → CONFIRM_PRODUCT → PLAN_IMAGES → GENERATE_IMAGES 
    → CONFIRM_IMAGES → BUILD_VIDEO_PROMPT → WAIT_VIDEO → EXTRACT_FRAMES 
    → BUILD_PROJECT → DONE
```

### 状态行为

| 状态 | Claude 行为 | Python 行为 |
|------|------------|------------|
| INIT | 检测 input/product.jpg | - |
| ANALYZE | 用视觉分析产品图片，生成产品特征摘要，让用户确认 | - |
| CONFIRM_PRODUCT | 展示选项，收集用户输入 | 保存到 workflow.json |
| PLAN_IMAGES | 生成图1/图2方案选项 | - |
| GENERATE_IMAGES | 展示 Prompt 初稿，用户可编辑 | 调用 Seedream API |
| CONFIRM_IMAGES | 展示图片，提供修改选项 | - |
| BUILD_VIDEO_PROMPT | 生成视频 Prompt 初稿 | 保存 Prompt |
| WAIT_VIDEO | 提示用户放入 video.mp4 | 检测文件是否存在 |
| EXTRACT_FRAMES | 显示进度 | 调用 ffmpeg |
| BUILD_PROJECT | 生成 PROMPT.md | 复制帧图片 |
| DONE | 完成提示 | - |

### 局部修改循环

```
CONFIRM_IMAGES ←→ GENERATE_IMAGES
(用户说"改背景" → 回到 GENERATE_IMAGES，只修改对应 Prompt 部分)
```

**局部修改机制：**
- 用户输入修改请求（如"换白色背景"、"加模特"）
- Claude 调用 `apply_modification(original_prompt, user_request)` 生成新 Prompt
- 新 Prompt = 原 Prompt 的主体描述 + 用户请求的修改部分
- 重新调用 Seedream API 生成图片

## Claude Code Skill

**Skill 名称：** `vibecode-agent`

**触发方式：**
- `/vibecode-agent`
- 或自然语言："开始产品视频工作流"

**职责：**
1. 读取 `state/workflow.json` 判断当前阶段
2. 根据阶段执行对应行为
3. 展示选项给用户
4. 调用 Python 模块执行实际工作
5. 更新 workflow.json

**对话模式：**
- Claude 提供选项，用户选择，Claude 执行
- 关键节点确认，其他自动推进

## Python 模块

### agent/image_generator.py

```python
def generate_image(prompt: str, output_path: str) -> str:
    """调用 Seedream API 生成图片，返回路径"""

def regenerate_with_modification(original_prompt: str, modification: str, output_path: str) -> str:
    """局部修改：合并原 Prompt + 修改描述，重新生成"""
```

### agent/frame_extractor.py

```python
def extract_frames(video_path: str, output_dir: str, fps: int = 24) -> int:
    """调用 ffmpeg 拆帧，返回总帧数"""
```

### agent/prompt_builder.py

```python
def analyze_product(image_path: str) -> dict:
    """分析产品图片，返回产品特征"""

def build_image_prompt(product_info: dict, image_type: str) -> str:
    """生成图片 Prompt 初稿"""

def build_video_prompt(img1_desc: str, img2_desc: str) -> str:
    """生成视频 Prompt 初稿"""

def apply_modification(original_prompt: str, user_request: str) -> str:
    """根据用户修改请求调整 Prompt"""
```

### agent/workflow.py

```python
def load_workflow() -> dict:
    """加载 workflow.json"""

def save_workflow(data: dict):
    """保存 workflow.json"""

def get_stage() -> str:
    """获取当前阶段"""

def set_stage(stage: str):
    """设置阶段"""
```

## 错误处理与恢复

**断点续传：**
- 每个阶段完成后自动保存 workflow.json
- 重新启动时读取 workflow.json，从上次阶段继续
- 用户可随时说"重新开始"清空状态

**错误处理：**
- API 调用失败：保留原 Prompt，提示用户重试
- ffmpeg 失败：检查视频文件，提示重新放入
- 图片生成失败：不更新 workflow.json，保持上一状态

**用户中断：**
- 用户可随时说"暂停"，当前状态已保存
- 下次启动自动恢复

**状态清理：**
- 用户说"重新开始" → 清空 workflow.json，回到 INIT
- 用户说"跳过视频" → 可选直接用现有帧图片

## 实现优先级

1. **P0** - workflow.py 状态管理
2. **P0** - image_generator.py（Seedream API）
3. **P0** - Claude Code skill 核心流程
4. **P1** - prompt_builder.py
5. **P1** - 局部修改支持
6. **P2** - frame_extractor.py（依赖 ffmpeg）
7. **P2** - BUILD_PROJECT 阶段
