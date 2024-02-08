import itertools
import logging
from typing import List, Optional
from PIL import Image

from src.converters.md_to_text_block.md_to_text_block import MarkdownToTextBlock
from src.input_output.markdown_reader import MarkdownReader
from src.image_generation.image_generator import ImageGenerator

logger = logging.getLogger(__name__)


class MarkdownToImageConverter:
    """
    Converts given markdown to images.
    """

    def __init__(self, input_file: str) -> None:
        self.input_file = input_file

    def convert(self) -> Optional[List[Image.Image]]:
        """
        Convert markdown to images based on the specified page type.
        """
        try:
            markdown_reader = MarkdownReader()
            image_generator = ImageGenerator()
            md_to_text = MarkdownToTextBlock()

            content = markdown_reader.read(self.input_file)
            if content is None:
                raise
            text_blocks = md_to_text.run(content)
            flatten_text_blocks = list(itertools.chain.from_iterable(text_blocks))

            return image_generator.generate_images(flatten_text_blocks)

        except Exception as e:
            logger.error(f"Error generating images: {e}", exc_info=True)
            return None
