---
name: hero-shot-builder
description: 将帧序列转化为英雄镜头风格全屏背景展示网页
---

# Hero Shot Builder

将帧序列（frame_0001.jpg ~ frame_XXXX.jpg）转化为全屏背景动画展示网页，配合精美的前端 UI。

## 触发条件

在 BUILD_PROJECT 阶段，帧图片已就绪时调用。

## 输入

- `projects/{产品名}/public/frames/` — 帧图片目录
- 页面标题（来自产品名或用户指定）

## 输出

- `projects/{产品名}/index.html` — 完整展示网页

## 网页结构

```
┌─────────────────────────────────────┐
│  Header (磨砂玻璃导航栏)              │
├─────────────────────────────────────┤
│                                     │
│   Hero Section                      │
│   ┌─────────────────────────────┐   │
│   │                             │   │
│   │   全屏背景 Canvas 动画       │   │
│   │   (帧序列 cover-fit 铺满)    │   │
│   │                             │   │
│   │   ┌─────────────────────┐   │   │
│   │   │ 叠加文字内容         │   │   │
│   │   │ 标题 + 描述 + 按钮   │   │   │
│   │   └─────────────────────┘   │   │
│   │                             │   │
│   └─────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│  Stats Bar (帧数/帧率/时长/AI标签)   │
└─────────────────────────────────────┘
```

## 技术要点

### 1. Canvas 全屏背景

```javascript
const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');

// Resize to fill viewport
function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  if (frames[current] && frames[current].complete) draw(current);
}

// Cover-fit: scale to fill, crop overflow
function draw(idx) {
  const img = frames[idx];
  const scale = Math.max(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);
  const w = img.naturalWidth * scale;
  const h = img.naturalHeight * scale;
  const x = (canvas.width - w) / 2;
  const y = (canvas.height - h) / 2;
  ctx.drawImage(img, x, y, w, h);
}
```

### 2. 关键注意事项

- **resize 后必须重绘**：`resize()` 会清空 canvas，需调用 `draw(current)` 恢复
- **图片加载检查**：`draw()` 中检查 `img.naturalWidth > 0` 防止未加载完成时报错
- **延迟播放**：等待至少 8-12 帧加载完成后再开始播放
- **帧路径**：`public/frames/frame_XXXX.jpg`（4位零填充）

### 3. 视觉设计规范

| 元素 | 规范 |
|------|------|
| 字体 | Google Fonts: Noto Sans SC + Playfair Display |
| 遮罩 | 上下渐变 + 径向渐变，确保文字可读 |
| 导航栏 | backdrop-filter: blur(12px) 磨砂玻璃 |
| 动画 | 错落渐入 (animation-delay 递增) |
| 纹理 | SVG noise 叠加增加质感 |
| 配色 | CSS 变量统一管理，支持主题切换 |

### 4. HTML 模板结构

```html
<!-- Background -->
<canvas id="bg"></canvas>
<div class="overlay"></div>
<div class="grain"></div>

<!-- Content -->
<div class="content">
  <header>...</header>
  <section class="hero">
    <div class="hero-tag">标签</div>
    <h1>标题</h1>
    <p>描述</p>
    <div class="hero-actions">按钮组</div>
  </section>
</div>

<!-- Stats -->
<div class="stats">统计信息</div>
```

## 使用方式

调用 `agent/web_builder.py`：

```python
from agent.web_builder import generate_player_html

html = generate_player_html(
    frame_count=123,
    fps=24,
    title="产品名称"
)

with open("projects/{产品名}/index.html", "w", encoding="utf-8") as f:
    f.write(html)
```

## 自定义扩展

如需修改设计风格，可直接编辑 `projects/{产品名}/index.html`：
- 修改 CSS 变量调整配色
- 修改 `.hero` 区域的文字内容
- 添加新的 section 扩展页面
