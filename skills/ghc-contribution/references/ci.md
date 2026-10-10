# Reading GHC CI

Sources: `.gitlab-ci.yml`, `.gitlab/ci.sh`, `.gitlab/generate-ci/gen_ci.hs`,
`.gitlab/jobs.yaml`, and `Contributing-a-Patch` §5.

## Where pipelines run

- An MR from a fork runs its pipeline in the fork project, the MR's `source_project_id`.
  `scripts/ghc-mr-ci.py <N>` finds it. So does `glab ci get -R <user>/ghc -b <branch> --output json`,
  but not `glab ci get --merge-request N`.
- The default MR pipeline is a subset of the jobs. ~"full-ci" runs all of them, and marge-bot
  always runs the full pipeline. Labels such as ~wasm, ~javascript, ~"RISC-V" and ~"LLVM
  backend" add their jobs.

## Before assuming the patch broke something

1. List the jobs with their durations and failure reasons: `scripts/ghc-mr-ci.py <N>`. A job
   that failed in under a minute hasn't built anything.
2. Read only the failing job's log tail, with a size cap: `scripts/ghc-mr-ci.py --log <job URL>`.
3. Failures that aren't the patch's fault:
   - `fatal: early EOF` or `fetch-pack: invalid index-pack output` under "Getting source": the
     runner couldn't fetch the fork. Retry; if it keeps happening, ask @triagers to run the
     pipeline in ghc/ghc.
   - `lint-changelog`: there's no changelog entry and no ~"no-changelog" label.
   - Errors from the docker registry or HTTP while pulling images: retry.
4. A real failure is a compile error, or a testsuite failure ("Unexpected failures:") in the log.
   Reproduce it locally before changing the patch.

## Which configurations CI covers

`.gitlab/jobs.yaml` is generated from `gen_ci.hs`. Apart from its first line, it's JSON. To
list the jobs by configure flags:

    tail -n +2 .gitlab/jobs.yaml > /tmp/jobs.json
    python3 - /tmp/jobs.json <<'EOF'
    import json, sys
    for name, job in sorted(json.load(open(sys.argv[1])).items()):
        v = job.get("variables", {}) if isinstance(job, dict) else {}
        print(name, v.get("CONFIGURE_ARGS", ""), v.get("ENABLE_NUMA", ""))
    EOF

Use this before writing "CI doesn't exercise this" in an MR. For #27926, only the FreeBSD 14
jobs pass `--with-ffi-libraries`.
