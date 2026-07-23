# Infrastructure and Deployment

## Infrastructure as Code

- **Tool:** None. There is no cloud infrastructure. "Deployment" is running a Python process on a laptop.
- **Location:** N/A
- **Approach:** Distribute the repo; install deps with `uv sync`; run via the documented command.

## Deployment Strategy

- **Strategy:** Local execution. Two run modes from one entry point:
  - Student (offline): `uv run contoso-support-mcp --transport stdio`
  - Instructor (network): `uv run contoso-support-mcp --transport http --host 0.0.0.0 --port 8000`
- **CI/CD Platform:** GitHub Actions (lint + test on push) — optional but recommended; the repo has a `.github/` directory.
- **Pipeline Configuration:** `.github/workflows/ci.yml`

## Environments

- **Local (student):** stdio transport, offline, single user.
- **Local (instructor):** streamable HTTP on the classroom LAN, many concurrent students.

## Environment Promotion Flow

```text
dev laptop  ->  git push  ->  CI (lint + unit/integration/e2e/consistency)  ->  tagged release (repo bundle)
```

## Rollback Strategy

- **Primary Method:** Git revert / checkout a previous tag; re-run. Data and code are versioned together.
- **Trigger Conditions:** A scenario/consistency test failure or a broken run.
- **Recovery Time Objective:** Minutes (local restart).
