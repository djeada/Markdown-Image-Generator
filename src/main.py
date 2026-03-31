import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from src.converters.md_to_image.md_to_image import MarkdownToImageConverter
from src.converters.batch_converter import BatchConverter
from src.input_output.image_saver import ImageSaver
from src.utils.config import Config
from src.utils.exceptions import MarkdownImageGeneratorError
from src.utils.presets import get_preset, list_presets
from src.utils.theme_loader import apply_theme, list_themes

VERSION = "0.1.0"
logger = logging.getLogger(__name__)


class CommandLineInterface:
    def __init__(self) -> None:
        parser = self.create_parser()
        self.args = parser.parse_args()

        # Handle --list-themes / --list-presets before requiring input_file
        if self.args.list_themes or self.args.list_presets:
            return

        # Validate input file/directory exists
        if self.args.input_file is None:
            parser.error("input_file is required (unless using --list-themes or --list-presets).")
        if self.args.batch:
            if not Path(self.args.input_file).is_dir():
                parser.error(f"--batch requires a directory, not a file: {self.args.input_file}")
        else:
            if not Path(self.args.input_file).exists():
                parser.error(f"Input file does not exist: {self.args.input_file}")

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Convert a Markdown file to a series of images."
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"Markdown Image Generator v{VERSION}",
            help="Show program's version number and exit",
        )
        parser.add_argument(
            "input_file",
            nargs="?",
            default=None,
            help="The input Markdown file.",
        )
        parser.add_argument(
            "-o",
            "--output",
            dest="output_directory",
            help="The directory where the output images will be saved. "
            "If not provided, images will be displayed on the screen, "
            "but not saved.",
            required=False,
        )
        parser.add_argument(
            "-c",
            "--config",
            dest="config_path",
            help="Path to the configuration file.",
            required=False,
        )
        parser.add_argument(
            "-t",
            "--theme",
            dest="theme",
            help="Theme name to apply (e.g. dark_modern, light_professional, vibrant_creative).",
            required=False,
        )
        parser.add_argument(
            "--list-themes",
            dest="list_themes",
            action="store_true",
            help="List available themes and exit.",
        )
        parser.add_argument(
            "--no-show",
            dest="no_show",
            action="store_true",
            help="Do not display the images on the screen.",
        )
        parser.add_argument(
            "-r",
            "--renderer",
            dest="renderer",
            choices=["playwright", "pil"],
            default="playwright",
            help="Rendering backend: 'playwright' (default, CSS-based) or 'pil' (legacy PIL).",
        )
        parser.add_argument(
            "-f",
            "--font",
            dest="font_path",
            help="Path to a .ttf/.otf font file for custom font rendering.",
            required=False,
        )
        parser.add_argument(
            "--preset",
            dest="preset",
            help="Social media preset name (overrides width/height). Use --list-presets to see options.",
            required=False,
        )
        parser.add_argument(
            "--list-presets",
            dest="list_presets",
            action="store_true",
            help="List available social media presets and exit.",
        )
        parser.add_argument(
            "--template",
            dest="template",
            help="Path to a custom CSS template file (overrides --theme for Playwright renderer).",
            required=False,
        )
        parser.add_argument(
            "--batch",
            dest="batch",
            action="store_true",
            help="Treat input as a directory and convert all .md files.",
        )
        parser.add_argument(
            "--recursive",
            dest="recursive",
            action="store_true",
            help="With --batch, search subdirectories recursively.",
        )
        return parser


def main() -> int:
    cli = CommandLineInterface()

    # Handle --list-themes
    if cli.args.list_themes:
        themes = list_themes()
        if themes:
            print("Available themes:")
            for name in themes:
                print(f"  - {name}")
        else:
            print("No themes found.")
        return 0

    # Handle --list-presets
    if cli.args.list_presets:
        presets = list_presets()
        print("Available presets:")
        for p in presets:
            print(f"  {p['name']:25s} {p['width']}×{p['height']}  ({p['label']})")
        return 0

    if cli.args.input_file is None:
        print("Error: input_file is required (unless using --list-themes or --list-presets).", file=sys.stderr)
        return 1

    if cli.args.config_path:
        Config().init_config(path=Path(cli.args.config_path))

    if cli.args.theme:
        try:
            apply_theme(Config(), cli.args.theme)
        except MarkdownImageGeneratorError as e:
            logger.error("Failed to apply theme: %s", e)
            return 1

    # Resolve preset dimensions
    preset_width = None
    preset_height = None
    if cli.args.preset:
        try:
            preset = get_preset(cli.args.preset)
        except KeyError as e:
            logger.error("%s", e)
            return 1
        preset_width = preset["width"]
        preset_height = preset["height"]
        logger.info("Using preset '%s' (%d×%d)", cli.args.preset, preset_width, preset_height)

    # Build renderer
    renderer = None
    if cli.args.renderer == "pil":
        from src.rendering.pil_renderer import PilRenderer
        renderer = PilRenderer()
    else:
        from src.rendering.playwright_renderer import PlaywrightRenderer
        renderer = PlaywrightRenderer(
            theme=cli.args.theme,
            font_path=cli.args.font_path,
            width=preset_width,
            height=preset_height,
            custom_css=cli.args.template,
        )

    # Batch mode
    if cli.args.batch:
        batch = BatchConverter(renderer=renderer, output_dir=cli.args.output_directory or "output")
        try:
            results = batch.convert_directory(
                cli.args.input_file,
                pattern="*.md",
                recursive=cli.args.recursive,
            )
        except (MarkdownImageGeneratorError, NotADirectoryError) as e:
            logger.error("Batch conversion failed: %s", e)
            return 1

        if not results:
            logger.error("No images were generated")
            return 1

        # Save images — use already-converted results
        if cli.args.output_directory:
            dest = Path(cli.args.output_directory)
            dest.mkdir(parents=True, exist_ok=True)
            for filepath, images in results.items():
                stem = Path(filepath).stem
                sub_dir = dest / stem
                sub_dir.mkdir(parents=True, exist_ok=True)
                saver = ImageSaver(str(sub_dir))
                saver.save_images(images)
                logger.info("Saved %d image(s) → %s", len(images), sub_dir)
        if not cli.args.no_show:
            for images in results.values():
                for img in images:
                    img.show()
        return 0

    # Single-file mode
    try:
        converter = MarkdownToImageConverter(
            input_file=cli.args.input_file,
            renderer=renderer,
        )
        images = converter.convert()
    except MarkdownImageGeneratorError as e:
        logger.error("Failed to generate images: %s", e)
        return 1
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return 1

    if not images:
        logger.error("No images were generated")
        return 1

    if cli.args.output_directory:
        Path(cli.args.output_directory).mkdir(parents=True, exist_ok=True)
        image_saver = ImageSaver(cli.args.output_directory)
        image_saver.save_images(images)

    if not cli.args.no_show:
        for image in images:
            image.show()

    return 0


if __name__ == "__main__":
    main()
