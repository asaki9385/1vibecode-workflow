import pytest
from agent.progress import ProgressTracker, TaskStatus


@pytest.fixture
def tracker(tmp_path):
    return ProgressTracker(state_dir=str(tmp_path))


def test_create_task(tracker):
    """create should return a task ID and store the task"""
    task_id = tracker.create("Generating images")
    assert isinstance(task_id, str)
    assert len(task_id) > 0
    task = tracker.get(task_id)
    assert task is not None
    assert task["status"] == TaskStatus.PENDING
    assert task["message"] == "Generating images"


def test_create_task_with_total(tracker):
    """create should accept optional total for progress tracking"""
    task_id = tracker.create("Extracting frames", total=100)
    task = tracker.get(task_id)
    assert task["total"] == 100
    assert task["current"] == 0


def test_update_task(tracker):
    """update should modify message and current progress"""
    task_id = tracker.create("Processing", total=10)
    tracker.update(task_id, current=5, message="Halfway done")
    task = tracker.get(task_id)
    assert task["current"] == 5
    assert task["message"] == "Halfway done"
    assert task["status"] == TaskStatus.RUNNING


def test_update_nonexistent_task(tracker):
    """update on missing task should not raise"""
    tracker.update("nonexistent-id", current=1)


def test_complete_task(tracker):
    """complete should set status to DONE and finalize progress"""
    task_id = tracker.create("Building video", total=50)
    tracker.update(task_id, current=30)
    tracker.complete(task_id)
    task = tracker.get(task_id)
    assert task["status"] == TaskStatus.DONE
    assert task["current"] == task["total"]


def test_cancel_task(tracker):
    """cancel should set status to CANCELLED"""
    task_id = tracker.create("Long task")
    tracker.cancel(task_id)
    task = tracker.get(task_id)
    assert task["status"] == TaskStatus.CANCELLED


def test_list_tasks(tracker):
    """list should return all tasks"""
    id1 = tracker.create("Task 1")
    id2 = tracker.create("Task 2")
    tracker.complete(id1)
    tasks = tracker.list_tasks()
    assert len(tasks) == 2


def test_list_tasks_by_status(tracker):
    """list_tasks with status filter should return matching tasks"""
    id1 = tracker.create("Task 1")
    id2 = tracker.create("Task 2")
    tracker.complete(id1)
    pending = tracker.list_tasks(status=TaskStatus.PENDING)
    done = tracker.list_tasks(status=TaskStatus.DONE)
    assert len(pending) == 1
    assert len(done) == 1


def test_get_nonexistent_task(tracker):
    """get should return None for unknown task"""
    assert tracker.get("no-such-id") is None


def test_persistence(tracker, tmp_path):
    """Tasks should survive across tracker instances"""
    task_id = tracker.create("Persistent task")
    tracker.update(task_id, current=50)

    tracker2 = ProgressTracker(state_dir=str(tmp_path))
    task = tracker2.get(task_id)
    assert task is not None
    assert task["current"] == 50
    assert task["message"] == "Persistent task"


def test_percent_complete(tracker):
    """percent should compute 0-100 based on current/total"""
    task_id = tracker.create("Work", total=200)
    tracker.update(task_id, current=50)
    task = tracker.get(task_id)
    assert task["percent"] == 25.0


def test_percent_no_total(tracker):
    """percent should be None when total is not set"""
    task_id = tracker.create("Indeterminate")
    task = tracker.get(task_id)
    assert task["percent"] is None


def test_multiple_tasks_isolation(tracker):
    """Updating one task should not affect others"""
    id1 = tracker.create("A")
    id2 = tracker.create("B")
    tracker.update(id1, current=10, message="Updated A")
    assert tracker.get(id2)["current"] == 0
    assert tracker.get(id2)["message"] == "B"
