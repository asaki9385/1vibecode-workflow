# VibeCode Agent

AI 驱动的产品视频工作流工具。从一张产品图片出发，经过视觉分析、意图澄清、图生图精修、视频提示词生成和自动抽帧，输出全屏动画 Hero Shot 网页。

## 功能特性

- **状态机架构**：11 阶段完整工作流，支持断点续传
- **双模式交互**：快速模式（Agent 自主决策）/ 详细模式（多轮意图澄清对话）
- **结构化视觉分析**：subject_type 分支、style_profile 四字段连贯推导
- **动态特效选项**：从 movable_elements 自动生成，非固定模板
- **真实色彩提取**：从 image1 提取强调色，避免泛化 AI 调色板
- **GSAP 入场动画**：ease/scale/rotation 根据 style_profile 关键词自动匹配
- **frontend-design 集成**：缓存摘要，避免重复加载
- **后置反馈循环**：4 个关键阶段统一反馈机制

## 工作流

```
INIT -> ANALYZE -> SELECT_MODE -> CONFIRM_PRODUCT -> GENERATE
-> CONFIRM_IMAGES -> BUILD_VIDEO_PROMPT -> WAIT_VIDEO
-> EXTRACT_FRAMES -> BUILD_PROJECT -> DONE
```

### 阶段说明

| 阶段 | 说明 |
|------|------|
| INIT | 检测 input/ 目录中的图片 |
| ANALYZE | 结构化视觉分析，输出 image_analysis（subject_type、movable_elements、style_profile） |
| SELECT_MODE | 强制选择：快速模式 / 详细模式 |
| CONFIRM_PRODUCT | 动态特效选项 + 四维意图澄清（效果/场景/排除/风格） |
| GENERATE | Image1 重绘 + 色彩提取 + Image2 精修 |
| CONFIRM_IMAGES | 结尾意图澄清 + image1->image2 对比（transition_analysis） |
| BUILD_VIDEO_PROMPT | 根据 transition_analysis 生成视频过渡提示词 |
| WAIT_VIDEO | 等待用户放置视频文件 |
| EXTRACT_FRAMES | ffmpeg 抽帧 |
| BUILD_PROJECT | 文案复制 + 色板选择 + frontend-design 规范 + 网页生成 |
| DONE | 完成，归档到 data/ |

## 快速开始

### 1. 安装依赖

```bash
pip install -e ".[dev]"
```

ffmpeg（用于抽帧）：
```bash
# macOS
brew install ffmpeg

# Windows
# 从 https://www.gyan.dev/ffmpeg/builds/ 下载并添加到 PATH

# Linux
sudo apt install ffmpeg
```

### 2. 配置 API Key

编辑 `.env` 文件：
```env
ARK_API_KEY=your-volcengine-api-key
FFMPEG_PATH=/path/to/ffmpeg  # 可选，自动检测时无需配置
```

获取 Key：https://console.volcengine.com/ark → API Key 管理

### 3. 放置产品图片

将产品图片放入 `input/` 目录。支持格式：`.jpg`、`.jpeg`、`.png`、`.webp`、`.gif`、`.bmp`、`.tiff`。

### 4. 启动工作流

在 Claude Code 中运行：
```
/vibecode-agent
```

## 项目结构

```
vibecode-workflow/
├── agent/
│   ├── workflow.py           <- 状态管理
│   ├── image_generator.py    <- Seedream API 封装（img2img 支持）
│   ├── prompt_builder.py     <- 提示词生成（含负面约束）
│   ├── color_extractor.py    <- 色板提取 + 强调色选择
│   ├── frame_extractor.py    <- ffmpeg 抽帧
│   ├── web_builder.py        <- Hero Shot 网页生成（GSAP 参数）
│   ├── config.py             <- 配置管理
│   ├── progress.py           <- 进度通知
│   ├── cache.py              <- 图片缓存
│   ├── batch.py              <- 批量处理
│   └── exceptions.py         <- 自定义异常
├── templates/
│   └── hero_shot.html        <- HTML 模板（GSAP + CSS 回退）
├── .claude/skills/
│   ├── vibecode-agent.md     <- 工作流技能定义（11 阶段）
│   └── hero-shot-builder.md  <- 网页构建技能
├── state/                    <- 运行时状态（自动生成）
├── generated/                <- 生成的图片、视频、帧（自动生成）
│   ├── image1.png
│   ├── image2.png
│   └── frames/
├── projects/                 <- 生成的项目文件
│   └── {product_name}/
│       ├── index.html
│       ├── public/frames/
│       ├── PROMPT.md
│       └── rules.json
├── input/                    <- 放置产品图片
├── .env                      <- API Key 配置
├── pyproject.toml
└── README.md
```

## 核心模块

### prompt_builder.py - 提示词生成

```python
from agent.prompt_builder import (
    build_regenerate_prompt,      # Image1 重绘（基于 subject_type 的特征）
    build_img2img_prompt,         # Image2 精修（基于 movable_elements）
    build_video_prompt,           # 视频过渡提示词（基于 transition_analysis）
    generate_ending_options,      # 结尾选项（subject_type 分支）
    build_ending_prompt,          # 结尾帧提示词
    apply_modification,           # 应用用户修改
)
```

所有提示词函数自动附加 `Avoid: ...`（来自 confirmed_intent.exclude + image_analysis.key_features）。

### color_extractor.py - 色彩提取

```python
from agent.color_extractor import extract_palette, pick_accent_color, hex_to_rgba

palette = extract_palette("generated/image1.png", num_colors=5)
accent = pick_accent_color(palette, image_analysis["style_profile"]["visual_tone"])
glow = hex_to_rgba(accent, 0.3)
```

依赖：Pillow（必需），colorthief（可选，更优量化）。低饱和度/灰度图片自动回退到 visual_tone 预设。

### web_builder.py - 网页生成

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
Agent 根据 image_analysis 自主决策 confirmed_intent，跳过意图澄清。支持中途切换到详细模式。

### 详细模式（Agent 提出完整方案）
Agent 提出完整方案，用户通过多轮对话在四个维度（效果/场景/排除/风格）进行调整。退出关键词：确认/继续/好的/没问题/开始/是。

### 后置反馈循环
ANALYZE、CONFIRM_IMAGES、BUILD_VIDEO_PROMPT、BUILD_PROJECT 阶段在展示结果后均附加统一反馈循环。模糊反馈会通过具体方向选项引导收窄；明确反馈触发重新生成。连续 5 轮后建议跳过并标记 needs_revisit 留待后续优化。

## 用户命令

- **重新开始** - 清除状态，从头开始
- **暂停** - 保存进度，稍后继续
- **跳过视频** - 直接使用 input 图片作为帧

## 常见问题

**Q: ffmpeg 找不到？**
A: 安装 ffmpeg 并确保其在系统 PATH 中。

**Q: 图片生成失败？**
A: 检查 `.env` 中的 ARK_API_KEY 是否正确。

**Q: 如何恢复中断的工作流？**
A: 运行 `/vibecode-agent`，会读取 state/workflow.json 从上次阶段继续。

**Q: GSAP 加载失败？**
A: 模板自动回退到 CSS @keyframes 动画，Agent 会通知你。

**Q: 强调色不理想？**
A: BUILD_PROJECT 阶段会展示 2-3 个候选色供选择，也可手动指定。

## 许可证

MIT
