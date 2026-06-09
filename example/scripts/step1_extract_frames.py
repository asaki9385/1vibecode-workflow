"""
Step 1: 视频拆帧

将你从即梦AI / Seedance网页版下载的过渡视频，拆解为帧序列

用法：
    python scripts/step1_extract_frames.py
    python scripts/step1_extract_frames.py --video my_video.mp4 --fps 24

输入：
    transition.mp4（或通过 --video 指定路径）

输出：
    temp/frames/frame_0001.jpg, frame_0002.jpg ...

完成后运行：
    python scripts/step2_prepare_project.py --product "产品名" --desc "产品描述"
"""

import os
import sys
import shutil
import argparse
import subprocess


def extract_frames(video_path: str, output_dir: str, fps: int = 24) -> int:
    """将视频拆解为 JPEG 帧序列，返回总帧数"""

    # 检查 ffmpeg
    if not shutil.which("ffmpeg"):
        print("❌ 未找到 ffmpeg，请先安装：")
        print("   macOS:   brew install ffmpeg")
        print("   Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("   Linux:   sudo apt install ffmpeg")
        sys.exit(1)

    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在：{video_path}")
        print(f"   请先完成手动步骤，将视频保存为 {video_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-q:v", "2",
        "-y",
        output_pattern
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise Exception(f"ffmpeg 执行失败：\n{result.stderr[-500:]}")

    frames = sorted([f for f in os.listdir(output_dir) if f.endswith(".jpg")])
    return len(frames)


def main():
    parser = argparse.ArgumentParser(description="视频拆帧 - Step 1")
    parser.add_argument("--video",  default="transition.mp4", help="视频文件路径（默认 transition.mp4）")
    parser.add_argument("--fps",    type=int, default=24,      help="提取帧率（默认 24）")
    parser.add_argument("--outdir", default="temp/frames",     help="帧输出目录（默认 temp/frames）")
    args = parser.parse_args()

    print(f"\n🖼️  开始拆帧")
    print(f"   视频：{args.video}")
    print(f"   帧率：{args.fps} fps\n")

    total = extract_frames(args.video, args.outdir, args.fps)

    estimated_seconds = total / args.fps
    print(f"  ✅ 拆帧完成！")
    print(f"     总帧数：{total} 帧")
    print(f"     视频时长约：{estimated_seconds:.1f} 秒")
    print(f"     帧目录：{args.outdir}")
    print(f"\n  ➡️  下一步，运行：")
    print(f"     python scripts/step2_prepare_project.py \\")
    print(f'         --product "你的产品名称" \\')
    print(f'         --desc "你的产品描述"\n')


if __name__ == "__main__":
    main()
