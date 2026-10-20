"""Original deterministic maximal unshared-cone Huffman rebalancing."""
import collections,heapq,json,random,sys,hashlib
from pathlib import Path
import rewrite
p=Path(__file__).resolve().parent
rng=random.Random(int(sys.argv[1]));front=[(166,10),(240,5)];out=p/'balance-search';out.mkdir(exist_ok=True)
for src in sys.argv[2:]:
 c=json.loads(Path(src).read_text());g,outs=rewrite.semantic(c);uses=collections.Counter(outs)
 for a,b in g.values():uses[a]+=1;uses[b]+=1
 for trial in range(300):
  h={};depth={1<<i:0 for i in range(32)}
  def build(z):
   if z in depth:return
   leaves=[]
   def flatten(t):
    if t in g and uses[t]==1 and t not in outs:
     a,b=g[t];flatten(a);flatten(b)
    else:leaves.append(t)
   a,b=g[z];flatten(a);flatten(b)
   leaves=[x for x,count in collections.Counter(leaves).items() if count%2]
   for x in leaves:build(x)
   heap=[(depth[x],rng.random(),x) for x in leaves];heapq.heapify(heap)
   while len(heap)>1:
    _,_,a=heapq.heappop(heap);_,_,b=heapq.heappop(heap);v=a^b
    if not v:continue
    dep=1+max(depth[a],depth[b])
    if v not in depth or dep<depth[v]:h[v]=(a,b);depth[v]=dep
    heapq.heappush(heap,(depth[v],rng.random(),v))
   assert heap and heap[0][2]==z
  order=outs[:];rng.shuffle(order)
  for z in order:build(z)
  cc,m,d=rewrite.rebuild(h,outs,32)
  if not any(a<=m[0] and b<=m[1] for a,b in front):
   front[:]=[(a,b) for a,b in front if not(m[0]<=a and m[1]<=b)]+[m]
   digest=hashlib.sha256((json.dumps(cc,separators=(',',':'))+'\n').encode()).hexdigest();dest=out/f'candidate-{m[0]}-{m[1]}-{digest[:12]}.json';rewrite.atomic(dest,cc);print(json.dumps({'path':str(dest),'metrics':m,'source':src}),flush=True)
print(json.dumps({'tested':300*(len(sys.argv)-2),'frontier':front}),flush=True)
