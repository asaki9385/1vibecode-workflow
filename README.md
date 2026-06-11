# VibeCode Agent

AI 驱动的产品视频工作流工具，支持图生图微调、结尾帧生成、英雄镜头展示。

## 功能特点

- **状态机架构**：10 个阶段的完整工作流，支持断点续传
- **图生图微调**：基于参考图重新生成，保留所有视觉元素
- **结尾帧系统**：AI 自动生成 2-3 个结尾方案，用户选择后生成
- **自动拆帧**：调用 ffmpeg 从视频提取帧序列
- **英雄镜头展示**：帧序列转化为全屏背景动画网页
- **多轮对话**：Claude Code 驱动，选项式交互

## 工作流程

```
产品图片 → 分析 → 确认效果 → 图1(首帧) → 选择结尾方案 → 图2(尾帧)
    → 生成视频提示词 → 用户生成视频 → 拆帧 → 生成展示网页
```

### 阶段说明

| 阶段 | 说明 |
|------|------|
| INIT | 检测 input/ 目录图片 |
| ANALYZE | 视觉分析图片内容 |
| CONFIRM_PRODUCT | 选择动态效果和视频比例 |
| GENERATE | 基于参考图生成图1，再生成图2 |
| CONFIRM_IMAGES | 展示结尾方案选项，确认首尾帧 |
| BUILD_VIDEO_PROMPT | 生成视频过渡提示词 |
| WAIT_VIDEO | 等待用户放入视频文件 |
| EXTRACT_FRAMES | ffmpeg 拆帧 |
| BUILD_PROJECT | 生成项目文件和展示网页 |
| DONE | 完成 |

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

将产品图片放入 `input/` 目录，支持 `.jpg`、`.jpeg`、`.png`、`.webp` 格式。

### 4. 启动工作流

在 Claude Code 中运行：
```
/vibecode-agent
```

## 使用方式

在 Claude Code 中通过命令与 Agent 交互：

```
/vibecode-agent
```

Agent 会引导你完成整个工作流，支持选项式交互。

## 批量处理 API

```python
from agent.batch import BatchWorkflow, BatchStatus

batch = BatchWorkflow("state/batch.json")

# 创建批次
items = batch.create(["img1.jpg", "img2.jpg", "img3.jpg"])

# 获取下一个待处理项
next_item = batch.get_next()

# 标记完成/跳过
batch.complete("img1.jpg")
batch.skip("img2.jpg")

# 查看进度
print(batch.progress())  # 0.0 ~ 1.0
print(batch.get_completed())  # 已处理数量
```

状态值：`PENDING` → `COMPLETED` / `SKIPPED`

## 缓存配置

```python
from agent.cache import ImageCache

cache = ImageCache(
    state_dir="state/cache",     # 元数据目录
    image_dir="generated/cache"  # 缓存图片目录
)

# 写入缓存（可选 TTL）
cache.set("prompt text", "output.png", reference_image="ref.jpg", ttl=3600)

# 查询缓存
meta = cache.get("prompt text")
if meta:
    print(meta["cached_at"])  # Unix 时间戳

# 清空缓存
cache.clear()
```

缓存基于 prompt + reference_image 的 MD5 哈希。设置 TTL（秒）可自动过期。

## 支持的图片格式

| 格式 | 扩展名 | 备注 |
|------|--------|------|
| JPEG | `.jpg`, `.jpeg` | 最常用 |
| PNG | `.png` | 支持透明 |
| WebP | `.webp` | 压缩率高 |
| GIF | `.gif` | 支持动图 |
| BMP | `.bmp` | 无压缩位图 |
| TIFF | `.tiff` | 印刷级 |

## 项目结构

```
vibecode-workflow/
├── agent/
│   ├── workflow.py           ← 状态管理
│   ├── image_generator.py    ← Seedream API 封装（支持 img2img）
│   ├── prompt_builder.py     ← 提示词生成（含结尾帧方案）
│   ├── frame_extractor.py    ← ffmpeg 拆帧
│   ├── web_builder.py        ← 英雄镜头网页生成
│   ├── cache.py              ← 图片缓存
│   ├── batch.py              ← 批量处理
│   ├── progress.py           ← 进度通知
│   ├── config.py             ← 配置管理
│   └── exceptions.py         ← 自定义异常
├── templates/
│   └── hero_shot.html        ← HTML 模板
├── tests/                    ← 测试文件（168 个测试）
├── .claude/skills/
│   ├── vibecode-agent.md     ← 工作流技能定义
│   └── hero-shot-builder.md  ← 网页构建技能
├── state/                    ← 运行时状态（自动生成）
├── generated/                ← 生成的图片、视频、帧（自动生成）
│   ├── image1.png            ← 首帧
│   ├── image2.png            ← 尾帧
│   └── frames/               ← 帧序列
├── projects/                 ← 生成的项目文件
│   └── {产品名}/
│       ├── index.html        ← 展示网页
│       ├── public/frames/    ← 帧图片
│       ├── PROMPT.md         ← 建站提示词
│       └── rules.json        ← 编码规范
├── input/                    ← 放产品图片
├── .env                      ← API 密钥配置
├── .env.example              ← 环境变量示例
├── pyproject.toml            ← 项目配置
└── requirements.txt          ← Python 依赖
```

## 用户命令

在工作流中可以随时使用：
- **重新开始** — 清空状态，从头开始
- **暂停** — 保存当前进度，下次继续
- **跳过视频** — 直接用输入图片作为帧

## Python 模块

### workflow.py — 状态管理

```python
from agent.workflow import Workflow

wf = Workflow()
wf.get_stage()           # 获取当前阶段
wf.set_stage("ANALYZE")  # 设置阶段
wf.get_data("product")   # 获取数据
wf.set_data("product", {"name": "产品"})  # 设置数据
wf.reset()               # 重置到初始状态
```

### image_generator.py — 图片生成

```python
from agent.image_generator import generate_image

# 文生图
path = generate_image("产品描述", "output.png")

# 图生图（参考图可以是 URL 或本地路径）
path = generate_image("保留特征的描述", "output.png", reference_image="input/photo.jpg")
```

### prompt_builder.py — 提示词生成

```python
from agent.prompt_builder import (
    build_regenerate_prompt,      # 生成图1的强约束重绘 Prompt
    build_img2img_prompt,         # 生成图2的微调 Prompt
    build_video_prompt,           # 生成视频过渡 Prompt
    generate_ending_options,      # 生成结尾方案选项
    build_ending_prompt,          # 生成结尾帧 Prompt
)

# 生成结尾方案
options = generate_ending_options({
    "subject": "动漫少女",
    "action": "做嘘的手势",
    "scene": "放射线背景",
    "mood": "安静、温柔"
})
# 返回 [{"type": "动作完成", "description": "...", "prompt": "..."}, ...]

# 生成结尾帧 Prompt
prompt = build_ending_prompt(
    "原始特征描述",
    "结尾方案描述"
)
```

### frame_extractor.py — 视频拆帧

```python
from agent.frame_extractor import extract_frames

count = extract_frames("video.mp4", "frames/", fps=24)  # 返回帧数
```

### web_builder.py — 英雄镜头网页

```python
from agent.web_builder import generate_player_html

html = generate_player_html(
    frame_count=123,
    fps=24,
    title="产品名称"
)
# 返回完整 HTML 字符串

with open("projects/产品名/index.html", "w", encoding="utf-8") as f:
    f.write(html)
```

## 结尾帧系统

图2 不再是简单的图1微调，而是有意义的结尾帧：

1. **AI 分析图1**：识别主体、动作、场景、情绪
2. **生成 2-3 个结尾方案**：
   - 动作完成（当前动作的自然结束）
   - 场景拉远（视角变化）
   - 情绪变化（表情/姿态转变）
3. **用户选择**：选择方案或自定义描述
4. **生成图2**：基于选择生成，保留所有原始特征

## 常见问题

**Q：ffmpeg 未找到？**
A：安装 ffmpeg 并确保在系统 PATH 中。

**Q：图片生成失败？**
A：检查 `.env` 中的 `ARK_API_KEY` 是否正确。

**Q：如何恢复中断的工作流？**
A：直接运行 `/vibecode-agent`，会自动从上次中断处继续。

**Q：图1 和图2 不一致？**
A：使用强约束 Prompt 保留所有视觉元素，如仍有问题可选择"全部重做"。

**Q：如何自定义展示网页？**
A：编辑 `projects/{产品名}/index.html`，修改 CSS 变量或文字内容。

## 许可证

MIT
