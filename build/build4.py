import os, json, html
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
    f'<button class="tile" type="button" aria-label="FRAMEXGOD frame {i+1:02d} — play the reel">'
    f'<span class="n mono">{i+1:02d}</span>'
    f'<img src="media/thumbs/{c}.webp" alt="" width="720" height="405" loading="{"eager" if i < 8 else "lazy"}" decoding="async">'
    f'<video muted loop playsinline preload="none" data-src="boom/{c}.mp4"></video></button>'
    for i, c in enumerate(ids))

CREDITS = [
    ('BEBE', '6ix9ine ft. Anuel AA', 'Producer · Director', '1.6B+', False),
    ('105°F Remix', 'Kevvo, Chencho Corleone, Farruko, Myke Towers, Arcángel, Ñengo Flow, Darell, Brytiago', 'Producer · Director · DP · Editor', '750M+', False),
    ('Passion Whine', 'Farruko ft. Sean Paul', 'Producer', '750M+', False),
    ('Hard Drive', 'Shenseea × Konshens × Rvssian', 'Producer · Director · DP · Editor', '40M+', False),
    ('Power', 'Kevvo ft. Myke Towers, Jhay Cortez, Darell', 'Producer · Director · DP · Editor', '40M+', False),
    ('Stay Schemin', 'Rick Ross ft. Drake, French Montana', 'Director of Photography', '25M+', False),
    ("Nobody's Favorite", 'Rick Ross ft. Gunplay', 'Director of Photography', '19M+', False),
    ('Mada', 'Kalash · Universal France', 'Producer · DP · Editor', '16M+', False),
    ('Embalao', 'Farruko, White Star, J. Cross', 'Producer · Director · DP · Editor', '3.8M+', False),
    ('Trapxficante', 'Farruko world tour and album · Sony Music', '15 music videos · campaign · merch · album design', '', False),
    ('La 167', 'Farruko world tour and album', '3 music videos · campaign · merch', '', False),
    ('Merlin', 'Feature film · 2025', 'Creative Producer · Production Design', "People's Choice Award · Chandler Film Festival", True),
]
cred = '\n'.join(
    f'<li><span class="i mono">{i+1:02d}</span><b>{html.escape(t)}</b><span class="a">{html.escape(a)}</span><span class="r mono">{html.escape(r)}</span>'
    + (f'<em class="sm">{html.escape(v)}</em>' if sm else (f'<em class="chrome">{html.escape(v)}</em>' if v else '<em></em>')) + '</li>'
    for i, (t, a, r, v, sm) in enumerate(CREDITS))

CLIENTS = ['Sony Music', 'Universal Music', 'Universal France', 'Interscope', 'Epic Records', 'Cash Money', 'CMG', 'Maybach Music Group', 'Carbon Fiber Music', 'Remas Records', 'Rebelión', 'Una Visión Quintana', 'Carnival Cruise Lines', 'Baptist Health', 'General Motors']
marq = ''.join(f'<span>{html.escape(c)}</span>' for c in CLIENTS)

tpl = open(os.path.join(B, 'template4.html'), encoding='utf-8').read()
out = tpl.replace('{{GRID}}', grid).replace('{{COUNT}}', str(len(ids))).replace('{{CREDITS}}', cred).replace('{{MARQ}}', marq)
assert '{{' not in out
assert 'gmail' not in out.lower() and 'claude.ai' not in out and 'drive.google' not in out
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print('tiles', len(ids), 'bytes', len(out.encode()))
