from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawHeader(DrawStrategy):
    """Drawing strategy for headers with accent styling."""
    
    def __init__(self, text_color: str) -> None:
        self.text_color = text_color
        self.header_color = Config()["COLORS"].get("HEADER_COLOR", "#00d4ff")
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
        
        # Draw accent line before header
        accent_width = 4
        accent_height = font.font.height
        d.rectangle(
            [
                (left_margin - 20, current_height),
                (left_margin - 20 + accent_width, current_height + accent_height)
            ],
            fill=self.accent_color
        )
        
        # Draw header text
        d.text((left_margin, current_height), text, fill=self.header_color, font=font)
        
        current_height += int(font.font.height * 1.8)
        
        return img, current_height
