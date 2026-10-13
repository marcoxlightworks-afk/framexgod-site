# FRAMEXGOD // AI NEWS: daily carousel playbook

Style source of truth: the FRAMEXGOD Brand Bible (vault `00-STANDARDS/Brand-Style-Bible.md`). Every carousel follows it:
one hero object per frame on seamless black, one hard ARRI light, black/white/steel only, Signal Orange #FF5A1F only on the
single pill tag, small precise type, calm technical voice. Adopted 2026-10-13.

One carousel a day on @framexgod: AI news in film, entertainment, music and creative tech.
Goal: grow followers. Every carousel ends on "Follow @framexgod for AI × <topic> news."

## 0. Queue first
Read `news/feed.json`. If `queue` is not empty, publish the oldest queued item (step 6) instead of making a new
one, move it to `posted`, and stop. Only make a new carousel when the queue is empty.

## 1. Pick the story
- One story from the last 48 hours: AI in film/TV, music, gaming, VFX, creative tools, or Hollywood business.
- Verify every fact against a primary or reputable outlet. Read the article with WebFetch. Never invent numbers, quotes or dates.
- Skip anything already listed in `feed.json` → `covered_topics`.
- Prefer stories with a surprising number, a big name or a clear consequence. A creator should care.

## 2. Write the slides (6 or 7)
1. Hook: one sentence, 8–14 words, no body. Break it into two lines with `\n` (size 42–50). No orange in type.
2–5. Story: short headline (≤ 6 words) plus a 1–2 sentence body. One fact per slide.
6. Optional "FRAMEXGOD TAKE": one plain line on what it means for creators. Use the per-slide tag "FRAMEXGOD TAKE".
Last. CTA: `Follow @framexgod\nfor AI × <film|music|tech> news.`, body "New stories every week.", swipe "@FRAMEXGOD",
bg = the house closing frame (chrome cinema camera, `tools/ai-news/assets/close.png`), lift 50.

Rules: plain words, no hype. No quotes longer than 10 words. Credit sources in `source` as "SRC: <OUTLET> · <MON DD YYYY>". Project code `FXG-N<3-digit issue>` (FXG-N001 = first story).
Real people can be named, but are never shown in images.

## 3. Backgrounds (Higgsfield)
- Model: `gpt_image_2_5`. aspect_ratio `4:5`, quality `high`, resolution `2k`. About 2.75 credits each, one per slide.
- Submit in batches of 4 (bigger batches hit rate limits), then `jobs_wait`.
- Each prompt uses the six-block structure, in order:
  SUBJECT → ACTION → ENVIRONMENT → ART STYLE/CAMERA → LIGHTING → DETAILS & CONSTRAINTS.
- SUBJECT: ONE hero object that tells the slide's fact (Brand Bible "Monument" shot): chrome, clear glass, liquid, machined
  steel. Unbranded. One surreal natural element max (water drop, mercury, ice). Never people, real products, brand marks,
  award statuettes or known characters.
- ENVIRONMENT always: "seamless void-black cyc, <glossy|matte> black floor, nothing else in frame."
- ART STYLE/CAMERA always: "ARRI Alexa 35, Cooke S7/i 75mm at T2.8, Kodak Vision3 250D film texture, editorial luxury campaign
  still, photoreal, documentary realism, not a 3D render, not CGI."
- LIGHTING always: "single ARRI SkyPanel S60 hard key from 45 degrees camera left through a 4x4 frame, black negative fill camera
  right, crisp specular highlights on chrome and glass, cool steel shadows, neutral highlights, deep rich blacks without crushing."
- DETAILS & CONSTRAINTS always end with: "Monochrome palette of black, white and steel only, no color accents. Subject centered
  inside the middle square of the frame with generous negative space. Keep the lower 30 percent of the frame darker and calm.
  No text, no letters, no numbers, no logos, no signage, no brand marks, no people, no faces, no hands, no recognizable
  trademarked objects, no warped geometry, no glow, no plastic sheen, no clutter, no oversaturation."
- Reference prompts that worked: `tools/ai-news/specs/` (2026-10-13 c1/c2).
- Download each result to `<raw>/s1.png … sN.png`.

## 4. Render
Write `<raw>/spec.json` (see the docstring in `make.py`). Then run `python3 tools/ai-news/make.py <raw>/spec.json <raw>`.
Needs Pillow and numpy. The look is fixed in `compose.py` (Brand Bible): slides alternate polarity (odd = void black,
even = inverted bone white), a circular "2X · POLARITY" loupe shows the opposite polarity, 12-column 0.5px grid, crosshairs,
mono spec block (code, Miami coordinates, date, source), one orange pill tag, Inter Tight caps headline, IBM Plex Mono
system text, chrome FRAMEXGOD lockup + FRAMEXGOD.COM bottom-center. Do not change it.
Per-slide tuning only: `lift` (px the image moves up so the subject clears the type, default 150) and `focus` ([x, y]
fractions of the source image the loupe magnifies, aim it at the subject's best detail).

## 5. Check before posting
Open every rendered slide and look at it. Check that no text is cut off, there are no orphan words, the subject clears the type and the loupe, the loupe shows real detail (not empty black), the facts match the source, there are no typos, no faces, and nothing that looks like a trademarked object.
Fix and re-render until it is clean.

## 6. Publish
1. Commit `news/<date>/` and push to `main`. Wait until `https://framexgod.com/news/<date>/<slug>_01.jpg` returns 200.
2. Write the caption to a file (Brand Bible format, calm, present tense, no emoji, no hype):
   `FRAMEXGOD // AI NEWS — <code>` / `AI × <Topic>` / blank / hook / blank / 2–3 sentences of the story / blank /
   one FRAMEXGOD take line / blank / `Follow @framexgod for AI × <topic> news.` / blank / `Source: <outlet>, <date>.` /
   blank / `FRAMEXGOD — Framexgod.com` / blank / 3 hashtags max.
3. Stage The Studio ledger from Marco's PC (`C:\Users\marco\studio-firm\ledger\studio.sqlite` plus its `-wal` and `-shm` files)
   and run `python3 tools/ai-news/publish.py <studio.sqlite> <date> <slug> <n> <caption_file>`.
4. Add the post to `feed.json` → `posted` and the topic to `covered_topics`. Commit and push.
5. Send Marco the permalink in one line.
