import argparse
from src.converters.md_to_image.md_to_image import MarkdownToImageConverter
from src.input_output.image_saver import ImageSaver


class CommandLineInterface:
    def __init__(self):
        parser = self.create_parser()
        self.args = parser.parse_args()

    @staticmethod
    def create_parser():
        parser = argparse.ArgumentParser(
            description="Convert a Markdown file to a series of images."
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
        return parser


def main():
    cli = CommandLineInterface()
    converter = MarkdownToImageConverter(input_file=cli.args.input_file)
    images = converter.convert()
    image_saver = ImageSaver(cli.args.output_directory)
    image_saver.save_images(images)
    for image in images:
        image.show()


if __name__ == "__main__":
    main()
