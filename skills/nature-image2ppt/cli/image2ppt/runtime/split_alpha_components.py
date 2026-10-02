#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def parse_names(value, option="--names"):
    if not value:
        return []
    names = [item.strip() for item in value.split(",") if item.strip()]
    for name in names:
        path = Path(name)
        if (
            "\x00" in name
            or "/" in name
            or "\\" in name
            or name in {".", ".."}
            or path.is_absolute()
            or path.drive
            or path.name != name
        ):
            raise SystemExit(f"{option} entries must be safe filename components: {name}")
    return names


NEIGHBORS = {
    4: ((1, 0), (-1, 0), (0, 1), (0, -1)),
    8: ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)),
}


def foreground_mask(alpha, threshold, close_radius):
    mask = alpha.point(lambda p: 255 if p > threshold else 0, mode="L")
    if close_radius <= 0:
        return mask
    size = close_radius * 2 + 1
    return mask.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.MinFilter(size))


def component_boxes(mask, min_area, connectivity):
    width, height = mask.size
    pixels = mask.load()
    seen = bytearray(width * height)
    components = []
    neighbors = NEIGHBORS[connectivity]

    for y in range(height):
        for x in range(width):
            idx = y * width + x
            if seen[idx] or pixels[x, y] == 0:
                continue

            stack = [(x, y)]
            seen[idx] = 1
            min_x = max_x = x
            min_y = max_y = y
            area = 0

            while stack:
                cx, cy = stack.pop()
                area += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for dx, dy in neighbors:
                    nx = cx + dx
                    ny = cy + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        nidx = ny * width + nx
                        if not seen[nidx] and pixels[nx, ny] != 0:
                            seen[nidx] = 1
                            stack.append((nx, ny))

            if area >= min_area:
                components.append({"area": area, "box": [min_x, min_y, max_x + 1, max_y + 1]})

    return components


def gap_between(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    dx = max(0, max(ax1, bx1) - min(ax2, bx2))
    dy = max(0, max(ay1, by1) - min(ay2, by2))
    return max(dx, dy)


def union_box(a, b):
    return [
        min(a[0], b[0]),
        min(a[1], b[1]),
        max(a[2], b[2]),
        max(a[3], b[3]),
    ]


def box_area(box):
    return max(1, box[2] - box[0]) * max(1, box[3] - box[1])


def should_merge(a, b, max_gap, max_union_growth):
    if gap_between(a["box"], b["box"]) > max_gap:
        return False
    union = union_box(a["box"], b["box"])
    separate_area = box_area(a["box"]) + box_area(b["box"])
    return box_area(union) / max(1, separate_area) <= max_union_growth


def merge_fragments(components, max_gap, max_union_growth):
    if max_gap <= 0:
        return components
    merged = [dict(component, merged_count=1) for component in components]
    changed = True
    while changed:
        changed = False
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                if not should_merge(merged[i], merged[j], max_gap, max_union_growth):
                    continue
                merged[i] = {
                    "area": merged[i]["area"] + merged[j]["area"],
                    "box": union_box(merged[i]["box"], merged[j]["box"]),
                    "merged_count": merged[i]["merged_count"] + merged[j]["merged_count"],
                }
                del merged[j]
                changed = True
                break
            if changed:
                break
    return merged


def sort_components(components, mode):
    if mode == "area":
        return sorted(components, key=lambda item: item["area"], reverse=True)
    if mode == "y":
        return sorted(components, key=lambda item: (item["box"][1], item["box"][0]))
    return sorted(components, key=lambda item: (item["box"][0], item["box"][1]))


def extract_component_asset(image, box, pad, square):
    width, height = image.size
    left, top, right, bottom = box
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(width, right + pad)
    bottom = min(height, bottom + pad)
    component_image = image.crop((left, top, right, bottom))
    if not square:
        return component_image, [left, top, right, bottom]

    side = max(component_image.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(
        component_image,
        ((side - component_image.size[0]) // 2, (side - component_image.size[1]) // 2),
    )
    return canvas, [left, top, right, bottom]


def write_contact_sheet(items, out_path):
    if not items:
        return
    thumb = 180
    label_h = 28
    cols = min(5, len(items))
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb, rows * (thumb + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(items):
        row, col = divmod(index, cols)
        preview = item["image"].copy()
        preview.thumbnail((thumb - 16, thumb - 16))
        x = col * thumb + (thumb - preview.width) // 2
        y = row * (thumb + label_h) + (thumb - preview.height) // 2
        checker = Image.new("RGB", preview.size, "#f4f4f4")
        checker.paste(preview, mask=preview.getchannel("A"))
        sheet.paste(checker, (x, y))
        draw.text((col * thumb + 8, row * (thumb + label_h) + thumb), item["name"], fill="black")
    sheet.save(out_path)


def main():
    parser = argparse.ArgumentParser(description="Split a transparent asset sheet into component PNG files.")
    parser.add_argument("--input", required=True, help="RGBA asset sheet after chroma-key removal")
    parser.add_argument("--out-dir", required=True, help="Directory for split PNG assets")
    parser.add_argument("--names", help="Comma-separated output names in sorted component order")
    parser.add_argument("--sort", choices=["x", "y", "area"], default="x")
    parser.add_argument("--threshold", type=int, default=20, help="Alpha threshold for foreground pixels")
    parser.add_argument("--min-area", type=int, default=1000, help="Minimum connected area to keep")
    parser.add_argument("--connectivity", type=int, choices=[4, 8], default=8)
    parser.add_argument("--close-radius", type=int, default=3, help="Small morphology close radius for broken strokes")
    parser.add_argument("--merge-gap", type=int, default=18, help="Merge nearby fragments within this pixel gap; 0 disables")
    parser.add_argument("--merge-union-growth", type=float, default=2.4, help="Maximum union-box growth allowed when merging fragments")
    parser.add_argument("--pad", type=int, default=24)
    parser.add_argument("--limit", type=int, help="Maximum number of components to write")
    parser.add_argument("--square", action="store_true", help="Place each extracted asset on a transparent square canvas")
    parser.add_argument("--manifest", help="Optional JSON report path for component boxes and outputs")
    parser.add_argument("--contact-sheet", help="Optional contact sheet image for visual QA")
    args = parser.parse_args()

    src = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(src).convert("RGBA")
    mask = foreground_mask(image.getchannel("A"), args.threshold, args.close_radius)
    components = component_boxes(mask, args.min_area, args.connectivity)
    components = merge_fragments(components, args.merge_gap, args.merge_union_growth)
    components = sort_components(components, args.sort)
    if args.limit:
        components = components[: args.limit]

    names = parse_names(args.names)
    if names and len(names) != len(components):
        raise SystemExit(f"--names supplied {len(names)} names, but detected {len(components)} components")

    outputs = []
    contact_items = []
    for index, component in enumerate(components, start=1):
        name = names[index - 1] if names else f"asset_{index:02d}.png"
        if not name.lower().endswith(".png"):
            name += ".png"
        component_image, padded_box = extract_component_asset(image, component["box"], args.pad, args.square)
        out_path = out_dir / name
        component_image.save(out_path)
        entry = {
            "path": str(out_path),
            "source": str(src),
            "box": component["box"],
            "padded_box": padded_box,
            "area": component["area"],
            "merged_count": component.get("merged_count", 1),
            "size": list(component_image.size),
        }
        outputs.append(entry)
        contact_items.append({"name": name, "image": component_image})
        print(f"{name}: box={component['box']} area={component['area']} size={component_image.size}")

    if args.manifest:
        Path(args.manifest).write_text(json.dumps({"source": str(src), "assets": outputs}, ensure_ascii=False, indent=2))
    if args.contact_sheet:
        write_contact_sheet(contact_items, Path(args.contact_sheet))


if __name__ == "__main__":
    main()
