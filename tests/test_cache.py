import os
import json
import time
import pytest
from agent.cache import ImageCache


@pytest.fixture
def cache(tmp_path):
    """Create a fresh ImageCache with temp directories"""
    state_dir = str(tmp_path / "state" / "cache")
    image_dir = str(tmp_path / "generated" / "cache")
    return ImageCache(state_dir=state_dir, image_dir=image_dir)


@pytest.fixture
def cache_with_entries(cache, tmp_path):
    """Create cache with some pre-existing entries"""
    # Create a fake image file to store
    img_path = tmp_path / "input.png"
    img_path.write_bytes(b"fake-image-data")

    cache.set("a beautiful sunset", str(img_path), output_ext=".png")
    cache.set("a dark forest", None)
    return cache


class TestImageCacheKey:
    def test_hash_deterministic(self, cache):
        key1 = cache.make_key("hello world")
        key2 = cache.make_key("hello world")
        assert key1 == key2

    def test_hash_different_for_different_prompts(self, cache):
        key1 = cache.make_key("prompt A")
        key2 = cache.make_key("prompt B")
        assert key1 != key2

    def test_hash_includes_reference_image(self, cache):
        key_no_ref = cache.make_key("test prompt")
        key_with_ref = cache.make_key("test prompt", "ref.png")
        assert key_no_ref != key_with_ref

    def test_hash_length(self, cache):
        key = cache.make_key("test")
        assert len(key) == 32  # MD5 hex digest is 32 chars


class TestImageCacheGetSet:
    def test_set_and_get_metadata(self, cache, tmp_path):
        img_path = tmp_path / "img.png"
        img_path.write_bytes(b"image-bytes")

        cache.set("test prompt", str(img_path), output_ext=".png")
        meta = cache.get("test prompt")
        assert meta is not None
        assert meta["prompt"] == "test prompt"
        assert meta["output_ext"] == ".png"

    def test_get_miss_returns_none(self, cache):
        assert cache.get("nonexistent prompt") is None

    def test_set_stores_image_copy(self, cache, tmp_path):
        img_path = tmp_path / "src.png"
        img_path.write_bytes(b"image-bytes")

        cache.set("test", str(img_path), output_ext=".png")
        key = cache.make_key("test")
        cached_path = os.path.join(cache.image_dir, f"{key}.png")
        assert os.path.exists(cached_path)
        with open(cached_path, "rb") as f:
            assert f.read() == b"image-bytes"

    def test_set_without_image(self, cache):
        cache.set("text only prompt", None)
        meta = cache.get("text only prompt")
        assert meta is not None
        assert meta["prompt"] == "text only prompt"
        assert meta.get("output_ext") is None

    def test_set_with_reference_image(self, cache):
        cache.set("prompt", None, reference_image="ref.jpg")
        meta = cache.get("prompt", reference_image="ref.jpg")
        assert meta is not None

    def test_different_reference_image_different_cache(self, cache):
        cache.set("prompt", None, reference_image="a.png")
        cache.set("prompt", None, reference_image="b.png")
        meta_a = cache.get("prompt", reference_image="a.png")
        meta_b = cache.get("prompt", reference_image="b.png")
        assert meta_a is not None
        assert meta_b is not None
        assert meta_a["reference_image"] != meta_b["reference_image"]


class TestImageCacheClear:
    def test_clear_removes_all(self, cache, tmp_path):
        img = tmp_path / "img.png"
        img.write_bytes(b"data")
        cache.set("prompt1", str(img), output_ext=".png")
        cache.set("prompt2", None)

        cache.clear()
        assert cache.get("prompt1") is None
        assert cache.get("prompt2") is None

    def test_clear_removes_files(self, cache, tmp_path):
        img = tmp_path / "img.png"
        img.write_bytes(b"data")
        cache.set("prompt1", str(img), output_ext=".png")
        key = cache.make_key("prompt1")
        assert os.path.exists(os.path.join(cache.image_dir, f"{key}.png"))
        assert os.path.exists(os.path.join(cache.state_dir, f"{key}.json"))

        cache.clear()
        assert not os.path.exists(os.path.join(cache.image_dir, f"{key}.png"))
        assert not os.path.exists(os.path.join(cache.state_dir, f"{key}.json"))


class TestImageCacheTTL:
    def test_expired_entry_returns_none(self, cache, tmp_path):
        img = tmp_path / "img.png"
        img.write_bytes(b"data")

        cache.set("prompt", str(img), output_ext=".png", ttl=0)
        time.sleep(0.01)
        assert cache.get("prompt") is None

    def test_valid_entry_returns_metadata(self, cache, tmp_path):
        img = tmp_path / "img.png"
        img.write_bytes(b"data")

        cache.set("prompt", str(img), output_ext=".png", ttl=60)
        meta = cache.get("prompt")
        assert meta is not None

    def test_expired_entry_file_cleaned(self, cache, tmp_path):
        img = tmp_path / "img.png"
        img.write_bytes(b"data")

        cache.set("prompt", str(img), output_ext=".png", ttl=0)
        time.sleep(0.01)
        cache.get("prompt")  # triggers cleanup
        key = cache.make_key("prompt")
        assert not os.path.exists(os.path.join(cache.state_dir, f"{key}.json"))

    def test_default_ttl_none_never_expires(self, cache, tmp_path):
        img = tmp_path / "img.png"
        img.write_bytes(b"data")

        cache.set("prompt", str(img), output_ext=".png")
        meta = cache.get("prompt")
        assert meta is not None
