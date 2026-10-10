"""Validate a skill directory against the Agent Skills specification.

Checks the frontmatter of SKILL.md (https://agentskills.io/specification), the length of
SKILL.md, and that every references/ and scripts/ path mentioned in the skill exists.
Usage: python3 check-skill.py SKILL_DIR
"""
import os
import re
import sys


def frontmatter(text):
    if not text.startswith("---\n"):
        sys.exit("SKILL.md must start with '---' frontmatter")
    body = text[4:].split("\n---\n", 1)[0]
    top, nested, current = {}, {}, None
    for line in body.split("\n"):
        if not line.strip():
            continue
        if line.startswith("  "):
            if current is None:
                sys.exit("indented line outside a mapping: %r" % line)
            k, _, v = line.strip().partition(":")
            nested.setdefault(current, {})[k] = v.strip()
            continue
        k, _, v = line.partition(":")
        top[k] = v.strip()
        current = k if not v.strip() else None
    for k, v in list(top.items()):
        if len(v) >= 2 and v[0] == v[-1] == '"':
            top[k] = v[1:-1]
    return top, nested


def main(skill_dir):
    errors = []
    # In the Nix store the directory is called <hash>-<name>.
    name_of_dir = re.sub(r"^[0-9a-z]{32}-", "", os.path.basename(os.path.normpath(skill_dir)))
    text = open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8").read()
    top, nested = frontmatter(text)
    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    for k in top:
        if k not in allowed:
            errors.append("unknown frontmatter field %r" % k)
    name = top.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append("invalid name %r" % name)
    if name != name_of_dir:
        errors.append("name %r doesn't match directory %r" % (name, name_of_dir))
    desc = top.get("description", "")
    if not 1 <= len(desc) <= 1024:
        errors.append("description must be 1-1024 characters, is %d" % len(desc))
    if len(top.get("compatibility", "")) > 500:
        errors.append("compatibility must be at most 500 characters")
    for k, v in nested.get("metadata", {}).items():
        if not (len(v) >= 2 and v[0] == v[-1] == '"'):
            errors.append("metadata value for %r should be a quoted string" % k)
    lines = text.count("\n")
    if lines >= 500:
        errors.append("SKILL.md has %d lines; keep it under 500" % lines)
    for root, _, files in os.walk(skill_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            content = open(os.path.join(root, f), encoding="utf-8").read()
            for ref in sorted(set(re.findall(r"(?<![\w/.])((?:references|scripts)/[\w.-]+)", content))):
                if not os.path.exists(os.path.join(skill_dir, ref)):
                    errors.append("%s mentions %s, which doesn't exist" % (f, ref))
    for e in errors:
        print("ERROR: " + e)
    print("skill %s: %s (%d lines in SKILL.md, description %d characters)"
          % (name, "FAILED" if errors else "OK", lines, len(desc)))
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
