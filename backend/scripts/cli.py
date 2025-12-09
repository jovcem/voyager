#!/usr/bin/env python3
"""CLI entry point for Voyager scraper"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from src
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.cli.commands import cli

if __name__ == '__main__':
    cli()
