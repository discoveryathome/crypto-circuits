import pathlib,json,hashlib,sys,subprocess
P=pathlib.Path(__file__).resolve().parent
root=P.parents[3]
label=sys.argv[1];wall=sys.argv[2]
s=json.loads((P/'start.json').read_text()); seed=int.from_bytes(hashlib.sha256(bytes.fromhex(s['seed'])+label.encode()).digest()[:8],'big')
seeds=json.loads((P/'seeds.json').read_text());seeds['attempts'].append({'id':label,'seed':seed,'derivation':"int.from_bytes(SHA256(bytes.fromhex(full_seed)+label.encode()).digest()[:8], 'big')",'label':label});(P/'seeds.json').write_text(json.dumps(seeds,indent=2)+'\n')
starts=[str(root/x['path']) for x in json.loads((P/'starting-frontier.json').read_text())]
cp=[]
for r in P.glob('search-*/receipt.json'):
 for c in json.loads(r.read_text())['checkpoints']:
  if c['method']!='start':cp.append(c)
for c in cp:
 if not any(x['XOR']<=c['XOR'] and x['depth']<=c['depth'] and (x['XOR'],x['depth'])!=(c['XOR'],c['depth']) for x in cp):
  if c['path'] not in starts:starts.append(c['path'])
cmd=[sys.executable,str(P/'run_search.py'),'--spec',str(root/'portfolio/whirlwindm0.json'),'--seed',str(seed),'--cpu-seconds',wall,'--wall-seconds',wall,'--output',str(P/label)]
for start in starts:cmd+=['--start',start]
print(json.dumps({'label':label,'seed':seed,'starts':starts}),flush=True)
raise SystemExit(subprocess.call(cmd,cwd=root))
