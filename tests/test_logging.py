"""Tests for logging configuration."""

import pytest
from pathlib import Path
from updt.logging import setup_logging
from updt.models.config import UpdtConfig


def test_setup_logging_text_format():
    """Test logging setup with text format."""
    config = UpdtConfig(log_format="text", log_level="INFO")
    logger = setup_logging(config)
    assert logger is not None


def test_setup_logging_jsonl_format():
    """Test logging setup with JSONL format."""
    config = UpdtConfig(log_format="jsonl", log_level="DEBUG")
    logger = setup_logging(config)
    assert logger is not None


def test_setup_logging_debug_level():
    """Test logging setup with DEBUG level."""
    config = UpdtConfig(log_level="DEBUG")
    logger = setup_logging(config)
    assert logger is not None


def test_setup_logging_warning_level():
    """Test logging setup with WARNING level."""
    config = UpdtConfig(log_level="WARNING")
    logger = setup_logging(config)
    assert logger is not None


def test_setup_logging_error_level():
    """Test logging setup with ERROR level."""
    config = UpdtConfig(log_level="ERROR")
    logger = setup_logging(config)
    assert logger is not None
