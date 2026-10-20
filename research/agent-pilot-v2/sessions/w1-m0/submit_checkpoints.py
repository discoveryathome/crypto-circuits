import json,pathlib,os,subprocess,time,datetime,hashlib
P=pathlib.Path(__file__).resolve().parent
root=P.parents[3]
out=P/'submissions';out.mkdir(exist_ok=True)
record=P/'submission-receipts.jsonl'
prior=set()
if record.exists():
 for line in record.read_text().splitlines(): prior.add(json.loads(line)['sha256'])
for receipt in sorted(P.glob('search-*/receipt.json')):
 r=json.loads(receipt.read_text())
 for cp in r['checkpoints']:
  if cp['method']=='start' or cp['sha256'] in prior:continue
  digest=cp['sha256'];src=pathlib.Path(cp['path']);dst=out/f"xor{cp['XOR']}-depth{cp['depth']}-{digest[:12]}.json"
  tmp=dst.with_suffix('.json.tmp');tmp.write_bytes(src.read_bytes());os.replace(tmp,dst)
  checks={}
  for name in ['check_submission','audit_submission']:
   t=time.monotonic();run=subprocess.run(['python3','-I',str(root/'tools'/f'{name}.py'),str(root/'portfolio/whirlwindm0.json'),str(dst)],text=True,capture_output=True,timeout=30)
   checks[name]={'wall_seconds':time.monotonic()-t,'returncode':run.returncode,'receipt':json.loads(run.stdout),'stderr':run.stderr}
  v={'path':str(dst.relative_to(root)),'sha256':digest,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_receipt':str(receipt.relative_to(root)),'checkpoint':cp,'checks':checks,'seed_protocol_deviation':receipt.parent.name=='search-initial','novelty':'unadjudicated; root independent review required'}
  with record.open('a') as f:f.write(json.dumps(v)+'\n')
  prior.add(digest);print(json.dumps({'submission':str(dst),'XOR':cp['XOR'],'depth':cp['depth'],'both_ok':all(z['returncode']==0 for z in checks.values())}),flush=True)
