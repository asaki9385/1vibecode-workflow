import sys
sys.path.insert(0, '.')
import pytest
import json

def test_full_workflow_with_style_pack():
    """Test full workflow with style pack integration"""
    # Mock workflow state
    workflow = {
        "stage": "BUILD_PROJECT",
        "image_analysis": {
            "subject": "test subject",
            "subject_type": "other",
            "style_profile": {
                "keywords": ["editorial", "magazine"],
                "copy_tone": "简短有力、诗意、留白感"
            },
            "mood": "神秘、超现实"
        },
        "page_purpose": "作品展示",
        "extracted_palette": {
            "accent_color": "#ff4444",
            "accent_glow": "rgba(255, 68, 68, 0.3)"
        }
    }

    # Test style pack selection
    keywords = workflow["image_analysis"]["style_profile"]["keywords"]
    style_pack = "gallery"  # default
    for kw in keywords:
        if kw in ["editorial", "magazine", "luxury"]:
            style_pack = "editorial"
            break
        elif kw in ["cyberpunk", "dark art", "neon"]:
            style_pack = "immersive"
            break
        elif kw in ["minimalist", "gallery", "organic"]:
            style_pack = "gallery"
            break
        elif kw in ["warm", "natural", "earth"]:
            style_pack = "warm"
            break

    assert style_pack == "editorial"

    # Test params decision
    from agent.web_builder import decide_params
    params = decide_params(workflow["image_analysis"])
    assert params["deco_density"] == "normal"
    assert params["anim_energy"] == "moderate"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
