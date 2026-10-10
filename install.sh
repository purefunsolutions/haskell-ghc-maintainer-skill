#!/usr/bin/env bash
# Link the ghc-contribution skill into the global skills directories of coding agents.
# Usage: install.sh [--source DIR] [--uninstall] [claude] [agents] [opencode]  (default: all three)
#   claude    ${CLAUDE_CONFIG_DIR:-~/.claude}/skills         Claude Code
#   agents    ~/.agents/skills                               Codex, Pi, Cline, Zed, Warp and others
#   opencode  ${XDG_CONFIG_HOME:-~/.config}/opencode/skills  OpenCode
# By default it links this checkout's skills/ghc-contribution, so `git pull` updates it.
set -euo pipefail

name=ghc-contribution
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
src="$here/skills/$name"
uninstall=0
targets=()

while [ $# -gt 0 ]; do
  case $1 in
    --source) src=${2:?--source needs a directory}; shift 2 ;;
    --uninstall) uninstall=1; shift ;;
    claude|agents|opencode) targets+=("$1"); shift ;;
    all) targets+=(claude agents opencode); shift ;;
    -h|--help) sed -n '2,7p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "install.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [ ${#targets[@]} -eq 0 ]; then
  targets=(claude agents opencode)
fi
if [ "$uninstall" = 0 ] && [ ! -f "$src/SKILL.md" ]; then
  echo "install.sh: no SKILL.md in $src" >&2
  exit 1
fi

for t in "${targets[@]}"; do
  case $t in
    claude) dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills" ;;
    agents) dir="$HOME/.agents/skills" ;;
    opencode) dir="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills" ;;
  esac
  dest="$dir/$name"
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    echo "skipping $dest: it exists and isn't a symlink" >&2
    continue
  fi
  if [ "$uninstall" = 1 ]; then
    rm -f "$dest"
    echo "removed $dest"
  else
    mkdir -p "$dir"
    ln -sfn "$src" "$dest"
    echo "$dest -> $src"
  fi
done
