"""Centralized configuration for the agent package."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ARK_API_KEY: str = os.getenv("ARK_API_KEY", "")
SEEDREAM_MODEL: str = os.getenv("SEEDREAM_MODEL", "doubao-seedream-5-0-260128")
BASE_URL: str = os.getenv("BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "60"))
FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "")

STATE_DIR: Path = PROJECT_ROOT / "state"
WORKFLOW_STATE_FILE: Path = STATE_DIR / "workflow.json"
BATCH_STATE_FILE: Path = STATE_DIR / "batch.json"
CACHE_STATE_DIR: Path = STATE_DIR / "cache"
PROGRESS_STATE_DIR: Path = STATE_DIR / "progress"

GENERATED_DIR: Path = PROJECT_ROOT / "generated"
CACHE_IMAGE_DIR: Path = GENERATED_DIR / "cache"
PROJECTS_DIR: Path = PROJECT_ROOT / "projects"

TEMPLATES_DIR: Path = PROJECT_ROOT / "templates"
