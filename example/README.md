# VibeCode 动效网站工作流

用 Seedream AI 生成产品图片，配合即梦/Seedance 生成过渡视频，自动拆帧并生成可直接使用的网站项目。

---

## 工作流程总览

```
Step 0（自动）  →  Step 1（手动）  →  Step 2（自动）  →  Step 3（自动）  →  Step 4（手动）
Seedream API       即梦/Seedance      视频拆帧           生成项目文件        AI IDE 建站
生成两张图片        网页生成视频       frame_xxxx.jpg      PROMPT.md          滚动动画网站
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

ffmpeg（拆帧必须）：
```bash
# macOS
brew install ffmpeg

# Windows：下载后加入 PATH
# https://www.gyan.dev/ffmpeg/builds/

# Linux
sudo apt install ffmpeg
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 ARK_API_KEY
```

### 3. Step 0 — 生成关键帧图片（自动）

```bash
python scripts/step0_generate_images.py \
    --product "智能咖啡杯" \
    --desc "具有温度控制和智能提醒功能的高端咖啡杯" \
    --style "白色背景，商业产品摄影，高清"
```

生成结果：`input/img1.jpg`（静态图）、`input/img2.jpg`（动态图）

---

### 4. Step 1 — 手动生成过渡视频

打开以下任意一个网页工具：

| 工具 | 地址 | 功能 |
|------|------|------|
| 即梦 AI | https://jimeng.jianying.com | 首尾帧生视频，免费额度 |
| 火山方舟视频生成 | https://console.volcengine.com/ark | Seedance 2.0，效果更好 |

操作步骤：
1. 选择「首尾帧生视频」功能
2. 首帧上传 `input/img1.jpg`，尾帧上传 `input/img2.jpg`
3. 提示词填写：`产品从精致完整到爆炸展开的流畅过渡，电影级，动感`
4. 时长选择 5~8 秒，分辨率 720p 或以上
5. 生成完成后下载视频，保存到项目根目录，**命名为 `transition.mp4`**

---

### 5. Step 2 — 视频拆帧（自动）

```bash
python scripts/step1_extract_frames.py
```

自定义参数：
```bash
python scripts/step1_extract_frames.py \
    --video transition.mp4 \
    --fps 24
```

---

### 6. Step 3 — 生成项目文件（自动）

```bash
python scripts/step2_prepare_project.py \
    --product "智能咖啡杯" \
    --desc "具有温度控制和智能提醒功能的高端咖啡杯"
```

生成结果：`projects/智能咖啡杯/`

---

### 7. Step 4 — 用 AI IDE 生成网站（手动）

1. 用 **Cursor** 或 **MarsCode** 打开 `projects/智能咖啡杯/` 文件夹
2. 打开 `PROMPT.md`，按步骤将提示词逐一粘贴给 AI 执行
3. 在浏览器打开 `index.html`，滚动页面查看动画效果

---

## 参数说明

### step0_generate_images.py

| 参数 | 说明 | 示例 |
|------|------|------|
| `--product` | 产品名称 | `"智能咖啡杯"` |
| `--desc` | 产品描述 | `"具有温度控制功能"` |
| `--style` | 画面风格 | `"白色背景，商业摄影"` |
| `--out` | 图片输出目录 | `input`（默认） |

### step1_extract_frames.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--video` | 视频文件路径 | `transition.mp4` |
| `--fps` | 提取帧率 | `24` |
| `--outdir` | 帧输出目录 | `temp/frames` |

### step2_prepare_project.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--product` | 产品名称 | 必填 |
| `--desc` | 产品描述 | 必填 |
| `--frames` | 帧图片目录 | `temp/frames` |
| `--output` | 项目输出目录 | `projects` |

---

## 目录结构

```
vibecode-workflow/
├── input/                      ← Step 0 生成的图片
│   ├── img1.jpg                   静态图
│   └── img2.jpg                   动态图
├── transition.mp4              ← 手动下载的过渡视频（放这里）
├── temp/
│   └── frames/                 ← Step 2 拆帧结果
├── projects/
│   └── 产品名称/               ← Step 3 生成的项目文件
│       ├── public/frames/         帧图片
│       ├── PROMPT.md              AI 提示词
│       ├── rules.json             编码规范
│       └── README.md
├── scripts/
│   ├── step0_generate_images.py
│   ├── step1_extract_frames.py
│   └── step2_prepare_project.py
├── .env                        ← 填写 ARK_API_KEY
├── .env.example                ← 配置模板
└── requirements.txt
```

---

## 常见问题

**Q：Step 0 图片生成报错 401？**
A：检查 `.env` 里的 `ARK_API_KEY` 是否正确，注意去掉前后空格。

**Q：即梦AI生成的视频效果不好？**
A：调整提示词，加入具体的动作描述。或改用火山方舟控制台的 Seedance 2.0，效果更可控。

**Q：拆帧后帧数太少（低于 60 帧）？**
A：说明视频时长较短。重新生成 8~10 秒的视频，或将 `--fps` 改为 `12` 降低帧率。

**Q：AI IDE 生成的动画滚动不流畅？**
A：在第四步提示词里加入："将帧动画改为每隔 2 帧取 1 帧，减少总帧数至 60 帧"。
