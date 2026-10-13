"""FRAMEXGOD // AI NEWS slide compositor, Brand Bible look (00-STANDARDS/Brand-Style-Bible).

Monochrome grade with Cold Shadow toe, fine 35mm grain, polarity flip on alternate slides
(positive = void-black frame, negative = bone-white frame), a circular 2X loupe showing the
opposite polarity, 12-column 0.5px grid, registration crosshairs, mono spec block, one Signal
Orange pill (the only accent), small tracked grotesk caps, chrome FRAMEXGOD lockup bottom-center.
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
DISPLAY = F + "InterTight-SemiBold.ttf"
BODY = F + "InterTight-Medium.ttf"
MONO = F + "IBMPlexMono-Medium.ttf"
MONO_R = F + "IBMPlexMono-Regular.ttf"

VOID = (10, 10, 11)
BONE = (242, 241, 238)
STEEL = (138, 143, 148)
COLD = np.array([22, 34, 43], np.float32) / 255
ORANGE = (255, 90, 31)
CHROME = [(230, 232, 234), (138, 143, 148), (43, 46, 49)]


def fnt(p, s): return ImageFont.truetype(p, s)


def cover(im, W, H):
    r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((l, t, l + W, t + H))


def grade(im, negative=False):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = a * 0.12 + lum[..., None] * 0.88                   # 90% monochrome
    if negative:                                            # invert + desaturate + lift (bible: Resolve polarity node)
        a = 1 - a
        a = a * 0.9 + 0.06
        a = a * (np.array(BONE, np.float32) / 255)
    else:
        toe = np.clip(1 - lum / 0.35, 0, 1)[..., None]       # Cold Shadow in the toe only
        a = a * (1 - 0.5 * toe) + COLD * 0.5 * toe
        a = np.clip((a - 0.5) * 1.06 + 0.5, 0.015, 1)
    return np.clip(a, 0, 1)


def grain(a, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, a.shape[:2]).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255 - 0.5
    lum = a.mean(axis=2, keepdims=True)
    w = 0.5 + 0.7 * (1 - np.abs(lum - 0.5) * 2)
    return np.clip(a + n[..., None] * 0.055 * w, 0, 1)


def floor(a, negative, H):
    """Calm the lower band so type reads, without a visible gradient box."""
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    k = np.clip((y - 0.56) / 0.2, 0, 1) ** 1.3 * 0.94
    tgt = np.array(BONE if negative else VOID, np.float32) / 255
    return a * (1 - k) + tgt * k


def tracked(d, xy, text, f, fill, track=0.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + f.size * track
    return x


def tlen(d, text, f, track=0.0):
    return sum(d.textlength(c, font=f) for c in text) + f.size * track * len(text)


def wrap(d, text, f, maxw, track=0.0):
    out = []
    for part in text.split("\n"):
        cur = ""
        for w in part.split():
            t = (cur + " " + w).strip()
            if tlen(d, t, f, track) <= maxw: cur = t
            else: out.append(cur); cur = w
        if cur: out.append(cur)
    return out


def chrome_text(base, xy, text, f, track=0.08):
    """Chrome wordmark: vertical #E6E8EA -> #8A8F94 -> #2B2E31 gradient through a text mask."""
    W, H = base.size
    m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
    tracked(md, xy, text, f, 255, track)
    bb = m.getbbox()
    if not bb: return
    h = bb[3] - bb[1]
    g = np.zeros((H, W, 3), np.float32)
    for yy in range(bb[1], bb[3]):
        t = (yy - bb[1]) / max(h - 1, 1)
        c0, c1, tt = (CHROME[0], CHROME[1], t / 0.5) if t < 0.5 else (CHROME[1], CHROME[2], (t - 0.5) / 0.5)
        g[yy] = [c0[i] + (c1[i] - c0[i]) * tt for i in range(3)]
    layer = Image.fromarray(g.astype(np.uint8)).convert("RGBA"); layer.putalpha(m)
    base.alpha_composite(layer)


def cross(d, x, y, s, fill, w=1):
    d.line([x - s, y, x + s, y], fill=fill, width=w); d.line([x, y - s, x, y + s], fill=fill, width=w)


def compose(spec, out, W=1080, H=1350, seed=7):
    neg = bool(spec.get("negative"))
    full = cover(Image.open(spec["bg"]), W, H)
    lift = spec.get("lift", 150)                            # move the subject up, clear of the type block
    src = Image.new("RGB", (W, H), full.getpixel((4, 4)))
    src.paste(full.crop((0, lift, W, H)), (0, 0))
    a = floor(grade(src, neg), neg, H)
    a = grain(a, seed)
    im = Image.fromarray((a * 255).astype(np.uint8)).convert("RGBA")

    ink = VOID if neg else BONE
    sub = (70, 74, 78) if neg else (176, 180, 184)
    gridc = (*(VOID if neg else STEEL), 38)
    M = 72

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    # 12-column grid, 0.5px at ~20% (drawn 1px at low alpha)
    cw = (W - 2 * M) / 12
    for i in range(13):
        x = round(M + i * cw); d.line([x, 0, x, H], fill=gridc, width=1)
    for y in range(M, H, round(cw * 2)):
        d.line([0, y, W, y], fill=(*gridc[:3], 22), width=1)
    im.alpha_composite(ov)

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    m17, m14, m13 = fnt(MONO, 17), fnt(MONO_R, 14), fnt(MONO_R, 13)

    # header
    tracked(d, (M, 48), "FRAMEXGOD // AI NEWS", m17, ink, 0.2)
    r = f"{spec['code']}   {spec['idx']}"
    tracked(d, (W - M - tlen(d, r, m17, 0.2), 48), r, m17, ink, 0.2)
    d.line([M, 84, W - M, 84], fill=(*sub, 140), width=1)

    # spec block
    y = 104
    for ln in spec["spec"]:
        tracked(d, (M, y), ln, m14, sub, 0.2); y += 22

    # registration marks around the hero zone
    for cx, cy in [(M, 238), (W - M, 238), (M, 880), (W - M, 880)]:
        cross(d, cx, cy, 9, (*ink, 200))

    # 2X loupe: opposite polarity, punch-in on frame center
    R = 112; lcx, lcy = W - M - R, 104 + R
    fx, fy = spec.get("focus", (0.5, 0.45))
    cx, cy = int(fx * W), int(fy * H)
    z = full.crop((cx - R // 2 * 1, cy - R // 2, cx + R // 2, cy + R // 2)).resize((2 * R, 2 * R), Image.LANCZOS)
    za = grain(grade(z, not neg), seed + 3)
    zi = Image.fromarray((za * 255).astype(np.uint8)).convert("RGBA")
    mask = Image.new("L", (2 * R, 2 * R), 0); ImageDraw.Draw(mask).ellipse([0, 0, 2 * R - 1, 2 * R - 1], fill=255)
    zi.putalpha(mask)
    im.alpha_composite(ov); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    im.alpha_composite(zi, (lcx - R, lcy - R))
    d.ellipse([lcx - R, lcy - R, lcx + R, lcy + R], outline=(*ink, 220), width=1)
    cross(d, lcx, lcy, 7, (*(BONE if neg else VOID), 200))
    lab = "2X · POLARITY"
    tracked(d, (lcx - tlen(d, lab, m13, 0.2) / 2, lcy + R + 10), lab, m13, sub, 0.2)

    # type block, bottom-anchored
    size = spec.get("size", 46)
    hf = fnt(DISPLAY, size); bf = fnt(BODY, 29)
    maxw = W - 2 * M - 40
    hl = wrap(d, spec["head"].upper(), hf, maxw, 0.04)
    bl = wrap(d, spec.get("body", ""), bf, maxw - 60) if spec.get("body") else []
    lh, blh = round(size * 1.1), 40
    foot = H - 150
    y = foot - (len(bl) * blh + (22 if bl else 0)) - len(hl) * lh
    # orange pill, the one accent
    pf = fnt(MONO, 15); tag = spec["tag"]
    pw = tlen(d, tag, pf, 0.2) + 30
    py = y - 54
    d.rounded_rectangle([M, py, M + pw, py + 32], radius=16, fill=ORANGE)
    tracked(d, (M + 15, py + 7), tag, pf, VOID, 0.2)
    for ln in hl:
        tracked(d, (M, y), ln, hf, ink, 0.04); y += lh
    if bl:
        y += 22
        for ln in bl:
            d.text((M, y), ln, font=bf, fill=(52, 54, 58) if neg else (214, 216, 218)); y += blh

    # footer: source · chrome lockup · swipe
    d.line([M, H - 112, W - M, H - 112], fill=(*sub, 140), width=1)
    tracked(d, (M, H - 82), spec["code"], m13, sub, 0.2)
    sw = spec.get("swipe", "SWIPE  >")
    tracked(d, (W - M - tlen(d, sw, m13, 0.2), H - 82), sw, m13, ink, 0.2)
    im.alpha_composite(ov)
    lf = fnt(DISPLAY, 22)
    wm = "FRAMEXGOD"; ww = tlen(ImageDraw.Draw(im), wm, lf, 0.4)
    chrome_text(im, ((W - ww) / 2, H - 90), wm, lf, 0.4)
    d = ImageDraw.Draw(im)
    url = "FRAMEXGOD.COM"
    tracked(d, ((W - tlen(d, url, m13, 0.25)) / 2, H - 58), url, m13, sub, 0.25)
    im.convert("RGB").save(out, quality=95)


if __name__ == "__main__":
    compose(json.loads(sys.argv[1]), sys.argv[2])
