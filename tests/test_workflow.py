import os
import json
import pytest
import tempfile
from agent.workflow import Workflow

@pytest.fixture
def tmp_workflow(tmp_path):
    """Create workflow with temporary state file"""
    state_file = tmp_path / "state" / "workflow.json"
    return Workflow(state_file=str(state_file))

def test_init_creates_state_dir(tmp_workflow):
    """INIT stage should be default when no state file exists"""
    assert tmp_workflow.get_stage() == "INIT"

def test_set_stage(tmp_workflow):
    """set_stage should update current stage"""
    tmp_workflow.set_stage("ANALYZE")
    assert tmp_workflow.get_stage() == "ANALYZE"

def test_save_and_load(tmp_workflow):
    """Data should persist across save/load cycles"""
    tmp_workflow.set_stage("CONFIRM_PRODUCT")
    tmp_workflow.set_data("product", {"name": "Test Product"})
    tmp_workflow.save()

    # Create new workflow instance to test persistence
    new_wf = Workflow(state_file=tmp_workflow.state_file)
    assert new_wf.get_stage() == "CONFIRM_PRODUCT"
    assert new_wf.get_data("product") == {"name": "Test Product"}

def test_reset(tmp_workflow):
    """reset should clear all state back to INIT"""
    tmp_workflow.set_stage("DONE")
    tmp_workflow.set_data("product", {"name": "Test"})
    tmp_workflow.reset()
    assert tmp_workflow.get_stage() == "INIT"
    assert tmp_workflow.get_data("product") is None

def test_get_data_default(tmp_workflow):
    """get_data should return default for missing keys"""
    assert tmp_workflow.get_data("nonexistent") is None
    assert tmp_workflow.get_data("nonexistent", "default") == "default"
