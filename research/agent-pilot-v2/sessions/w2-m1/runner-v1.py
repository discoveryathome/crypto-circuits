import datetime,hashlib,json,os,subprocess,time,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,o):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(o,separators=(',',':'))+'\n');os.replace(t,p)
start=json.loads((P/'start.json').read_text());seed=int(start['seed'],16)&((1<<64)-1)
front=json.loads((P/'starting-frontier.json').read_text());files=[]
for i,r in enumerate(front):
 p=ROOT/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];c=json.loads(p.read_text());out=P/f'start-{i}.txt';out.write_text(f"{c['inputs']} {len(c['gates'])} {len(c['outputs'])}\n"+'\n'.join(f'{a} {b}' for _,a,b in c['gates'])+'\n'+' '.join(map(str,c['outputs']))+'\n');files.append(str(out))
phase=int(sys.argv[2]) if len(sys.argv)>2 else 0
seed=(seed+phase*0x9e3779b97f4a7c15)&((1<<64)-1)
with (P/'derived-seeds.jsonl').open('a') as f:f.write(json.dumps({'phase':phase,'seed':seed,'derivation':'(low64(start.seed)+phase*0x9e3779b97f4a7c15) mod 2^64','at':now()})+'\n')
for path in sorted((P/'submissions').glob('*.json')):
 c=json.loads(path.read_text());out=P/f'own-{path.stem}.txt';out.write_text(f"{c['inputs']} {len(c['gates'])} {len(c['outputs'])}\n"+'\n'.join(f'{a} {b}' for _,a,b in c['gates'])+'\n'+' '.join(map(str,c['outputs']))+'\n');files.append(str(out));front.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
cmd=[str(P/'search-bin'),str(seed),sys.argv[1],*files];atomic(P/f'phase-{phase}-lineage.json',{'command':cmd,'starts':front,'source_sha256':hashlib.sha256((P/'search.cpp').read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256((P/'search-bin').read_bytes()).hexdigest(),'at':now()})
with (P/f'phase-{phase}.stderr').open('w') as err:
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=err,text=True)
 with (P/f'phase-{phase}-checkpoints.jsonl').open('a') as log:
  for line in proc.stdout:
   ev=json.loads(line);ev['checkpoint_at']=now();c=ev.pop('circuit');data=(json.dumps(c,separators=(',',':'))+'\n').encode();h=hashlib.sha256(data).hexdigest();ev['sha256']=h;cp=P/f'checkpoint-{h[:12]}.json';cp.write_bytes(data);ev['checkpoint_path']=str(cp);log.write(json.dumps(ev)+'\n');log.flush()
   checks=[]
   for tool in ['check_submission.py','audit_submission.py']:
    t=time.monotonic();r=subprocess.run(['python3','-I',str(ROOT/'tools'/tool),str(ROOT/'portfolio/whirlwindm1.json'),str(cp)],capture_output=True,text=True,timeout=10);checks.append({'tool':tool,'code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'wall_seconds':time.monotonic()-t})
   ev['checks']=checks;ev['seed']=seed;ev['parent_start']=front[ev['parent']]
   if all(x['code']==0 for x in checks):
    dest=P/'submissions'/f'candidate-{ev["XOR"]}-{ev["depth"]}-{h[:12]}.json';tmp=dest.with_suffix('.tmp');tmp.write_bytes(data);os.replace(tmp,dest);ev['submitted_at']=now();ev['path']=str(dest)
   else:ev['invalid']=True
   with (P/'receipts.jsonl').open('a') as f:f.write(json.dumps(ev)+'\n')
   front.append({'path':ev.get('path',str(cp)),'sha256':h});print(json.dumps(ev),flush=True)
 code=proc.wait()
atomic(P/f'phase-{phase}-completion.json',{'returncode':code,'ended_at':now()})
sys.exit(code)
