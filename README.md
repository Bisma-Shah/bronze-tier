# 🤖 AI Employee - Bronze Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A Personal AI Employee built with Claude Code and Obsidian that proactively manages your personal and business affairs 24/7.

## 📋 Overview

This Bronze Tier implementation provides the foundation for an autonomous AI agent that:

- **Monitors** file drops and creates actionable tasks
- **Processes** items using Claude Code reasoning
- **Tracks** all actions in an Obsidian vault
- **Requires approval** for sensitive operations (Human-in-the-Loop)
- **Persists** until tasks are complete (Ralph Wiggum pattern)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI EMPLOYEE (Bronze Tier)                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   PERCEPTION    │────▶│    REASONING     │────▶│     ACTION      │
│                 │     │                  │     │                 │
│ • File Watcher  │     │ • Claude Code    │     │ • File Ops      │
│ • Drop Folder   │     │ • Orchestrator   │     │ • Dashboard     │
│                 │     │ • Ralph Wiggum   │     │ • Logging       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │     MEMORY       │
                    │                  │
                    │ • Obsidian Vault │
                    │ • Dashboard.md   │
                    │ • Company Handbook│
                    └──────────────────┘
```

## 📁 Project Structure

```
bronze-tier/
├── AI_Employee_Vault/       # Obsidian vault (memory)
│   ├── Dashboard.md         # Real-time status dashboard
│   ├── Company_Handbook.md  # Rules of engagement
│   ├── Business_Goals.md    # Objectives and metrics
│   ├── Inbox/               # Raw incoming items
│   ├── Needs_Action/        # Items requiring attention
│   ├── In_Progress/         # Items being worked on
│   ├── Pending_Approval/    # Awaiting human approval
│   ├── Approved/            # Approved actions ready to execute
│   ├── Done/                # Completed tasks
│   ├── Rejected/            # Rejected items
│   ├── Logs/                # Audit logs
│   ├── Briefings/           # CEO briefings
│   └── Accounting/          # Financial records
│
├── watchers/
│   ├── base_watcher.py      # Abstract base class
│   └── filesystem_watcher.py # File drop monitor
│
├── orchestrator.py          # Master process
├── requirements.txt         # Python dependencies
│
└── .claude/plugins/
    ├── ralph_wiggum.py      # Stop hook plugin
    └── ralph_wiggum_hook.sh # Shell integration
```

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Claude Code](https://claude.com/claude-code) | Latest | Reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Knowledge base |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers (future) |

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bronze-tier
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Open Obsidian Vault**
   ```bash
   # Open Obsidian and select the AI_Employee_Vault folder
   ```

4. **Verify Claude Code**
   ```bash
   claude --version
   ```

### Running the System

#### 1. Start the File System Watcher

```bash
# Terminal 1: Start the watcher
python watchers/filesystem_watcher.py AI_Employee_Vault
```

This monitors the `AI_Employee_Vault/Drop_Folder/` for new files.

#### 2. Start the Orchestrator

```bash
# Terminal 2: Start the orchestrator
python orchestrator.py AI_Employee_Vault
```

This processes pending items and updates the dashboard.

#### 3. Run Claude Code

```bash
# Terminal 3: Start Claude pointed at the vault
claude --cwd AI_Employee_Vault
```

#### 4. Process Tasks with Ralph Wiggum Loop

```bash
# In Claude Code, process pending items:
/ralph-loop "Process all files in /Needs_Action, analyze them, create plans, and move completed items to /Done"
```

## 📖 Usage Guide

### Adding Tasks

**Method 1: File Drop**
1. Copy any file to `AI_Employee_Vault/Drop_Folder/`
2. The watcher creates an action file in `Needs_Action/`
3. Claude processes it on next cycle

**Method 2: Manual Creation**
1. Create a `.md` file in `AI_Employee_Vault/Needs_Action/`
2. Use this format:
   ```markdown
   ---
   type: task
   priority: high
   created: 2026-02-24T10:00:00Z
   ---
   
   # Task Description
   
   ## Details
   Add details here
   
   ## Suggested Actions
   - [ ] Action 1
   - [ ] Action 2
   ```

### Approval Workflow

For sensitive actions, Claude creates a file in `Pending_Approval/`:

```markdown
---
type: approval_request
action: file_move
created: 2026-02-24T10:00:00Z
---

## Action Required
Move file to Approved folder

## To Approve
Move this file to /Approved folder

## To Reject
Move this file to /Rejected folder
```

**To approve**: Move the file to `Approved/`
**To reject**: Move the file to `Rejected/`

### Checking Status

Open `AI_Employee_Vault/Dashboard.md` in Obsidian for real-time status.

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# .env
VAULT_PATH=./AI_Employee_Vault
DRY_RUN=false
LOG_LEVEL=INFO
CHECK_INTERVAL=60
```

### Watcher Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `check_interval` | 5s | File system poll interval |
| `drop_folder` | `Drop_Folder/` | Folder to monitor |

### Orchestrator Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `cycle_interval` | 30s | Orchestration cycle interval |
| `dry_run` | false | Log without executing |

## 📊 Bronze Tier Deliverables

✅ **Completed**:
- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] File System Watcher (drop folder monitoring)
- [x] Claude Code integration (reading/writing to vault)
- [x] Basic folder structure (/Inbox, /Needs_Action, /Done)
- [x] Orchestrator for task coordination
- [x] Ralph Wiggum persistence pattern
- [x] Audit logging

## 🔮 Future Tiers

### Silver Tier (Next Steps)
- Gmail Watcher integration
- WhatsApp Watcher (Playwright-based)
- MCP server for email sending
- Scheduled operations (cron)

### Gold Tier
- Full cross-domain integration
- Odoo accounting integration
- CEO Briefing generation
- Error recovery

### Platinum Tier
- Cloud deployment (24/7)
- Multi-agent coordination
- Production monitoring

## 🛠️ Troubleshooting

### Watcher not detecting files

```bash
# Check if watchdog is installed
pip install watchdog

# Verify drop folder exists
ls AI_Employee_Vault/Drop_Folder/

# Check logs
cat AI_Employee_Vault/Logs/watcher_FileSystemWatcher.log
```

### Orchestrator not processing items

```bash
# Run in dry-run mode first
python orchestrator.py AI_Employee_Vault --dry-run --once

# Check logs
cat AI_Employee_Vault/Logs/orchestrator_*.log
```

### Ralph Wiggum not working

```bash
# Reset state
python .claude/plugins/ralph_wiggum.py AI_Employee_Vault --reset

# Verify plugin location
ls ~/.claude/plugins/ralph_wiggum.py
```

## 📝 Example Flow

### Scenario: Process a dropped invoice file

1. **Drop file**: Copy `invoice.pdf` to `AI_Employee_Vault/Drop_Folder/`

2. **Watcher detects**: Creates `FILE_invoice.pdf.md` in `Needs_Action/`

3. **Orchestrator updates**: Dashboard shows 1 pending item

4. **Claude processes**:
   - Reads the action file
   - Creates plan in `Plans/`
   - Moves file to `Done/` after processing

5. **Dashboard updates**: Shows completed task

## 🔒 Security

- **Local-first**: All data stays on your machine
- **Human-in-the-loop**: Sensitive actions require approval
- **Audit logging**: Every action is logged
- **No credential storage**: Use environment variables

## 📚 Documentation

- [Company Handbook](AI_Employee_Vault/Company_Handbook.md) - Rules of engagement
- [Business Goals](AI_Employee_Vault/Business_Goals.md) - Objectives and metrics
- [Dashboard](AI_Employee_Vault/Dashboard.md) - Real-time status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [Claude Code](https://claude.com/claude-code) - Reasoning engine
- [Obsidian](https://obsidian.md) - Knowledge base
- [Panaversity](https://panaversity.org) - Hackathon organizers

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*
