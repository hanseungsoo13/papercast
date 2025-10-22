"""Pytest configuration and fixtures.

This file contains shared fixtures and configuration for all tests.
"""

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-contract-tests",
        action="store_true",
        default=False,
        help="Run contract tests that make real API calls (or use real API mocks)"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "contract: Contract tests for external APIs"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle custom markers."""
    if config.getoption("--run-contract-tests"):
        # Run contract tests
        return
    
    # Skip contract tests by default
    skip_contract = pytest.mark.skip(reason="need --run-contract-tests option to run")
    for item in items:
        if "contract" in item.keywords:
            item.add_marker(skip_contract)


