# FRAMEXGOD daily outreach runner (GitHub Actions), set up at the owner's request.
# Lead data is sealed; logs print counts only.
import hashlib,os,json,glob,csv,tarfile,io,subprocess,datetime,base64,re
from nacl.public import PrivateKey,SealedBox
SK=PrivateKey(base64.b64decode(os.environ['OUTREACH_SK'])); box=SealedBox(SK); seal=SealedBox(SK.public_key)
CAP=int(os.environ.get('DAILY_CAP') or 90)
W=os.path.abspath('work'); os.makedirs(W,exist_ok=True)
tarfile.open(fileobj=io.BytesIO(box.decrypt(open('data.sealed','rb').read()))).extractall(W)
P=lambda f:os.path.join(W,f)
KEY=os.environ.get('RESEND_KEY') or open(P('resend.key')).read().strip()
print(f'::add-mask::{KEY}')
log=json.load(open(P('outreach_log.json')))
known=set()
for f in ('leads_enriched.csv','leads_wave2.csv'):
    for r in csv.DictReader(open(P(f))): known.add(r['email'].strip().lower())
F2=['name','category','city','website','instagram','email','phone','contact_name','why_now','source_url','market']
added=replied=0
skip=open(P('skip_extra.txt'),'a')
for f in sorted(glob.glob('inbox/*.sealed')):
    try: d=json.loads(box.decrypt(open(f,'rb').read()))
    except Exception: os.remove(f); continue
    rows=[r for r in d.get('leads',[]) if '@' in (r.get('email') or '') and r['email'].strip().lower() not in known]
    with open(P('leads_wave2.csv'),'a',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=F2,extrasaction='ignore')
        for r in rows:
            r={k:(r.get(k) or '') for k in F2}; r['email']=r['email'].strip()
            if r['market'] not in ('Miami','New York','Los Angeles'): r['market']='Miami'
            w.writerow(r); known.add(r['email'].lower()); added+=1
    for m in d.get('replied',[]):
        m=m.strip().lower()
        if not m: continue
        dom=m.split('@')[-1]
        for x in log:
            t=x['to'].lower()
            if (t==m or t.endswith('@'+dom)) and not x.get('replied'): x['replied']=True; replied+=1
        if '@' in m: skip.write(m+'\n')
    os.remove(f)
skip.close(); json.dump(log,open(P('outreach_log.json'),'w'),indent=1)

def run(args,env=None):
    r=subprocess.run(['python3']+args,cwd=W,capture_output=True,text=True,env={**os.environ,**(env or {})})
    with open(P('run_'+args[0].replace('.py','')+'.log'),'a') as fh: fh.write(f"--- {datetime.datetime.utcnow()}\n{r.stdout}\n{r.stderr}\n")
    return r.stdout

def reseal():
    buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode='w:gz') as t:
        for f in os.listdir(W):
            if f not in ('wave.json','__pycache__'): t.add(P(f),arcname=f)
    open('data.sealed','wb').write(seal.encrypt(buf.getvalue()))

def main():
    run(['resend_stats.py',KEY])
    fo=run(['followup.py',KEY],{'FU_MAX':str(CAP)}); fu=fo.count('fu sent')
    new=max(0,CAP-fu); sent=0; note=''
    if new:
        run(['compose3.py',str(new)])
        so=run(['send_paced.py',KEY,'20','40',datetime.date.today().isoformat()])
        sent=sum(1 for l in so.splitlines() if l.startswith('sent '))
        note='; '.join(re.sub(r'\[.*?\]','',l) for l in so.splitlines() if l.startswith(('STOP','FINAL')))
    log=json.load(open(P('outreach_log.json')))
    done={x['to'].lower() for x in log}
    bad={b.lower() for b in json.load(open(P('bounced.json')))} if os.path.exists(P('bounced.json')) else set()
    rem=len({e for e in known if '@' in e and e not in done and e not in bad})
    st={'date':datetime.date.today().isoformat(),'followups_sent':fu,'new_sent':sent,'leads_added':added,'replies_marked':replied,
        'remaining_leads':rem,'total_contacted':len(log),'total_replied':sum(1 for x in log if x.get('replied')),'note':note}
    json.dump(st,open('status.json','w'),indent=1); print(json.dumps(st))
    import hashlib
    doms=sorted({hashlib.sha256(e.split('@')[-1].encode()).hexdigest()[:16] for e in known if '@' in e})
    open('seen_domains.txt','w').write('\n'.join(doms)+'\n')

try:
    main()
finally:
    reseal()
