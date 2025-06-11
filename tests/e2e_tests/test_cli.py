import os
import sys
import pytest
from pathlib import Path
from src.main import main, CommandLineInterface

pytestmark = pytest.mark.e2e  # Mark all tests in this module as E2E tests

@pytest.fixture
def run_cli(monkeypatch):
    """Fixture to run the CLI with given arguments"""
    def _run_cli(args):
        monkeypatch.setattr(sys, 'argv', ['md-image-generator'] + args)
        try:
            cli = CommandLineInterface()
            return cli.args
        except SystemExit as e:
            return e.code
    return _run_cli

def test_version_flag(run_cli):
    """Test that --version flag works."""
    result = run_cli(['--version'])
    assert result == 0  # SystemExit(0) for version display

def test_help_flag(run_cli):
    """Test that --help flag works."""
    result = run_cli(['--help'])
    assert result == 0  # SystemExit(0) for help display

def test_missing_input_file(run_cli):
    """Test that the program fails gracefully when input file is missing."""
    args = run_cli(['nonexistent.md'])
    assert isinstance(args, int) and args != 0

def test_basic_markdown_conversion(run_cli, temp_markdown_file, tmp_path):
    """Test basic markdown to image conversion with a simple file."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    args = run_cli([str(temp_markdown_file), '-o', str(output_dir), '--no-show'])
    assert not isinstance(args, int)  # Should not be an error code
    assert args.input_file == str(temp_markdown_file)
    assert args.output_directory == str(output_dir)
    assert args.no_show is True

    # Verify that output directory exists
    assert output_dir.exists()

def test_config_file_usage(run_cli, temp_markdown_file, tmp_path):
    """Test using a custom config file."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create a test config file
    config_file = tmp_path / "test_config.json"
    config_file.write_text("""{
        "PAGE_LAYOUT": {
            "TOP_MARGIN": 200,
            "RIGHT_MARGIN": 60,
            "IMAGE_WIDTH": 1080,
            "IMAGE_HEIGHT": 1080
        }
    }""")
    
    args = run_cli([
        str(temp_markdown_file),
        '-o', str(output_dir),
        '-c', str(config_file),
        '--no-show'
    ])
    
    assert not isinstance(args, int)  # Should not be an error code
    assert args.config_path == str(config_file)
    assert args.output_directory == str(output_dir)
