import os, json, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'build')
order = json.load(open(os.path.join(B, 'palette_order.json')))
a2b = json.load(open(os.path.join(B, 'a2b.json')))
ids = [a2b[n] for n in order]
assert len(set(ids)) == len(ids)
for c in ids:
    assert os.path.exists(os.path.join(ROOT, 'media', 'thumbs', c + '.webp')), c
    assert os.path.exists(os.path.join(ROOT, 'boom', c + '.mp4')), c
grid = '\n'.join(
    f'<div class="tile" tabindex="0" role="button" aria-label="FRAMEXGOD frame {i+1:02d} — play the reel">'
    f'<span class="idx mono">{i+1:02d}</span>'
    f'<img src="media/thumbs/{c}.webp" alt="" width="720" height="405" loading="{"eager" if i < 8 else "lazy"}" decoding="async">'
    f'<video muted loop playsinline preload="none" data-src="boom/{c}.mp4"></video></div>'
    for i, c in enumerate(ids))
tpl = open(os.path.join(B, 'template5.html'), encoding='utf-8').read()
jp = ''.join(sorted(set(ch for ch in tpl if ord(ch) > 0x3000)))
out = tpl.replace('{{FEATURED}}', grid).replace('{{FEATURED_COUNT}}', str(len(ids))).replace('{{JP}}', urllib.parse.quote(jp))
assert '{{' not in out
assert 'gmail' not in out.lower() and 'claude.ai' not in out and 'drive.google' not in out
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print('tiles', len(ids), 'bytes', len(out.encode()))
