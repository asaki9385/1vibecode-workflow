import os
import json
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    CANCELLED = "cancelled"


DEFAULT_STATE_DIR = "state/progress"


class ProgressTracker:
    def __init__(self, state_dir: str = DEFAULT_STATE_DIR):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)

    def _task_path(self, task_id: str) -> str:
        return os.path.join(self.state_dir, f"{task_id}.json")

    def _load(self, task_id: str) -> Optional[dict]:
        path = self._task_path(task_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _save(self, task_id: str, data: dict):
        path = self._task_path(task_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create(self, message: str, total: Optional[int] = None) -> str:
        task_id = uuid.uuid4().hex[:12]
        data = {
            "id": task_id,
            "status": TaskStatus.PENDING,
            "message": message,
            "total": total,
            "current": 0,
            "percent": None,
        }
        self._save(task_id, data)
        return task_id

    def get(self, task_id: str) -> Optional[dict]:
        return self._load(task_id)

    def update(self, task_id: str, current: Optional[int] = None, message: Optional[str] = None):
        data = self._load(task_id)
        if data is None:
            return
        if current is not None:
            data["current"] = current
        if message is not None:
            data["message"] = message
        if data["status"] == TaskStatus.PENDING:
            data["status"] = TaskStatus.RUNNING
        total = data.get("total")
        if total and total > 0:
            data["percent"] = round(data["current"] / total * 100, 1)
        self._save(task_id, data)

    def complete(self, task_id: str):
        data = self._load(task_id)
        if data is None:
            return
        data["status"] = TaskStatus.DONE
        if data.get("total"):
            data["current"] = data["total"]
        self._save(task_id, data)

    def cancel(self, task_id: str):
        data = self._load(task_id)
        if data is None:
            return
        data["status"] = TaskStatus.CANCELLED
        self._save(task_id, data)

    def list_tasks(self, status: Optional[str] = None) -> list:
        tasks = []
        for filename in os.listdir(self.state_dir):
            if not filename.endswith(".json"):
                continue
            task_id = filename[:-5]
            data = self._load(task_id)
            if data is None:
                continue
            if status and data.get("status") != status:
                continue
            tasks.append(data)
        return tasks
