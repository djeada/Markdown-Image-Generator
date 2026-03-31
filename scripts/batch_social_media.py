#!/usr/bin/env python3
"""Batch convert a directory of markdown files for social media.

Usage:
    python scripts/batch_social_media.py [INPUT_DIR] [--preset NAME] [--theme THEME] [--template PATH] [--output DIR]

Examples:
    # Convert all demo files as Instagram posts
    python scripts/batch_social_media.py demo/ --preset instagram-square --theme dark_modern

    # Convert with a custom CSS template for LinkedIn
    python scripts/batch_social_media.py content/ --preset linkedin --template templates/examples/corporate_deck.css

    # Process recursively with custom font
    python scripts/batch_social_media.py posts/ --preset twitter --font /path/to/font.ttf --recursive
"""

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.converters.batch_converter import BatchConverter
from src.utils.presets import get_preset, list_presets

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch convert markdown files to social media images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets set image dimensions for common social platforms.
Run with --list-presets to see all options.

Each input .md file gets its own subdirectory in the output folder.
""",
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=str(PROJECT_ROOT / "demo"),
        help="Directory containing .md files (default: demo/).",
    )
    parser.add_argument(
        "--preset",
        default="instagram-square",
        help="Social media preset (default: instagram-square).",
    )
    parser.add_argument("--theme", default="dark_modern", help="CSS theme name.")
    parser.add_argument("--template", default=None, help="Path to custom CSS template file.")
    parser.add_argument("--font", default=None, help="Path to .ttf/.otf font file.")
    parser.add_argument("-o", "--output", default=str(PROJECT_ROOT / "output"), help="Output directory.")
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories.")
    parser.add_argument("--pattern", default="*.md", help="File pattern (default: *.md).")
    parser.add_argument("--list-presets", action="store_true", help="List presets and exit.")
    return parser.parse_args()


def build_renderer(args: argparse.Namespace):
    """Build a PlaywrightRenderer with preset dimensions."""
    preset = get_preset(args.preset)
    logger.info(
        "Preset: %s (%d×%d)", preset["label"], preset["width"], preset["height"]
    )

    try:
        from src.rendering.playwright_renderer import PlaywrightRenderer

        return PlaywrightRenderer(
            theme=args.theme,
            font_path=args.font,
            width=preset["width"],
            height=preset["height"],
            custom_css=args.template,
        )
    except Exception:
        logger.warning("Playwright unavailable, falling back to PIL")
        from src.rendering.pil_renderer import PilRenderer

        return PilRenderer()


def main() -> int:
    args = parse_args()

    if args.list_presets:
        print("Available presets:")
        for p in list_presets():
            print(f"  {p['name']:25s} {p['width']:>5}×{p['height']:<5} {p['label']}")
        return 0

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        logger.error("Not a directory: %s", input_dir)
        return 1

    renderer = build_renderer(args)
    batch = BatchConverter(renderer=renderer, output_dir=args.output)

    results = batch.convert_directory(
        str(input_dir), pattern=args.pattern, recursive=args.recursive
    )

    if not results:
        logger.error("No files found or no images generated")
        return 1

    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    total_images = 0
    for filepath, images in results.items():
        stem = Path(filepath).stem
        sub_dir = output_dir / stem
        sub_dir.mkdir(parents=True, exist_ok=True)

        from src.input_output.image_saver import ImageSaver

        saver = ImageSaver(str(sub_dir))
        saver.save_images(images)
        total_images += len(images)
        logger.info("  %s → %d image(s) in %s/", Path(filepath).name, len(images), sub_dir)

    logger.info("Done! %d file(s), %d total image(s) → %s", len(results), total_images, output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
