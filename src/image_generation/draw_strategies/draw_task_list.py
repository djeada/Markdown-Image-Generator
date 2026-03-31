import textwrap
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawTaskList(DrawStrategy):
    """
    Drawing strategy for task lists (checkboxes) with modern styling.
    """

    def __init__(self, text_color: str) -> None:
        self.text_color = text_color
        self.highlight_color = Config()["COLORS"]["HIGHLIGHT"]
        self.checked_color = Config()["COLORS"].get("BULLET_COLOR", self.highlight_color)
        self.unchecked_color = Config()["COLORS"].get("DIVIDER_COLOR", "#555555")

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
        checkbox_indent = 30
        img_width = img.size[0]
        
        items = text.split("\n")
        char_per_line = (img_width - left_margin - checkbox_indent - right_margin - 70) // font.getbbox("a")[2]
        
        for item in items:
            if not item.strip() or ":" not in item:
                continue
            
            # Parse state and text
            state, item_text = item.split(":", 1)
            is_checked = state == "checked"
            
            # Draw checkbox
            box_size = 18
            box_x = left_margin + checkbox_indent
            box_y = current_height + (font.font.height - box_size) // 2
            
            # Draw checkbox outline
            d.rounded_rectangle(
                [
                    (box_x, box_y),
                    (box_x + box_size, box_y + box_size)
                ],
                radius=4,
                outline=self.checked_color if is_checked else self.unchecked_color,
                width=2
            )
            
            if is_checked:
                # Draw checkmark
                d.rounded_rectangle(
                    [
                        (box_x + 3, box_y + 3),
                        (box_x + box_size - 3, box_y + box_size - 3)
                    ],
                    radius=2,
                    fill=self.checked_color
                )
                # Draw check symbol using background color for contrast
                check_color = Config()["COLORS"].get("BACKGROUND", "#0f0f23")
                check_points = [
                    (box_x + 5, box_y + box_size // 2),
                    (box_x + box_size // 2 - 1, box_y + box_size - 6),
                    (box_x + box_size - 4, box_y + 5)
                ]
                d.line(check_points, fill=check_color, width=2)
            
            # Wrap text for long items
            wrapped_lines = textwrap.wrap(item_text, width=int(char_per_line), break_long_words=False)
            text_x = box_x + box_size + 15
            
            # Use strikethrough color for checked items
            text_color = self.unchecked_color if is_checked else self.text_color
            
            for line in wrapped_lines:
                d.text(
                    (text_x, current_height),
                    line,
                    fill=text_color,
                    font=font,
                )
                current_height += int(font.font.height * 1.4)
            
            current_height += 8  # Extra spacing between items
        
        return img, int(current_height + 15)
