# FRAMEXGOD // AI NEWS: daily carousel playbook

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
1. Hook: one sentence, 8–14 words. Its payoff line is highlighted orange.
2–5. Story: short headline (≤ 6 words) plus a 1–2 sentence body. One fact per slide.
6. Optional "FRAMEXGOD TAKE": one plain line on what it means for creators. Use the per-slide tag "FRAMEXGOD TAKE".
Last. CTA: `Follow @framexgod\nfor AI × <film|music|tech> news.`, body "New stories every week.", swipe "@FRAMEXGOD", highlight [0].

Rules: plain words, no hype. No quotes longer than 10 words. Credit sources in `source` (e.g. "SOURCE: VARIETY · OCT 13 2026").
Real people can be named, but are never shown in images.

## 3. Backgrounds (Higgsfield)
- Model: `gpt_image_2_5`. aspect_ratio `4:5`, quality `high`, resolution `2k`. About 2.75 credits each, one per slide.
- Submit in batches of 4 (bigger batches hit rate limits), then `jobs_wait`.
- Each prompt uses the six-block structure, in order:
  SUBJECT → ACTION → ENVIRONMENT → ART STYLE/CAMERA → LIGHTING → DETAILS & CONSTRAINTS.
- ART STYLE/CAMERA always: "ARRI Alexa 35, Cooke S4 prime, <lens>, Kodak Vision3 500T film emulation, photoreal cinematic still,
  documentary realism, not a 3D render." Lighting is ARRI fixtures and motivated practicals.
- DETAILS & CONSTRAINTS always end with: "Keep the lower 30 percent of the frame darker and calm. No text, no letters, no numbers,
  no logos, no signage, no people, no faces, no hands, no recognizable trademarked objects or award statuettes, no warped geometry,
  no oversaturation."
- Subjects are objects and places that tell the story (screens, marquees, studios, consoles, servers), never people,
  real products or brand marks.
- Download each result to `<raw>/s1.png … sN.png`.

## 4. Render
Write `<raw>/spec.json` (see the docstring in `make.py`). Then run `python3 tools/ai-news/make.py <raw>/spec.json <raw>`.
Needs Pillow and numpy. The look is fixed in `compose.py`: inverted film negative, grain, scanlines, the normal image
in a "LIVE FEED" window, and the FRAMEXGOD // AI NEWS bar. Do not change it.

## 5. Check before posting
Open every rendered slide and look at it. Check that no text is cut off, there are no orphan words, the highlight sits on the
payoff, the facts match the source, there are no typos, no faces, and nothing that looks like a trademarked object.
Fix and re-render until it is clean.

## 6. Publish
1. Commit `news/<date>/` and push to `main`. Wait until `https://framexgod.com/news/<date>/<slug>_01.jpg` returns 200.
2. Write the caption to a file: hook line, 1–2 sentences, a question, "Follow @framexgod for AI × … news every week.",
   "Source: …", then 8–9 hashtags ending in #framexgod.
3. Stage The Studio ledger from Marco's PC (`C:\Users\marco\studio-firm\ledger\studio.sqlite` plus its `-wal` and `-shm` files)
   and run `python3 tools/ai-news/publish.py <studio.sqlite> <date> <slug> <n> <caption_file>`.
4. Add the post to `feed.json` → `posted` and the topic to `covered_topics`. Commit and push.
5. Send Marco the permalink in one line.
