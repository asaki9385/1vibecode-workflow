# 结尾帧生成系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将图2从"图1的微调"升级为"有意义的结尾帧"，支持 AI 自动推断 + 用户指定的混合模式

**Architecture:** 在 prompt_builder.py 中新增结尾方案生成和 Prompt 构建函数，更新 vibecode-agent.md 的 CONFIRM_IMAGES 阶段交互流程

**Tech Stack:** Python, pytest

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `agent/prompt_builder.py` | 修改 | 新增 `generate_ending_options()` 和 `build_ending_prompt()` |
| `tests/test_prompt_builder.py` | 修改 | 新增结尾帧相关测试 |
| `.claude/skills/vibecode-agent.md` | 修改 | 更新 CONFIRM_IMAGES 阶段交互 |

---

### Task 1: 添加 generate_ending_options() 函数

**Files:**
- Modify: `agent/prompt_builder.py`
- Test: `tests/test_prompt_builder.py`

- [ ] **Step 1: Write the failing test**

```python
def test_generate_ending_options_panda():
    """Should generate ending options for panda eating bamboo"""
    analysis = {
        "subject": "卡通熊猫",
        "action": "坐着吃竹子",
        "scene": "白色背景",
        "mood": "可爱、满足"
    }
    options = generate_ending_options(analysis)
    assert len(options) >= 2
    assert len(options) <= 3
    for opt in options:
        assert "type" in opt
        assert "description" in opt
        assert "prompt" in opt


def test_generate_ending_options_default():
    """Should provide default options when analysis is empty"""
    options = generate_ending_options({})
    assert len(options) >= 2


def test_generate_ending_options_types():
    """Should include different ending types"""
    analysis = {"subject": "人物", "action": "站立", "scene": "户外", "mood": "平静"}
    options = generate_ending_options(analysis)
    types = [opt["type"] for opt in options]
    assert len(set(types)) >= 2  # At least 2 different types
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_prompt_builder.py::test_generate_ending_options_panda -v`
Expected: FAIL with "name 'generate_ending_options' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def generate_ending_options(image_analysis: dict) -> list:
    """基于图1分析结果，生成 2-3 个结尾方案

    Args:
        image_analysis: 图1的分析结果 {"subject": ..., "action": ..., "scene": ..., "mood": ...}

    Returns:
        [{"type": "动作完成", "description": "...", "prompt": "..."}, ...]
    """
    subject = image_analysis.get("subject", "主体")
    action = image_analysis.get("action", "存在")
    scene = image_analysis.get("scene", "背景中")
    mood = image_analysis.get("mood", "平静")

    options = [
        {
            "type": "动作完成",
            "description": f"{subject}完成了{action}，满足地休息",
            "prompt": f"Same {subject} as reference. {subject} has finished {action}, now resting contentedly. Preserve all original features. Do NOT add new elements."
        },
        {
            "type": "场景拉远",
            "description": f"镜头拉远，展示{subject}在{scene}中的全貌",
            "prompt": f"Same {subject} as reference. Camera pulls back to reveal the full scene: {subject} in {scene}. Preserve all original features. Do NOT add new elements."
        },
        {
            "type": "情绪变化",
            "description": f"{subject}表情变化，从{mood}变为更加开心",
            "prompt": f"Same {subject} as reference. {subject}'s expression changes from {mood} to happy and joyful. Preserve all original features. Do NOT add new elements."
        }
    ]

    return options
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_prompt_builder.py::test_generate_ending_options_panda tests/test_prompt_builder.py::test_generate_ending_options_default tests/test_prompt_builder.py::test_generate_ending_options_types -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agent/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add generate_ending_options function"
```

---

### Task 2: 添加 build_ending_prompt() 函数

**Files:**
- Modify: `agent/prompt_builder.py`
- Test: `tests/test_prompt_builder.py`

- [ ] **Step 1: Write the failing test**

```python
def test_build_ending_prompt():
    """Should build ending prompt with original features preserved"""
    original = "卡通熊猫，黑白毛色，蓝色大眼睛，坐着吃竹子"
    ending = "熊猫吃完竹子，舔舔嘴巴"
    prompt = build_ending_prompt(original, ending)
    assert original in prompt
    assert ending in prompt
    assert "Do NOT" in prompt  # Should have prohibition clause


def test_build_ending_prompt_empty_original():
    """Should raise ValueError for empty original features"""
    with pytest.raises(ValueError, match="original_features cannot be empty"):
        build_ending_prompt("", "some ending")


def test_build_ending_prompt_empty_ending():
    """Should raise ValueError for empty ending description"""
    with pytest.raises(ValueError, match="ending_description cannot be empty"):
        build_ending_prompt("some features", "")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_prompt_builder.py::test_build_ending_prompt -v`
Expected: FAIL with "name 'build_ending_prompt' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def build_ending_prompt(original_features: str, ending_description: str) -> str:
    """基于图1特征和结尾描述，生成图2的 Prompt

    Args:
        original_features: 图1需要保留的特征描述
        ending_description: 结尾方案的描述

    Returns:
        图生图 Prompt
    """
    if not original_features:
        raise ValueError("original_features cannot be empty")
    if not ending_description:
        raise ValueError("ending_description cannot be empty")

    return (
        f"Same subject as reference image. Preserve ALL original features: {original_features}. "
        f"Change: {ending_description}. "
        f"Do NOT add new elements not mentioned above. "
        f"Maintain identical art style, color palette, and composition."
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_prompt_builder.py::test_build_ending_prompt tests/test_prompt_builder.py::test_build_ending_prompt_empty_original tests/test_prompt_builder.py::test_build_ending_prompt_empty_ending -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agent/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add build_ending_prompt function"
```

---

### Task 3: 更新 vibecode-agent.md 交互流程

**Files:**
- Modify: `.claude/skills/vibecode-agent.md`

- [ ] **Step 1: Update CONFIRM_IMAGES stage**

Replace the current CONFIRM_IMAGES section with:

```markdown
### CONFIRM_IMAGES

**阶段 A：展示结尾方案选项**

图1 生成后，调用 `agent/prompt_builder.py` 的 `generate_ending_options()` 获取结尾方案。

展示选项给用户：

请选择结尾帧效果：
1. 【动作完成】熊猫吃完竹子，舔舔嘴巴，满足地坐着
2. 【场景拉远】镜头拉远，熊猫在竹林中，周围是更多竹子
3. 【情绪变化】熊猫抬头看天空，表情从专注变为开心
4. 自定义（描述你想要的结尾）

回复选项，例如：1 或 4、熊猫站起来挥手

**阶段 B：生成图2**

- 用户选 1-3 → 调用 `build_ending_prompt()` 生成 Prompt，再调用 `generate_image()` 生成图2
- 用户选 4 → 收集自定义描述 → 调用 `build_ending_prompt()` 生成 Prompt → 生成图2

**阶段 C：确认**

展示图1+图2，提供选项：
1. 满意，继续
2. 重新选择结尾方案（回到阶段 A）
3. 修改图1（重新生成）
4. 全部重做
```

- [ ] **Step 2: Update Python module interface**

Add to the Python 模块接口 section:

```markdown
### agent/prompt_builder.py
```python
# 生成结尾方案选项
generate_ending_options(image_analysis: dict) -> list[dict]

# 生成结尾帧 Prompt
build_ending_prompt(original_features: str, ending_description: str) -> str

# 其他已有函数...
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/vibecode-agent.md
git commit -m "docs: update agent with ending frame flow"
```

---

### Task 4: 运行全部测试验证

**Files:**
- None (verification only)

- [ ] **Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 2: Verify no regressions**

Check that existing functions still work correctly.

---

### Task 5: 端到端测试

**Files:**
- None (manual verification)

- [ ] **Step 1: Reset workflow**

```bash
cd D:/1vibecode-workflow && python -c "from agent.workflow import Workflow; Workflow().reset()"
```

- [ ] **Step 2: Start agent and test ending frame flow**

Run `/vibecode-agent` in Claude Code and verify:
1. 图1 生成后，展示 3 个结尾方案选项
2. 选择方案后，生成对应的图2
3. 图2 与图1 保持一致性，只改变结尾描述的部分
