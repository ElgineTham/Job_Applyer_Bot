#!/usr/bin/env python3
"""Locked FIFO queue on job_links.json, shared by job_finder (push) and ats_scorer (pop),
plus a permanent history (job_history.json) of every job ever pushed, so the same job is
never collected twice across runs.

Usage:
  python3 jobqueue.py reset              # empty the queue (the history is kept)
  python3 jobqueue.py seen <jobright_id> # print "seen" if the id is in the history, else "new"
  python3 jobqueue.py push '<job json>'  # append one job to the back, unless it is a duplicate:
                                         #   prints the queue size, or "duplicate of <id>"
  python3 jobqueue.py push --force '<job json>'  # re-queue a job even if it is in the history
  python3 jobqueue.py pop                # print the front job as JSON and remove it; prints nothing if empty
  python3 jobqueue.py peek               # print the queue size
  python3 jobqueue.py history-reset      # forget every job ever seen (only when asked to)

A job is a duplicate if its jobright_id is in the history, or if its original post URL
(with tracking parameters removed) matches a job already in the history. Jobs with no URL
fall back to matching on company + title.
"""
import fcntl
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, "job_links.json")
HISTORY = os.path.join(HERE, "job_history.json")
LOCK = os.path.join(HERE, ".job_links.lock")

# Query parameters that only track where a click came from; they never identify the job.
TRACKING = {"jr_id", "source", "sid", "src", "ref", "referrer", "gh_src", "lever-source",
            "lever-origin", "hl", "domain", "ccuid", "jobpipeline", "codes", "iis", "iisn"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def url_key(url):
    """Normalize an original post URL so reposts of the same job compare equal."""
    if not url:
        return None
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.rstrip("/")
    query = [(k, v) for k, v in parse_qsl(parts.query)
             if k.lower() not in TRACKING and not k.lower().startswith("utm_")]
    q = dict(query)
    # Greenhouse embed form -> canonical description page
    if host.endswith("greenhouse.io") and path.endswith("/embed/job_app") and "for" in q and "token" in q:
        return f"greenhouse.io/{q['for'].lower()}/jobs/{q['token']}"
    if host.endswith("greenhouse.io"):
        host = "greenhouse.io"
    # Application-form suffixes (Ashby /application, Lever /apply, many others)
    path = re.sub(r"/(application|apply)$", "", path)
    query_str = urlencode(sorted(query))
    return f"{host}{path}" + (f"?{query_str}" if query_str else "")


def title_key(job):
    company = re.sub(r"\W+", " ", (job.get("company") or "")).strip().lower()
    title = re.sub(r"\W+", " ", (job.get("title") or "")).strip().lower()
    return f"ct:{company}|{title}" if company and title else None


def dedupe_key(job):
    return url_key(job.get("original_post_url")) or title_key(job)


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)  # atomic: readers never see a half-written file


def load():
    data = load_json(QUEUE, {})
    data.setdefault("source", "jobright_recommend")
    data.setdefault("jobs", [])
    return data


def save(data):
    data.pop("status", None)
    data["updated_at"] = now()
    data["count"] = len(data["jobs"])
    write_json(QUEUE, data)


def load_history():
    hist = load_json(HISTORY, {})
    hist.setdefault("jobs", {})
    return hist


def save_history(hist):
    hist["updated_at"] = now()
    hist["count"] = len(hist["jobs"])
    write_json(HISTORY, {k: hist[k] for k in ("updated_at", "count", "jobs")})


def find_duplicate(job, hist):
    jid = job.get("jobright_id")
    if jid and jid in hist["jobs"]:
        return jid
    key = dedupe_key(job)
    if key:
        for other_id, entry in hist["jobs"].items():
            if entry.get("key") == key:
                return other_id
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    force = "--force" in args
    args = [a for a in args if a != "--force"]
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # one writer at a time, for the queue and the history
        if cmd == "reset":
            save({"source": "jobright_recommend", "jobs": []})
        elif cmd == "seen":
            if not args:
                sys.exit("usage: jobqueue.py seen <jobright_id>")
            print("seen" if args[0] in load_history()["jobs"] else "new")
        elif cmd == "push":
            if not args:
                sys.exit("usage: jobqueue.py push [--force] '<job json>'")
            job = json.loads(args[0])
            hist = load_history()
            dup = find_duplicate(job, hist)
            if dup and not force:
                print(f"duplicate of {dup}")
                return
            data = load()
            if not any(j.get("jobright_id") == job.get("jobright_id") for j in data["jobs"]):
                data["jobs"].append(job)
                save(data)
            if job.get("jobright_id") and job["jobright_id"] not in hist["jobs"]:
                hist["jobs"][job["jobright_id"]] = {
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "original_post_url": job.get("original_post_url"),
                    "key": dedupe_key(job),
                    "first_seen": now(),
                }
                save_history(hist)
            print(len(data["jobs"]))
        elif cmd == "pop":
            data = load()
            if data["jobs"]:
                job = data["jobs"].pop(0)
                save(data)
                print(json.dumps(job))
        elif cmd == "peek":
            print(len(load()["jobs"]))
        elif cmd == "history-reset":
            save_history({"jobs": {}})
        else:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
