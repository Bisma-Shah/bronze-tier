"""
File System Watcher Module

Monitors a drop folder for new files and creates action files for processing.
This is the Bronze Tier watcher - simple, reliable, and doesn't require API credentials.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Watchdog library for file system events
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create stub for when watchdog is not available
    class FileSystemEventHandler:
        pass
    Observer = None
    FileCreatedEvent = None
    print("Warning: watchdog not installed. Running in poll mode.")


class DropFolderHandler(FileSystemEventHandler):
    """
    Handles file system events in the drop folder.
    """
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        """
        Initialize the handler.
        
        Args:
            watcher: Parent FileSystemWatcher instance
        """
        super().__init__()
        self.watcher = watcher
    
    def on_created(self, event) -> None:
        """
        Handle file creation events.
        
        Args:
            event: File system event object
        """
        if event.is_directory:
            return
        
        self.watcher.logger.info(f'File detected: {event.src_path}')
        
        try:
            source = Path(event.src_path)
            
            # Wait a moment for file to be fully written
            import time
            time.sleep(0.5)
            
            # Create action file
            self.watcher.process_file(source)
            
        except Exception as e:
            self.watcher.logger.error(f'Error processing file: {e}')


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    When a file is dropped into the monitored folder, this watcher:
    1. Copies the file to Needs_Action
    2. Creates a markdown metadata file
    3. Logs the action
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the drop folder (default: vault/Drop_Folder)
            check_interval: Seconds between checks in poll mode
        """
        super().__init__(vault_path, check_interval)
        
        self.drop_folder = Path(drop_folder) if drop_folder else self.vault_path / 'Drop_Folder'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files: set = set()
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
    
    def check_for_updates(self) -> List[Path]:
        """
        Check the drop folder for new files (poll mode).
        
        Returns:
            List of new file paths
        """
        if not WATCHDOG_AVAILABLE:
            # Poll mode - check for new files
            new_files = []
            
            try:
                for file_path in self.drop_folder.iterdir():
                    if file_path.is_file() and file_path not in self.processed_files:
                        # Check if file is fully written (not being copied)
                        try:
                            file_path.stat()
                            new_files.append(file_path)
                        except (OSError, IOError):
                            # File still being written
                            pass
                
                return new_files
                
            except Exception as e:
                self.logger.error(f'Error checking drop folder: {e}')
                return []
        
        return []  # Watchdog mode handles events directly
    
    def process_file(self, source: Path) -> Optional[Path]:
        """
        Process a dropped file.
        
        Args:
            source: Path to the source file
            
        Returns:
            Path to the created action file, or None if failed
        """
        try:
            # Skip if already processed
            if source in self.processed_files:
                return None
            
            # Skip metadata files
            if source.suffix == '.meta.json':
                return None
            
            # Generate destination path
            dest_name = f'FILE_{source.name}'
            dest = self.needs_action / dest_name
            
            # Copy file
            shutil.copy2(source, dest)
            self.logger.info(f'Copied {source.name} to Needs_Action')
            
            # Create metadata file
            metadata = self.create_action_file({
                'source': source,
                'destination': dest,
                'filename': source.name
            })
            
            # Mark as processed
            self.processed_files.add(source)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f'Error processing file {source}: {e}')
            return None
    
    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a markdown action file for the dropped file.
        
        Args:
            item: Dictionary containing file information
            
        Returns:
            Path to the created metadata file
        """
        try:
            source = item['source']
            dest = item['destination']
            filename = item['filename']
            
            # Get file info
            file_size = source.stat().st_size
            modified_time = datetime.fromtimestamp(source.stat().st_mtime)
            
            # Create metadata content
            content = f'''---
type: file_drop
original_name: {filename}
size: {file_size}
size_human: {self._format_size(file_size)}
received: {datetime.now().isoformat()}
modified: {modified_time.isoformat()}
status: pending
priority: normal
---

# File Dropped for Processing

## File Information

- **Original Name**: {filename}
- **Size**: {self._format_size(file_size)}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Last Modified**: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}

## Location

- **Action File**: `{dest.name}`
- **Vault**: `Needs_Action/`

## Suggested Actions

- [ ] Review file contents
- [ ] Categorize file type
- [ ] Process or take action
- [ ] Move to appropriate folder
- [ ] Mark as done

## Notes

*Add notes about processing this file*

---
*Generated by FileSystemWatcher v0.1*
'''
            
            # Write metadata file
            meta_path = dest.with_suffix('.md')
            meta_path.write_text(content)
            
            self.logger.info(f'Created metadata file: {meta_path.name}')
            
            return meta_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human-readable size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'
    
    def run(self) -> None:
        """
        Main run loop with watchdog support.
        """
        if WATCHDOG_AVAILABLE:
            self._run_watchdog_mode()
        else:
            self._run_poll_mode()
    
    def _run_watchdog_mode(self) -> None:
        """
        Run using watchdog library for real-time file monitoring.
        """
        self.logger.info('Starting FileSystemWatcher (watchdog mode)')
        
        event_handler = DropFolderHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        self.logger.info(f'Watching folder: {self.drop_folder}')
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Stopping FileSystemWatcher')
            observer.stop()
        
        observer.join()
    
    def _run_poll_mode(self) -> None:
        """
        Run in poll mode (fallback when watchdog is not available).
        """
        self.logger.info('Starting FileSystemWatcher (poll mode)')
        super().run()


def main():
    """
    Entry point for running the file system watcher.
    """
    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path> [drop_folder]")
        print("\nExample:")
        print("  python filesystem_watcher.py /path/to/AI_Employee_Vault")
        print("  python filesystem_watcher.py /path/to/AI_Employee_Vault /path/to/Drop_Folder")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    drop_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate vault path
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Create and run watcher
    watcher = FileSystemWatcher(vault_path, drop_folder)
    watcher.run()


if __name__ == '__main__':
    main()
