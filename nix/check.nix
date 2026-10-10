{
  runCommand,
  runtimeShell,
  python3,
  src,
  skill,
}:

runCommand "ghc-contribution-skill-check" { nativeBuildInputs = [ python3 ]; } ''
  python3 -I ${./check-skill.py} ${src}
  ${runtimeShell} -n ${src}/scripts/ghc-search.sh
  for f in ${src}/scripts/*.py; do
    python3 -I -c 'import ast, sys; ast.parse(open(sys.argv[1]).read(), sys.argv[1])' "$f"
  done
  # The example commit message in references/commit.md must pass the skill's own linter.
  python3 -I - ${src}/references/commit.md > example.txt <<'EOF'
  import re, sys
  text = open(sys.argv[1]).read()
  block = text.split("## Example", 1)[1].split("\n\n", 1)[1].split("\n## ", 1)[0]
  print("\n".join(l[4:] for l in block.rstrip().split("\n")))
  EOF
  ${skill}/scripts/ghc-lint-commit.py -F example.txt
  touch $out
''
