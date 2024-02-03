import logging
from typing import List, Dict, Optional
from PIL import Image, ImageFont, ImageDraw
from enum import Enum, auto

from src.data.text_block import TextBlock
from src.image_generation.draw_strategy import (
    DrawDefault,
    DrawTable,
    DrawCode,
    DrawTitle,
)
from src.utils.config import Config

logger = logging.getLogger(__name__)


class BlockType(Enum):
    PARAGRAPH = auto()
    HEADER = auto()
    TABLE = auto()
    CODE = auto()
    BULLET = auto()
    TITLE = auto()


class ImageGenerator:
    def __init__(
        self,
        bg_image: Optional[str] = None,
        font_path: str = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ):
        self.bg_image = bg_image
        self.width = Config().get("IMAGE_WIDTH")
        self.height = Config().get("IMAGE_HEIGHT")
        self.bg_color = Config().get("BG_COLOR")
        self.text_color = Config().get("TEXT_COLOR")
        self.start_index = Config().get("START_INDEX")
        self.font_path = font_path
        self.block_styles = self.initialize_block_styles()

    def initialize_block_styles(self) -> Dict[BlockType, Dict]:
        height = self.height
        challenge_mode = Config().get("CHALLENGE")
        return {
            BlockType.TITLE: {
                "font_size": height // 12,
                "line_height": height // 22,
            },
            BlockType.HEADER: {
                "font_size": height // 20,
                "line_height": height // 18,
            },
            BlockType.PARAGRAPH: {
                "font_size": height // 35 if challenge_mode else height // 40,
                "line_height": height // 25 if challenge_mode else height // 30,
            },
            BlockType.TABLE: {
                "font_size": height // 30,
                "line_height": height // 28,
            },
            BlockType.CODE: {
                "font_size": height // 32,
                "line_height": height // 30,
            },
            BlockType.BULLET: {
                "font_size": height // 30,
                "line_height": height // 28,
            },
            # You can add additional block types here
        }

    def draw_page_number(self, image: Image, page_num: int) -> None:
        # Define a position and style for the page number and draw it
        position = (self.width - 165, 130)
        draw = ImageDraw.Draw(image)
        page_num_str = (
            f"?" if Config().get("CHALLENGE") else f"{page_num + self.start_index}"
        )
        font_color = Config().get("PAGE_NUMBER_FONT_COLOR")
        font = self.get_font_for_block(BlockType.HEADER)
        if font:
            draw.text(position, page_num_str, fill=font_color, font=font)

    def generate_images(self, blocks: List[TextBlock]):
        TOP_MARGIN = Config().get("PAGE_TOP_MARGIN")
        images = [self.create_new_image()]
        current_height = TOP_MARGIN
        current_page = 1  # start with page 1
        last_block_type = None  # To store the last block's type

        for idx, block in enumerate(blocks):
            img = images[-1]

            # Check if the block can fit on the current image
            # if current_height + block_height + TOP_MARGIN > self.height + 1111:
            if block.type != "title":  # Check the last block type here
                # Finalize the page number on the previous page before creating a new page
                self.draw_page_number(img, current_page)

            # Now draw the block on the appropriate image
            block_height = self.draw_text_on_image(img, block, current_height)
            current_height = block_height
            last_block_type = (
                block.type
            )  # Update the last block type at the end of loop

        if last_block_type != "title":  # Check the last block type here
            # Draw the page number on the last page
            self.draw_page_number(images[-1], current_page)

        return images

    def create_new_image(self) -> Image:
        if self.bg_image:
            return Image.open(self.bg_image).resize((self.width, self.height))
        else:
            return Image.new("RGB", (self.width, self.height), color=self.bg_color)

    def get_font_for_block(
        self, block_type: BlockType
    ) -> Optional[ImageFont.ImageFont]:
        try:
            style = self.block_styles.get(
                block_type, self.block_styles[BlockType.PARAGRAPH]
            )
            return ImageFont.truetype(self.font_path, size=style["font_size"])
        except IOError as e:
            logger.error(f"Error: The font file {self.font_path} wasn't found. {e}")
        except KeyError as e:
            logger.error(f"Error: The block type {block_type} isn't supported. {e}")

        return None

    def draw_text_on_image(
        self, img: Image, block: TextBlock, current_height: int
    ) -> int:
        font = self.get_font_for_block(BlockType[block.type.upper()])
        if not font:
            return 0

        strategies = {
            BlockType.PARAGRAPH: DrawDefault(self.text_color),
            BlockType.TABLE: DrawTable(self.text_color),
            BlockType.CODE: DrawCode(),
            BlockType.BULLET: DrawDefault(self.text_color),
            BlockType.TITLE: DrawTitle(self.text_color),
        }
        strategy = strategies.get(
            BlockType[block.type.upper()], strategies[BlockType.PARAGRAPH]
        )
        try:
            _, block_height = strategy.draw(img, block.data, font, current_height)
            return block_height
        except Exception as e:
            logger.error(f"Error drawing text on image: {e}")
            return 0
