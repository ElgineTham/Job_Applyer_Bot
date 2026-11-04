#!/usr/bin/env python3
"""Locked FIFO queue on job_links.json, shared by job_finder (push) and ats_scorer (pop).

Usage:
  python3 jobqueue.py reset            # empty the queue
  python3 jobqueue.py push '<job json>' # append one job to the back (skips duplicate jobright_id)
  python3 jobqueue.py pop              # print the front job as JSON and remove it; prints nothing if empty
  python3 jobqueue.py peek             # print the queue size
"""
import fcntl
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, "job_links.json")
LOCK = os.path.join(HERE, ".job_links.lock")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load():
    try:
        with open(QUEUE) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data.setdefault("source", "jobright_recommend")
    data.setdefault("jobs", [])
    return data


def save(data):
    data.pop("status", None)
    data["updated_at"] = now()
    data["count"] = len(data["jobs"])
    tmp = QUEUE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, QUEUE)  # atomic: readers never see a half-written file


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # one writer at a time
        if cmd == "reset":
            save({"source": "jobright_recommend", "jobs": []})
        elif cmd == "push":
            job = json.loads(sys.argv[2])
            data = load()
            if not any(j.get("jobright_id") == job.get("jobright_id") for j in data["jobs"]):
                data["jobs"].append(job)
                save(data)
            print(len(data["jobs"]))
        elif cmd == "pop":
            data = load()
            if data["jobs"]:
                job = data["jobs"].pop(0)
                save(data)
                print(json.dumps(job))
        elif cmd == "peek":
            print(len(load()["jobs"]))
        else:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
