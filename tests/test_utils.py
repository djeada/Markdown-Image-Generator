"""Test utilities for running E2E tests."""
import subprocess
from pathlib import Path
from typing import Union

import pytest


def run_as_module(
    *args: Union[str, Path],
    cwd: Union[str, Path, None] = None
) -> subprocess.CompletedProcess:
    """Run the package as a module with given arguments.
    
    Args:
        *args: Arguments to pass to the module
        cwd: Working directory to run from
        
    Returns:
        CompletedProcess instance with return code and output
    """
    cmd = ["python", "-m", "src.main"] + [str(arg) for arg in args]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result


def playwright_browsers_available() -> bool:
    """Return True only if Playwright *and* a Chromium browser are installed.

    This checks that the ``playwright`` package can be imported **and** that
    ``chromium.launch()`` succeeds (i.e. the browser binary exists).
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:  # ImportError, browser-not-found, etc.
        return False


_has_playwright = playwright_browsers_available()
requires_playwright = pytest.mark.skipif(
    not _has_playwright,
    reason="Playwright browsers not installed (run 'playwright install chromium')",
)
