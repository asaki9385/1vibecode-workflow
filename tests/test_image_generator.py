import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from agent.image_generator import generate_image, apply_modification

@pytest.fixture
def mock_env(monkeypatch):
    """Set test API key"""
    monkeypatch.setenv("ARK_API_KEY", "test-key")

@patch("agent.image_generator.requests.post")
@patch("agent.image_generator.requests.get")
def test_generate_image_success(mock_get, mock_post, tmp_path, mock_env):
    """Should download and save image on success"""
    # Mock API response
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"data": [{"url": "https://example.com/img.png"}]}
    )
    mock_get.return_value = MagicMock(
        status_code=200,
        content=b"fake-image-data"
    )

    output_path = str(tmp_path / "test.png")
    result = generate_image("test prompt", output_path)

    assert result == output_path
    assert os.path.exists(output_path)
    with open(output_path, "rb") as f:
        assert f.read() == b"fake-image-data"

@patch("agent.image_generator.requests.post")
def test_generate_image_api_error(mock_post, tmp_path, mock_env):
    """Should raise on API error"""
    mock_post.return_value = MagicMock(
        status_code=400,
        text="Bad request"
    )

    with pytest.raises(Exception, match="图片生成失败"):
        generate_image("test", str(tmp_path / "fail.png"))

def test_apply_modification():
    """Should merge original prompt with modification"""
    original = "A smart doorbell, dark background, cinematic"
    modification = "white background"
    result = apply_modification(original, modification)
    assert "white background" in result
    assert "smart doorbell" in result

def test_generate_image_no_api_key(monkeypatch, tmp_path):
    """Should raise ValueError when API key is missing"""
    monkeypatch.delenv("ARK_API_KEY", raising=False)
    # Need to reload module to pick up the missing env var
    # Patch load_dotenv at source to prevent .env file from restoring the var
    import importlib
    import agent.image_generator
    with patch("dotenv.load_dotenv"):
        importlib.reload(agent.image_generator)

    with pytest.raises(ValueError, match="缺少 ARK_API_KEY"):
        agent.image_generator.generate_image("test", str(tmp_path / "fail.png"))

@patch("agent.image_generator.requests.post")
@patch("agent.image_generator.requests.get")
def test_generate_image_download_error(mock_get, mock_post, tmp_path, mock_env):
    """Should raise when image download fails"""
    # Reload module to restore ARK_API_KEY after no_api_key test may have cleared it
    import importlib
    import agent.image_generator
    importlib.reload(agent.image_generator)

    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"data": [{"url": "https://example.com/img.png"}]}
    )
    mock_get.return_value = MagicMock(
        status_code=404,
        raise_for_status=MagicMock(side_effect=requests.exceptions.HTTPError("404 Not Found"))
    )

    with pytest.raises(requests.exceptions.HTTPError):
        generate_image("test", str(tmp_path / "fail.png"))
