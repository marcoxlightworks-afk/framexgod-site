# Seal new leads / replied addresses for the daily outreach runner.
# usage: python3 add_inbox.py input.json
# input JSON: {"leads":[{name,category,city,website,instagram,email,phone,contact_name,why_now,source_url,market}], "replied":["a@b.com","b.com"]}
# market must be Miami, New York or Los Angeles.
import sys,json,base64,datetime,os
from nacl.public import PublicKey,SealedBox
D=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(sys.argv[1])); assert isinstance(d,dict)
pk=PublicKey(base64.b64decode(open(os.path.join(D,'pub.key')).read().strip()))
os.makedirs(os.path.join(D,'inbox'),exist_ok=True)
fn=os.path.join(D,'inbox',f"{datetime.datetime.utcnow():%Y%m%d%H%M%S}.sealed")
open(fn,'wb').write(SealedBox(pk).encrypt(json.dumps(d).encode()))
print(fn,len(d.get('leads',[])),'leads',len(d.get('replied',[])),'replied')
