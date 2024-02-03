import time
import logging
import traceback
from enum import Enum, auto
from typing import List, Optional, Callable, Union

from src.converters.md_to_text_block.md_to_text_block import MarkdownToTextBlock
from src.input_output.markdown_reader import MarkdownReader
from src.image_generation.image_generator import ImageGenerator

logger = logging.getLogger(__name__)


class PageType(Enum):
    INTRO = auto()
    NORMAL = auto()
    FINAL = auto()
    QUESTION = auto()


class MarkdownToImageConverter:
    """
    Converts given markdown to images.
    """

    PAGE_RESOURCES = {
        PageType.INTRO: "../resources/intro.png",
        PageType.NORMAL: "../resources/page.png",
        PageType.FINAL: "../resources/final.png",
        PageType.QUESTION: "../resources/challenge.png",
    }

    def __init__(
        self,
        input_file: str,
        output_directory: Optional[str] = None,
        markdown_reader: Optional[MarkdownReader] = None,
        image_generator: Optional[ImageGenerator] = None,
    ):
        self.input_file = input_file
        self.output_directory = output_directory
        self.markdown_reader = markdown_reader if markdown_reader else MarkdownReader()
        self.image_generator = image_generator if image_generator else ImageGenerator()
        self.md_to_title = MarkdownToTextBlock(is_title=True)
        self.md_to_text = MarkdownToTextBlock()

    def interpret_content(self, content: str, is_title: bool = False) -> List[str]:
        """
        Interpret markdown content for text blocks.
        """
        md_interpreter = self.md_to_title if is_title else self.md_to_text
        return md_interpreter.run(content)

    def handle_output(self, images: List[str]) -> None:
        """
        Handle image output either by saving or displaying them.
        """
        try:
            if self.output_directory:
                for idx, image in enumerate(images):
                    image.save(f"{self.output_directory}/output{idx}.png")
            else:
                for image in images:
                    image.show()
        except Exception as e:
            logger.error(f"Error handling output: {e}")

    def generate_page(self, interpret_method: Callable[[str], List[str]]) -> None:
        try:
            content = self.markdown_reader.read(self.input_file)
            text_blocks = interpret_method(content)
            text_blocks = (
                [text_blocks] if not isinstance(text_blocks, list) else text_blocks
            )

            for text_block in text_blocks:
                images = self.image_generator.generate_images(text_block)
                self.handle_output(images)
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error generating page: {e}\n{traceback.format_exc()}")

    def convert(self, page_type: Union[PageType, str]) -> None:
        """
        Convert markdown to images based on the specified page type.
        """
        if isinstance(page_type, str):
            try:
                page_type = PageType[page_type.upper()]
            except KeyError:
                logger.error(f"Invalid page type specified: {page_type}")
                return

        page_info = self.PAGE_RESOURCES.get(page_type)
        if not page_info:
            logger.error(f"Page type not supported: {page_type}")
            return

        bg_image = page_info
        is_title = page_type in [PageType.INTRO, PageType.FINAL, PageType.QUESTION]
        interpret_method = lambda content: self.interpret_content(
            content, is_title=is_title
        )

        self.image_generator.bg_image = bg_image
        self.generate_page(interpret_method)
