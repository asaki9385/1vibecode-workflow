# Hero Shot Builder Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign hero-shot-builder skill to generate premium, style-adaptive web pages with 4 visual style packs and 5 tuning parameters.

**Architecture:** Create 4 style pack directories (editorial/immersive/gallery/warm) each containing HTML template and JS animation files. Update hero-shot-builder.md with style selection logic and parameter system. Update vibecode-agent.md to integrate new workflow.

**Tech Stack:** HTML5, CSS3, GSAP (ScrollTrigger, Timeline), vanilla JavaScript

---

## File Structure

```
.claude/skills/
├── hero-shot-builder.md              ← Modify: add style pack selection logic
├── hero-shot-builder/
│   ├── styles/
│   │   ├── editorial.html            ← Create: editorial style template
│   │   ├── immersive.html            ← Create: immersive style template
│   │   ├── gallery.html              ← Create: gallery style template
│   │   └── warm.html                 ← Create: warm style template
│   ├── animations/
│   │   ├── editorial.js              ← Create: editorial animations
│   │   ├── immersive.js              ← Create: immersive animations
│   │   ├── gallery.js                ← Create: gallery animations
│   │   └── warm.js                   ← Create: warm animations
│   └── params.json                   ← Create: parameter definitions
├── frontend-design.md                ← Already exists
└── gsap.md                           ← Already exists
```

---

### Task 1: Create params.json parameter definition file

**Files:**
- Create: `.claude/skills/hero-shot-builder/params.json`

- [ ] **Step 1: Create params.json with all parameter definitions**

```json
{
  "parameters": {
    "deco_density": {
      "type": "enum",
      "values": ["none", "sparse", "normal", "dense"],
      "default": "normal",
      "description": "装饰元素密度"
    },
    "anim_energy": {
      "type": "enum",
      "values": ["calm", "moderate", "high"],
      "default": "moderate",
      "description": "动画节奏强度"
    },
    "layout_compact": {
      "type": "bool",
      "default": false,
      "description": "布局紧凑度"
    },
    "text_overlay": {
      "type": "bool",
      "default": false,
      "description": "文字是否叠加在画面上"
    },
    "parallax_depth": {
      "type": "enum",
      "values": ["none", "subtle", "deep"],
      "default": "subtle",
      "description": "视差滚动深度"
    }
  },
  "deco_density_mappings": {
    "none": {
      "deco_text": false,
      "grain_overlay": false,
      "radial_glow": false,
      "accent_lines": false,
      "ghost_text": false
    },
    "sparse": {
      "deco_text": false,
      "grain_overlay": true,
      "radial_glow": true,
      "accent_lines": false,
      "ghost_text": false
    },
    "normal": {
      "deco_text": true,
      "grain_overlay": true,
      "radial_glow": true,
      "accent_lines": false,
      "ghost_text": false
    },
    "dense": {
      "deco_text": true,
      "grain_overlay": true,
      "radial_glow": true,
      "accent_lines": true,
      "ghost_text": true
    }
  },
  "anim_energy_mappings": {
    "calm": {
      "entrance_duration": 1.2,
      "entrance_easing": "sine.inOut",
      "scroll_duration": 1.0,
      "stagger": 0.3
    },
    "moderate": {
      "entrance_duration": 0.8,
      "entrance_easing": "power2.out",
      "scroll_duration": 0.8,
      "stagger": 0.2
    },
    "high": {
      "entrance_duration": 0.5,
      "entrance_easing": "expo.out",
      "scroll_duration": 0.5,
      "stagger": 0.15
    }
  },
  "layout_mappings": {
    "compact_true": {
      "section_padding": "60px clamp(24px, 4vw, 60px)",
      "grid_gap": "24px",
      "hero_min_height": "80vh"
    },
    "compact_false": {
      "section_padding": "120px clamp(24px, 6vw, 80px)",
      "grid_gap": "48px",
      "hero_min_height": "100vh"
    }
  },
  "parallax_mappings": {
    "none": {
      "parallax_enabled": false
    },
    "subtle": {
      "parallax_enabled": true,
      "parallax_bg_speed": 0.3,
      "parallax_content_speed": 0.1
    },
    "deep": {
      "parallax_enabled": true,
      "parallax_bg_speed": 0.5,
      "parallax_content_speed": 0.2,
      "parallax_deco_speed": 0.4
    }
  }
}
```

- [ ] **Step 2: Verify file structure**

Run: `ls -la .claude/skills/hero-shot-builder/`
Expected: `params.json` exists

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/hero-shot-builder/params.json
git commit -m "feat: add parameter definition file for hero-shot-builder style packs"
```

---

### Task 2: Create editorial style pack HTML template

**Files:**
- Create: `.claude/skills/hero-shot-builder/styles/editorial.html`

- [ ] **Step 1: Create editorial.html with magazine-style layout**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<style>
  @import url('$font_import');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --white: #ffffff;
    --black: #000000;
    --glass: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.12);
    --text-primary: rgba(255, 255, 255, 0.95);
    --text-secondary: rgba(255, 255, 255, 0.6);
    --text-muted: rgba(255, 255, 255, 0.35);
    --accent: $accent_color;
    --accent-glow: $accent_glow;
  }

  body {
    background: var(--black);
    color: var(--white);
    font-family: '$font_body', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
    min-height: 100vh;
  }

  /* Full-screen background canvas */
  #bg {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
  }

  /* Dark overlay for text legibility */
  .overlay {
    position: fixed;
    inset: 0;
    z-index: 1;
    background:
      linear-gradient(180deg,
        rgba(0,0,0,0.3) 0%,
        rgba(0,0,0,0.1) 30%,
        rgba(0,0,0,0.1) 60%,
        rgba(0,0,0,0.6) 100%
      ),
      radial-gradient(ellipse at 30% 50%, rgba(0,0,0,0.4) 0%, transparent 70%);
    pointer-events: none;
  }

  /* Grain texture */
  .grain {
    position: fixed;
    inset: 0;
    z-index: 2;
    opacity: 0.04;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 128px;
  }

  /* Background decorations */
  .bg-decorations {
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
  }

  .radial-glow {
    position: absolute;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
    opacity: 0.15;
    filter: blur(80px);
    top: 20%;
    right: 10%;
  }

  .ghost-text {
    position: absolute;
    font-family: '$font_heading', serif;
    font-size: 20vw;
    font-weight: 900;
    opacity: 0.03;
    color: var(--text-primary);
    right: -5%;
    bottom: 10%;
    line-height: 1;
    user-select: none;
  }

  /* Main content layer */
  .content {
    position: relative;
    z-index: 10;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Header - Editorial style: thin line separator */
  header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 clamp(24px, 4vw, 48px);
    z-index: 100;
    background: transparent;
    transition: background 0.4s ease;
  }

  header.scrolled {
    background: rgba(0,0,0,0.85);
    border-bottom: 1px solid var(--accent);
  }

  .logo {
    font-family: '$font_heading', serif;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: var(--text-primary);
  }

  nav {
    display: flex;
    gap: 32px;
    align-items: center;
  }

  nav a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    transition: color 0.3s;
  }

  nav a:hover { color: var(--text-primary); }

  /* Hero section */
  .hero {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 120px clamp(24px, 6vw, 80px) 80px;
    max-width: 900px;
    position: relative;
  }

  .hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 100px;
    font-size: 12px;
    color: var(--accent);
    font-weight: 500;
    letter-spacing: 0.5px;
    width: fit-content;
    margin-bottom: 32px;
  }

  .hero-tag .dot {
    width: 6px;
    height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .hero h1 {
    font-family: '$font_heading', serif;
    font-size: clamp(48px, 8vw, 120px);
    font-weight: 700;
    font-style: italic;
    line-height: 1.05;
    letter-spacing: -0.02em;
    margin-bottom: 24px;
  }

  .hero-subtitle {
    font-family: '$font_heading', serif;
    font-size: clamp(24px, 3vw, 40px);
    font-weight: 400;
    letter-spacing: 0.02em;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }

  .hero p {
    font-size: clamp(14px, 1.5vw, 18px);
    line-height: 1.7;
    color: var(--text-secondary);
    max-width: 520px;
    margin-bottom: 48px;
  }

  .hero-actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 32px;
    background: var(--white);
    color: var(--black);
    border: none;
    border-radius: 100px;
    font-size: 14px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(255,255,255,0.2);
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 28px;
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--glass-border);
    border-radius: 100px;
    font-size: 14px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-secondary:hover {
    background: var(--glass);
    border-color: rgba(255,255,255,0.25);
  }

  /* Detail section */
  .detail {
    padding: 120px clamp(24px, 6vw, 80px);
    border-top: 1px solid var(--glass-border);
  }

  .detail-grid {
    display: grid;
    grid-template-columns: 200px 1fr 1fr;
    gap: 48px;
    max-width: 1200px;
  }

  .detail-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    padding-top: 8px;
  }

  .detail-content h2 {
    font-family: '$font_heading', serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 400;
    margin-bottom: 16px;
  }

  .detail-content p {
    font-size: 16px;
    line-height: 1.7;
    color: var(--text-secondary);
  }

  .detail-meta {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .meta-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }

  .meta-value {
    font-family: '$font_heading', serif;
    font-size: 18px;
    color: var(--text-primary);
  }

  /* Tech section */
  .tech {
    padding: 120px clamp(24px, 6vw, 80px);
    border-top: 1px solid var(--glass-border);
  }

  .tech-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 64px;
  }

  .section-number {
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: var(--accent);
    letter-spacing: 2px;
  }

  .tech-header h2 {
    font-family: '$font_heading', serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 400;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 48px;
  }

  .tech-card {
    padding: 32px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
  }

  .tech-icon {
    font-size: 32px;
    margin-bottom: 16px;
  }

  .tech-card h3 {
    font-family: '$font_heading', serif;
    font-size: 20px;
    font-weight: 400;
    margin-bottom: 12px;
  }

  .tech-card p {
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-secondary);
  }

  /* Stats bar */
  .stats {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    display: flex;
    justify-content: center;
    gap: 1px;
    background: var(--glass-border);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-top: 1px solid var(--glass-border);
  }

  .stat {
    flex: 1;
    max-width: 200px;
    padding: 20px 24px;
    text-align: center;
    background: rgba(0,0,0,0.5);
  }

  .stat-value {
    font-family: '$font_heading', serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }

  /* Scroll indicator */
  .scroll-hint {
    position: fixed;
    bottom: 100px;
    right: 40px;
    z-index: 50;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .scroll-hint span {
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    writing-mode: vertical-rl;
  }

  .scroll-line {
    width: 1px;
    height: 40px;
    background: linear-gradient(to bottom, var(--text-muted), transparent);
    animation: scrollPulse 2s infinite;
  }

  @keyframes scrollPulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.8; }
  }

  /* Loading overlay */
  .loader {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: var(--black);
    z-index: 1000;
    transition: opacity 0.6s, visibility 0.6s;
  }

  .loader.done {
    opacity: 0;
    visibility: hidden;
  }

  .loader-ring {
    width: 48px;
    height: 48px;
    border: 2px solid var(--glass-border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .loader-text {
    margin-top: 20px;
    font-family: '$font_heading', serif;
    font-size: 14px;
    color: var(--text-secondary);
    letter-spacing: 2px;
  }

  .loader-bar {
    margin-top: 16px;
    width: 120px;
    height: 2px;
    background: var(--glass-border);
    border-radius: 1px;
    overflow: hidden;
  }

  .loader-fill {
    height: 100%;
    background: var(--accent);
    width: 0%;
    transition: width 0.3s;
  }

  /* Reveal animations */
  .reveal {
    opacity: 0;
    transform: translateY(40px);
  }

  /* Responsive */
  @media (max-width: 768px) {
    nav { display: none; }
    .hero { padding: 140px 24px 120px; }
    .hero-actions { flex-direction: column; align-items: flex-start; }
    .scroll-hint { display: none; }
    .stats { flex-wrap: wrap; }
    .stat { min-width: 50%; }
    .detail-grid { grid-template-columns: 1fr; }
    .tech-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<!-- Background animation -->
<canvas id="bg"></canvas>
<div class="overlay"></div>
<div class="grain"></div>

<!-- Background decorations -->
<div class="bg-decorations">
  <div class="radial-glow breathing"></div>
  <div class="ghost-text drifting">$ghost_text</div>
</div>

<!-- Loading -->
<div class="loader" id="loader">
  <div class="loader-ring"></div>
  <div class="loader-text">Loading</div>
  <div class="loader-bar"><div class="loader-fill" id="loadFill"></div></div>
</div>

<!-- Content -->
<div class="content">
  <header id="header">
    <div class="logo">$title</div>
    <nav>
      <a href="#detail">About</a>
      <a href="#tech">Process</a>
      <a href="#contact" class="nav-cta">$cta_secondary</a>
    </nav>
  </header>

  <section class="hero" id="hero">
    <div class="hero-tag">
      <span class="dot"></span>
      $tag
    </div>
    <h1>$hero_title</h1>
    <div class="hero-subtitle">$subtitle</div>
    <p>$description</p>
    <div class="hero-actions">
      <button class="btn-primary" onclick="toggle()">
        $cta_primary
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
      <a href="#detail" class="btn-secondary">$cta_secondary</a>
    </div>
  </section>

  <section class="detail reveal" id="detail">
    <div class="detail-grid">
      <div class="detail-label">About</div>
      <div class="detail-content">
        <h2>$hero_title</h2>
        <p>$description</p>
      </div>
      <div class="detail-meta">
        <div class="meta-item">
          <span class="meta-label">Frames</span>
          <span class="meta-value">$frame_count</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Frame Rate</span>
          <span class="meta-value">${fps}fps</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Duration</span>
          <span class="meta-value">${duration}s</span>
        </div>
      </div>
    </div>
  </section>

  <section class="tech reveal" id="tech">
    <div class="tech-header">
      <span class="section-number">02</span>
      <h2>Process</h2>
    </div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-icon">🎨</div>
        <h3>Analysis</h3>
        <p>Visual analysis of reference image to extract style, mood, and key features.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">✨</div>
        <h3>Generation</h3>
        <p>AI-powered image generation with style preservation and effect application.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🎬</div>
        <h3>Motion</h3>
        <p>Frame extraction and animation to create seamless motion sequences.</p>
      </div>
    </div>
  </section>
</div>

<!-- Stats -->
<div class="stats">
  <div class="stat">
    <div class="stat-value">$frame_count</div>
    <div class="stat-label">Frames</div>
  </div>
  <div class="stat">
    <div class="stat-value">${fps}fps</div>
    <div class="stat-label">Frame Rate</div>
  </div>
  <div class="stat">
    <div class="stat-value">${duration}s</div>
    <div class="stat-label">Duration</div>
  </div>
  <div class="stat">
    <div class="stat-value">AI</div>
    <div class="stat-label">Generated</div>
  </div>
</div>

<!-- Scroll hint -->
<div class="scroll-hint">
  <span>Scroll</span>
  <div class="scroll-line"></div>
</div>

<!-- GSAP CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>

<script>
const TOTAL = $frame_count;
const FPS = $fps;
const ANIM_EASE = "$anim_ease";
const ANIM_DURATION = "$anim_duration";
const ANIM_STAGGER = "$anim_stagger";
const PARALLAX_ENABLED = $parallax_enabled;
const PARALLAX_BG_SPEED = $parallax_bg_speed;

const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');
const loader = document.getElementById('loader');
const loadFill = document.getElementById('loadFill');
const header = document.getElementById('header');

let frames = [];
let current = 0;
let playing = false;
let lastTime = 0;
let loaded = 0;
let ready = false;

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  if (frames[current] && frames[current].complete) draw(current);
}

function draw(idx) {
  if (!frames[idx] || !frames[idx].complete || !frames[idx].naturalWidth) return;
  const img = frames[idx];
  const scale = Math.max(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);
  const w = img.naturalWidth * scale;
  const h = img.naturalHeight * scale;
  const x = (canvas.width - w) / 2;
  const y = (canvas.height - h) / 2;
  ctx.drawImage(img, x, y, w, h);
}

function loop(time) {
  if (!playing) return;
  if (time - lastTime >= 1000 / FPS) {
    current = (current + 1) % TOTAL;
    draw(current);
    lastTime = time;
  }
  requestAnimationFrame(loop);
}

function toggle() {
  if (!ready) return;
  playing = !playing;
  if (playing) {
    requestAnimationFrame(loop);
  }
}

function start() {
  if (ready) return;
  ready = true;
  playing = true;
  loader.classList.add('done');
  draw(0);
  requestAnimationFrame(loop);

  // Editorial entrance timeline
  const tl = gsap.timeline();
  tl.from("header", { opacity: 0, y: -20, duration: 0.6, ease: ANIM_EASE })
    .from(".hero-tag", { opacity: 0, y: 24, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.3")
    .from(".hero h1", { opacity: 0, y: 30, clipPath: "inset(0 0 100% 0)", duration: parseFloat(ANIM_DURATION) * 1.2, ease: ANIM_EASE }, "-=0.6")
    .from(".hero-subtitle", { opacity: 0, y: 20, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.4")
    .from(".hero p", { opacity: 0, y: 20, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.4")
    .from(".hero-actions", { opacity: 0, y: 16, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.3")
    .from(".stats", { opacity: 0, y: 20, duration: 0.5, ease: "power2.out" }, "-=0.2")
    .from(".scroll-hint", { opacity: 0, duration: 0.5, ease: "power2.out" }, "-=0.3");

  // Scroll-triggered reveals
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
      duration: parseFloat(ANIM_DURATION),
      ease: "power2.out"
    });
  });

  // Header scroll effect
  ScrollTrigger.create({
    start: "top -50",
    end: 99999,
    toggleClass: { className: "scrolled", targets: header }
  });

  // Parallax (if enabled)
  if (PARALLAX_ENABLED) {
    gsap.to('.parallax-bg', {
      scrollTrigger: {
        trigger: '.hero',
        start: "top top",
        end: "bottom top",
        scrub: true
      },
      y: 100 * PARALLAX_BG_SPEED,
      ease: "none"
    });
  }
}

// GSAP load failure detection
if (typeof gsap === 'undefined') {
  console.warn('GSAP CDN failed to load, falling back to CSS animations');
  document.querySelectorAll('.hero-tag, .hero h1, .hero-subtitle, .hero p, .hero-actions, .stats, .scroll-hint, header').forEach(el => {
    el.style.opacity = '1';
    el.style.transform = 'none';
  });
  document.body.setAttribute('data-gsap-failed', 'true');
}

resize();
window.addEventListener('resize', resize);

for (let i = 1; i <= TOTAL; i++) {
  const img = new Image();
  img.onload = () => {
    loaded++;
    loadFill.style.width = (loaded / TOTAL * 100) + '%';
    if (loaded === 1) {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      draw(0);
    }
    if (loaded >= Math.min(12, TOTAL)) start();
  };
  img.src = `public/frames/frame_${String(i).padStart(4, '0')}.jpg`;
  frames.push(img);
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    e.preventDefault();
    toggle();
  }
});
</script>
</body>
</html>
```

- [ ] **Step 2: Verify file exists**

Run: `ls -la .claude/skills/hero-shot-builder/styles/`
Expected: `editorial.html` exists

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/hero-shot-builder/styles/editorial.html
git commit -m "feat: add editorial style pack HTML template"
```

---

### Task 3: Create immersive style pack HTML template

**Files:**
- Create: `.claude/skills/hero-shot-builder/styles/immersive.html`

- [ ] **Step 1: Create immersive.html with futuristic layout**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<style>
  @import url('$font_import');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --white: #ffffff;
    --black: #000000;
    --glass: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.08);
    --text-primary: rgba(255, 255, 255, 0.95);
    --text-secondary: rgba(255, 255, 255, 0.5);
    --text-muted: rgba(255, 255, 255, 0.25);
    --accent: $accent_color;
    --accent-glow: $accent_glow;
  }

  body {
    background: var(--black);
    color: var(--white);
    font-family: '$font_body', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
    min-height: 100vh;
  }

  #bg {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
  }

  .overlay {
    position: fixed;
    inset: 0;
    z-index: 1;
    background:
      linear-gradient(180deg,
        rgba(0,0,0,0.2) 0%,
        rgba(0,0,0,0.05) 40%,
        rgba(0,0,0,0.05) 60%,
        rgba(0,0,0,0.7) 100%
      );
    pointer-events: none;
  }

  .grain {
    position: fixed;
    inset: 0;
    z-index: 2;
    opacity: 0.03;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 128px;
  }

  .bg-decorations {
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
  }

  .radial-glow {
    position: absolute;
    width: 800px;
    height: 800px;
    border-radius: 50%;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 60%);
    opacity: 0.12;
    filter: blur(100px);
    top: 30%;
    left: 50%;
    transform: translateX(-50%);
  }

  .ghost-text {
    position: absolute;
    font-family: '$font_label', monospace;
    font-size: 8vw;
    font-weight: 400;
    opacity: 0.02;
    color: var(--text-primary);
    left: 10%;
    top: 20%;
    letter-spacing: 0.1em;
    user-select: none;
  }

  .content {
    position: relative;
    z-index: 10;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Header - Immersive: transparent, centered logo */
  header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    background: transparent;
    transition: backdrop-filter 0.4s ease, background 0.4s ease;
  }

  header.scrolled {
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    background: rgba(0,0,0,0.3);
  }

  .logo {
    font-family: '$font_heading', sans-serif;
    font-size: 18px;
    font-weight: 200;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-primary);
  }

  .hero {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 120px 24px 80px;
    position: relative;
  }

  .hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: transparent;
    border: 1px solid var(--accent);
    border-radius: 100px;
    font-family: '$font_label', monospace;
    font-size: 10px;
    color: var(--accent);
    font-weight: 400;
    letter-spacing: 3px;
    text-transform: uppercase;
    width: fit-content;
    margin-bottom: 40px;
  }

  .hero-tag .dot {
    width: 5px;
    height: 5px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  .hero h1 {
    font-family: '$font_heading', sans-serif;
    font-size: clamp(56px, 10vw, 160px);
    font-weight: 200;
    line-height: 1.0;
    letter-spacing: 0.05em;
    margin-bottom: 24px;
  }

  .hero-subtitle {
    font-family: '$font_heading', sans-serif;
    font-size: clamp(20px, 2.5vw, 32px);
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 20px;
  }

  .hero p {
    font-size: clamp(13px, 1.2vw, 16px);
    line-height: 1.6;
    color: var(--text-secondary);
    max-width: 480px;
    margin-bottom: 48px;
  }

  .hero-actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 16px 36px;
    background: var(--accent);
    color: var(--black);
    border: none;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 500;
    font-family: '$font_label', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 40px var(--accent-glow);
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 16px 32px;
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--glass-border);
    border-radius: 100px;
    font-size: 13px;
    font-weight: 400;
    font-family: '$font_label', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-secondary:hover {
    background: var(--glass);
    border-color: var(--accent);
  }

  /* Detail section - Immersive */
  .detail {
    padding: 120px clamp(24px, 6vw, 80px);
    background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.5) 100%);
  }

  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 80px;
    max-width: 1000px;
    margin: 0 auto;
  }

  .detail-label {
    font-family: '$font_label', monospace;
    font-size: 10px;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 24px;
  }

  .detail-content h2 {
    font-family: '$font_heading', sans-serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 200;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
  }

  .detail-content p {
    font-size: 15px;
    line-height: 1.7;
    color: var(--text-secondary);
  }

  .detail-meta {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    align-content: start;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .meta-label {
    font-family: '$font_label', monospace;
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .meta-value {
    font-family: '$font_heading', sans-serif;
    font-size: 24px;
    font-weight: 200;
    color: var(--text-primary);
  }

  /* Tech section - Immersive */
  .tech {
    padding: 120px clamp(24px, 6vw, 80px);
  }

  .tech-header {
    text-align: center;
    margin-bottom: 80px;
  }

  .section-number {
    font-family: '$font_label', monospace;
    font-size: 10px;
    color: var(--accent);
    letter-spacing: 3px;
    display: block;
    margin-bottom: 16px;
  }

  .tech-header h2 {
    font-family: '$font_heading', sans-serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 200;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .tech-card {
    padding: 40px 32px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 4px;
    text-align: center;
    transition: border-color 0.3s;
  }

  .tech-card:hover {
    border-color: var(--accent);
  }

  .tech-icon {
    font-size: 28px;
    margin-bottom: 20px;
  }

  .tech-card h3 {
    font-family: '$font_label', monospace;
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }

  .tech-card p {
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-secondary);
  }

  .stats {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    display: flex;
    justify-content: center;
    gap: 1px;
    background: var(--glass-border);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-top: 1px solid var(--glass-border);
  }

  .stat {
    flex: 1;
    max-width: 200px;
    padding: 20px 24px;
    text-align: center;
    background: rgba(0,0,0,0.5);
  }

  .stat-value {
    font-family: '$font_heading', sans-serif;
    font-size: 24px;
    font-weight: 200;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .stat-label {
    font-family: '$font_label', monospace;
    font-size: 9px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .scroll-hint {
    position: fixed;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 50;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .scroll-hint span {
    font-family: '$font_label', monospace;
    font-size: 9px;
    color: var(--text-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
  }

  .scroll-line {
    width: 1px;
    height: 40px;
    background: linear-gradient(to bottom, var(--accent), transparent);
    animation: scrollPulse 2s infinite;
  }

  @keyframes scrollPulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.8; }
  }

  .loader {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: var(--black);
    z-index: 1000;
    transition: opacity 0.6s, visibility 0.6s;
  }

  .loader.done {
    opacity: 0;
    visibility: hidden;
  }

  .loader-ring {
    width: 48px;
    height: 48px;
    border: 1px solid var(--glass-border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .loader-text {
    margin-top: 20px;
    font-family: '$font_label', monospace;
    font-size: 10px;
    color: var(--text-secondary);
    letter-spacing: 3px;
    text-transform: uppercase;
  }

  .loader-bar {
    margin-top: 16px;
    width: 120px;
    height: 1px;
    background: var(--glass-border);
    overflow: hidden;
  }

  .loader-fill {
    height: 100%;
    background: var(--accent);
    width: 0%;
    transition: width 0.3s;
  }

  .reveal {
    opacity: 0;
    transform: translateY(40px);
  }

  @media (max-width: 768px) {
    .hero { padding: 140px 24px 120px; }
    .hero-actions { flex-direction: column; }
    .scroll-hint { display: none; }
    .stats { flex-wrap: wrap; }
    .stat { min-width: 50%; }
    .detail-grid { grid-template-columns: 1fr; gap: 48px; }
    .tech-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<canvas id="bg"></canvas>
<div class="overlay"></div>
<div class="grain"></div>

<div class="bg-decorations">
  <div class="radial-glow breathing"></div>
  <div class="ghost-text">$ghost_text</div>
</div>

<div class="loader" id="loader">
  <div class="loader-ring"></div>
  <div class="loader-text">Loading</div>
  <div class="loader-bar"><div class="loader-fill" id="loadFill"></div></div>
</div>

<div class="content">
  <header id="header">
    <div class="logo">$title</div>
  </header>

  <section class="hero" id="hero">
    <div class="hero-tag">
      <span class="dot"></span>
      $tag
    </div>
    <h1>$hero_title</h1>
    <div class="hero-subtitle">$subtitle</div>
    <p>$description</p>
    <div class="hero-actions">
      <button class="btn-primary" onclick="toggle()">
        $cta_primary
      </button>
      <a href="#detail" class="btn-secondary">$cta_secondary</a>
    </div>
  </section>

  <section class="detail reveal" id="detail">
    <div class="detail-grid">
      <div>
        <div class="detail-label">About</div>
        <div class="detail-content">
          <h2>$hero_title</h2>
          <p>$description</p>
        </div>
      </div>
      <div class="detail-meta">
        <div class="meta-item">
          <span class="meta-label">Frames</span>
          <span class="meta-value">$frame_count</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Frame Rate</span>
          <span class="meta-value">${fps}fps</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Duration</span>
          <span class="meta-value">${duration}s</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Generated</span>
          <span class="meta-value">AI</span>
        </div>
      </div>
    </div>
  </section>

  <section class="tech reveal" id="tech">
    <div class="tech-header">
      <span class="section-number">02</span>
      <h2>Process</h2>
    </div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-icon">🎨</div>
        <h3>Analysis</h3>
        <p>Visual analysis of reference image to extract style, mood, and key features.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">✨</div>
        <h3>Generation</h3>
        <p>AI-powered image generation with style preservation and effect application.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🎬</div>
        <h3>Motion</h3>
        <p>Frame extraction and animation to create seamless motion sequences.</p>
      </div>
    </div>
  </section>
</div>

<div class="stats">
  <div class="stat">
    <div class="stat-value">$frame_count</div>
    <div class="stat-label">Frames</div>
  </div>
  <div class="stat">
    <div class="stat-value">${fps}fps</div>
    <div class="stat-label">Frame Rate</div>
  </div>
  <div class="stat">
    <div class="stat-value">${duration}s</div>
    <div class="stat-label">Duration</div>
  </div>
  <div class="stat">
    <div class="stat-value">AI</div>
    <div class="stat-label">Generated</div>
  </div>
</div>

<div class="scroll-hint">
  <span>Scroll</span>
  <div class="scroll-line"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>

<script>
const TOTAL = $frame_count;
const FPS = $fps;
const ANIM_EASE = "$anim_ease";
const ANIM_DURATION = "$anim_duration";
const ANIM_STAGGER = "$anim_stagger";
const PARALLAX_ENABLED = $parallax_enabled;
const PARALLAX_BG_SPEED = $parallax_bg_speed;

const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');
const loader = document.getElementById('loader');
const loadFill = document.getElementById('loadFill');
const header = document.getElementById('header');

let frames = [];
let current = 0;
let playing = false;
let lastTime = 0;
let loaded = 0;
let ready = false;

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  if (frames[current] && frames[current].complete) draw(current);
}

function draw(idx) {
  if (!frames[idx] || !frames[idx].complete || !frames[idx].naturalWidth) return;
  const img = frames[idx];
  const scale = Math.max(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);
  const w = img.naturalWidth * scale;
  const h = img.naturalHeight * scale;
  const x = (canvas.width - w) / 2;
  const y = (canvas.height - h) / 2;
  ctx.drawImage(img, x, y, w, h);
}

function loop(time) {
  if (!playing) return;
  if (time - lastTime >= 1000 / FPS) {
    current = (current + 1) % TOTAL;
    draw(current);
    lastTime = time;
  }
  requestAnimationFrame(loop);
}

function toggle() {
  if (!ready) return;
  playing = !playing;
  if (playing) {
    requestAnimationFrame(loop);
  }
}

function start() {
  if (ready) return;
  ready = true;
  playing = true;
  loader.classList.add('done');
  draw(0);
  requestAnimationFrame(loop);

  // Immersive entrance timeline
  const tl = gsap.timeline();
  tl.from("header", { opacity: 0, duration: 0.4, ease: ANIM_EASE })
    .from(".hero-tag", { opacity: 0, scale: 0.95, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.2")
    .from(".hero h1", { opacity: 0, y: 40, scale: 0.95, duration: parseFloat(ANIM_DURATION) * 1.2, ease: ANIM_EASE }, "-=0.3")
    .from(".hero-subtitle", { opacity: 0, y: 20, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.2")
    .from(".hero p", { opacity: 0, y: 20, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.2")
    .from(".hero-actions", { opacity: 0, y: 16, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.2")
    .from(".stats", { opacity: 0, y: 20, duration: 0.5, ease: "power2.out" }, "-=0.2");

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
      duration: parseFloat(ANIM_DURATION),
      ease: "power2.out"
    });
  });

  ScrollTrigger.create({
    start: "top -50",
    end: 99999,
    toggleClass: { className: "scrolled", targets: header }
  });

  if (PARALLAX_ENABLED) {
    gsap.to('.parallax-bg', {
      scrollTrigger: {
        trigger: '.hero',
        start: "top top",
        end: "bottom top",
        scrub: true
      },
      y: 100 * PARALLAX_BG_SPEED,
      ease: "none"
    });
  }
}

if (typeof gsap === 'undefined') {
  console.warn('GSAP CDN failed to load, falling back to CSS animations');
  document.body.setAttribute('data-gsap-failed', 'true');
}

resize();
window.addEventListener('resize', resize);

for (let i = 1; i <= TOTAL; i++) {
  const img = new Image();
  img.onload = () => {
    loaded++;
    loadFill.style.width = (loaded / TOTAL * 100) + '%';
    if (loaded === 1) {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      draw(0);
    }
    if (loaded >= Math.min(12, TOTAL)) start();
  };
  img.src = `public/frames/frame_${String(i).padStart(4, '0')}.jpg`;
  frames.push(img);
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    e.preventDefault();
    toggle();
  }
});
</script>
</body>
</html>
```

- [ ] **Step 2: Verify file exists**

Run: `ls -la .claude/skills/hero-shot-builder/styles/`
Expected: `immersive.html` exists

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/hero-shot-builder/styles/immersive.html
git commit -m "feat: add immersive style pack HTML template"
```

---

### Task 4: Create gallery style pack HTML template

**Files:**
- Create: `.claude/skills/hero-shot-builder/styles/gallery.html`

- [ ] **Step 1: Create gallery.html with minimalist layout**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<style>
  @import url('$font_import');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --white: #ffffff;
    --black: #000000;
    --glass: rgba(255, 255, 255, 0.04);
    --glass-border: rgba(255, 255, 255, 0.08);
    --text-primary: rgba(255, 255, 255, 0.95);
    --text-secondary: rgba(255, 255, 255, 0.5);
    --text-muted: rgba(255, 255, 255, 0.25);
    --accent: $accent_color;
    --accent-glow: $accent_glow;
  }

  body {
    background: var(--black);
    color: var(--white);
    font-family: '$font_body', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
    min-height: 100vh;
  }

  #bg {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
  }

  .overlay {
    position: fixed;
    inset: 0;
    z-index: 1;
    background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.4) 100%);
    pointer-events: none;
  }

  .grain {
    position: fixed;
    inset: 0;
    z-index: 2;
    opacity: 0.03;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 128px;
  }

  .bg-decorations {
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
  }

  .deco-number {
    position: absolute;
    font-family: '$font_heading', 'Helvetica Neue', sans-serif;
    font-size: 20vw;
    font-weight: 700;
    opacity: 0.06;
    color: var(--text-primary);
    left: 5%;
    top: 15%;
    line-height: 1;
    user-select: none;
  }

  .content {
    position: relative;
    z-index: 10;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Header - Gallery: label style */
  header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 clamp(24px, 4vw, 48px);
    z-index: 100;
    background: var(--black);
    border-bottom: 1px solid var(--glass-border);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .header-number {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    color: var(--accent);
    letter-spacing: 2px;
  }

  .header-title {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .header-year {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 2px;
  }

  .hero {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 120px clamp(24px, 8vw, 120px) 80px;
    max-width: 800px;
  }

  .hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 40px;
  }

  .hero-tag::before {
    content: '';
    width: 24px;
    height: 1px;
    background: var(--accent);
  }

  .hero h1 {
    font-family: '$font_heading', 'Helvetica Neue', sans-serif;
    font-size: clamp(40px, 6vw, 96px);
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.01em;
    margin-bottom: 24px;
  }

  .hero-subtitle {
    font-family: '$font_heading', 'Helvetica Neue', sans-serif;
    font-size: clamp(18px, 2vw, 28px);
    font-weight: 300;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }

  .hero p {
    font-size: clamp(13px, 1.2vw, 15px);
    line-height: 1.6;
    color: var(--text-secondary);
    max-width: 480px;
    margin-bottom: 48px;
  }

  .hero-actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 28px;
    background: var(--white);
    color: var(--black);
    border: none;
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-primary:hover {
    background: var(--accent);
    color: var(--black);
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 24px;
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--glass-border);
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-secondary:hover {
    border-color: var(--text-secondary);
  }

  .detail {
    padding: 120px clamp(24px, 8vw, 120px);
    border-top: 1px solid var(--glass-border);
  }

  .detail-grid {
    display: grid;
    grid-template-columns: 160px 1fr 1fr;
    gap: 64px;
    max-width: 1200px;
  }

  .detail-label {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    padding-top: 4px;
  }

  .detail-content h2 {
    font-family: '$font_heading', 'Helvetica Neue', sans-serif;
    font-size: clamp(20px, 2.5vw, 28px);
    font-weight: 300;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
  }

  .detail-content p {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-secondary);
  }

  .detail-meta {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .meta-label {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 9px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .meta-value {
    font-family: '$font_heading', 'Helvetica Neue', sans-serif;
    font-size: 16px;
    font-weight: 300;
    color: var(--text-primary);
  }

  .tech {
    padding: 120px clamp(24px, 8vw, 120px);
    border-top: 1px solid var(--glass-border);
  }

  .tech-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 64px;
  }

  .section-number {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    color: var(--accent);
    letter-spacing: 2px;
  }

  .tech-header h2 {
    font-family: '$font_heading', 'Helvetica Neue', sans-serif;
    font-size: clamp(20px, 2.5vw, 28px);
    font-weight: 300;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--glass-border);
  }

  .tech-card {
    padding: 40px 32px;
    background: var(--black);
  }

  .tech-icon {
    font-size: 24px;
    margin-bottom: 16px;
  }

  .tech-card h3 {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }

  .tech-card p {
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-secondary);
  }

  .stats {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    display: flex;
    justify-content: center;
    background: var(--black);
    border-top: 1px solid var(--glass-border);
  }

  .stat {
    flex: 1;
    max-width: 200px;
    padding: 16px 24px;
    text-align: center;
    border-right: 1px solid var(--glass-border);
  }

  .stat:last-child {
    border-right: none;
  }

  .stat-value {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 14px;
    font-weight: 400;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .stat-label {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 8px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .scroll-hint {
    position: fixed;
    bottom: 80px;
    right: 40px;
    z-index: 50;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .scroll-hint span {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 8px;
    color: var(--text-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    writing-mode: vertical-rl;
  }

  .scroll-line {
    width: 1px;
    height: 32px;
    background: var(--text-muted);
    animation: scrollPulse 2s infinite;
  }

  @keyframes scrollPulse {
    0%, 100% { opacity: 0.2; }
    50% { opacity: 0.6; }
  }

  .loader {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: var(--black);
    z-index: 1000;
    transition: opacity 0.6s, visibility 0.6s;
  }

  .loader.done {
    opacity: 0;
    visibility: hidden;
  }

  .loader-text {
    font-family: '$font_label', 'Space Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  .loader-bar {
    margin-top: 16px;
    width: 80px;
    height: 1px;
    background: var(--glass-border);
    overflow: hidden;
  }

  .loader-fill {
    height: 100%;
    background: var(--text-primary);
    width: 0%;
    transition: width 0.3s;
  }

  .reveal {
    opacity: 0;
    transform: translateX(-30px);
  }

  @media (max-width: 768px) {
    .hero { padding: 100px 24px 80px; }
    .hero-actions { flex-direction: column; align-items: flex-start; }
    .scroll-hint { display: none; }
    .stats { flex-wrap: wrap; }
    .stat { min-width: 50%; border-bottom: 1px solid var(--glass-border); }
    .detail-grid { grid-template-columns: 1fr; gap: 32px; }
    .tech-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<canvas id="bg"></canvas>
<div class="overlay"></div>
<div class="grain"></div>

<div class="bg-decorations">
  <div class="deco-number">$deco_number</div>
</div>

<div class="loader" id="loader">
  <div class="loader-text">Loading</div>
  <div class="loader-bar"><div class="loader-fill" id="loadFill"></div></div>
</div>

<div class="content">
  <header id="header">
    <div class="header-left">
      <span class="header-number">$deco_number</span>
      <span class="header-title">$title</span>
    </div>
    <span class="header-year">2024</span>
  </header>

  <section class="hero" id="hero">
    <div class="hero-tag">$tag</div>
    <h1>$hero_title</h1>
    <div class="hero-subtitle">$subtitle</div>
    <p>$description</p>
    <div class="hero-actions">
      <button class="btn-primary" onclick="toggle()">
        $cta_primary
      </button>
      <a href="#detail" class="btn-secondary">$cta_secondary</a>
    </div>
  </section>

  <section class="detail reveal" id="detail">
    <div class="detail-grid">
      <div class="detail-label">About</div>
      <div class="detail-content">
        <h2>$hero_title</h2>
        <p>$description</p>
      </div>
      <div class="detail-meta">
        <div class="meta-item">
          <span class="meta-label">Frames</span>
          <span class="meta-value">$frame_count</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Frame Rate</span>
          <span class="meta-value">${fps}fps</span>
       106        </div>
        <div class="meta-item">
          <span class="meta-label">Duration</span>
          <span class="meta-value">${duration}s</span>
        </div>
      </div>
    </div>
  </section>

  <section class="tech reveal" id="tech">
    <div class="tech-header">
      <span class="section-number">02</span>
      <h2>Process</h2>
    </div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-icon">🎨</div>
        <h3>Analysis</h3>
        <p>Visual analysis of reference image to extract style, mood, and key features.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">✨</div>
        <h3>Generation</h3>
        <p>AI-powered image generation with style preservation and effect application.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🎬</div>
        <h3>Motion</h3>
        <p>Frame extraction and animation to create seamless motion sequences.</p>
      </div>
    </div>
  </section>
</div>

<div class="stats">
  <div class="stat">
    <div class="stat-value">$frame_count</div>
    <div class="stat-label">Frames</div>
  </div>
  <div class="stat">
    <div class="stat-value">${fps}fps</div>
    <div class="stat-label">Frame Rate</div>
  </div>
  <div class="stat">
    <div class="stat-value">${duration}s</div>
    <div class="stat-label">Duration</div>
  </div>
  <div class="stat">
    <div class="stat-value">AI</div>
    <div class="stat-label">Generated</div>
  </div>
</div>

<div class="scroll-hint">
  <span>Scroll</span>
  <div class="scroll-line"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>

<script>
const TOTAL = $frame_count;
const FPS = $fps;
const ANIM_EASE = "$anim_ease";
const ANIM_DURATION = "$anim_duration";
const ANIM_STAGGER = "$anim_stagger";
const PARALLAX_ENABLED = $parallax_enabled;

const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');
const loader = document.getElementById('loader');
const loadFill = document.getElementById('loadFill');

let frames = [];
let current = 0;
let playing = false;
let lastTime = 0;
let loaded = 0;
let ready = false;

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  if (frames[current] && frames[current].complete) draw(current);
}

function draw(idx) {
  if (!frames[idx] || !frames[idx].complete || !frames[idx].naturalWidth) return;
  const img = frames[idx];
  const scale = Math.max(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);
  const w = img.naturalWidth * scale;
  const h = img.naturalHeight * scale;
  const x = (canvas.width - w) / 2;
  const y = (canvas.height - h) / 2;
  ctx.drawImage(img, x, y, w, h);
}

function loop(time) {
  if (!playing) return;
  if (time - lastTime >= 1000 / FPS) {
    current = (current + 1) % TOTAL;
    draw(current);
    lastTime = time;
  }
  requestAnimationFrame(loop);
}

function toggle() {
  if (!ready) return;
  playing = !playing;
  if (playing) {
    requestAnimationFrame(loop);
  }
}

function start() {
  if (ready) return;
  ready = true;
  playing = true;
  loader.classList.add('done');
  draw(0);
  requestAnimationFrame(loop);

  // Gallery entrance timeline
  const tl = gsap.timeline();
  tl.from("header", { opacity: 0, duration: 1.2, ease: ANIM_EASE })
    .from(".hero-tag", { opacity: 0, x: -20, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.6")
    .from(".hero h1", { opacity: 0, x: -30, duration: parseFloat(ANIM_DURATION) * 1.2, ease: ANIM_EASE }, "-=0.8")
    .from(".hero-subtitle", { opacity: 0, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.6")
    .from(".hero p", { opacity: 0, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.6")
    .from(".hero-actions", { opacity: 0, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.4")
    .from(".stats", { opacity: 0, duration: 0.5, ease: "power2.out" }, "-=0.2");

  gsap.utils.toArray('.reveal').forEach(el => {
    gsap.from(el, {
      scrollTrigger: {
        trigger: el,
        start: "top 85%",
        end: "top 50%",
        toggleActions: "play none none reverse"
      },
      opacity: 0,
      x: -30,
      duration: parseFloat(ANIM_DURATION),
      ease: "power2.out"
    });
  });
}

if (typeof gsap === 'undefined') {
  console.warn('GSAP CDN failed to load, falling back to CSS animations');
  document.body.setAttribute('data-gsap-failed', 'true');
}

resize();
window.addEventListener('resize', resize);

for (let i = 1; i <= TOTAL; i++) {
  const img = new Image();
  img.onload = () => {
    loaded++;
    loadFill.style.width = (loaded / TOTAL * 100) + '%';
    if (loaded === 1) {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      draw(0);
    }
    if (loaded >= Math.min(12, TOTAL)) start();
  };
  img.src = `public/frames/frame_${String(i).padStart(4, '0')}.jpg`;
  frames.push(img);
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    e.preventDefault();
    toggle();
  }
});
</script>
</body>
</html>
```

- [ ] **Step 2: Verify file exists**

Run: `ls -la .claude/skills/hero-shot-builder/styles/`
Expected: `gallery.html` exists

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/hero-shot-builder/styles/gallery.html
git commit -m "feat: add gallery style pack HTML template"
```

---

### Task 5: Create warm style pack HTML template

**Files:**
- Create: `.claude/skills/hero-shot-builder/styles/warm.html`

- [ ] **Step 1: Create warm.html with natural layout**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<style>
  @import url('$font_import');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --white: #ffffff;
    --black: #000000;
    --glass: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --text-primary: rgba(255, 255, 255, 0.95);
    --text-secondary: rgba(255, 255, 255, 0.6);
    --text-muted: rgba(255, 255, 255, 0.35);
    --accent: $accent_color;
    --accent-glow: $accent_glow;
  }

  body {
    background: var(--black);
    color: var(--white);
    font-family: '$font_body', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
    min-height: 100vh;
  }

  #bg {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
  }

  .overlay {
    position: fixed;
    inset: 0;
    z-index: 1;
    background:
      linear-gradient(180deg,
        rgba(0,0,0,0.25) 0%,
        rgba(0,0,0,0.1) 30%,
        rgba(0,0,0,0.1) 60%,
        rgba(0,0,0,0.5) 100%
      );
    pointer-events: none;
  }

  .grain {
    position: fixed;
    inset: 0;
    z-index: 2;
    opacity: 0.04;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 128px;
  }

  .bg-decorations {
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
  }

  .radial-glow {
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
    opacity: 0.1;
    filter: blur(80px);
    bottom: 20%;
    right: 15%;
  }

  .ghost-text {
    position: absolute;
    font-family: '$font_heading', serif;
    font-size: 12vw;
    font-weight: 400;
    font-style: italic;
    opacity: 0.04;
    color: var(--text-primary);
    right: 5%;
    bottom: 15%;
    line-height: 1;
    user-select: none;
  }

  .content {
    position: relative;
    z-index: 10;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Header - Warm: hamburger menu */
  header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 clamp(24px, 4vw, 48px);
    z-index: 100;
    background: rgba(0,0,0,0.05);
    transition: background 0.4s ease;
  }

  header.scrolled {
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  .logo {
    font-family: '$font_heading', serif;
    font-size: 18px;
    font-weight: 400;
    font-style: italic;
    color: var(--text-primary);
  }

  .menu-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-primary);
    font-family: '$font_body', sans-serif;
    font-size: 13px;
  }

  .menu-icon {
    width: 20px;
    height: 14px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .menu-icon span {
    display: block;
    width: 100%;
    height: 1px;
    background: var(--text-primary);
    transition: all 0.3s;
  }

  .hero {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 120px clamp(24px, 6vw, 80px) 80px;
    max-width: 800px;
  }

  .hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 100px;
    font-size: 12px;
    color: var(--accent);
    font-weight: 400;
    width: fit-content;
    margin-bottom: 32px;
  }

  .hero-tag .dot {
    width: 6px;
    height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .hero h1 {
    font-family: '$font_heading', serif;
    font-size: clamp(36px, 5vw, 72px);
    font-weight: 400;
    font-style: italic;
    line-height: 1.15;
    letter-spacing: 0.01em;
    margin-bottom: 24px;
  }

  .hero-subtitle {
    font-family: '$font_heading', serif;
    font-size: clamp(18px, 2vw, 28px);
    font-weight: 400;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }

  .hero p {
    font-size: clamp(14px, 1.5vw, 17px);
    line-height: 1.8;
    color: var(--text-secondary);
    max-width: 520px;
    margin-bottom: 48px;
  }

  .hero-actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 32px;
    background: var(--accent);
    color: var(--black);
    border: none;
    border-radius: 100px;
    font-size: 14px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px var(--accent-glow);
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 28px;
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--glass-border);
    border-radius: 100px;
    font-size: 14px;
    font-weight: 400;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
  }

  .btn-secondary:hover {
    background: var(--glass);
    border-color: var(--text-secondary);
  }

  .detail {
    padding: 120px clamp(24px, 6vw, 80px);
    background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.3) 100%);
  }

  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 80px;
    max-width: 1000px;
  }

  .detail-label {
    font-size: 12px;
    color: var(--accent);
    letter-spacing: 1px;
    margin-bottom: 16px;
  }

  .detail-content h2 {
    font-family: '$font_heading', serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 400;
    font-style: italic;
    margin-bottom: 16px;
  }

  .detail-content p {
    font-size: 15px;
    line-height: 1.8;
    color: var(--text-secondary);
  }

  .detail-meta {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    align-content: start;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .meta-label {
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 1px;
  }

  .meta-value {
    font-family: '$font_heading', serif;
    font-size: 18px;
    font-style: italic;
    color: var(--text-primary);
  }

  .tech {
    padding: 120px clamp(24px, 6vw, 80px);
  }

  .tech-header {
    margin-bottom: 64px;
  }

  .section-number {
    font-size: 11px;
    color: var(--accent);
    display: block;
    margin-bottom: 8px;
  }

  .tech-header h2 {
    font-family: '$font_heading', serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 400;
    font-style: italic;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
  }

  .tech-card {
    padding: 32px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
  }

  .tech-icon {
    font-size: 28px;
    margin-bottom: 16px;
  }

  .tech-card h3 {
    font-family: '$font_heading', serif;
    font-size: 18px;
    font-weight: 400;
    font-style: italic;
    margin-bottom: 12px;
  }

  .tech-card p {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-secondary);
  }

  .stats {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    display: flex;
    justify-content: center;
    gap: 1px;
    background: var(--glass-border);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-top: 1px solid var(--glass-border);
  }

  .stat {
    flex: 1;
    max-width: 200px;
    padding: 20px 24px;
    text-align: center;
    background: rgba(0,0,0,0.5);
  }

  .stat-value {
    font-family: '$font_heading', serif;
    font-size: 24px;
    font-style: italic;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 1px;
  }

  .scroll-hint {
    position: fixed;
    bottom: 100px;
    right: 40px;
    z-index: 50;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .scroll-hint span {
    font-size: 9px;
    color: var(--text-muted);
    letter-spacing: 2px;
    writing-mode: vertical-rl;
  }

  .scroll-line {
    width: 1px;
    height: 40px;
    background: linear-gradient(to bottom, var(--accent), transparent);
    animation: scrollPulse 2s infinite;
  }

  @keyframes scrollPulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.8; }
  }

  .loader {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: var(--black);
    z-index: 1000;
    transition: opacity 0.6s, visibility 0.6s;
  }

  .loader.done {
    opacity: 0;
    visibility: hidden;
  }

  .loader-ring {
    width: 40px;
    height: 40px;
    border: 2px solid var(--glass-border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .loader-text {
    margin-top: 20px;
    font-family: '$font_heading', serif;
    font-size: 14px;
    font-style: italic;
    color: var(--text-secondary);
  }

  .loader-bar {
    margin-top: 16px;
    width: 100px;
    height: 2px;
    background: var(--glass-border);
    border-radius: 1px;
    overflow: hidden;
  }

  .loader-fill {
    height: 100%;
    background: var(--accent);
    width: 0%;
    transition: width 0.3s;
  }

  .reveal {
    opacity: 0;
    transform: translateY(30px);
  }

  @media (max-width: 768px) {
    .hero { padding: 140px 24px 120px; }
    .hero-actions { flex-direction: column; align-items: flex-start; }
    .scroll-hint { display: none; }
    .stats { flex-wrap: wrap; }
    .stat { min-width: 50%; }
    .detail-grid { grid-template-columns: 1fr; gap: 48px; }
    .tech-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<canvas id="bg"></canvas>
<div class="overlay"></div>
<div class="grain"></div>

<div class="bg-decorations">
  <div class="radial-glow breathing"></div>
  <div class="ghost-text drifting">$ghost_text</div>
</div>

<div class="loader" id="loader">
  <div class="loader-ring"></div>
  <div class="loader-text">Loading</div>
  <div class="loader-bar"><div class="loader-fill" id="loadFill"></div></div>
</div>

<div class="content">
  <header id="header">
    <div class="logo">$title</div>
    <button class="menu-btn">
      <span>Menu</span>
      <div class="menu-icon">
        <span></span>
        <span></span>
      </div>
    </button>
  </header>

  <section class="hero" id="hero">
    <div class="hero-tag">
      <span class="dot"></span>
      $tag
    </div>
    <h1>$hero_title</h1>
    <div class="hero-subtitle">$subtitle</div>
    <p>$description</p>
    <div class="hero-actions">
      <button class="btn-primary" onclick="toggle()">
        $cta_primary
      </button>
      <a href="#detail" class="btn-secondary">$cta_secondary</a>
    </div>
  </section>

  <section class="detail reveal" id="detail">
    <div class="detail-grid">
      <div>
        <div class="detail-label">About</div>
        <div class="detail-content">
          <h2>$hero_title</h2>
          <p>$description</p>
        </div>
      </div>
      <div class="detail-meta">
        <div class="meta-item">
          <span class="meta-label">Frames</span>
          <span class="meta-value">$frame_count</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Frame Rate</span>
          <span class="meta-value">${fps}fps</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Duration</span>
          <span class="meta-value">${duration}s</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Generated</span>
          <span class="meta-value">AI</span>
        </div>
      </div>
    </div>
  </section>

  <section class="tech reveal" id="tech">
    <div class="tech-header">
      <span class="section-number">02</span>
      <h2>Process</h2>
    </div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-icon">🎨</div>
        <h3>Analysis</h3>
        <p>Visual analysis of reference image to extract style, mood, and key features.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">✨</div>
        <h3>Generation</h3>
        <p>AI-powered image generation with style preservation and effect application.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🎬</div>
        <h3>Motion</h3>
        <p>Frame extraction and animation to create seamless motion sequences.</p>
      </div>
    </div>
  </section>
</div>

<div class="stats">
  <div class="stat">
    <div class="stat-value">$frame_count</div>
    <div class="stat-label">Frames</div>
  </div>
  <div class="stat">
    <div class="stat-value">${fps}fps</div>
    <div class="stat-label">Frame Rate</div>
  </div>
  <div class="stat">
    <div class="stat-value">${duration}s</div>
    <div class="stat-label">Duration</div>
  </div>
  <div class="stat">
    <div class="stat-value">AI</div>
    <div class="stat-label">Generated</div>
  </div>
</div>

<div class="scroll-hint">
  <span>Scroll</span>
  <div class="scroll-line"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>

<script>
const TOTAL = $frame_count;
const FPS = $fps;
const ANIM_EASE = "$anim_ease";
const ANIM_DURATION = "$anim_duration";
const ANIM_STAGGER = "$anim_stagger";
const PARALLAX_ENABLED = $parallax_enabled;

const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');
const loader = document.getElementById('loader');
const loadFill = document.getElementById('loadFill');
const header = document.getElementById('header');

let frames = [];
let current = 0;
let playing = false;
let lastTime = 0;
let loaded = 0;
let ready = false;

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  if (frames[current] && frames[current].complete) draw(current);
}

function draw(idx) {
  if (!frames[idx] || !frames[idx].complete || !frames[idx].naturalWidth) return;
  const img = frames[idx];
  const scale = Math.max(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);
  const w = img.naturalWidth * scale;
  const h = img.naturalHeight * scale;
  const x = (canvas.width - w) / 2;
  const y = (canvas.height - h) / 2;
  ctx.drawImage(img, x, y, w, h);
}

function loop(time) {
  if (!playing) return;
  if (time - lastTime >= 1000 / FPS) {
    current = (current + 1) % TOTAL;
    draw(current);
    lastTime = time;
  }
  requestAnimationFrame(loop);
}

function toggle() {
  if (!ready) return;
  playing = !playing;
  if (playing) {
    requestAnimationFrame(loop);
  }
}

function start() {
  if (ready) return;
  ready = true;
  playing = true;
  loader.classList.add('done');
  draw(0);
  requestAnimationFrame(loop);

  // Warm entrance timeline
  const tl = gsap.timeline();
  tl.from("header", { opacity: 0, y: -10, duration: 1.0, ease: ANIM_EASE })
    .from(".hero-tag", { opacity: 0, y: 16, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.5")
    .from(".hero h1", { opacity: 0, y: 20, duration: parseFloat(ANIM_DURATION) * 1.2, ease: ANIM_EASE }, "-=0.5")
    .from(".hero-subtitle", { opacity: 0, y: 12, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.4")
    .from(".hero p", { opacity: 0, y: 12, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.4")
    .from(".hero-actions", { opacity: 0, y: 10, duration: parseFloat(ANIM_DURATION), ease: ANIM_EASE }, "-=0.3")
    .from(".stats", { opacity: 0, y: 20, duration: 0.5, ease: "power2.out" }, "-=0.2");

  gsap.utils.toArray('.reveal').forEach(el => {
    gsap.from(el, {
      scrollTrigger: {
        trigger: el,
        start: "top 85%",
        end: "top 50%",
        toggleActions: "play none none reverse"
      },
      opacity: 0,
      y: 30,
      duration: parseFloat(ANIM_DURATION),
      ease: "power2.out"
    });
  });

  ScrollTrigger.create({
    start: "top -50",
    end: 99999,
    toggleClass: { className: "scrolled", targets: header }
  });

  // Breathing animation for decorations
  gsap.to('.breathing', {
    scale: 1.02,
    duration: 3,
    repeat: -1,
    yoyo: true,
    ease: "sine.inOut"
  });

  gsap.to('.drifting', {
    y: "+=15",
    duration: 8,
    repeat: -1,
    yoyo: true,
    ease: "sine.inOut"
  });
}

if (typeof gsap === 'undefined') {
  console.warn('GSAP CDN failed to load, falling back to CSS animations');
  document.body.setAttribute('data-gsap-failed', 'true');
}

resize();
window.addEventListener('resize', resize);

for (let i = 1; i <= TOTAL; i++) {
  const img = new Image();
  img.onload = () => {
    loaded++;
    loadFill.style.width = (loaded / TOTAL * 100) + '%';
    if (loaded === 1) {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      draw(0);
    }
    if (loaded >= Math.min(12, TOTAL)) start();
  };
  img.src = `public/frames/frame_${String(i).padStart(4, '0')}.jpg`;
  frames.push(img);
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    e.preventDefault();
    toggle();
  }
});
</script>
</body>
</html>
```

- [ ] **Step 2: Verify file exists**

Run: `ls -la .claude/skills/hero-shot-builder/styles/`
Expected: `warm.html` exists

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/hero-shot-builder/styles/warm.html
git commit -m "feat: add warm style pack HTML template"
```

---

### Task 6: Update hero-shot-builder.md with style pack selection logic

**Files:**
- Modify: `.claude/skills/hero-shot-builder.md`

- [ ] **Step 1: Read current hero-shot-builder.md**

Run: `cat .claude/skills/hero-shot-builder.md | head -100`

- [ ] **Step 2: Add style pack selection section after Step 2**

Insert after line 85 (after animation presets table):

```markdown
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
```

- [ ] **Step 3: Update Step 6 to use style packs**

Replace the template reference section with:

```markdown
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
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/hero-shot-builder.md
git commit -m "feat: add style pack selection logic to hero-shot-builder"
```

---

### Task 7: Update vibecode-agent.md BUILD_PROJECT section

**Files:**
- Modify: `.claude/skills/vibecode-agent.md`

- [ ] **Step 1: Read current BUILD_PROJECT section**

Run: `grep -n "BUILD_PROJECT" .claude/skills/vibecode-agent.md`

- [ ] **Step 2: Add style pack integration note**

Insert after "Step 4：生成网页文件" section:

```markdown
**风格包集成**：
- 读取 `.claude/skills/hero-shot-builder/params.json` 获取参数定义
- 根据 `image_analysis.style_profile.keywords` 选择风格包
- 使用 `decide_params()` 函数自动决定参数值
- 读取对应风格包模板 `.claude/skills/hero-shot-builder/styles/{style_pack}.html`
- 应用参数微调后生成最终 HTML
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/vibecode-agent.md
git commit -m "feat: add style pack integration to vibecode-agent BUILD_PROJECT"
```

---

### Task 8: Test style pack selection logic

**Files:**
- Create: `tests/test_style_packs.py`

- [ ] **Step 1: Write test for style pack selection**

```python
import sys
sys.path.insert(0, '.')
import pytest

def test_style_pack_selection():
    """Test that style packs are correctly selected based on keywords"""
    from agent.web_builder import get_design_direction
    
    # Test editorial
    fh, fb, ac, ag, fi = get_design_direction("person")
    assert fh == "Playfair Display"
    
    # Test immersive (cyberpunk)
    # This tests the mapping logic
    
def test_params_decision():
    """Test that parameters are correctly decided based on analysis"""
    # Mock analysis
    analysis = {
        "style_profile": {
            "keywords": ["cyberpunk", "high contrast"],
            "visual_tone": "高对比、冷色调"
        },
        "mood": "神秘、未来感"
    }
    
    # Import the decide_params function
    # This would need to be added to web_builder.py
    
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_style_packs.py -v`
Expected: FAIL (function not defined)

- [ ] **Step 3: Add decide_params function to web_builder.py**

```python
def decide_params(analysis):
    """根据 image_analysis 自动决定参数值"""
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

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_style_packs.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_style_packs.py agent/web_builder.py
git commit -m "feat: add decide_params function and tests for style pack selection"
```

---

### Task 9: Integration test with actual workflow

**Files:**
- Create: `tests/test_integration_style_packs.py`

- [ ] **Step 1: Write integration test**

```python
import sys
sys.path.insert(0, '.')
import pytest
import json

def test_full_workflow_with_style_pack():
    """Test full workflow with style pack integration"""
    # Mock workflow state
    workflow = {
        "stage": "BUILD_PROJECT",
        "image_analysis": {
            "subject": "test subject",
            "subject_type": "other",
            "style_profile": {
                "keywords": ["editorial", "magazine"],
                "copy_tone": "简短有力、诗意、留白感"
            },
            "mood": "神秘、超现实"
        },
        "page_purpose": "作品展示",
        "extracted_palette": {
            "accent_color": "#ff4444",
            "accent_glow": "rgba(255, 68, 68, 0.3)"
        }
    }
    
    # Test style pack selection
    keywords = workflow["image_analysis"]["style_profile"]["keywords"]
    style_pack = "gallery"  # default
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
    
    assert style_pack == "editorial"
    
    # Test params decision
    from agent.web_builder import decide_params
    params = decide_params(workflow["image_analysis"])
    assert params["deco_density"] == "normal"
    assert params["anim_energy"] == "moderate"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

- [ ] **Step 2: Run integration test**

Run: `python -m pytest tests/test_integration_style_packs.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration_style_packs.py
git commit -m "test: add integration test for style pack workflow"
```

---

## Plan Complete

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
