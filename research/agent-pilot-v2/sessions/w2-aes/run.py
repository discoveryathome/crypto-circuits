import pathlib,json,hashlib,sys,subprocess,time,datetime,os,resource
P=pathlib.Path(__file__).resolve().parent; ROOT=P.parents[3]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,o):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(o,indent=2)+'\n');os.replace(t,p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
name=sys.argv[1];secs=float(sys.argv[2]);bridges=sys.argv[3];source=sys.argv[4] if len(sys.argv)>4 else 'union.cpp'
start=json.loads((P/'start.json').read_text());seed=(int(start['seed'],16)&((1<<64)-1))^({'union-v1':0,'union-v2':0x9e3779b97f4a7c15,'union-v3':0xd1b54a32d192ed03}.get(name, int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],'big')))
D=P/name;D.mkdir();front=json.loads((P/'starting-frontier.json').read_text());spec=ROOT/'portfolio/square-aes-mugi.json';sp=json.loads(spec.read_text());paths=[]
for i,s in enumerate(front):
 p=ROOT/s['path'];assert sha(p)==s['sha256'];c=json.loads(p.read_text());out=D/f'start-{i}.txt';out.write_text(f"{c['inputs']} {len(c['gates'])} {len(c['outputs'])}\n"+'\n'.join(f'{g[1]} {g[2]}' for g in c['gates'])+'\n'+' '.join(map(str,c['outputs']))+'\n');paths.append(str(out))
mat=D/'matrix.txt';mat.write_text(f"{sp['inputs']} {sp['outputs']}\n"+' '.join(str(sum(int(x)<<i for i,x in enumerate(r))) for r in sp['matrix'])+'\n')
bin=P/(source+'.bin');compilecmd=['c++','-O3','-std=c++17',str(P/source),'-o',str(bin)];ts=time.monotonic();subprocess.run(compilecmd,check=True);compiletime=time.monotonic()-ts
remain=datetime.datetime.fromisoformat(start['deadline']).timestamp()-time.time()-8;secs=min(secs,remain);cmd=[str(bin),str(seed),str(secs),str(secs),bridges,str(mat),*paths]
receipt={'name':name,'seed':seed,'seed_derivation':'low64 XOR named constant; unnamed runs XOR first8 SHA256(name) big-endian','started_at':now(),'command':cmd,'compile_command':compilecmd,'compile_wall':compiletime,'source_sha256':sha(P/source),'toolkit_sha256':sha(P/'toolkit.cpp'),'binary_sha256':sha(bin),'starts':front,'status':'running','checkpoints':[]};atomic(D/'receipt.json',receipt)
with (D/'progress.log').open('w') as log,(D/'raw-checkpoints.jsonl').open('w') as raw:
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=log,text=True);t0=time.monotonic()
 for line in proc.stdout:
  raw.write(line);raw.flush();r=json.loads(line);c=r.pop('circuit');r['first_checkpoint_at']=now();p=D/f'candidate-{len(receipt["checkpoints"])}.json';atomic(p,c);r['sha256']=sha(p);r['path']=str(p)
  checks=[]
  for tool in ['tools/check_submission.py','tools/audit_submission.py']:
   t=time.monotonic();x=subprocess.run([sys.executable,'-I',str(ROOT/tool),str(spec),str(p)],capture_output=True,text=True,timeout=10);checks.append({'tool':tool,'returncode':x.returncode,'stdout':x.stdout,'stderr':x.stderr,'wall_seconds':time.monotonic()-t});assert x.returncode==0,x.stderr
  r['checks']=checks
  prior=any(s['metrics']['XOR']<=r['XOR'] and s['metrics']['depth']<=r['depth'] for s in front);r['dominated_by_issued_prior']=prior
  if not prior:
   sub=P/'submissions';sub.mkdir(exist_ok=True);q=sub/f'candidate-{r["XOR"]}-{r["depth"]}-{r["sha256"][:12]}.json';atomic(q,c);r['atomic_submission_at']=now();r['submission_path']=str(q);atomic(q.with_suffix('.receipt.json'),dict(r,seed=seed,method_version=source,parent_hashes=[s['sha256'] for s in front],source_sha256=sha(P/source)))
  receipt['checkpoints'].append(r);atomic(D/'receipt.json',receipt);print(json.dumps({k:r[k] for k in ['XOR','depth','sha256','dominated_by_issued_prior']}),flush=True)
 code=proc.wait();receipt.update(status='complete' if code==0 else 'failed',returncode=code,ended_at=now(),search_wall_seconds=time.monotonic()-t0);atomic(D/'receipt.json',receipt)
 sys.exit(code)
