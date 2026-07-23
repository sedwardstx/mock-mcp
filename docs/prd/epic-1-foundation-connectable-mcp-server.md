# Epic 1 Foundation & Connectable MCP Server

**Epic Goal:** Stand up the Python project and a working MCP server that students and instructors can actually connect to, in both deployment modes. By the end of this epic the server starts via a single documented command in either **stdio** (student-local, offline) or **network** (instructor-hosted) mode, exposes a health/identity tool so a connecting agent can confirm the link, and ships with the project scaffolding, test harness, and run docs that every later epic builds on.

## Story 1.1 Project Scaffold & Health Tool (stdio)

As an instructor setting up the teaching server,
I want a Python MCP server project that starts over stdio and exposes a health/identity tool,
so that I have a runnable, connectable foundation and can confirm an agent is talking to the right server.

### Acceptance Criteria

1: A Python project is initialized with dependency management (e.g., pyproject/`uv` or `pip`), the official Python MCP SDK as a dependency, and a documented project structure that separates the MCP surface from the (future) mock data layer.
2: A unit + integration test harness is configured and runnable via a single command, with at least one passing smoke test.
3: The server runs over **stdio** via a single documented command and is discoverable by a standard MCP client.
4: The server exposes a health/identity tool (e.g., `get_server_info` / `ping`) that returns server name, version, and a static status, with a clear MCP schema and description.
5: An integration test connects an MCP client over stdio, invokes the health tool, and asserts the returned identity/status.
6: A brief README section documents how to install dependencies and run the server over stdio.

## Story 1.2 Network Transport Mode (Instructor Hosting)

As an instructor hosting the server for the class,
I want to run the same server over a network transport,
so that many students can connect to a single instructor-hosted endpoint.

### Acceptance Criteria

1: The server supports a **network transport** (streamable HTTP/SSE) exposing the identical tool surface as stdio mode, from the same codebase.
2: The transport mode is selectable at startup (CLI flag and/or config), with host and port configurable.
3: A remote MCP client can connect over the network transport, invoke the health/identity tool, and receive the correct response.
4: The server accepts multiple concurrent client connections and responds correctly to each (validated by a test simulating concurrent clients).
5: An integration test exercises the health tool over the network transport.
6: No external services, credentials, or internet access are required to run the network mode.

## Story 1.3 Configuration & Classroom Run Documentation

As an instructor or student preparing for a lab,
I want clear configuration and a single documented command per mode,
so that I can start the correct server for my scenario in under 10 minutes.

### Acceptance Criteria

1: Configuration (transport mode, host, port, and any core settings) is settable via a documented mechanism (CLI flags and/or a config file) with sensible defaults.
2: The documentation provides one copy-paste command to start **student-local stdio** mode and one to start **instructor-hosted network** mode.
3: The docs describe how a student confirms a successful connection using the health/identity tool.
4: Invalid configuration (e.g., a bad port) produces a clear, actionable error message rather than a stack trace.
5: The run docs are validated by following them from a clean environment to a successful health-tool call in both modes.
