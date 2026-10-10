# Merge requests

Sources: `Contributing-a-Patch` (§1, §2, §3, §5, §6, §8, §9),
`.gitlab/merge_request_templates/Default.md`, wiki `contributing/changelog`, `.gitlab/ci.sh`
(`lint_changelog`), and wiki `contributing` ("Getting a Gitlab account").

## Before

- Forking ghc/ghc needs a verified account. New users open a "get-verified" issue (an issue
  template on ghc/ghc).
- Push the branch to the fork: `git remote add <user> git@gitlab.haskell.org:<user>/ghc.git`,
  then `git push <user> <branch>`.

## Creating the MR

- Source: `<user>/ghc`, the branch. **Target: `ghc/ghc`, `master`.** Check this; the link
  printed after a push can default to the fork.
- Title: the commit subject plus ` (#N)`.
- Don't mark it Draft unless review isn't wanted yet. In that case, say so at the top (P3).
- Keep "Allow commits from members who can merge to the target branch" checked. marge-bot pushes
  its rebase to the fork.

## Description

Start with the disclosure line and `Fixes #N.`, then keep the template's structure:

    ## Changes contained in this patch
    <first line: what reviewers should look at first>
    ### Problem                (short; the issue has the reproducers)
    ### Fix                    (why it's correct, what stays the same)
    ### Alternative considered (only if a reviewer would ask)
    ### Testing                (what ran where, results, fresh build roots)

    ## MR Checklist
    <the template's ten items, word for word>

Fill in the checklist honestly:
- Tick items that are done, and items whose condition doesn't apply; for those, add a short
  italic note such as "_Not applicable._".
- Leave the rest unticked and say why, e.g. "no testcase, because CI can't trigger the bug".
- Keep the template's link definitions at the end (`[notes]: …`, `[adding test]: …`,
  `[changelog]: …`).

End with what you need from maintainers, for example:
`@triagers: could you please add ~"no-changelog" and ~"backport needed:10.0"? I can't set labels myself.`

## Changelog

- User-facing changes need a file in `changelog.d/`. Its fields are cabal-like: `section`,
  `synopsis`, `issues`, `mrs`, and optionally `description`. The sections are listed in
  `changelog.d/config`. `mrs: !N` needs the MR's number, so add the entry after opening the MR.
- Otherwise the MR needs the ~"no-changelog" label. A fix for a regression that no release
  ever shipped can do without an entry.
- The `lint-changelog` job fails without one or the other. A retried job keeps the labels its
  pipeline started with, so after the labels change, start a new pipeline.

## Review and landing

- Reviewers are volunteers. If nothing happens for a few days, comment mentioning @triagers and
  ask for ~"Blocked on Review".
- The human replies to reviews in their own words (P1). Follow-up commits are fine during
  review; squash them into the original commit before landing.
- After approval, and at least 24 h after opening, @triagers assign marge-bot. It rebases,
  batches, runs the full pipeline and merges. It then comments "Merged in <sha>", and the MR
  shows "closed".

## Backports

- Mark the MR ~"backport needed:X.Y", and ask for the issue's milestone to be the next minor
  release.
- After the merge, either the release manager backports it, or you open the backport MR yourself:
  - with the merged MR's Cherry-pick button (target `ghc-X.Y`), or
  - with `git cherry-pick -x` and the `backport-for-ghc-X.Y` template.

  The backport MR gets the ~backport label and the milestone. Once it lands, remove
  ~"backport needed:X.Y" from the original MR.
- Release managers accept small, low-risk fixes more readily than large changes.
