from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path


def main() -> None:
    command_name = Path(sys.argv[0]).name or "image2ppt"
    if command_name in {"cli.py", "__main__.py"}:
        command_name = "image2ppt"
    runtime_dir = Path(__file__).resolve().parent / "runtime"
    script = runtime_dir / "main.py"
    if not script.exists():
        raise RuntimeError(f"runtime entrypoint not found: {script}")

    os.environ.setdefault("IMAGE2PPT_CLI_PROG", command_name)
    sys.path.insert(0, str(runtime_dir))
    sys.argv = [command_name, *sys.argv[1:]]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
