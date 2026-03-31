import re
from io import BytesIO
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config
from src.utils.other import hex_to_rgba


class DrawCode(DrawStrategy):
    """
    Drawing strategy for a block of code.
    """

    def __init__(self) -> None:
        self.scale_factor = Config()["CODE_BLOCK"]["SCALE_FACTOR"]

    def _extract_lexer_name(self, text: str) -> Tuple[str, str]:
        """
        Extract lexer name from text and return the cleaned text.

        :param text: The input code text which includes the lexer name.
        :return: Tuple containing lexer name and cleaned text.
        """
        # Match the format similar to markdown code blocks
        match = re.match(r"^[ \t]*```([\w+-]+)", text)
        if match:
            lexer_name = match.group(1)
            # Strip the lexer name line from the text
            text = text[match.end() :].lstrip()
        else:
            lexer_name = "text"  # Default lexer

        # Remove any trailing code block marks
        text = text.replace("```", "")

        return lexer_name, text

    def _get_lexer(self, lexer_name: str):
        """Get the lexer based on the lexer name."""
        try:
            return get_lexer_by_name(lexer_name)
        except ClassNotFound:
            return get_lexer_by_name("text")

    def _create_rounded_rect(
        self, width: int, height: int, corner_radius: int = 10, padding: int = 10
    ) -> Image.Image:
        """Create a rounded rectangle image."""
        scale_factor = 4  # we'll draw everything 4 times larger and then resize it

        # Adjust all the dimensions and positions for the scale factor
        width *= scale_factor
        height *= scale_factor
        corner_radius *= scale_factor
        padding *= scale_factor
        circle_radius = 8 * scale_factor
        circle_padding = 4 * scale_factor

        rounded_rect = Image.new(
            "RGBA", (width + 2 * padding, height + 2 * padding), (255, 255, 255, 0)
        )
        draw = ImageDraw.Draw(rounded_rect)

        draw.rounded_rectangle(
            (0, 0, rounded_rect.width, rounded_rect.height),
            fill=hex_to_rgba(Config()["CODE_BLOCK"]["BACKGROUND"]),
            radius=corner_radius,
        )

        colors = ["#ff5757", "#ffde59", "#7ed957"]

        # Draw the circles
        for idx, color in enumerate(colors):
            circle_x = (
                padding + idx * (circle_radius * 2 + circle_padding) + circle_radius
            )
            circle_y = padding + circle_radius
            left_up_point = (circle_x - circle_radius, circle_y - circle_radius)
            right_down_point = (circle_x + circle_radius, circle_y + circle_radius)

            draw.ellipse([left_up_point, right_down_point], fill=color)

        # Draw a horizontal thin line in the middle
        line_thickness = 1 * scale_factor
        line_y = 2 * (padding + circle_radius)
        draw.line(
            [(padding, line_y), (rounded_rect.width - padding, line_y)],
            fill="grey",
            width=line_thickness,
        )

        # Downscale the image to achieve anti-aliasing and smoother results
        rounded_rect = rounded_rect.resize(
            (rounded_rect.width // scale_factor, rounded_rect.height // scale_factor),
            resample=Image.LANCZOS,
        )

        return rounded_rect

    def _ensure_alpha_channel(self, img: Image.Image) -> Image.Image:
        """Ensure that the image has an alpha channel."""
        if img.mode != "RGBA":
            img = img.convert("RGBA")
            alpha = Image.new("L", img.size, 255)  # Fully opaque alpha channel
            img.putalpha(alpha)
        return img

    def _paste_onto_image(self, img: Image.Image, rounded_rect: Image.Image, current_height: int) -> Tuple[Image.Image, int]:
        scaled_rounded_rect_width = int(rounded_rect.width * self.scale_factor)
        x_position = (img.width - scaled_rounded_rect_width) // 2

        scaled_rounded_rect_height = int(rounded_rect.height * self.scale_factor)

        scaled_rounded_rect = rounded_rect.resize(
            (scaled_rounded_rect_width, scaled_rounded_rect_height)
        )
        img.paste(
            scaled_rounded_rect,
            (x_position, current_height),
            scaled_rounded_rect,
        )

        return img, current_height + scaled_rounded_rect.size[1]

    def draw(
        self, img: Image.Image, code: str, _: ImageFont.FreeTypeFont, current_height: int
    ) -> Tuple[Image.Image, int]:
        lexer_name, cleaned_code = self._extract_lexer_name(code)
        lexer = self._get_lexer(lexer_name)

        highlighted_code = highlight(
            cleaned_code,
            lexer,
            ImageFormatter(style=get_style_by_name("vim"), line_numbers=False),
        )
        current_height += 10
        code_img = Image.open(BytesIO(highlighted_code))
        code_img = self._ensure_alpha_channel(code_img)

        rounded_rect = self._create_rounded_rect(
            code_img.width,
            code_img.height + Config()["CODE_BLOCK"]["TOP_PADDING"],
            Config()["CODE_BLOCK"]["RADIUS"],
            Config()["CODE_BLOCK"]["RADIUS"],
        )
        rounded_rect.paste(
            code_img,
            (10, 10 + Config()["CODE_BLOCK"]["TOP_PADDING"]),
            code_img,
        )  # 10 is the padding

        img, height = self._paste_onto_image(img, rounded_rect, current_height)

        return img, height + 50  # TODO: make configurable
