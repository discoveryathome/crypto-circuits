"""Seeded local task suggestion; inspect live Discussions before claiming work."""
import argparse,json,random,secrets
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--seed')
p.add_argument('--expert',action='store_true',help='Include tasks requiring qualified scientific review')
a=p.parse_args();seed=a.seed or secrets.token_hex(16)
if len(seed)!=32 or any(x not in '0123456789abcdefABCDEF' for x in seed):p.error('seed must be 32 hexadecimal digits')
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'discover.json').read_text())
c=json.loads((root/manifest['catalog']).read_text())
tracks=[t for t in c['tracks'] if t['weight']>0 and (a.expert or t['id']!='expert-review')]
rng=random.Random(int(seed,16));draw=rng.randrange(sum(t['weight'] for t in tracks))
for t in tracks:
    if draw<t['weight']:break
    draw-=t['weight']
card=t['tasks'][rng.randrange(len(t['tasks']))]
print(json.dumps(dict(seed=seed.lower(),priority_revision=c['priority_revision'],track=t['id'],task=card,
    status='suggestion only; inspect live Discussions before claiming; no message sent'),indent=2))
