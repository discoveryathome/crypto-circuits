#!/usr/bin/env python3
"""Original circuit transposition with free permutation equivalence search."""
import json,itertools,heapq,collections,random,sys,os,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from linear_pilot.checker import verify
p=Path(__file__).resolve().parent
m=json.loads((ROOT/'portfolio/whirlwindm1.json').read_text())['matrix'];targets=[sum(b<<i for i,b in enumerate(row)) for row in m];mt=list(map(list,zip(*m)))
perms=[]
for bits in itertools.permutations(range(4)):
 for rev in [False,True]:
  for shift in range(8):
   mapping=[4*(((-w if rev else w)+shift)%8)+bits[b] for w in range(8) for b in range(4)]
   rows=[sum(b<<mapping[i] for i,b in enumerate(row)) for row in mt]
   if set(rows)==set(targets):perms.append((mapping,[rows.index(t) for t in targets]))
print(json.dumps({'permutation_equivalences':len(perms)}),flush=True)
(p/'transpose-equivalences.json').write_text(json.dumps(perms)+'\n')
if not perms:sys.exit(0)

def transpose(c,rng):
 n=c['inputs'];lists=[[] for _ in range(n+len(c['gates']))];v=[1<<i for i in range(len(c['outputs']))];d=[0]*len(v);new={'inputs':len(v),'gates':[],'outputs':[]};known={val:i for i,val in enumerate(v)}
 for i,o in enumerate(c['outputs']):lists[o].append(i)
 def total(xs):
  xs=[i for i,count in collections.Counter(xs).items() if count%2]
  if not xs:return None
  heap=[(d[i],rng.random(),i) for i in xs];heapq.heapify(heap)
  while len(heap)>1:
   _,_,a=heapq.heappop(heap);_,_,b=heapq.heappop(heap);z=v[a]^v[b]
   if not z:continue
   if z in known:k=known[z]
   else:k=len(v);v.append(z);d.append(max(d[a],d[b])+1);new['gates'].append(['XOR',a,b]);known[z]=k
   heapq.heappush(heap,(d[k],rng.random(),k))
  return heap[0][2] if heap else None
 for j in range(len(c['gates'])-1,-1,-1):
  w=n+j;a,b=c['gates'][j][1:];z=total(lists[w])
  if z is not None:lists[a].append(z);lists[b].append(z)
 new['outputs']=[total(lists[i]) for i in range(n)]
 return new
rng=random.Random(int(sys.argv[1]));out=p/'transpose-search';out.mkdir(exist_ok=True)
front=[(166,10),(240,5)]
for src in sys.argv[2:]:
 c=json.loads(Path(src).read_text())
 for iteration in range(30):
  t=transpose(c,rng);mapping,ordering=rng.choice(perms)
  t['gates']=[[op,mapping[a] if a<32 else a,mapping[b] if b<32 else b] for op,a,b in t['gates']];t['outputs']=[t['outputs'][i] for i in ordering]
  try:result=verify(t,json.loads((ROOT/'portfolio/whirlwindm1.json').read_text()))
  except Exception as e:print('FAIL',e);raise
  # prune any CSE leftovers with the session semantic routine
  import rewrite
  g,o=rewrite.semantic(t);t,metric,_=rewrite.rebuild(g,o,32)
  if not any(a<=metric[0] and b<=metric[1] for a,b in front):
   front[:]=[(a,b) for a,b in front if not(metric[0]<=a and metric[1]<=b)]+[metric]
   digest=hashlib.sha256(json.dumps(t,separators=(',',':')).encode()).hexdigest();dest=out/f'candidate-{metric[0]}-{metric[1]}-{digest[:12]}.json';rewrite.atomic(dest,t);print(json.dumps({'source':src,'iteration':iteration,'metrics':metric,'path':str(dest)}),flush=True)
