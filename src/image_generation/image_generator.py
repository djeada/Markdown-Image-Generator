from PIL import Image, ImageFont, ImageDraw
from typing import List


from src.data.text_block import TextBlock
from src.image_generation.draw_strategy import (
    DrawDefault,
    DrawTable,
    DrawCode,
    DrawList,
    DrawTitle,
)
from src.utils.config import Config


class ImageGenerator:
    def __init__(
        self,
        bg_image=None,
        width=Config.get_instance().get("IMAGE_WIDTH"),
        height=Config.get_instance().get("IMAGE_HEIGHT"),
        bg_color=Config.get_instance().get("BG_COLOR"),
        text_color=Config.get_instance().get("TEXT_COLOR"),
        font_path="/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        start_index=Config.get_instance().get("START_INDEX"),
    ):
        self.bg_image = bg_image
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_path = font_path
        self.start_index = start_index
        self.block_styles = {
            "title": {
                "font_size": int(self.height / 10),
                "line_height": int(self.height / 15),
            },
            "header": {
                "font_size": int(self.height / 30),
                "line_height": int(self.height / 25),
            },
            "paragraph": {
                "font_size": int(self.height / 40),
                "line_height": int(self.height / 35),
            },
        }

    def draw_page_number(self, image, page_num):
        # Define a position and style for the page number and draw it
        position = (self.width - 165, 130)  # this is just an example position
        draw = ImageDraw.Draw(image)
        draw.text(
            position,
            f"{page_num +    self.start_index }",
            fill=Config.get_instance().get("PAGE_NUMBER_FONT_COLOR"),
            font=self.get_font_for_block("header"),
        )

    def generate_images(self, blocks: List[TextBlock]):
        TOP_MARGIN = Config.get_instance().get("PAGE_TOP_MARGIN")
        images = [self.create_new_image()]
        current_height = TOP_MARGIN
        current_page = 1  # start with page 1

        for idx, block in enumerate(blocks):
            img = images[-1]

            # Draw on a temporary canvas to get the block height
            temp_canvas = self.create_new_image()
            block_height = self.draw_text_on_image(temp_canvas, block, TOP_MARGIN)

            # Check if the block can fit on the current image
            if current_height + block_height + TOP_MARGIN > self.height:
                if block.type != "title":
                    # Finalize the page number on the previous page before creating a new page
                    self.draw_page_number(img, current_page)

                img = self.create_new_image()
                images.append(img)
                current_height = TOP_MARGIN
                current_page += 1  # increment page number

            # Now draw the block on the appropriate image
            self.draw_text_on_image(img, block, current_height)
            current_height += block_height
        if block.type != "title":
            # Draw the page number on the last page
            self.draw_page_number(images[-1], current_page)

        return images

    def create_new_image(self):
        if self.bg_image:
            return Image.open(self.bg_image).resize((self.width, self.height))
        else:
            return Image.new("RGB", (self.width, self.height), color=self.bg_color)

    def get_font_for_block(self, block_type):
        try:
            style = self.block_styles.get(block_type, self.block_styles["paragraph"])
            return ImageFont.truetype(self.font_path, size=style["font_size"])
        except IOError:
            print(f"Error: The font file {self.font_path} wasn't found.")
            return None
        except KeyError:
            print(f"Error: The block type {block_type} isn't supported.")
            return None

    def draw_text_on_image(self, img, block, current_height):
        font = self.get_font_for_block(block.type)
        if not font:
            return

        strategies = {
            "default": DrawDefault(self.text_color),
            "table": DrawTable(self.text_color),
            "code": DrawCode(),
            "bullet": DrawList(self.text_color),
            "title": DrawTitle(self.text_color),
        }
        strategy = strategies.get(block.type, strategies["default"])
        try:
            _, block_height = strategy.draw(img, block.data, font, current_height)
            return block_height
        except:
            return 0
