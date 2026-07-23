# Next Steps

With the architecture approved:

1. **Product Owner review** — validate PRD + architecture alignment; then **shard** both documents (`docs/prd/`, `docs/architecture/`) for story-by-story development.
2. **Extract dev-load files** — per `core-config.yaml`, create `docs/architecture/coding-standards.md`, `docs/architecture/tech-stack.md`, and `docs/architecture/source-tree.md` (these are always loaded by the dev agent). Sharding produces these.
3. **Begin implementation** — SM drafts Story 1.1; Dev agent implements against this architecture.
4. **Confirmed decisions:** package/run manager is **`uv`**; instructor-hosted HTTP runs as an **open endpoint on a trusted classroom LAN** (no auth/TLS in MVP).
5. **Remaining item for init:** verify the exact MCP SDK version + streamable-HTTP transport API during a Story 1.2 spike, then pin in `uv.lock`.
