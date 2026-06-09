import pytest
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

def test_set_stage_invalid(tmp_workflow):
    """set_stage should raise ValueError for invalid stage"""
    with pytest.raises(ValueError, match="Invalid stage"):
        tmp_workflow.set_stage("INVALID_STAGE")

def test_save_and_load(tmp_workflow):
    """Data should persist across save/load cycles"""
    tmp_workflow.set_stage("CONFIRM_PRODUCT")
    tmp_workflow.set_data("product", {"name": "Test Product"})

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

def test_corrupt_state_file(tmp_path):
    """Should handle corrupt JSON gracefully"""
    state_file = tmp_path / "state" / "workflow.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("not valid json{{{", encoding="utf-8")

    wf = Workflow(state_file=str(state_file))
    assert wf.get_stage() == "INIT"

def test_bare_filename(tmp_path):
    """Should handle state_file with no directory component"""
    state_file = tmp_path / "workflow.json"
    wf = Workflow(state_file=str(state_file))
    wf.set_stage("ANALYZE")
    assert wf.get_stage() == "ANALYZE"
