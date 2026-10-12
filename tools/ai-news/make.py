"""Render a day's carousel.  usage: python3 make.py <spec.json> <raw_bg_dir>
spec.json: {"date": "2026-10-13", "slug": "c1", "tag": "AI × FILM", "source": "SOURCE: ...",
            "caption": "...", "slides": [{"bg": "s1", "head": "...", "body": "...", "highlight": [0], "size": 66, "tag": "...", "swipe": "..."}]}
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
    compose({"bg": os.path.join(raw, s["bg"] + ".png"), "date": label, "idx": f"{i:02d}/{n:02d}",
             "tag": s.get("tag", spec["tag"]), "head": s["head"], "body": s.get("body"), "highlight": s.get("highlight"),
             "size": s.get("size", 66), "source": spec["source"], "swipe": s.get("swipe", "SWIPE →"), "mode": "inset"},
            os.path.join(out, f"{spec['slug']}_{i:02d}.jpg"), seed=7 + i)
    print("rendered", i)
