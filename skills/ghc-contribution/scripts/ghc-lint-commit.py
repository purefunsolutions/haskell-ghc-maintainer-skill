#!/usr/bin/env python3
"""Check a commit message against GHC's commit message rules and this skill's rules.

Usage: ghc-lint-commit.py [REV]       check a commit in the current repository (default HEAD)
       ghc-lint-commit.py -F FILE     check a message file

The limits mirror linters/lint-commit-msg/Main.hs in the GHC tree: the subject warns above 50
characters and fails above 80 or below 8; body lines warn above 72 and fail above 100. On top of
that: no placeholder issue numbers, a #N issue reference, and an Assisted-by trailer for AI help.
Exit status: 0 if there are no errors, 1 if there are, 2 on usage errors.
"""
import re
import subprocess
import sys

AI_TOOLS = r"(claude|codex|copilot|gpt|gemini|cursor|openai|anthropic|llm|opencode)"


def read_message(argv):
    if argv[:1] == ["-F"]:
        if len(argv) != 2:
            sys.exit(__doc__)
        with open(argv[1], encoding="utf-8") as f:
            return f.read()
    if len(argv) > 1 or argv[:1] in (["-h"], ["--help"]):
        print(__doc__)
        sys.exit(0 if argv[:1] in (["-h"], ["--help"]) else 2)
    rev = argv[0] if argv else "HEAD"
    return subprocess.run(["git", "log", "-1", "--format=%B", rev],
                          check=True, capture_output=True, text=True).stdout


def lint(msg):
    found = []
    lines = msg.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    subj = lines[0] if lines else ""

    def add(level, lineno, text):
        found.append((level, lineno, text))

    if not subj.strip():
        add("ERROR", 1, "empty subject line")
    else:
        if subj != subj.lstrip():
            add("ERROR", 1, "subject line starts with whitespace")
        if subj != subj.rstrip():
            add("warning", 1, "subject line ends with whitespace")
        if "\t" in subj:
            add("ERROR", 1, "subject line contains a TAB")
        n = len(subj)
        if n > 80:
            add("ERROR", 1, "subject is %d characters (limit 80, aim for 50)" % n)
        elif n > 50:
            add("warning", 1, "subject is %d characters (aim for 50)" % n)
        elif n < 8:
            add("ERROR", 1, "subject is only %d characters (minimum 8)" % n)

    if len(lines) > 1:
        if lines[1] != "":
            add("ERROR", 2, "second line must be empty")
        elif len(lines) == 2:
            add("warning", 2, "second line exists, but there is no body")
        for no, line in enumerate(lines[2:], start=3):
            if line != line.rstrip():
                add("warning", no, "trailing whitespace")
            if "\t" in line:
                add("warning", no, "contains a TAB")
            if line.startswith("Summary:"):
                add("warning", no, "Phabricator-style 'Summary:' line")
            if len(line) > 100:
                add("ERROR", no, "line is %d characters (limit 100, aim for 72)" % len(line))
            elif len(line) > 72:
                add("warning", no, "line is %d characters (aim for 72)" % len(line))

    text = "\n".join(lines)
    if re.search(r"#N{3,}|![M]{3,}|#X{3,}|#\?\?\?", text):
        add("ERROR", 0, "placeholder issue or MR number left in the message")
    if not re.search(r"(?<![\w/])#\d{3,}", text):
        add("warning", 0, "no issue reference; GHC wants e.g. 'Fixes #12345.'")
    if re.search(r"(?im)^co-authored-by:.*" + AI_TOOLS, text):
        add("warning", 0, "AI tool credited with Co-authored-by; GHC's LLM policy asks for "
                          "'Assisted-by: <tool>' instead")
    if not re.search(r"(?im)^assisted-by:", text):
        add("note", 0, "no 'Assisted-by:' trailer; GHC's LLM policy requires one if an AI "
                       "tool generated any part of the change")
    return found


def main(argv):
    found = lint(read_message(argv))
    for level, lineno, text in found:
        where = "line %d" % lineno if lineno else "message"
        print("%s (%s): %s" % (level, where, text))
    errors = sum(1 for level, _, _ in found if level == "ERROR")
    print("commit message: %s" % ("FAILED, %d error(s)" % errors if errors else "OK"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
