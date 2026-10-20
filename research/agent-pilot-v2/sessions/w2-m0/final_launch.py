import pathlib,json,datetime,time,subprocess,sys
D=pathlib.Path(__file__).parent; deadline=datetime.datetime.fromisoformat(json.loads((D/'start.json').read_text())['deadline']).timestamp();duration=max(0,deadline-time.time()-13)
cmd=[sys.executable,str(D/'run.py'),'5',str(duration),'0'];print(json.dumps({'final_command':cmd,'cleanup_reserve_seconds':13}),flush=True);raise SystemExit(subprocess.call(cmd))
