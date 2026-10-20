import pathlib,json,subprocess,time,datetime,hashlib,sys,resource
D=pathlib.Path(__file__).parent; run=int(sys.argv[1]); duration=float(sys.argv[2]); expand=sys.argv[3]
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
seed=(json.loads((D/'seed.json').read_text())['low64']+run*0x9e3779b97f4a7c15)&((1<<64)-1)
cmd=[str(D/'graph'),str(seed),str(duration),str(D/'starts.txt'),expand]
started=now(); t=time.monotonic(); cpu=resource.getrusage(resource.RUSAGE_CHILDREN)
log=(D/f'run-{run}.stderr').open('w'); raw=(D/f'run-{run}.jsonl').open('w')
p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=log,text=True)
records=[]
for line in p.stdout:
 raw.write(line);raw.flush();c=json.loads(line);c['first_checkpoint_at']=now();b=(json.dumps(c.pop('circuit'),separators=(',',':'))+'\n').encode();sha=hashlib.sha256(b).hexdigest();path=D/'checkpoints'/f'{sha}.json';path.write_bytes(b)
 c.update(sha256=sha,seed=seed,run=run,source_sha256=hashlib.sha256((D/'graph.cpp').read_bytes()).hexdigest(),parent_frontier=json.loads((D/'starting-frontier.json').read_text())[c['parent_index']]['sha256'])
 checks=[]
 for tool in ['check_submission.py','audit_submission.py']:
  q=subprocess.run([sys.executable,'-I','tools/'+tool,'portfolio/whirlwindm0.json',str(path)],capture_output=True,text=True,timeout=10);checks.append({'tool':tool,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr})
 c['checks']=checks
 if all(x['returncode']==0 for x in checks):
  dest=D/'submissions'/f'xor{c["XOR"]}-depth{c["depth"]}-{sha[:12]}.json';tmp=dest.with_suffix('.tmp');tmp.write_bytes(b);tmp.replace(dest);c['submitted_at']=now();c['path']=str(dest);print('VERIFIED',c['XOR'],c['depth'],sha,flush=True)
 else:print('INVALID',sha,flush=True)
 records.append(c);(D/f'run-{run}-candidates.json').write_text(json.dumps(records,indent=2))
code=p.wait();log.close();raw.close();after=resource.getrusage(resource.RUSAGE_CHILDREN)
(D/f'run-{run}-receipt.json').write_text(json.dumps({'command':cmd,'seed':seed,'started_at':started,'ended_at':now(),'wall_seconds':time.monotonic()-t,'children_cpu_seconds':after.ru_utime+after.ru_stime-cpu.ru_utime-cpu.ru_stime,'returncode':code,'source_sha256':hashlib.sha256((D/'graph.cpp').read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256((D/'graph').read_bytes()).hexdigest(),'candidate_count':len(records)},indent=2))
