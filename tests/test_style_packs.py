import sys
sys.path.insert(0, '.')
import pytest

def test_style_pack_selection():
    """Test that style packs are correctly selected based on keywords"""
    from agent.web_builder import get_design_direction

    # Test editorial
    fh, fb, ac, ag, fi = get_design_direction("person")
    assert fh == "Playfair Display"

    # Test immersive (cyberpunk)
    # This tests the mapping logic

def test_params_decision():
    """Test that parameters are correctly decided based on analysis"""
    from agent.web_builder import decide_params

    # Mock analysis
    analysis = {
        "style_profile": {
            "keywords": ["cyberpunk", "high contrast"],
            "visual_tone": "高对比、冷色调"
        },
        "mood": "神秘、未来感"
    }

    params = decide_params(analysis)
    assert params["deco_density"] == "sparse"
    assert params["anim_energy"] == "high"
    assert params["text_overlay"] is True
    assert params["layout_compact"] is False
    assert params["parallax_depth"] == "subtle"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
