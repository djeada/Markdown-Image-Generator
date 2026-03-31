import textwrap
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawBlockquote(DrawStrategy):
    """
    Drawing strategy for blockquotes with a stylish left border and background.
    """

    def __init__(self, text_color: str) -> None:
        self.text_color = text_color
        self.quote_color = Config()["COLORS"].get("QUOTE_COLOR", "#888888")
        self.border_color = Config()["COLORS"].get("QUOTE_BORDER", Config()["COLORS"]["HIGHLIGHT"])

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
        border_width = 4
        quote_indent = 30
        img_width = img.size[0]
        
        start_height = current_height
        lines = text.split("\n")
        char_per_line = (img_width - left_margin - quote_indent - right_margin - 100) // font.getbbox("a")[2]
        
        # Calculate total height first for background
        all_wrapped_lines = []
        for line in lines:
            if not line.strip():
                all_wrapped_lines.append(None)  # Empty line marker
            else:
                wrapped = textwrap.wrap(line, width=int(char_per_line), break_long_words=False)
                all_wrapped_lines.extend(wrapped)
        
        # Draw semi-transparent background
        total_line_height = sum(
            int(font.font.height * 0.5) if line is None else int(font.font.height * 1.4)
            for line in all_wrapped_lines
        )
        
        bg_padding = 15
        bg_rect = [
            left_margin + quote_indent - bg_padding,
            start_height - bg_padding,
            img_width - right_margin,
            start_height + total_line_height + bg_padding
        ]
        # Draw subtle background using a darker shade of the background color
        quote_bg = Config()["COLORS"].get("INLINE_CODE_BG", "#1a1a2e")
        d.rounded_rectangle(bg_rect, radius=8, fill=quote_bg)
        
        # Draw quote text
        for line in lines:
            if not line.strip():
                current_height += int(font.font.height * 0.5)
                continue
            
            wrapped_lines = textwrap.wrap(line, width=int(char_per_line), break_long_words=False)
            text_x = left_margin + quote_indent + 20
            
            for wrapped_line in wrapped_lines:
                d.text(
                    (text_x, current_height),
                    wrapped_line,
                    fill=self.quote_color,
                    font=font,
                )
                current_height += int(font.font.height * 1.4)
        
        # Draw left border
        border_x = left_margin + quote_indent
        d.rectangle(
            [
                (border_x, start_height - 5),
                (border_x + border_width, current_height + 5)
            ],
            fill=self.border_color
        )
        
        return img, int(current_height + 25)
