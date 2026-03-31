import textwrap
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawBulletList(DrawStrategy):
    """
    Drawing strategy for bullet lists with stylish bullet points.
    """

    def __init__(self, text_color: str) -> None:
        self.text_color = text_color
        self.highlight_color = Config()["COLORS"]["HIGHLIGHT"]
        self.bullet_color = Config()["COLORS"].get("BULLET_COLOR", self.highlight_color)

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
        bullet_indent = 30
        img_width = img.size[0]
        
        items = text.split("\n")
        char_per_line = (img_width - left_margin - bullet_indent - right_margin - 50) // font.getbbox("a")[2]
        
        for item in items:
            if not item.strip():
                continue
                
            # Draw bullet point (filled circle with glow effect)
            bullet_radius = 6
            bullet_x = left_margin + bullet_indent
            bullet_y = current_height + font.font.height // 2
            
            # Draw outer glow
            d.ellipse(
                [
                    (bullet_x - bullet_radius - 2, bullet_y - bullet_radius - 2),
                    (bullet_x + bullet_radius + 2, bullet_y + bullet_radius + 2)
                ],
                fill=None,
                outline=self.bullet_color,
                width=1
            )
            
            # Draw bullet point
            d.ellipse(
                [
                    (bullet_x - bullet_radius, bullet_y - bullet_radius),
                    (bullet_x + bullet_radius, bullet_y + bullet_radius)
                ],
                fill=self.bullet_color
            )
            
            # Wrap text for long items
            wrapped_lines = textwrap.wrap(item, width=int(char_per_line), break_long_words=False)
            text_x = bullet_x + bullet_radius * 3 + 5
            
            for idx, line in enumerate(wrapped_lines):
                d.text(
                    (text_x, current_height),
                    line,
                    fill=self.text_color,
                    font=font,
                )
                current_height += int(font.font.height * 1.4)
            
            current_height += 8  # Extra spacing between items
        
        return img, int(current_height + 15)
