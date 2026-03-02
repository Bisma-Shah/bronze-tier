"""
Demo Script for Bronze Tier AI Employee

This script demonstrates the AI Employee system by:
1. Showing current vault status
2. Processing sample files
3. Simulating the workflow

Usage:
    python demo.py
"""

import sys
from pathlib import Path
from datetime import datetime


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")


def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}>> {text}{Colors.RESET}\n")


def print_item(text, icon="•"):
    print(f"  {icon} {text}")


def count_md_files(folder):
    """Count markdown files in a folder."""
    if not folder.exists():
        return 0
    return len(list(folder.glob('*.md')))


def show_vault_status(vault):
    """Display current vault status."""
    print_header("AI Employee Vault Status")
    
    folders = {
        'Inbox': 'Raw incoming items',
        'Needs_Action': 'Items requiring attention',
        'In_Progress': 'Items being worked on',
        'Pending_Approval': 'Awaiting human approval',
        'Approved': 'Approved, ready to execute',
        'Done': 'Completed tasks',
        'Plans': 'Action plans',
    }
    
    print_section("Folder Contents")
    
    for folder_name, description in folders.items():
        folder_path = vault / folder_name
        count = count_md_files(folder_path)
        
        if count > 0:
            status = f"{Colors.YELLOW}{count} item(s){Colors.RESET}"
        else:
            status = f"{Colors.GREEN}Empty{Colors.RESET}"
        
        print_item(f"{folder_name:25} | {status:20} | {description}")
    
    print()


def show_file_details(vault):
    """Show details of files in key folders."""
    print_header("File Details")
    
    # Show Needs_Action files
    needs_action = vault / 'Needs_Action'
    if needs_action.exists():
        files = list(needs_action.glob('*.md'))
        if files:
            print_section("Needs Action (Ready for Processing)")
            for f in files:
                stat = f.stat()
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime)
                print_item(f"{f.name}")
                print_item(f"  Size: {size} bytes | Modified: {modified.strftime('%Y-%m-%d %H:%M')}", "  ")
                
                # Read and show type/priority
                try:
                    content = f.read_text()
                    if 'priority: high' in content:
                        print_item(f"  Priority: HIGH", "  ")
                    if 'type:' in content:
                        for line in content.split('\n'):
                            if line.startswith('type:'):
                                print_item(f"  Type: {line.split(':')[1].strip()}", "  ")
                                break
                except Exception:
                    pass
                print()
    
    # Show Pending_Approval files
    pending_approval = vault / 'Pending_Approval'
    if pending_approval.exists():
        files = list(pending_approval.glob('*.md'))
        if files:
            print_section("Pending Approval (Requires Your Decision)")
            for f in files:
                print_item(f"{f.name}")
                
                try:
                    content = f.read_text()
                    # Extract action type and amount
                    for line in content.split('\n'):
                        if line.startswith('action:'):
                            print_item(f"  Action: {line.split(':')[1].strip()}", "  ")
                        if line.startswith('amount:'):
                            print_item(f"  Amount: {line.split(':')[1].strip()}", "  ")
                except Exception:
                    pass
                print()
    
    # Show Plans files
    plans = vault / 'Plans'
    if plans.exists():
        files = list(plans.glob('*.md'))
        if files:
            print_section("Active Plans")
            for f in files:
                print_item(f"{f.name}")
                
                try:
                    content = f.read_text()
                    for line in content.split('\n'):
                        if line.startswith('status:'):
                            print_item(f"  Status: {line.split(':')[1].strip()}", "  ")
                        if line.startswith('objective:'):
                            print_item(f"  Objective: {line.split(':')[1].strip()[:50]}...", "  ")
                except Exception:
                    pass
                print()


def show_workflow_guide():
    """Display workflow guide."""
    print_header("How The AI Employee Works")
    
    print_section("Workflow Overview")
    print("""
    1. INPUT: Files dropped or created in Needs_Action/
       • Email requests
       • Task assignments
       • File drops
    
    2. PROCESSING: Claude Code analyzes and creates plans
       • Reads Company_Handbook.md for rules
       • Creates Plan.md in Plans/ folder
       • Identifies actions requiring approval
    
    3. APPROVAL: Sensitive actions require your decision
       • Files in Pending_Approval/ need your review
       • Move to Approved/ to proceed
       • Move to Rejected/ to decline
    
    4. ACTION: Approved actions are executed
       • Emails sent
       • Files moved
       • Logs updated
    
    5. COMPLETION: Tasks moved to Done/
       • Dashboard updated
       • Activity logged
    """)
    
    print_section("Your Role (Human-in-the-Loop)")
    print_item("Review files in Pending_Approval/ folder")
    print_item("Move to Approved/ to authorize actions")
    print_item("Move to Rejected/ to decline")
    print_item("Check Dashboard.md for status updates")


def show_quick_commands():
    """Display quick start commands."""
    print_header("Quick Start Commands")
    
    print_section("Start the System")
    print("  # Terminal 1: Start file watcher")
    print("  python watchers/filesystem_watcher.py AI_Employee_Vault")
    print()
    print("  # Terminal 2: Start orchestrator")
    print("  python orchestrator.py AI_Employee_Vault")
    print()
    print("  # Terminal 3: Run Claude Code")
    print("  claude --cwd AI_Employee_Vault")
    print()
    
    print_section("Test Commands")
    print("  # Run verification tests")
    print("  python test_bronze_tier.py")
    print()
    print("  # Run orchestrator once (no loop)")
    print("  python orchestrator.py AI_Employee_Vault --once")
    print()
    print("  # Run orchestrator in dry-run mode")
    print("  python orchestrator.py AI_Employee_Vault --dry-run --once")
    print()


def main():
    """Main demo function."""
    vault = Path(__file__).parent / 'AI_Employee_Vault'
    
    if not vault.exists():
        print(f"{Colors.RED}Error: Vault not found at {vault}{Colors.RESET}")
        sys.exit(1)
    
    print_header("AI Employee - Bronze Tier Demo")
    print(f"Vault Location: {vault.absolute()}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    show_vault_status(vault)
    show_file_details(vault)
    show_workflow_guide()
    show_quick_commands()
    
    print_header("Demo Complete")
    print(f"{Colors.GREEN}Your AI Employee Bronze Tier is ready to use!{Colors.RESET}")
    print()
    print("Next Steps:")
    print("  1. Review the files shown above")
    print("  2. Run: python orchestrator.py AI_Employee_Vault --once")
    print("  3. Open Dashboard.md in Obsidian to see status")
    print("  4. Start Claude Code to process pending tasks")
    print()


if __name__ == '__main__':
    main()
