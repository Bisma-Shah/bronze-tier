"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
Watchers monitor external inputs and create actionable files in the Needs_Action folder.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Watchers run continuously, monitoring their respective data sources
    and creating markdown action files when new items are detected.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    def _setup_logging(self) -> None:
        """Setup logging to file and console."""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'watcher_{self.__class__.__name__}.log'
        
        # Create logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
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
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the data source for new items.
        
        Returns:
            List of new items to process
            
        Raises:
            Exception: If there's an error checking for updates
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file for the given item.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if creation failed
        """
        pass
    
    def run(self) -> None:
        """
        Main run loop. Continuously checks for updates and creates action files.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        
                    for item in items:
                        try:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created action file: {filepath.name}')
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                    
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: File prefix (e.g., 'EMAIL', 'WHATSAPP')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename with .md extension
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Sanitize unique_id for filesystem
        safe_id = ''.join(c for c in unique_id if c.isalnum() or c in '-_')
        return f'{prefix}_{safe_id}_{timestamp}.md'
    
    def create_metadata_file(self, action_file: Path, metadata: dict) -> None:
        """
        Create a companion metadata file for an action file.
        
        Args:
            action_file: Path to the action file
            metadata: Dictionary of metadata to store
        """
        meta_file = action_file.with_suffix('.meta.json')
        import json
        
        metadata['created_at'] = datetime.now().isoformat()
        metadata['action_file'] = str(action_file.name)
        
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
