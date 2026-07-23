"""Guard test (1.1-UNIT-003): no stdout writes in src/.

A stray print() corrupts the MCP stdio transport framing. All human-readable
output must go to stderr via logging. [architecture/coding-standards.md]
"""

from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"


def test_no_print_calls_in_src():
    offenders = []
    for path in SRC.rglob("*.py"):
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if "print(" in line:
                offenders.append(f"{path.relative_to(SRC.parent)}:{lineno}")
    assert not offenders, f"stdout writes found in src/ (use logging to stderr): {offenders}"
