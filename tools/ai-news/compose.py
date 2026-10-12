"""FRAMEXGOD // AI NEWS slide compositor: invert -> grade -> grain -> newsroom overlay -> type."""
import sys, json, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
GROT = F + "SpaceGrotesk.ttf"
MONO = F + "JetBrainsMono.ttf"
ORANGE = (255, 92, 0)
INK = (8, 8, 10)

def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    try: f.set_variation_by_axes([wght] if "Mono" in path or "Grotesk" in path else [14, wght])
    except Exception: pass
    return f

def cover(im, W, H):
    r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((l, t, l + W, t + H))

def negative(im):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    a = 1.0 - a                                   # film negative
    lum = a @ np.array([0.299, 0.587, 0.114])
    a = a * 0.55 + lum[..., None] * 0.45          # pull saturation down so it reads as film, not filter
    a = np.clip((a - 0.5) * 1.32 + 0.5, 0, 1)      # contrast
    a = a ** 1.45                                   # pull the paper-white highlights down so the frame has weight
    a[..., 2] = np.clip(a[..., 2] * 1.04, 0, 1)    # cold cast
    return a

def grain(a, strength=0.075, seed=7):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, a.shape[:2]).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255 - 0.5
    lum = a.mean(axis=2, keepdims=True)
    w = 0.6 + 0.8 * (1 - np.abs(lum - 0.5) * 2)    # grain strongest in mids, like film
    return np.clip(a + n[..., None] * strength * 2 * w, 0, 1)

def scanlines(a, every=4, depth=0.035):
    a = a.copy(); a[::every] *= (1 - depth); return a

def vignette(a, k=0.28):
    H, W = a.shape[:2]
    y, x = np.ogrid[:H, :W]
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    return np.clip(a * (1 - k * np.clip(d - 0.55, 0, 1))[..., None], 0, 1)

def wrap(draw, text, fnt, maxw):
    if "\n" in text:
        out = []
        for part in text.split("\n"): out += wrap(draw, part, fnt, maxw)
        return out
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def compose(spec, out, W=1080, H=1350, seed=7):
    bg = cover(Image.open(spec["bg"]), W, H)
    a = negative(bg)
    if spec.get("mode") == "overlay":
        n = np.asarray(bg.convert("RGB")).astype(np.float32) / 255.0
        a = a * (1 - spec.get("opacity", 0.5)) + n * spec.get("opacity", 0.5)
    a = vignette(a)
    a = grain(a, seed=seed)
    a = scanlines(a)
    im = Image.fromarray((a * 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    M = 64
    # top bar
    mono_s = font(MONO, 22, 600)
    d.rectangle([0, 0, W, 86], fill=(*INK, 235))
    d.rectangle([M, 40, M + 14, 54], fill=ORANGE)
    d.text((M + 28, 34), "FRAMEXGOD // AI NEWS", font=mono_s, fill=(245, 245, 245))
    right = f"{spec['date']}   {spec['idx']}"
    d.text((W - M - d.textlength(right, font=mono_s), 34), right, font=mono_s, fill=(245, 245, 245))
    d.line([0, 86, W, 86], fill=ORANGE, width=3)
    # category tag
    tag_f = font(MONO, 20, 700)
    tag = spec["tag"]
    tw = d.textlength(tag, font=tag_f)
    d.rectangle([M, 122, M + tw + 28, 160], fill=ORANGE)
    d.text((M + 14, 129), tag, font=tag_f, fill=INK)
    # headline block (bottom)
    size = spec.get("size", 84)
    head_f = font(GROT, size, 700)
    lines = wrap(d, spec["head"], head_f, W - 2 * M)
    lh = int(size * 1.04)
    body_f = font(GROT, 34, 500)
    blines = wrap(d, spec.get("body", ""), body_f, W - 2 * M) if spec.get("body") else []
    blh = 46
    block = len(lines) * lh + (24 + len(blines) * blh if blines else 0)
    y0 = H - 150 - block
    pad = 36
    d.rectangle([0, y0 - pad, W, H], fill=(*INK, 240))
    d.line([M, y0 - pad, M + 120, y0 - pad], fill=ORANGE, width=6)
    if spec.get("mode") == "inset":
        top, bot = 190, y0 - pad - 44
        ww, wh = W - 2 * M, bot - top
        n = np.asarray(cover(Image.open(spec["bg"]), ww, wh).convert("RGB")).astype(np.float32) / 255.0
        n = scanlines(grain(n, seed=seed + 1))
        win = Image.fromarray((n * 255).astype(np.uint8)).convert("RGBA")
        im.alpha_composite(win, (M, top))
        d.rectangle([M - 2, top - 2, M + ww + 1, top + wh + 1], outline=(245, 245, 245), width=2)
        for cx, cy, sx, sy in [(M, top, 1, 1), (M + ww, top, -1, 1), (M, top + wh, 1, -1), (M + ww, top + wh, -1, -1)]:
            d.line([cx, cy, cx + 34 * sx, cy], fill=ORANGE, width=6); d.line([cx, cy, cx, cy + 34 * sy], fill=ORANGE, width=6)
        lf = font(MONO, 18, 700)
        d.rectangle([M + 18, top + 18, M + 18 + 22 + d.textlength("LIVE FEED", font=lf) + 14, top + 48], fill=(*INK, 230))
        d.ellipse([M + 28, top + 27, M + 40, top + 39], fill=ORANGE)
        d.text((M + 48, top + 23), "LIVE FEED", font=lf, fill=(245, 245, 245))
    y = y0
    for i, ln in enumerate(lines):
        hl = spec.get("highlight")
        d.text((M, y), ln, font=head_f, fill=ORANGE if hl is not None and i in hl else (250, 250, 250))
        y += lh
    if blines:
        y += 24
        for ln in blines:
            d.text((M, y), ln, font=body_f, fill=(215, 215, 215)); y += blh
    # footer ticker
    foot_f = font(MONO, 20, 500)
    d.line([M, H - 92, W - M, H - 92], fill=(90, 90, 90), width=1)
    d.text((M, H - 72), spec.get("source", ""), font=foot_f, fill=(170, 170, 170))
    sw = spec.get("swipe", "SWIPE →")
    d.text((W - M - d.textlength(sw, font=foot_f), H - 72), sw, font=foot_f, fill=ORANGE)
    Image.alpha_composite(im, ov).convert("RGB").save(out, quality=95)

if __name__ == "__main__":
    spec = json.loads(sys.argv[1]); compose(spec, sys.argv[2])
