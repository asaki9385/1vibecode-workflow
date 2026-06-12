import os
import json
import logging
from pathlib import Path
from typing import Any, Optional
import portalocker

logger = logging.getLogger(__name__)

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
    def __init__(self, state_file: str = None):
        """Initialize workflow using working directories."""
        from agent.config import STATE_DIR, WORKFLOW_STATE_FILE, ensure_working_dirs
        
        ensure_working_dirs()
        self.state_file = state_file or str(WORKFLOW_STATE_FILE)
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
        
        # Archive workflow when DONE
        if stage == "DONE":
            self._archive()

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
    
    def _archive(self):
        """Archive completed workflow to data/{project_name}/"""
        from agent.config import archive_completed_workflow
        
        # Use product name from image_analysis or default
        analysis = self._data.get("image_analysis", {})
        subject = analysis.get("subject", "project")
        # Clean subject for use as directory name
        project_name = subject.replace(" ", "_").replace("/", "_")[:50]
        
        archive_completed_workflow(project_name)
    
    def get_input_path(self, filename: str) -> str:
        """Get full path for input file."""
        from agent.config import INPUT_DIR
        return str(INPUT_DIR / filename)
    
    def get_generated_path(self, filename: str) -> str:
        """Get full path for generated file."""
        from agent.config import GENERATED_DIR
        return str(GENERATED_DIR / filename)
    
    def get_frames_dir(self) -> str:
        """Get frames directory path."""
        from agent.config import GENERATED_DIR
        return str(GENERATED_DIR / "frames")
