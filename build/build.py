import os, re, urllib.parse
from PIL import Image, ImageStat

THUMB_SRC = os.environ.get('THUMB_SRC')

def zoom(cid):
    im = Image.open(os.path.join(ROOT_GUESS, 'media', 'thumbs', cid + '.webp')).convert('L')
    w, h = im.size
    rows = [ImageStat.Stat(im.crop((0, y, w, y + 1))).mean[0] for y in range(h)]
    t = next((y for y in range(h) if rows[y] > 14), 0)
    b = next((y for y in range(h - 1, -1, -1) if rows[y] > 14), h - 1)
    z = h / max(1, b - t + 1)
    return round(z, 3) if z > 1.04 else 1

ROOT_GUESS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'build', 'template.html'), encoding='utf-8').read()

FEATURED = [
    ('rendido_r1_10s', 'big', 'Rendido', 'JHEX · Director', 'Performer leaping across a mirrored salt flat at sunrise'),
    ('b71', '', '', '', 'Woman with braids aiming a rifle'),
    ('b12', '', '', '', 'Dancer reaching up through pink light'),
    ('b76', '', '', '', 'Artist with his hand on his head in a crowded room'),
    ('b30', '', '', '', 'Artist in a silver headpiece reaching toward the camera'),
    ('b25', '', '', '', 'Monster truck firing a flamethrower in a shipping yard'),
    ('b13', '', '', '', 'Face in clear glasses washed in violet light'),
    ('b67', '', '', '', 'Woman on a yellow pool float at a lake party'),
    ('b93', '', '', '', 'Black-and-white shot of a man at the edge of the ocean'),
]

all_clips = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, 'boom')) if f.endswith('.mp4'))
featured_ids = {f[0] for f in FEATURED}
archive = [c for c in all_clips if c not in featured_ids]


def tile(cid, cls, title, sub, alt, idx, eager=False):
    cap = ''
    if title:
        cap = f'<div class="cap"><div><b>{title}</b><span class="mono">{sub}</span></div></div>'
    load = 'eager' if eager else 'lazy'
    klass = ('tile ' + cls).strip()
    z = zoom(cid)
    zs = f' style="--z:{z}"' if z != 1 else ''
    return (f'    <div class="{klass}"{zs} tabindex="0" role="button" aria-label="{alt} — play the reel">'
            f'<span class="idx mono">{idx:02d}</span>'
            f'<img src="media/thumbs/{cid}.webp" alt="{alt}" width="720" height="405" loading="{load}" decoding="async">'
            f'<video muted loop playsinline preload="none" data-src="boom/{cid}.mp4"></video>{cap}</div>')


feat_html = '\n'.join(
    tile(c, cls, t, s, a, i + 1, eager=(i == 0))
    for i, (c, cls, t, s, a) in enumerate(FEATURED))

arch_rows = []
for i, c in enumerate(archive):
    alt = f'FRAMEXGOD archive clip {i + 1:02d}'
    arch_rows.append(
        f'    <div class="tile"{(lambda z: f' style="--z:{z}"' if z != 1 else '')(zoom(c))} tabindex="0" role="button" aria-label="{alt} — play the reel">'
        f'<img src="media/thumbs/{c}.webp" alt="{alt}" width="720" height="405" loading="lazy" decoding="async">'
        f'<video muted loop playsinline preload="none" data-src="boom/{c}.mp4"></video></div>')

jp_chars = ''.join(sorted(set(ch for ch in tpl if ord(ch) > 0x3000)))

out = (tpl.replace('{{FEATURED}}', feat_html)
          .replace('{{FEATURED_COUNT}}', str(len(FEATURED)))
          .replace('{{ARCHIVE}}', '\n'.join(arch_rows))
          .replace('{{ARCHIVE_COUNT}}', str(len(archive)))
          .replace('{{JP}}', urllib.parse.quote(jp_chars)))

assert '{{' not in out, 'unfilled placeholder'
for c, *_ in FEATURED:
    assert os.path.exists(os.path.join(ROOT, 'media', 'thumbs', c + '.webp')), c
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print('featured', len(FEATURED), 'archive', len(archive), 'bytes', len(out.encode()), 'jp', jp_chars)
