# Hero Shot Builder 重设计规格

## 概述

重设计 hero-shot-builder skill，使其能根据 `image_analysis.style_profile` 自适应生成精品网页。采用混合模式（方案 C）：4 个精心设计的风格包作为基底，每个风格包提供 5 个可调参数用于微调。

## 设计目标

1. **自适应风格**：根据图片内容自动选择最合适的视觉方向
2. **精品质量**：网页质量达到商业落地级，可选创意模式
3. **参数微调**：agent 可根据图片细节调整装饰密度、动画节奏等
4. **参考标准**：基于 hyperframes visual-styles.md 和 frontend-design skill

## 风格包体系

### 4 个核心风格包

| 风格包 | 对应 keywords | 视觉特征 | 参考 hyperframes 风格 |
|--------|---------------|----------|----------------------|
| `editorial` | editorial, magazine, luxury | 杂志排版、大留白、精致字体、优雅动画 | Velvet Standard |
| `immersive` | cyberpunk, dark art, neon | 全屏视觉冲击、文字叠加、霓虹发光、快速转场 | Data Drift / Shadow Cut |
| `gallery` | minimalist, gallery, organic | 克制、大量负空间、柔和过渡、呼吸感 | Swiss Pulse |
| `warm` | warm, natural, earth | 温暖色调、柔和曲线、自然质感、感性排版 | Soft Signal |

### 选择规则

- 取 `style_profile.keywords` 第一个词匹配风格包
- 无匹配时 fallback 到 `gallery`（最安全的默认）

## 自适应顶栏

### editorial（杂志风）
- 字体：body font，13px，字间距 0.5px
- 背景：纯透明 → 滚动后 `rgba(0,0,0,0.85)` 渐变
- 分隔线：1px `var(--accent)` 色，底部 1px
- 特点：精致、克制、信息层次清晰

### immersive（沉浸风）
- 字体：heading font，18px，字间距 2px
- 背景：完全透明，`backdrop-filter: blur(20px)` 仅在滚动后激活
- 无边框，与画面融为一体
- 特点：视觉优先，导航退居次要

### gallery（画廊风）
- 字体：mono font（如 Space Mono），11px，全大写
- 背景：纯黑，无透明效果
- 内容：编号 + 作品名 + 年份，像画廊标签
- 特点：信息密度高、专业感、档案感

### warm（温暖风）
- 字体：serif font（如 Lora），16px，italic
- 背景：`rgba(255,255,255,0.05)` 微透明
- 汉堡菜单图标，点击展开全屏导航
- 特点：柔和、人文感、呼吸感

### 滚动行为

- 所有顶栏在滚动 50px 后改变背景透明度（GSAP ScrollTrigger）
- 滚动到页面顶部时恢复初始状态
- 响应式：移动端隐藏复杂导航，显示汉堡菜单

## 艺术文字系统

### 字体配对原则（来自 house-style.md）

- 标题：700-900 字重，60px+
- 正文：300-400 字重，20px+
- 必须 serif + sans 混搭（不能两个 sans）

### 4 个风格包的排版系统

#### editorial（杂志风）
```yaml
typography:
  display:
    fontFamily: "Playfair Display"
    fontSize: "clamp(48px, 8vw, 120px)"
    fontWeight: 700
    fontStyle: italic
    letterSpacing: "-0.02em"
    lineHeight: 1.05
  heading:
    fontFamily: "Playfair Display"
    fontSize: "clamp(24px, 3vw, 40px)"
    fontWeight: 400
    letterSpacing: "0.02em"
  body:
    fontFamily: "Noto Sans SC"
    fontSize: "clamp(14px, 1.5vw, 18px)"
    fontWeight: 300
    lineHeight: 1.7
    letterSpacing: "0.01em"
  label:
    fontFamily: "Noto Sans SC"
    fontSize: "11px"
    fontWeight: 500
    textTransform: uppercase
    letterSpacing: "2px"
```

#### immersive（沉浸风）
```yaml
typography:
  display:
    fontFamily: "Inter"
    fontSize: "clamp(56px, 10vw, 160px)"
    fontWeight: 200
    letterSpacing: "0.05em"
    lineHeight: 1.0
  heading:
    fontFamily: "Inter"
    fontSize: "clamp(20px, 2.5vw, 32px)"
    fontWeight: 300
    letterSpacing: "0.08em"
    textTransform: uppercase
  body:
    fontFamily: "Inter"
    fontSize: "clamp(13px, 1.2vw, 16px)"
    fontWeight: 300
    lineHeight: 1.6
  label:
    fontFamily: "Space Mono"
    fontSize: "10px"
    fontWeight: 400
    letterSpacing: "3px"
    textTransform: uppercase
```

#### gallery（画廊风）
```yaml
typography:
  display:
    fontFamily: "Helvetica Neue"
    fontSize: "clamp(40px, 6vw, 96px)"
    fontWeight: 700
    letterSpacing: "-0.01em"
    lineHeight: 1.1
  heading:
    fontFamily: "Helvetica Neue"
    fontSize: "clamp(18px, 2vw, 28px)"
    fontWeight: 300
    letterSpacing: "0.15em"
    textTransform: uppercase
  body:
    fontFamily: "Inter"
    fontSize: "clamp(13px, 1.2vw, 15px)"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Space Mono"
    fontSize: "10px"
    fontWeight: 400
    letterSpacing: "2px"
    textTransform: uppercase
```

#### warm（温暖风）
```yaml
typography:
  display:
    fontFamily: "Lora"
    fontSize: "clamp(36px, 5vw, 72px)"
    fontWeight: 400
    fontStyle: italic
    letterSpacing: "0.01em"
    lineHeight: 1.15
  heading:
    fontFamily: "Lora"
    fontSize: "clamp(18px, 2vw, 28px)"
    fontWeight: 400
    letterSpacing: "0.02em"
  body:
    fontFamily: "Noto Sans SC"
    fontSize: "clamp(14px, 1.5vw, 17px)"
    fontWeight: 300
    lineHeight: 1.8
  label:
    fontFamily: "Noto Sans SC"
    fontSize: "11px"
    fontWeight: 400
    letterSpacing: "1px"
```

### 装饰性文字元素

| 风格包 | 装饰文字样式 | 位置 | 动画 |
|--------|-------------|------|------|
| editorial | 大号年份/编号，5% 透明度 | 背景右侧 | 缓慢向上漂移 |
| immersive | 代码片段/技术术语，3% 透明度 | 散布全屏 | 打字机效果循环 |
| gallery | 作品编号 "01"，8% 透明度 | 左上角 | 静止 |
| warm | 手写风格短语，4% 透明度 | 右下角 | 缓慢呼吸缩放 |

## 动画系统

### 入场动画序列

每个风格包有独立的入场 timeline：

#### editorial
- easing: `power3.out`
- header: opacity 0 → 1, y -20 → 0, 0.6s
- hero-tag: opacity 0 → 1, y 24 → 0, 1.0s, delay -0.3s
- h1: opacity 0 → 1, y 30 → 0, clipPath reveal, 1.2s, delay -0.6s
- p: opacity 0 → 1, y 20 → 0, 0.8s, delay -0.4s
- actions: opacity 0 → 1, y 16 → 0, 0.6s, delay -0.3s

#### immersive
- easing: `expo.out`
- header: opacity 0 → 1, 0.4s
- hero-tag: opacity 0 → 1, scale 0.95 → 1, 0.5s, delay -0.2s
- h1: opacity 0 → 1, y 40 → 0, scale 0.95 → 1, 0.6s, delay -0.3s
- p: opacity 0 → 1, y 20 → 0, 0.5s, delay -0.2s
- actions: opacity 0 → 1, y 16 → 0, 0.4s, delay -0.2s

#### gallery
- easing: `power1.inOut`
- header: opacity 0 → 1, 1.2s
- hero-tag: opacity 0 → 1, x -20 → 0, 1.0s, delay -0.6s
- h1: opacity 0 → 1, x -30 → 0, 1.2s, delay -0.8s
- p: opacity 0 → 1, 1.0s, delay -0.6s
- actions: opacity 0 → 1, 0.8s, delay -0.4s

#### warm
- easing: `sine.inOut`
- header: opacity 0 → 1, y -10 → 0, 1.0s
- hero-tag: opacity 0 → 1, y 16 → 0, 0.9s, delay -0.5s
- h1: opacity 0 → 1, y 20 → 0, 1.0s, delay -0.5s
- p: opacity 0 → 1, y 12 → 0, 0.8s, delay -0.4s
- actions: opacity 0 → 1, y 10 → 0, 0.7s, delay -0.3s

### 滚动驱动动画（ScrollTrigger）

所有区块内容随滚动出现：

```javascript
gsap.utils.toArray('.reveal').forEach(el => {
  gsap.from(el, {
    scrollTrigger: {
      trigger: el,
      start: "top 85%",
      end: "top 50%",
      toggleActions: "play none none reverse"
    },
    opacity: 0,
    y: 40,
    duration: 0.8,
    ease: "power2.out"
  });
});
```

### 视差效果（仅 editorial 和 immersive）

```javascript
gsap.to('.parallax-bg', {
  scrollTrigger: {
    trigger: '.hero',
    start: "top top",
    end: "bottom top",
    scrub: true
  },
  y: 100,
  ease: "none"
});
```

### 装饰元素动画

```javascript
// 呼吸缩放
gsap.to('.breathing', {
  scale: 1.02,
  duration: 3,
  repeat: -1,
  yoyo: true,
  ease: "sine.inOut"
});

// 缓慢漂移
gsap.to('.drifting', {
  y: "+=20",
  duration: 8,
  repeat: -1,
  yoyo: true,
  ease: "sine.inOut"
});

// 脉冲透明度
gsap.to('.pulsing', {
  opacity: 0.08,
  duration: 2,
  repeat: -1,
  yoyo: true,
  ease: "sine.inOut"
});
```

## 布局与区块系统

### 区块布局方案（根据 page_purpose 自适应）

| page_purpose | 区块组合 | 说明 |
|--------------|----------|------|
| `作品展示` | Hero + 作品信息 + 技术说明 | 精简版，突出视觉 |
| `产品宣传` | Hero + 特性亮点 + CTA + 页脚 | 完整营销版 |
| `个人主页` | Hero + 作品网格 + 关于 + 联系 | 作品集版 |

### 区块结构

#### Hero 区块（全屏，所有风格共有）
```html
<section class="hero" id="hero">
  <div class="deco-text">01</div>
  <div class="hero-content">
    <div class="hero-tag">
      <span class="dot"></span>
      {tag}
    </div>
    <h1 class="hero-title">{title}</h1>
    <p class="hero-subtitle">{subtitle}</p>
    <p class="hero-description">{description}</p>
    <div class="hero-actions">
      <button class="btn-primary">{cta_primary}</button>
      <a class="btn-secondary">{cta_secondary}</a>
    </div>
  </div>
  <div class="scroll-hint">
    <span>Scroll</span>
    <div class="scroll-line"></div>
  </div>
</section>
```

#### 作品信息区块
```html
<section class="detail" id="detail">
  <div class="detail-grid">
    <div class="detail-label">About</div>
    <div class="detail-content">
      <h2>{作品名称}</h2>
      <p>{详细描述}</p>
    </div>
    <div class="detail-meta">
      <div class="meta-item">
        <span class="meta-label">Style</span>
        <span class="meta-value">{风格}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Frames</span>
        <span class="meta-value">{帧数}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Duration</span>
        <span class="meta-value">{时长}</span>
      </div>
    </div>
  </div>
</section>
```

#### 技术说明区块
```html
<section class="tech" id="tech">
  <div class="tech-header">
    <span class="section-number">02</span>
    <h2>Process</h2>
  </div>
  <div class="tech-grid">
    <div class="tech-card">
      <div class="tech-icon">🎨</div>
      <h3>Analysis</h3>
      <p>{分析过程描述}</p>
    </div>
    <div class="tech-card">
      <div class="tech-icon">✨</div>
      <h3>Generation</h3>
      <p>{生成过程描述}</p>
    </div>
    <div class="tech-card">
      <div class="tech-icon">🎬</div>
      <h3>Motion</h3>
      <p>{动态效果描述}</p>
    </div>
  </div>
</section>
```

### 背景层设计

```html
<div class="bg-decorations">
  <div class="radial-glow"></div>
  <div class="ghost-text">{风格关键词}</div>
  <div class="accent-line"></div>
  <div class="grain-overlay"></div>
</div>
```

## 参数微调系统

### 5 个可调参数

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| `deco_density` | enum | `none / sparse / normal / dense` | `normal` | 装饰元素密度 |
| `anim_energy` | enum | `calm / moderate / high` | `moderate` | 动画节奏强度 |
| `layout_compact` | bool | `true / false` | `false` | 布局紧凑度 |
| `text_overlay` | bool | `true / false` | `false` | 文字是否叠加在画面上 |
| `parallax_depth` | enum | `none / subtle / deep` | `subtle` | 视差滚动深度 |

### 参数 → 视觉映射

#### deco_density
- `none`: 无装饰元素
- `sparse`: 仅 grain_overlay + radial_glow
- `normal`: deco_text + grain_overlay + radial_glow
- `dense`: 所有装饰元素 + ghost_text

#### anim_energy
- `calm`: duration 1.2s, easing sine.inOut, stagger 0.3s
- `moderate`: duration 0.8s, easing power2.out, stagger 0.2s
- `high`: duration 0.5s, easing expo.out, stagger 0.15s

#### layout_compact
- `true`: section_padding 60px, grid_gap 24px, hero_min_height 80vh
- `false`: section_padding 120px, grid_gap 48px, hero_min_height 100vh

#### text_overlay
- `true`: hero content absolute positioned, centered, overlay 0.4
- `false`: hero content relative positioned, left-aligned

#### parallax_depth
- `none`: parallax disabled
- `subtle`: bg_speed 0.3, content_speed 0.1
- `deep`: bg_speed 0.5, content_speed 0.2, deco_speed 0.4

### Agent 自动决策规则

| image_analysis 特征 | 推荐参数组合 |
|---------------------|-------------|
| 高对比度、暗色调 | `deco_density=sparse, anim_energy=high, text_overlay=true` |
| 柔和、自然、温暖 | `deco_density=normal, anim_energy=calm, text_overlay=false` |
| 极简、留白多 | `deco_density=none, anim_energy=calm, layout_compact=false` |
| 复杂、细节丰富 | `deco_density=dense, anim_energy=moderate, parallax_depth=deep` |

## 文件结构

```
.claude/skills/
├── hero-shot-builder.md          ← 更新：添加风格包选择逻辑
├── hero-shot-builder/
│   ├── styles/
│   │   ├── editorial.html        ← 新增：风格包 HTML 模板
│   │   ├── immersive.html
│   │   ├── gallery.html
│   │   └── warm.html
│   ├── animations/
│   │   ├── editorial.js          ← 新增：风格包动画预设
│   │   ├── immersive.js
│   │   ├── gallery.js
│   │   └── warm.js
│   └── params.json               ← 新增：参数定义
├── frontend-design.md            ← 已有
└── gsap.md                       ← 已有
```

## 与现有工作流的集成

```
vibecode-agent.md
  └── BUILD_PROJECT 阶段
        ├── Step 1: 生成文案（已有）
        ├── Step 2: 读取 frontend-design skill（已有）
        ├── Step 3: 确定设计方向（已有，需扩展）
        ├── Step 4: 读取 hero-shot-builder skill（已有）
        │           └── 新增：读取风格包参数定义
        │           └── 新增：根据 image_analysis 决定参数
        ├── Step 5: 生成网页（已有，需重写模板）
        │           └── 新增：应用风格包
        │           └── 新增：应用参数微调
        └── Step 6: 一致性自检（已有）
```

## 实现优先级

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P0 | 更新 hero-shot-builder.md | 添加风格包选择逻辑和参数系统 |
| P0 | 创建 4 个风格包 HTML 模板 | 基于现有模板重构 |
| P0 | 创建 4 个风格包 JS 动画 | 基于 GSAP 技能 |
| P1 | 创建 params.json | 参数定义文件 |
| P1 | 更新 vibecode-agent.md | BUILD_PROJECT 阶段调用新逻辑 |
| P2 | 测试 4 种风格 | 确保每种风格都能正确生成 |

## 关键约束

1. **必须保留**：Canvas 全屏背景播放逻辑、帧预加载、键盘控制
2. **必须重写**：HTML 结构、CSS 样式、GSAP 动画序列
3. **必须读取**：frontend-design skill（排版规范）、gsap skill（动画 API）
4. **必须自适应**：根据 image_analysis 自动选择风格包和参数

## 参考来源

- hyperframes visual-styles.md（8 种视觉风格定义）
- hyperframes house-style.md（设计规范和最佳实践）
- frontend-design skill（排版比例、间距原则、配色规范）
- gsap skill（GSAP API 参考和动画模式）
