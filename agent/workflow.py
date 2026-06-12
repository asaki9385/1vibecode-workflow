import os
import json
import logging
from pathlib import Path
from typing import Any, Optional
import portalocker

logger = logging.getLogger(__name__)

DEFAULT_STATE_FILE = "state/workflow.json"

STAGES = [
    "INIT",
    "ANALYZE",
    "CONFIRM_PRODUCT",
    "GENERATE",
    "CONFIRM_IMAGES",
    "BUILD_VIDEO_PROMPT",
    "WAIT_VIDEO",
    "EXTRACT_FRAMES",
    "BUILD_PROJECT",
    "DONE"
]

class Workflow:
    def __init__(self, state_file: str = DEFAULT_STATE_FILE, project_name: str = None):
        """Initialize workflow.
        
        Args:
            state_file: Path to state file (legacy support)
            project_name: Project name for data/ structure
        """
        if project_name:
            from agent.config import get_state_dir, ensure_project_dirs
            ensure_project_dirs(project_name)
            self.state_file = str(get_state_dir(project_name) / "workflow.json")
            self.project_name = project_name
        else:
            self.state_file = state_file
            self.project_name = None
        self._data = self._load()

    def _load(self) -> dict:
        """Load state from file or create default"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    portalocker.lock(f, portalocker.LOCK_SH)
                    try:
                        data = json.load(f)
                        if not isinstance(data, dict):
                            return {"stage": "INIT"}
                        return data
                    finally:
                        portalocker.unlock(f)
            except (json.JSONDecodeError, IOError):
                return {"stage": "INIT"}
        return {"stage": "INIT"}

    def save(self):
        """Persist current state to file"""
        dir_name = os.path.dirname(self.state_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            try:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            finally:
                portalocker.unlock(f)

    def get_stage(self) -> str:
        """Get current workflow stage"""
        return self._data.get("stage", "INIT")

    def set_stage(self, stage: str):
        """Set current workflow stage"""
        if stage not in STAGES:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {STAGES}")
        current = self.get_stage()
        current_idx = STAGES.index(current)
        target_idx = STAGES.index(stage)
        if target_idx > current_idx + 1:
            raise ValueError(
                f"Cannot skip stages: {current} -> {stage}. "
                f"Must complete intermediate stages first."
            )
        logger.info("Stage transition: %s -> %s", current, stage)
        self._data["stage"] = stage
        self.save()

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data by key"""
        return self._data.get(key, default)

    def set_data(self, key: str, value: Any):
        """Set data by key and auto-save"""
        self._data[key] = value
        self.save()

    def reset(self):
        """Reset workflow to initial state"""
        logger.info("Workflow reset from stage %s", self.get_stage())
        self._data = {"stage": "INIT"}
        self.save()
    
    def get_input_path(self, filename: str) -> str:
        """Get full path for input file."""
        from agent.config import get_input_dir
        return str(get_input_dir(self.project_name) / filename)
    
    def get_generated_path(self, filename: str) -> str:
        """Get full path for generated file."""
        from agent.config import get_generated_dir
        return str(get_generated_dir(self.project_name) / filename)
    
    def get_frames_dir(self) -> str:
        """Get frames directory path."""
        from agent.config import get_generated_dir
        return str(get_generated_dir(self.project_name) / "frames")
