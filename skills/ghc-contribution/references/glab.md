# glab (GitLab CLI) on gitlab.haskell.org

Prefer `glab` when it's logged in to gitlab.haskell.org:

    glab auth status --hostname gitlab.haskell.org

With a login it reads what the anonymous API can't: discussions, labels and milestones. It also
handles paging and JSON output. Without a login, use this skill's scripts, which need no token.
Sources: `glab <command> --help` (glab 1.99), <https://gitlab.com/gitlab-org/cli>, and
<https://docs.gitlab.com/user/profile/personal_access_tokens/>.

## Setup (the user does this, once)

- Create a personal access token at
  <https://gitlab.haskell.org/-/user_settings/personal_access_tokens>, with an expiry date.
  - `read_api` alone is enough for everything an agent does with this skill: search, view,
    comments, CI, labels. It can't post or change anything, which matches the rule that the
    user publishes. This is the safe choice.
  - Add `api` only if the user wants glab itself to create issues, MRs or comments, or to retry
    jobs.
- Log in without putting the token on the command line or in the shell history, and keep it in
  the OS keyring rather than glab's plaintext config:

      glab auth login --hostname gitlab.haskell.org --git-protocol ssh --use-keyring --stdin < token.txt

  With the ssh git protocol, git keeps using SSH keys, so a `read_api` token doesn't get in the
  way of pushes.
- Agents must not print or read the token: no `--show-token`, and don't open glab's config file.

## Always point glab at the right host

Outside a checkout whose remotes are on gitlab.haskell.org, `-R ghc/ghc` goes to **gitlab.com**,
and the answer is "404 Not Found". So either export the host, or give the full URL:

    export GITLAB_HOST=gitlab.haskell.org                # then -R ghc/ghc works anywhere
    glab issue list -R https://gitlab.haskell.org/ghc/ghc ...   # or the full URL each time

## Recipes (with `GITLAB_HOST=gitlab.haskell.org`)

Duplicate check, issues and MRs, all states. `--search` matches titles and descriptions:

    glab issue list -R ghc/ghc --all --search "library-dirs-static" --per-page 20
    glab mr list    -R ghc/ghc --all --search "library-dirs-static" --per-page 20
    # more filters: --label "backport needed:10.0", --author <user>, --closed, --merged,
    # --created-after 2026-01-01 (MRs), --in title (issues)

For compact machine-readable output, use the long flag `--output json`. Its short form
differs (`-O` for `issue list`, `-F` for `mr list`). Keep only the fields you need:

    glab mr list -R ghc/ghc --all --search "<term>" --output json |
      python3 -c 'import json,sys; [print("!%s [%s] %s" % (m["iid"], m["state"], m["title"])) for m in json.load(sys.stdin)]'

Read an issue or MR, with its discussion. The output starts with the full description:

    glab issue view 27926 -R ghc/ghc --comments
    glab mr view 16791 -R ghc/ghc --comments --unresolved   # open review threads only
    glab mr diff 16791 -R ghc/ghc --color=never

From a commit to its MR (the API's commit-to-MR lookup is empty for marge-bot merges):

    glab mr list -R ghc/ghc --all --search "<commit subject>"

CI of an MR from a fork: the pipeline runs in the fork, so address the fork and the branch.
`glab ci get -R ghc/ghc --merge-request N` won't find it.

    glab ci get -R <user>/ghc -b <branch> --output json    # pipeline with jobs, durations, failure reasons
    glab ci trace <job-id> -R <user>/ghc | tail -n 80      # downloads the whole log first

When bandwidth matters, `scripts/ghc-mr-ci.py --log <job URL>` caps the download.

Anything else through the API, authenticated, e.g. labels and milestones:

    glab api "projects/1/labels?search=backport&per_page=100"
    glab api "projects/1/milestones?search=10.0"
    glab api --paginate "projects/1/merge_requests?labels=backport%20needed:10.0&state=opened"

Keep paging bounded: every page costs tokens.

## Writing (only with the user's explicit go-ahead, and an `api` token)

`glab issue create`, `glab mr create`, `glab issue note`, `glab mr note`, and `glab ci retry
<job-id> -R <user>/ghc`. Show the user the exact command first. The skill's default stays the
same: prepare texts in files, and let the user post them.

## Avoid

- Interactive commands: `glab ci view` (a TUI), and `glab ci trace` or `glab ci retry` without
  a job ID, both of which prompt.
- `glab search semantic`: gitlab.haskell.org answers "404 Not Found" (tested 2026-10-10). Search
  the code with `git grep` in a local checkout instead.
- Unbounded `--paginate` over issues or MRs.

## Also available

- `glab skills install --global` installs glab's own generic skill to `~/.agents/skills/glab`.
  It complements this one.
- `glab mcp serve` runs an MCP server (experimental) for agents that use MCP tools.
