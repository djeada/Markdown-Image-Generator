#!/usr/bin/env python3
"""Full workflow demo: convert a markdown file to images.

Usage:
    python scripts/full_workflow.py [--theme THEME] [--renderer pil|playwright] [--font PATH] [--output DIR] [--preset NAME] [--template PATH] [MARKDOWN_FILE]

By default, uses demo/comprehensive_demo.md with the dark_modern theme
and the Playwright renderer (falls back to PIL if unavailable).
"""

import argparse
import logging
import sys
from pathlib import Path

# Ensure the project root is on the Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.converters.md_to_image.md_to_image import MarkdownToImageConverter
from src.input_output.image_saver import ImageSaver
from src.utils.config import Config
from src.utils.presets import get_preset, list_presets
from src.utils.theme_loader import apply_theme, list_themes

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_DEMO = PROJECT_ROOT / "demo" / "comprehensive_demo.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Full workflow: Markdown → themed images."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=str(DEFAULT_DEMO),
        help=f"Markdown file to convert (default: {DEFAULT_DEMO.name}).",
    )
    parser.add_argument(
        "-t", "--theme",
        default="dark_modern",
        help="Theme name to apply (default: dark_modern).",
    )
    parser.add_argument(
        "-r", "--renderer",
        choices=["pil", "playwright"],
        default="playwright",
        help="Rendering backend (default: playwright).",
    )
    parser.add_argument(
        "--font",
        default=None,
        help="Path to a .ttf/.otf font file for custom typography.",
    )
    parser.add_argument(
        "-o", "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output directory for images (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes and exit.",
    )
    parser.add_argument(
        "--preset",
        default=None,
        help="Social media preset name (overrides width/height). Use --list-presets to see options.",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available social media presets and exit.",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to a custom CSS template file (overrides --theme for Playwright renderer).",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not display images after generation.",
    )
    return parser.parse_args()


def _build_renderer(args: argparse.Namespace):
    """Construct the appropriate renderer from CLI args."""
    if args.renderer == "pil":
        from src.rendering.pil_renderer import PilRenderer
        return PilRenderer()

    # Resolve preset dimensions
    preset_width = None
    preset_height = None
    if args.preset:
        preset = get_preset(args.preset)
        preset_width = preset["width"]
        preset_height = preset["height"]
        logger.info("Using preset '%s' (%d×%d)", args.preset, preset_width, preset_height)

    # Playwright (default) — fall back to PIL if unavailable
    try:
        from src.rendering.playwright_renderer import PlaywrightRenderer
        return PlaywrightRenderer(
            theme=args.theme,
            font_path=args.font,
            width=preset_width,
            height=preset_height,
            custom_css=args.template,
        )
    except Exception:
        logger.warning("Playwright unavailable, falling back to PIL renderer")
        from src.rendering.pil_renderer import PilRenderer
        return PilRenderer()


def main() -> int:
    args = parse_args()

    if args.list_themes:
        print("Available themes:")
        for name in list_themes():
            print(f"  - {name}")
        # Also list CSS themes
        css_dir = PROJECT_ROOT / "themes" / "css"
        if css_dir.is_dir():
            css_themes = sorted(p.stem for p in css_dir.glob("*.css"))
            if css_themes:
                print("CSS themes (for Playwright renderer):")
                for name in css_themes:
                    print(f"  - {name}")
        return 0

    if args.list_presets:
        presets = list_presets()
        print("Available presets:")
        for p in presets:
            print(f"  {p['name']:25s} {p['width']}×{p['height']}  ({p['label']})")
        return 0

    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return 1

    # Apply JSON theme for PIL renderer
    if args.renderer == "pil":
        logger.info("Applying theme: %s", args.theme)
        try:
            apply_theme(Config(), args.theme)
        except Exception as e:
            logger.error("Failed to apply theme '%s': %s", args.theme, e)
            return 1

    # Build renderer
    renderer = _build_renderer(args)
    logger.info("Using renderer: %s", renderer.name)

    # Convert markdown to images
    logger.info("Converting: %s", input_path)
    converter = MarkdownToImageConverter(input_file=str(input_path), renderer=renderer)
    images = converter.convert()

    if not images:
        logger.error("No images were generated")
        return 1

    logger.info("Generated %d image(s)", len(images))

    # Save images
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    saver = ImageSaver(str(output_dir))
    saver.save_images(images)
    logger.info("Saved images to: %s", output_dir)

    # Show images
    if not args.no_show:
        for img in images:
            img.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())
