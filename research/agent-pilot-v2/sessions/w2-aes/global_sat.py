# Original finite semantic-universe depth-bounded circuit extraction.
from pathlib import Path
import z3,json,time,sys,hashlib,datetime,os,subprocess,collections
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,o):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(o,indent=2)+'\n');os.replace(t,p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
name=sys.argv[1];Dmax=int(sys.argv[2]);bound=int(sys.argv[3]);seconds=float(sys.argv[4]);bridges=int(sys.argv[5]);D=P/name;D.mkdir();start=json.loads((P/'start.json').read_text());seed=(int(start['seed'],16)&((1<<64)-1))^int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],'big');front=json.loads((P/'starting-frontier.json').read_text())
starts=[json.loads((ROOT/s['path']).read_text()) for s in front];n=32;vs=[1<<i for i in range(n)];ids={v:i for i,v in enumerate(vs)}
def add(v):
 if v not in ids:ids[v]=len(vs);vs.append(v)
 return ids[v]
for c in starts:
 vv=[1<<i for i in range(n)]
 for _,a,b in c['gates']:vv.append(vv[a]^vv[b])
 for shift in range(4):
  for v in vv:add(((v<<(8*shift))|(v>>(32-8*shift)))&0xffffffff if shift else v)
N=len(vs);freq=collections.Counter(vs[a]^vs[b] for a in range(N) for b in range(a+1,N) if (vs[a]^vs[b]) not in ids and (vs[a]^vs[b]).bit_count()<=4)
for v,k in sorted(freq.items(),key=lambda t:(-t[1],t[0]))[:bridges]:add(v)
N=len(vs);opts=[[] for _ in vs]
for a in range(N):
 for b in range(a+1,N):
  u=ids.get(vs[a]^vs[b]);
  if u is not None and u>=n:opts[u].append((a,b))
spec=ROOT/'portfolio/square-aes-mugi.json';sp=json.loads(spec.read_text());targets=[sum(int(x)<<i for i,x in enumerate(row)) for row in sp['matrix']];outs=[ids[t] for t in targets]
# A finite semantic graph, no claim to encompass arbitrary circuits.
used=[z3.Bool(f'u{i}') for i in range(N)];dep=[z3.Int(f'd{i}') for i in range(N)];solver=z3.Solver();solver.set(random_seed=seed&0x3fffffff)
for i in range(n):solver.add(used[i],dep[i]==0)
for u in range(n,N):
 mind=(vs[u].bit_count()-1).bit_length();solver.add(dep[u]>=mind,z3.Implies(used[u],dep[u]<=Dmax));alternatives=[]
 for a,b in opts[u]:
  if max((vs[a].bit_count()-1).bit_length(),(vs[b].bit_count()-1).bit_length())<Dmax:alternatives.append(z3.And(used[a],used[b],dep[u]>dep[a],dep[u]>dep[b]))
 solver.add(z3.Implies(used[u],z3.Or(alternatives)))
for o in outs:solver.add(used[o])
# Verify the finite model contains a supplied witness at the requested depth.
validation=None
for c in starts:
 vv=[1<<i for i in range(n)];dd=[0]*n
 for _,a,b in c['gates']:vv.append(vv[a]^vv[b]);dd.append(1+max(dd[a],dd[b]))
 if max(dd[o] for o in c['outputs'])>Dmax:continue
 known={ids[v]:d for v,d in zip(vv,dd)};solver.push()
 for u in range(N):
  solver.add(used[u] if u in known else z3.Not(used[u]))
  if u in known:solver.add(dep[u]==known[u])
 solver.set(timeout=5000);validation=str(solver.check());solver.pop();assert validation=='sat',validation;break
solver.add(z3.PbLe([(used[u],1) for u in range(n,N)],bound))
receipt=dict(name=name,seed=seed,seed_derivation='low64 XOR first8 SHA256(name) big-endian; z3 receives low30 bits',started_at=now(),source_sha256=sha(Path(__file__)),parent_hashes=[s['sha256'] for s in front],universe=N,options=sum(map(len,opts)),depth_limit=Dmax,count_bound=bound,timeout_seconds=seconds,installed_z3_version=z3.get_version_string(),baseline_model_validation=validation,status='running');atomic(D/'receipt.json',receipt)
remain=datetime.datetime.fromisoformat(start['deadline']).timestamp()-time.time()-8;solver.set(timeout=int(min(seconds,remain)*1000));t=time.monotonic();cpu=time.process_time();result=solver.check();receipt.update(status=str(result),ended_at=now(),solver_wall_seconds=time.monotonic()-t,solver_cpu_seconds=time.process_time()-cpu,statistics=str(solver.statistics()))
if result==z3.sat:
 model=solver.model();chosen={};wire={i:i for i in range(n)};g=[]
 def emit(u):
  if u in wire:return wire[u]
  du=model.eval(dep[u]).as_long()
  for a,b in opts[u]:
   if z3.is_true(model.eval(used[a])) and z3.is_true(model.eval(used[b])) and model.eval(dep[a]).as_long()<du and model.eval(dep[b]).as_long()<du:
    aa,bb=emit(a),emit(b);wire[u]=n+len(g);g.append(['XOR',aa,bb]);return wire[u]
  raise RuntimeError('no extraction option')
 output=[emit(o) for o in outs];c=dict(inputs=n,gates=g,outputs=output);p=D/'candidate.json';atomic(p,c);receipt['first_checkpoint_at']=now();receipt['checks']=[]
 for tool in ['tools/check_submission.py','tools/audit_submission.py']:
  t=time.monotonic();x=subprocess.run([sys.executable,'-I',str(ROOT/tool),str(spec),str(p)],capture_output=True,text=True,timeout=10);assert x.returncode==0;receipt['checks'].append(dict(tool=tool,returncode=x.returncode,stdout=x.stdout,stderr=x.stderr,wall_seconds=time.monotonic()-t))
 ds=[0]*n
 for _,a,b in g:ds.append(1+max(ds[a],ds[b]))
 receipt['XOR']=len(g);receipt['depth']=max(ds[o] for o in output);receipt['sha256']=sha(p);S=P/'submissions';S.mkdir(exist_ok=True);q=S/f'candidate-{len(g)}-{receipt["depth"]}-{receipt["sha256"][:12]}.json';atomic(q,c);receipt['atomic_submission_at']=now();receipt['submission_path']=str(q);atomic(q.with_suffix('.receipt.json'),receipt)
atomic(D/'receipt.json',receipt);print(json.dumps(receipt),flush=True)
