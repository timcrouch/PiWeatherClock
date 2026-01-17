#!/usr/bin/env python3
"""
WeatherClock Pi - Main Entry Point

A dedicated weather and time display application for Raspberry Pi 5
with touchscreen support.

Usage:
    python main.py [--windowed] [--show-cursor] [--debug]
    
Options:
    --windowed      Run in windowed mode instead of fullscreen
    --show-cursor   Show the mouse cursor (hidden by default)
    --debug         Enable debug logging
"""

import sys
import argparse
import logging

from utils.logging_config import setup_logging
from utils.config import load_config
from gui.display import WeatherClockApp


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="WeatherClock Pi - Weather and time display for Raspberry Pi"
    )
    
    parser.add_argument(
        '--windowed', '-w',
        action='store_true',
        help='Run in windowed mode instead of fullscreen'
    )
    
    parser.add_argument(
        '--show-cursor', '-c',
        action='store_true',
        help='Show the mouse cursor'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--config', '-f',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=log_level, console=True)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("WeatherClock Pi Starting")
    logger.info("=" * 50)
    
    # Load configuration
    if args.config:
        from pathlib import Path
        config = load_config(Path(args.config))
    else:
        config = load_config()
    
    logger.info(f"Temperature unit: {config.display.temperature_unit}")
    logger.info(f"Time format: {config.display.time_format}")
    logger.info(f"Theme: {config.display.theme}")
    
    # Check for location
    if not config.location.is_configured():
        logger.info("Location not configured, will attempt auto-detection")
    else:
        logger.info(f"Location: {config.location.name} "
                   f"({config.location.latitude}, {config.location.longitude})")
    
    try:
        # Create and run application
        app = WeatherClockApp(
            config=config,
            fullscreen=not args.windowed,
            hide_cursor=not args.show_cursor
        )
        
        logger.info("Application initialized, starting main loop")
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
    
    logger.info("WeatherClock Pi stopped")


if __name__ == "__main__":
    main()
