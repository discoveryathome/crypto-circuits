import json,pathlib,hashlib,datetime
D=pathlib.Path(__file__).parent
s=json.loads((D/'start.json').read_text()); seed=int(s['seed'],16)&((1<<64)-1)
f=json.loads((D/'starting-frontier.json').read_text())
lines=[str(len(f))]
for x in f:
 p=pathlib.Path(x['path']); assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
 c=json.loads(p.read_text()); lines.append(f"{c['inputs']} {len(c['gates'])} {len(c['outputs'])}")
 for op,a,b in c['gates']: assert op=='XOR'; lines.append(f'{a} {b}')
 lines.append(' '.join(map(str,c['outputs'])))
(D/'starts.txt').write_text('\n'.join(lines)+'\n')
(D/'seed.json').write_text(json.dumps({'seed_hex':s['seed'],'low64':seed,'derivation':'int(start.seed,16) & ((1<<64)-1)','further':'run seed = (low64 + run_index * 0x9e3779b97f4a7c15) mod 2^64','prepared_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'starts':f},indent=2))
print(seed)
