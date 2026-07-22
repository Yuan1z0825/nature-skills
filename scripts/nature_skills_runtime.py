"""Small startup defaults for the isolated Nature Skills Python runtime."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def configure_matplotlib_cache() -> None:
    """Give Matplotlib a sandbox-writable cache without overriding user choice."""
    if os.environ.get("MPLCONFIGDIR"):
        return
    try:
        user_suffix = str(os.getuid()) if hasattr(os, "getuid") else "user"
        cache_dir = Path(tempfile.gettempdir()) / f"nature-skills-matplotlib-cache-{user_suffix}"
        cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError:
        return
    os.environ["MPLCONFIGDIR"] = str(cache_dir)


configure_matplotlib_cache()
