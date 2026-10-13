"""Render a day's carousel in the Brand Bible look.  usage: python3 make.py <spec.json> <raw_bg_dir>
spec.json: {"date": "2026-10-13", "slug": "c2", "code": "FXG-N002", "tag": "AI × MUSIC",
            "source": "SRC: MUSIC BUSINESS WORLDWIDE · OCT 09 2026", "caption": "...",
            "slides": [{"bg": "s1", "head": "...", "body": "...", "tag": "...", "swipe": "...", "size": 50}]}
Slides alternate polarity automatically: odd = positive (void black), even = negative (bone white).
Backgrounds are read from <raw_bg_dir>/<bg>.png. Output: news/<date>/<slug>_NN.jpg (repo root relative)."""
import json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import compose

spec = json.load(open(sys.argv[1])); raw = sys.argv[2]
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
out = os.path.join(root, "news", spec["date"]); os.makedirs(out, exist_ok=True)
label = datetime.date.fromisoformat(spec["date"]).strftime("%b %d %Y").upper()
n = len(spec["slides"])
for i, s in enumerate(spec["slides"], 1):
    compose({"bg": os.path.join(raw, s["bg"] + ".png"), "idx": f"{i:02d}/{n:02d}", "code": spec["code"],
             "negative": s.get("negative", i % 2 == 0),
             "spec": [f"{spec['code']} / {s.get('tag', spec['tag'])}", "25.7617° N, 80.1918° W", f"MIAMI FL · {label}"] + spec["source"].split(" · ", 1)[:1] + ([spec["source"].split(" · ", 1)[1]] if " · " in spec["source"] else []),
             "tag": s.get("tag", spec["tag"]), "head": s["head"], "body": s.get("body"),
             "size": s.get("size", 46), "lift": s.get("lift", 150), "focus": s.get("focus", (0.5, 0.45)), "source": spec["source"], "swipe": s.get("swipe", "SWIPE  >")},
            os.path.join(out, f"{spec['slug']}_{i:02d}.jpg"), seed=7 + i)
    print("rendered", i)
