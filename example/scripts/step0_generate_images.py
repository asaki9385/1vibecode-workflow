"""
Step 0: 调用 Seedream 5.0 API 生成两张关键帧图片

用法：
    python scripts/step0_generate_images.py \
        --product "智能咖啡杯" \
        --desc "具有温度控制和智能提醒功能的高端咖啡杯" \
        --style "白色背景，商业产品摄影，高清"

生成结果：
    input/img1.jpg  ← 静态图（产品完整精致状态）
    input/img2.jpg  ← 动态图（产品爆炸/展开状态）

完成后：
    将两张图上传到即梦AI或Seedance网页版，生成首尾帧过渡视频
    下载视频后，运行 step1_extract_frames.py
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

ARK_API_KEY   = os.getenv("ARK_API_KEY")
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
BASE_URL       = "https://ark.cn-beijing.volces.com/api/v3"


def generate_image(prompt: str, output_path: str) -> str:
    """调用 Seedream 5.0 生成一张图片并保存到本地"""

    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "size": "2K",
        "response_format": "url",
        "sequential_image_generation": "disabled",
        "watermark": False,
        "stream": False
    }

    resp = requests.post(
        f"{BASE_URL}/images/generations",
        headers=headers,
        json=payload,
        timeout=60
    )

    if resp.status_code != 200:
        raise Exception(f"图片生成失败 [{resp.status_code}]: {resp.text}")

    image_url = resp.json()["data"][0]["url"]

    # 下载图片
    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    return output_path


def main():
    if not ARK_API_KEY:
        print("❌ 缺少 ARK_API_KEY，请在 .env 文件中配置")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Seedream 图片生成 - Step 0")
    parser.add_argument("--product", required=True, help="产品名称，如：智能咖啡杯")
    parser.add_argument("--desc",    required=True, help="产品描述，如：具有温度控制功能")
    parser.add_argument("--style",   default="白色背景，商业产品摄影，高清，精致",
                                     help="画面风格（两张图共用）")
    parser.add_argument("--out",     default="input", help="图片输出目录（默认 input/）")
    args = parser.parse_args()

    # 构建两张图的提示词
    prompt_static = (
        f"{args.product}，{args.desc}，"
        f"产品完整精致状态，正面展示，{args.style}"
    )
    prompt_dynamic = (
        f"{args.product}，{args.desc}，"
        f"产品爆炸分解展示，零件四散飞溅，动感十足，{args.style}"
    )

    print("\n📸 开始生成关键帧图片（Seedream 5.0）")
    print(f"   产品：{args.product}")
    print(f"   风格：{args.style}\n")

    # 生成静态图
    print("  生成 img1.jpg（静态图）...")
    print(f"  提示词：{prompt_static[:60]}...")
    path1 = generate_image(prompt_static, os.path.join(args.out, "img1.jpg"))
    print(f"  ✅ 已保存：{path1}")

    # 生成动态图
    print("\n  生成 img2.jpg（动态图）...")
    print(f"  提示词：{prompt_dynamic[:60]}...")
    path2 = generate_image(prompt_dynamic, os.path.join(args.out, "img2.jpg"))
    print(f"  ✅ 已保存：{path2}")

    print("\n" + "="*55)
    print("  ✅ 图片生成完成！")
    print("="*55)
    print(f"\n  📁 图片位置：")
    print(f"     静态图 → {path1}")
    print(f"     动态图 → {path2}")
    print(f"\n  ➡️  下一步（手动）：")
    print(f"     1. 打开即梦AI：https://jimeng.jianying.com")
    print(f"        或火山方舟视频生成：https://console.volcengine.com/ark")
    print(f"     2. 使用「首尾帧生视频」功能")
    print(f"        首帧上传：{path1}")
    print(f"        尾帧上传：{path2}")
    print(f"        提示词建议：{args.product}从精致完整到爆炸展开的流畅过渡，电影级，动感")
    print(f"     3. 下载生成的视频，保存到项目根目录，命名为 transition.mp4")
    print(f"     4. 运行下一步：python scripts/step1_extract_frames.py\n")


if __name__ == "__main__":
    main()
