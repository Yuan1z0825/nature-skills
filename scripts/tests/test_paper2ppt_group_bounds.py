import importlib.util
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
import zipfile

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "nature-paper2ppt" / "scripts" / "audit_pptx_quality.py"
spec = importlib.util.spec_from_file_location("group_bounds", SCRIPT)
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)


def shape(x=1400, y=100, w=200, h=100, kind="sp"):
    props = "p:xfrm" if kind == "graphicFrame" else "a:xfrm"
    xfrm = f'<{props}><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></{props}>'
    return f'<p:{kind}><p:spPr>{xfrm}</p:spPr><a:t>Text</a:t></p:{kind}>'


def group(child, x=100, y=100, w=200, h=100, cx=1400, cy=100, cw=200, ch=100, attrs=""):
    return (f'<p:grpSp><p:grpSpPr><a:xfrm {attrs}><a:off x="{x}" y="{y}"/>'
            f'<a:ext cx="{w}" cy="{h}"/><a:chOff x="{cx}" y="{cy}"/>'
            f'<a:chExt cx="{cw}" cy="{ch}"/></a:xfrm></p:grpSpPr>{child}</p:grpSp>')


def root(content):
    return ET.fromstring(f'<p:sld xmlns:p="{audit.NS["p"]}" xmlns:a="{audit.NS["a"]}"><p:cSld><p:spTree>{content}</p:spTree></p:cSld></p:sld>')


def bounds(content):
    result = audit.extract_shapes(root(content))
    assert len(result) == 1
    s = result[0]
    return s.left, s.top, s.width, s.height


def test_translated_child_uses_slide_coordinates():
    assert bounds(group(shape())) == (100, 100, 200, 100)


def test_scaled_and_nested_groups_compose():
    assert bounds(group(shape(), w=400, h=300)) == (100, 100, 400, 300)
    nested = group(group(shape()), cx=0, cy=0, cw=400, ch=400, w=800, h=800)
    assert bounds(nested) == (300, 300, 400, 200)


def test_group_rotation_and_flip_transform_corners():
    assert bounds(group(shape(), attrs='rot="5400000"')) == (150, 50, 100, 200)
    assert bounds(group(shape(x=1400, w=50), attrs='flipH="1"')) == (250, 100, 50, 100)


def test_images_tables_and_ungrouped_shapes_remain_supported():
    for kind in ("sp", "pic", "graphicFrame"):
        assert bounds(group(shape(kind=kind))) == (100, 100, 200, 100)
    assert bounds(shape(x=10, y=20)) == (10, 20, 200, 100)


def test_real_out_of_bounds_group_still_blocks(tmp_path):
    for left, expected in ((100, False), (1200, True)):
        slide = root(group(shape(), x=left))
        path = tmp_path / f"group-{left}.pptx"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("ppt/presentation.xml", f'<p:presentation xmlns:p="{audit.NS["p"]}"><p:sldSz cx="1000" cy="750"/></p:presentation>')
            zf.writestr("ppt/slides/slide1.xml", ET.tostring(slide))
        result = audit.audit_pptx(path)
        assert any(f["code"] == "shape_out_of_bounds" for f in result["findings"]) == expected
