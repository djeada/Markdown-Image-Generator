import argparse
from src.converters.md_to_text_block import MarkdownToTextBlock
from src.converters.md_to_title import MarkdownToTitleBlock
from src.input_output.markdown_reader import MarkdownReader
from src.image_generation.image_generator import ImageGenerator


class MarkdownToImageConverter:
    def __init__(self, input_file, output_directory=None):
        self.input_file = input_file
        self.output_directory = output_directory
        self.markdown_reader = MarkdownReader()
        self.image_generator = ImageGenerator()

    def interpret_title(self, content):
        return MarkdownToTitleBlock().interpret(content)

    def interpret_normal_page(self, content):
        return MarkdownToTextBlock().interpret(content)

    def interpret_final_page(self, content):
        return MarkdownToTextBlock().interpret(content)

    def handle_output(self, images):
        if self.output_directory is not None:
            for idx, image in enumerate(images):
                image.save(f"{self.output_directory}/output{idx}.png")
        else:
            for image in images:
                image.show()

    def generate_title_page(self):
        content = self.markdown_reader.read(self.input_file)
        text_block = self.interpret_title(content)
        images = self.image_generator.generate_images([text_block])
        self.handle_output(images)

    def generate_normal_page(self):
        content = self.markdown_reader.read(self.input_file)
        text_blocks = self.interpret_normal_page(content)
        for text_block in text_blocks:
            images = self.image_generator.generate_images(text_block)
            self.handle_output(images)

    def generate_final_page(self):
        content = self.markdown_reader.read(self.input_file)
        text_block = self.interpret_final_page(content)
        images = self.image_generator.generate_images([text_block])
        self.handle_output(images)

    def convert(self, page_type):
        if page_type == "intro":
            self.image_generator.bg_image = "../resources/intro.png"
            self.generate_title_page()
        elif page_type == "normal":
            self.image_generator.bg_image = "../resources/page.png"
            self.generate_normal_page()
        elif page_type == "final":
            self.image_generator.bg_image = "../resources/final.png"
            self.generate_final_page()
        else:
            print("Invalid page type specified.")


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
