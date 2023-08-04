import re
from abc import ABC, abstractmethod

import numpy as np
from PIL import ImageFont, ImageDraw, Image
import pandas as pd
import matplotlib.pyplot as plt
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.table import Table


class DrawStrategy(ABC):
    @abstractmethod
    def draw(self, img, text, font: ImageFont.FreeTypeFont, current_height: int):
        pass


class DrawDefault(DrawStrategy):
    def __init__(self, text_color):
        self.text_color = text_color

    def draw(self, img, text, font, current_height):
        d = ImageDraw.Draw(img)
        d.text((10, current_height), text, fill=self.text_color, font=font)


class DrawTable(DrawStrategy):
    def __init__(self, text_color):
        self.text_color = text_color

    def draw(self, img, text, font, current_height):
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

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.axis("off")

        # Draw table
        table = Table(ax, bbox=[0, 0, 1, 1])

        # Determine the number of rows and columns
        nrows, ncols = df.shape
        width, height = 1.0 / ncols, 1.0 / nrows

        # Add cells
        for (i, j), val in np.ndenumerate(df):
            idx = np.array([j % ncols, (nrows - i % nrows) - 1])
            cell = table.add_cell(
                *idx,
                width=width,
                height=height,
                text=val,
                loc="left",
                facecolor="white"
            )

        # Add headers
        for i, label in enumerate(df.columns):
            table.add_cell(
                -1,
                i,
                width=width,
                height=0.05,
                text=label,
                loc="center",
                facecolor="grey",
            )

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        ax.add_table(table)
        plt.tight_layout()  # This line can help reducing the padding.
        # Convert matplotlib figure to a PIL Image
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        buf = canvas.buffer_rgba()
        X = np.asarray(buf)
        table_img = Image.fromarray(X)

        # Paste the table onto the original image
        img.paste(table_img, (0, current_height))

        plt.close(fig)


class DrawCode(DrawStrategy):
    def draw(self, img, text, font, current_height):
        # Implement your strategy for drawing code here
        pass
