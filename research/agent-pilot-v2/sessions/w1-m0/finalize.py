import pathlib,json,datetime,subprocess,sys,hashlib
P=pathlib.Path(__file__).resolve().parent
subprocess.run([sys.executable,str(P/'submit_checkpoints.py')],check=True)
subprocess.run([sys.executable,str(P/'summarize.py')],check=True)
s=json.loads((P/'session-summary.json').read_text())
r=json.loads((P/'search-rotation-4/receipt.json').read_text())
assert r['status']=='complete',r['status']
stop=r['search_stopped_observed_unix_ns'];deadline=datetime.datetime.fromisoformat(s['deadline']).timestamp()
assert stop/1e9<=deadline
versions={hashlib.sha256(f.read_bytes()).hexdigest():str(f) for f in (P/'versions').glob('*')}
source_consistency=[]
for f in P.glob('search-rotation-*/receipt.json'):
 v=json.loads(f.read_text());source_consistency.append({'attempt':f.parent.name,'source_sha256':v['source_sha256'],'source_preserved':v['source_sha256'] in versions,'wrapper_sha256':v['wrapper_sha256'],'wrapper_preserved':v['wrapper_sha256'] in versions})
assert all(x['source_preserved'] and x['wrapper_preserved'] for x in source_consistency)
front_hashes={x['sha256'] for x in s['pareto_proposals']}
method_results=[]
for f in sorted(P.glob('search-*/receipt.json')):
 v=json.loads(f.read_text());fresh=[x for x in v['checkpoints'] if x['method']!='start']
 method_results.append({'attempt':f.parent.name,'seed':v['seed'],'status':v['status'],'new_checkpoints':len(fresh),'final_frontier_points':[(x['XOR'],x['depth']) for x in fresh if x['sha256'] in front_hashes],'progress_final_line':(f.parent/'progress.log').read_text().splitlines()[-1]})
s['method_results']=method_results
now=datetime.datetime.now(datetime.timezone.utc)
s.update(status='complete',stop_reason='Final fixed-budget search phase completed before hard deadline; remaining session time used for provenance and receipt cleanup. No optimality claim.',search_stop_observed_at=datetime.datetime.fromtimestamp(stop/1e9,datetime.timezone.utc).isoformat(),search_stop_observed_unix_ns=stop,receipt_cleanup_ended_at=now.isoformat(),actual_ended_at=now.isoformat(),actual_elapsed_seconds=(now-datetime.datetime.fromisoformat(s['issued_at'])).total_seconds(),search_stopped_before_deadline=True,source_receipt_consistency=source_consistency)
(P/'session-summary.json').write_text(json.dumps(s,indent=2)+'\n')
(P/'checkpoint.json').write_text(json.dumps({'at':now.isoformat(),'stage':'session complete','final_summary':'session-summary.json','search_stop_observed_at':s['search_stop_observed_at'],'protocol_deviation_retained':True},indent=2)+'\n')
print(json.dumps({'final':True,'submissions':s['submissions'],'elapsed_seconds':s['actual_elapsed_seconds'],'search_stop_observed_at':s['search_stop_observed_at'],'cleanup_ended_at':s['receipt_cleanup_ended_at'],'process_cpu_seconds':s['process_cpu_seconds'],'process_wall_seconds':s['process_wall_seconds'],'frontier':[(x['XOR'],x['depth']) for x in s['pareto_proposals']]}))
