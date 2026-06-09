def generate_player_html(frame_count: int, fps: int = 24, title: str = "Hero Shot") -> str:
    """生成精美展示网页 HTML

    Args:
        frame_count: 帧图片总数
        fps: 播放帧率
        title: 页面标题

    Returns:
        完整的 HTML 字符串
    """
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    if fps <= 0:
        raise ValueError("fps must be positive")

    duration = f"{frame_count // fps}:{frame_count % fps:02d}"

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  :root {{
    --bg: #0a0a0a;
    --surface: #141414;
    --border: rgba(255,255,255,0.08);
    --text: rgba(255,255,255,0.9);
    --text-dim: rgba(255,255,255,0.5);
    --accent: #fff;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* Header */
  header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    background: linear-gradient(var(--bg), transparent);
    z-index: 100;
    opacity: 0;
    transform: translateY(-10px);
    animation: fadeDown 0.6s 1s forwards;
  }}
  @keyframes fadeDown {{
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .logo {{
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }}
  .nav {{
    display: flex;
    gap: 24px;
  }}
  .nav a {{
    color: var(--text-dim);
    text-decoration: none;
    font-size: 13px;
    font-weight: 400;
    transition: color 0.2s;
  }}
  .nav a:hover {{ color: var(--text); }}

  /* Hero Section */
  .hero {{
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
    padding: 80px 32px 120px;
  }}

  .player-wrap {{
    position: relative;
    width: 100%;
    max-width: 960px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 24px 80px rgba(0,0,0,0.5), 0 0 0 1px var(--border);
    background: #000;
    opacity: 0;
    transform: scale(0.95);
    animation: scaleIn 0.8s 0.3s forwards;
  }}
  @keyframes scaleIn {{
    to {{ opacity: 1; transform: scale(1); }}
  }}

  canvas {{
    display: block;
    width: 100%;
    aspect-ratio: 16/9;
    background: #000;
  }}

  /* Vignette */
  .player-wrap::after {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.3) 100%);
    pointer-events: none;
    border-radius: 12px;
  }}

  /* Controls overlay */
  .controls {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 48px 20px 16px;
    background: linear-gradient(transparent, rgba(0,0,0,0.8));
    display: flex;
    align-items: center;
    gap: 12px;
    opacity: 0;
    transition: opacity 0.3s;
  }}
  .player-wrap:hover .controls {{ opacity: 1; }}

  .btn {{
    background: rgba(255,255,255,0.1);
    border: none;
    color: #fff;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    transition: background 0.2s;
    flex-shrink: 0;
  }}
  .btn:hover {{ background: rgba(255,255,255,0.2); }}

  .timeline {{
    flex: 1;
    height: 4px;
    background: rgba(255,255,255,0.2);
    border-radius: 2px;
    cursor: pointer;
    position: relative;
    transition: height 0.15s;
  }}
  .timeline:hover {{ height: 6px; }}
  .timeline-fill {{
    height: 100%;
    background: #fff;
    border-radius: 2px;
    width: 0%;
    position: relative;
  }}
  .timeline-fill::after {{
    content: '';
    position: absolute;
    right: -5px;
    top: 50%;
    transform: translateY(-50%);
    width: 10px;
    height: 10px;
    background: #fff;
    border-radius: 50%;
    opacity: 0;
    transition: opacity 0.15s;
  }}
  .timeline:hover .timeline-fill::after {{ opacity: 1; }}

  .time {{
    color: rgba(255,255,255,0.6);
    font-size: 12px;
    font-variant-numeric: tabular-nums;
    min-width: 90px;
    text-align: right;
  }}

  /* Loading */
  .loader {{
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #000;
    z-index: 10;
    transition: opacity 0.5s;
    border-radius: 12px;
  }}
  .loader.done {{ opacity: 0; pointer-events: none; }}
  .loader-ring {{
    width: 40px;
    height: 40px;
    border: 2px solid rgba(255,255,255,0.1);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  .loader-text {{
    margin-top: 16px;
    color: var(--text-dim);
    font-size: 12px;
    letter-spacing: 1px;
  }}
  .loader-bar {{
    margin-top: 12px;
    width: 100px;
    height: 2px;
    background: rgba(255,255,255,0.1);
    border-radius: 1px;
    overflow: hidden;
  }}
  .loader-fill {{
    height: 100%;
    background: #fff;
    width: 0%;
    transition: width 0.2s;
  }}

  /* Info section */
  .info {{
    max-width: 960px;
    margin: 0 auto;
    padding: 60px 32px 80px;
    opacity: 0;
    transform: translateY(20px);
    animation: fadeUp 0.6s 1.2s forwards;
  }}
  @keyframes fadeUp {{
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .info-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    border-radius: 12px;
    overflow: hidden;
  }}
  .info-card {{
    background: var(--surface);
    padding: 24px;
  }}
  .info-label {{
    font-size: 11px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
  }}
  .info-value {{
    font-size: 20px;
    font-weight: 500;
  }}

  /* Footer */
  footer {{
    text-align: center;
    padding: 32px;
    color: var(--text-dim);
    font-size: 12px;
    border-top: 1px solid var(--border);
  }}

  /* Keyboard hint */
  .kbd {{
    display: inline-block;
    padding: 2px 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
    font-size: 11px;
    font-family: monospace;
    margin: 0 2px;
  }}

  @media (max-width: 640px) {{
    header {{ padding: 0 16px; }}
    .nav {{ display: none; }}
    .hero {{ padding: 60px 16px 100px; }}
    .player-wrap {{ border-radius: 8px; }}
    .info {{ padding: 40px 16px 60px; }}
    .info-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <div class="logo">{title}</div>
  <nav class="nav">
    <a href="#player">Watch</a>
    <a href="#info">Details</a>
  </nav>
</header>

<section class="hero" id="player">
  <div class="player-wrap">
    <canvas id="canvas"></canvas>
    <div class="loader" id="loader">
      <div class="loader-ring"></div>
      <div class="loader-text">Loading frames</div>
      <div class="loader-bar"><div class="loader-fill" id="loadFill"></div></div>
    </div>
    <div class="controls">
      <button class="btn" id="playBtn">&#9654;</button>
      <div class="timeline" id="timeline">
        <div class="timeline-fill" id="progress"></div>
      </div>
      <span class="time" id="time">0:00 / {duration}</span>
    </div>
  </div>
</section>

<section class="info" id="info">
  <div class="info-grid">
    <div class="info-card">
      <div class="info-label">Frames</div>
      <div class="info-value">{frame_count}</div>
    </div>
    <div class="info-card">
      <div class="info-label">Frame Rate</div>
      <div class="info-value">{fps} fps</div>
    </div>
    <div class="info-card">
      <div class="info-label">Duration</div>
      <div class="info-value">{duration}s</div>
    </div>
  </div>
</section>

<footer>
  Press <span class="kbd">Space</span> to play / pause &middot; Click timeline to seek
</footer>

<script>
const TOTAL = {frame_count};
const FPS = {fps};
const DURATION = TOTAL / FPS;

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const playBtn = document.getElementById('playBtn');
const progress = document.getElementById('progress');
const timeline = document.getElementById('timeline');
const timeEl = document.getElementById('time');
const loader = document.getElementById('loader');
const loadFill = document.getElementById('loadFill');

let frames = [];
let current = 0;
let playing = false;
let lastTime = 0;
let loaded = 0;

function fmt(s) {{
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return m + ':' + String(sec).padStart(2, '0');
}}

for (let i = 1; i <= TOTAL; i++) {{
  const img = new Image();
  img.onload = () => {{
    loaded++;
    loadFill.style.width = (loaded / TOTAL * 100) + '%';
    if (loaded === 1) {{
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      draw(0);
    }}
    if (loaded >= Math.min(12, TOTAL)) startPlayback();
  }};
  img.src = `public/frames/frame_${{String(i).padStart(4, '0')}}.jpg`;
  frames.push(img);
}}

function draw(idx) {{
  if (frames[idx] && frames[idx].complete) {{
    ctx.drawImage(frames[idx], 0, 0);
  }}
  progress.style.width = ((idx + 1) / TOTAL * 100) + '%';
  timeEl.textContent = fmt(idx / FPS) + ' / ' + fmt(DURATION);
}}

function loop(time) {{
  if (!playing) return;
  if (time - lastTime >= 1000 / FPS) {{
    current = (current + 1) % TOTAL;
    draw(current);
    lastTime = time;
  }}
  requestAnimationFrame(loop);
}}

function startPlayback() {{
  if (playing) return;
  loader.classList.add('done');
  playing = true;
  playBtn.innerHTML = '&#9646;&#9646;';
  requestAnimationFrame(loop);
}}

function toggle() {{
  playing = !playing;
  playBtn.innerHTML = playing ? '&#9646;&#9646;' : '&#9654;';
  if (playing) requestAnimationFrame(loop);
}}

playBtn.addEventListener('click', (e) => {{
  e.stopPropagation();
  toggle();
}});

timeline.addEventListener('click', (e) => {{
  e.stopPropagation();
  const rect = timeline.getBoundingClientRect();
  const ratio = (e.clientX - rect.left) / rect.width;
  current = Math.floor(ratio * TOTAL) % TOTAL;
  draw(current);
}});

document.addEventListener('keydown', (e) => {{
  if (e.code === 'Space') {{
    e.preventDefault();
    toggle();
  }}
}});
</script>
</body>
</html>'''
