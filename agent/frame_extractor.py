import os
import sys
import shutil
import subprocess


def extract_frames(video_path: str, output_dir: str, fps: int = 24) -> int:
    """将视频拆解为 JPEG 帧序列，返回总帧数

    Args:
        video_path: 视频文件路径
        output_dir: 帧输出目录
        fps: 提取帧率
    """
    if not shutil.which("ffmpeg"):
        print("❌ 未找到 ffmpeg，请先安装：")
        print("   macOS:   brew install ffmpeg")
        print("   Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("   Linux:   sudo apt install ffmpeg")
        sys.exit(1)

    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在：{video_path}")
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
