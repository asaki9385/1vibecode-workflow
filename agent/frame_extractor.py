import os
import shutil
import subprocess

from agent.exceptions import FFmpegNotFoundError, FFmpegExecutionError

FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "")


def _find_ffmpeg() -> str:
    """Locate ffmpeg binary: env var → hardcoded path → system PATH."""
    if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
        return FFMPEG_PATH
    found = shutil.which("ffmpeg")
    if found:
        return found
    return ""


def extract_frames(video_path: str, output_dir: str, fps: int = 24) -> int:
    """将视频拆解为 JPEG 帧序列，返回总帧数

    Args:
        video_path: 视频文件路径
        output_dir: 帧输出目录
        fps: 提取帧率，必须大于0
    """
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")

    ffmpeg_cmd = _find_ffmpeg()
    if not ffmpeg_cmd:
        raise FFmpegNotFoundError(
            "未找到 ffmpeg，请先安装：\n"
            "  macOS:   brew install ffmpeg\n"
            "  Windows: https://www.gyan.dev/ffmpeg/builds/\n"
            "  Linux:   sudo apt install ffmpeg\n"
            "  或设置环境变量 FFMPEG_PATH 指向 ffmpeg 可执行文件"
        )

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在：{video_path}")

    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    cmd = [
        ffmpeg_cmd,
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-q:v", "2",
        "-y",
        output_pattern
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise FFmpegExecutionError(f"ffmpeg 执行失败：\n{result.stderr[-500:]}")

    frames = sorted([f for f in os.listdir(output_dir) if f.endswith(".jpg")])
    return len(frames)
