import argparse
import logging
from pathlib import Path

from src.converters.md_to_image.md_to_image import MarkdownToImageConverter
from src.input_output.image_saver import ImageSaver
from src.utils.config import Config

VERSION = "0.1.0"
logger = logging.getLogger(__name__)


class CommandLineInterface:
    def __init__(self):
        parser = self.create_parser()
        self.args = parser.parse_args()

        # Validate input file exists
        if not Path(self.args.input_file).exists():
            parser.error(f"Input file does not exist: {self.args.input_file}")

    @staticmethod
    def create_parser():
        parser = argparse.ArgumentParser(
            description="Convert a Markdown file to a series of images."
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"Markdown Image Generator v{VERSION}",
            help="Show program's version number and exit",
        )
        parser.add_argument("input_file", help="The input Markdown file.")
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
            "--no-show",
            dest="no_show",
            action="store_true",
            help="Do not display the images on the screen.",
        )
        return parser


def main():
    cli = CommandLineInterface()

    if cli.args.config_path:
        Config().init_config(path=Path(cli.args.config_path))

    converter = MarkdownToImageConverter(input_file=cli.args.input_file)
    images = converter.convert()
    if images is None:
        logger.error("No image could be generated")
        return 1

    if cli.args.output_directory:
        image_saver = ImageSaver(cli.args.output_directory)
        image_saver.save_images(images)

    if not cli.args.no_show:
        for image in images:
            image.show()


if __name__ == "__main__":
    main()
