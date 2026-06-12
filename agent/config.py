"""Centralized configuration for the agent package."""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ARK_API_KEY: str = os.getenv("ARK_API_KEY", "")
SEEDREAM_MODEL: str = os.getenv("SEEDREAM_MODEL", "doubao-seedream-5-0-260128")
BASE_URL: str = os.getenv("BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "60"))
FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "")

# Working directories (current session)
INPUT_DIR: Path = PROJECT_ROOT / "input"
GENERATED_DIR: Path = PROJECT_ROOT / "generated"
STATE_DIR: Path = PROJECT_ROOT / "state"
TEMP_DIR: Path = PROJECT_ROOT / "temp"

# Archive directory (completed workflows)
DATA_DIR: Path = PROJECT_ROOT / "data"

# Projects output directory (built websites)
PROJECTS_DIR: Path = PROJECT_ROOT / "projects"

# Templates
TEMPLATES_DIR: Path = PROJECT_ROOT / "templates"

# State files
WORKFLOW_STATE_FILE: Path = STATE_DIR / "workflow.json"
BATCH_STATE_FILE: Path = STATE_DIR / "batch.json"
CACHE_STATE_DIR: Path = STATE_DIR / "cache"
PROGRESS_STATE_DIR: Path = STATE_DIR / "progress"
CACHE_IMAGE_DIR: Path = GENERATED_DIR / "cache"


def get_archive_dir(project_name: str) -> Path:
    """Get archive directory for a completed project."""
    return DATA_DIR / project_name


def archive_completed_workflow(project_name: str):
    """Archive a completed workflow to data/{project_name}/
    
    Called when workflow reaches DONE stage.
    Copies input/, generated/, state/ to data/{project_name}/
    """
    archive_dir = get_archive_dir(project_name)
    archive_input = archive_dir / "input"
    archive_generated = archive_dir / "generated"
    archive_state = archive_dir / "state"
    
    # Create directories
    for d in [archive_dir, archive_input, archive_generated, archive_state]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy input files
    if INPUT_DIR.exists():
        for f in INPUT_DIR.iterdir():
            if f.is_file():
                dest = archive_input / f.name
                if not dest.exists():
                    shutil.copy2(str(f), str(dest))
    
    # Copy generated files
    if GENERATED_DIR.exists():
        for f in GENERATED_DIR.iterdir():
            if f.is_file():
                dest = archive_generated / f.name
                if not dest.exists():
                    shutil.copy2(str(f), str(dest))
        # Copy frames subdirectory
        frames_dir = GENERATED_DIR / "frames"
        if frames_dir.exists():
            archive_frames = archive_generated / "frames"
            archive_frames.mkdir(exist_ok=True)
            for f in frames_dir.iterdir():
                if f.is_file():
                    dest = archive_frames / f.name
                    if not dest.exists():
                        shutil.copy2(str(f), str(dest))
    
    # Copy state files
    if STATE_DIR.exists():
        for f in STATE_DIR.iterdir():
            if f.is_file():
                dest = archive_state / f.name
                if not dest.exists():
                    shutil.copy2(str(f), str(dest))
    
    print(f"Workflow archived to data/{project_name}/")


def ensure_working_dirs():
    """Ensure working directories exist."""
    for d in [INPUT_DIR, GENERATED_DIR, STATE_DIR, TEMP_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / "frames").mkdir(exist_ok=True)
    (GENERATED_DIR / "cache").mkdir(exist_ok=True)
