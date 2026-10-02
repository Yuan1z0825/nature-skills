import sys
import unittest
from unittest import mock
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "cli/image2ppt/runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import numpy as np  # noqa: E402
from build_pptx_from_manifest import fitted_font_size  # noqa: E402
from text_hints import binarize_page, measure_leaves, xy_cut  # noqa: E402

IMAGE_SIZE = (1280, 720)


def draw_glyph_block(draw, x, y, glyph_h, chars=8, lines=1, color="#1a1a1a"):
    """Rows of hollow rectangles standing in for glyphs (font-free)."""
    char_w = max(4, round(glyph_h * 0.7))
    gap = max(2, glyph_h // 6)
    line_gap = max(2, round(glyph_h * 0.5))
    stroke = max(2, glyph_h // 6)
    for line in range(lines):
        top = y + line * (glyph_h + line_gap)
        for index in range(chars):
            left = x + index * (char_w + gap)
            draw.rectangle([left, top, left + char_w - 1, top + glyph_h - 1], outline=color, width=stroke)
    width = chars * (char_w + gap) - gap
    height = lines * glyph_h + (lines - 1) * line_gap
    return (x, y, width, height)


def detect(image):
    gray = np.asarray(image.convert("L"), dtype=np.float32)
    mask = binarize_page(gray)
    boxes = []
    height, width = gray.shape
    xy_cut(mask, 0, 0, max(6, round(height * 0.008)), max(14, round(width * 0.011)), boxes)
    return measure_leaves(gray, mask, boxes, 6)


def find_line_at(lines, box, tolerance=24):
    cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
    for line in lines:
        x, y, w, h = line["box_px"]
        if x - tolerance <= cx <= x + w + tolerance and y - tolerance <= cy <= y + h + tolerance:
            return line
    return None


class TextHintsTest(unittest.TestCase):
    def test_detects_lines_with_accurate_glyph_heights(self):
        image = Image.new("RGB", IMAGE_SIZE, "white")
        draw = ImageDraw.Draw(image)
        title = draw_glyph_block(draw, 100, 60, glyph_h=40, chars=10)
        body = draw_glyph_block(draw, 100, 200, glyph_h=18, chars=14, lines=2)
        label = draw_glyph_block(draw, 760, 420, glyph_h=12, chars=6)

        lines = detect(image)

        title_line = find_line_at(lines, title)
        self.assertIsNotNone(title_line)
        self.assertAlmostEqual(40, title_line["glyph_height_px"], delta=2)
        body_line = find_line_at(lines, body)
        self.assertIsNotNone(body_line)
        self.assertAlmostEqual(18, body_line["glyph_height_px"], delta=2)
        label_line = find_line_at(lines, label)
        self.assertIsNotNone(label_line)
        self.assertAlmostEqual(12, label_line["glyph_height_px"], delta=2)

    def test_light_text_on_dark_card_is_detected(self):
        image = Image.new("RGB", IMAGE_SIZE, "white")
        draw = ImageDraw.Draw(image)
        # Card aligned inside binarization tiles so its interior tiles are
        # uniformly dark with light glyphs.
        draw.rectangle([384, 192, 768, 384], fill="#15233f")
        block = draw_glyph_block(draw, 430, 260, glyph_h=24, chars=8, color="#f4f6fa")

        lines = detect(image)

        found = find_line_at(lines, block)
        self.assertIsNotNone(found, [line["box_px"] for line in lines])
        self.assertAlmostEqual(24, found["glyph_height_px"], delta=2)

    def test_photos_and_dividers_are_not_reported(self):
        # Text sits in its own row band: sharing rows with a tall photo is a
        # known detection limitation (hints are advisory; the author fills
        # missed lines by reading the source).
        image = Image.new("RGB", IMAGE_SIZE, "white")
        draw = ImageDraw.Draw(image)
        photo = (800, 80, 300, 200)
        draw.rectangle([photo[0], photo[1], photo[0] + photo[2], photo[1] + photo[3]], fill="#3a4a3a")
        draw.rectangle([100, 400, 1100, 403], fill="#888888")  # full-width divider
        text = draw_glyph_block(draw, 100, 500, glyph_h=20, chars=10)

        lines = detect(image)

        self.assertIsNotNone(find_line_at(lines, text))
        # Neither the photo body nor the divider may masquerade as a text line.
        photo_hits = [
            line for line in lines
            if line["box_px"][0] >= photo[0] - 5 and line["box_px"][1] >= photo[1] - 5
            and line["box_px"][0] + line["box_px"][2] <= photo[0] + photo[2] + 5
            and line["box_px"][1] + line["box_px"][3] <= photo[1] + photo[3] + 5
        ]
        self.assertEqual([], photo_hits)
        divider_hits = [line for line in lines if 392 < line["box_px"][1] < 412]
        self.assertEqual([], divider_hits)

    def test_thin_bridge_does_not_merge_blocks(self):
        image = Image.new("RGB", IMAGE_SIZE, "white")
        draw = ImageDraw.Draw(image)
        left = draw_glyph_block(draw, 100, 300, glyph_h=22, chars=6)
        right = draw_glyph_block(draw, 700, 300, glyph_h=22, chars=6)
        # Thin arrow bridging the gap between the two blocks.
        draw.rectangle([left[0] + left[2] + 10, 310, 690, 313], fill="#1a1a1a")

        lines = detect(image)

        left_line = find_line_at(lines, left)
        right_line = find_line_at(lines, right)
        self.assertIsNotNone(left_line)
        self.assertIsNotNone(right_line)
        self.assertNotEqual(left_line["box_px"], right_line["box_px"], "bridge must not merge the two blocks")


class MeasuredFontTrustTest(unittest.TestCase):
    def make_item(self, **extra):
        item = {
            "text": "标题文字测试",
            "font_size": 30.0,
            "width": 3.0,
            "height": 0.6,
        }
        item.update(extra)
        return item

    def test_measured_boxes_skip_the_safety_shrink(self):
        manifest = {}
        plain = fitted_font_size(self.make_item(), manifest)
        measured = fitted_font_size(self.make_item(font_size_source="measured"), manifest)
        self.assertAlmostEqual(plain / 0.9, measured, places=6)

    def test_measured_boxes_still_clamp_at_geometric_limit(self):
        item = self.make_item(font_size_source="measured", font_size=200.0)
        fitted = fitted_font_size(item, {})
        self.assertLess(fitted, 200.0)


class SizeGroupClusterTest(unittest.TestCase):
    def test_same_level_jitter_collapses_to_one_size(self):
        from text_hints import attach_font_sizes
        lines = [{"glyph_height_px": g, "box_px": [0, 0, 100, 30], "line_count": 1}
                 for g in (37.0, 38.0, 39.0, 40.0, 34.0)]
        attach_font_sizes(lines, {"source": {"width_px": 1280, "height_px": 720},
                                  "slide": {"width": 13.333, "height": 7.5}})
        metric_groups = {l["size_group"] for l in lines[:4]}
        self.assertEqual(1, len(metric_groups), "37-40px jitter must collapse into one group")
        sizes = {l["font_pt_if_cjk"] for l in lines[:4]}
        self.assertEqual(1, len(sizes))
        self.assertNotEqual(lines[4]["size_group"], lines[0]["size_group"], "34px header is a different level")

    def test_long_smooth_chain_is_force_split(self):
        from text_hints import cluster_glyph_heights
        values = [17.0, 18.0, 18.5, 19.0, 19.0, 19.5]
        clusters = cluster_glyph_heights(values)
        for cluster in clusters:
            members = [values[i] for i in cluster]
            self.assertLessEqual(max(members) / min(members), 1.12 + 1e-9)


class DeckTextHintsTest(unittest.TestCase):
    def test_offline_fallback_writes_hints_per_page(self):
        import json as _json
        import os as _os
        import subprocess as _sub
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            for page_id in ("page_001", "page_002"):
                page_dir = run_dir / "pages" / page_id
                page_dir.mkdir(parents=True)
                image = Image.new("RGB", IMAGE_SIZE, "white")
                draw_glyph_block(ImageDraw.Draw(image), 100, 100, glyph_h=30, chars=8)
                image.save(page_dir / "source.png")
            (run_dir / "deck_manifest.json").write_text(_json.dumps(
                {"schema_version": 1, "run_id": "t", "input_type": "images", "pages": []}))
            (run_dir / "page_jobs.json").write_text(_json.dumps({
                "schema_version": 1, "run_id": "t", "max_concurrent_pages": 6,
                "pages": [{"page_id": p, "status": "pending", "page_dir": f"pages/{p}"}
                          for p in ("page_001", "page_002")]}))

            env = dict(_os.environ)
            env.pop("PADDLE_OCR_TOKEN", None)
            env["IMAGE2PPT_CONFIG_HOME"] = str(Path(tmp) / "nohome")  # 避免读取本机 token 配置
            result = _sub.run([sys.executable, str(RUNTIME_DIR / "deck_text_hints.py"), str(run_dir)],
                              env=env, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("backend=builtin-ink", result.stdout)
            for page_id in ("page_001", "page_002"):
                hints_path = run_dir / "pages" / page_id / "text_hints.json"
                self.assertTrue(hints_path.exists())
                hints = _json.loads(hints_path.read_text(encoding="utf-8"))
                self.assertEqual("builtin-ink", hints["backend"])
                self.assertTrue(hints["lines"], "fallback detector must report the drawn text")
                self.assertTrue((run_dir / "pages" / page_id / "text_hints.png").exists())


class PaddleScaleTest(unittest.TestCase):
    def test_ocr_coordinates_rescale_to_source_resolution(self):
        from paddle_text_hints import text_blocks_to_lines

        image = Image.new("RGB", IMAGE_SIZE, "white")
        true_box = draw_glyph_block(ImageDraw.Draw(image), 200, 100, glyph_h=24, chars=8)
        gray = np.asarray(image.convert("L"), dtype=np.float32)
        # OCR 在半分辨率渲染页面：bbox 坐标除以 2，需要 scale 2 映射回 source。
        half_bbox = [true_box[0] / 2 - 3, true_box[1] / 2 - 3,
                     (true_box[0] + true_box[2]) / 2 + 3, (true_box[1] + true_box[3]) / 2 + 3]
        pruned = {"parsing_res_list": [
            {"block_label": "text", "block_content": "示例文字", "block_bbox": half_bbox}]}

        lines = text_blocks_to_lines(pruned, gray, 6, scale_x=2.0, scale_y=2.0)

        self.assertEqual(1, len(lines))
        line = lines[0]
        self.assertEqual("ink-measured", line["glyph_source"])
        self.assertAlmostEqual(24, line["glyph_height_px"], delta=2)
        cx = line["box_px"][0] + line["box_px"][2] / 2
        self.assertAlmostEqual(true_box[0] + true_box[2] / 2, cx, delta=10)


if __name__ == "__main__":
    unittest.main()
