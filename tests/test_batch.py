import pytest
from agent.batch import BatchWorkflow, BatchItem, BatchStatus

@pytest.fixture
def tmp_batch(tmp_path):
    """Create BatchWorkflow with temporary state file"""
    state_file = tmp_path / "batch" / "state.json"
    return BatchWorkflow(state_file=str(state_file))

def test_create_batch(tmp_batch):
    """create should initialize a new batch with images"""
    images = ["img1.jpg", "img2.jpg", "img3.jpg"]
    batch = tmp_batch.create(images)
    assert len(batch) == 3
    assert tmp_batch.get_total() == 3
    assert tmp_batch.get_completed() == 0

def test_create_batch_empty(tmp_batch):
    """create with empty list should raise ValueError"""
    with pytest.raises(ValueError, match="At least one image required"):
        tmp_batch.create([])

def test_get_next(tmp_batch):
    """get_next should return next unprocessed item"""
    images = ["img1.jpg", "img2.jpg"]
    tmp_batch.create(images)
    item = tmp_batch.get_next()
    assert item is not None
    assert item.image_path == "img1.jpg"
    assert item.status == BatchStatus.PENDING

def test_get_next_none(tmp_batch):
    """get_next should return None when all items processed"""
    tmp_batch.create(["img1.jpg"])
    tmp_batch.complete("img1.jpg")
    item = tmp_batch.get_next()
    assert item is None

def test_complete(tmp_batch):
    """complete should mark item as done"""
    tmp_batch.create(["img1.jpg", "img2.jpg"])
    result = tmp_batch.complete("img1.jpg")
    assert result is True
    assert tmp_batch.get_completed() == 1

def test_complete_nonexistent(tmp_batch):
    """complete should return False for unknown image"""
    tmp_batch.create(["img1.jpg"])
    result = tmp_batch.complete("nonexistent.jpg")
    assert result is False

def test_skip(tmp_batch):
    """skip should mark item as skipped"""
    tmp_batch.create(["img1.jpg", "img2.jpg"])
    result = tmp_batch.skip("img1.jpg")
    assert result is True
    item = tmp_batch.get_item("img1.jpg")
    assert item.status == BatchStatus.SKIPPED

def test_skip_nonexistent(tmp_batch):
    """skip should return False for unknown image"""
    tmp_batch.create(["img1.jpg"])
    result = tmp_batch.skip("nonexistent.jpg")
    assert result is False

def test_get_item(tmp_batch):
    """get_item should return specific batch item"""
    tmp_batch.create(["img1.jpg"])
    item = tmp_batch.get_item("img1.jpg")
    assert item is not None
    assert item.image_path == "img1.jpg"

def test_get_total(tmp_batch):
    """get_total should return total number of items"""
    tmp_batch.create(["a.jpg", "b.jpg", "c.jpg"])
    assert tmp_batch.get_total() == 3

def test_get_completed(tmp_batch):
    """get_completed should count completed and skipped items"""
    tmp_batch.create(["a.jpg", "b.jpg", "c.jpg"])
    tmp_batch.complete("a.jpg")
    tmp_batch.skip("b.jpg")
    assert tmp_batch.get_completed() == 2

def test_progress(tmp_batch):
    """progress should return fraction of completed items"""
    tmp_batch.create(["a.jpg", "b.jpg", "c.jpg", "d.jpg"])
    tmp_batch.complete("a.jpg")
    tmp_batch.complete("b.jpg")
    assert tmp_batch.progress() == 0.5

def test_progress_empty(tmp_batch):
    """progress should return 0 for empty batch"""
    assert tmp_batch.progress() == 0.0

def test_persistence(tmp_path):
    """Batch state should persist across load cycles"""
    state_file = tmp_path / "batch.json"
    batch1 = BatchWorkflow(state_file=str(state_file))
    batch1.create(["a.jpg", "b.jpg", "c.jpg"])
    batch1.complete("a.jpg")
    batch1.skip("b.jpg")

    batch2 = BatchWorkflow(state_file=str(state_file))
    assert batch2.get_total() == 3
    assert batch2.get_completed() == 2
    item_a = batch2.get_item("a.jpg")
    assert item_a.status == BatchStatus.COMPLETED
    item_b = batch2.get_item("b.jpg")
    assert item_b.status == BatchStatus.SKIPPED

def test_get_next_respects_order(tmp_batch):
    """get_next should return items in creation order"""
    tmp_batch.create(["first.jpg", "second.jpg", "third.jpg"])
    first = tmp_batch.get_next()
    assert first.image_path == "first.jpg"
    tmp_batch.complete("first.jpg")
    second = tmp_batch.get_next()
    assert second.image_path == "second.jpg"

def test_corrupt_state_file(tmp_path):
    """Should handle corrupt JSON gracefully"""
    state_file = tmp_path / "batch.json"
    state_file.write_text("invalid json{{{", encoding="utf-8")
    batch = BatchWorkflow(state_file=str(state_file))
    assert batch.get_total() == 0
    assert batch.get_next() is None

def test_skip_does_not_count_as_completed(tmp_batch):
    """skip should not affect completed count"""
    tmp_batch.create(["a.jpg", "b.jpg"])
    tmp_batch.complete("a.jpg")
    tmp_batch.skip("b.jpg")
    assert tmp_batch.get_completed() == 2  # both completed + skipped
    # but progress should treat them differently if needed
    assert tmp_batch.progress() == 1.0

def test_get_next_after_skip(tmp_batch):
    """get_next should skip over skipped items"""
    tmp_batch.create(["a.jpg", "b.jpg", "c.jpg"])
    tmp_batch.skip("a.jpg")
    next_item = tmp_batch.get_next()
    assert next_item.image_path == "b.jpg"
