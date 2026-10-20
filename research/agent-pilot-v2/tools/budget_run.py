#!/usr/bin/env python3
"""Run a session's own search command inside its recorded elapsed-time cap."""
import argparse
import datetime
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    directory = EXPERIMENT/"sessions"/args.session
    receipt = json.loads((directory/"start.json").read_text())
    deadline = datetime.datetime.fromisoformat(receipt["deadline"]).timestamp()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        raise SystemExit("missing command")
    remaining = deadline-time.time()
    if remaining <= 0:
        raise SystemExit("session deadline reached")
    started, before = now(), resource.getrusage(resource.RUSAGE_CHILDREN)
    clock = time.monotonic()
    process = subprocess.Popen(command, cwd=ROOT, start_new_session=True)
    timed_out = False
    try:
        code = process.wait(timeout=remaining)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGTERM)
        try:
            code = process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            code = process.wait()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    event = dict(command=command, started_at=started, ended_at=now(),
                 wall_seconds=time.monotonic()-clock,
                 cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
                 returncode=code, deadline_stop=timed_out)
    with (directory/"processes.jsonl").open("a") as f:
        f.write(json.dumps(event)+"\n")
    print(json.dumps(event), flush=True)
    raise SystemExit(0 if timed_out else code)


if __name__ == "__main__":
    main()
