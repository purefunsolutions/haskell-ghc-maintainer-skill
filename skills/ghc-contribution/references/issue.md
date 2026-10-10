# Filing a GHC issue

Sources: wiki `working-conventions/fixing-bugs` (step 1: "Make sure the bug has a GitLab
issue"), `Contributing-a-Patch` §2.1 ("Every MR should have a ticket"), wiki `report-a-bug`, and
`.gitlab/issue_templates/default.md`.

## Before writing

1. Run `scripts/ghc-search.sh` with several terms, closed issues included. For a regression, also
   look at the release tracking ticket ("Tracking ticket for GHC X.Y.Z").
2. Reproduce on current master. Note which release branches are affected
   (`git show origin/ghc-X.Y:<file>`, `git merge-base --is-ancestor <sha> <tag>`).

## Template (keep these headings)

    <disclosure line from ai-policy.md>

    ## Summary
    What goes wrong, in which configuration, and the cause if known (commit hashes, MRs).

    ## Steps to reproduce
    Exact commands and the actual output, shortened (e.g. /nix/store/…-foo).

    ## Expected behavior
    One or two sentences.

    ## Environment
    * GHC version used: master (<short sha>); other affected branches
    * Operating System:
    * System Architecture:

    /label ~"T::bug"
    /label ~"needs triage"

Optional lines at the end: "I'll open an MR with a fix", a backport request ("Could a triager
milestone this for X.Y.Z?"), `Related: #…, !…`, `cc @<author of the regressing commit>`.

## Notes

- Non-members see "Only project members can add metadata". The `/label` lines are then ignored,
  but triagers label new issues anyway. Ask for a milestone in the text.
- Write the issue paste-ready in a file: one line per paragraph, fenced code blocks, no smart
  quotes. On macOS, `pbcopy < file` puts it on the clipboard. Tell the user whom a `cc` line will
  notify.
- After the user creates the issue, confirm it with
  `curl -sS https://gitlab.haskell.org/api/v4/projects/1/issues/<N>`. Then use `#N` in the commit
  and in the MR title.
