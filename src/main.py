import argparse
from src.converters.md_to_text_block import MarkdownToTextBlock
from src.input_output.markdown_reader import MarkdownReader
from src.image_generation.image_generator import ImageGenerator


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file to a series of images."
    )
    parser.add_argument("input_file", help="The input Markdown file.")
    parser.add_argument(
        "-o",
        "--output",
        dest="output_directory",
        help="The directory where the output images will be saved. If not provided, images will be displayed on the screen.",
    )
    args = parser.parse_args()

    # Instantiate your classes
    markdown_reader = MarkdownReader()
    image_generator = ImageGenerator()
    markdown_interpreter = MarkdownToTextBlock()

    # Read markdown file
    file_content = markdown_reader.read(args.input_file)

    # Interpret markdown lines into blocks
    text_blocks = markdown_interpreter.interpret(file_content)

    # Generate images from TextBlock objects
    for idx, text_block in enumerate(text_blocks):
        images = image_generator.generate_images(text_block)

        # Save images to the output directory if provided, otherwise display them
        if args.output_directory is not None:
            for idx, image in enumerate(images):
                image.save(f"{args.output_directory}/output{idx}.png")
        else:
            for image in images:
                image.show()


if __name__ == "__main__":
    main()
