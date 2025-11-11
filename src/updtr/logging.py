"""Logging configuration using Loguru."""

import sys
from pathlib import Path

from loguru import logger

from .models.config import UpdtConfig


def setup_logging(config: UpdtConfig) -> None:
    """Configure logging based on configuration.

    Args:
        config: Application configuration
    """
    # Remove default handler
    logger.remove()

    # Setup format based on config
    if config.log_format == "jsonl":
        # JSONL format for structured logging - use Loguru's serialize option
        logger.add(
            sys.stderr,
            format="{message}",
            level=config.log_level,
            serialize=True,
        )
    else:
        # Text format for human-readable logs
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        # Add stdout handler
        logger.add(
            sys.stderr,
            format=format_string,
            level=config.log_level,
            colorize=True,
        )

    # Add file handler if configured
    if config.log_file:
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path),
            format="{message}" if config.log_format == "jsonl" else None,
            level=config.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            serialize=config.log_format == "jsonl",
        )

    logger.info("Logging configured", level=config.log_level, format=config.log_format)
