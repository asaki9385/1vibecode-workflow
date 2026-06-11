import os
import json
import time
import hashlib
import shutil


class ImageCache:
    """Cache generated images based on prompt + reference_image hash."""

    def __init__(self, state_dir: str = "state/cache", image_dir: str = "generated/cache"):
        self.state_dir = state_dir
        self.image_dir = image_dir
        os.makedirs(state_dir, exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)

    def make_key(self, prompt: str, reference_image: str = None) -> str:
        """Create MD5 hash from prompt and optional reference_image."""
        content = prompt
        if reference_image:
            content += f"\n{reference_image}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def set(self, prompt: str, image_path: str = None, reference_image: str = None,
            output_ext: str = None, ttl: int = None) -> str:
        """Store image and metadata in cache.

        Args:
            prompt: The generation prompt
            image_path: Path to image file to cache (None for metadata-only)
            reference_image: Reference image path used during generation
            output_ext: File extension for cached image
            ttl: Time-to-live in seconds (None = never expires)

        Returns:
            Cache key (MD5 hash)
        """
        key = self.make_key(prompt, reference_image)

        if image_path and os.path.exists(image_path):
            cached_image = os.path.join(self.image_dir, f"{key}{output_ext or ''}")
            shutil.copy2(image_path, cached_image)

        metadata = {
            "prompt": prompt,
            "reference_image": reference_image,
            "output_ext": output_ext,
            "cached_at": time.time(),
            "ttl": ttl,
        }

        meta_path = os.path.join(self.state_dir, f"{key}.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return key

    def get(self, prompt: str, reference_image: str = None):
        """Retrieve cached metadata if entry exists and is not expired.

        Returns:
            Metadata dict or None if miss/expired
        """
        key = self.make_key(prompt, reference_image)
        meta_path = os.path.join(self.state_dir, f"{key}.json")

        if not os.path.exists(meta_path):
            return None

        with open(meta_path, "r") as f:
            meta = json.load(f)

        ttl = meta.get("ttl")
        if ttl is not None:
            if time.time() - meta["cached_at"] > ttl:
                self._remove(key)
                return None

        return meta

    def clear(self):
        """Remove all cached entries."""
        for filename in os.listdir(self.state_dir):
            if filename.endswith(".json"):
                key = filename[:-5]
                self._remove(key)

    def _remove(self, key: str):
        """Remove a single cache entry by key."""
        meta_path = os.path.join(self.state_dir, f"{key}.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            ext = meta.get("output_ext", "")
            img_path = os.path.join(self.image_dir, f"{key}{ext or ''}")
            if os.path.exists(img_path):
                os.remove(img_path)
            os.remove(meta_path)
