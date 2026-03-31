from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawTitle(DrawStrategy):
    """Drawing strategy for titles with impressive styling."""
    
    def __init__(self, text_color: str) -> None:
        self.text_color = text_color
        self.title_color = Config()["COLORS"].get("TITLE_COLOR", "#ffffff")
        self.accent_color = Config()["COLORS"]["HIGHLIGHT"]

    def draw(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        current_height: int,
    ) -> Tuple[Image.Image, int]:
        d = ImageDraw.Draw(img)
        img_width = img.size[0]
        left_margin = Config()["PAGE_LAYOUT"].get("LEFT_MARGIN", Config()["PAGE_LAYOUT"]["RIGHT_MARGIN"])
        right_margin = Config()["PAGE_LAYOUT"]["RIGHT_MARGIN"]
        max_width = img_width - left_margin - right_margin
        
        # Word wrap the title if needed
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line of the title
        for line in lines:
            d.text((left_margin, current_height), line, fill=self.title_color, font=font)
            current_height += int(font.font.height * 1.3)
        
        # Get the width of the first line for underline
        if lines:
            bbox = font.getbbox(lines[0])
            text_width = bbox[2] - bbox[0]
            
            # Draw underline accent
            line_y = current_height + 5
            d.line(
                [(left_margin, line_y), (left_margin + min(text_width, 200), line_y)],
                fill=self.accent_color,
                width=3
            )
        
        current_height += int(font.font.height * 0.8)
        
        return img, current_height
