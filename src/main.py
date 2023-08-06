import argparse

from src.converters.md_to_image.md_to_image import MarkdownToImageConverter


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file to a series of images."
    )
    parser.add_argument("input_file", help="The input Markdown file.")
    parser.add_argument(
        "-t",
        "--page_type",
        dest="page_type",
        choices=["intro", "normal", "final"],
        default="normal",
        help="Type of page: intro, normal, or final.",
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_directory",
        help="The directory where the output images will be saved. If not provided, images will be displayed on the screen.",
        required=False,
    )

    args = parser.parse_args()

    converter = MarkdownToImageConverter(args.input_file, args.output_directory)
    converter.convert(args.page_type)


if __name__ == "__main__":
    main()
