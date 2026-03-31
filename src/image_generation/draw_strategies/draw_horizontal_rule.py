from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawHorizontalRule(DrawStrategy):
    """
    Drawing strategy for horizontal rules/dividers with modern styling.
    """

    def __init__(self, text_color: str) -> None:
        self.line_color = Config()["COLORS"].get("DIVIDER_COLOR", "#555555")
        self.accent_color = Config()["COLORS"]["HIGHLIGHT"]

    def draw(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        current_height: int,
    ) -> Tuple[Image.Image, int]:
        d = ImageDraw.Draw(img)
        left_margin = Config()["PAGE_LAYOUT"].get("LEFT_MARGIN", Config()["PAGE_LAYOUT"]["RIGHT_MARGIN"])
        right_margin = Config()["PAGE_LAYOUT"]["RIGHT_MARGIN"]
        img_width = img.size[0]
        
        # Add some vertical spacing
        current_height += 25
        
        # Draw a stylish horizontal line
        line_y = current_height
        line_start = left_margin + 50
        line_end = img_width - right_margin - 50
        line_height = 2
        
        # Draw gradient-like line (fade from edges)
        center_x = (line_start + line_end) // 2
        
        # Draw main line
        d.rectangle(
            [(line_start, line_y), (line_end, line_y + line_height)],
            fill=self.line_color
        )
        
        # Draw accent diamond in the center
        diamond_size = 10
        d.polygon(
            [
                (center_x, line_y - diamond_size),
                (center_x + diamond_size, line_y + line_height // 2),
                (center_x, line_y + line_height + diamond_size),
                (center_x - diamond_size, line_y + line_height // 2),
            ],
            fill=self.accent_color
        )
        
        # Draw small dots on either side of the diamond
        dot_radius = 3
        dot_offset = 30
        for offset in [-dot_offset, dot_offset]:
            d.ellipse(
                [
                    (center_x + offset - dot_radius, line_y - dot_radius + 1),
                    (center_x + offset + dot_radius, line_y + dot_radius + 1)
                ],
                fill=self.accent_color
            )
        
        current_height += 35
        
        return img, int(current_height)
