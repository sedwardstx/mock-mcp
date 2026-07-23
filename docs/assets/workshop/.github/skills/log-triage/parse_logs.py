"""Rank the most frequent ERROR/FATAL lines in an Azure log file by AZURE-#### code."""

import re
import sys
from collections import Counter

LEVEL = re.compile(r"\b(ERROR|FATAL)\b")
CODE = re.compile(r"\bAZURE-\d{4}\b")


def main(path: str) -> None:
    counts: Counter = Counter()
    first_seen: dict[str, str] = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if LEVEL.search(line):
                match = CODE.search(line)
                key = match.group(0) if match else "UNCODED"
                counts[key] += 1
                first_seen.setdefault(key, line.strip())
    if not counts:
        print("No ERROR/FATAL lines found.")
        return
    print("Ranked errors (most frequent first):")
    for code, n in counts.most_common():
        print(f"  {code}: {n}x | first: {first_seen[code][:120]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python parse_logs.py <path-to-log>")
    main(sys.argv[1])
