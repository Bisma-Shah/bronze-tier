"""
Ralph Wiggum Stop Hook Plugin

This plugin intercepts Claude Code's exit attempt and checks if the task is complete.
If incomplete, it blocks the exit and re-injects the prompt to continue working.

Installation:
    Copy this file to: ~/.claude/plugins/ralph_wiggum.py
    
Usage in Claude Code:
    /ralph-loop "Process all files in /Needs_Action, move to Done when complete"
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


class RalphWiggumPlugin:
    """
    Ralph Wiggum Stop Hook Plugin.
    
    Keeps Claude Code working until tasks are complete by intercepting
    exit attempts and checking completion status.
    """
    
    def __init__(self, vault_path: str, max_iterations: int = 10):
        """
        Initialize the Ralph Wiggum plugin.
        
        Args:
            vault_path: Path to the Obsidian vault
            max_iterations: Maximum loop iterations before forcing exit
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.iteration_count = 0
        
        # State file to track iterations
        self.state_file = self.vault_path / '.ralph_state.json'
        
        # Load existing state
        self._load_state()
    
    def _load_state(self) -> None:
        """Load iteration state from file."""
        import json
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.iteration_count = state.get('iteration_count', 0)
            except Exception:
                self.iteration_count = 0
    
    def _save_state(self) -> None:
        """Save iteration state to file."""
        import json
        
        state = {
            'iteration_count': self.iteration_count,
            'last_updated': datetime.now().isoformat(),
            'vault_path': str(self.vault_path)
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def should_allow_exit(self) -> Tuple[bool, str]:
        """
        Check if Claude should be allowed to exit.
        
        Returns:
            Tuple of (allow_exit: bool, reason: str)
        """
        self.iteration_count += 1
        self._save_state()
        
        # Check max iterations
        if self.iteration_count >= self.max_iterations:
            return True, f'Max iterations ({self.max_iterations}) reached'
        
        # Check if Needs_Action is empty
        needs_action = self.vault_path / 'Needs_Action'
        if needs_action.exists():
            pending_files = list(needs_action.glob('*.md'))
            if pending_files:
                return False, f'{len(pending_files)} pending item(s) still in Needs_Action'
        
        # Check if In_Progress has items
        in_progress = self.vault_path / 'In_Progress'
        if in_progress.exists():
            progress_files = list(in_progress.glob('*.md'))
            if progress_files:
                return False, f'{len(progress_files)} item(s) still in progress'
        
        # Check if Pending_Approval has items
        pending_approval = self.vault_path / 'Pending_Approval'
        if pending_approval.exists():
            approval_files = list(pending_approval.glob('*.md'))
            if approval_files:
                return False, f'{len(approval_files)} item(s) awaiting approval'
        
        # All clear - allow exit
        return True, 'All tasks complete'
    
    def get_continuation_prompt(self) -> str:
        """
        Generate a continuation prompt to re-inject.
        
        Returns:
            Prompt string to continue working
        """
        return f'''
<RALPH_WIGGUM_LOOP>
Iteration: {self.iteration_count + 1}/{self.max_iterations}

The task is not yet complete. Continue working on the remaining items.

Check these folders:
- /Needs_Action/ - Items requiring attention
- /In_Progress/ - Items being worked on
- /Pending_Approval/ - Items awaiting human approval

Continue processing until all items are moved to /Done/ or /Pending_Approval/.
</RALPH_WIGGUM_LOOP>
'''
    
    def reset(self) -> None:
        """Reset the iteration counter."""
        self.iteration_count = 0
        self._save_state()
        
        # Remove state file
        if self.state_file.exists():
            self.state_file.unlink()


def ralph_wiggum_hook(vault_path: str, max_iterations: int = 10) -> None:
    """
    Main entry point for the Ralph Wiggum hook.
    
    This function is called by Claude Code's plugin system.
    
    Args:
        vault_path: Path to the Obsidian vault
        max_iterations: Maximum loop iterations
    """
    plugin = RalphWiggumPlugin(vault_path, max_iterations)
    
    allow_exit, reason = plugin.should_allow_exit()
    
    if allow_exit:
        print(f"✅ Ralph Wiggum: {reason}")
        plugin.reset()
    else:
        print(f"⏸️  Ralph Wiggum: {reason}")
        print(plugin.get_continuation_prompt())
        # Exit with special code to trigger re-injection
        sys.exit(42)  # Special code recognized by the stop hook


# CLI interface for testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Stop Hook')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--max-iterations', type=int, default=10,
                       help='Maximum loop iterations')
    parser.add_argument('--reset', action='store_true', help='Reset iteration counter')
    
    args = parser.parse_args()
    
    plugin = RalphWiggumPlugin(args.vault_path, args.max_iterations)
    
    if args.reset:
        plugin.reset()
        print("Iteration counter reset")
        sys.exit(0)
    
    allow_exit, reason = plugin.should_allow_exit()
    
    print(f"Vault: {args.vault_path}")
    print(f"Iteration: {plugin.iteration_count}/{args.max_iterations}")
    print(f"Status: {'✅ Allow exit' if allow_exit else '⏸️  Block exit'}")
    print(f"Reason: {reason}")
    
    if not allow_exit:
        print("\nContinuation prompt:")
        print(plugin.get_continuation_prompt())
