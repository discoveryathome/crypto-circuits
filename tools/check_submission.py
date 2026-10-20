#!/usr/bin/env python3
"""Run with python3 -I tools/check_submission.py SPEC CANDIDATE."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from linear_pilot.checker import read_json, verify

if __name__ == "__main__":
    try:
        spec = read_json(sys.argv[1])
        candidate = read_json(sys.argv[2])
        print(json.dumps(verify(candidate, spec), sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        sys.exit(1)
