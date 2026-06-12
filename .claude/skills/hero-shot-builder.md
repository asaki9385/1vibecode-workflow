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

从 `state/workflow.json` 读取 `image_analysis`（重点是 `style_profile`）：

```python
import json
with open("state/workflow.json") as f:
    data = json.load(f)
analysis = data.get("image_analysis", {})
style_profile = analysis.get("style_profile", {})
# style_profile = {
#   "keywords": ["cyberpunk", "high contrast"],
#   "visual_tone": "高对比、冷色调、霓虹光感、未来感",
#   "copy_tone": "前卫、简短、科技感词汇、英文为主",
#   "camera_style": "快速切换、动态运镜"
# }
```

### Step 2: 确定设计方向

根据 `image_analysis.style_profile.keywords` 选择美学方向（**必须直接复用 keywords，不要重新做风格判断**）：

| style_profile.keywords 首词 | font_heading       | font_body    | accent_color | 风格      |
| ------------------------- | ------------------ | ------------ | ------------ | ------- |
| cyberpunk / neon          | Clash Display      | Satoshi      | #ff00ff      | 赛博朋克/霓虹 |
| organic / earth           | Fraunces           | DM Sans      | #8b7355      | 有机/大地色系 |
| editorial / magazine      | Playfair Display   | Noto Sans SC | #7dd3a0      | 杂志/编辑   |
| luxury / premium          | Cormorant Garamond | Outfit       | #d4a853      | 奢华/金色   |
| minimalist / gallery      | Space Mono         | Manrope      | #ffffff      | 极简/画廊   |
| industrial / geometric    | Bebas Neue         | Inter        | #6b7280      | 工业/几何   |
| warm / natural            | Lora               | Noto Sans SC | #c2410c      | 温暖/自然   |

**多关键词叠加规则**：

- 取第一个关键词作为主方向
- 如果第二个关键词映射到不同方向，在主方向基础上微调 accent 色
  - 例：keywords=["cyberpunk", "luxury"] → 赛博朋克配色 + 金属色调 accent

**accent 色来源**：

- **首选**：`extracted_palette.accent_color`（从 image1 实际提取的真实色值）
- **备选**：`extracted_palette.top_accents`（多候选时展示给用户选择）
- **兜底**：方向表中的示例色值（仅在 extracted_palette 缺失时使用）
- 方向表决定配色的**整体框架和氛围**，`extracted_palette` 决定框架内的**具体色值**

**风格预设包 — 动画参数**（与字体/配色同源派生，复用 style_profile.keywords）：

| style_profile.keywords 首词 | GSAP ease    | duration | stagger | scale | rotation | 动效特征                 |
| ------------------------- | ------------ | -------- | ------- | ----- | -------- | -------------------- |
| cyberpunk / tech          | expo.out     | 0.5s     | 0.15s   | 0.95  | 0        | 快速冲击，带 scale(0.95→1) |
| minimalist / gallery      | power1.inOut | 1.2s     | 0.3s    | 1     | 0        | 缓慢从容，纯位移+透明度         |
| organic / natural         | sine.inOut   | 0.9s     | 0.25s   | 1     | 2        | 柔和曲线，轻微 rotation     |
| luxury / editorial        | power3.out   | 1.0s     | 0.3s    | 1     | 0        | 优雅错落，间隔加大            |
| 默认                        | power2.out   | 0.8s     | 0.2s    | 1     | 0        | 均衡过渡                 |

### Step 2.5: 选择风格包

根据 `image_analysis.style_profile.keywords` 第一个词选择风格包：

| 关键词 | 风格包 | 模板文件 | 动画文件 |
|--------|--------|----------|----------|
| editorial, magazine, luxury | `editorial` | `styles/editorial.html` | `animations/editorial.js` |
| cyberpunk, dark art, neon | `immersive` | `styles/immersive.html` | `animations/immersive.js` |
| minimalist, gallery, organic | `gallery` | `styles/gallery.html` | `animations/gallery.js` |
| warm, natural, earth | `warm` | `styles/warm.html` | `animations/warm.js` |
| 无匹配 | `gallery`（默认） | `styles/gallery.html` | `animations/gallery.js` |

**读取风格包参数**：
```python
import json
with open(".claude/skills/hero-shot-builder/params.json") as f:
    params_config = json.load(f)
```

**根据 image_analysis 自动决定参数值**：
```python
def decide_params(analysis):
    style = analysis.get("style_profile", {})
    keywords = style.get("keywords", [])
    mood = analysis.get("mood", "")

    params = {
        "deco_density": "normal",
        "anim_energy": "moderate",
        "layout_compact": False,
        "text_overlay": False,
        "parallax_depth": "subtle"
    }

    if "minimalist" in keywords:
        params["deco_density"] = "none"
        params["anim_energy"] = "calm"
    elif "cyberpunk" in keywords or "dark art" in keywords:
        params["deco_density"] = "sparse"
        params["anim_energy"] = "high"
        params["text_overlay"] = True

    if "温暖" in mood or "柔和" in mood:
        params["anim_energy"] = "calm"

    return params
```

**GSAP 加载失败处理**：如果 GSAP CDN 加载失败（`typeof gsap === 'undefined'`），页面自动使用 CSS `@keyframes fadeUp` 兜底动画。agent 在展示结果时必须告知用户："GSAP加载失败，已使用CSS动画兜底"。

 **GSAP 进阶参考**：如需自定义动画（时间线、ScrollTrigger、文本动画等），读取 `.claude/skills/gsap/SKILL.md` 获取完整 API 参考。

**调用方式**：

```python
import json

# 1. 读取风格包参数
with open(".claude/skills/hero-shot-builder/params.json") as f:
    params_config = json.load(f)

# 2. 根据 keywords 选择风格包
style_pack = "gallery"  # 默认
keywords = analysis["style_profile"]["keywords"]
for kw in keywords:
    if kw in ["editorial", "magazine", "luxury"]:
        style_pack = "editorial"
        break
    elif kw in ["cyberpunk", "dark art", "neon"]:
        style_pack = "immersive"
        break
    elif kw in ["minimalist", "gallery", "organic"]:
        style_pack = "gallery"
        break
    elif kw in ["warm", "natural", "earth"]:
        style_pack = "warm"
        break

# 3. 读取风格包模板
template_path = f".claude/skills/hero-shot-builder/styles/{style_pack}.html"
with open(template_path, encoding="utf-8") as f:
    template = f.read()

# 4. 替换模板变量
html = template.replace("$title", title)
html = html.replace("$hero_title", copy["title"])
html = html.replace("$subtitle", copy["subtitle"])
html = html.replace("$description", copy["description"])
html = html.replace("$tag", copy["tag"])
html = html.replace("$cta_primary", copy["cta_primary"])
html = html.replace("$cta_secondary", copy["cta_secondary"])
html = html.replace("$accent_color", accent_color)
html = html.replace("$accent_glow", accent_glow)
html = html.replace("$font_import", font_import)
html = html.replace("$font_heading", font_heading)
html = html.replace("$font_body", font_body)
html = html.replace("$frame_count", str(frame_count))
html = html.replace("$fps", str(fps))
html = html.replace("$duration", duration)
# ... 其他变量

# 5. 根据参数条件渲染装饰元素
deco_settings = params_config["deco_density_mappings"][params["deco_density"]]
if not deco_settings["radial_glow"]:
    html = html.replace('<div class="radial-glow breathing"></div>', '')
if not deco_settings["ghost_text"]:
    html = html.replace('<div class="ghost-text drifting">$ghost_text</div>', '')
```

### Step 3: 生成文案

**必须参考 `style_profile.copy_tone` 决定措辞风格**，确保文案调性与视觉调性一致：

```python
def generate_copy(analysis, page_purpose):
    subject = analysis.get("subject", "创作")
    style_profile = analysis.get("style_profile", {})
    copy_tone = style_profile.get("copy_tone", "")
    page_purpose = page_purpose or "作品展示"

    # 根据 copy_tone 选择措辞风格
    if "前卫" in copy_tone or "科技" in copy_tone:
        # 冷峻、简洁、科技感
        title = "Signal"
        description = "Beyond the boundary of perception"
    elif "温暖" in copy_tone or "自然" in copy_tone:
        # 柔和、感性、自然
        title = "静谧时光"
        description = "捕捉自然的温柔瞬间"
    elif "奢华" in copy_tone or "精致" in copy_tone:
        # 优雅、高端
        title = "L'Art du Détail"
        description = "Every pixel, perfected"
    else:
        # 默认
        title = f"Experience {subject}"
        description = f"A visual journey through {subject}"

    # 根据 page_purpose 微调
    if page_purpose == "产品宣传":
        description = f"Discover {subject} — {description}"
    elif page_purpose == "个人主页":
        title = "Portfolio"

    return {
        "tag": "AI-Generated Motion",
        "title": title,
        "subtitle": subject,
        "description": description,
        "cta_primary": "Watch Now",
        "cta_secondary": "Learn More"
    }
```

### Step 4: 获取 frontend-design 规范

在生成最终 HTML 之前，**必须先读取 frontend-design skill**，获取设计执行规范：

```
read .claude/skills/frontend-design/SKILL.md
```

从该 skill 中提取并记录以下约束，供 Step 5 使用：

- 排版比例系统（字号层级、行高、字间距）
- 间距/留白原则（呼吸感、负空间使用）
- 配色原则（明度对比、饱和度搭配、避免 AI 审美套路的技巧）
- 布局建议（非对称、网格系统、视觉层次）
- 动效原则（入场时机、微交互、避免过度动画）

### Step 5: 设计职责划分

**方向表**（style_profile.keywords）→ 回答"用什么字体/什么色调/什么风格关键词"
**frontend-design skill** → 回答"这套字体/色调如何被正确地执行成专业的视觉层次"

两者配合使用，不是二选一。

### Step 6: 构建网页

**读取风格包模板**：
```python
style_pack = "editorial"  # 从 Step 2.5 获取
template_path = f".claude/skills/hero-shot-builder/styles/{style_pack}.html"
with open(template_path, encoding="utf-8") as f:
    template = f.read()
```

**应用参数微调**：
```python
# 从 params.json 获取映射
deco_mappings = params_config["deco_density_mappings"]
deco_settings = deco_mappings[params["deco_density"]]

# 替换模板变量
html = template.replace("$title", title)
html = html.replace("$hero_title", copy["title"])
# ... 其他变量替换

# 根据参数条件渲染装饰元素
if not deco_settings["radial_glow"]:
    html = html.replace('<div class="radial-glow breathing"></div>', '')
if not deco_settings["ghost_text"]:
    html = html.replace('<div class="ghost-text drifting">$ghost_text</div>', '')
```

**Canvas 播放逻辑保持不变**：
- `<canvas id="bg">` 全屏背景播放
- 帧预加载、进度条
- requestAnimationFrame 播放循环
- 键盘控制（空格暂停/播放）

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
import json

# 读取分析结果
with open("state/workflow.json") as f:
    data = json.load(f)
analysis = data.get("image_analysis", {})
style_profile = analysis.get("style_profile", {})
extracted_palette = data.get("extracted_palette", {})

# 1. 根据 keywords 选择风格包
keywords = style_profile.get("keywords", [])
style_pack = "gallery"  # 默认
for kw in keywords:
    if kw in ["editorial", "magazine", "luxury"]:
        style_pack = "editorial"
        break
    elif kw in ["cyberpunk", "dark art", "neon"]:
        style_pack = "immersive"
        break
    elif kw in ["minimalist", "gallery", "organic"]:
        style_pack = "gallery"
        break
    elif kw in ["warm", "natural", "earth"]:
        style_pack = "warm"
        break

# 2. 读取风格包参数和模板
with open(".claude/skills/hero-shot-builder/params.json") as f:
    params_config = json.load(f)

template_path = f".claude/skills/hero-shot-builder/styles/{style_pack}.html"
with open(template_path, encoding="utf-8") as f:
    template = f.read()

# 3. 决定参数值
from agent.web_builder import decide_params
params = decide_params(analysis)

# 4. agent 生成的文案（基于 style_profile.copy_tone）
copy = {
    "tag": "AI Motion Art",
    "title": "Shatter",
    "subtitle": "碎裂之间",
    "description": "光在裂缝中呼吸",
    "cta_primary": "View Work",
    "cta_secondary": "About"
}

# 5. 替换模板变量
accent_color = extracted_palette.get("accent_color", "#ff4444")
accent_glow = extracted_palette.get("accent_glow", "rgba(255, 68, 68, 0.3)")

# 字体配置（根据风格包）
font_configs = {
    "editorial": {
        "heading": "Playfair Display",
        "body": "Noto Sans SC",
        "import": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Noto+Sans+SC:wght@300;400;500;700&display=swap"
    },
    "immersive": {
        "heading": "Inter",
        "body": "Inter",
        "import": "https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500&display=swap"
    },
    "gallery": {
        "heading": "Helvetica Neue",
        "body": "Inter",
        "import": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap"
    },
    "warm": {
        "heading": "Lora",
        "body": "Noto Sans SC",
        "import": "https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&family=Noto+Sans+SC:wght@300;400;500;700&display=swap"
    }
}
font_config = font_configs.get(style_pack, font_configs["gallery"])

html = template
html = html.replace("$title", "项目名称")
html = html.replace("$hero_title", copy["title"])
html = html.replace("$subtitle", copy["subtitle"])
html = html.replace("$description", copy["description"])
html = html.replace("$tag", copy["tag"])
html = html.replace("$cta_primary", copy["cta_primary"])
html = html.replace("$cta_secondary", copy["cta_secondary"])
html = html.replace("$accent_color", accent_color)
html = html.replace("$accent_glow", accent_glow)
html = html.replace("$font_import", font_config["import"])
html = html.replace("$font_heading", font_config["heading"])
html = html.replace("$font_body", font_config["body"])
html = html.replace("$frame_count", "121")
html = html.replace("$fps", "24")
html = html.replace("$duration", "5:01")
html = html.replace("$anim_ease", "power3.out")
html = html.replace("$anim_duration", "1.0")
html = html.replace("$anim_stagger", "0.3")
html = html.replace("$parallax_enabled", "true")
html = html.replace("$parallax_bg_speed", "0.3")
html = html.replace("$ghost_text", "SHATTER")
html = html.replace("$deco_number", "01")

# 6. 根据参数条件渲染装饰元素
deco_settings = params_config["deco_density_mappings"][params["deco_density"]]
if not deco_settings["radial_glow"]:
    html = html.replace('<div class="radial-glow breathing"></div>', '')
if not deco_settings["ghost_text"]:
    html = html.replace('<div class="ghost-text drifting">$ghost_text</div>', '')

# 7. 写入文件
with open("projects/{产品名}/index.html", "w", encoding="utf-8") as f:
    f.write(html)
```

## 关键注意事项

1. **必须使用风格包模板**：根据 `style_profile.keywords` 选择对应的风格包模板，不要使用旧的 `generate_player_html()` 函数
2. **风格包模板路径**：`.claude/skills/hero-shot-builder/styles/{style_pack}.html`
3. **参数文件路径**：`.claude/skills/hero-shot-builder/params.json`
4. **模板变量替换**：必须替换所有 `$` 开头的变量，包括字体、颜色、文案、动画参数等
5. **参数条件渲染**：根据 `deco_density` 参数决定是否渲染装饰元素（radial-glow、ghost-text 等）
6. **Canvas 播放逻辑**：模板已包含完整的 Canvas 播放逻辑，无需额外添加
7. **避免 AI 审美套路**：遵循 frontend-design skill 中关于避免通用字体、均匀间距等的具体指导
8. **一致性自检**：生成后检查文案/配色/排版是否与 style_profile 一致
