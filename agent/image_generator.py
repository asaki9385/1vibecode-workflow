import os
import requests
from dotenv import load_dotenv

load_dotenv()

ARK_API_KEY = os.getenv("ARK_API_KEY")
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


def generate_image(prompt: str, output_path: str) -> str:
    """调用 Seedream API 生成图片，返回保存路径"""
    if not ARK_API_KEY:
        raise ValueError("缺少 ARK_API_KEY，请在 .env 文件中配置")

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

    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()

    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    return output_path


def apply_modification(original_prompt: str, modification: str) -> str:
    """合并原 Prompt 和修改描述，生成新 Prompt"""
    return f"{original_prompt}, {modification}"
