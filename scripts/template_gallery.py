#!/usr/bin/env python3
"""Render every CSS theme and template as a preview gallery.

Usage:
    python scripts/template_gallery.py [--output DIR] [--preset NAME] [--font PATH]

Generates a preview image for each available CSS theme and template
using a standard sample markdown file. Useful for choosing a style.
"""

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.converters.md_to_image.md_to_image import MarkdownToImageConverter
from src.input_output.image_saver import ImageSaver
from src.utils.presets import get_preset

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SAMPLE_MD = PROJECT_ROOT / "demo" / "comprehensive_demo.md"


def discover_css_files() -> list:
    """Find all CSS themes and templates."""
    found = []

    # Built-in themes
    themes_dir = PROJECT_ROOT / "themes" / "css"
    if themes_dir.is_dir():
        for css in sorted(themes_dir.glob("*.css")):
            found.append(("theme", css.stem, css))

    # User templates
    templates_dir = PROJECT_ROOT / "templates" / "examples"
    if templates_dir.is_dir():
        for css in sorted(templates_dir.glob("*.css")):
            found.append(("template", css.stem, css))

    return found


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate preview images for all themes and templates."
    )
    parser.add_argument(
        "-o", "--output",
        default=str(PROJECT_ROOT / "output" / "gallery"),
        help="Output directory for previews.",
    )
    parser.add_argument(
        "--preset", default="instagram-square",
        help="Preset dimensions (default: instagram-square).",
    )
    parser.add_argument("--font", default=None, help="Custom font path.")
    parser.add_argument(
        "--sample", default=str(SAMPLE_MD),
        help=f"Sample markdown file (default: {SAMPLE_MD.name}).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    preset = get_preset(args.preset)
    width, height = preset["width"], preset["height"]

    css_files = discover_css_files()
    if not css_files:
        logger.error("No CSS themes or templates found")
        return 1

    logger.info(
        "Found %d style(s). Rendering at %d×%d (%s)...",
        len(css_files), width, height, preset["label"],
    )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from src.rendering.playwright_renderer import PlaywrightRenderer
    except ImportError:
        logger.error("Playwright is required for the template gallery")
        return 1

    for kind, name, css_path in css_files:
        label = f"{kind}/{name}"
        logger.info("  Rendering: %s", label)

        renderer = PlaywrightRenderer(
            theme="dark_modern",  # fallback, overridden by custom_css
            font_path=args.font,
            width=width,
            height=height,
            custom_css=str(css_path),
        )

        converter = MarkdownToImageConverter(
            input_file=args.sample, renderer=renderer
        )
        images = converter.convert()

        if images:
            # Save first slide as the preview
            preview_path = output_dir / f"{kind}_{name}.png"
            images[0].save(str(preview_path))
            logger.info("    → %s (%d slide(s))", preview_path.name, len(images))

    logger.info("Gallery saved to: %s", output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
