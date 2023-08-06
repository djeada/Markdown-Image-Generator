import time
from typing import List, Optional

from src.converters.md_to_text_block.md_to_text_block import MarkdownToTextBlock
from src.converters.md_to_title.md_to_title import MarkdownToTitleBlock
from src.input_output.markdown_reader import MarkdownReader
from src.image_generation.image_generator import ImageGenerator


class MarkdownToImageConverter:
    """
    Converts given markdown to images.

    Attributes:
    - input_file (str): Path to the input markdown file.
    - output_directory (Optional[str]): Directory to save the images. If not provided, images are displayed.
    """

    def __init__(self, input_file: str, output_directory: Optional[str] = None):
        self.input_file = input_file
        self.output_directory = output_directory
        self.markdown_reader = MarkdownReader()
        self.image_generator = ImageGenerator()
        self.md_to_title = MarkdownToTitleBlock()
        self.md_to_text = MarkdownToTextBlock()

    def interpret_title(self, content: str) -> str:
        """Interpret markdown content for title blocks."""
        return self.md_to_title.interpret(content)

    def interpret_normal_page(self, content: str) -> List[str]:
        """Interpret markdown content for normal text blocks."""
        return self.md_to_text.interpret(content)

    def interpret_final_page(self, content: str) -> List[str]:
        """Interpret markdown content for final text blocks."""
        return self.md_to_text.interpret(content)

    def handle_output(self, images: List[str]):
        """Handle image output either by saving or displaying them."""
        if self.output_directory:
            for idx, image in enumerate(images):
                image.save(f"{self.output_directory}/output{idx}.png")
        else:
            for image in images:
                image.show()

    def generate_page(self, interpret_method) -> None:
        content = self.markdown_reader.read(self.input_file)
        text_blocks = interpret_method(content)

        # Ensure text_blocks is a list for uniform handling
        if not isinstance(text_blocks, list):
            text_blocks = [text_blocks]

        for text_block in text_blocks:
            images = self.image_generator.generate_images(text_block)
            self.handle_output(images)
            time.sleep(0.1)

    def convert(self, page_type: str) -> None:
        """Convert markdown to images based on the specified page type."""
        page_types = {
            "intro": (self.interpret_title, "../resources/intro.png"),
            "normal": (self.interpret_normal_page, "../resources/page.png"),
            "final": (self.interpret_final_page, "../resources/final.png"),
        }

        if page_type not in page_types:
            print("Invalid page type specified.")
            return

        interpret_method, bg_image = page_types[page_type]
        self.image_generator.bg_image = bg_image
        self.generate_page(interpret_method)
