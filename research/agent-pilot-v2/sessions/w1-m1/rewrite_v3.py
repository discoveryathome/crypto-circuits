#!/usr/bin/env python3
"""Original semantic-DAG relaxation and associative cone rewriting, version 3, depth-biased.
Only original local code. Fixed semantic vertices are relaxed to minimum arrival;
associative mutations replace an unshared intermediate then CSE/prune the graph.
"""
import argparse,collections,datetime,hashlib,heapq,json,os,random,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
import sys
sys.path.insert(0,str(ROOT))
from linear_pilot.checker import verify
import importlib.util
sp=importlib.util.spec_from_file_location('audit',ROOT/'tools/audit_submission.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
def atomic(p,o):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(o,separators=(',',':'))+'\n');os.replace(t,p)
def semantic(c):
 v=[1<<i for i in range(c['inputs'])];g={}
 for _,a,b in c['gates']:
  z=v[a]^v[b];v.append(z);g[z]=(v[a],v[b])
 return g,[v[a] for a in c['outputs']]
def rebuild(g,outs,n):
 c={'inputs':n,'gates':[],'outputs':[]}; ids={1<<i:i for i in range(n)};depth={1<<i:0 for i in range(n)};active=set()
 def add(z):
  if z in ids:return ids[z]
  if z in active:raise ValueError('cycle')
  active.add(z);a,b=g[z];aa,bb=add(a),add(b);active.remove(z)
  ids[z]=n+len(c['gates']);c['gates'].append(['XOR',aa,bb]);depth[z]=1+max(depth[a],depth[b]);return ids[z]
 c['outputs']=[add(z) for z in outs]
 return c,(len(c['gates']),max(depth[z] for z in outs)),depth

def relax(g,outs,n,rng):
 nodes=list(set(g)|{1<<i for i in range(n)});have=set(nodes);pairs=collections.defaultdict(list)
 for i,a in enumerate(nodes):
  for b in nodes[:i]:
   z=a^b
   if z in g:pairs[z].append((a,b))
 d={1<<i:0 for i in range(n)};chosen={}
 changed=True
 while changed:
  changed=False
  order=list(g);rng.shuffle(order)
  for z in order:
   pp=pairs[z][:];rng.shuffle(pp)
   for a,b in pp:
    if a in d and b in d:
     dd=1+max(d[a],d[b])
     if dd<d.get(z,10000):d[z]=dd;chosen[z]=(a,b);changed=True
 c,m,depth=rebuild(chosen,outs,n)
 return semantic(c)[0],m

def mutation(g,outs,n,rng):
 uses=collections.Counter(outs)
 for a,b in g.values():uses[a]+=1;uses[b]+=1
 candidates=[x for x in g if x not in outs and (uses[x]==1 or rng.random()<0.08)]
 if not candidates:return g
 x=rng.choice(candidates);a,b=g[x]
 parents=[(y,c if d==x else d) for y,(c,d) in g.items() if x in (c,d)]
 if not parents:return g
 y,c=rng.choice(parents)
 if rng.randrange(2):a,b=b,a
 z=a^c
 if z==0 or z==y or z==x:return g
 h=g.copy()
 if uses[x]==1:del h[x]
 if z not in h and z.bit_count()!=1:h[z]=(a,c)
 h[y]=(z,b)
 try:cc,m,dd=rebuild(h,outs,n)
 except (KeyError,ValueError):return g
 return semantic(cc)[0]
def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int);p.add_argument('--seconds',type=float);p.add_argument('--start',action='append');p.add_argument('--output');a=p.parse_args()
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);spec=json.loads((ROOT/'portfolio/whirlwindm1.json').read_text());rng=random.Random(a.seed);t=time.monotonic();front=[];events=[];iterations=0
 starts=[]
 for path in a.start:
  c=json.loads(Path(path).read_text());g,o=semantic(c);cc,m,d=rebuild(g,o,c['inputs']);front.append(m);starts.append((g,o,c['inputs']))
 def offer(g,o,n,method):
  c,m,d=rebuild(g,o,n)
  if any(x<=m[0] and y<=m[1] for x,y in front):return
  p=verify(c,spec);s=mod.audit(spec,c);digest=hashlib.sha256((json.dumps(c,separators=(',',':'))+'\n').encode()).hexdigest();dest=out/(f'candidate-{m[0]}-{m[1]}-{digest[:12]}.json');atomic(dest,c)
  front[:]=[(x,y) for x,y in front if not(m[0]<=x and m[1]<=y)]+[m]
  starts.append((g.copy(),o,n))
  rec={'iteration':iterations,'elapsed':time.monotonic()-t,'method':method,'path':str(dest),'metrics':m,'sha256':digest,'primary':p,'second':s};events.append(rec);atomic(out/'receipt.json',{'seed':a.seed,'frontier':front,'events':events,'iterations':iterations});print(json.dumps(rec),flush=True)
 current,outs,n=starts[0];base=current.copy();bestcount=len(current);stagnant=0
 while time.monotonic()-t<a.seconds:
  if iterations%1000==0:
   current,outs,n=rng.choice([entry for entry in starts if len(entry[0])<=169]);current,m=relax(current,outs,n,rng);offer(current,outs,n,'semantic-relaxation');bestcount=m[0];stagnant=0
  h=mutation(current,outs,n,rng)
  if iterations%20==0:h,m=relax(h,outs,n,rng)
  c,m,d=rebuild(h,outs,n);old,om,od=rebuild(current,outs,n)
  # Explore neutral count moves while allowing depth walks around each start.
  score=lambda mm:mm[0]*3+mm[1]*6
  temperature=0.8+1.4*(1-(iterations%1000)/1000)
  import math
  delta=score(m)-score(om)+0.12*sum(d[z]-od[z] for z in outs)
  if m[0]<=169 and (delta<=0 or rng.random()<math.exp(-delta/temperature)):current=h
  offer(h,outs,n,'associative-semantic-walk')
  iterations+=1;stagnant+=1
  if m[0]<bestcount:bestcount=m[0];stagnant=0;starts.append((h,outs,n))
  if iterations%1000==0:print(json.dumps({'progress':iterations,'elapsed':time.monotonic()-t,'current':m,'frontier':front}),flush=True)
 atomic(out/'receipt.json',{'seed':a.seed,'frontier':front,'events':events,'iterations':iterations,'elapsed':time.monotonic()-t,'status':'complete'})
if __name__=='__main__':main()
