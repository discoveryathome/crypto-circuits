#!/usr/bin/env python3
"""Fetch pinned SBP data and regenerate excluded certificates; never execute it."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import heapq
import json
from pathlib import Path
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_sbp import parse as parse_sbp16


def digest(data):
    return hashlib.sha256(data).hexdigest()


def destination(relative):
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents:
        raise ValueError("Artifact path escapes repository")
    return path


def store(item, data):
    if digest(data) != item["sha256"]:
        raise ValueError("SHA-256 mismatch: " + item["path"])
    path = destination(item["path"])
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refusing to overwrite different bytes: " + item["path"])
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".download")
    temporary.write_bytes(data)
    temporary.replace(path)


def fetch(item):
    path = destination(item["path"])
    if path.exists():
        store(item, path.read_bytes())
        return
    url = item["url"]
    prefix = "https://raw.githubusercontent.com/demirmehmet0/SBP/"
    if not url.startswith(prefix + "f3880c8f87085e3eead3029593cee781e94ee60a/"):
        raise ValueError("Expected a pinned SBP raw-data URL")
    request = urllib.request.Request(url, headers={"User-Agent": "crypto-circuits-artifact-fetcher"})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Artifact exceeds size limit")
    store(item, data)


def parse_sbp32(path):
    names = {f"x{i:02d}": i for i in range(32)}
    depth, gates = [0] * 32, []
    for line in path.read_text().splitlines():
        if "=" not in line:
            continue
        match = re.fullmatch(r"([ty]\d+)\s*=\s*([xty0-9+ ]+)", line)
        if not match:
            raise ValueError("Unexpected assignment in SBP data")
        lhs, rhs = match.groups()
        if lhs in names:
            raise ValueError("Repeated assignment")
        queue = [(depth[names[x.strip()]], names[x.strip()]) for x in rhs.split("+")]
        if not 2 <= len(queue) <= 4:
            raise ValueError("Unexpected native fan-in")
        heapq.heapify(queue)
        while len(queue) > 1:
            da, a = heapq.heappop(queue)
            db, b = heapq.heappop(queue)
            wire = 32 + len(gates)
            gates.append(["XOR", a, b])
            depth.append(max(da, db) + 1)
            heapq.heappush(queue, (depth[-1], wire))
        names[lhs] = queue[0][1]
    return {"inputs": 32, "gates": gates, "outputs": [names[f"y{i:02d}"] for i in range(32)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Also restore the original 32-instance calibration's SBP data")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "sources/optional-artifacts.json").read_text())
    items = [x for x in manifest["artifacts"] if args.all or x["group"] == "agent"]
    downloads = [x for x in items if "url" in x]
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(fetch, downloads))
    for item in items:
        if "transform" not in item:
            continue
        source = destination(item["source"])
        transform = {"sbp16": parse_sbp16, "sbp32": parse_sbp32}[item["transform"]]
        data = (json.dumps(transform(source), indent=2) + "\n").encode()
        store(item, data)
    print(json.dumps({"ok": True, "hash_checked_artifacts": len(items),
                      "download_inputs": len(downloads),
                      "upstream_code_executed": False}, indent=2))


if __name__ == "__main__":
    main()
