import re
import textwrap
from abc import ABC, abstractmethod

import numpy as np
from PIL import ImageFont, ImageDraw, Image
import pandas as pd
import matplotlib.pyplot as plt
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.table import Table
from io import BytesIO
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from typing import Tuple

from pygments.styles import get_style_by_name

from src.utils.config import Config
from src.utils.other import hex_to_rgba


class DrawStrategy(ABC):
    """
    Abstract base class for different drawing strategies.
    """

    @abstractmethod
    def draw(
        self, img: Image, text: str, font: ImageFont.FreeTypeFont, current_height: int
    ) -> Tuple[Image.Image, int]:
        """
        Abstract method to be implemented by concrete strategies to draw on the image.

        :param img: The image to draw on.
        :param text: The text to be drawn.
        :param font: The font of the text.
        :param current_height: The current height on the image to draw the text.
        :return: A tuple containing the image with the text drawn and the height of the drawn text in pixels.
        """
        pass


class DrawDefault:
    """
    Default drawing strategy.
    """

    def __init__(self, text_color: str):
        """
        Constructor for the DrawDefault class.

        :param text_color: The color of the text to be drawn.
        """
        self.text_color = text_color

    def draw(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        current_height: int,
    ) -> Tuple[Image.Image, int]:
        """
        Method to draw the text on the image and return the image and the height of the text.

        :param img: The image to draw on.
        :param text: The text to be drawn.
        :param font: The font of the text.
        :param current_height: The current height on the image to draw the text.
        :return: A tuple containing the image with the text drawn and the height of the text in pixels.
        """
        d = ImageDraw.Draw(img)

        # Width of the image
        img_width = img.size[0]

        # Estimate the number of characters that can fit in the line
        char_per_line = img_width // Config.get_instance().get("CHAR_WIDTH")

        # Wrap the text
        lines = textwrap.wrap(text, width=char_per_line)

        # Calculate the total height of the text based on the number of lines and the line height
        line_height = Config.get_instance().get("DEFAULT_LINE_HEIGHT")
        text_height = len(lines) * line_height

        # Draw each line of text
        for i, line in enumerate(lines):
            d.text(
                (
                    Config.get_instance().get("PAGE_RIGHT_MARGIN"),
                    current_height + i * line_height,
                ),
                line,
                fill=self.text_color,
                font=font,
            )

        # Return image and the new current height
        return img, text_height + line_height


class DrawTitle:
    """
    Title drawing strategy.
    Ensures there are a maximum of 2 title words per line.
    """

    def __init__(
        self,
        text_color: str,
        padding_left: int = Config.get_instance().get("PAGE_RIGHT_MARGIN"),
        padding_top: int = Config.get_instance().get("PAGE_TOP_MARGIN"),
    ):
        """
        Constructor for the DrawTitle class.

        :param text_color: The color of the text to be drawn.
        :param padding_left: The horizontal padding from the left edge.
        :param padding_top: The vertical padding from the top edge.
        """
        self.text_color = text_color
        self.padding_left = padding_left
        self.padding_top = padding_top

    def draw(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        current_height: int,
    ) -> Tuple[Image.Image, int]:
        """
        Method to draw the text on the image and return the image and the height of the text.

        :param img: The image to draw on.
        :param text: The text to be drawn.
        :param font: The font of the text.
        :param current_height: The current height on the image to draw the text.
        :return: A tuple containing the image with the text drawn and the height of the text in pixels.
        """
        d = ImageDraw.Draw(img)

        # Wrap the text by two words per line
        lines = textwrap.wrap(text, width=12, break_long_words=False)

        # Calculate the total height of the text based on the number of lines and the line height
        line_height = 150
        text_height = len(lines) * line_height

        # Draw each line of text
        for i, line in enumerate(lines):
            width = 1000
            x_pos = (
                img.width - width
            ) // 2 + self.padding_left  # Center the text horizontally considering padding
            y_pos = self.padding_top + current_height + i * line_height
            d.text(
                (x_pos, y_pos),
                line,
                fill=self.text_color,
                font=font,
            )

        # Return image and the new current height
        return img, current_height + text_height + line_height


class DrawList:
    """
    Drawing strategy for a list of texts with bullet points.
    """

    def __init__(self, text_color: str, bullet_point="\u2022 "):
        """
        Constructor for the DrawList class.

        :param text_color: The color of the text to be drawn.
        :param bullet_point: The symbol used for the bullet point. Defaults to "\u2022 " (bullet point symbol followed by a space).
        """
        self.text_color = text_color
        self.bullet_point = bullet_point

    def draw(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        current_height: int,
    ) -> Tuple[Image.Image, int]:
        """
        Method to draw the text as a list of bullet points on the image and return the image and the new height.

        :param img: The image to draw on.
        :param text: The text to be drawn, where each line is separated by '\n'.
        :param font: The font of the text.
        :param current_height: The current height on the image to start drawing the text.
        :return: A tuple containing the image with the text drawn and the new height.
        """
        d = ImageDraw.Draw(img)

        # Width of the image
        img_width = img.size[0]

        char_per_line = img_width // Config.get_instance().get("CHAR_WIDTH") - len(
            self.bullet_point
        )  # Adjust for the width of the bullet point

        # Calculate the line height based on the size of the string "Ay"
        line_height = Config.get_instance().get("LIST_LINE_HEIGHT")

        # Split the text into lines and draw each line as a bullet point
        lines = text.split("\n")
        n = current_height
        for line in lines:
            # Wrap the line
            wrapped_lines = textwrap.wrap(line, width=char_per_line)

            # Draw each wrapped line of text
            for i, wrapped_line in enumerate(wrapped_lines):
                if i == 0:  # If it's the first line of the bullet point
                    d.text(
                        (
                            Config.get_instance().get("PAGE_RIGHT_MARGIN"),
                            current_height,
                        ),
                        self.bullet_point + wrapped_line,
                        fill=self.text_color,
                        font=font,
                    )
                else:  # If it's a continuation line of the bullet point
                    d.text(
                        (
                            10
                            + Config.get_instance().get("CHAR_WIDTH")
                            * len(self.bullet_point),
                            current_height,
                        ),
                        wrapped_line,
                        fill=self.text_color,
                        font=font,
                    )

                # Update the current height for the next line
                current_height += line_height

            # Add an extra line_height for spacing between bullet points
            current_height += line_height

        # Return image and the new current height
        return img, current_height - n + line_height


class DrawTable:
    """
    Class that represents a strategy to draw a table on an image using matplotlib.
    """

    def __init__(self, text_color: str):
        """
        Constructor for the DrawTable class.

        :param text_color: The color of the text to be drawn.
        """
        self.scale_factor = Config.get_instance().get("TABLE_SCALE_FACTOR")
        self.background_color = Config.get_instance().get("TABLE_BG_COLOR")
        self.text_color = Config.get_instance().get("TABLE_FG_COLOR")

    def draw(
        self, img: Image, text: str, font, current_height: int
    ) -> Tuple[Image.Image, int]:
        """
        Method to draw the table on the image and return the image and the height of the table.

        :param img: The image to draw on.
        :param text: The table text to be drawn.
        :param font: The font of the text.
        :param current_height: The current height on the image to draw the table.
        :return: A tuple containing the image with the table drawn on it and the height of the table in pixels.
        """
        df = self.text_to_dataframe(text)
        img_width = img.size[0]
        table_img = self.dataframe_to_matplotlib(df, img_width * 0.8)
        self.add_matplotlib_to_image(img, table_img, current_height)

        # Calculate the height of the table
        table_height = table_img.size[1]

        return img, table_height * self.scale_factor + 20

    def text_to_dataframe(self, text: str) -> pd.DataFrame:
        """
        Method to convert the text to a pandas DataFrame.

        :param text: The table text to be converted.
        :return: The text converted to a pandas DataFrame.
        """
        cleaned_table_str = re.sub(
            r"(?<=\|)( *[\S ]*? *)(?=\|)", lambda match: match.group(0).strip(), text
        )
        df = (
            pd.read_table(
                io.StringIO(cleaned_table_str), sep="|", header=0, skipinitialspace=True
            )
            .dropna(axis=1, how="all")
            .iloc[1:]
        )
        df.columns = df.columns.str.strip()
        return df

    def dataframe_to_matplotlib(self, df: pd.DataFrame, img_width: int) -> Image:
        """
        Method to convert the pandas DataFrame to a matplotlib table and then to an image.

        :param df: The pandas DataFrame to be converted.
        :param img_width: The width of the image to fit the table.
        :return: The table as an image.
        """
        img_width = 0.8 * img_width
        fig_width = img_width / 80  # Convert pixel to inches, assuming 80 dpi
        fig_height = 6  # Adjust this value as needed

        # Set transparent background with the facecolor parameter
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor="none")
        ax.axis("off")
        table = Table(ax, bbox=[0, 0, 1, 1])

        nrows, ncols = df.shape
        width, height = 1.0 / ncols, 1.0 / nrows

        wrapping_width = 20

        for (i, j), val in np.ndenumerate(df):
            val = textwrap.fill(str(val), width=wrapping_width)
            cell = table.add_cell(
                i,
                j,
                width=width,
                height=height,
                text=val,
                loc="left",
                facecolor=self.background_color,
            )
            cell.get_text().set_color(self.text_color)  # set color to blue

        for i, label in enumerate(df.columns):
            label = textwrap.fill(str(label), width=wrapping_width)
            table.add_cell(
                -1,
                i,
                width=width,
                height=0.2,
                text=label,
                loc="center",
                facecolor="#8c52ff",
            )

        table.auto_set_font_size(False)
        table.set_fontsize(15)
        table.scale(1, 1.5)

        ax.add_table(table)
        plt.tight_layout()

        canvas = FigureCanvasAgg(fig)
        canvas.draw()

        # Get the buffer in RGBA format
        buf = canvas.buffer_rgba()
        array = np.asarray(buf)
        table_img = Image.fromarray(array)

        plt.close(fig)
        return table_img

    def add_matplotlib_to_image(
        self, img: Image, table_img: Image, current_height: int
    ) -> Image:
        """
        Method to add the table image to the main image.

        :param img: The main image.
        :param table_img: The table image.
        :param current_height: The current height on the main image to add the table.
        :return: The main image with the table added.
        """

        r, g, b, a = table_img.split()
        rgb_img = Image.merge("RGB", (r, g, b))

        # Resize the image and its alpha channel separately
        new_width = int(table_img.width * self.scale_factor)
        new_height = int(table_img.height * self.scale_factor)
        resized_img = rgb_img.resize((new_width, new_height), Image.LANCZOS)
        resized_alpha = a.resize((new_width, new_height), Image.LANCZOS)

        # Merge them back together
        resized_table_img = Image.merge(
            "RGBA",
            (
                resized_img.split()[0],
                resized_img.split()[1],
                resized_img.split()[2],
                resized_alpha,
            ),
        )

        # Calculate horizontal offset for centering
        horizontal_offset = (img.width - resized_table_img.width) // 2

        # Paste the resized table_img onto the main image
        img.paste(
            resized_table_img,
            (horizontal_offset, current_height),
            mask=resized_table_img.split()[3],
        )

        return img


class DrawCode:
    """
    Drawing strategy for a block of code.
    """

    def __init__(self):
        """
        Constructor for the DrawCode class.

        :param lexer_name: The name of the lexer to use for syntax highlighting, e.g., "python".
        """
        self.scale_factor = Config.get_instance().get("CODE_BLOCK_SCALE_FACTOR")

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
        except:
            return get_lexer_by_name(
                "text"
            )  # Default to basic lexer for unknown language

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
            fill=hex_to_rgba(Config.get_instance().get("CODE_BLOCK_BG")),
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
        line_thickness = 1 * scale_factor  # you can adjust the thickness here
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

    def _paste_onto_image(self, img, rounded_rect, current_height):
        scaled_rounded_rect_width = int(rounded_rect.width * self.scale_factor)
        x_position = (img.width - scaled_rounded_rect_width) // 2

        scaled_rounded_rect_height = int(rounded_rect.height * self.scale_factor)
        height_difference = (rounded_rect.height - scaled_rounded_rect_height) // 2

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
        self, img: Image.Image, code: str, _, current_height: int
    ) -> Tuple[Image.Image, int]:
        lexer_name, cleaned_code = self._extract_lexer_name(code)
        lexer = self._get_lexer(lexer_name)

        highlighted_code = highlight(
            cleaned_code,
            lexer,
            ImageFormatter(style=get_style_by_name("vim"), line_numbers=False),
        )

        code_img = Image.open(BytesIO(highlighted_code))
        code_img = self._ensure_alpha_channel(code_img)

        rounded_rect = self._create_rounded_rect(
            code_img.width,
            code_img.height + Config.get_instance().get("CODE_BLOCK_TOP_PADDING"),
            Config.get_instance().get("CODE_BLOCK_RADIUS"),
            Config.get_instance().get("CODE_BLOCK_RADIUS"),
        )
        rounded_rect.paste(
            code_img,
            (10, 10 + Config.get_instance().get("CODE_BLOCK_TOP_PADDING")),
            code_img,
        )  # 10 is the padding

        img, height = self._paste_onto_image(img, rounded_rect, current_height)

        return img, height
