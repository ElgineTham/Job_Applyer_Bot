#!/usr/bin/env python3
"""Locked results file ats_passed.json, shared by every ats_scorer running at once.

Usage:
  python3 passed.py reset              # empty the results (job_finder runs this at startup)
  python3 passed.py add '<job json>'   # insert or replace one job (dedupe by jobright_id)
  python3 passed.py add <<'EOF'        # same, reading the job JSON from stdin
  { ...job json... }
  EOF
  python3 passed.py count              # print how many jobs are saved
  python3 passed.py add --any-score ... # test runs only: also accept scores below 75

`add` keeps jobs sorted by ats_score (highest first), updates count and updated_at,
and refuses a job below the threshold or without jobright_id / ats_score.
"""
import fcntl
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PASSED = os.path.join(HERE, "ats_passed.json")
LOCK = os.path.join(HERE, ".ats_passed.lock")
THRESHOLD = 75


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load():
    try:
        with open(PASSED) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data.setdefault("jobs", [])
    return data


def save(data):
    data["updated_at"] = now()
    data["threshold"] = THRESHOLD
    data["jobs"].sort(key=lambda j: j.get("ats_score", 0), reverse=True)
    data["count"] = len(data["jobs"])
    ordered = {k: data[k] for k in ("updated_at", "threshold", "count", "jobs")}
    tmp = PASSED + ".tmp"
    with open(tmp, "w") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, PASSED)  # atomic: readers never see a half-written file


ANY_SCORE = "--any-score" in sys.argv  # test runs only: accept scores below the threshold
if ANY_SCORE:
    sys.argv.remove("--any-score")


def read_job():
    raw = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else sys.stdin.read()
    job = json.loads(raw)
    if not isinstance(job, dict) or not job.get("jobright_id"):
        sys.exit("error: job JSON needs a jobright_id")
    if not isinstance(job.get("ats_score"), (int, float)):
        sys.exit("error: job JSON needs a numeric ats_score")
    if job["ats_score"] < THRESHOLD and not ANY_SCORE:
        sys.exit(f"error: ats_score {job['ats_score']} is below the threshold {THRESHOLD}")
    return job


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    job = read_job() if cmd == "add" else None  # parse before locking
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # one writer at a time
        if cmd == "reset":
            save({"jobs": []})
        elif cmd == "add":
            data = load()
            data["jobs"] = [j for j in data["jobs"] if j.get("jobright_id") != job["jobright_id"]]
            data["jobs"].append(job)
            save(data)
            print(len(data["jobs"]))
        elif cmd == "count":
            print(len(load()["jobs"]))
        else:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
