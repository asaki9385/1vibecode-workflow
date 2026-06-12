# VibeCode Agent

AI driven product video workflow tool. From a single product image, through visual analysis, intent clarification, image-to-image refinement, video prompt generation, and automatic frame extraction, output a full-screen animated hero shot webpage.

## Features

- **State machine architecture**: 11-stage complete workflow with resume capability
- **Dual-mode interaction**: Quick mode (agent decides) / Detailed mode (intent clarification dialogue)
- **Structured visual analysis**: subject_type branching, style_profile 4-field coherent derivation
- **Dynamic effect options**: Auto-generated from movable_elements, not fixed templates
- **Real color extraction**: Accent color from image1, avoids generic AI palette
- **GSAP entrance animations**: ease/scale/rotation auto-matched from style_profile keywords
- **frontend-design integration**: Cached summary, no repeated loading
- **Post-generation feedback loop**: Unified feedback at 4 key stages

## Workflow

```
INIT -> ANALYZE -> SELECT_MODE -> CONFIRM_PRODUCT -> GENERATE
-> CONFIRM_IMAGES -> BUILD_VIDEO_PROMPT -> WAIT_VIDEO
-> EXTRACT_FRAMES -> BUILD_PROJECT -> DONE
```

### Stage Overview

| Stage | Description |
|-------|-------------|
| INIT | Detect images in input/ directory |
| ANALYZE | Structured visual analysis, output image_analysis (subject_type, movable_elements, style_profile) |
| SELECT_MODE | Mandatory choice: Quick mode / Detailed mode |
| CONFIRM_PRODUCT | Dynamic effect options + 4-dimension intent clarification (effect/scene/exclude/style) |
| GENERATE | Image1 regenerate + color extraction + Image2 refine |
| CONFIRM_IMAGES | Ending intent clarification + image1->image2 comparison (transition_analysis) |
| BUILD_VIDEO_PROMPT | Generate video transition prompt from transition_analysis |
| WAIT_VIDEO | Wait for user to place video file |
| EXTRACT_FRAMES | ffmpeg frame extraction |
| BUILD_PROJECT | Copy generation + palette selection + frontend-design specs + webpage generation |
| DONE | Complete, archive to data/ |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

ffmpeg required (for frame extraction):
```bash
# macOS
brew install ffmpeg

# Windows
# Download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH

# Linux
sudo apt install ffmpeg
```

### 2. Configure API Key

Edit `.env` file:
```env
ARK_API_KEY=your-volcengine-api-key
```

Get key at: https://console.volcengine.com/ark -> API Key Management

### 3. Place Product Images

Put product images in the `input/` directory. Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`, `.tiff`.

### 4. Start Workflow

In Claude Code, run:
```
/vibecode-agent
```

## Project Structure

```
vibecode-workflow/
├── agent/
│   ├── workflow.py           <- State management
│   ├── image_generator.py    <- Seedream API wrapper (img2img support)
│   ├── prompt_builder.py     <- Prompt generation (with negative constraints)
│   ├── color_extractor.py    <- Palette extraction + accent color selection
│   ├── frame_extractor.py    <- ffmpeg frame extraction
│   ├── web_builder.py        <- Hero shot webpage generation (GSAP params)
│   ├── config.py             <- Configuration management
│   ├── progress.py           <- Progress notifications
│   ├── cache.py              <- Image caching
│   ├── batch.py              <- Batch processing
│   └── exceptions.py         <- Custom exceptions
├── templates/
│   └── hero_shot.html        <- HTML template (GSAP + CSS fallback)
├── .claude/skills/
│   ├── vibecode-agent.md     <- Workflow skill definition (11 stages)
│   └── hero-shot-builder.md  <- Webpage building skill
├── state/                    <- Runtime state (auto-generated)
├── generated/                <- Generated images, videos, frames (auto-generated)
│   ├── image1.png
│   ├── image2.png
│   └── frames/
├── projects/                 <- Generated project files
│   └── {product_name}/
│       ├── index.html
│       ├── public/frames/
│       ├── PROMPT.md
│       └── rules.json
├── input/                    <- Place product images here
├── .env                      <- API key configuration
├── requirements.txt
└── README.md
```

## Core Modules

### prompt_builder.py - Prompt Generation

```python
from agent.prompt_builder import (
    build_regenerate_prompt,      # Image1 regenerate (subject_type-based features)
    build_img2img_prompt,         # Image2 refine (movable_elements-based)
    build_video_prompt,           # Video transition prompt (transition_analysis-based)
    generate_ending_options,      # Ending options (subject_type branching)
    build_ending_prompt,          # Ending frame prompt
    apply_modification,           # Apply user modifications
)
```

All prompt functions automatically append `Avoid: ...` from confirmed_intent.exclude + image_analysis.key_features.

### color_extractor.py - Color Extraction

```python
from agent.color_extractor import extract_palette, pick_accent_color, hex_to_rgba

palette = extract_palette("generated/image1.png", num_colors=5)
accent = pick_accent_color(palette, image_analysis["style_profile"]["visual_tone"])
glow = hex_to_rgba(accent, 0.3)
```

Dependencies: Pillow (required), colorthief (optional, better quantization). Auto-fallback to visual_tone presets for low-saturation/grayscale images.

### web_builder.py - Webpage Generation

```python
from agent.web_builder import generate_player_html, get_design_direction, get_animation_preset

html = generate_player_html(
    frame_count=120, fps=24, title="Project",
    copy={"tag": "...", "title": "...", "subtitle": "...", "description": "...", "cta_primary": "...", "cta_secondary": "..."},
    font_heading="Clash Display", font_body="Satoshi",
    accent_color="#ff00ff", accent_glow="rgba(255, 0, 255, 0.3)",
    font_import="https://fonts.googleapis.com/css2?family=Satoshi...",
    anim_ease="expo.out", anim_duration="0.5", anim_stagger="0.15",
    gsap_scale="0.95", gsap_rotation="0",
)
```

### workflow.json Structure

```json
{
  "stage": "current stage",
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

## Interaction Modes

### Quick Mode (quick)
Agent decides confirmed_intent based on image_analysis. Skips intent clarification. Supports mid-flow switch to detailed mode.

### Detailed Mode (agent proposes full plan)
Agent proposes complete plan, user refines through multi-turn dialogue on 4 dimensions (effect/scene/exclude/style). Exit phrases: confirm/continue/ok/good/go/yes.

### Post-Generation Feedback Loop
ANALYZE, CONFIRM_IMAGES, BUILD_VIDEO_PROMPT, BUILD_PROJECT stages all append a unified feedback loop after showing results. Vague feedback narrows with specific direction options. Clear feedback triggers regeneration. After 5 consecutive rounds, suggests skipping and marking needs_revisit for later refinement.

## User Commands

- **Restart** - Clear state, start over
- **Pause** - Save progress, resume later
- **Skip video** - Use input images directly as frames

## FAQ

**Q: ffmpeg not found?**
A: Install ffmpeg and ensure it is in your system PATH.

**Q: Image generation failed?**
A: Check that ARK_API_KEY in `.env` is correct.

**Q: How to resume an interrupted workflow?**
A: Run `/vibecode-agent` - it reads state/workflow.json and resumes from the last stage.

**Q: GSAP loading failed?**
A: Template automatically falls back to CSS @keyframes animations. Agent will notify you.

**Q: Accent color not ideal?**
A: BUILD_PROJECT stage shows 2-3 candidate colors for selection, or you can specify manually.

## License

MIT
