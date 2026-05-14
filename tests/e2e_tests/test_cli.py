import os
import pytest
from pathlib import Path
from tests.test_utils import run_as_module, requires_playwright


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

@requires_playwright
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

@requires_playwright
def test_config_file_usage(temp_markdown_file, tmp_path):
    """Test using a custom config file end-to-end"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create test config
    config_file = tmp_path / "test_config.json"
    config_file.write_text("""{
        "PATHS": {
            "DEFAULT_PAGE": "resources/page.png",
            "TITLE_PAGE": "resources/intro.png",
            "FINAL_PAGE": "resources/final.png",
            "QUESTION_PAGE": "resources/page.png",
            "FONT": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        },
        "PAGE_LAYOUT": {
            "TOP_MARGIN": 200,
            "LEFT_MARGIN": 60,
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


def test_pil_renderer_conversion(temp_markdown_file, tmp_path):
    """Test conversion using the PIL renderer (does not require Playwright browsers)."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    test_config = Path(__file__).parent / "test_config.json"

    result = run_as_module(
        str(temp_markdown_file),
        "-o", str(output_dir),
        "-c", str(test_config),
        "--renderer", "pil",
        "--no-show",
    )
    assert result.returncode == 0

    output_files = list(output_dir.glob("*.png"))
    assert len(output_files) > 0, "No output images were generated"

    for img_path in output_files:
        assert img_path.stat().st_size > 0, f"Image file {img_path} is empty"


def test_list_themes():
    """Test that --list-themes flag works."""
    result = run_as_module("--list-themes")
    assert result.returncode == 0
    assert "Available themes" in result.stdout


def test_list_presets():
    """Test that --list-presets flag works."""
    result = run_as_module("--list-presets")
    assert result.returncode == 0
    assert "Available presets" in result.stdout
    assert "instagram" in result.stdout.lower()


@requires_playwright
def test_preset_flag(temp_markdown_file, tmp_path):
    """Test using a social media preset end-to-end."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = run_as_module(
        str(temp_markdown_file),
        "-o", str(output_dir),
        "--preset", "instagram-square",
        "--no-show",
    )
    assert result.returncode == 0

    output_files = list(output_dir.glob("*.png"))
    assert len(output_files) > 0, "No output images were generated"

    from PIL import Image
    img = Image.open(output_files[0])
    assert img.width == 1080
    assert img.height == 1080


@requires_playwright
def test_theme_flag(temp_markdown_file, tmp_path):
    """Test using a theme flag end-to-end."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = run_as_module(
        str(temp_markdown_file),
        "-o", str(output_dir),
        "--theme", "vibrant_creative",
        "--no-show",
    )
    assert result.returncode == 0

    output_files = list(output_dir.glob("*.png"))
    assert len(output_files) > 0, "No output images were generated"


def test_invalid_renderer_flag():
    """Test that an invalid renderer flag is rejected."""
    result = run_as_module("dummy.md", "--renderer", "nonexistent")
    assert result.returncode != 0


def test_invalid_preset_flag(temp_markdown_file, tmp_path):
    """Test that an invalid preset produces an error."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = run_as_module(
        str(temp_markdown_file),
        "-o", str(output_dir),
        "--preset", "nonexistent_preset",
        "--no-show",
    )
    assert result.returncode != 0


def test_invalid_config_fails_cleanly(tmp_path):
    """Test that invalid config exits cleanly with a validation error."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nBody\n")
    config_file = tmp_path / "bad_config.json"
    config_file.write_text("{}")

    result = run_as_module(
        str(md_file),
        "-c",
        str(config_file),
        "--no-show",
    )

    assert result.returncode != 0
    assert "Invalid configuration:" in result.stderr
