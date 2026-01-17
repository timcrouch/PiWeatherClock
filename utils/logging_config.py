"""
Logging configuration for WeatherClock Pi.

Sets up rotating file handler and console output.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_log_directory() -> Path:
    """Get the log directory path."""
    log_home = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/log"))
    return Path(log_home) / "weatherclock"


def setup_logging(level: int = logging.INFO, console: bool = True) -> None:
    """
    Configure application logging.
    
    Args:
        level: Logging level (default: INFO)
        console: Whether to also log to console (useful for development)
    """
    log_dir = get_log_directory()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "app.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up rotating file handler
    # Max 1MB per file, keep 7 backup files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,
        backupCount=7
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    
    # Optionally add console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized. Log file: {log_file}")
