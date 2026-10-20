# Original bounded semantic-window SMT resynthesis, uses installed z3 only.
from pathlib import Path
import z3,json,time,sys,random,hashlib,datetime,os,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,o):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(o,indent=2)+'\n');os.replace(t,p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
name=sys.argv[1];seconds=float(sys.argv[2]);maximum=int(sys.argv[3]);timeout=int(sys.argv[4]);D=P/name;D.mkdir();start=json.loads((P/'start.json').read_text());seed=(int(start['seed'],16)&((1<<64)-1))^int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],'big');rng=random.Random(seed)
front=json.loads((P/'starting-frontier.json').read_text());starts=[json.loads((ROOT/s['path']).read_text()) for s in front];n=32;target=None
spec=ROOT/'portfolio/square-aes-mugi.json';rows=json.loads(spec.read_text())['matrix'];targets=[sum(int(b)<<i for i,b in enumerate(row)) for row in rows]
def vals(c):
 v=[1<<i for i in range(n)]
 for _,a,b in c['gates']:v.append(v[a]^v[b])
 return v
def metrics(c):
 ds=[0]*n
 for _,a,b in c['gates']:ds.append(1+max(ds[a],ds[b]))
 return len(c['gates']),max(ds[o] for o in c['outputs'])
def prune(c):
 live=set(c['outputs'])
 for i in range(len(c['gates'])-1,-1,-1):
  if n+i in live:live.update(c['gates'][i][1:])
 mp={i:i for i in range(n)};g=[]
 for i,(_,a,b) in enumerate(c['gates']):
  if n+i in live:mp[n+i]=n+len(g);g.append(['XOR',mp[a],mp[b]])
 return dict(inputs=n,gates=g,outputs=[mp[o] for o in c['outputs']])
def reorder(c):
 pending=set(range(len(c['gates'])));done=set(range(n));mp={i:i for i in range(n)};g=[];last=set()
 while pending:
  avail=[i for i in pending if set(c['gates'][i][1:])<=done]
  weights=[1+4*len(set(c['gates'][i][1:])&last) for i in avail];i=rng.choices(avail,weights=weights)[0];_,a,b=c['gates'][i];mp[n+i]=n+len(g);g.append(['XOR',mp[a],mp[b]]);done.add(n+i);pending.remove(i);last={a,b,n+i}
 return dict(inputs=n,gates=g,outputs=[mp[o] for o in c['outputs']])
def synth(c,lo,hi,k,extra):
 v=vals(c);incoming=sorted({a for g in c['gates'][lo:hi] for a in g[1:] if a<n+lo});ext=sorted({a for g in c['gates'][hi:] for a in g[1:] if n+lo<=a<n+hi}|{o for o in c['outputs'] if n+lo<=o<n+hi})
 if len(incoming)>12 or not ext:return None,'skip'
 if extra:
  candidates=[i for i in range(n+lo) if i not in incoming and any((v[i]^v[j]).bit_count()<=2 for j in ext)]
  rng.shuffle(candidates);incoming+=candidates[:extra]
 # Select independent bit projections of input values to preserve full affine identity in this span.
 basis={};bits=[]
 for bit in range(32):
  pattern=sum(((v[a]>>bit)&1)<<i for i,a in enumerate(incoming));x=pattern
  while x:
   p=x.bit_length()-1
   if p in basis:x^=basis[p]
   else:basis[p]=x;bits.append(bit);break
 width=len(bits)
 if not width:return None,'skip'
 def proj(x):return sum(((x>>bit)&1)<<j for j,bit in enumerate(bits))
 values=[z3.BitVecVal(proj(v[a]),width) for a in incoming];s=z3.Solver();s.set(timeout=timeout,random_seed=rng.randrange(1<<30));choices=[];pairs=[]
 for i in range(k):
  opts=[(a,b) for a in range(len(values)) for b in range(a+1,len(values))];sel=z3.BitVec('s'+str(i),max(1,(len(opts)-1).bit_length()));vv=z3.BitVec('v'+str(i),width);s.add(z3.Or([sel==j for j in range(len(opts))]));s.add([z3.Implies(sel==j,vv==values[a]^values[b]) for j,(a,b) in enumerate(opts)]);s.add([vv!=x for x in values]);s.add(vv!=0);values.append(vv);choices.append(sel);pairs.append(opts)
 for a in ext:s.add(z3.Or([x==proj(v[a]) for x in values]))
 result=s.check()
 if result!=z3.sat:return None,str(result)
 model=s.model();g=c['gates'][:lo];mapping=list(incoming);sem=[v[x] for x in incoming]
 for i in range(k):
  a,b=pairs[i][model.eval(choices[i]).as_long()];g.append(['XOR',mapping[a],mapping[b]]);mapping.append(n+len(g)-1);sem.append(sem[a]^sem[b])
 mp={i:i for i in range(n+lo)}
 for a in ext:
  if v[a] not in sem:raise RuntimeError('projection failed full equality')
  mp[a]=mapping[sem.index(v[a])]
 for i,(_,a,b) in enumerate(c['gates'][hi:],hi):mp[n+i]=n+len(g);g.append(['XOR',mp[a],mp[b]])
 return prune(dict(inputs=n,gates=g,outputs=[mp[o] for o in c['outputs']])),'sat'
receipt={'name':name,'seed':seed,'seed_derivation':'low64 XOR first8 bytes SHA256(run name), big endian','source_sha256':sha(Path(__file__)),'started_at':now(),'parent_hashes':[s['sha256'] for s in front],'counts':{},'checkpoints':[],'status':'running'};atomic(D/'receipt.json',receipt)
end=min(time.time()+seconds,datetime.datetime.fromisoformat(start['deadline']).timestamp()-8);it=0;current=starts[0];best=[metrics(c) for c in starts];cpustart=time.process_time()
with (D/'progress.jsonl').open('w') as log:
 while time.time()<end:
  if it%20==0:current=reorder(starts[rng.randrange(len(starts))])
  if it%5==0:current=reorder(current)
  length=rng.randrange(3,maximum+1);lo=rng.randrange(len(current['gates'])-length);hi=lo+length;budget=length-(0 if it%4==0 else 1)
  candidate,status=synth(current,lo,hi,budget,2 if it%3==0 else 0);receipt['counts'][status]=receipt['counts'].get(status,0)+1
  if candidate is not None:
   vv=vals(candidate);assert [vv[o] for o in candidate['outputs']]==targets
   met=metrics(candidate);old=metrics(current)
   if met[0]<=old[0] and met[1]<=old[1]:current=candidate;receipt['counts']['accepted']=receipt['counts'].get('accepted',0)+1
   if not any(a<=met[0] and b<=met[1] for a,b in best):
    best=[x for x in best if not(met[0]<=x[0] and met[1]<=x[1])]+[met];r={'first_checkpoint_at':now(),'iteration':it,'XOR':met[0],'depth':met[1],'window':[lo,hi],'replacement_gates':budget};p=D/f'candidate-{it}.json';atomic(p,candidate);r['sha256']=sha(p);r['checks']=[]
    for tool in ['tools/check_submission.py','tools/audit_submission.py']:
     t=time.monotonic();q=subprocess.run([sys.executable,'-I',str(ROOT/tool),str(spec),str(p)],capture_output=True,text=True,timeout=10);assert q.returncode==0;r['checks'].append(dict(tool=tool,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr,wall_seconds=time.monotonic()-t))
    S=P/'submissions';S.mkdir(exist_ok=True);dest=S/f'candidate-{met[0]}-{met[1]}-{r["sha256"][:12]}.json';atomic(dest,candidate);r['atomic_submission_at']=now();r['submission_path']=str(dest);r['seed']=seed;r['parent_hashes']=receipt['parent_hashes'];atomic(dest.with_suffix('.receipt.json'),r);receipt['checkpoints'].append(r);print(json.dumps(r),flush=True)
  it+=1
  if it%10==0:log.write(json.dumps(dict(iteration=it,time=now(),cpu=time.process_time()-cpustart,counts=receipt['counts'],best=best))+'\n');log.flush();atomic(D/'receipt.json',receipt)
 receipt.update(status='complete',iterations=it,ended_at=now(),core_cpu_seconds=time.process_time()-cpustart,best=best);atomic(D/'receipt.json',receipt);print(json.dumps({k:receipt[k] for k in ['status','iterations','ended_at','core_cpu_seconds','counts','best']}),flush=True)
