import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from agent.workflow import Workflow
from agent.batch import BatchWorkflow, BatchItem, BatchStatus
from agent.cache import ImageCache
from agent.progress import ProgressTracker
from agent.prompt_builder import (
    apply_modification,
    build_ending_prompt,
    generate_ending_options,
)
from agent.web_builder import generate_player_html
from agent.frame_extractor import extract_frames


class TestWorkflowEdgeCases:
    def test_init_with_corrupted_json_file(self, tmp_path):
        """Should fall back to INIT when state file is corrupted"""
        state_file = tmp_path / "workflow.json"
        state_file.write_text("{invalid json content!!!", encoding="utf-8")

        wf = Workflow(state_file=str(state_file))
        assert wf.get_stage() == "INIT"

    def test_init_with_empty_json_file(self, tmp_path):
        """Should fall back to INIT when state file is empty"""
        state_file = tmp_path / "workflow.json"
        state_file.write_text("", encoding="utf-8")

        wf = Workflow(state_file=str(state_file))
        assert wf.get_stage() == "INIT"

    def test_init_with_non_dict_json(self, tmp_path):
        """Should fall back to INIT when JSON is not a dict"""
        state_file = tmp_path / "workflow.json"
        state_file.write_text('"just a string"', encoding="utf-8")

        wf = Workflow(state_file=str(state_file))
        assert wf.get_stage() == "INIT"

    def test_init_with_list_json(self, tmp_path):
        """Should fall back to INIT when JSON is a list"""
        state_file = tmp_path / "workflow.json"
        state_file.write_text("[1, 2, 3]", encoding="utf-8")

        wf = Workflow(state_file=str(state_file))
        assert wf.get_stage() == "INIT"

    def test_set_invalid_stage_raises(self, tmp_path):
        """Should raise ValueError for invalid stage"""
        state_file = tmp_path / "workflow.json"
        wf = Workflow(state_file=str(state_file))

        with pytest.raises(ValueError, match="Invalid stage"):
            wf.set_stage("NONEXISTENT")

    def test_set_data_on_nonexistent_key(self, tmp_path):
        """Should allow setting new keys"""
        state_file = tmp_path / "workflow.json"
        wf = Workflow(state_file=str(state_file))
        wf.set_data("new_key", "new_value")
        assert wf.get_data("new_key") == "new_value"

    def test_get_data_default(self, tmp_path):
        """Should return default for missing keys"""
        state_file = tmp_path / "workflow.json"
        wf = Workflow(state_file=str(state_file))
        assert wf.get_data("missing", "fallback") == "fallback"
        assert wf.get_data("missing") is None

    def test_nested_data_persistence(self, tmp_path):
        """Should persist nested dicts and lists"""
        state_file = tmp_path / "workflow.json"
        wf = Workflow(state_file=str(state_file))

        nested = {"a": {"b": {"c": [1, 2, 3]}}}
        wf.set_data("nested", nested)

        wf2 = Workflow(state_file=str(state_file))
        assert wf2.get_data("nested") == nested

    def test_corrupted_state_recovery(self, tmp_path):
        """Should recover when file is corrupted mid-session"""
        state_file = tmp_path / "workflow.json"
        wf = Workflow(state_file=str(state_file))
        wf.set_stage("ANALYZE")

        # Corrupt the file
        state_file.write_text("CORRUPTED", encoding="utf-8")

        wf2 = Workflow(state_file=str(state_file))
        assert wf2.get_stage() == "INIT"


class TestBatchEdgeCases:
    def test_batch_empty_list_raises(self, tmp_path):
        """Should raise ValueError when creating batch with empty list"""
        state_file = tmp_path / "batch.json"
        batch = BatchWorkflow(state_file=str(state_file))
        with pytest.raises(ValueError, match="At least one image required"):
            batch.create([])

    def test_batch_get_next_empty(self, tmp_path):
        """Should return None when batch is empty"""
        state_file = tmp_path / "batch.json"
        batch = BatchWorkflow(state_file=str(state_file))
        assert batch.get_next() is None

    def test_batch_complete_nonexistent(self, tmp_path):
        """Should return False for non-existent path"""
        state_file = tmp_path / "batch.json"
        batch = BatchWorkflow(state_file=str(state_file))
        assert batch.complete("nonexistent.png") is False

    def test_batch_skip_nonexistent(self, tmp_path):
        """Should return False for non-existent path"""
        state_file = tmp_path / "batch.json"
        batch = BatchWorkflow(state_file=str(state_file))
        assert batch.skip("nonexistent.png") is False

    def test_batch_progress_zero_items(self, tmp_path):
        """Should return 0.0 progress for empty batch"""
        state_file = tmp_path / "batch.json"
        batch = BatchWorkflow(state_file=str(state_file))
        assert batch.progress() == 0.0

    def test_batch_progress_all_completed(self, tmp_path):
        """Should return 1.0 when all items are completed"""
        state_file = tmp_path / "batch.json"
        batch = BatchWorkflow(state_file=str(state_file))
        batch.create(["a.png", "b.png"])
        batch.complete("a.png")
        batch.complete("b.png")
        assert batch.progress() == 1.0

    def test_batch_all_skipped(self, tmp_path):
        """Should count skipped items as completed"""
        state_file = tmp_path / "batch.json"
        batch = BatchWorkflow(state_file=str(state_file))
        batch.create(["a.png", "b.png"])
        batch.skip("a.png")
        batch.skip("b.png")
        assert batch.progress() == 1.0
        assert batch.get_completed() == 2

    def test_batch_persistence(self, tmp_path):
        """Should persist state across instances"""
        state_file = tmp_path / "batch.json"
        b1 = BatchWorkflow(state_file=str(state_file))
        b1.create(["x.png"])
        b1.complete("x.png")

        b2 = BatchWorkflow(state_file=str(state_file))
        assert b2.get_total() == 1
        assert b2.get_item("x.png").status == BatchStatus.COMPLETED

    def test_batch_corrupted_state(self, tmp_path):
        """Should recover from corrupted state file"""
        state_file = tmp_path / "batch.json"
        state_file.write_text("NOT JSON!!!", encoding="utf-8")

        batch = BatchWorkflow(state_file=str(state_file))
        assert batch.get_total() == 0


class TestCacheEdgeCases:
    def test_cache_miss(self, tmp_path):
        """Should return None for cache miss"""
        cache = ImageCache(
            state_dir=str(tmp_path / "cache_state"),
            image_dir=str(tmp_path / "cache_images"),
        )
        assert cache.get("nonexistent prompt") is None

    def test_cache_roundtrip(self, tmp_path):
        """Should store and retrieve metadata"""
        cache = ImageCache(
            state_dir=str(tmp_path / "cache_state"),
            image_dir=str(tmp_path / "cache_images"),
        )
        cache.set("test prompt", ttl=3600)
        result = cache.get("test prompt")
        assert result is not None
        assert result["prompt"] == "test prompt"

    def test_cache_expiry(self, tmp_path):
        """Should return None for expired entries"""
        cache = ImageCache(
            state_dir=str(tmp_path / "cache_state"),
            image_dir=str(tmp_path / "cache_images"),
        )
        cache.set("test prompt", ttl=-1)
        result = cache.get("test prompt")
        assert result is None

    def test_cache_clear(self, tmp_path):
        """Should remove all entries"""
        cache = ImageCache(
            state_dir=str(tmp_path / "cache_state"),
            image_dir=str(tmp_path / "cache_images"),
        )
        cache.set("prompt1")
        cache.set("prompt2")
        cache.clear()
        assert cache.get("prompt1") is None
        assert cache.get("prompt2") is None

    def test_cache_with_image_file(self, tmp_path):
        """Should cache image file alongside metadata"""
        cache = ImageCache(
            state_dir=str(tmp_path / "cache_state"),
            image_dir=str(tmp_path / "cache_images"),
        )
        src = tmp_path / "source.png"
        src.write_bytes(b"fake png data")

        cache.set("prompt", image_path=str(src), output_ext=".png")
        result = cache.get("prompt")
        assert result is not None
        cached_img = os.path.join(cache.image_dir, f"{result['output_ext'].replace('.', '')}.png")
        # The key is MD5 based, verify the image dir is populated
        assert len(os.listdir(cache.image_dir)) > 0

    def test_cache_no_ttl(self, tmp_path):
        """Should not expire entries without ttl"""
        cache = ImageCache(
            state_dir=str(tmp_path / "cache_state"),
            image_dir=str(tmp_path / "cache_images"),
        )
        cache.set("eternal prompt")
        result = cache.get("eternal prompt")
        assert result is not None


class TestProgressEdgeCases:
    def test_get_nonexistent_task(self, tmp_path):
        """Should return None for unknown task id"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        assert tracker.get("nonexistent") is None

    def test_update_nonexistent_task(self, tmp_path):
        """Should not raise when updating nonexistent task"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        tracker.update("nonexistent", current=5)

    def test_complete_nonexistent_task(self, tmp_path):
        """Should not raise when completing nonexistent task"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        tracker.complete("nonexistent")

    def test_cancel_nonexistent_task(self, tmp_path):
        """Should not raise when cancelling nonexistent task"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        tracker.cancel("nonexistent")

    def test_list_empty(self, tmp_path):
        """Should return empty list when no tasks exist"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        assert tracker.list_tasks() == []

    def test_list_filter_by_status(self, tmp_path):
        """Should filter tasks by status"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        id1 = tracker.create("task1")
        id2 = tracker.create("task2")
        tracker.update(id1, current=1)
        tracker.complete(id1)

        done = tracker.list_tasks(status="done")
        assert len(done) == 1
        assert done[0]["id"] == id1

    def test_update_percent_calculation(self, tmp_path):
        """Should calculate percent correctly"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        task_id = tracker.create("task", total=100)
        tracker.update(task_id, current=33)
        data = tracker.get(task_id)
        assert data["percent"] == 33.0

    def test_progress_roundtrip(self, tmp_path):
        """Should persist progress across instances"""
        tracker = ProgressTracker(state_dir=str(tmp_path / "progress"))
        task_id = tracker.create("task", total=10)
        tracker.update(task_id, current=5)

        tracker2 = ProgressTracker(state_dir=str(tmp_path / "progress"))
        data = tracker2.get(task_id)
        assert data["current"] == 5


class TestPromptBuilderEdgeCases:
    def test_apply_modification_empty_original(self):
        """Should raise ValueError for empty original"""
        with pytest.raises(ValueError, match="original_prompt cannot be empty"):
            apply_modification("", "modification")

    def test_apply_modification_empty_modification(self):
        """Should raise ValueError for empty modification"""
        with pytest.raises(ValueError, match="modification cannot be empty"):
            apply_modification("original", "")

    def test_build_ending_prompt_empty_features(self):
        """Should raise ValueError for empty features"""
        with pytest.raises(ValueError, match="original_features cannot be empty"):
            build_ending_prompt("", "ending desc")

    def test_build_ending_prompt_empty_description(self):
        """Should raise ValueError for empty description"""
        with pytest.raises(ValueError, match="ending_description cannot be empty"):
            build_ending_prompt("features", "")

    def test_generate_ending_options_none_input(self):
        """Should raise TypeError for None input"""
        with pytest.raises(TypeError, match="image_analysis must be a dict"):
            generate_ending_options(None)

    def test_generate_ending_options_not_dict(self):
        """Should raise TypeError for non-dict input"""
        with pytest.raises(TypeError, match="image_analysis must be a dict"):
            generate_ending_options("not a dict")

    def test_generate_ending_options_empty_dict(self):
        """Should handle empty dict with defaults"""
        options = generate_ending_options({})
        assert len(options) == 3
        assert all("type" in o for o in options)


class TestWebBuilderEdgeCases:
    def test_negative_frame_count(self):
        """Should raise ValueError for negative frame count"""
        with pytest.raises(ValueError):
            generate_player_html(frame_count=-5, fps=24)

    def test_negative_fps(self):
        """Should raise ValueError for negative fps"""
        with pytest.raises(ValueError):
            generate_player_html(frame_count=10, fps=-30)

    def test_large_frame_count(self):
        """Should handle large frame count"""
        html = generate_player_html(frame_count=10000, fps=24)
        assert "10000" in html
        assert "<!DOCTYPE html>" in html

    def test_single_frame(self):
        """Should handle single frame"""
        html = generate_player_html(frame_count=1, fps=24)
        assert "1" in html
        assert "<!DOCTYPE html>" in html

    def test_high_fps(self):
        """Should handle high fps value"""
        html = generate_player_html(frame_count=120, fps=120)
        assert "120" in html


class TestFrameExtractorEdgeCases:
    def test_extract_frames_invalid_fps(self):
        """Should raise ValueError for zero fps"""
        with pytest.raises(ValueError, match="fps must be positive"):
            extract_frames("video.mp4", "/tmp/out", fps=0)

    def test_extract_frames_negative_fps(self):
        """Should raise ValueError for negative fps"""
        with pytest.raises(ValueError, match="fps must be positive"):
            extract_frames("video.mp4", "/tmp/out", fps=-1)

    def test_extract_frames_nonexistent_video(self, tmp_path, monkeypatch):
        """Should raise FileNotFoundError for missing video"""
        monkeypatch.setattr("agent.frame_extractor._find_ffmpeg", lambda: "C:/fake/ffmpeg.exe")
        with pytest.raises(FileNotFoundError):
            extract_frames("/nonexistent/video.mp4", str(tmp_path / "out"))
