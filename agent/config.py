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

# Data directory for all intermediate files
DATA_DIR: Path = PROJECT_ROOT / "data"

# Default project name (can be overridden per session)
DEFAULT_PROJECT: str = os.getenv("VIBECODE_PROJECT", "default")

def get_project_dir(project_name: str = None) -> Path:
    """Get project-specific data directory."""
    name = project_name or DEFAULT_PROJECT
    return DATA_DIR / name

def get_input_dir(project_name: str = None) -> Path:
    """Get input directory for a project."""
    return get_project_dir(project_name) / "input"

def get_generated_dir(project_name: str = None) -> Path:
    """Get generated directory for a project."""
    return get_project_dir(project_name) / "generated"

def get_state_dir(project_name: str = None) -> Path:
    """Get state directory for a project."""
    return get_project_dir(project_name) / "state"

def get_projects_dir() -> Path:
    """Get projects output directory (for built websites)."""
    return PROJECT_ROOT / "projects"

def get_templates_dir() -> Path:
    """Get templates directory."""
    return PROJECT_ROOT / "templates"

# Legacy paths (for backward compatibility)
STATE_DIR: Path = PROJECT_ROOT / "state"
WORKFLOW_STATE_FILE: Path = STATE_DIR / "workflow.json"
BATCH_STATE_FILE: Path = STATE_DIR / "batch.json"
CACHE_STATE_DIR: Path = STATE_DIR / "cache"
PROGRESS_STATE_DIR: Path = STATE_DIR / "progress"

GENERATED_DIR: Path = PROJECT_ROOT / "generated"
CACHE_IMAGE_DIR: Path = GENERATED_DIR / "cache"
PROJECTS_DIR: Path = PROJECT_ROOT / "projects"

TEMPLATES_DIR: Path = PROJECT_ROOT / "templates"


def ensure_project_dirs(project_name: str = None):
    """Create all necessary directories for a project."""
    dirs = [
        get_project_dir(project_name),
        get_input_dir(project_name),
        get_generated_dir(project_name),
        get_generated_dir(project_name) / "frames",
        get_generated_dir(project_name) / "cache",
        get_state_dir(project_name),
        get_state_dir(project_name) / "cache",
        get_state_dir(project_name) / "progress",
        get_projects_dir(),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def migrate_legacy_data(project_name: str = None):
    """Migrate data from legacy directories to new data/ structure.
    
    This moves files from the old flat structure to the new project-based structure.
    """
    import shutil
    
    name = project_name or DEFAULT_PROJECT
    new_input = get_input_dir(name)
    new_generated = get_generated_dir(name)
    new_state = get_state_dir(name)
    
    # Migrate input/
    old_input = PROJECT_ROOT / "input"
    if old_input.exists() and old_input.is_dir():
        for f in old_input.iterdir():
            if f.is_file():
                dest = new_input / f.name
                if not dest.exists():
                    shutil.move(str(f), str(dest))
                    print(f"Migrated: {f.name} -> data/{name}/input/")
    
    # Migrate generated/
    old_generated = PROJECT_ROOT / "generated"
    if old_generated.exists() and old_generated.is_dir():
        for f in old_generated.iterdir():
            if f.is_file():
                dest = new_generated / f.name
                if not dest.exists():
                    shutil.move(str(f), str(dest))
                    print(f"Migrated: {f.name} -> data/{name}/generated/")
        # Migrate frames subdirectory
        old_frames = old_generated / "frames"
        if old_frames.exists() and old_frames.is_dir():
            new_frames = new_generated / "frames"
            for f in old_frames.iterdir():
                if f.is_file():
                    dest = new_frames / f.name
                    if not dest.exists():
                        shutil.move(str(f), str(dest))
    
    # Migrate state/
    old_state = PROJECT_ROOT / "state"
    if old_state.exists() and old_state.is_dir():
        for f in old_state.iterdir():
            if f.is_file():
                dest = new_state / f.name
                if not dest.exists():
                    shutil.move(str(f), str(dest))
                    print(f"Migrated: {f.name} -> data/{name}/state/")
