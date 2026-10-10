# Sources (last verified 2026-10-10)

To update this skill:
1. Re-read these sources and compare them with the files that cite them.
2. Bump `metadata.last-verified` in `SKILL.md`.

Wiki pages are also available as raw markdown: add `.md` to the URL and fetch it with plain
`curl`.

| Topic | Source |
|---|---|
| LLM policy (P1-P4, R1) | <https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing/AI> |
| MR workflow: tickets, commits, Draft, CI labels, marge-bot, backports | <https://gitlab.haskell.org/ghc/ghc/-/wikis/Contributing-a-Patch> |
| Fixing bugs: issue first, tests, commit message | <https://gitlab.haskell.org/ghc/ghc/-/wikis/working-conventions/fixing-bugs> |
| Contributing overview, account verification, licensing | <https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing> |
| Changelog entries | <https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing/changelog>, `utils/changelog-d/README.md`, `changelog.d/config` |
| Backporting | <https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing/Backporting> |
| Reporting bugs | <https://gitlab.haskell.org/ghc/ghc/-/wikis/report-a-bug> |
| Coding style | <https://gitlab.haskell.org/ghc/ghc/-/wikis/commentary/coding-style>, <https://gitlab.haskell.org/ghc/ghc/-/wikis/commentary/rts/conventions> |
| MR template | `.gitlab/merge_request_templates/Default.md` |
| Issue template | `.gitlab/issue_templates/default.md` |
| Commit message limits | `linters/lint-commit-msg/Main.hs` |
| Changelog check in CI | `.gitlab/ci.sh` (`lint_changelog`), `.gitlab-ci.yml` (`lint-changelog`) |
| CI job matrix | `.gitlab/generate-ci/gen_ci.hs`, `.gitlab/jobs.yaml` |
| Hadrian layout | `hadrian/README.md` |
| Hadrian's package caching | `hadrian/src/Hadrian/Haskell/Cabal/Parse.hs` (`resolveContextData`) |
| macOS build preparation | <https://gitlab.haskell.org/ghc/ghc/-/wikis/building/preparation/mac-osx> |
| GitLab REST API | <https://docs.gitlab.com/api/> |
| Agent Skills format | <https://agentskills.io/specification> |
| Skill directories per agent | <https://github.com/vercel-labs/skills> (README table) |

Observed rather than documented (recheck if something behaves differently):
- Anubis on gitlab.haskell.org lets plain `curl` through.
- Non-members can't set labels or milestones ("Only project members can add metadata").
- The commit-to-MR API is empty for commits that marge-bot merged.
- Pipelines for MRs from forks run in the fork project.
- Fetch failures (`fatal: early EOF`) happen on fork pipelines.
