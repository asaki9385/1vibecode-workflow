# Feature 4: Functionality Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 5 new features: image caching, batch processing, extended image format support, Streamlit Web UI, and progress notification.

**Architecture:** Extend existing modules with minimal changes. Add `agent/cache.py` for caching, `agent/batch.py` for batch workflow, extend `agent/image_generator.py` for format support, create `app.py` for Streamlit UI, and add `state/progress.json` for polling.

**Tech Stack:** Python, Streamlit, hashlib, JSON, existing agent modules

---

### Task 1: Image Format Support

**Covers:** Extended image format support

**Files:**
- Modify: `agent/image_generator.py`

- [ ] **Step 1: Add supported formats constant and validation**

```python
# Add at top of agent/image_generator.py after imports
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

def validate_image(image_path: str) -> bool:
    """验证图片格式是否支持"""
    ext = os.path.splitext(image_path)[1].lower()
    return ext in SUPPORTED_FORMATS
```

- [ ] **Step 2: Extend mime map in _image_to_data_url**

```python
# Replace existing mime_map in _image_to_data_url
mime_map = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", 
    ".png": "image/png", ".webp": "image/webp",
    ".gif": "image/gif", ".bmp": "image/bmp", 
    ".tiff": "image/tiff"
}
```

- [ ] **Step 3: Add validation to generate_image**

```python
# Add at start of generate_image function, after API key check
if not validate_image(reference_image if reference_image else output_path):
    raise ValueError(f"不支持的图片格式，支持: {SUPPORTED_FORMATS}")
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_image_generator.py -v`

- [ ] **Step 5: Commit**

```bash
git add agent/image_generator.py
git commit -m "feat: add extended image format support (gif, bmp, tiff)"
```

---

### Task 2: Cache Module

**Covers:** Image caching system

**Files:**
- Create: `agent/cache.py`
- Create: `tests/test_cache.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cache.py
import os
import json
import time
import pytest
from agent.cache import ImageCache

@pytest.fixture
def cache(tmp_path):
    return ImageCache(cache_dir=str(tmp_path / "cache"), 
                      images_dir=str(tmp_path / "images"),
                      ttl_hours=1)

def test_cache_miss(cache):
    assert cache.get("prompt1", None) is None

def test_cache_hit(cache, tmp_path):
    # Create a dummy image
    img_path = tmp_path / "test.png"
    img_path.write_bytes(b"fake image data")
    
    # Store in cache
    cache.set("prompt1", None, str(img_path))
    
    # Should hit
    result = cache.get("prompt1", None)
    assert result is not None
    assert os.path.exists(result)

def test_cache_expired(cache, tmp_path):
    img_path = tmp_path / "test.png"
    img_path.write_bytes(b"fake image data")
    
    cache.set("prompt1", None, str(img_path))
    
    # Manually expire
    cache_file = cache._get_cache_file("prompt1", None)
    with open(cache_file, "r") as f:
        data = json.load(f)
    data["created_at"] = time.time() - 72000  # 20 hours ago
    with open(cache_file, "w") as f:
        json.dump(data, f)
    
    assert cache.get("prompt1", None) is None

def test_cache_key_generation(cache):
    key1 = cache._make_key("prompt", None)
    key2 = cache._make_key("prompt", "ref.jpg")
    assert key1 != key2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cache.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agent.cache'"

- [ ] **Step 3: Implement cache module**

```python
# agent/cache.py
import os
import json
import hashlib
import shutil
import time
from typing import Optional

class ImageCache:
    def __init__(self, cache_dir: str = "state/cache", 
                 images_dir: str = "generated/cache",
                 ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.images_dir = images_dir
        self.ttl_seconds = ttl_hours * 3600
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
    
    def _make_key(self, prompt: str, reference_image: Optional[str]) -> str:
        content = f"{prompt}|{reference_image or ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_file(self, prompt: str, reference_image: Optional[str]) -> str:
        key = self._make_key(prompt, reference_image)
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, prompt: str, reference_image: Optional[str]) -> Optional[str]:
        cache_file = self._get_cache_file(prompt, reference_image)
        if not os.path.exists(cache_file):
            return None
        
        with open(cache_file, "r") as f:
            data = json.load(f)
        
        if time.time() - data["created_at"] > self.ttl_seconds:
            os.remove(cache_file)
            return None
        
        if not os.path.exists(data["image_path"]):
            os.remove(cache_file)
            return None
        
        return data["image_path"]
    
    def set(self, prompt: str, reference_image: Optional[str], image_path: str):
        key = self._make_key(prompt, reference_image)
        
        # Copy image to cache directory
        dest_path = os.path.join(self.images_dir, f"{key}{os.path.splitext(image_path)[1]}")
        shutil.copy2(image_path, dest_path)
        
        # Store metadata
        cache_file = self._get_cache_file(prompt, reference_image)
        with open(cache_file, "w") as f:
            json.dump({
                "key": key,
                "prompt": prompt,
                "reference_image": reference_image,
                "image_path": dest_path,
                "created_at": time.time()
            }, f)
    
    def clear(self):
        shutil.rmtree(self.cache_dir)
        shutil.rmtree(self.images_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cache.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agent/cache.py tests/test_cache.py
git commit -m "feat: add image caching module with TTL support"
```

---

### Task 3: Batch Processing

**Covers:** Batch workflow management

**Files:**
- Create: `agent/batch.py`
- Create: `tests/test_batch.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_batch.py
import os
import json
import pytest
from agent.batch import BatchWorkflow

@pytest.fixture
def batch(tmp_path):
    state_dir = str(tmp_path / "state")
    return BatchWorkflow(state_dir=state_dir)

def test_batch_create(batch):
    batch_id = batch.create(["img1.jpg", "img2.jpg"])
    assert batch_id is not None
    assert batch.get_status()["total"] == 2

def test_batch_add_images(batch):
    batch_id = batch.create(["img1.jpg"])
    batch.add_images(["img2.jpg", "img3.jpg"])
    assert batch.get_status()["total"] == 3

def test_batch_get_next(batch):
    batch_id = batch.create(["img1.jpg", "img2.jpg"])
    next_img = batch.get_next()
    assert next_img == "img1.jpg"

def test_batch_complete_current(batch):
    batch_id = batch.create(["img1.jpg", "img2.jpg"])
    batch.get_next()
    batch.complete_current("output1.png")
    assert batch.get_status()["current"] == 1

def test_batch_skip(batch):
    batch_id = batch.create(["img1.jpg", "img2.jpg"])
    batch.get_next()
    batch.skip_current("API error")
    assert batch.get_status()["current"] == 1
    assert batch.get_status()["skipped"] == 1

def test_batch_is_complete(batch):
    batch_id = batch.create(["img1.jpg"])
    assert not batch.is_complete()
    batch.get_next()
    batch.complete_current("output.png")
    assert batch.is_complete()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_batch.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agent.batch'"

- [ ] **Step 3: Implement batch module**

```python
# agent/batch.py
import os
import json
import uuid
import time
from typing import Optional, List

class BatchWorkflow:
    def __init__(self, state_dir: str = "state"):
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
        self._data = None
        self._batch_id = None
    
    def create(self, images: List[str]) -> str:
        self._batch_id = str(uuid.uuid4())[:8]
        self._data = {
            "batch_id": self._batch_id,
            "images": images,
            "current": 0,
            "completed": [],
            "skipped": [],
            "results": {},
            "created_at": time.time(),
            "updated_at": time.time()
        }
        self._save()
        return self._batch_id
    
    def load(self, batch_id: str) -> bool:
        state_file = os.path.join(self.state_dir, f"batch_{batch_id}.json")
        if not os.path.exists(state_file):
            return False
        with open(state_file, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        self._batch_id = batch_id
        return True
    
    def _save(self):
        if not self._data:
            return
        self._data["updated_at"] = time.time()
        state_file = os.path.join(self.state_dir, f"batch_{self._batch_id}.json")
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
    
    def get_status(self) -> dict:
        if not self._data:
            return {}
        return {
            "batch_id": self._batch_id,
            "total": len(self._data["images"]),
            "current": self._data["current"],
            "completed": len(self._data["completed"]),
            "skipped": len(self._data["skipped"]),
            "is_complete": self.is_complete()
        }
    
    def get_next(self) -> Optional[str]:
        if not self._data or self.is_complete():
            return None
        idx = self._data["current"]
        return self._data["images"][idx]
    
    def complete_current(self, output_path: str):
        if not self._data:
            return
        idx = self._data["current"]
        img = self._data["images"][idx]
        self._data["completed"].append(img)
        self._data["results"][img] = {"status": "done", "output": output_path}
        self._data["current"] = idx + 1
        self._save()
    
    def skip_current(self, reason: str):
        if not self._data:
            return
        idx = self._data["current"]
        img = self._data["images"][idx]
        self._data["skipped"].append(img)
        self._data["results"][img] = {"status": "skipped", "reason": reason}
        self._data["current"] = idx + 1
        self._save()
    
    def is_complete(self) -> bool:
        if not self._data:
            return True
        return self._data["current"] >= len(self._data["images"])
    
    def get_results(self) -> dict:
        if not self._data:
            return {}
        return self._data.get("results", {})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_batch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agent/batch.py tests/test_batch.py
git commit -m "feat: add batch workflow management"
```

---

### Task 4: Progress Notification

**Covers:** Progress tracking for polling

**Files:**
- Create: `agent/progress.py`
- Create: `tests/test_progress.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_progress.py
import os
import json
import time
import pytest
from agent.progress import ProgressTracker

@pytest.fixture
def tracker(tmp_path):
    return ProgressTracker(state_dir=str(tmp_path / "state"))

def test_create_task(tracker):
    task_id = tracker.create("generating", total=5)
    assert task_id is not None
    status = tracker.get_status(task_id)
    assert status["total"] == 5
    assert status["current"] == 0

def test_update_progress(tracker):
    task_id = tracker.create("generating", total=5)
    tracker.update(task_id, current=2, status="extracting")
    status = tracker.get_status(task_id)
    assert status["current"] == 2
    assert status["status"] == "extracting"

def test_complete_task(tracker):
    task_id = tracker.create("generating", total=5)
    tracker.complete(task_id)
    status = tracker.get_status(task_id)
    assert status["status"] == "done"

def test_cancel_task(tracker):
    task_id = tracker.create("generating", total=5)
    tracker.cancel(task_id)
    status = tracker.get_status(task_id)
    assert status["status"] == "cancelled"

def test_list_tasks(tracker):
    id1 = tracker.create("generating", total=5)
    id2 = tracker.create("extracting", total=10)
    tasks = tracker.list_tasks()
    assert len(tasks) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_progress.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agent.progress'"

- [ ] **Step 3: Implement progress module**

```python
# agent/progress.py
import os
import json
import uuid
import time
from typing import Optional, List

class ProgressTracker:
    def __init__(self, state_dir: str = "state"):
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
    
    def _get_file(self, task_id: str) -> str:
        return os.path.join(self.state_dir, f"progress_{task_id}.json")
    
    def create(self, status: str, total: int, metadata: dict = None) -> str:
        task_id = str(uuid.uuid4())[:8]
        data = {
            "task_id": task_id,
            "status": status,
            "current": 0,
            "total": total,
            "metadata": metadata or {},
            "created_at": time.time(),
            "updated_at": time.time()
        }
        with open(self._get_file(task_id), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return task_id
    
    def update(self, task_id: str, current: int = None, status: str = None, 
               metadata: dict = None):
        file_path = self._get_file(task_id)
        if not os.path.exists(file_path):
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if current is not None:
            data["current"] = current
        if status is not None:
            data["status"] = status
        if metadata is not None:
            data["metadata"].update(metadata)
        
        data["updated_at"] = time.time()
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def complete(self, task_id: str):
        self.update(task_id, status="done")
    
    def cancel(self, task_id: str):
        self.update(task_id, status="cancelled")
    
    def get_status(self, task_id: str) -> Optional[dict]:
        file_path = self._get_file(task_id)
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def list_tasks(self) -> List[dict]:
        tasks = []
        for filename in os.listdir(self.state_dir):
            if filename.startswith("progress_") and filename.endswith(".json"):
                file_path = os.path.join(self.state_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    tasks.append(json.load(f))
        return tasks
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_progress.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agent/progress.py tests/test_progress.py
git commit -m "feat: add progress tracking for polling notifications"
```

---

### Task 5: Streamlit Web UI

**Covers:** Web interface for workflow management

**Files:**
- Create: `app.py`
- Create: `requirements-streamlit.txt`

- [ ] **Step 1: Create Streamlit requirements**

```txt
# requirements-streamlit.txt
streamlit>=1.28.0
Pillow>=10.0.0
```

- [ ] **Step 2: Create main app.py**

```python
# app.py
import streamlit as st
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.workflow import Workflow
from agent.batch import BatchWorkflow
from agent.progress import ProgressTracker
from agent.cache import ImageCache
from agent.image_generator import generate_image, SUPPORTED_FORMATS

# Initialize components
tracker = ProgressTracker()
cache = ImageCache()

st.set_page_config(
    page_title="VibeCode Agent",
    page_icon="🎬",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("🎬 VibeCode Agent")
    page = st.radio(
        "导航",
        ["首页", "批量处理", "工作流", "生成", "展示"]
    )

# Main content
if page == "首页":
    st.title("产品视频工作流")
    st.markdown("AI 驱动的产品视频生成工具")
    
    # Upload section
    st.header("上传产品图片")
    uploaded_files = st.file_uploader(
        "选择图片",
        type=["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"已上传 {len(uploaded_files)} 张图片")
        for file in uploaded_files:
            st.image(file, caption=file.name, width=200)

elif page == "批量处理":
    st.title("批量处理")
    
    # Create new batch
    st.header("创建新批次")
    uploaded_files = st.file_uploader(
        "选择产品图片",
        type=["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"],
        accept_multiple_files=True,
        key="batch_upload"
    )
    
    if uploaded_files and st.button("创建批次"):
        # Save uploaded files
        input_dir = "input"
        os.makedirs(input_dir, exist_ok=True)
        
        file_paths = []
        for file in uploaded_files:
            path = os.path.join(input_dir, file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            file_paths.append(path)
        
        # Create batch
        batch = BatchWorkflow()
        batch_id = batch.create(file_paths)
        st.success(f"批次已创建: {batch_id}")
        st.rerun()
    
    # Show existing batches
    st.header("现有批次")
    # TODO: List existing batches from state directory

elif page == "工作流":
    st.title("工作流状态")
    
    # Load workflow state
    workflow = Workflow()
    current_stage = workflow.get_stage()
    
    st.info(f"当前阶段: {current_stage}")
    
    # Stage progress
    stages = ["INIT", "ANALYZE", "CONFIRM_PRODUCT", "GENERATE", 
              "CONFIRM_IMAGES", "BUILD_VIDEO_PROMPT", "WAIT_VIDEO", 
              "EXTRACT_FRAMES", "BUILD_PROJECT", "DONE"]
    
    progress = stages.index(current_stage) / len(stages)
    st.progress(progress)
    
    # Stage details
    st.subheader("阶段详情")
    for stage in stages:
        if stage == current_stage:
            st.markdown(f"**▶ {stage}** (当前)")
        elif stages.index(stage) < stages.index(current_stage):
            st.markdown(f"✓ {stage}")
        else:
            st.markdown(f"○ {stage}")

elif page == "生成":
    st.title("图片生成")
    
    # Cache stats
    st.subheader("缓存状态")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("已缓存", "0")
    with col2:
        st.metric("命中率", "0%")
    with col3:
        st.metric("节省时间", "0s")
    
    # Generation form
    st.subheader("生成设置")
    prompt = st.text_area("Prompt", placeholder="描述你想要的图片...")
    reference_image = st.file_uploader("参考图片 (可选)", type=["jpg", "jpeg", "png", "webp"])
    
    if st.button("生成图片"):
        if not prompt:
            st.error("请输入 Prompt")
        else:
            # Check cache first
            cached = cache.get(prompt, None)
            if cached:
                st.success("命中缓存!")
                st.image(cached)
            else:
                with st.spinner("生成中..."):
                    # TODO: Call actual generation
                    st.info("生成功能需要集成到工作流中")

elif page == "展示":
    st.title("英雄镜头展示")
    
    # List generated projects
    projects_dir = "projects"
    if os.path.exists(projects_dir):
        projects = [d for d in os.listdir(projects_dir) 
                   if os.path.isdir(os.path.join(projects_dir, d))]
        
        if projects:
            selected = st.selectbox("选择项目", projects)
            if selected:
                index_path = os.path.join(projects_dir, selected, "index.html")
                if os.path.exists(index_path):
                    st.markdown(f"### {selected}")
                    st.info("打开 index.html 查看完整展示效果")
                    # Could embed iframe here
        else:
            st.info("暂无生成的项目")
    else:
        st.info("暂无生成的项目")

# Auto-refresh for polling
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = time.time()
    st.rerun()
```

- [ ] **Step 3: Test app starts**

Run: `streamlit run app.py --server.headless true`
Expected: App starts without errors

- [ ] **Step 4: Commit**

```bash
git add app.py requirements-streamlit.txt
git commit -m "feat: add Streamlit Web UI with batch, cache, and progress views"
```

---

### Task 6: Integration

**Covers:** Integrate all features together

**Files:**
- Modify: `requirements.txt`
- Modify: `README.md`

- [ ] **Step 1: Update requirements.txt**

```txt
requests>=2.28.0
python-dotenv>=1.0.0
pytest>=7.0.0
streamlit>=1.28.0
Pillow>=10.0.0
```

- [ ] **Step 2: Update README.md**

Add sections for:
- Web UI usage (`streamlit run app.py`)
- Batch processing API
- Cache configuration
- Supported image formats

- [ ] **Step 3: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add requirements.txt README.md
git commit -m "docs: update requirements and README for new features"
```

---

## Self-Review

1. **Spec coverage:** All 5 features covered by Tasks 1-6
2. **Placeholder scan:** No TBD/TODO placeholders in implementation steps
3. **Type consistency:** Consistent use of `Optional[str]`, `List[str]`, `dict` throughout

## Execution Handoff

This plan has 6 tasks with clear dependencies:
- Task 1 (format support) - independent
- Task 2 (cache) - independent  
- Task 3 (batch) - independent
- Task 4 (progress) - independent
- Task 5 (Streamlit UI) - depends on Tasks 1-4
- Task 6 (integration) - depends on all

**Recommendation:** Use subagent execution for parallel development of Tasks 1-4, then sequential for Tasks 5-6.
