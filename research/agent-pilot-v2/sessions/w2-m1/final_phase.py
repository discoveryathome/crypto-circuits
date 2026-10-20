import datetime,json,os,sys,time
from pathlib import Path
p=Path(__file__).resolve().parent
s=json.loads((p/'start.json').read_text());seconds=datetime.datetime.fromisoformat(s['deadline']).timestamp()-time.time()-18
if seconds<=0:raise SystemExit('No time remains for search plus receipt cleanup')
os.execv(sys.executable,[sys.executable,str(p/'runner.py'),str(seconds),'3','search-v4'])
