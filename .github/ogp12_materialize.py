#!/usr/bin/env python3
from PIL import Image, ImageDraw
from pathlib import Path
import math, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
(ASSETS / "concepts").mkdir(parents=True, exist_ok=True)

SCALE = 3
BG = (0, 0, 0, 255)
GOLD = (199, 162, 86, 255)
GOLD_DARK = (118, 87, 34, 255)
GOLD_LIGHT = (235, 205, 129, 255)
OBS = [(8, 8, 9, 255), (14, 14, 16, 255), (21, 21, 24, 255), (29, 29, 33, 255), (38, 38, 42, 255)]


def ellipse_pt(cx, cy, rx, ry, ang):
    return (cx + rx * math.cos(ang), cy + ry * math.sin(ang))


def poly(draw, pts, fill, outline=None, width=1):
    pts = [(int(x), int(y)) for x, y in pts]
    draw.polygon(pts, fill=fill)
    if outline:
        draw.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


def draw_cover(width, height, concept="portal"):
    img = Image.new("RGBA", (width * SCALE, height * SCALE), BG)
    d = ImageDraw.Draw(img)
    S = lambda p: tuple(int(v * SCALE) for v in p)
    left_cx, cy = int(width * 0.245), int(height * 0.51)
    right_cx = int(width * 0.735)

    if concept == "portal":
        outer = (int(width * 0.145), int(height * 0.33))
        inner = (int(width * 0.070), int(height * 0.18))
        n = 24
        for ring_scale, alpha in [(1.0, 210), (0.82, 105)]:
            pts = [ellipse_pt(left_cx, cy, outer[0] * ring_scale, outer[1] * ring_scale, 2 * math.pi * i / n) for i in range(n)]
            d.line([S(p) for p in pts + [pts[0]]], fill=(199, 162, 86, alpha), width=2 * SCALE, joint="curve")
        inner_pts = [ellipse_pt(left_cx, cy, inner[0], inner[1], 2 * math.pi * i / n) for i in range(n)]
        d.line([S(p) for p in inner_pts + [inner_pts[0]]], fill=(199, 162, 86, 180), width=2 * SCALE, joint="curve")
        for i in range(0, n, 2):
            p1 = ellipse_pt(left_cx, cy, outer[0], outer[1], 2 * math.pi * i / n)
            p2 = ellipse_pt(left_cx, cy, inner[0], inner[1], 2 * math.pi * i / n)
            d.line([S(p1), S(p2)], fill=(199, 162, 86, 115), width=SCALE)
        for j, x in enumerate([int(width * 0.44), int(width * 0.50), int(width * 0.56)]):
            y, sz = cy, int(height * 0.025)
            d.line([S((x - sz, y - sz)), S((x + sz, y)), S((x - sz, y + sz))], fill=(199, 162, 86, 180 - j * 35), width=2 * SCALE, joint="curve")
        outer_pts = [ellipse_pt(right_cx, cy, outer[0], outer[1], 2 * math.pi * i / n) for i in range(n)]
        inner_pts_r = [ellipse_pt(right_cx, cy, inner[0], inner[1], 2 * math.pi * i / n) for i in range(n)]
        for i in range(n):
            a, b = outer_pts[i], outer_pts[(i + 1) % n]
            c, e = inner_pts_r[(i + 1) % n], inner_pts_r[i]
            ang_mid = 2 * math.pi * (i + 0.5) / n
            light = max(0, math.cos(ang_mid + math.pi * 0.75))
            shade_idx = min(4, max(0, int(1 + 3 * light)))
            fill = OBS[shade_idx]
            if i in {1, 2, 3, 8, 14}:
                fill = GOLD if i not in {1, 14} else GOLD_DARK
            poly(d, [S(a), S(b), S(c), S(e)], fill=fill, outline=(5, 5, 6, 255), width=SCALE)
            mid = ((a[0] + b[0] + c[0] + e[0]) / 4, (a[1] + b[1] + c[1] + e[1]) / 4)
            if fill not in {GOLD, GOLD_DARK}:
                poly(d, [S(a), S(b), S(mid)], fill=OBS[min(4, shade_idx + 1)])
                poly(d, [S(e), S(mid), S(c)], fill=OBS[max(0, shade_idx - 1)])
        d.line([S(p) for p in inner_pts_r + [inner_pts_r[0]]], fill=GOLD_LIGHT, width=3 * SCALE, joint="curve")
        highlight = [ellipse_pt(right_cx, cy, outer[0] + 2, outer[1] + 2, math.pi * (0.72 + 0.03 * i)) for i in range(8)]
        d.line([S(p) for p in highlight], fill=(120, 120, 126, 150), width=2 * SCALE)

    elif concept == "prism":
        lx, ly = left_cx, cy
        pts = [(lx - 130, ly + 90), (lx - 30, ly - 150), (lx + 120, ly - 70), (lx + 130, ly + 110), (lx, ly + 170)]
        d.line([S(p) for p in pts + [pts[0]]], fill=(199, 162, 86, 185), width=2 * SCALE)
        for p in pts:
            d.line([S((lx, ly)), S(p)], fill=(199, 162, 86, 90), width=SCALE)
        for j, x in enumerate([int(width * 0.44), int(width * 0.50), int(width * 0.56)]):
            y, sz = cy, int(height * 0.025)
            d.line([S((x - sz, y - sz)), S((x + sz, y)), S((x - sz, y + sz))], fill=(199, 162, 86, 170 - j * 35), width=2 * SCALE)
        rx, ry = right_cx, cy
        verts = [(rx - 170, ry + 110), (rx - 40, ry - 180), (rx + 160, ry - 95), (rx + 175, ry + 120), (rx, ry + 185)]
        for i in range(len(verts)):
            fill = GOLD if i == 1 else OBS[(i + 1) % len(OBS)]
            poly(d, [S((rx, ry)), S(verts[i]), S(verts[(i + 1) % len(verts)])], fill=fill, outline=(4, 4, 5, 255), width=SCALE)

    else:
        lx, ly, n = left_cx, cy, 12
        pts = [ellipse_pt(lx, ly, 130, 180, 2 * math.pi * i / n) for i in range(n)]
        d.line([S(p) for p in pts + [pts[0]]], fill=(199, 162, 86, 180), width=2 * SCALE)
        for i in range(n):
            if i % 2 == 0:
                d.line([S(pts[i]), S(pts[(i + 3) % n])], fill=(199, 162, 86, 80), width=SCALE)
        for j, x in enumerate([int(width * 0.44), int(width * 0.50), int(width * 0.56)]):
            y, sz = cy, int(height * 0.025)
            d.line([S((x - sz, y - sz)), S((x + sz, y)), S((x - sz, y + sz))], fill=(199, 162, 86, 170 - j * 35), width=2 * SCALE)
        rx, ry = right_cx, cy
        outer = [ellipse_pt(rx, ry, 170, 225, 2 * math.pi * i / n) for i in range(n)]
        inner = [ellipse_pt(rx, ry, 65, 90, 2 * math.pi * i / n) for i in range(n)]
        for i in range(n):
            fill = GOLD if i in {1, 7} else OBS[(i + 2) % len(OBS)]
            poly(d, [S(outer[i]), S(outer[(i + 1) % n]), S(inner[(i + 1) % n]), S(inner[i])], fill=fill, outline=(4, 4, 5, 255), width=SCALE)
        d.ellipse([S((rx - 50, ry - 65)), S((rx + 50, ry + 65))], fill=GOLD_DARK, outline=GOLD_LIGHT, width=2 * SCALE)

    return img.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")


for name in ("portal", "prism", "core"):
    im = draw_cover(1000, 500, name).resize((600, 300), Image.Resampling.LANCZOS)
    im.quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(ASSETS / "concepts" / f"concept-{name}.png", optimize=True)

cover = draw_cover(1600, 800, "portal").resize((1280, 640), Image.Resampling.LANCZOS)
cover_q = cover.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
cover_q.save(ASSETS / "repository-cover.png", optimize=True)
cover_q.save(ASSETS / "social-preview.png", optimize=True)
cover.save(ASSETS / "repository-cover.webp", format="WEBP", quality=88, method=6)
cover.resize((64, 32), Image.Resampling.LANCZOS).quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(ASSETS / "repository-cover-64px.png", optimize=True)

manifest = json.loads((ASSETS / "cover-source-manifest.json").read_text())
for rel, meta in manifest["exports"].items():
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"missing export: {rel}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.stat().st_size != meta["bytes"] or digest != meta["sha256"]:
        raise SystemExit(f"checksum mismatch: {rel} size={path.stat().st_size} sha256={digest}")
print("OGP12 materialization PASS")
