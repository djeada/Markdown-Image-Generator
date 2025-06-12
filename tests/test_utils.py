"""Test utilities for running E2E tests."""
import subprocess
from pathlib import Path
from typing import List, Union

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
