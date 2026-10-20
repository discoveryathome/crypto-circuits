import pathlib,json,hashlib
D=pathlib.Path(__file__).parent
p=D/'run-0-starts.json'
if not p.exists():p.write_text((D/'starting-frontier.json').read_text())
records=[]
for p in sorted(D.glob('run-*-starts.json')):
 manifest=json.loads(p.read_text()); lines=[str(len(manifest))]
 for x in manifest:
  src=pathlib.Path(x['path']);assert hashlib.sha256(src.read_bytes()).hexdigest()==x['sha256'];c=json.loads(src.read_text());lines.append(f"{c['inputs']} {len(c['gates'])} {len(c['outputs'])}");lines.extend(f'{a} {b}' for _,a,b in c['gates']);lines.append(' '.join(map(str,c['outputs'])))
 target=p.with_suffix('.txt');target.write_text('\n'.join(lines)+'\n');records.append({'manifest':str(p),'replay_input':str(target),'input_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'starts':len(manifest)})
(D/'replay-inputs.json').write_text(json.dumps(records,indent=2));print('archived',len(records),'run inputs')
