"""
Directory management utilities
Ensures required directories exist for the application
"""

import os
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

def ensure_directories_exist(directories: List[str]) -> None:
    """
    Ensure that all required directories exist
    
    Args:
        directories: List of directory paths to create
    """
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            raise

def get_required_directories() -> List[str]:
    """
    Get list of required directories for the application
    
    Returns:
        List of directory paths that should exist
    """
    return [
        "data",
        "logs", 
        ".cache",
        ".cache/yf",  # Yahoo Finance cache
        "backups"
    ]

def initialize_app_directories() -> None:
    """
    Initialize all required application directories
    """
    directories = get_required_directories()
    ensure_directories_exist(directories)
    logger.info(f"Initialized {len(directories)} application directories")
