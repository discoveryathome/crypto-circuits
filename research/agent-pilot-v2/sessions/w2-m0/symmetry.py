import pathlib,json,hashlib,subprocess,sys,datetime
D=pathlib.Path(__file__).parent; auto=json.loads((D/'xor-automorphisms.json').read_text())[1:];manifest=json.loads((D/'starts-manifest.json').read_text());selected=[]
for x in manifest:
 g,d=x['metrics']['XOR'],x['metrics']['depth']
 if g<=171 and not any(y['metrics']['XOR']<=g and y['metrics']['depth']<=d and (y['metrics']['XOR']<g or y['metrics']['depth']<d) for y in manifest):selected.append(x)
(D/'derived-starts').mkdir(exist_ok=True);checks=[]
for src in selected:
 c=json.loads(pathlib.Path(src['path']).read_text())
 for a in auto:
  p=a['input_permutation'];conv=lambda v:p[v] if v<32 else v
  out={'inputs':32,'gates':[[op,conv(i),conv(j)] for op,i,j in c['gates']],'outputs':[conv(c['outputs'][i]) for i in a['output_reorder']]}
  b=(json.dumps(out,separators=(',',':'))+'\n').encode();h=hashlib.sha256(b).hexdigest();f=D/'derived-starts'/f'{h}.json';f.write_bytes(b)
  item={'path':str(f),'sha256':h,'metrics':src['metrics'],'kind':'known-cost-automorphic-start','parent_sha256':src['sha256'],'input_permutation':p,'output_reorder':a['output_reorder']}
  ch=[]
  for tool in ['check_submission.py','audit_submission.py']:
   z=subprocess.run([sys.executable,'-I','tools/'+tool,'portfolio/whirlwindm0.json',str(f)],capture_output=True,text=True,timeout=5);ch.append({'tool':tool,'returncode':z.returncode,'stdout':z.stdout});assert z.returncode==0
  checks.append({'start':item,'checks':ch});manifest.append(item)
lines=[str(len(manifest))]
for x in manifest:
 c=json.loads(pathlib.Path(x['path']).read_text());lines.append(f"32 {len(c['gates'])} 32");lines.extend(f'{a} {b}' for _,a,b in c['gates']);lines.append(' '.join(map(str,c['outputs'])))
(D/'starts.txt').write_text('\n'.join(lines)+'\n');(D/'starts-manifest.json').write_text(json.dumps(manifest,indent=2));(D/'symmetry-checks.json').write_text(json.dumps(checks,indent=2));print('symmetry starts',len(manifest))
