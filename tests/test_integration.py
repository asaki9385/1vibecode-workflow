import os
import json
import pytest
from agent.workflow import Workflow

def test_full_workflow_cycle(tmp_path):
    """Test complete workflow state transitions"""
    state_file = tmp_path / "state" / "workflow.json"
    wf = Workflow(state_file=str(state_file))

    # INIT
    assert wf.get_stage() == "INIT"

    # ANALYZE
    wf.set_stage("ANALYZE")
    assert wf.get_stage() == "ANALYZE"

    # CONFIRM_PRODUCT
    wf.set_stage("CONFIRM_PRODUCT")
    wf.set_data("product", {"name": "Test", "desc": "Test desc", "style": "科技感"})
    wf.set_data("config", {"effect": "wind", "ratio": "16:9"})
    assert wf.get_data("product")["name"] == "Test"

    # GENERATE
    wf.set_stage("GENERATE")
    wf.set_data("images", {
        "img1": {"path": "generated/image1.png"},
        "img2": {"path": "generated/image2.png"}
    })

    # CONFIRM_IMAGES
    wf.set_stage("CONFIRM_IMAGES")

    # BUILD_VIDEO_PROMPT
    wf.set_stage("BUILD_VIDEO_PROMPT")
    wf.set_data("video_prompt", "test video prompt")

    # WAIT_VIDEO
    wf.set_stage("WAIT_VIDEO")

    # EXTRACT_FRAMES
    wf.set_stage("EXTRACT_FRAMES")

    # BUILD_PROJECT
    wf.set_stage("BUILD_PROJECT")

    # DONE
    wf.set_stage("DONE")
    assert wf.get_stage() == "DONE"

def test_workflow_persistence(tmp_path):
    """Test workflow persists across instances"""
    state_file = tmp_path / "state" / "workflow.json"

    # First instance
    wf1 = Workflow(state_file=str(state_file))
    wf1.set_stage("CONFIRM_PRODUCT")
    wf1.set_data("product", {"name": "Test"})

    # Second instance
    wf2 = Workflow(state_file=str(state_file))
    assert wf2.get_stage() == "CONFIRM_PRODUCT"
    assert wf2.get_data("product")["name"] == "Test"

def test_workflow_reset(tmp_path):
    """Test workflow reset clears all data"""
    state_file = tmp_path / "state" / "workflow.json"
    wf = Workflow(state_file=str(state_file))

    wf.set_stage("DONE")
    wf.set_data("product", {"name": "Test"})
    wf.reset()

    assert wf.get_stage() == "INIT"
    assert wf.get_data("product") is None
