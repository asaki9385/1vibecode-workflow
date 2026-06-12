# VibeCode Agent

AI 驱动的产品视频工作流工具。从一张产品图片出发，经过视觉分析、意图澄清、图生图微调、视频提示词生成、自动拆帧，最终输出全屏背景动画展示网页。

## 功能特点

- **状态机架构**：11 个阶段的完整工作流，支持断点续传
- **双模式交互**：快速模式（agent 自主决策）/ 精细模式（意图澄清对话）
- **结构化视觉分析**：subject_type 分支驱动，style_profile 四字段同源派生
- **动态效果选项**：基于 movable_elements 自动生成，非固定模板
- **真实色值提取**：从 image1 提取 accent 色，避免 AI 审美套路配色
- **GSAP 入场动画**：按 style_profile 关键词自动匹配 ease/scale/rotation
- **frontend-design 规范接入**：摘要缓存方式，避免重复加载
- **生成后反馈循环**：4 个关键节点统一反馈机制，支持迭代精修

## 工作流程

```
INIT → ANALYZE → SELECT_MODE → CONFIRM_PRODUCT → GENERATE
→ CONFIRM_IMAGES → BUILD_VIDEO_PROMPT → WAIT_VIDEO
→ EXTRACT_FRAMES → BUILD_PROJECT → DONE
```

### 阶段说明

| 阶段 | 说明 |
|------|------|
| INIT | 检测 input/ 目录图片 |
| ANALYZE | 结构化视觉分析，输出 image_analysis（含 subject_type、movable_elements、style_profile） |
| SELECT_MODE | 强制选择：快速模式 / 精细模式 |
| CONFIRM_PRODUCT | 动态效果选项生成 + 4 维度意图澄清（效果/场景/排除/风格） |
| GENERATE | 图1 重绘 + 色彩提取 + 图2 微调 |
| CONFIRM_IMAGES | 结尾意图澄清 + 图1→图2 对比分析（transition_analysis） |
| BUILD_VIDEO_PROMPT | 基于 transition_analysis 生成视频过渡 Prompt |
| WAIT_VIDEO | 等待用户放入视频文件 |
| EXTRACT_FRAMES | ffmpeg 拆帧 |
| BUILD_PROJECT | 文案生成 + 色板选择 + frontend-design 规范 + 网页生成 |
| DONE | 完成，归档到 data/ |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

需要 ffmpeg（拆帧必须）：
```bash
# macOS
brew install ffmpeg

# Windows
# 下载 https://www.gyan.dev/ffmpeg/builds/ 后加入 PATH

# Linux
sudo apt install ffmpeg
```

### 2. 配置 API Key

编辑 `.env` 文件：
```env
ARK_API_KEY=你的火山方舟API密钥
```

获取地址：https://console.volcengine.com/ark → API Key 管理

### 3. 准备产品图片

将产品图片放入 `input/` 目录，支持 `.jpg`、`.jpeg`、`.png`、`.webp`、`.gif`、`.bmp`、`.tiff` 格式。

### 4. 启动工作流

在 Claude Code 中运行：
```
/vibecode-agent
```

## 项目结构

```
vibecode-workflow/
├── agent/
│   ├── workflow.py           ← 状态管理
│   ├── image_generator.py    ← Seedream API 封装（支持 img2img）
│   ├── prompt_builder.py     ← 提示词生成（含 negative constraints）
│   ├── color_extractor.py    ← 色板提取 + accent 色选择
│   ├── frame_extractor.py    ← ffmpeg 拆帧
│   ├── web_builder.py        ← 英雄镜头网页生成（GSAP 参数）
│   ├── config.py             ← 配置管理
│   ├── progress.py           ← 进度通知
│   ├── cache.py              ← 图片缓存
│   ├── batch.py              ← 批量处理
│   └── exceptions.py         ← 自定义异常
├── templates/
│   └── hero_shot.html        ← HTML 模板（GSAP + CSS fallback）
├── .claude/skills/
│   ├── vibecode-agent.md     ← 工作流技能定义（11 阶段）
│   └── hero-shot-builder.md  ← 网页构建技能
├── state/                    ← 运行时状态（自动生成）
├── generated/                ← 生成的图片、视频、帧（自动生成）
│   ├── image1.png
│   ├── image2.png
│   └── frames/
├── projects/                 ← 生成的项目文件
│   └── {产品名}/
│       ├── index.html
│       ├── public/frames/
│       ├── PROMPT.md
│       └── rules.json
├── input/                    ← 放产品图片
├── .env                      ← API 密钥配置
├── requirements.txt
└── README.md
```

## 核心模块

### prompt_builder.py — 提示词生成

```python
from agent.prompt_builder import (
    build_regenerate_prompt,      # 图1 重绘（按 subject_type 激活特征维度）
    build_img2img_prompt,         # 图2 微调（基于 movable_elements）
    build_video_prompt,           # 视频过渡 Prompt（基于 transition_analysis）
    generate_ending_options,      # 结尾方案（按 subject_type 分支）
    build_ending_prompt,          # 结尾帧 Prompt
    apply_modification,           # 应用用户修改
)
```

所有 prompt 函数自动追加 `Avoid: ...` 部分，来源：confirmed_intent.exclude + image_analysis.key_features。

### color_extractor.py — 色彩提取

```python
from agent.color_extractor import extract_palette, pick_accent_color, hex_to_rgba

palette = extract_palette("generated/image1.png", num_colors=5)
accent = pick_accent_color(palette, image_analysis["style_profile"]["visual_tone"])
glow = hex_to_rgba(accent, 0.3)
```

依赖：Pillow（必须）、colorthief（可选，提升量化质量）。低饱和/灰度图自动 fallback 到 visual_tone 预设色。

### web_builder.py — 网页生成

```python
from agent.web_builder import generate_player_html, get_design_direction, get_animation_preset

html = generate_player_html(
    frame_count=120, fps=24, title="项目名称",
    copy={"tag": "...", "title": "...", "subtitle": "...", "description": "...", "cta_primary": "...", "cta_secondary": "..."},
    font_heading="Clash Display", font_body="Satoshi",
    accent_color="#ff00ff", accent_glow="rgba(255, 0, 255, 0.3)",
    font_import="https://fonts.googleapis.com/css2?family=Satoshi...",
    anim_ease="expo.out", anim_duration="0.5", anim_stagger="0.15",
    gsap_scale="0.95", gsap_rotation="0",
)
```

### workflow.json 结构

```json
{
  "stage": "当前阶段",
  "mode": "quick | detailed",
  "image_analysis": {
    "subject": "...",
    "subject_type": "person|product|landscape|anime_character|abstract|architecture|food|other",
    "movable_elements": ["..."],
    "key_features": ["..."],
    "style_profile": {
      "keywords": ["..."],
      "visual_tone": "...",
      "copy_tone": "...",
      "camera_style": "..."
    }
  },
  "confirmed_intent": { "effect": "...", "scene": "...", "exclude": "...", "style": "..." },
  "transition_analysis": { "changed_elements": ["..."], "change_description": "..." },
  "extracted_palette": { "full_palette": ["..."], "accent_color": "#...", "accent_glow": "rgba(...)" },
  "iteration_history": [ {"stage": "...", "feedback": "...", "action": "..."} ],
  "needs_revisit": { "ANALYZE": false, "CONFIRM_IMAGES": false, "BUILD_VIDEO_PROMPT": false, "BUILD_PROJECT": false }
}
```

## 交互模式

### 快速模式（quick）
agent 基于 image_analysis 自行决定 confirmed_intent，跳过意图澄清对话。支持中途切换到精细模式。

### 精细模式（agent 提出完整方案）
agent 先提出完整方案描述，用户通过多轮对话逐步明确 4 个维度（效果/场景/排除/风格）。退出短语：`确认/继续/可以了/没问题/开始/go/ok/行`。

### 生成后反馈循环
ANALYZE、CONFIRM_IMAGES、BUILD_VIDEO_PROMPT、BUILD_PROJECT 四个节点展示结果后统一追加反馈循环。模糊反馈用具体方向选项收窄，明确反馈调用对应函数重新生成。连续 5 轮不满意可跳过，标记 needs_revisit 待后续精修。

## 用户命令

- **重新开始** — 清空状态，从头开始
- **暂停** — 保存当前进度，下次继续
- **跳过视频** — 直接用输入图片作为帧

## 常见问题

**Q：ffmpeg 未找到？**
A：安装 ffmpeg 并确保在系统 PATH 中。

**Q：图片生成失败？**
A：检查 `.env` 中的 `ARK_API_KEY` 是否正确。

**Q：如何恢复中断的工作流？**
A：直接运行 `/vibecode-agent`，会自动从上次中断处继续（读取 state/workflow.json）。

**Q：GSAP 加载失败？**
A：模板自动使用 CSS @keyframes 动画兜底。agent 会在展示结果时告知。

**Q：accent 色提取不理想？**
A：BUILD_PROJECT 阶段会展示 2-3 个候选色供选择，也可手动指定。

## 许可证

MIT
