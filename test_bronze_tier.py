"""
Test and Verification Script for Bronze Tier AI Employee

This script verifies that all Bronze Tier components are properly set up and functional.

Usage:
    python test_bronze_tier.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Unicode symbols (fallback for Windows)
    CHECK = '[OK]'
    CROSS = '[FAIL]'
    WARNING = '[WARN]'
    BULLET = '[INFO]'


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}{Colors.CHECK}{Colors.RESET} {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}{Colors.CROSS}{Colors.RESET} {text}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}{Colors.WARNING}{Colors.RESET} {text}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}{Colors.BULLET}{Colors.RESET} {text}")


class BronzeTierTester:
    """Test suite for Bronze Tier AI Employee."""
    
    def __init__(self):
        self.root = Path(__file__).parent
        self.vault = self.root / 'AI_Employee_Vault'
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        print_header("AI Employee - Bronze Tier Verification")
        print_info(f"Root directory: {self.root}")
        print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_directory_structure()
        self.test_vault_files()
        self.test_python_modules()
        self.test_claude_plugins()
        self.test_configuration_files()
        self.test_imports()
        
        self.print_summary()
        
        return self.failed == 0
    
    def test_directory_structure(self) -> None:
        """Test required directory structure."""
        print_header("1. Directory Structure")
        
        required_dirs = [
            'AI_Employee_Vault/Inbox',
            'AI_Employee_Vault/Needs_Action',
            'AI_Employee_Vault/Done',
            'AI_Employee_Vault/Plans',
            'AI_Employee_Vault/Pending_Approval',
            'AI_Employee_Vault/Approved',
            'AI_Employee_Vault/Rejected',
            'AI_Employee_Vault/Logs',
            'AI_Employee_Vault/Briefings',
            'AI_Employee_Vault/Accounting',
            'AI_Employee_Vault/Invoices',
            'AI_Employee_Vault/In_Progress',
            'watchers',
            '.claude/plugins',
        ]
        
        for dir_path in required_dirs:
            full_path = self.root / dir_path
            if full_path.exists() and full_path.is_dir():
                print_success(f"Directory exists: {dir_path}")
                self.passed += 1
            else:
                print_error(f"Missing directory: {dir_path}")
                self.failed += 1
    
    def test_vault_files(self) -> None:
        """Test required vault files."""
        print_header("2. Vault Files")
        
        required_files = [
            'AI_Employee_Vault/Dashboard.md',
            'AI_Employee_Vault/Company_Handbook.md',
            'AI_Employee_Vault/Business_Goals.md',
        ]
        
        for file_path in required_files:
            full_path = self.root / file_path
            if full_path.exists() and full_path.is_file():
                print_success(f"File exists: {file_path}")
                self.passed += 1
            else:
                print_error(f"Missing file: {file_path}")
                self.failed += 1
    
    def test_python_modules(self) -> None:
        """Test Python module files."""
        print_header("3. Python Modules")
        
        required_modules = [
            'watchers/base_watcher.py',
            'watchers/filesystem_watcher.py',
            'orchestrator.py',
            '.claude/plugins/ralph_wiggum.py',
        ]
        
        for module_path in required_modules:
            full_path = self.root / module_path
            if full_path.exists() and full_path.is_file():
                print_success(f"Module exists: {module_path}")
                self.passed += 1
            else:
                print_error(f"Missing module: {module_path}")
                self.failed += 1
    
    def test_claude_plugins(self) -> None:
        """Test Claude plugin files."""
        print_header("4. Claude Plugins")
        
        required_plugins = [
            '.claude/plugins/ralph_wiggum.py',
            '.claude/plugins/ralph_wiggum_hook.sh',
        ]
        
        for plugin_path in required_plugins:
            full_path = self.root / plugin_path
            if full_path.exists() and full_path.is_file():
                print_success(f"Plugin exists: {plugin_path}")
                self.passed += 1
            else:
                print_error(f"Missing plugin: {plugin_path}")
                self.failed += 1
    
    def test_configuration_files(self) -> None:
        """Test configuration files."""
        print_header("5. Configuration Files")
        
        required_files = [
            'requirements.txt',
            '.env.example',
            '.gitignore',
            'README.md',
        ]
        
        for file_path in required_files:
            full_path = self.root / file_path
            if full_path.exists() and full_path.is_file():
                print_success(f"Config exists: {file_path}")
                self.passed += 1
            else:
                print_error(f"Missing config: {file_path}")
                self.failed += 1
    
    def test_imports(self) -> None:
        """Test Python imports."""
        print_header("6. Python Imports")
        
        # Add root to path
        sys.path.insert(0, str(self.root))
        
        # Test base imports
        try:
            from pathlib import Path
            print_success("pathlib available")
            self.passed += 1
        except ImportError as e:
            print_error(f"pathlib import failed: {e}")
            self.failed += 1
        
        # Test watchdog (optional)
        try:
            import watchdog
            print_success("watchdog installed (real-time file monitoring)")
            self.passed += 1
        except ImportError:
            print_warning("watchdog not installed (will use poll mode)")
            self.warnings += 1
        
        # Test dotenv (optional)
        try:
            import dotenv
            print_success("python-dotenv installed")
            self.passed += 1
        except ImportError:
            print_warning("python-dotenv not installed (will use defaults)")
            self.warnings += 1
        
        # Test module syntax
        try:
            import watchers.base_watcher
            print_success("base_watcher.py syntax valid")
            self.passed += 1
        except Exception as e:
            print_error(f"base_watcher.py error: {e}")
            self.failed += 1
        
        try:
            import watchers.filesystem_watcher
            print_success("filesystem_watcher.py syntax valid")
            self.passed += 1
        except Exception as e:
            print_error(f"filesystem_watcher.py error: {e}")
            self.failed += 1
        
        try:
            import orchestrator
            print_success("orchestrator.py syntax valid")
            self.passed += 1
        except Exception as e:
            print_error(f"orchestrator.py error: {e}")
            self.failed += 1
    
    def print_summary(self) -> None:
        """Print test summary."""
        print_header("Test Summary")
        
        total = self.passed + self.failed
        print_info(f"Total tests: {total}")
        print_success(f"Passed: {self.passed}")
        
        if self.failed > 0:
            print_error(f"Failed: {self.failed}")
        else:
            print_info("Failed: 0")
        
        if self.warnings > 0:
            print_warning(f"Warnings: {self.warnings}")
        
        print()
        
        if self.failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] Bronze Tier is ready!{Colors.RESET}")
            print("\nNext steps:")
            print("  1. Install dependencies: pip install -r requirements.txt")
            print("  2. Open vault in Obsidian: AI_Employee_Vault/")
            print("  3. Start watcher: python watchers/filesystem_watcher.py AI_Employee_Vault")
            print("  4. Start orchestrator: python orchestrator.py AI_Employee_Vault")
            print("  5. Run Claude: claude --cwd AI_Employee_Vault")
        else:
            print(f"{Colors.RED}{Colors.BOLD}[ERROR] Some tests failed. Please fix the issues above.{Colors.RESET}")


def main():
    """Main entry point."""
    tester = BronzeTierTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
