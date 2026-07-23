# Building AI Support Agents with GitHub Copilot in VS Code

*A hands-on 2-day workshop for technical support engineers*

**PARTICIPANT WORKBOOK**

The hands-on lab manual to follow along.

Audience: Technical support engineers · Mixed skill levels

Format: 2 days · ~70% hands-on labs / 30% instruction · ~6.5 hrs/day

*Example company: “Contoso” — Gateway (networking), Vault (auth), Store (database)*

## How to Use This Workbook

This workbook is your lab manual. Keep it open beside VS Code and work through each lab in order. It is written for a room of mixed skill levels, so every lab is designed with two tracks.

#### The two tracks

> **✓ Checkpoint**
> The baseline “done” bar. If you hit the Checkpoint, you have completed the lab successfully. Everyone should reach every Checkpoint before the group moves on — ask your neighbor or a facilitator if you are stuck.

> **→ Stretch**
> Optional extensions for anyone who finishes early. Stretch goals go deeper but are never required to keep up. Skip them without worry — you can always come back.

#### Conventions used throughout

- **Actions to take** are written as concrete steps, e.g. “In the Chat view, switch to Agent mode and type: …”

- **Code assets** appear in shaded, monospaced boxes with the exact file path in a bold caption above. Type or paste them exactly — they match the facilitator’s screen.

- Monospace marks file names, commands, and things you type literally.

- Pair up **mixed-skill**, and ask early. The fastest way to learn agent mode is to watch it work and read the approval prompts.

## Prerequisites Checklist

Confirm each item before Day 1. Check the boxes as you go. If anything is missing, flag a facilitator during Module 0 setup.

☐ VS Code, latest stable, installed.

☐ Extensions: GitHub Copilot and GitHub Copilot Chat, signed in with the org Copilot license.

☐ Org policy: agent mode and MCP enabled (admin confirms ahead of time; setting chat.mcp.enabled).

☐ Node.js 18+ installed (for npx-launched MCP servers).

☐ Python 3.10+ installed (for skill helper scripts).

☐ Git installed, with clone access to the workshop starter repo.

☐ Access to at least one company MCP server endpoint + credentials — OR use the provided mock MCP server.

☐ A laptop where you can install VS Code extensions and run local processes.

## The Customization Stack — One-Page Primer

Everything you build in this workshop is one of five layers. They range from “always on” to “on demand,” and all of them live as files in the repo — so the whole team shares them through source control. This is the core mental model; keep coming back to it.

| **\#** | **Layer**           | **Lives in**                     | **In plain language**                                                               |
|--------|---------------------|----------------------------------|-------------------------------------------------------------------------------------|
| 1      | Custom instructions | .github/copilot-instructions.md  | Always-on team standards, product context, and escalation rules. Instructions only. |
| 2      | Prompt files        | .github/prompts/\*.prompt.md     | Reusable task prompts you run with /name. One saved prompt per recurring job.       |
| 3      | Agent Skills        | .github/skills/\<name\>/SKILL.md | Reusable procedures loaded on demand — a folder Copilot opens when relevant.        |
| 4      | Custom agents       | .github/agents/\<name\>.agent.md | A persona = instructions + a curated tool set (+ optional model, MCP, sub-agents).  |
| 5      | MCP servers         | .vscode/mcp.json                 | Connect Copilot to external/company systems: ticketing, KB, monitoring.             |

#### How the layers map to what we build

- **Build agents and skills** → layers 3 & 4.

- **Connect agents to company MCP servers** → layer 5, surfaced as tools inside an agent.

- **Coordinator agents that pick the right agent** → a layer-4 agent with tools: \['agent'\] + agents: \[...\] + handoffs.

#### Agent mode is the runtime

In **Agent** mode Copilot plans, calls tools, edits files, and loops (plan → act → observe → repeat), pausing for approval on sensitive actions. Contrast with **Ask** (Q&A) and **Edit** (scoped multi-file edits) modes.

## DAY 1

*Foundations: Agent Mode, Instructions, Prompts & Skills*

### Module 0 — Welcome & Setup (30 min)

Welcome, workshop goals, agenda, and ground rules: pair up mixed-skill, and ask early.

#### Setup verification (do this together)

- Open VS Code and confirm Copilot is signed in.

- Open the starter repo.

- Open the **Chat view** and switch to **Agent** mode.

- Confirm the model picker shows models.

> **✓ Checkpoint**
> Everyone is green-checked — signed in, starter repo open, Agent mode active, and models visible in the picker — before the group moves on.

### Module 1 — The Agent Landscape (45 min)

Instruction plus a live demo. Key ideas:

- Agent vs autocomplete vs chat, and the agentic loop.

- **Ask / Edit / Agent** modes — when to use each.

- The customization stack (the five layers) — one diagram.

- Why it matters for support: turn runbooks and tribal knowledge into reusable, shareable agents; consistency; faster onboarding.

**Live demo:** In agent mode, the facilitator investigates a failing scenario in the starter repo end to end — reads logs, forms a hypothesis, proposes a fix — narrating the loop and the approval prompts.

### Lab 1 — First Agent-Mode Task + Team Instructions (60 min)

**Goal:** Get comfortable in agent mode and capture team context so Copilot answers like an Contoso support engineer.

#### Steps

1.  In the Chat view, switch to **Agent** mode. Type: Investigate samples/logs/gateway-500.log and tell me the likely cause. Watch it read the file, reason, and report. Approve any read actions it requests.

2.  Note how it forms a hypothesis. Ask a follow-up: Which exact log line supports that?

3.  Create the file .github/copilot-instructions.md at the repo root with the team context below (products, tone, “cite the evidence,” the PII rule, and escalation).

**.github/copilot-instructions.md**

```markdown
---
applyTo: "**"
---
# Contoso Support Engineering — Copilot Instructions
## About us
- We provide Tier 2/3 support for the Contoso Cloud Platform.
- Products: Contoso Gateway (networking), Contoso Vault (auth), Contoso Store (database).
## How to help
- Prefer concrete, reproducible diagnostic steps over speculation.
- Always cite the log line, metric, or config value that supports a conclusion.
- Never include customer PII in examples, summaries, or write-ups.
## Escalation
- P1 (customer outage) -> page on-call per the runbook, then post in #sev.
- Only Tier 3 may recommend changes to production configuration.
```

4.  Save the file. Re-run a similar question in a **new** chat and notice how the instructions shape the answer — it should now cite evidence and respect the PII and escalation rules automatically.

5.  Commit the file so your team gets it: git add .github/copilot-instructions.md && git commit -m "Add team Copilot instructions"

> **✓ Checkpoint**
> The instructions file is committed, and a fresh agent answer cites a specific log line from gateway-500.log.

> **→ Stretch** — Add a scoped instructions file that only applies to SQL, then open a `.sql` file and a non-SQL file and confirm the guidance only applies to the SQL file.

**.github/instructions/db.instructions.md**

```markdown
---
applyTo: "**/*.sql"
---
# SQL-specific guidance
- Prefer parameterized queries; never inline user input.
- Call out full table scans and missing indexes.
- Flag any statement that writes to production data for human review.
```

### Module 2 — Reusable Prompts (30 min)

- Prompt files: anatomy and frontmatter (agent, model, tools, argument-hint).

- **/name** invocation, and the editor play button.

- Demo of a /triage-ticket prompt.

### Lab 2 — Build Support Prompt Files (60 min)

**Goal:** Codify two recurring support tasks as reusable prompts.

#### Steps

1.  Create the file .github/prompts/summarize-ticket.prompt.md with the content below.

**.github/prompts/summarize-ticket.prompt.md**

```markdown
---
description: 'Summarize a support ticket into problem, impact, and next steps'
agent: 'agent'
argument-hint: 'paste ticket text or reference a ticket file'
---
Summarize the support ticket below into:
1. **Problem** — one sentence.
2. **Customer impact** — severity and who is affected.
3. **What we know** — key facts, log lines, versions.
4. **Recommended next step** — the single best diagnostic action.
Keep it under 150 words. Do not invent details that are not present.
```

2.  Create the file .github/prompts/draft-customer-reply.prompt.md with the content below.

**.github/prompts/draft-customer-reply.prompt.md**

```markdown
---
description: 'Draft a customer-facing reply from an internal diagnosis'
agent: 'agent'
argument-hint: 'the internal diagnosis / notes'
---
Write a concise, empathetic customer reply based on the internal notes below.
- Acknowledge the impact.
- State what we found in plain language (no internal jargon or hostnames).
- Give the next step and a realistic timeframe.
- Do NOT promise a fix time we cannot commit to. Flag anything needing a human decision.
Return the draft only; a human will review before sending.
```

3.  Test each one: in the Chat view type / and confirm both summarize-ticket and draft-customer-reply appear. Run /summarize-ticket and paste a sample ticket; then run /draft-customer-reply on the diagnosis.

> **✓ Checkpoint**
> Both prompts appear under / and each produces useful output on a sample ticket.

> **→ Stretch**
> Add an argument-hint (already present above) and pass an argument, e.g. /summarize-ticket samples/tickets/CONTOSO-4821.md.
> Try setting agent: 'ask' versus agent: 'agent' in the frontmatter and observe the difference in how the prompt runs.

**— LUNCH (60 min) —**

### Module 3 — Agent Skills (45 min)

- What a skill is: a folder Copilot loads when relevant. SKILL.md anatomy.

- **Progressive disclosure**: name + description discovered first; the body loaded on use; resource files loaded only when referenced.

- Frontmatter fields; automatic vs manual (/skill) invocation; context: fork.

- Where skills live; portability as an open cross-tool standard.

- Demo the log-triage skill firing automatically from a natural question.

### Lab 3 — Build a Troubleshooting Skill (75 min) — Day 1 Capstone

**Goal:** Build a real, reusable log-triage skill — a SKILL.md procedure, a helper script, and a lookup table.

#### Steps

1.  Create the folder .github/skills/log-triage/.

2.  Add SKILL.md with the procedure below. The **description** is what makes it auto-trigger — keep it saying WHAT it does and WHEN to use it.

**.github/skills/log-triage/SKILL.md**

```markdown
---
name: log-triage
description: Triage application and gateway logs to find the root-cause error. Use when a user shares a log file, stack trace, or error output and needs the likely cause and next step.
argument-hint: path to a log file or pasted log lines
---
# Log Triage
Follow this procedure to triage logs.
## 1. Classify
Scan for the first ERROR or FATAL line. Note its timestamp, component, and error code.
## 2. Look up the code
Match the error code against [error-codes.md](./error-codes.md). If found, use its
known cause and remediation.
## 3. Correlate
Check for WARN lines from the same component within 60s BEFORE the error — these
often reveal the trigger.
## 4. Extract with the helper (for large logs)
Run the parser to get a ranked summary:
python parse_logs.py <path-to-log>
## 5. Report
Return: the root-cause line, the error code and its meaning, correlated warnings, and
the single recommended next step. Never state a cause you cannot support with a log line.
```

3.  Add the ranked error extractor helper script parse_logs.py in the same folder.

**.github/skills/log-triage/parse_logs.py**

```python
"""Rank the most frequent ERROR/FATAL lines in a log file."""
import re
import sys
from collections import Counter
LEVEL = re.compile(r"\b(ERROR|FATAL)\b")
CODE = re.compile(r"\bCONTOSO-\d{4}\b")
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
print(f" {code}: {n}x | first: {first_seen[code][:120]}")
if __name__ == "__main__":
if len(sys.argv) != 2:
sys.exit("usage: python parse_logs.py <path-to-log>")
main(sys.argv[1])
```

4.  Add the error-code lookup table error-codes.md in the same folder.

**.github/skills/log-triage/error-codes.md**

```markdown
# Contoso error code reference (excerpt)
| Code | Component | Likely cause | First remediation |
|------|-----------|--------------|-------------------|
| CONTOSO-1001 | Gateway | Upstream timeout | Check upstream health + timeout config |
| CONTOSO-1002 | Gateway | TLS handshake failure | Verify cert chain / expiry |
| CONTOSO-2003 | Store | Connection pool exhausted | Check max connections + leaked sessions |
| CONTOSO-2007 | Store | Replication lag > threshold | Inspect replica load; failover if stale |
| CONTOSO-3005 | Vault | Token expired / clock skew | Sync NTP; re-issue token |
```

5.  Test auto-trigger: in Agent mode ask a natural question such as Here's a gateway log with a 500 — what's the root cause? and confirm the skill loads on its own.

6.  Force it manually: run /log-triage samples/logs/gateway-500.log and confirm the helper script runs and returns a ranked summary.

> **✓ Checkpoint**
> The skill triggers automatically from a natural question AND via the /log-triage slash command, and the helper script runs and prints a ranked error list.

> **→ Stretch**
> Add a second resource file, e.g. runbook-links.md, and reference it from SKILL.md — note it only loads when referenced (progressive disclosure).
> Try context: fork in the frontmatter and discuss when running the skill in an isolated context helps.

### Day 1 Wrap (30 min)

Recap the five layers; Q&A; preview Day 2 (MCP + specialist agents + coordinator).

**Homework:** sketch a skill or specialist for YOUR real domain.

## DAY 2

*MCP Servers, Custom Agents & Coordinators*

### Module 4 — Recap & MCP Concepts (30 min)

- 10-minute recap of Day 1.

- **What is MCP (Model Context Protocol)?** Servers expose tools / resources / prompts to Copilot over a standard protocol.

- Company MCP servers: what your org exposes — ticketing, internal KB, monitoring/observability, deployment (facilitators fill in the list).

- .vscode/mcp.json structure; server types (stdio / http / sse); the **trust dialog**; **secrets via inputs**; least-privilege tooling.

### Lab 4 — Connect to a Company MCP Server (75 min)

**Goal:** Wire Copilot to an MCP server and use its tools in agent mode.

#### Steps

1.  Create the file .vscode/mcp.json for the mock contoso-ticketing (stdio) and contoso-kb (http) servers, using the content below.

**.vscode/mcp.json**

```json
{
"inputs": [
{
"type": "promptString",
"id": "contoso-api-token",
"description": "Contoso internal API token",
"password": true
}
],
"servers": {
"contoso-ticketing": {
"type": "stdio",
"command": "npx",
"args": ["-y", "@contoso/mcp-ticketing"]
},
"contoso-kb": {
"type": "http",
"url": "https://mcp.internal.contoso.example/kb",
"headers": {
"Authorization": "Bearer ${input:contoso-api-token}"
}
}
}
}
```

2.  When prompted, accept the **trust dialog**. Then run MCP: List Servers from the Command Palette to confirm both are running and view their tools.

3.  In Agent mode, ask a question that requires a tool call, e.g. Look up ticket CONTOSO-4821 and summarize it. Approve the tool call when prompted.

4.  Open **Configure Tools** and toggle one tool off, then re-ask and observe the effect.

**Security discussion (facilitator-led, ~10 min):** trust model, least privilege, never commit secrets, and approval prompts for write actions.

> **✓ Checkpoint**
> At least one MCP tool call succeeds inside agent mode (e.g., a ticket lookup returns data).

> **→ Stretch**
> Point contoso-kb at the real internal server using an inputs token (as shown in the config), and curate the tool set down to least privilege.

### Module 5 — Custom Agents (45 min)

- Custom agent anatomy: .agent.md, frontmatter (description, tools, model, mcp-servers), persona body.

- How agents differ from skills/instructions: an agent is a whole persona + curated tools; a skill is a procedure; instructions are standards.

- Selecting an agent from the agents dropdown; user-invocable.

- Note the old name (“custom chat modes”; files were .chatmode.md) so people reading older blogs aren’t confused. Demo a db-diagnostics agent.

### Lab 5 — Build a Specialist Troubleshooting Agent (75 min)

**Goal:** Build a focused specialist that combines a persona + curated tools + a skill + MCP tools.

#### Steps

1.  Create the file .github/agents/db-diagnostics.agent.md with the content below: a tight persona, restricted tools, a reference to the log-triage skill in its body, and the ticketing/KB MCP tools.

**.github/agents/db-diagnostics.agent.md**

```markdown
---
description: Specialist for Contoso Store (database) issues — connection errors, slow queries, replication lag.
tools: ['codebase', 'contoso-ticketing', 'contoso-kb']
model: Claude Sonnet
---
You are a Tier 3 database support specialist for Contoso Store.
When given a problem:
1. If logs are provided, use the log-triage skill first.
2. Check the ticket and the KB via the Contoso MCP tools for known issues.
3. Stay in your lane — connections, queries, indexes, replication. If the issue is
clearly network or auth, say so and name the specialist who should take it.
Ground every conclusion in a specific log line, metric, or query plan.
Never recommend a production change without a rollback step.
```

> ℹ Note
> The tool names in tools: must match exactly what appears in the Configure Tools picker for your workspace — the list above is representative. network-diagnostics and auth-diagnostics are the same template with the domain swapped (Gateway / Vault).

2.  Test it: open the **agents dropdown**, select db-diagnostics, and throw a database symptom at it. Confirm it uses the log-triage skill and stays in its lane.

3.  **Group assignment:** each group builds a different specialist — db-diagnostics, network-diagnostics, or auth-diagnostics — so Lab 6 has real sub-agents to route to.

> **✓ Checkpoint**
> The specialist appears in the agents dropdown and stays in its lane — it defers issues outside its domain and names the right specialist.

> **→ Stretch**
> Pin a model; tighten tools to least privilege; and add a KB-only “read-only” variant of the specialist.

**— LUNCH (60 min) —**

### Module 6 — Coordinator Agents (45 min) — Marquee Topic

- The routing problem: one general “front door” that dispatches to the right specialist.

- agents: property + the agent tool = sub-agent invocation. handoffs: = guided transitions.

- **Patterns:** coordinator-as-router (classify → delegate), sequential handoff chains, fork for isolation, and a fallback path. Plus when NOT to delegate (simple issues).

- Demo a support-triage coordinator routing a mixed problem to two specialists and synthesizing.

### Lab 6 — Build the Coordinator (90 min) — Workshop Capstone

**Goal:** Build a general troubleshooting coordinator that routes to the specialists from Lab 5.

#### Steps

1.  Create the file .github/agents/support-triage.agent.md with the content below: tools: \['agent'\], the three specialists in agents:, a persona that asks 1–2 clarifying questions, classifies, delegates, and synthesizes, plus a handoffs entry to a ticket-writer agent.

**.github/agents/support-triage.agent.md**

```markdown
---
description: General support triage front door. Classifies an incoming issue and routes it to the right specialist agent.
tools: ['agent']
agents: ['db-diagnostics', 'network-diagnostics', 'auth-diagnostics']
handoffs:
- label: 'Draft the resolution'
agent: ticket-writer
prompt: 'Write up the resolution for the issue we just diagnosed.'
---
You are the front-line support triage coordinator.
Your job is NOT to fix the problem yourself. It is to:
1. Ask 1–2 clarifying questions if the symptom is ambiguous.
2. Classify the issue: database (Store), network (Gateway), or auth (Vault).
3. Delegate to the matching specialist using the agent tool.
4. If it spans domains, coordinate specialists in sequence and synthesize their findings.
5. If nothing matches, ask for more detail rather than guessing.
After a diagnosis is confirmed, offer the "Draft the resolution" handoff.
Never send customer-facing text without human review.
```

2.  Select support-triage from the agents dropdown. Throw an **ambiguous** problem at it, e.g. Customers intermittently can't log in and some queries time out. Watch it ask a clarifying question, classify, and route.

3.  Now throw a **cross-domain** problem and confirm it coordinates specialists in sequence and synthesizes their findings.

4.  After a diagnosis, accept the **Draft the resolution** handoff and confirm it hands off to the ticket-writer flow (human-review gate).

> **✓ Checkpoint**
> The coordinator correctly routes at least two different problem types and offers the “Draft the resolution” handoff.

> **→ Stretch**
> Add a fallback: if nothing matches, ask for more info rather than guessing.
> Build the ticket-writer handoff target that drafts a resolution behind a human-review gate.

### Module 7 — Ship It: Governance, Sharing & Best Practices (30 min)

- Share via the repo: commit .github/agents, /skills, /prompts, and .vscode/mcp.json so the whole team gets them; org-level custom agents auto-discovery.

- Versioning & review of agents like code; testing/maintaining; prompt hygiene.

- **Security:** MCP trust + least privilege, secrets via inputs, approval gates, and human-in-the-loop for anything customer-facing or production-changing. Avoid over-automation.

### Capstone share-out & close (45 min)

- Groups demo their coordinator + specialists (5 min each).

- Retro (keep/change), resources, next steps, completion checklist.

## Appendix A — Quick Reference

#### File locations — where each of the 5 layers lives

| Layer | File location | Invocation |
| --- | --- | --- |
| 1. Custom instructions | .github/copilot-instructions.md (or *.instructions.md ) | Always on (or by applyTo glob) |
| 2. Prompt files | .github/prompts/*.prompt.md | /name or play button |
| 3. Agent Skills | .github/skills/<name>/SKILL.md | Auto by description, or /skillname |
| 4. Custom agents | .github/agents/<name>.agent.md | Agents dropdown / delegated |
| 5. MCP servers | .vscode/mcp.json | Tools inside agent mode |

#### Frontmatter cheat-sheets

**Prompt files (\*.prompt.md)**

| **Field**     | **Purpose**                                      |
|---------------|--------------------------------------------------|
| description   | What the prompt does (shown in the / list).      |
| agent         | Which mode/agent runs it, e.g. 'agent' or 'ask'. |
| model         | Optional model override.                         |
| tools         | Optional curated tool set for the run.           |
| argument-hint | Hint text for the argument you pass after /name. |

#### Agent Skills (SKILL.md)

| Field | Purpose |
| --- | --- |
| name (required) | The skill's identifier; used by /skillname. |
| description (required) | WHAT it does and WHEN to use it — drives auto-trigger. |
| argument-hint | Hint for the argument, e.g. a log file path. |
| user-invocable | Whether it can be run manually via slash command. |
| disable-model-invocation | Prevent automatic (model-driven) triggering. |
| context: inline\|fork | Run inline, or fork an isolated context. |

**Custom agents (\*.agent.md)**

| **Field**      | **Purpose**                                            |
|----------------|--------------------------------------------------------|
| description    | What the agent is for (shown in the dropdown).         |
| name           | The agent's identifier.                                |
| tools          | Curated tool set the agent may use (least privilege).  |
| model          | Optional pinned model.                                 |
| agents         | Named sub-agents this agent may invoke (coordinators). |
| handoffs       | Guided next-step transitions to other agents.          |
| user-invocable | Whether it appears in the agents dropdown.             |
| mcp-servers    | MCP servers whose tools the agent may use.             |
| target         | Where the agent runs / its scope.                      |

## Appendix B — Troubleshooting (Common Gotchas)

If something is not working, scan this table first.

| **Symptom**                  | **Likely cause & fix**                                                                                                   |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| “Agent mode missing”         | Extension outdated, or org policy disabled. Update; check admin policy.                                                  |
| “No models in picker”        | Not signed in / license not seated. Re-auth.                                                                             |
| MCP server won't start       | Node/Python missing, wrong command/args, or the trust dialog not accepted. Use MCP: List Servers → Show Output for logs. |
| Skill not triggering         | Weak description; make it say WHAT it does and WHEN to use it. Test with /skillname to confirm it loads at all.          |
| Custom agent not in dropdown | user-invocable: false, wrong folder, or filename not \*.agent.md.                                                        |
| Coordinator won't delegate   | Missing tools: \['agent'\], or the named sub-agents don't exist / aren't spelled exactly.                                |
| Secrets in mcp.json          | Never hardcode; use inputs + \${input:id}.                                                                               |
