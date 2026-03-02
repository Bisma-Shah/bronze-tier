# Bronze Tier - Personal AI Employee Project

## Project Overview

This repository is the **Bronze Tier** implementation of a "Personal AI Employee" (Digital FTE - Full-Time Equivalent) hackathon project. The goal is to build an autonomous AI agent that manages personal and business affairs 24/7 using:

- **Claude Code** as the reasoning engine
- **Obsidian** (Markdown) as the knowledge base and dashboard
- **Python Watcher Scripts** for monitoring inputs (Gmail, WhatsApp, filesystems)
- **MCP (Model Context Protocol) Servers** for external actions (browser automation, email, payments)

The architecture follows a **Perception → Reasoning → Action** pattern with human-in-the-loop approval for sensitive operations.

## Directory Structure

```
bronze-tier/
├── README.md                    # Project readme (minimal)
├── Personal AI Employee.md      # Comprehensive hackathon blueprint (1201 lines)
├── skills-lock.json             # Qwen skills configuration
├── .gitattributes               # Git text normalization settings
├── .qwen/                       # Qwen agent configuration
│   └── skills/
│       └── browsing-with-playwright/
│           ├── SKILL.md         # Playwright MCP usage documentation
│           ├── references/
│           │   └── playwright-tools.md  # Complete MCP tool reference
│           └── scripts/
│               ├── mcp-client.py        # MCP client for tool calls
│               ├── start-server.sh      # Start Playwright MCP server
│               ├── stop-server.sh       # Stop Playwright MCP server
│               └── verify.py            # Server health verification
```

## Key Concepts

### Digital FTE Comparison

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000–$8,000+ | $500–$2,000 |
| Ramp-up Time | 3–6 months | Instant |
| Consistency | 85–95% accuracy | 99%+ consistency |
| Annual Hours | ~2,000 hours | ~8,760 hours |

### Architecture Layers

1. **Perception (Watchers)**: Python scripts monitoring Gmail, WhatsApp, filesystems
2. **Reasoning (Claude Code)**: Reads tasks, creates plans, makes decisions
3. **Action (MCP Servers)**: Executes external actions (browser, email, payments)
4. **Memory (Obsidian)**: Long-term storage in Markdown format

### Folder Conventions (Obsidian Vault)

- `/Inbox` - Raw incoming items
- `/Needs_Action` - Items requiring attention
- `/In_Progress/<agent>/` - Claimed tasks (prevents double-work)
- `/Pending_Approval` - Actions awaiting human approval
- `/Approved` - Approved actions ready for execution
- `/Done` - Completed tasks
- `/Plans` - Generated action plans
- `/Briefings` - CEO briefing reports

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base/GUI |
| Python | 3.13+ | Watcher scripts |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Playwright MCP Server

The project includes a configured Playwright MCP skill for browser automation:

```bash
# Start the Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server (closes browser first)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# Navigate to a URL
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Take a page snapshot (accessibility tree)
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_snapshot \
  -p '{}'

# Click an element
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_click \
  -p '{"element": "Submit button", "ref": "e42"}'
```

### Ralph Wiggum Loop (Persistence Pattern)

For autonomous multi-step task completion, use the Ralph Wiggum pattern—a Stop hook that keeps Claude working until the task is complete:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Development Conventions

### Coding Style

- **Python**: Use type hints, follow PEP 8
- **Markdown**: Use YAML frontmatter for metadata
- **Shell Scripts**: Use bash with error handling

### Watcher Script Pattern

All Watcher scripts follow a base class pattern:

```python
from base_watcher import BaseWatcher
from pathlib import Path

class MyWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass
```

### Action File Schema

```markdown
---
type: email  # or: whatsapp, file_drop, payment, approval_request
from: sender@example.com
subject: Urgent matter
received: 2026-01-07T10:30:00Z
priority: high
status: pending
---

## Content
...

## Suggested Actions
- [ ] Action item 1
- [ ] Action item 2
```

### Human-in-the-Loop Pattern

For sensitive actions (payments, sending messages), Claude writes an approval request file instead of acting directly:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A

## To Approve
Move this file to /Approved folder.
```

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hours | Obsidian vault, 1 Watcher, Claude Code integration |
| **Silver** | 20-30 hours | Multiple Watchers, MCP server, HITL workflow |
| **Gold** | 40+ hours | Full integration, Odoo accounting, Ralph Wiggum loop |
| **Platinum** | 60+ hours | Cloud deployment, multi-agent sync, production-ready |

## Available Tools

### Playwright MCP Tools (22 tools)

- **Navigation**: `browser_navigate`, `browser_navigate_back`
- **Snapshot**: `browser_snapshot`, `browser_take_screenshot`
- **Interaction**: `browser_click`, `browser_type`, `browser_fill_form`, `browser_select_option`, `browser_hover`, `browser_drag`
- **Advanced**: `browser_evaluate`, `browser_run_code`, `browser_wait_for`
- **Utilities**: `browser_tabs`, `browser_resize`, `browser_console_messages`, `browser_network_requests`

See `.qwen/skills/browsing-with-playwright/references/playwright-tools.md` for complete tool documentation.

## Research Meetings

Weekly meetings every Wednesday at 10:00 PM PKT on Zoom:
- **Meeting ID**: 871 8870 7642
- **Passcode**: 744832
- **YouTube**: https://www.youtube.com/@panaversity

## Key Files

| File | Description |
|------|-------------|
| `Personal AI Employee.md` | Complete hackathon blueprint with architecture, templates, and implementation guides |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Playwright MCP server lifecycle and usage guide |
| `skills-lock.json` | Qwen skills configuration and versioning |
