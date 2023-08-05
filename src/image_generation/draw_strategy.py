import re
import textwrap
from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from PIL import ImageFont, ImageDraw, Image
import pandas as pd
import matplotlib.pyplot as plt
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.table import Table


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
        char_width = 7
        char_per_line = img_width // char_width

        # Wrap the text
        lines = textwrap.wrap(text, width=char_per_line)

        # Calculate the total height of the text based on the number of lines and the line height
        line_height = 20
        text_height = len(lines) * line_height

        # Draw each line of text
        for i, line in enumerate(lines):
            d.text(
                (10, current_height + i * line_height),
                line,
                fill=self.text_color,
                font=font,
            )

        # Return image and the new current height
        return img, text_height + line_height


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

        # Estimate the number of characters that can fit in the line by using a sample character "0"
        sample_char = "0"
        char_width = 7
        char_per_line = img_width // char_width - len(
            self.bullet_point
        )  # Adjust for the width of the bullet point

        # Calculate the line height based on the size of the string "Ay"
        line_height = 10

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
                        (10, current_height),
                        self.bullet_point + wrapped_line,
                        fill=self.text_color,
                        font=font,
                    )
                else:  # If it's a continuation line of the bullet point
                    d.text(
                        (10 + char_width * len(self.bullet_point), current_height),
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
        self.text_color = text_color

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

        return img, table_height

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
        fig_width = img_width / 80  # Convert pixel to inches, assuming 80 dpi
        fig_height = 4  # Adjust this value as needed

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis("off")
        table = Table(ax, bbox=[0, 0, 1, 1])

        nrows, ncols = df.shape
        width, height = 1.0 / ncols, 1.0 / nrows

        # Define a wrapping width
        wrapping_width = 25

        for (i, j), val in np.ndenumerate(df):
            # Wrap the text in each cell
            val = textwrap.fill(str(val), width=wrapping_width)
            table.add_cell(
                i,
                j,
                width=width,
                height=height,
                text=val,
                loc="left",
                facecolor="white",
            )

        for i, label in enumerate(df.columns):
            # Also wrap the column headers
            label = textwrap.fill(str(label), width=wrapping_width)
            table.add_cell(
                -1,
                i,
                width=width,
                height=0.1,
                text=label,
                loc="center",
                facecolor="grey",
            )

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        ax.add_table(table)
        plt.tight_layout()

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
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
        img.paste(table_img, (0, current_height))
        return img


class DrawCode(DrawStrategy):
    def draw(self, img, text, font, current_height):
        # Implement your strategy for drawing code here
        pass
