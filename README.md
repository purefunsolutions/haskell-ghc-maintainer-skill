# GHC maintainer skill

An [Agent Skill](https://agentskills.io/specification) that teaches coding agents how to
contribute a change upstream to [GHC](https://gitlab.haskell.org/ghc/ghc), following GHC's
own rules:
- check that no issue or merge request already covers the problem;
- file the issue first, then put its number in the commit message and the MR title;
- make the smallest correct change, without filler comments;
- follow GHC's [LLM policy](https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing/AI): disclose
  AI use, and keep the human as the author;
- fill in the MR template and its checklist honestly;
- read CI failures, and ask for labels and backports.

It came out of fixing [#27926](https://gitlab.haskell.org/ghc/ghc/-/issues/27926)
([!16791](https://gitlab.haskell.org/ghc/ghc/-/merge_requests/16791)).

## How agents load it

At startup, an agent sees only the skill's name and its one-paragraph description (about 100
tokens). It reads `SKILL.md` (about 140 lines) only when a task is about GHC upstream work, not
for ordinary Haskell programming. It reads the files in `references/` only for the step it's on.
The scripts do the repetitive work, so even simple agents follow it reliably:

| Script | Does |
|---|---|
| `scripts/ghc-search.sh` | duplicate check over issues and MRs, open and closed |
| `scripts/ghc-lint-commit.py` | GHC's commit-message limits, plus placeholder, issue-reference and AI-trailer checks |
| `scripts/ghc-mr-ci.py` | an MR's labels and pipelines, failed jobs first, short log tails |

They need `bash`, `git`, `curl` and `python3`; the Nix package brings its own. No token is
needed.

## Recommended: glab

If you can log in, [glab](https://gitlab.com/gitlab-org/cli), the GitLab CLI, does all of this
better. Logged in, it reads what the anonymous API refuses:
- issue and MR discussions (`glab mr view N --comments --unresolved`);
- labels and milestones (`glab api`);
- job logs (`glab ci trace`).

It also handles paging and JSON output for you. The skill tells agents to use it whenever
`glab auth status --hostname gitlab.haskell.org` shows a login, and to fall back to the scripts
otherwise. The scripts stay useful in two cases: they need no setup at all, and `ghc-mr-ci.py`
finds a fork MR's pipeline from the MR number alone.

Set it up once:

1. Create a [personal access token](https://gitlab.haskell.org/-/user_settings/personal_access_tokens)
   with an expiry date.
   - `read_api` is all the skill needs. With it, an agent can search and read everything, but it
     can't post, comment or change anything. Choose this if you'd rather not hand an agent write
     access; it also matches the skill's rule that you publish.
   - Add `api` only if you want glab itself to create issues or MRs, comment, or retry jobs.
2. Log in without putting the token in your shell history, and keep it in the OS keyring:

       glab auth login --hostname gitlab.haskell.org --git-protocol ssh --use-keyring --stdin < token.txt

   With `--git-protocol ssh`, git keeps using your SSH key, so a `read_api` token doesn't affect
   pushing.
3. Point glab at the right host. Outside a checkout of a gitlab.haskell.org repository,
   `-R ghc/ghc` otherwise goes to gitlab.com:

       export GITLAB_HOST=gitlab.haskell.org

`glab skills install --global` adds glab's own generic agent skill (to `~/.agents/skills/glab`),
which complements this one. The skill's recipes are in
`skills/ghc-contribution/references/glab.md`.

## Install

The skill is a plain directory, `skills/ghc-contribution/`, that gets linked into each agent's
global skills directory:

| Agent | Directory |
|---|---|
| Claude Code | `~/.claude/skills/` (or `$CLAUDE_CONFIG_DIR/skills/`) |
| Codex, Pi, Cline, Zed, Warp and others | `~/.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/` |

Codex also reads `~/.codex/skills/` (`$CODEX_HOME/skills/`), but its
[source](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/ext/skills/src/host_roots.rs#L96-L107)
marks that location deprecated, even though Codex's bundled skill-installer still uses it.

Other agents that support Agent Skills (Gemini CLI, GitHub Copilot, Cursor, Goose and more) have
their own directories; see the table in [vercel-labs/skills](https://github.com/vercel-labs/skills).
Linking the same directory there works too.

**With Nix:**

    nix run github:purefunsolutions/haskell-ghc-maintainer-skill#install            # all three
    nix run github:purefunsolutions/haskell-ghc-maintainer-skill#install -- claude  # or a subset

This creates a GC root at `~/.local/state/ghc-contribution-skill` and links the agents'
directories to it, so garbage collection can't remove the skill.

**With Home Manager:**

```nix
{
  inputs.ghc-skill.url = "github:purefunsolutions/haskell-ghc-maintainer-skill";
  # inputs.ghc-skill.inputs.nixpkgs.follows = "nixpkgs";
  # then, in your Home Manager configuration:
  imports = [ inputs.ghc-skill.homeManagerModules.default ];
  programs.ghc-contribution-skill.enable = true;   # agents = [ "claude" "agents" "opencode" ];
}
```

**Without Nix** (symlinks to this checkout, so `git pull` updates the skill):

    git clone https://github.com/purefunsolutions/haskell-ghc-maintainer-skill
    cd haskell-ghc-maintainer-skill && ./install.sh          # or: ./install.sh claude agents
    ./install.sh --uninstall                                  # removes the links again

## Layout

    skills/ghc-contribution/
      SKILL.md              workflow, ground rules, where things are, quick reference
      references/           one focused file per step, read on demand
        ai-policy.md  issue.md  commit.md  merge-request.md  ci.md  glab.md
        testing.md  gitlab-api.md  example-27926.md  sources.md
      scripts/              ghc-search.sh  ghc-lint-commit.py  ghc-mr-ci.py
    flake.nix, nix/         package, install app, checks, Home Manager module
    install.sh              installer without Nix

## Keeping it current

Every rule cites its source, and `skills/ghc-contribution/references/sources.md` lists them all:
the GHC wiki pages (fetch them as raw markdown by adding `.md` to the URL) and the files in the
GHC tree. To update:
1. Re-read the sources.
2. Adjust the reference files.
3. Bump `metadata.last-verified` in `SKILL.md`.
4. Run the checks:

       nix flake check                                     # or, without Nix:
       python3 nix/check-skill.py skills/ghc-contribution
