import io
import re
import textwrap
from typing import Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.table import Table
from PIL import Image

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawTable(DrawStrategy):
    """
    Class that represents a strategy to draw a table on an image using matplotlib.
    """

    def __init__(self, text_color: str) -> None:
        """
        Constructor for the DrawTable class.

        :param text_color: The color of the text to be drawn.
        """
        self.scale_factor = Config()["TABLE"]["SCALE_FACTOR"]
        self.background_color = Config()["TABLE"]["BACKGROUND"]
        self.text_color = Config()["TABLE"]["FOREGROUND"]
        self.highlight_color = Config()["TABLE"]["HIGHLIGHT"]
        self.header_fg_color = Config()["TABLE"]["HEADER_FG_COLOR"]
        self.header_bg_color = Config()["TABLE"]["HEADER_BG_COLOR"]

    def draw(
        self, img: Image.Image, text: str, font, current_height: int
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

    def dataframe_to_matplotlib(self, df: pd.DataFrame, img_width: int) -> Image.Image:
        """
        Method to convert the pandas DataFrame to a matplotlib table and then to an image.

        :param df: The pandas DataFrame to be converted.
        :param img_width: The width of the image to fit the table.
        :return: The table as an image.
        """
        img_width *= 0.9
        fig_width = img_width / 80  # Convert pixel to inches, assuming 80 dpi
        fig_height = Config()["TABLE"]["HEIGHT"]

        # Set transparent background with the facecolor parameter
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor="none")
        ax.axis("off")
        table = Table(ax, bbox=[0, 0, 1, 1])

        nrows, ncols = df.shape
        width, height = 1.0 / ncols, 1.0 / nrows

        wrapping_width = 14  # TODO: Move to CONFIG

        for (i, j), val in np.ndenumerate(df):
            # Split the cell text on '<br/>' and join with newline characters
            split_vals = str(val).split('<br>')
            wrapped_vals = [textwrap.fill(part, width=wrapping_width) for part
                            in split_vals]
            val = '\n\n'.join(wrapped_vals)

            cell = table.add_cell(
                i,
                j,
                width=width,
                height=height,
                text=val,
                loc="left",
                facecolor=self.background_color,
            )

            if val.startswith("*") or val.endswith("*"):
                cell.get_text().set_color(self.highlight_color)
                unwrapped_val = val.replace("*", "")
                cell.get_text().set_text(
                    textwrap.fill(unwrapped_val, width=wrapping_width)
                )
            else:
                cell.get_text().set_color(self.text_color)

        for i, label in enumerate(df.columns):
            label = textwrap.fill(str(label), width=wrapping_width)
            cell = table.add_cell(
                -1,
                i,
                width=width,
                height=0.2,
                text=label,
                loc="center",
                facecolor=self.header_bg_color,
            )
            cell.get_text().set_color(self.header_fg_color)

        table.auto_set_font_size(False)
        table.set_fontsize(16)
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
        self, img: Image.Image, table_img: Image.Image, current_height: int
    ) -> Image.Image:
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
