"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path

from rich.logging import RichHandler

from videotranslator.config import settings


def setup_logger(name: str = "videotranslator") -> logging.Logger:
    """
    Set up a logger with Rich handler for beautiful terminal output.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(settings.log_level)

    # Rich handler for beautiful console output
    console_handler = RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        show_time=True,
        show_path=True,
    )
    console_handler.setLevel(settings.log_level)

    # Formatter
    formatter = logging.Formatter(
        "%(message)s",
        datefmt="[%X]",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logger()
