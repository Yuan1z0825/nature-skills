from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StaticIndependenceTests(unittest.TestCase):
    def test_runtime_prompt_and_operational_docs_have_no_cross_skill_dependency(self) -> None:
        forbidden = [
            "-".join(("image", "to", "editable", "ppt", "skill")),
            "-".join(("image", "to", "editable", "ppt")),
            "-".join(("ppt", "to", "editable")),
            "edit" + "ppt_skill_root",
            "sibling" + " runtime",
            "IMAGE2PPT_" + "EDITPPT",
            "shutil.which(" + '"edit' + 'ppt"' + ")",
        ]
        roots = [
            ROOT / "cli",
            ROOT / "scripts",
            ROOT / "prompts",
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "README_EN.md",
            ROOT / "references",
            ROOT / "agents",
            ROOT / ".github",
            ROOT / "NOTICE.md",
            ROOT / "config.example.yaml",
        ]
        hits = []
        for root in roots:
            paths = [root] if root.is_file() else root.rglob("*")
            for path in paths:
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                if path == ROOT / "NOTICE.md":
                    continue
                if path.suffix not in {".py", ".md", ".yaml", ".yml", ".toml", ".example"}:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                for token in forbidden:
                    if token in text:
                        hits.append(f"{path.relative_to(ROOT)}: {token}")
        self.assertEqual(hits, [])

    def test_python_imports_resolve_inside_runtime_or_normal_packages(self) -> None:
        runtime = ROOT / "cli" / "image2ppt" / "runtime"
        self.assertTrue((runtime / "deck_run_state.py").is_file())
        self.assertTrue((runtime / "paddle_text_hints.py").is_file())
        self.assertTrue((runtime / "build_pptx_from_manifest.py").is_file())
        self.assertFalse((ROOT / "scripts" / "runtime_paths.py").read_text(encoding="utf-8").find("SKILLS_ROOT") >= 0)


if __name__ == "__main__":
    unittest.main()
