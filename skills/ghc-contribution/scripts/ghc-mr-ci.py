#!/usr/bin/env python3
"""Show a ghc/ghc merge request's state, labels and pipelines, and its latest pipeline's jobs.

Usage: ghc-mr-ci.py MR_NUMBER        summary; failed jobs first, with durations and URLs
       ghc-mr-ci.py --log JOB_URL    error lines and tail of one job log (download capped at 5 MB)

No token needed. Pipelines of MRs from forks run in the fork project; this finds them.
Downloads go through curl, because gitlab.haskell.org's bot check lets curl through.
With glab logged in, `glab ci get -R <user>/ghc -b <branch>` also lists the jobs; see
references/glab.md. This script still finds a fork MR's pipeline from the MR number alone, and
caps log downloads.
"""
import json
import re
import subprocess
import sys

API = "https://gitlab.haskell.org/api/v4"


def curl(url, *extra):
    r = subprocess.run(["curl", "-sS", "--fail", "--max-time", "120", *extra, url],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit("ghc-mr-ci.py: fetching %s failed: %s" % (url, r.stderr.decode().strip()))
    return r.stdout


def get_json(path):
    return json.loads(curl(API + path))


def show_log(url):
    raw = curl(url.rstrip("/") + "/raw", "-L", "--max-filesize", "5000000")
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]|\r", "", raw.decode("utf-8", "replace"))
    lines = text.split("\n")
    pat = re.compile(r"fatal:|error:|ERROR|Error when running|Unexpected failures|FAILED|"
                     r"not found|cannot find|undefined reference|Exception")
    hits = [l for l in lines if pat.search(l)]
    print("== %d lines, %d matching error patterns (first 40):" % (len(lines), len(hits)))
    print("\n".join(hits[:40]))
    print("== last 25 lines:")
    print("\n".join(lines[-25:]))


def show_mr(mr):
    m = get_json("/projects/1/merge_requests/%s" % mr)
    pipes = get_json("/projects/1/merge_requests/%s/pipelines" % mr)
    print("!%s [%s%s] %s" % (m["iid"], m["state"], ", draft" if m.get("draft") else "", m["title"]))
    print("  %s -> %s, by @%s" % (m["source_branch"], m["target_branch"], m["author"]["username"]))
    if m["target_project_id"] != 1 or m["target_branch"] != "master":
        print("  NOTE: target is project %s, branch %s (usually ghc/ghc = project 1, master)"
              % (m["target_project_id"], m["target_branch"]))
    print("  labels: %s" % (", ".join(m["labels"]) or "none"))
    print("  head %s, %s" % (m["sha"][:10], m["web_url"]))
    if not pipes:
        print("no pipelines yet")
        return
    print("pipelines (latest first):")
    for p in pipes[:5]:
        print("  %s [%s] project %s, sha %s" % (p["id"], p["status"], p.get("project_id"), p["sha"][:10]))
    latest = pipes[0]
    project = latest.get("project_id") or m["source_project_id"]
    jobs = []
    for page in (1, 2, 3):
        part = get_json("/projects/%s/pipelines/%s/jobs?per_page=100&page=%d"
                        % (project, latest["id"], page))
        jobs += part
        if len(part) < 100:
            break
    order = {"failed": 0, "running": 1, "pending": 2, "created": 3, "manual": 4,
             "canceled": 5, "skipped": 6, "success": 7}
    counts = {}
    for j in jobs:
        counts[j["status"]] = counts.get(j["status"], 0) + 1
    print("jobs of pipeline %s: %s" % (latest["id"], ", ".join("%s %d" % kv for kv in sorted(counts.items()))))
    for j in sorted(jobs, key=lambda j: (order.get(j["status"], 9), j["stage"], j["name"])):
        d = int(j.get("duration") or 0)
        note = ""
        if j["status"] == "failed" and 0 < d < 90:
            note = "  <- failed after %ds, probably before building; check the log" % d
        print(("  %-8s %-11s %-45s %5ds %s%s" % (j["status"], j["stage"], j["name"], d,
                                                 j.get("failure_reason") or "", note)).rstrip())
        if j["status"] == "failed":
            print("           %s" % j["web_url"])


def main(argv):
    if argv[:1] == ["--log"] and len(argv) == 2:
        show_log(argv[1])
    elif len(argv) == 1 and argv[0] not in ("-h", "--help"):
        show_mr(argv[0].lstrip("!"))
    else:
        print(__doc__)
        return 0 if argv[:1] in (["-h"], ["--help"]) else 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
