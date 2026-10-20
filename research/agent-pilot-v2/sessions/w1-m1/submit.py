from pathlib import Path
import os,json,subprocess,time,hashlib,datetime,sys
p=Path(__file__).resolve().parent;d=p/'submissions';d.mkdir(exist_ok=True)
with (p/'standalone-checks.jsonl').open('a') as f:
 for directory in sys.argv[1:]:
  receipt=p/directory/'receipt.json'
  starts=set()
  if receipt.exists():starts={Path(r['path']).name for r in json.loads(receipt.read_text()).get('checkpoints',[]) if r['method']=='start'}
  for c in sorted((p/directory).glob('candidate-*.json')):
   if c.name in starts:continue
   dest=d/c.name
   if dest.exists():continue
   t=dest.with_suffix('.tmp');t.write_bytes(c.read_bytes());os.replace(t,dest)
   for tool in ['check_submission.py','audit_submission.py']:
    begun=time.monotonic();r=subprocess.run(['python3','-I','tools/'+tool,'portfolio/whirlwindm1.json',str(dest)],capture_output=True,text=True)
    record={'candidate':str(dest),'submitted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(c.read_bytes()).hexdigest(),'tool':tool,'returncode':r.returncode,'wall_seconds':time.monotonic()-begun,'result':json.loads(r.stdout),'stderr':r.stderr};f.write(json.dumps(record)+'\n');f.flush();print(json.dumps(record))
