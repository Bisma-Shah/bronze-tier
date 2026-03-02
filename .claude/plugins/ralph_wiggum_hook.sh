# Ralph Wiggum Stop Hook for Claude Code
# 
# This script integrates the Ralph Wiggum pattern with Claude Code.
# It intercepts Claude's exit and keeps it working until tasks are complete.
#
# Usage:
#   source ralph_wiggum_hook.sh /path/to/vault
#

RALPH_VAULT_PATH="${1:-.}"
RALPH_MAX_ITERATIONS="${2:-10}"
RALPH_STATE_FILE="$RALPH_VAULT_PATH/.ralph_state.json"

# Function to check if task is complete
ralph_check_completion() {
    local vault="$1"
    local needs_action="$vault/Needs_Action"
    local in_progress="$vault/In_Progress"
    local pending_approval="$vault/Pending_Approval"
    
    # Count pending items
    local pending_count=0
    
    if [ -d "$needs_action" ]; then
        local count=$(find "$needs_action" -name "*.md" 2>/dev/null | wc -l)
        pending_count=$((pending_count + count))
    fi
    
    if [ -d "$in_progress" ]; then
        local count=$(find "$in_progress" -name "*.md" 2>/dev/null | wc -l)
        pending_count=$((pending_count + count))
    fi
    
    if [ -d "$pending_approval" ]; then
        local count=$(find "$pending_approval" -name "*.md" 2>/dev/null | wc -l)
        # Don't count pending approval as incomplete - those need human action
    fi
    
    echo "$pending_count"
}

# Function to get iteration count
ralph_get_iteration() {
    if [ -f "$RALPH_STATE_FILE" ]; then
        python3 -c "import json; print(json.load(open('$RALPH_STATE_FILE')).get('iteration_count', 0))" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Function to save iteration count
ralph_save_iteration() {
    local count="$1"
    python3 -c "
import json
from datetime import datetime
state = {
    'iteration_count': $count,
    'last_updated': datetime.now().isoformat(),
    'vault_path': '$RALPH_VAULT_PATH'
}
json.dump(state, open('$RALPH_STATE_FILE', 'w'), indent=2)
"
}

# Function to reset state
ralph_reset() {
    rm -f "$RALPH_STATE_FILE"
    echo "Ralph Wiggum state reset"
}

# Main hook function - call this after Claude exits
ralph_post_exit_hook() {
    local exit_code=$?
    
    # Get current iteration
    local iteration=$(ralph_get_iteration)
    iteration=$((iteration + 1))
    ralph_save_iteration "$iteration"
    
    # Check completion
    local pending=$(ralph_check_completion "$RALPH_VAULT_PATH")
    
    if [ "$pending" -gt 0 ]; then
        if [ "$iteration" -ge "$RALPH_MAX_ITERATIONS" ]; then
            echo "⏹️  Ralph Wiggum: Max iterations ($RALPH_MAX_ITERATIONS) reached. Stopping."
            ralph_reset
            return 1
        fi
        
        echo "⏸️  Ralph Wiggum: $pending item(s) still pending (iteration $iteration/$RALPH_MAX_ITERATIONS)"
        echo ""
        echo "<RALPH_WIGGUM_LOOP>"
        echo "The task is not yet complete. Continue working."
        echo ""
        echo "Check these folders:"
        echo "  - /Needs_Action/ - Items requiring attention"
        echo "  - /In_Progress/ - Items being worked on"
        echo ""
        echo "Continue processing until all items are moved to /Done/ or /Pending_Approval/."
        echo "</RALPH_WIGGUM_LOOP>"
        echo ""
        
        # Return special code to indicate re-injection needed
        return 42
    fi
    
    echo "✅ Ralph Wiggum: All tasks complete after $iteration iteration(s)"
    ralph_reset
    return 0
}

# Export functions for use in shell
export -f ralph_check_completion
export -f ralph_get_iteration
export -f ralph_save_iteration
export -f ralph_post_exit_hook
export -f ralph_reset

echo "Ralph Wiggum Stop Hook loaded"
echo "  Vault: $RALPH_VAULT_PATH"
echo "  Max iterations: $RALPH_MAX_ITERATIONS"
echo ""
echo "Usage:"
echo "  After running claude, call: ralph_post_exit_hook"
echo "  To reset: ralph_reset"
