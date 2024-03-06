import logging
import traceback
from typing import List, Dict, Optional
from PIL import Image, ImageFont, ImageDraw

from src.converters.block_to_background_image.block_image_factory import (
    BlockImageFactory,
)
from src.data.text_block import TextBlock, BlockType
from src.image_generation.draw_strategy import (
    DrawDefault,
    DrawTable,
    DrawCode,
)
from src.utils.config import Config

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self):
        self.width = Config()["PAGE_LAYOUT"]["IMAGE_WIDTH"]
        self.height = Config()["PAGE_LAYOUT"]["IMAGE_HEIGHT"]
        self.text_color = Config()["COLORS"]["TEXT"]
        self.font_path = Config()["PATHS"]["FONT"]

        self.block_styles = self.initialize_block_styles()

    def initialize_block_styles(self) -> Dict[BlockType, Dict]:
        height = self.height
        ## TODO: MAKE CONFIGURABLE
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
                "font_size": height // 40,
                "line_height": height // 30,
            },
            BlockType.TABLE: {
                "font_size": height // 30,
                "line_height": height // 28,
            },
            BlockType.CODE: {
                "font_size": height // 32,
                "line_height": height // 30,
            },
        }

    def draw_page_number(self, image: Image, page_num: int) -> None:
        # Define a position and style for the page number and draw it
        position = (self.width - 170, 120)
        draw = ImageDraw.Draw(image)
        page_num_str = f'{page_num + Config()["PAGE_LAYOUT"]["START_INDEX"]}'
        font_color = Config()["COLORS"]["PAGE_NUMBER_FONT"]
        font = self.get_font_for_block(BlockType.HEADER)
        if font:
            draw.text(position, page_num_str, fill=font_color, font=font)

    def generate_images(self, blocks: List[TextBlock]):
        images = []
        current_height = Config()["PAGE_LAYOUT"]["TOP_MARGIN"]
        current_page = 1  # start with page 1

        img = None
        for idx, block in enumerate(blocks):
            if img is None:
                img = BlockImageFactory.create_background_image(
                    block.type,
                    Config()["PAGE_LAYOUT"]["IMAGE_WIDTH"],
                    Config()["PAGE_LAYOUT"]["IMAGE_HEIGHT"],
                )

            if block.type != "title":
                self.draw_page_number(img, current_page)

            # Create a copy of the current image to draw on
            img_copy = img.copy()

            # Draw on the copy to check the new height
            block_height = self.draw_text_on_image(img_copy, block, current_height)

            # Check if the height difference is too large
            height_difference = block_height - current_height
            if height_difference > Config()["PAGE_LAYOUT"]["IMAGE_HEIGHT"] * 0.8:
                raise Exception("Block height difference exceeds allowable limit")

            if block_height > Config()["PAGE_LAYOUT"]["IMAGE_HEIGHT"] - Config()["PAGE_LAYOUT"]["BOTTOM_MARGIN"]:
                # If the block height exceeds the limit, reset current height and increment page
                current_height = Config()["PAGE_LAYOUT"]["TOP_MARGIN"]
                current_page += 1
                images.append(img)
                img = BlockImageFactory.create_background_image(
                    block.type,
                    Config()["PAGE_LAYOUT"]["IMAGE_WIDTH"],
                    Config()["PAGE_LAYOUT"]["IMAGE_HEIGHT"],
                )
                if block.type != "title":
                    self.draw_page_number(img, current_page)
                # Draw the block on the new image
                block_height = self.draw_text_on_image(img, block, current_height)
                current_height = int(block_height)
            else:
                # If the block height does not exceed the limit, redraw on the original image
                current_height = int(block_height)
                img = img_copy

        if img is not None:
            images.append(img)

        return images

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
            BlockType.TITLE: DrawDefault(self.text_color),
        }
        strategy = strategies.get(
            BlockType[block.type.upper()], strategies[BlockType.PARAGRAPH]
        )
        additional_height = (
            30 if BlockType[block.type.upper()] == BlockType.HEADER else 0
        )
        try:
            _, block_height = strategy.draw(
                img, block.data, font, current_height + additional_height
            )
            return block_height
        except Exception as e:
            error_message = (
                f"Error drawing text on image: {e}\n{traceback.format_exc()}"
            )
            logger.error(error_message)
            return 0
