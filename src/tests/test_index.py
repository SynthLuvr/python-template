"""Tests for src.index."""

from __future__ import annotations

from src.index import greet


def test_greet() -> None:
    """greet() returns a greeting."""
    assert greet() == "hello"
