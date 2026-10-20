from pathlib import Path
import datetime,hashlib,json,sys
p=Path(__file__).resolve().parent;start=json.loads((p/'start.json').read_text());now=datetime.datetime.now(datetime.timezone.utc);issued=datetime.datetime.fromisoformat(start['issued_at']);records=[json.loads(x) for x in (p/'standalone-checks.jsonl').read_text().splitlines()];latest={}
for r in records:
 if r['tool']=='check_submission.py':latest[Path(r['candidate']).name]=r
proposals=[]
for path in sorted((p/'submissions').glob('*.json')):
 r=latest[path.name];m=r['result']['metrics'];c={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'metrics':m,'submitted_at':datetime.datetime.fromtimestamp(path.stat().st_birthtime,datetime.timezone.utc).isoformat()}
 matches=list(p.glob('*/'+path.name));matches=[x for x in matches if x.parent.name!='submissions']
 if matches:c['checkpoint_at']=datetime.datetime.fromtimestamp(min(x.stat().st_birthtime for x in matches),datetime.timezone.utc).isoformat()
 proposals.append(c)
allpoints=[(r['metrics']['XOR'],r['metrics']['depth'],r['path']) for r in proposals]+[(169,11,'frozen published'),(240,5,'frozen internal')]
front=[(x,y,path) for x,y,path in allpoints if not any(xx<=x and yy<=y and (xx<x or yy<y) for xx,yy,_ in allpoints)]
processes=[json.loads(x) for x in (p/'processes.jsonl').read_text().splitlines()]
sources={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in p.iterdir() if x.suffix in ('.cpp','.py') or x.name.endswith('-bin')}
summary={'session':'w1-m1','instance':'whirlwindm1','agent_task':start['agent_task'],'issued_at':start['issued_at'],'actual_session_start':start['issued_at'],'actual_session_end':now.isoformat(),'elapsed_seconds':(now-issued).total_seconds(),'deadline':start['deadline'],'seed':start['seed'],'initial_frontier_sha256':start['frontier_sha256'],'stop_reason':sys.argv[1] if len(sys.argv)>1 else 'interim checkpoint; search active','source_versions_sha256':sources,'methods':['frozen bounded-distance BP + exact-distance windows','original semantic minimum-arrival DAG relaxation and associative mutation v1','adaptive count-biased semantic walk v2','topological cone-order exact-distance windows with cut arrival times','transpose/free-port-permutation exploration','depth-biased semantic walk v3'],'proposals':proposals,'final_combined_frontier':front,'invalid_submissions':sum(1 for r in records if r['returncode']!=0 or not r['result'].get('ok')),'duplicates':'Equal-or-dominated metric offers suppressed; unique strict circuit hashes retained. Historical transient points retained and not counted separately as useful final outcomes.','novelty_status':'Pending independent candidate-specific literature/lineage review; correctness does not establish discovery.','last_search_process_ended_at':max(r['ended_at'] for r in processes),'receipt_cleanup_ended_at':now.isoformat(),'process_count':len(processes),'process_cpu_seconds':sum(r['cpu_seconds'] for r in processes),'process_wall_seconds':sum(r['wall_seconds'] for r in processes),'additional_initial_standalone_checks':2,'additional_initial_check_timing':'checking-effort-extra.json','standalone_checker_invocations':len(records),'standalone_checker_wall_seconds':sum(r['wall_seconds'] for r in records),'checker_internal_seconds':sum(r['result'].get('verification_seconds',0) for r in records),'model_token_usage':'unavailable','model_cost':'unavailable','model_identity':'inherited default; exact model accounting not exposed','limitations':['elapsed-time cap; no optimality proof','random seeds govern local search, not model sampling','local correctness checks are not external scientific review']}
def semvalues(c):
 v=[1<<i for i in range(c['inputs'])]
 for _,a,b in c['gates']:v.append(v[a]^v[b])
 return set(v[c['inputs']:])
base=semvalues(json.loads((p.parents[3]/'certificates/whirlwindm1--xu2026-size.json').read_text()))
lineage=[]
for r in proposals:
 other=semvalues(json.loads(Path(r['path']).read_text()));lineage.append({'candidate':Path(r['path']).name,'source':'certificates/whirlwindm1--xu2026-size.json','retained_semantic_intermediates':len(base&other),'removed_semantic_intermediates':len(base-other),'added_semantic_intermediates':len(other-base),'novelty':'pending independent review'})
(p/'lineage.json').write_text(json.dumps(lineage,indent=2)+'\n')
(p/'submission-timing.json').write_text(json.dumps([{'path':r['path'],'submitted_at':r['submitted_at'],'checkpoint_at':r.get('checkpoint_at'),'sha256':r['sha256']} for r in proposals],indent=2)+'\n')
summary['first_submission_at']=min(r['submitted_at'] for r in proposals)
summary['time_to_first_submission_seconds']=(datetime.datetime.fromisoformat(summary['first_submission_at'])-issued).total_seconds()
summary['first_checkpoint_at']=min(r['checkpoint_at'] for r in proposals if 'checkpoint_at' in r)
summary['time_to_first_checkpoint_seconds']=(datetime.datetime.fromisoformat(summary['first_checkpoint_at'])-issued).total_seconds()
summary['method_outcomes']={}
for receipt in p.glob('*/receipt.json'):
 data=json.loads(receipt.read_text());summary['method_outcomes'][receipt.parent.name]={'status':data.get('status'),'iterations':data.get('iterations'),'non_start_checkpoints':len(data.get('events',[])) if 'events' in data else sum(r['method']!='start' for r in data.get('checkpoints',[]))}
summary['supplementary_attempts_file']='attempts.jsonl'
(p/'session-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'elapsed_seconds':summary['elapsed_seconds'],'frontier':front,'proposals':len(proposals),'cpu_seconds':summary['process_cpu_seconds']}))
