# usage: python3 check_seen.py domain1.com domain2.com ...  -> prints which domains are already in the lead list
import sys,hashlib,os
D=os.path.dirname(os.path.abspath(__file__))
seen=set(open(os.path.join(D,'seen_domains.txt')).read().split()) if os.path.exists(os.path.join(D,'seen_domains.txt')) else set()
for d in sys.argv[1:]:
    d=d.lower().strip().removeprefix('www.')
    print(d,'SEEN' if hashlib.sha256(d.encode()).hexdigest()[:16] in seen else 'new')
