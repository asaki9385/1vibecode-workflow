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
- `state/workflow.json` 中的 `image_analysis`（用于生成文案）

## 输出

- `projects/{产品名}/index.html` — 完整展示网页
- `projects/{产品名}/PROMPT.md` — 建站提示词
- `projects/{产品名}/rules.json` — 编码规范

## 核心原则

**必须使用 frontend-design skill 的设计原则**，避免通用 AI 审美，创造独特、有记忆点的视觉体验。

## 设计流程

### Step 1: 分析素材

从 `state/workflow.json` 读取 `image_analysis`：

```python
import json
with open("state/workflow.json") as f:
    data = json.load(f)
analysis = data.get("image_analysis", {})
# analysis = {
#   "subject": "蓝紫色短发动漫少女",
#   "action": "手指轻触嘴唇的思考姿势",
#   "scene": "抽象红/青/黑泼墨背景",
#   "mood": "神秘、沉思、前卫"
# }
```

### Step 2: 确定设计方向

根据分析结果选择美学方向：

| 素材特征 | 推荐方向 | 字体 | 配色 |
|----------|----------|------|------|
| 动漫/二次元 | 赛博朋克/霓虹 | Clash Display + Satoshi | 深色 + 霓虹强调色 |
| 自然/风景 | 有机/极简 | Fraunces + DM Sans | 大地色系 |
| 人物/肖像 | 杂志/编辑 | Playfair Display + Inter | 黑白 + 单色强调 |
| 产品/物品 | 奢华/精致 | Cormorant + Outfit | 深色 + 金色 |
| 抽象/艺术 | 极简/画廊 | Space Mono + Manrope | 纯黑 + 白 |

### Step 3: 生成文案

基于分析结果生成占位文案：

```python
def generate_copy(analysis):
    subject = analysis.get("subject", "创作")
    mood = analysis.get("mood", "独特")
    
    title = f"Experience {mood}"
    subtitle = f"A visual journey through {subject}"
    description = "AI-crafted motion art that captures the essence of creativity"
    
    return {
        "tag": "AI-Generated Motion",
        "title": title,
        "subtitle": subtitle,
        "description": description,
        "cta_primary": "Watch Now",
        "cta_secondary": "Learn More"
    }
```

### Step 4: 构建网页

使用 frontend-design 原则构建：

## 设计规范

### 字体选择（必须独特，避免通用字体）

```css
/* ❌ 不要这样 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

/* ✅ 要这样 - 根据素材选择独特字体组合 */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
```

**字体组合推荐**：

| 场景 | 标题字体 | 正文字体 | 氛围 |
|------|----------|----------|------|
| 动漫/二次元 | Clash Display | Satoshi | 现代科技 |
| 自然/风景 | Fraunces | DM Sans | 有机温暖 |
| 人物/肖像 | Playfair Display | Noto Sans SC | 优雅编辑 |
| 产品/物品 | Cormorant Garamond | Outfit | 奢华精致 |
| 抽象/艺术 | Space Mono | Manrope | 极简画廊 |

### 配色系统

```css
:root {
  /* 基础色 */
  --white: #ffffff;
  --black: #000000;
  
  /* 玻璃效果 */
  --glass: rgba(255, 255, 255, 0.08);
  --glass-border: rgba(255, 255, 255, 0.12);
  
  /* 文字层次 */
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.6);
  --text-muted: rgba(255, 255, 255, 0.35);
  
  /* 强调色 - 根据素材主色调选择 */
  --accent: #7dd3a0;  /* 示例：柔和绿色 */
  --accent-glow: rgba(125, 211, 160, 0.3);
}
```

### 视觉效果层

```
z-index: 1000  → 加载动画
z-index: 100   → 导航栏、统计栏
z-index: 50    → 滚动提示
z-index: 10    → 内容层（标题、描述、按钮）
z-index: 2     → 噪点纹理
z-index: 1     → 渐变遮罩
z-index: 0     → Canvas 全屏背景
```

### 动画规范

```css
/* 入场动画 - 错落渐入 */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 使用方式 */
.hero-tag { animation: fadeUp 0.6s 0.8s ease forwards; }
.hero h1 { animation: fadeUp 0.8s 1s ease forwards; }
.hero p { animation: fadeUp 0.8s 1.2s ease forwards; }
.hero-actions { animation: fadeUp 0.8s 1.4s ease forwards; }

/* 间隔：0.2s */
```

### 布局结构

```html
<!-- 背景层 -->
<canvas id="bg"></canvas>
<div class="overlay"></div>
<div class="grain"></div>

<!-- 加载层 -->
<div class="loader" id="loader">...</div>

<!-- 内容层 -->
<div class="content">
  <header>
    <div class="logo">{项目名称}</div>
    <nav>...</nav>
  </header>
  
  <section class="hero">
    <div class="hero-tag">
      <span class="dot"></span>
      {标签文字}
    </div>
    <h1>{主标题}</h1>
    <p>{描述文字}</p>
    <div class="hero-actions">
      <button class="btn-primary">{主按钮}</button>
      <a class="btn-secondary">{次按钮}</a>
    </div>
  </section>
</div>

<!-- 统计栏 -->
<div class="stats">
  <div class="stat">帧数</div>
  <div class="stat">帧率</div>
  <div class="stat">时长</div>
  <div class="stat">AI</div>
</div>
```

### 磨砂玻璃效果

```css
header {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  background: rgba(0,0,0,0.4);
  border-bottom: 1px solid var(--glass-border);
}
```

### Canvas 全屏背景

```javascript
function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  if (frames[current] && frames[current].complete) draw(current);
}

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

## 使用方式

```python
from agent.web_builder import generate_player_html
import json

# 读取分析结果
with open("state/workflow.json") as f:
    data = json.load(f)
analysis = data.get("image_analysis", {})

# 生成网页
html = generate_player_html(
    frame_count=120,
    fps=24,
    title="项目名称",
    analysis=analysis  # 传递分析结果
)

with open("projects/{产品名}/index.html", "w", encoding="utf-8") as f:
    f.write(html)
```

## 关键注意事项

1. **必须使用独特字体**：避免 Inter、Roboto、Arial 等通用字体
2. **必须有视觉层次**：标题 > 副标题 > 描述 > 按钮
3. **必须有动画效果**：错落渐入、悬停反馈
4. **必须有质感**：噪点纹理、渐变遮罩
5. **必须响应式**：适配移动端
