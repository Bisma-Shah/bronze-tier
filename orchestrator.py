"""
Orchestrator Module

Master process for the AI Employee system. Manages watchers, processes action files,
updates the dashboard, and coordinates Claude Code interactions.

Usage:
    python orchestrator.py /path/to/vault [--dry-run]
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Responsibilities:
    - Monitor Needs_Action folder for pending items
    - Update Dashboard.md with current status
    - Trigger Claude Code for reasoning tasks
    - Manage approval workflows
    - Log all operations
    """
    
    def __init__(self, vault_path: str, dry_run: bool = False):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
            dry_run: If True, log actions without executing
        """
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        
        # Folder paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.in_progress = self.vault_path / 'In_Progress'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all directories exist
        for folder in [self.needs_action, self.done, self.plans, 
                       self.pending_approval, self.approved, self.rejected,
                       self.in_progress, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info(f'Orchestrator initialized')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Dry run: {dry_run}')
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y%m%d")}.log'
        
        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
    
    def run(self) -> None:
        """
        Main orchestration loop.
        """
        self.logger.info('Starting orchestration loop')
        
        try:
            while True:
                self._process_cycle()
                import time
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
    
    def _process_cycle(self) -> None:
        """
        Execute one orchestration cycle.
        """
        try:
            # Update dashboard
            self.update_dashboard()
            
            # Check for approved actions
            self.process_approved_actions()
            
            # Check for pending items
            self.process_needs_action()
            
            # Log cycle completion
            self.logger.debug('Orchestration cycle complete')
            
        except Exception as e:
            self.logger.error(f'Error in cycle: {e}')
    
    def update_dashboard(self) -> None:
        """
        Update the Dashboard.md with current status.
        """
        try:
            # Count items in each folder
            pending_count = len(list(self.needs_action.glob('*.md')))
            approval_count = len(list(self.pending_approval.glob('*.md')))
            in_progress_count = len(list(self.in_progress.glob('*.md')))
            done_today = len([
                f for f in self.done.glob('*.md')
                if self._is_today(f)
            ])
            
            # Get recent activity
            recent_activity = self._get_recent_activity()
            
            # Generate dashboard content
            content = f'''---
last_updated: {datetime.now().isoformat()}
version: 0.1.0
---

# AI Employee Dashboard

## Quick Stats

| Metric | Value | Status |
|--------|-------|--------|
| Pending Tasks | {pending_count} | {"Action needed" if pending_count > 0 else "Clear"} |
| Awaiting Approval | {approval_count} | {"Review required" if approval_count > 0 else "Clear"} |
| In Progress | {in_progress_count} | - |
| Completed Today | {done_today} | - |

---

## Inbox Status

- **Needs Action**: {pending_count}
- **In Progress**: {in_progress_count}
- **Pending Approval**: {approval_count}

---

## Pending Approvals

{self._list_pending_approvals()}

---

## Active Projects

*No active projects*

---

## Recent Transactions

*No transactions this month*

---

## Completed Today

{self._list_completed_today()}

---

## Alerts & Notifications

{self._get_alerts()}

---

## Recent Activity Log

{recent_activity}

---
*Last generated by AI Employee v0.1 (Bronze Tier)*
'''

            if not self.dry_run:
                self.dashboard.write_text(content, encoding='utf-8')

            self.logger.debug(f'Dashboard updated: {pending_count} pending, {approval_count} awaiting approval')

        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def _is_today(self, file_path: Path) -> bool:
        """Check if file was modified today."""
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return mtime.date() == datetime.now().date()
        except Exception:
            return False
    
    def _get_recent_activity(self, limit: int = 10) -> str:
        """Get recent activity log entries."""
        try:
            # Get recent log files
            log_files = sorted(self.logs.glob('*.log'), key=lambda f: f.stat().st_mtime, reverse=True)
            
            if not log_files:
                return '| Time | Action | Status |\n|------|--------|--------|\n| - | No activity logged | - |'
            
            activities = []
            for log_file in log_files[:3]:  # Check last 3 log files
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-limit:]
                        for line in lines:
                            if 'INFO' in line or 'WARNING' in line:
                                parts = line.strip().split(' - ')
                                if len(parts) >= 4:
                                    time_str = parts[0].split(',')[1].strip()
                                    level = parts[2]
                                    message = parts[3][:50]
                                    status = '[OK]' if 'INFO' in level else '[WARN]'
                                    activities.append(f'| {time_str} | {message} | {status} |')
                except Exception:
                    pass
            
            if not activities:
                return '| Time | Action | Status |\n|------|--------|--------|\n| - | No recent activity | - |'
            
            return '| Time | Action | Status |\n|------|--------|--------|\n' + '\n'.join(activities[:limit])
            
        except Exception as e:
            self.logger.error(f'Error getting recent activity: {e}')
            return '| Time | Action | Status |\n|------|--------|--------|\n| - | Error retrieving activity | [ERROR] |'
    
    def _list_pending_approvals(self) -> str:
        """List pending approval items."""
        try:
            approvals = list(self.pending_approval.glob('*.md'))
            
            if not approvals:
                return '*No pending approvals*'
            
            lines = ['| File | Created | Type |', '|------|---------|------|']
            for approval in approvals[:10]:  # Limit to 10
                try:
                    content = approval.read_text()
                    created = self._extract_yaml_field(content, 'created', 'Unknown')
                    action_type = self._extract_yaml_field(content, 'action', 'general')
                    lines.append(f'| {approval.name} | {created} | {action_type} |')
                except Exception:
                    lines.append(f'| {approval.name} | Unknown | - |')
            
            return '\n'.join(lines)
            
        except Exception as e:
            self.logger.error(f'Error listing pending approvals: {e}')
            return '*Error retrieving pending approvals*'
    
    def _list_completed_today(self) -> str:
        """List completed items from today."""
        try:
            done_files = [f for f in self.done.glob('*.md') if self._is_today(f)]
            
            if not done_files:
                return '*No completed tasks today*'
            
            lines = []
            for done_file in sorted(done_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                lines.append(f'- [x] {done_file.name}')
            
            return '\n'.join(lines)
            
        except Exception as e:
            self.logger.error(f'Error listing completed today: {e}')
            return '*Error retrieving completed tasks*'
    
    def _get_alerts(self) -> str:
        """Get current alerts."""
        try:
            alerts = []
            
            # Check for old pending items
            for item in self.needs_action.glob('*.md'):
                age = datetime.now().timestamp() - item.stat().st_mtime
                if age > 86400 * 2:  # Older than 2 days
                    alerts.append(f'[ALERT] {item.name} pending for >2 days')
            
            if not alerts:
                return '*No alerts*'
            
            return '\n'.join(alerts[:5])  # Limit to 5 alerts
            
        except Exception as e:
            self.logger.error(f'Error getting alerts: {e}')
            return '*Error retrieving alerts*'
    
    def _extract_yaml_field(self, content: str, field: str, default: str) -> str:
        """Extract a field from YAML frontmatter."""
        try:
            lines = content.split('\n')
            in_yaml = False
            for line in lines:
                if line.strip() == '---':
                    in_yaml = not in_yaml
                    continue
                if in_yaml and line.startswith(f'{field}:'):
                    return line.split(':', 1)[1].strip()
            return default
        except Exception:
            return default
    
    def process_approved_actions(self) -> None:
        """
        Process items in the Approved folder.
        """
        try:
            approved_files = list(self.approved.glob('*.md'))
            
            for approved_file in approved_files:
                try:
                    self._process_approved_file(approved_file)
                except Exception as e:
                    self.logger.error(f'Error processing {approved_file.name}: {e}')
                    
        except Exception as e:
            self.logger.error(f'Error processing approved actions: {e}')
    
    def _process_approved_file(self, approved_file: Path) -> None:
        """
        Process a single approved file.
        
        Args:
            approved_file: Path to the approved file
        """
        self.logger.info(f'Processing approved file: {approved_file.name}')
        
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would process: {approved_file.name}')
            return
        
        # Move to Done folder
        dest = self.done / approved_file.name
        shutil = __import__('shutil')
        shutil.move(str(approved_file), str(dest))
        
        self.logger.info(f'Moved {approved_file.name} to Done')
    
    def process_needs_action(self) -> None:
        """
        Process items in Needs_Action folder.
        """
        try:
            pending_files = list(self.needs_action.glob('*.md'))
            
            if not pending_files:
                return
            
            self.logger.info(f'Found {len(pending_files)} pending item(s)')
            
            # Create a summary for Claude Code processing
            self._create_claude_prompt(pending_files)
            
        except Exception as e:
            self.logger.error(f'Error processing needs action: {e}')
    
    def _create_claude_prompt(self, pending_files: List[Path]) -> None:
        """
        Create a prompt file for Claude Code to process pending items.
        
        Args:
            pending_files: List of pending action files
        """
        try:
            prompt_file = self.vault_path / 'CLAUDE_PROMPT.md'
            
            content = f'''# Claude Code Processing Request

**Generated**: {datetime.now().isoformat()}

## Pending Items

{len(pending_files)} item(s) require attention in `/Needs_Action/`

## Instructions

1. Read all files in `/Needs_Action/` folder
2. For each item:
   - Analyze the content and type
   - Determine required actions
   - Create a plan in `/Plans/` folder
   - If approval needed, create file in `/Pending_Approval/`
   - If auto-actionable, process and move to `/Done/`

3. Update Dashboard.md with current status
4. Log all actions taken

## Company Handbook

Refer to `/Company_Handbook.md` for rules and guidelines.

## Output

After processing, move completed items to `/Done/` folder.
'''
            
            if not self.dry_run:
                prompt_file.write_text(content)
                self.logger.info(f'Created Claude prompt: {prompt_file.name}')
            
        except Exception as e:
            self.logger.error(f'Error creating Claude prompt: {e}')
    
    def log_action(self, action_type: str, details: Dict[str, Any], result: str = 'success') -> None:
        """
        Log an action to the audit log.
        
        Args:
            action_type: Type of action (e.g., 'file_move', 'approval_request')
            details: Dictionary of action details
            result: Result status ('success', 'error', 'skipped')
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action_type': action_type,
                'actor': 'orchestrator',
                'parameters': details,
                'result': result
            }
            
            log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.json'
            
            # Append to log file
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            if not self.dry_run:
                with open(log_file, 'w') as f:
                    json.dump(logs, f, indent=2)
            
            self.logger.debug(f'Logged action: {action_type}')
            
        except Exception as e:
            self.logger.error(f'Error logging action: {e}')


def main():
    """
    Entry point for the orchestrator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--dry-run', action='store_true', help='Log actions without executing')
    parser.add_argument('--once', action='store_true', help='Run once and exit (no loop)')
    
    args = parser.parse_args()
    
    # Validate vault path
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)
    
    # Create and run orchestrator
    orchestrator = Orchestrator(str(vault_path), dry_run=args.dry_run)
    
    if args.once:
        orchestrator._process_cycle()
        print("Orchestration cycle complete")
    else:
        orchestrator.run()


if __name__ == '__main__':
    main()
