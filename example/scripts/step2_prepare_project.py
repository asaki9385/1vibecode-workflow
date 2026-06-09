"""
Step 2: 生成 AI IDE 项目文件

将帧图片整理成项目结构，并生成可直接粘贴的 AI 提示词文档

用法：
    python scripts/step2_prepare_project.py \
        --product "智能咖啡杯" \
        --desc "具有温度控制和智能提醒功能的高端咖啡杯"

输入：
    temp/frames/（Step 1 生成的帧图片）

输出：
    projects/{产品名}/
    ├── public/frames/    ← 帧图片
    ├── PROMPT.md         ← 直接粘贴给 AI IDE 的提示词
    └── README.md         ← 操作说明
"""

import os
import sys
import json
import shutil
import argparse


def prepare_project(frames_dir: str, product_name: str, product_desc: str,
                    output_dir: str = "projects") -> str:
    """生成完整项目结构，返回项目目录路径"""

    # 检查帧目录
    if not os.path.exists(frames_dir):
        print(f"❌ 帧目录不存在：{frames_dir}")
        print(f"   请先运行 step1_extract_frames.py")
        sys.exit(1)

    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith(".jpg")])
    if not frame_files:
        print(f"❌ 帧目录中没有 jpg 文件：{frames_dir}")
        sys.exit(1)

    total_frames = len(frame_files)
    last_frame   = frame_files[-1]

    # 创建项目目录
    project_dir = os.path.join(output_dir, product_name)
    frames_dest = os.path.join(project_dir, "public", "frames")
    os.makedirs(frames_dest, exist_ok=True)

    # 复制帧图片
    for filename in frame_files:
        shutil.copy2(os.path.join(frames_dir, filename),
                     os.path.join(frames_dest, filename))
    print(f"  已复制 {total_frames} 张帧图片 → {frames_dest}")

    # 生成编码规范
    rules = {
        "rules": [
            "始终使用语义化 HTML5 标签（header/main/section/footer）",
            "间距使用 8px 网格系统，所有值为 8 的倍数",
            "所有动画添加 prefers-reduced-motion 支持",
            "颜色使用 CSS 自定义变量（--color-*）统一管理",
            "图片添加 loading='lazy' 属性",
            "代码注释使用中文"
        ]
    }
    with open(os.path.join(project_dir, "rules.json"), "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)

    # 生成提示词文档
    prompt_md = _build_prompt_md(product_name, product_desc, total_frames, last_frame)
    with open(os.path.join(project_dir, "PROMPT.md"), "w", encoding="utf-8") as f:
        f.write(prompt_md)

    # 生成 README
    readme = _build_readme(product_name, total_frames)
    with open(os.path.join(project_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    return project_dir


def _build_prompt_md(product_name, product_desc, total_frames, last_frame):
    return f"""# {product_name} — 网站构建提示词

> 使用方法：用 Cursor / MarsCode 打开此文件夹，按顺序将每步提示词粘贴给 AI 执行

---

## 第一步：建站基础结构

请根据以下产品信息，构建一个完整的单页产品展示网站：

**产品名称**：{product_name}
**产品描述**：{product_desc}

技术要求：
- 纯 HTML + CSS + JavaScript，不依赖任何外部框架
- 遵循 rules.json 中的编码规范
- 整体使用深色主题（背景 #0a0a0a）

页面结构（从上到下）：
1. 导航栏：左侧产品名称，右侧深/浅色切换按钮
2. Hero 区域：先用 `<section id="hero"></section>` 占位，高度 100vh，背景 #111
3. 产品特点区：3 列卡片，展示 3 个核心卖点（根据产品描述自动生成内容）
4. 用户评价区：3 条评价，带头像占位、姓名、评价文字
5. CTA 区：大标题 + "立即体验" 按钮
6. 页脚：产品名称 + 版权

视觉要求：
- 标题字体：Google Fonts "Playfair Display"
- 正文字体：Google Fonts "Inter"
- 页面元素进入时有 fadeInUp 动画，各元素错开 0.1s

---

## 第二步：Hero 滚动帧动画

将 Hero 区域替换为滚动触发的帧动画。

帧图片路径：`public/frames/frame_0001.jpg` 到 `public/frames/{last_frame}`
总帧数：**{total_frames} 帧**

实现要求：

```
核心逻辑：
1. 页面加载后预加载所有 {total_frames} 张帧图片
2. Hero 容器高度设为 300vh（用于滚动触发范围）
3. 画布（canvas 或 img）在视口内 sticky 固定，覆盖全屏
4. 监听滚动事件，将滚动进度（0%~100%）映射为帧索引（0~{total_frames - 1}）
5. 用 requestAnimationFrame 更新画面，确保流畅
6. 全部帧加载完成前显示加载进度条
```

注意：
- 图片用 object-fit: cover 铺满全屏
- 预加载期间显示进度百分比（如"加载中 47%"）
- 移动端降级：屏幕宽度 < 768px 时改为静态展示第一帧

---

## 第三步：深色/浅色模式切换

为导航栏右侧的切换按钮添加功能：

- 切换时所有颜色通过 CSS 变量平滑过渡（transition 0.3s）
- 用 localStorage 记忆用户选择
- 默认跟随系统（prefers-color-scheme）
- 浅色模式：背景 #f5f5f5，文字 #111

---

## 第四步：细节优化

1. 加载优化：帧动画预加载完成前，用骨架屏代替 Hero 区域
2. 导航栏：页面滚动超过 80px 后，背景变为半透明毛玻璃效果（backdrop-filter: blur(12px)）
3. CTA 按钮：点击时添加水波纹（ripple）效果
4. 评价区：在移动端支持左右滑动切换
5. 整体检查：确保在 375px 和 1440px 宽度下布局均正常
"""


def _build_readme(product_name, total_frames):
    return f"""# {product_name} — VibeCode 项目

由 VibeCode 工作流自动生成，共 {total_frames} 帧动画图片。

## 使用步骤

1. 用 **Cursor** 或 **MarsCode** 打开此文件夹
2. 打开 `PROMPT.md`，将**第一步**的内容粘贴给 AI → 生成基础页面
3. 依次执行第二步（动画）、第三步（深浅色）、第四步（优化）
4. 在浏览器打开 `index.html`，**滚动页面**查看帧动画效果

## 文件说明

```
{product_name}/
├── public/
│   └── frames/      ← {total_frames} 张帧图片
├── rules.json        ← AI 编码规范
├── PROMPT.md         ← AI 提示词（按步骤执行）
└── README.md         ← 本文件
```

## 注意

- 第二步完成后需要**实际滚动**才能看到动画
- 帧图片较多时预加载需要几秒，属正常现象
- 动画触发范围是 300vh（3 倍屏幕高度的滚动距离）
"""


def main():
    parser = argparse.ArgumentParser(description="生成 AI IDE 项目文件 - Step 2")
    parser.add_argument("--product",   required=True,          help="产品名称")
    parser.add_argument("--desc",      required=True,          help="产品描述")
    parser.add_argument("--frames",    default="temp/frames",  help="帧图片目录（默认 temp/frames）")
    parser.add_argument("--output",    default="projects",     help="项目输出目录（默认 projects/）")
    args = parser.parse_args()

    print(f"\n📁 生成 AI IDE 项目文件")
    print(f"   产品：{args.product}\n")

    project_dir = prepare_project(args.frames, args.product, args.desc, args.output)

    print(f"\n  ✅ 项目文件生成完成！")
    print(f"\n{'='*55}")
    print(f"  🎉 全流程完成！")
    print(f"{'='*55}")
    print(f"\n  📁 项目目录：{project_dir}")
    print(f"\n  ➡️  最后一步：")
    print(f"     1. 用 Cursor / MarsCode 打开 {project_dir}/")
    print(f"     2. 打开 PROMPT.md，按步骤将提示词粘贴给 AI")
    print(f"     3. 在浏览器预览，滚动页面查看动画效果\n")


if __name__ == "__main__":
    main()
