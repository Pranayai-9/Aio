"""Run: python scripts/make_icons.py

The Aio mark: a lowercase "a" whose stem ends in a download arrow. Writes icon.svg and the PNG app icons.

One geometry (a 100-unit square) drives both the SVG and the rasterizer, so they always match.
"""
import struct
import sys
import zlib
from pathlib import Path

INK, PAPER, ACCENT = "#14130f", "#f2efe9", "#ff5b1f"
DX, DY = 7, -1  # centers the mark in the square

RING = (40 + DX, 48 + DY, 23, 13)  # cx, cy, outer radius, inner radius
STEM = (53 + DX, 25 + DY, 63 + DX, 64 + DY, 5)  # x0, y0, x1, y1, corner radius
ARROW = ((47 + DX, 61 + DY), (69 + DX, 61 + DY), (58 + DX, 77 + DY))
GAP = 3  # clear space between the arrow and the bowl
CORNER = 28
# The bowl stops in a clean vertical cut just left of the arrow, instead of tapering into a sliver.
CUT = (ARROW[0][0] - GAP, ARROW[0][1] - GAP, STEM[0], RING[1] + RING[2] + 1)  # x0, y0, x1, y1


def svg(maskable=False):
    cx, cy, ro, ri = RING
    x0, y0, x1, y1, r = STEM
    pts = " ".join(f"{x:g},{y:g}" for x, y in ARROW)
    bg = '<rect width="100" height="100" fill="{0}"/>' if maskable else '<rect width="100" height="100" rx="{1}" fill="{0}"/>'
    mark = (
        f'<circle cx="{cx:g}" cy="{cy:g}" r="{(ro + ri) / 2:g}" fill="none" stroke="{PAPER}" stroke-width="{ro - ri:g}"/>'
        f'<rect x="{CUT[0]:g}" y="{CUT[1]:g}" width="{CUT[2] - CUT[0]:g}" height="{CUT[3] - CUT[1]:g}" fill="{INK}"/>'
        f'<polygon points="{pts}" fill="{INK}" stroke="{INK}" stroke-width="{GAP * 2:g}" stroke-linejoin="round"/>'
        f'<rect x="{x0:g}" y="{y0:g}" width="{x1 - x0:g}" height="{y1 - y0:g}" rx="{r:g}" fill="{PAPER}"/>'
        f'<polygon points="{pts}" fill="{ACCENT}"/>'
    )
    if maskable:
        mark = f'<g transform="translate(50 50) scale(0.8) translate(-50 -50)">{mark}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'{bg.format(INK, CORNER)}{mark}</svg>\n')


def rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def in_rrect(x, y, x0, y0, x1, y1, r):
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    cx, cy = min(max(x, x0 + r), x1 - r), min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def in_triangle(x, y):
    (ax, ay), (bx, by), (cx, cy) = ARROW
    def side(px, py, qx, qy):
        return (qx - px) * (y - py) - (qy - py) * (x - px)
    s = [side(ax, ay, bx, by), side(bx, by, cx, cy), side(cx, cy, ax, ay)]
    return all(v >= 0 for v in s) or all(v <= 0 for v in s)


def dist_to_triangle(x, y):
    best = float("inf")
    for (px, py), (qx, qy) in zip(ARROW, ARROW[1:] + ARROW[:1], strict=True):
        vx, vy = qx - px, qy - py
        t = max(0, min(1, ((x - px) * vx + (y - py) * vy) / (vx * vx + vy * vy)))
        best = min(best, ((x - px - t * vx) ** 2 + (y - py - t * vy) ** 2) ** 0.5)
    return best


def color_at(x, y, maskable):
    if maskable:
        x, y = (x - 50) / 0.8 + 50, (y - 50) / 0.8 + 50
    elif not in_rrect(x, y, 0, 0, 100, 100, CORNER):
        return None
    if in_triangle(x, y):
        return ACCENT
    if in_rrect(x, y, *STEM):
        return PAPER
    if dist_to_triangle(x, y) <= GAP or (CUT[0] <= x <= CUT[2] and CUT[1] <= y <= CUT[3]):
        return INK
    cx, cy, ro, ri = RING
    if ri ** 2 <= (x - cx) ** 2 + (y - cy) ** 2 <= ro ** 2:
        return PAPER
    return INK


def png(size, maskable, ss=4):
    palette = {c: rgb(c) for c in (INK, PAPER, ACCENT)}
    rows = []
    for py in range(size):
        row = bytearray([0])
        for px in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    c = color_at((px + (sx + .5) / ss) * 100 / size, (py + (sy + .5) / ss) * 100 / size, maskable)
                    if c:
                        r, g, b = palette[c]
                        acc = [acc[0] + r, acc[1] + g, acc[2] + b, acc[3] + 1]
            n = acc[3]
            row += bytes([round(acc[0] / n) if n else 0, round(acc[1] / n) if n else 0,
                          round(acc[2] / n) if n else 0, round(255 * n / ss ** 2)])
        rows.append(bytes(row))
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))


out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "server/aio_server/static/icons"
(out / "icon.svg").write_text(svg(), encoding="utf-8")
for size in (192, 512):
    (out / f"icon-{size}.png").write_bytes(png(size, False))
(out / "icon-maskable-512.png").write_bytes(png(512, True))
print("ok")
