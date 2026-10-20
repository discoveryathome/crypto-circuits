import pathlib,json,hashlib,datetime
D=pathlib.Path(__file__).parent
orig=json.loads((D/'starting-frontier.json').read_text()); extra=[]
for p in (D/'submissions').glob('*.json'):
 c=json.loads(p.read_text());dep=[0]*c['inputs']
 for _,a,b in c['gates']:dep.append(1+max(dep[a],dep[b]))
 extra.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'metrics':{'XOR':len(c['gates']),'depth':max(dep[x] for x in c['outputs'])},'kind':'own-dual-verified-submission'})
allc=orig+extra
front=[x for x in extra if not any(y['metrics']['XOR']<=x['metrics']['XOR'] and y['metrics']['depth']<=x['metrics']['depth'] and y['metrics']!=x['metrics'] for y in allc)]
manifest=orig+front
lines=[str(len(manifest))]
for x in manifest:
 p=pathlib.Path(x['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'];c=json.loads(p.read_text());lines.append(f"{c['inputs']} {len(c['gates'])} {len(c['outputs'])}")
 for op,a,b in c['gates']:assert op=='XOR';lines.append(f'{a} {b}')
 lines.append(' '.join(map(str,c['outputs'])))
(D/'starts.txt').write_text('\n'.join(lines)+'\n');(D/'starts-manifest.json').write_text(json.dumps(manifest,indent=2)); print('starts',len(manifest))
