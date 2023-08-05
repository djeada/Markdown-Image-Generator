import textwrap

from PIL import Image, ImageDraw, ImageFont
from typing import List

from src.data.text_block import TextBlock
from src.image_generation.draw_strategy import DrawDefault, DrawTable, DrawCode

TOP_MARGIN = 20


class ImageGenerator:
    def __init__(
        self,
        bg_image=None,
        width=800,
        height=600,
        bg_color=(255, 255, 255),
        text_color=(0, 0, 0),
        font_path="/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ):
        self.bg_image = bg_image
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_path = font_path
        self.block_styles = {
            "header": {
                "font_size": int(self.height / 30),
                "line_height": int(self.height / 25),
            },
            "paragraph": {
                "font_size": int(self.height / 40),
                "line_height": int(self.height / 35),
            },
        }

    def generate_images(self, blocks: List[TextBlock]):
        images = [self.create_new_image()]
        current_height = TOP_MARGIN
        for block in blocks:
            img = images[-1]
            block_height = self.draw_text_on_image(img, block, current_height)
            current_height += block_height

            if 50 + current_height > self.height:
                current_height = TOP_MARGIN
                img = self.create_new_image()
                images.append(img)

        return images

    def create_new_image(self):
        if self.bg_image:
            return Image.open(self.bg_image).resize((self.width, self.height))
        else:
            return Image.new("RGB", (self.width, self.height), color=self.bg_color)

    def get_font_for_block(self, block):
        try:
            style = self.block_styles.get(block.type, self.block_styles["paragraph"])
            return ImageFont.truetype(self.font_path, size=style["font_size"])
        except IOError:
            print(f"Error: The font file {self.font_path} wasn't found.")
            return None
        except KeyError:
            print(f"Error: The block type {block.type} isn't supported.")
            return None

    def draw_text_on_image(self, img, block, current_height):
        font = self.get_font_for_block(block)
        if not font:
            return

        strategies = {
            "default": DrawDefault(self.text_color),
            "table": DrawTable(self.text_color),
            "code": DrawCode(),
        }
        strategy = strategies.get(block.type, strategies["default"])
        _, block_height = strategy.draw(img, block.data, font, current_height)
        return block_height
