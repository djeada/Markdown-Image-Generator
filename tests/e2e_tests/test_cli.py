import os
import pytest
from pathlib import Path
from tests.test_utils import run_as_module

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.timeout(10)
]

def test_version_flag():
    """Test that --version flag works"""
    result = run_as_module("--version")
    assert result.returncode == 0
    assert "Markdown Image Generator" in result.stdout

def test_help_flag():
    """Test that --help flag works"""
    result = run_as_module("--help")
    assert result.returncode == 0
    assert "Convert a Markdown file to a series of images" in result.stdout

def test_missing_input_file():
    """Test that the program fails when input file is missing"""
    result = run_as_module("nonexistent.md")
    assert result.returncode != 0
    assert "Input file does not exist" in result.stderr

def test_basic_markdown_conversion(temp_markdown_file, tmp_path):
    """Test basic markdown to image conversion end-to-end"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Get default test config path
    test_config = Path(__file__).parent / "test_config.json"
    
    # Run conversion
    result = run_as_module(
        str(temp_markdown_file),
        "-o", str(output_dir),
        "-c", str(test_config),
        "--no-show"
    )
    print(f"\nstdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    assert result.returncode == 0
    
    # Verify output files were created
    output_files = list(output_dir.glob("*.png"))
    assert len(output_files) > 0, "No output images were generated"
    
    # Verify image files are valid
    for img_path in output_files:
        assert img_path.stat().st_size > 0, f"Image file {img_path} is empty"

def test_config_file_usage(temp_markdown_file, tmp_path):
    """Test using a custom config file end-to-end"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create test config
    config_file = tmp_path / "test_config.json"
    config_file.write_text("""{
        "PATHS": {
            "DEFAULT_PAGE": "../resources/page.png",
            "TITLE_PAGE": "../resources/intro.png",
            "FINAL_PAGE": "../resources/final.png",
            "QUESTION_PAGE": "../resources/challenge.png",
            "FONT": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        },
        "PAGE_LAYOUT": {
            "TOP_MARGIN": 200,
            "RIGHT_MARGIN": 60,
            "IMAGE_WIDTH": 1080,
            "IMAGE_HEIGHT": 1080,
            "BOTTOM_MARGIN": 250,
            "CHAR_WIDTH": 15,
            "DEFAULT_LINE_HEIGHT": 30,
            "LIST_LINE_HEIGHT": 20,
            "START_INDEX": 0
        },
        "COLORS": {
            "PAGE_NUMBER_FONT": "#292929",
            "TEXT": "#FFFFFF",
            "BACKGROUND": "#000000",
            "HIGHLIGHT": "#ffab00"
        },
        "CODE_BLOCK": {
            "SCALE_FACTOR": 2,
            "BACKGROUND": "#000000",
            "RADIUS": 20,
            "TOP_PADDING": 50
        },
        "TABLE": {
            "SCALE_FACTOR": 1,
            "FOREGROUND": "#FFFFFF",
            "BACKGROUND": "#292929",
            "HIGHLIGHT": "#ffab00",
            "HEADER_BG_COLOR": "#8c52ff",
            "HEADER_FG_COLOR": "#000000",
            "HEIGHT": 8
        }
    }""")
    
    # Run conversion with config
    result = run_as_module(
        str(temp_markdown_file),
        "-o", str(output_dir),
        "-c", str(config_file),
        "--no-show"
    )
    assert result.returncode == 0
    
    # Verify output
    output_files = list(output_dir.glob("*.png"))
    assert len(output_files) > 0, "No output images were generated"
    
    # Verify image dimensions match config
    from PIL import Image
    img = Image.open(output_files[0])
    assert img.width == 1080, f"Image width does not match config: {img.width}"
    assert img.height == 1080, f"Image height does not match config: {img.height}"
