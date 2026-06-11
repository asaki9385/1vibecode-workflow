import os
import time
import base64
from typing import Optional

import requests
from dotenv import load_dotenv

from agent.exceptions import ImageGenerationError
from agent.prompt_builder import apply_modification  # noqa: F401 – re-export for backward compat

load_dotenv()

ARK_API_KEY = os.getenv("ARK_API_KEY")
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))

SUPPORTED_FORMATS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0


def validate_image_format(image_path: str) -> bool:
    """验证图片格式是否受支持"""
    ext = os.path.splitext(image_path)[1].lower()
    return ext in SUPPORTED_FORMATS


def _image_to_data_url(image_path: str) -> str:
    """将本地图片转换为 base64 data URL"""
    ext = os.path.splitext(image_path)[1].lower()
    mime_map: dict[str, str] = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
    }
    mime = mime_map.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """Execute an HTTP request with retry and exponential backoff.

    Only retries on transient errors (connection, timeout). HTTP status errors
    are raised immediately.
    """
    func = getattr(requests, method)
    last_exc: Optional[Exception] = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = func(url, **kwargs)
            resp.raise_for_status()
            return resp
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
    raise last_exc  # type: ignore[misc]


def generate_image(prompt: str, output_path: str, reference_image: Optional[str] = None) -> str:
    """调用 Seedream API 生成图片，返回保存路径

    Args:
        prompt: 图片描述
        output_path: 保存路径
        reference_image: 参考图URL或本地路径（用于图生图模式）
    """
    if not ARK_API_KEY:
        raise ValueError("缺少 ARK_API_KEY，请在 .env 文件中配置")

    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload: dict = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "size": "2K",
        "response_format": "url",
        "sequential_image_generation": "disabled",
        "watermark": False,
        "stream": False
    }

    if reference_image:
        if not reference_image.startswith("http") and not validate_image_format(reference_image):
            raise ValueError(f"不支持的图片格式: {os.path.splitext(reference_image)[1]}。支持的格式: {', '.join(sorted(SUPPORTED_FORMATS))}")
        if reference_image.startswith("http"):
            payload["image"] = reference_image
        else:
            payload["image"] = _image_to_data_url(reference_image)

    resp = _request_with_retry(
        "post",
        f"{BASE_URL}/images/generations",
        headers=headers,
        json=payload,
        timeout=API_TIMEOUT,
    )

    if resp.status_code != 200:
        raise ImageGenerationError(f"图片生成失败 [{resp.status_code}]: {resp.text}")

    image_url = resp.json()["data"][0]["url"]

    img_resp = _request_with_retry("get", image_url, timeout=API_TIMEOUT)

    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    return output_path
