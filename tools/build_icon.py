"""Render assets/logo-square.svg into a high-quality multi-size .ico.

The SVG is a simple 4-shape "E" mark. Rather than relying on an SVG renderer
(which on Windows requires cairo system libs), we redraw the geometry directly
with Pillow at 4x oversampling and downscale with LANCZOS for crisp edges.
"""
from pathlib import Path

from PIL import Image, ImageDraw

SVG_W, SVG_H = 965, 1010
RADIUS_SVG = 183.228
BLACK = (0, 0, 0, 255)


def render(size: int) -> Image.Image:
    work = size * 4
    canvas = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Transparent background; just render the black mark with generous padding.
    pad = int(work * 0.14)

    inner_x0 = pad
    inner_y0 = pad
    inner_x1 = work - pad
    inner_y1 = work - pad
    inner_w = inner_x1 - inner_x0
    inner_h = inner_y1 - inner_y0

    scale = min(inner_w / SVG_W, inner_h / SVG_H)
    draw_w = SVG_W * scale
    draw_h = SVG_H * scale
    off_x = inner_x0 + (inner_w - draw_w) / 2
    off_y = inner_y0 + (inner_h - draw_h) / 2

    def t(x, y):
        return (off_x + x * scale, off_y + y * scale)

    r = RADIUS_SVG * scale

    def add_bar_rounded(box, round_corners):
        x0, y0, x1, y1 = box
        draw.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=BLACK)
        cr = r
        if "tl" not in round_corners:
            draw.rectangle((x0, y0, x0 + cr, y0 + cr), fill=BLACK)
        if "tr" not in round_corners:
            draw.rectangle((x1 - cr, y0, x1, y0 + cr), fill=BLACK)
        if "bl" not in round_corners:
            draw.rectangle((x0, y1 - cr, x0 + cr, y1), fill=BLACK)
        if "br" not in round_corners:
            draw.rectangle((x1 - cr, y1 - cr, x1, y1), fill=BLACK)

    add_bar_rounded((*t(0, 0), *t(223.945, 1009.79)), {"tl", "bl"})
    add_bar_rounded((*t(366.456, 0), *t(965, 223.946)), {"tr"})
    add_bar_rounded((*t(366.456, 394.958), *t(965, 618.903)), set())
    add_bar_rounded((*t(223.945, 785.845), *t(965, 1009.79)), {"br"})

    # LANCZOS blurs hard black edges → gray halos at 16–32px (taskbar looks "muddy").
    # Use NEAREST for small output sizes so edges stay crisp in the .ico layers.
    if size <= 48:
        return canvas.resize((size, size), Image.Resampling.NEAREST)
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def save_ico(path: Path, images_by_size: dict[int, Image.Image]) -> None:
    """Write a multi-size ICO reliably."""
    # Pillow is finicky about ICO multi-size; providing only the largest image
    # and the sizes list is the most reliable approach.
    largest = images_by_size[max(images_by_size)]
    largest.save(path, format="ICO", sizes=[(s, s) for s in sorted(images_by_size)])


def main():
    sizes = [256, 128, 96, 64, 48, 32, 24, 16]
    imgs = {s: render(s) for s in sizes}

    assets = Path(__file__).resolve().parent.parent / "assets"
    assets.mkdir(exist_ok=True)
    ico_path = assets / "logo-square.ico"
    png_path = assets / "logo-square.png"

    save_ico(ico_path, imgs)
    imgs[256].save(png_path, format="PNG")

    print("written:", ico_path, png_path)
    with Image.open(ico_path) as ico:
        print("ico sizes:", sorted(ico.ico.sizes()))


if __name__ == "__main__":
    main()
