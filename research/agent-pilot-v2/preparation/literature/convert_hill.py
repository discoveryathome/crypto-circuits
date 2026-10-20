"""Read-only normalization of published Table 9 data; no downloaded code execution."""
from pathlib import Path
import json,heapq,sys,subprocess
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from linear_pilot.checker import verify
BASE=Path(__file__).resolve().parent
names={f'x{i}':i for i in range(32)};depth=[0]*32;gates=[];fanin={2:0,3:0}
for line in (BASE/'hill-table9.txt').read_text().splitlines():
 lhs,rhs=line.split('='); operands=[names[x] for x in rhs.split('+')];fanin[len(operands)]+=1
 # Smallest arrival first minimizes output depth for a fixed XOR2 tree.
 q=[(depth[i],i) for i in operands];heapq.heapify(q)
 while len(q)>1:
  da,a=heapq.heappop(q);db,b=heapq.heappop(q);wire=32+len(gates)
  gates.append(['XOR',a,b]);depth.append(max(da,db)+1);heapq.heappush(q,(depth[-1],wire))
 names[lhs]=q[0][1]
c={'inputs':32,'gates':gates,'outputs':[names[f'y{i}'] for i in range(32)]}
spec=json.loads((ROOT/'portfolio/square-aes-mugi.json').read_text())
# Port adapters are literal within-byte reversals, as used by NIST current AES witness.
variants=[]
for reverse in [False,True]:
 c2=json.loads(json.dumps(c))
 if reverse:
  for g in c2['gates']:
   for j in (1,2):
    if g[j]<32:g[j]=(g[j]//8)*8+7-g[j]%8
  c2['outputs']=[c2['outputs'][(i//8)*8+7-i%8] for i in range(32)]
 try:
  r=verify(c2,spec)
 except Exception as e:r={'ok':False,'error':str(e)}
 variants.append({'reverse_bits_within_bytes':reverse,'result':r})
 if r.get('ok'):
  p=BASE/'aes-mixcolumns-hill-table9-binary.json';p.write_text(json.dumps(c2,indent=2)+'\n')
  second=subprocess.run([sys.executable,str(ROOT/'tools/audit_submission.py'),str(ROOT/'portfolio/square-aes-mugi.json'),str(p)],capture_output=True,text=True)
  variants[-1]['second_checker']=json.loads(second.stdout)
print(json.dumps({'native_fanin_counts':fanin,'variants':variants},indent=2))
(BASE/'hill-normalization.json').write_text(json.dumps({'native_fanin_counts':fanin,'variants':variants},indent=2)+'\n')
