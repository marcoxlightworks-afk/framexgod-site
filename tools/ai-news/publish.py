"""Publish a carousel already hosted on framexgod.com to @framexgod.
usage: python3 publish.py <studio.sqlite> <date> <slug> <n_slides> <caption_file>
The Instagram token is read from The Studio's ledger (kv 'ig:token'); it never lives in this repo."""
import json, sqlite3, sys, time, urllib.parse, urllib.request
db, date, slug, n, capfile = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
c = sqlite3.connect(db)
tok = json.loads(c.execute("select value from kv where key='ig:token'").fetchone()[0])["access_token"]
uid = json.loads(c.execute("select value from kv where key='ig:app'").fetchone()[0])["user_id"]
H = "https://graph.instagram.com/v21.0"

def call(method, path, **p):
    p["access_token"] = tok
    data = urllib.parse.urlencode(p).encode()
    url = f"{H}/{path}" + ("" if method == "POST" else "?" + data.decode())
    req = urllib.request.Request(url, data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path.split('?')[0]} -> {e.code}: {e.read().decode()[:400]}")

def ready(cid):
    for _ in range(40):
        s = call("GET", cid, fields="status_code").get("status_code")
        if s == "FINISHED": return
        if s == "ERROR": raise SystemExit(f"container {cid} failed")
        time.sleep(3)
    raise SystemExit(f"container {cid} not ready")

kids = [call("POST", f"{uid}/media", image_url=f"https://framexgod.com/news/{date}/{slug}_{i:02d}.jpg", is_carousel_item="true")["id"] for i in range(1, n + 1)]
for k in kids: ready(k)
car = call("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(kids), caption=open(capfile).read().strip())
ready(car["id"])
pub = call("POST", f"{uid}/media_publish", creation_id=car["id"])
print(json.dumps({"date": date, "slug": slug, "media_id": pub["id"], **call("GET", pub["id"], fields="permalink,timestamp")}))
