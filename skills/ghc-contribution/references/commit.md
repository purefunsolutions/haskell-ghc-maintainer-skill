# Commits

Sources: `Contributing-a-Patch` §2.4 and §2.6, wiki `working-conventions/fixing-bugs`,
`linters/lint-commit-msg/Main.hs` in the GHC tree.

## Shape

- One logical change per commit; an MR usually has one commit. Every commit must build. Squash
  fixups before landing.
- Subject: `<area>: <what it does>`, e.g. `rts:`, `hadrian:`, `configure:`, `testsuite:`,
  `docs:`, or a compiler area. Aim for at most 50 characters.
- Body: describe the change, not the implementation as it is now; that belongs in a Note in the
  code. Name the regressing commit by its short hash. End with `Fixes #N.`; GitLab closes the
  issue when the commit reaches master.
- For a small fix, two to five body lines are enough. The issue has the details.
- Trailers come last: `Assisted-by: …` if an AI tool helped, then the human's optional
  `Signed-off-by`.

## lint-commit-msg limits

The CI doesn't run this linter at the moment, but its limits are the convention.

| Check | Warning | Error |
|---|---|---|
| Subject length | over 50 | over 80, or under 8 |
| Subject | trailing whitespace | empty, leading whitespace, TAB |
| Line 2 | | not empty |
| Body line length | over 72 | over 100 |
| Body | trailing whitespace, TAB, `Summary:` | |

`scripts/ghc-lint-commit.py` checks HEAD, or a file with `-F file`. It also flags placeholder
numbers (`#NNNNN`), a missing issue reference, and AI tools credited with `Co-authored-by`.

## Code changes

- Make the smallest change that fixes the problem. Don't add explanatory multi-line comments to
  trivial edits, and don't reformat or rename nearby code. If something needs a long
  explanation, that's usually a Note (coding style §2) and a bigger change, so ask the user
  first.
- Follow the style of the surrounding file. The guides are wiki `commentary/coding-style` for
  the compiler and `commentary/rts/conventions` for the RTS.

## Example (the commit of MR !16791, fixing #27926)

    rts: don't restrict static lib dirs to libffi's

    With --with-ffi-libraries, extra-lib-dirs-static in rts.buildinfo
    stops Cabal from falling back to extra-lib-dirs, so the RTS's
    library-dirs-static lacks the libnuma, libdw and libzstd dirs and
    linking fails. Drop it. Fixes #27926.

    Assisted-by: Claude Code (Claude Opus 5.5)

## Mechanics

- Commit under the user's git identity. If the user signs their commits, don't sign for them:
  commit with `--no-gpg-sign` and let them run `git commit --amend -S --no-edit`.
- marge-bot rebases before merging, so GPG signatures don't survive into master.
- After an amend, push with `git push --force-with-lease <fork-remote> <branch>`. Never use plain
  `--force`, and don't push until the user says so.
- If the issue doesn't exist yet, write `#NNNNN` as a placeholder. The lint script won't let it
  through.
