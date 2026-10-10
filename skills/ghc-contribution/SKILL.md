---
name: ghc-contribution
description: "Workflow and rules for contributing a change upstream to GHC, the Glasgow Haskell Compiler, on gitlab.haskell.org (project ghc/ghc). Covers checking for existing issues and merge requests, filing an issue, writing a minimal commit, opening the MR, reading its CI, and asking for labels and backports. Use when the user wants to report a GHC bug, prepare or submit a GHC patch or merge request, or handle GHC review, labels, CI failures or backports. Not for ordinary Haskell programming or for packages outside the GHC repository."
compatibility: "Any agent that supports Agent Skills (Claude Code, Codex, OpenCode, Pi and others). The scripts need bash, git, curl and python3, plus network access to gitlab.haskell.org."
metadata:
  version: "0.1.0"
  last-verified: "2026-10-10"
  homepage: "https://github.com/purefunsolutions/haskell-ghc-maintainer-skill"
---

# Contributing to GHC upstream

GHC is developed on GitLab, not GitHub: <https://gitlab.haskell.org/ghc/ghc> (project ID `1`
in the API). Issues are `#N`, merge requests `!N`. GitLab links both, and short commit hashes,
automatically. Paths below (`references/`, `scripts/`) are relative to this skill's directory.

## Ground rules

1. **The user publishes, you prepare.** Never push, comment, file an issue or open an MR without
   the user's explicit go-ahead. Write paste-ready texts into files instead.
2. **Search before writing anything** (step 1). Don't duplicate an existing issue or an MR in
   flight.
3. **Issue first, then the MR.** Put the issue number in the commit message (`Fixes #N.`) and in
   the MR title (`... (#N)`).
4. **Make the smallest correct change.** Don't add multi-line comments to trivial edits, and
   don't clean up nearby code. The reasoning goes into the issue and the MR. Example: #27926
   was fixed by deleting one line; the three-line comment drafted next to it added nothing.
5. **GHC's LLM policy applies** to commits, issues, MRs and review replies: disclose AI use, keep
   the human as the author, keep prose short. Read `references/ai-policy.md` before drafting any
   text.
6. **Every claim must be checkable.** Cite commit hashes, `file:line`, CI job names and output
   you actually produced. Say "not tested" where that's the case.
7. **Ask before big downloads or long builds.** A shallow clone with submodules is several
   hundred MB, and a build root takes about 3 GB and 25-40 minutes on 8 cores. The user may be
   on a metered connection.

## Where things are

| What | Where |
|---|---|
| Upstream repository | `https://gitlab.haskell.org/ghc/ghc.git` (clone with `--recurse-submodules`) |
| The user's fork | `git@gitlab.haskell.org:<user>/ghc.git`, usually a remote named after the user |
| Base for new work | `origin/master`, after `git fetch origin` |
| Release branches and tags | `origin/ghc-X.Y`; tags `ghc-X.Y.Z-release`, `ghc-X.Y-start`, `ghc-X.Y.Z-alpha1` |
| Commit that introduced a bug | `git log -S'<text>' -- <file>`, `git log -- <file>`, `git blame` |
| MR of a commit | search MR titles with the commit subject: `scripts/ghc-search.sh "<subject>"` |
| Final commit of a merged MR | marge-bot's "Merged in <sha>" comment on the MR |
| LLM policy | <https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing/AI> |
| How to contribute a patch | <https://gitlab.haskell.org/ghc/ghc/-/wikis/Contributing-a-Patch> |
| MR and issue templates | `.gitlab/merge_request_templates/Default.md`, `.gitlab/issue_templates/default.md` |
| All sources of this skill | `references/sources.md` |

## Workflow

### 0. Base and history
- Work on top of `origin/master`. To see whether a release branch is affected, read the file
  there: `git show origin/ghc-X.Y:<file>`. Backports are cherry-picks with different hashes, so
  `git branch --contains` can miss them.
- GitLab's commit-to-MR lookup is empty for commits that marge-bot merged. Find the MR by its
  title instead, or by author plus keyword.

### 1. Check for duplicates (always, and again right before filing)
Pick 2-4 distinctive terms: fragments of the error message, flag, field, file or function names.

    scripts/ghc-search.sh "library-dirs-static" "cannot find -lnuma"

This lists matching issues and MRs, open and closed. Also run
`git log origin/master --grep='<term>'` for fixes that already landed. If anything matches,
stop and show the user: commenting on or reviewing the existing work may be the better move.

### 2. Reproduce and test
Reproduce on current master, then test the fix, each variant in a fresh build root. See
`references/testing.md` for hadrian's caching trap, stage directories, testing outside Nix and
macOS.

### 3. File the issue
Draft it with `references/issue.md`. The user creates it and tells you its number.

### 4. Commit
Rules and an example: `references/commit.md`. Check the message before every push:

    scripts/ghc-lint-commit.py            # HEAD; or: scripts/ghc-lint-commit.py -F message.txt

### 5. Push to the user's fork
Forking needs a verified GitLab account (`references/merge-request.md`). After amending, push
with `git push --force-with-lease <fork-remote> <branch>`, never plain `--force`.

### 6. Open the MR
Use `references/merge-request.md` for the description and the checklist. The target must be
**`ghc/ghc` `master`**; GitLab sometimes defaults to the fork.

### 7. Labels, CI, review, landing
- Only project members can set labels and milestones. Others ask `@triagers` in the text.
- `lint-changelog` fails until there's a `changelog.d/` entry or the ~"no-changelog" label.
- CI status: `scripts/ghc-mr-ci.py <MR number>`. To read failures, see `references/ci.md`.
- The human answers reviewers in their own words. Fixup commits are fine during review; squash
  them before landing. Wait at least 24 h after opening, then @triagers assign marge-bot.

### 8. Backports
Ask for ~"backport needed:X.Y" on the MR and for the issue's milestone to be set to the next
minor release. After the merge, cherry-pick to `ghc-X.Y`; see `references/merge-request.md`.

## Quick reference

| Item | Rule |
|---|---|
| Commit subject | `<area>: <what it does>`, at most 50 characters (lint warns above 50, errors above 80) |
| Commit body | lines at most 72 characters; short; regressing commit hash; `Fixes #N.` |
| AI trailer | `Assisted-by: <tool> (<model>)`, e.g. `Assisted-by: Claude Code (Claude Opus 5.5)` |
| Issue or MR description | starts with the LLM-assistance disclosure (`references/ai-policy.md`) |
| MR title | the commit subject plus ` (#N)` |
| No changelog entry | needs ~"no-changelog" |
| Backport | ~"backport needed:X.Y" on the MR, milestone on the issue |
| marge-bot | after approval, at least 24 h after opening |

## Files (read only what the current step needs)

- `references/ai-policy.md`: GHC's LLM policy, disclosure line and trailer
- `references/issue.md`: issue template and content checklist
- `references/commit.md`: commit message rules, linter limits, example
- `references/merge-request.md`: MR description and checklist, changelog, review, backports
- `references/ci.md`: fork pipelines, failures that aren't the patch's fault, CI coverage
- `references/testing.md`: hadrian layout and pitfalls, Nix and macOS environments
- `references/gitlab-api.md`: GitLab API recipes that need no token
- `references/example-27926.md`: a complete worked example
- `references/sources.md`: where each rule comes from (start here when updating the skill)
- `scripts/ghc-search.sh`: duplicate check for issues and MRs
- `scripts/ghc-lint-commit.py`: commit message check
- `scripts/ghc-mr-ci.py`: MR state, pipelines, failed jobs, short job logs
