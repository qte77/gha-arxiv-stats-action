"""Tests for env var validation (#11)."""

import pytest

from src.validation import validate_env


def test_validate_env_accepts_valid_config():
    """Valid config should not raise."""
    env = {
        "OUT_DIR": "./data",
        "START_RESULT": "0",
        "RESULT_COUNT": "199",
        "MAX_RESULTS_PER_QUERY": "100",
        "TOPICS": "cat:cs.AI",
        "INCLUDE_CITATIONS": "false",
    }
    validate_env(env)


def test_validate_env_rejects_path_traversal():
    """OUT_DIR with .. should raise ValueError."""
    env = {"OUT_DIR": "../../../etc", "TOPICS": "cat:cs.AI"}
    with pytest.raises(ValueError, match="OUT_DIR"):
        validate_env(env)


def test_validate_env_rejects_non_integer_start():
    """Non-integer START_RESULT should raise ValueError."""
    env = {"OUT_DIR": "./data", "TOPICS": "cat:cs.AI", "START_RESULT": "abc"}
    with pytest.raises(ValueError, match="START_RESULT"):
        validate_env(env)


def test_validate_env_rejects_negative_count():
    """Negative RESULT_COUNT should raise ValueError."""
    env = {"OUT_DIR": "./data", "TOPICS": "cat:cs.AI", "RESULT_COUNT": "-5"}
    with pytest.raises(ValueError, match="RESULT_COUNT"):
        validate_env(env)


def test_validate_env_rejects_empty_topics():
    """Empty TOPICS should raise ValueError."""
    env = {"OUT_DIR": "./data", "TOPICS": ""}
    with pytest.raises(ValueError, match="TOPICS"):
        validate_env(env)


def test_validate_env_rejects_invalid_citations_flag():
    """INCLUDE_CITATIONS must be true/false."""
    env = {"OUT_DIR": "./data", "TOPICS": "cat:cs.AI", "INCLUDE_CITATIONS": "yes"}
    with pytest.raises(ValueError, match="INCLUDE_CITATIONS"):
        validate_env(env)
