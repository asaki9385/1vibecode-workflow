import os
import sys
import streamlit as st
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent.workflow import Workflow, STAGES
from agent.batch import BatchWorkflow, BatchStatus
from agent.cache import ImageCache
from agent.progress import ProgressTracker, TaskStatus
from agent.image_generator import validate_image_format, SUPPORTED_FORMATS

PROJECT_ROOT = Path(__file__).parent
GENERATED_DIR = PROJECT_ROOT / "generated"
PROJECTS_DIR = PROJECT_ROOT / "projects"

st.set_page_config(
    page_title="VibeCode Agent",
    page_icon="🎨",
    layout="wide"
)

if "page" not in st.session_state:
    st.session_state.page = "首页"


def get_workflow():
    return Workflow(str(PROJECT_ROOT / "state" / "workflow.json"))


def get_batch():
    return BatchWorkflow(str(PROJECT_ROOT / "state" / "batch.json"))


def get_cache():
    return ImageCache(
        str(PROJECT_ROOT / "state" / "cache"),
        str(GENERATED_DIR / "cache")
    )


def get_progress():
    return ProgressTracker(str(PROJECT_ROOT / "state" / "progress"))


def page_home():
    st.header("首页 - 产品图片上传")

    uploaded = st.file_uploader(
        "上传产品图片",
        type=[ext.lstrip(".") for ext in SUPPORTED_FORMATS],
        accept_multiple_files=False
    )

    if uploaded:
        temp_dir = PROJECT_ROOT / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / uploaded.name
        temp_path.write_bytes(uploaded.getvalue())

        if validate_image_format(str(temp_path)):
            st.success(f"图片格式验证通过: {uploaded.name}")
            st.image(str(temp_path), caption=uploaded.name, use_container_width=True)
            st.session_state["uploaded_image"] = str(temp_path)
        else:
            st.error(f"不支持的图片格式。支持的格式: {', '.join(sorted(SUPPORTED_FORMATS))}")

    existing = st.session_state.get("uploaded_image")
    if existing and os.path.exists(existing):
        st.info(f"当前已上传: {Path(existing).name}")

    st.subheader("上传历史")
    if "upload_history" not in st.session_state:
        st.session_state.upload_history = []

    for entry in st.session_state.upload_history:
        if os.path.exists(entry):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(Path(entry).name)
            with col2:
                if st.button("查看", key=f"view_{Path(entry).name}"):
                    st.image(entry, caption=Path(entry).name, width=300)


def page_batch():
    st.header("批量处理")

    batch = get_batch()

    st.subheader("创建新批次")
    uploaded_files = st.file_uploader(
        "选择图片文件",
        type=[ext.lstrip(".") for ext in SUPPORTED_FORMATS],
        accept_multiple_files=True,
        key="batch_upload"
    )

    if uploaded_files and st.button("创建批次"):
        temp_dir = PROJECT_ROOT / "temp"
        temp_dir.mkdir(exist_ok=True)
        paths = []
        for f in uploaded_files:
            p = temp_dir / f.name
            p.write_bytes(f.getvalue())
            paths.append(str(p))
        batch.create(paths)
        st.success(f"已创建批次，包含 {len(paths)} 张图片")
        st.rerun()

    st.subheader("现有批次")
    total = batch.get_total()
    if total > 0:
        completed = batch.get_completed()
        st.progress(batch.progress(), text=f"进度: {completed}/{total}")
        st.write(f"待处理: {total - completed} | 已完成: {completed}")

        tasks = batch._items
        for item in tasks:
            status_icon = {
                BatchStatus.PENDING: "⏳",
                BatchStatus.COMPLETED: "✅",
                BatchStatus.SKIPPED: "⏭️"
            }.get(item.status, "❓")
            st.text(f"{status_icon} {Path(item.image_path).name} - {item.status.value}")
    else:
        st.info("暂无批次数据")

    if total > 0:
        st.subheader("批次操作")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("重置批次"):
                batch.create([])
                st.success("批次已重置")
                st.rerun()
        with col2:
            next_item = batch.get_next()
            if next_item:
                st.text(f"下一个待处理: {Path(next_item.image_path).name}")


def page_workflow():
    st.header("工作流状态")

    wf = get_workflow()
    current_stage = wf.get_stage()

    stage_index = STAGES.index(current_stage) if current_stage in STAGES else 0
    st.progress((stage_index + 1) / len(STAGES), text=f"当前阶段: {current_stage}")
    st.write(f"进度: {stage_index + 1}/{len(STAGES)}")

    st.subheader("阶段详情")
    for i, stage in enumerate(STAGES):
        icon = "✅" if i < stage_index else ("➡️" if i == stage_index else "⬜")
        st.text(f"{icon} {stage}")

    st.subheader("工作流数据")
    for key in ["image_analysis", "effect_type", "custom_desc", "aspect_ratio"]:
        value = wf.get_data(key)
        if value:
            st.write(f"**{key}**: {value}")

    st.subheader("操作")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("重置工作流"):
            wf.reset()
            st.success("工作流已重置")
            st.rerun()
    with col2:
        if stage_index > 0:
            if st.button("返回上一阶段"):
                prev_stage = STAGES[stage_index - 1]
                wf.set_stage(prev_stage)
                st.rerun()


def page_generate():
    st.header("生成")

    cache = get_cache()
    st.subheader("缓存统计")
    cache_dir = cache.state_dir
    if os.path.exists(cache_dir):
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]
        st.write(f"缓存条目数: {len(cache_files)}")
    else:
        st.write("缓存条目数: 0")

    st.subheader("生成表单")
    prompt = st.text_area("Prompt", placeholder="描述要生成的图片...")
    ref_image = st.text_input("参考图片路径（可选）", placeholder="本地图片路径或URL")
    output_name = st.text_input("输出文件名", placeholder="output.png")

    if st.button("生成图片"):
        if not prompt:
            st.error("请输入 Prompt")
        else:
            output_path = str(GENERATED_DIR / output_name) if output_name else str(GENERATED_DIR / f"gen_{hash(prompt) & 0xFFFF:04x}.png")
            try:
                from agent.image_generator import generate_image
                with st.spinner("正在生成图片..."):
                    result = generate_image(prompt, output_path, ref_image or None)
                st.success(f"图片已生成: {result}")
                cache.set(prompt, result, ref_image or None, ".png")
                st.image(result, caption="生成结果")
            except Exception as e:
                st.error(f"生成失败: {e}")

    st.subheader("缓存查询")
    query_prompt = st.text_input("查询 Prompt", key="cache_query")
    if st.button("查询缓存"):
        result = cache.get(query_prompt)
        if result:
            st.json(result)
            cached_at = result.get("cached_at")
            if cached_at:
                import time
                age = time.time() - cached_at
                st.write(f"缓存年龄: {age/3600:.1f} 小时")
        else:
            st.info("未找到缓存")

    if st.button("清空缓存"):
        cache.clear()
        st.success("缓存已清空")


def page_display():
    st.header("展示")

    st.subheader("已生成项目")
    if PROJECTS_DIR.exists():
        projects = [d for d in PROJECTS_DIR.iterdir() if d.is_dir()]
        if projects:
            selected = st.selectbox("选择项目", [p.name for p in projects])
            project_dir = PROJECTS_DIR / selected

            st.write(f"项目路径: {project_dir}")

            image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
            images = [
                f for f in project_dir.iterdir()
                if f.suffix.lower() in image_extensions
            ]

            if images:
                st.subheader(f"项目图片 ({len(images)})")
                cols = st.columns(3)
                for i, img in enumerate(images):
                    with cols[i % 3]:
                        st.image(str(img), caption=img.name, use_container_width=True)
            else:
                st.info("项目中暂无图片")
        else:
            st.info("暂无已生成的项目")
    else:
        st.info("暂无已生成的项目")

    st.subheader("Hero Shot 播放器")
    if "hero_shots" not in st.session_state:
        st.session_state.hero_shots = []
        if PROJECTS_DIR.exists():
            for project in PROJECTS_DIR.iterdir():
                if project.is_dir():
                    for f in project.iterdir():
                        if f.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                            st.session_state.hero_shots.append(str(f))

    if st.session_state.hero_shots:
        idx = st.slider("选择图片", 0, len(st.session_state.hero_shots) - 1, 0)
        current = st.session_state.hero_shots[idx]
        st.image(current, caption=Path(current).name, use_container_width=True)
        st.write(f"图片 {idx + 1}/{len(st.session_state.hero_shots)}")
    else:
        st.info("暂无可用的 Hero Shot")


PAGES = {
    "首页": page_home,
    "批量处理": page_batch,
    "工作流": page_workflow,
    "生成": page_generate,
    "展示": page_display
}

with st.sidebar:
    st.title("VibeCode Agent")
    st.divider()
    for page_name in PAGES:
        if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name
            st.rerun()
    st.divider()
    st.caption("自动刷新: 5秒")
    if st.button("立即刷新", use_container_width=True):
        st.rerun()

page_func = PAGES.get(st.session_state.page)
if page_func:
    page_func()

st.markdown("---")
st.caption("VibeCode Agent - Web UI | Auto-refresh: 5s")

import time
time.sleep(5)
st.rerun()
