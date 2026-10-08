import os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hero still. Swap for the 4K generated hero when it exists.
HERO = 'media/hero.webp' if os.path.exists(os.path.join(ROOT, 'media', 'hero.webp')) else 'media/min-begin.jpg'

# Three capability tiles. Swap for 4K generated stills when they exist.
def cat(key, fallback):
    p = f'media/cat-{key}.webp'
    return p if os.path.exists(os.path.join(ROOT, p)) else fallback
CATS = [
    ('Music Video', 'Performance, narrative, world-building', cat('music', 'media/thumbs/b12.webp'), 'b12'),
    ('Narrative / Feature', 'Features, series, branded story', cat('narrative', 'media/thumbs/b93.webp'), 'b93'),
    ('Commercial / Editorial', 'Spots, campaigns, fashion and product', cat('editorial', 'media/thumbs/b71.webp'), 'b71'),
]

FEATURED = [
    ('rendido_r1_10s', 'a', 'Rendido', 'JHEX · Director', 'Performer leaping across a mirrored salt flat at sunrise'),
    ('b71', 'b', '', '', 'Woman with braids aiming a rifle'),
    ('b12', 'c', '', '', 'Dancer reaching up through pink light'),
    ('b76', 'd', '', '', 'Artist with his hand on his head in a crowded room'),
    ('b30', 'e', '', '', 'Artist in a silver headpiece reaching toward the camera'),
    ('b25', 'f', '', '', 'Monster truck firing a flamethrower in a shipping yard'),
    ('b13', 'g', '', '', 'Face in clear glasses washed in violet light'),
    ('b15', 'h', '', '', 'Artist in a white fur coat under blue and red light'),
    ('b93', 'i', '', '', 'Black-and-white shot of a man at the edge of the ocean'),
]
SPEEDS = {'a': 0, 'b': .08, 'c': -.06, 'd': .05, 'e': -.09, 'f': .04, 'g': -.05, 'h': .07, 'i': -.04}

CREDITS = [
    ('BEBE', '6ix9ine ft. Anuel AA', 'Producer · Director', '1.6B+ views'),
    ('105°F Remix', 'Kevvo, Chencho Corleone, Farruko, Myke Towers, Arcángel, Ñengo Flow, Darell, Brytiago', 'Producer · Director · DP · Editor', '750M+ views'),
    ('Passion Whine', 'Farruko ft. Sean Paul', 'Producer', '750M+ views'),
    ('Hard Drive', 'Shenseea × Konshens × Rvssian', 'Producer · Director · DP · Editor', '40M+ views'),
    ('Power', 'Kevvo ft. Myke Towers, Jhay Cortez, Darell', 'Producer · Director · DP · Editor', '40M+ views'),
    ('Stay Schemin', 'Rick Ross ft. Drake, French Montana', 'Director of Photography', '25M+ views'),
    ("Nobody's Favorite", 'Rick Ross ft. Gunplay', 'Director of Photography', '19M+ views'),
    ('Mada', 'Kalash · Universal France', 'Producer · DP · Editor', '16M+ views'),
    ('Merlin', 'Feature film · 2025', 'Creative Producer · Production Design', "People's Choice Award, Chandler Film Festival"),
]

all_clips = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, 'boom')) if f.endswith('.mp4'))
featured_ids = {f[0] for f in FEATURED}
archive = [c for c in all_clips if c not in featured_ids and not c.startswith('rendido')]

def tile(cid, cls, title, sub, alt, idx, speed):
    cap = f'<div class="cap"><b>{html.escape(title)}</b><span class="mono">{html.escape(sub)}</span></div>' if title else ''
    return (f'<figure class="tile {cls}" data-speed="{speed}" tabindex="0" role="button" aria-label="{html.escape(alt)} — play the reel">'
            f'<span class="idx mono">{idx:02d}</span>'
            f'<img src="media/thumbs/{cid}.webp" alt="{html.escape(alt)}" width="720" height="405" loading="{"eager" if idx == 1 else "lazy"}" decoding="async">'
            f'<video muted loop playsinline preload="none" data-src="boom/{cid}.mp4"></video>{cap}</figure>')

feat_html = '\n'.join(tile(c, k, t, s, a, i + 1, SPEEDS[k]) for i, (c, k, t, s, a) in enumerate(FEATURED))
arch_html = '\n'.join(
    f'<figure class="tile" tabindex="0" role="button" aria-label="FRAMEXGOD archive clip {i+1:02d} — play the reel">'
    f'<img src="media/thumbs/{c}.webp" alt="FRAMEXGOD archive clip {i+1:02d}" width="720" height="405" loading="lazy" decoding="async">'
    f'<video muted loop playsinline preload="none" data-src="boom/{c}.mp4"></video></figure>'
    for i, c in enumerate(archive))
cat_html = '\n'.join(
    f'<figure class="cat" tabindex="0" role="button" aria-label="{html.escape(t)} — play the reel">'
    f'<img src="{src}" alt="{html.escape(t)}" width="1280" height="720" loading="lazy" decoding="async">'
    f'<video muted loop playsinline preload="none" data-src="boom/{clip}.mp4"></video>'
    f'<figcaption><b>{html.escape(t)}</b><span class="mono">{html.escape(s)}</span></figcaption></figure>'
    for t, s, src, clip in CATS)
cred_html = '\n'.join(
    f'<li><b>{html.escape(t)}</b><span>{html.escape(a)}</span><i class="mono">{html.escape(r)}</i><em class="mono">{html.escape(v)}</em></li>'
    for t, a, r, v in CREDITS)

tpl = open(os.path.join(ROOT, 'build', 'template3.html'), encoding='utf-8').read()
out = (tpl.replace('{{HERO}}', HERO).replace('{{FEATURED}}', feat_html).replace('{{ARCHIVE}}', arch_html)
          .replace('{{ARCHIVE_COUNT}}', str(len(archive))).replace('{{CATS}}', cat_html).replace('{{CREDITS}}', cred_html))
assert '{{' not in out, 'unfilled placeholder'
assert 'gmail' not in out.lower(), 'no gmail on the site'
assert 'claude.ai' not in out, 'no claude.ai links'
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print('hero', HERO, 'featured', len(FEATURED), 'archive', len(archive), 'bytes', len(out.encode()))
