from PIL import Image, ImageDraw, ImageFont
from typing import List

from src.data.text_block import TextBlock


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
        images = []
        current_height = (
            0  # height on the current image where the next block will start
        )

        for block in blocks:
            try:
                style = self.block_styles[block.type]
                font = ImageFont.truetype(self.font_path, size=style["font_size"])
            except IOError:
                print(f"Error: The font file {self.font_path} wasn't found.")
                return
            except KeyError:
                print(f"Error: The block type {block.type} isn't supported.")
                return

            # calculate height of the text block
            block_height = 2 * 20  # we add 20 for padding

            if block_height + current_height > self.height or not images:
                # not enough space on the current image, or it's the first image
                if self.bg_image:
                    img = Image.open(self.bg_image).resize((self.width, self.height))
                else:
                    img = Image.new(
                        "RGB", (self.width, self.height), color=self.bg_color
                    )
                images.append(img)
                current_height = 0
            else:
                # enough space on the current image, get the last one
                img = images[-1]

            d = ImageDraw.Draw(img)
            d.text((10, current_height), block.data, fill=self.text_color, font=font)
            current_height += block_height  # update the height for the next block

        return images
