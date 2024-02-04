import logging
from typing import List, Optional

from src.converters.md_to_text_block.md_to_text_block import MarkdownToTextBlock
from src.input_output.markdown_reader import MarkdownReader
from src.image_generation.image_generator import ImageGenerator
from PIL import Image

logger = logging.getLogger(__name__)


class MarkdownToImageConverter:
    """
    Converts given markdown to images.
    """

    def __init__(
        self,
        input_file: str,
        markdown_reader: Optional[MarkdownReader] = None,
        image_generator: Optional[ImageGenerator] = None,
    ):
        self.input_file = input_file
        self.markdown_reader = markdown_reader or MarkdownReader()
        self.image_generator = image_generator or ImageGenerator()
        self.md_to_text = MarkdownToTextBlock()

    def convert(self) -> Optional[List[Image.Image]]:
        """
        Convert markdown to images based on the specified page type.
        """

        try:
            images = []
            content = self.markdown_reader.read(self.input_file)
            text_blocks = self.md_to_text.run(content)
            for text_block in text_blocks:
                images.extend(self.image_generator.generate_images(text_block))
            return images
        except Exception as e:
            logger.error(f"Error generating page: {e}", exc_info=True)
            return None
