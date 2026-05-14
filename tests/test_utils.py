"""Test utilities for running E2E tests."""
import subprocess
import sys
from pathlib import Path
from typing import Union

import pytest

from src.rendering.playwright_renderer import playwright_runtime_available


def run_as_module(
    *args: Union[str, Path],
    cwd: Union[str, Path, None] = None,
) -> subprocess.CompletedProcess:
    """Run the package as a module with given arguments.

    Args:
        *args: Arguments to pass to the module
        cwd: Working directory to run from

    Returns:
        CompletedProcess instance with return code and output
    """
    cmd = [sys.executable, "-m", "src.main"] + [str(arg) for arg in args]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result


_has_playwright = playwright_runtime_available()
requires_playwright = pytest.mark.skipif(
    not _has_playwright,
    reason="Playwright browsers not installed (run 'playwright install chromium')",
)
