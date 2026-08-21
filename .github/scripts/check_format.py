#!/usr/bin/env python3
"""Enforce README.md formatting rules: alphabetical tool order, valid pricing tags,
description length. See CONTRIBUTING.md for the rules this checks."""
import re
import sys

NON_CATEGORY_HEADINGS = {
    "table of contents",
    "how tools get listed",
    "quick comparison",
    "faq",
    "sponsors",
    "contributing",
    "more directories",
}

ENTRY_RE = re.compile(
    r"^- \*\*\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\*\* — (?P<desc>.+?) "
    r"`(?P<tag>Free|Freemium|Paid(?: \(enterprise/custom pricing\))?)`$"
)
MAX_DESC_LEN = 160
SUPERLATIVES = {"best", "revolutionary", "leading", "top", "unrivaled", "unmatched", "#1"}


def heading_text(line):
    return re.sub(r"^#+\s*", "", line).strip()


def strip_emoji_prefix(text):
    return re.sub(r"^[^\w]+", "", text).strip().lower()


def main():
    with open("README.md", encoding="utf-8") as f:
        lines = f.readlines()

    errors = []
    current_category = None
    current_names = []

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        if line.startswith("## "):
            current_category = heading_text(line)
            current_names = []
            continue

        if not line.startswith("- "):
            continue

        if current_category is None or strip_emoji_prefix(current_category) in NON_CATEGORY_HEADINGS:
            continue

        match = ENTRY_RE.match(line)
        if not match:
            errors.append(f"README.md:{lineno}: entry doesn't match required format: {line}")
            continue

        name = match.group("name")
        desc = match.group("desc")

        sort_key = name.lower()
        if current_names and sort_key < current_names[-1]:
            errors.append(
                f"README.md:{lineno}: '{name}' is out of alphabetical order in "
                f"'{current_category}' (comes after '{current_names[-1]}')"
            )
        current_names.append(sort_key)

        if len(desc) > MAX_DESC_LEN:
            errors.append(
                f"README.md:{lineno}: description for '{name}' is {len(desc)} chars, "
                f"max is {MAX_DESC_LEN}"
            )

        lowered = desc.lower()
        for word in SUPERLATIVES:
            if re.search(rf"\b{re.escape(word)}\b", lowered):
                errors.append(
                    f"README.md:{lineno}: description for '{name}' contains "
                    f"superlative '{word}' — keep it factual"
                )

    if errors:
        print(f"Found {len(errors)} formatting issue(s):\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("README.md format check passed.")


if __name__ == "__main__":
    main()
