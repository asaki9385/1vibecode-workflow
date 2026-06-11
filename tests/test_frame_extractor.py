import os
import pytest
from unittest.mock import patch, MagicMock
from agent.frame_extractor import extract_frames
from agent.exceptions import FFmpegNotFoundError

@patch("agent.frame_extractor.subprocess.run")
@patch("agent.frame_extractor.shutil.which", return_value="/usr/bin/ffmpeg")
def test_extract_frames_success(mock_which, mock_run, tmp_path):
    """Should call ffmpeg and return frame count"""
    # Create fake frame files
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    for i in range(5):
        (frames_dir / f"frame_{i:04d}.jpg").touch()

    mock_run.return_value = MagicMock(returncode=0)

    video_path = str(tmp_path / "test.mp4")
    output_dir = str(frames_dir)

    # Create fake video file
    with open(video_path, "w") as f:
        f.write("fake video")

    count = extract_frames(video_path, output_dir, fps=24)
    assert count == 5

@patch("agent.frame_extractor.shutil.which", return_value=None)
@patch("agent.frame_extractor.os.path.exists", return_value=False)
def test_extract_frames_no_ffmpeg(mock_exists, mock_which):
    """Should raise FFmpegNotFoundError when ffmpeg not found"""
    with pytest.raises(FFmpegNotFoundError, match="未找到 ffmpeg"):
        extract_frames("test.mp4", "output", fps=24)

@patch("agent.frame_extractor.shutil.which", return_value="/usr/bin/ffmpeg")
def test_extract_frames_no_video(mock_which):
    """Should raise FileNotFoundError when video file doesn't exist"""
    with pytest.raises(FileNotFoundError, match="视频文件不存在"):
        extract_frames("nonexistent.mp4", "output", fps=24)

def test_extract_frames_invalid_fps():
    """Should raise ValueError for invalid fps"""
    with pytest.raises(ValueError, match="fps must be positive"):
        extract_frames("test.mp4", "output", fps=0)

    with pytest.raises(ValueError, match="fps must be positive"):
        extract_frames("test.mp4", "output", fps=-1)
