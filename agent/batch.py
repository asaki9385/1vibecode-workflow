import os
import json
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

DEFAULT_STATE_FILE = "state/batch.json"

class BatchStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class BatchItem:
    image_path: str
    status: BatchStatus = BatchStatus.PENDING

class BatchWorkflow:
    def __init__(self, state_file: str = DEFAULT_STATE_FILE):
        self.state_file = state_file
        self._items: List[BatchItem] = []
        self._load()

    def _load(self):
        """Load state from file or initialize empty"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "items" in data:
                        self._items = [
                            BatchItem(
                                image_path=item["image_path"],
                                status=BatchStatus(item["status"])
                            )
                            for item in data["items"]
                        ]
                    else:
                        self._items = []
            except (json.JSONDecodeError, IOError):
                self._items = []
        else:
            self._items = []

    def _save(self):
        """Persist current state to file"""
        dir_name = os.path.dirname(self.state_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        data = {
            "items": [asdict(item) for item in self._items]
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create(self, images: List[str]) -> List[BatchItem]:
        """Create a new batch with list of image paths"""
        if not images:
            raise ValueError("At least one image required")
        self._items = [BatchItem(image_path=img) for img in images]
        self._save()
        return self._items

    def get_next(self) -> Optional[BatchItem]:
        """Get next pending item in order"""
        for item in self._items:
            if item.status == BatchStatus.PENDING:
                return item
        return None

    def get_item(self, image_path: str) -> Optional[BatchItem]:
        """Get specific item by image path"""
        for item in self._items:
            if item.image_path == image_path:
                return item
        return None

    def complete(self, image_path: str) -> bool:
        """Mark item as completed"""
        item = self.get_item(image_path)
        if item is None:
            return False
        item.status = BatchStatus.COMPLETED
        self._save()
        return True

    def skip(self, image_path: str) -> bool:
        """Mark item as skipped"""
        item = self.get_item(image_path)
        if item is None:
            return False
        item.status = BatchStatus.SKIPPED
        self._save()
        return True

    def get_total(self) -> int:
        """Return total number of items in batch"""
        return len(self._items)

    def get_completed(self) -> int:
        """Return count of completed and skipped items"""
        return sum(
            1 for item in self._items
            if item.status in (BatchStatus.COMPLETED, BatchStatus.SKIPPED)
        )

    def progress(self) -> float:
        """Return fraction of completed items (0.0 to 1.0)"""
        total = self.get_total()
        if total == 0:
            return 0.0
        return self.get_completed() / total
