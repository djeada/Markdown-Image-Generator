import textwrap
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawNumberedList(DrawStrategy):
    """
    Drawing strategy for numbered/ordered lists with modern styling.
    """

    def __init__(self, text_color: str) -> None:
        self.text_color = text_color
        self.highlight_color = Config()["COLORS"]["HIGHLIGHT"]
        self.number_color = Config()["COLORS"].get("NUMBER_COLOR", self.highlight_color)

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
        number_indent = 30
        img_width = img.size[0]
        
        items = text.split("\n")
        char_per_line = (img_width - left_margin - number_indent - right_margin - 80) // font.getbbox("a")[2]
        
        for idx, item in enumerate(items, 1):
            if not item.strip():
                continue
            
            # Draw number in a circle with gradient-like effect
            number_str = str(idx)
            circle_radius = 14
            circle_x = left_margin + number_indent
            circle_y = current_height + font.font.height // 2
            
            # Draw outer ring
            d.ellipse(
                [
                    (circle_x - circle_radius - 2, circle_y - circle_radius - 2),
                    (circle_x + circle_radius + 2, circle_y + circle_radius + 2)
                ],
                fill=None,
                outline=self.number_color,
                width=1
            )
            
            # Draw circle background
            d.ellipse(
                [
                    (circle_x - circle_radius, circle_y - circle_radius),
                    (circle_x + circle_radius, circle_y + circle_radius)
                ],
                fill=self.number_color
            )
            
            # Draw number centered in circle
            try:
                number_font = ImageFont.truetype(Config()["PATHS"]["FONT"], size=font.size - 4)
            except (IOError, OSError):
                number_font = font
            
            # Get text bounding box for centering
            bbox = d.textbbox((0, 0), number_str, font=number_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Use background color for number text to ensure contrast
            number_text_color = Config()["COLORS"].get("BACKGROUND", "#0f0f23")
            d.text(
                (circle_x - text_width // 2, circle_y - text_height // 2 - 2),
                number_str,
                fill=number_text_color,
                font=number_font,
            )
            
            # Wrap text for long items
            wrapped_lines = textwrap.wrap(item, width=int(char_per_line), break_long_words=False)
            text_x = circle_x + circle_radius * 2 + 15
            
            for line in wrapped_lines:
                d.text(
                    (text_x, current_height),
                    line,
                    fill=self.text_color,
                    font=font,
                )
                current_height += int(font.font.height * 1.4)
            
            current_height += 10  # Extra spacing between items
        
        return img, int(current_height + 15)
