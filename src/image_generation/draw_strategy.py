import re
import textwrap
from abc import ABC, abstractmethod

import numpy as np
from PIL import ImageFont, ImageDraw, Image, ImageFilter
import pandas as pd
import matplotlib.pyplot as plt
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.table import Table
from io import BytesIO
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from typing import Tuple, List

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
    def __init__(
        self,
        text_color: str,
    ):
        self.text_color = text_color
        self.highlight_color = Config()["COLORS"]["HIGHLIGHT"]
        self.italic_color = Config()["COLORS"].get("ITALIC_COLOR", self.text_color)
        self.link_color = Config()["COLORS"].get("LINK_COLOR", "#5dade2")
        self.inline_code_bg = Config()["COLORS"].get("INLINE_CODE_BG", "#282a36")
        self.inline_code_fg = Config()["COLORS"].get("INLINE_CODE_FG", "#50fa7b")

    def parse_formatted_words(self, text: str) -> List[Tuple[str, str]]:
        """
        Parse text and return a list of words with formatting info.
        Returns list of tuples: (word, format_type)
        format_type can be: 'normal', 'bold', 'italic', 'link', 'inline_code'
        Each word includes any trailing space.
        """
        result = []
        
        # First, handle inline code `code`
        inline_code_pattern = re.compile(r'`([^`]+)`')
        inline_code_ranges = []
        
        cleaned_text = text
        offset = 0
        for match in inline_code_pattern.finditer(text):
            code_text = match.group(1)
            start_pos = match.start() - offset
            end_pos = start_pos + len(code_text)
            inline_code_ranges.append((start_pos, end_pos))
            offset += len(match.group(0)) - len(code_text)
        
        cleaned_text = inline_code_pattern.sub(r'\1', text)
        
        # Handle links [text](url) - replace with just text
        link_pattern = re.compile(r'\[([^\]]+)\]\([^)]+\)')
        link_ranges = []
        
        offset = 0
        for match in link_pattern.finditer(cleaned_text):
            link_text = match.group(1)
            start_pos = match.start() - offset
            end_pos = start_pos + len(link_text)
            link_ranges.append((start_pos, end_pos))
            offset += len(match.group(0)) - len(link_text)
        
        cleaned_text = link_pattern.sub(r'\1', cleaned_text)
        
        # Pattern for bold (**text** or __text__)
        bold_pattern = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
        bold_ranges = []
        
        offset = 0
        for match in bold_pattern.finditer(cleaned_text):
            bold_text = match.group(1) or match.group(2)
            start_pos = match.start() - offset
            end_pos = start_pos + len(bold_text)
            bold_ranges.append((start_pos, end_pos))
            offset += len(match.group(0)) - len(bold_text)
        
        cleaned_text = bold_pattern.sub(lambda m: m.group(1) or m.group(2), cleaned_text)
        
        # Pattern for italic (*text* or _text_) - single markers
        italic_pattern = re.compile(r'(?<!\*)\*([^*]+?)\*(?!\*)|(?<!_)_([^_]+?)_(?!_)')
        italic_ranges = []
        
        offset = 0
        for match in italic_pattern.finditer(cleaned_text):
            italic_text = match.group(1) or match.group(2)
            start_pos = match.start() - offset
            end_pos = start_pos + len(italic_text)
            italic_ranges.append((start_pos, end_pos))
            offset += len(match.group(0)) - len(italic_text)
        
        cleaned_text = italic_pattern.sub(lambda m: m.group(1) or m.group(2), cleaned_text)
        
        # Now split into words and track formatting
        words = cleaned_text.split(' ')
        current_pos = 0
        
        for i, word in enumerate(words):
            format_type = 'normal'
            word_start = current_pos
            word_end = current_pos + len(word)
            
            # Check formatting (priority: inline_code > bold > italic > link)
            for code_start, code_end in inline_code_ranges:
                if word_start < code_end and word_end > code_start:
                    format_type = 'inline_code'
                    break
            
            if format_type == 'normal':
                for bold_start, bold_end in bold_ranges:
                    if word_start < bold_end and word_end > bold_start:
                        format_type = 'bold'
                        break
            
            if format_type == 'normal':
                for italic_start, italic_end in italic_ranges:
                    if word_start < italic_end and word_end > italic_start:
                        format_type = 'italic'
                        break
            
            if format_type == 'normal':
                for link_start, link_end in link_ranges:
                    if word_start < link_end and word_end > link_start:
                        format_type = 'link'
                        break
            
            # Add space after word (except for last word)
            if i < len(words) - 1:
                result.append((word + ' ', format_type))
                current_pos = word_end + 1  # +1 for the space
            else:
                result.append((word, format_type))
                current_pos = word_end
        
        return result

    def get_color_for_format(self, format_type: str) -> str:
        """Get the appropriate color for a format type."""
        if format_type == 'bold':
            return self.highlight_color
        elif format_type == 'italic':
            return self.italic_color
        elif format_type == 'link':
            return self.link_color
        elif format_type == 'inline_code':
            return self.inline_code_fg
        return self.text_color

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

        # Parse the text to get words with formatting
        words = self.parse_formatted_words(text)
        
        # Build clean text for checking if it starts with a digit
        clean_text = "".join(w[0] for w in words)
        
        # Handle numbering prefix spacing
        if clean_text.strip() and clean_text.strip()[0].isdigit():
            current_height += int(font.font.height * 1.2)
        
        # Word-by-word rendering with line wrapping
        x_position = left_margin
        space_width = font.getbbox(" ")[2]
        
        for word, format_type in words:
            word_stripped = word.rstrip()
            has_trailing_space = word != word_stripped
            
            # Get word width
            bbox = font.getbbox(word_stripped)
            word_width = bbox[2] - bbox[0]
            
            # Check if we need to wrap to next line
            if x_position + word_width > img_width - right_margin and x_position > left_margin:
                current_height += int(font.font.height * 1.5)
                x_position = left_margin
            
            # Choose color based on formatting
            color = self.get_color_for_format(format_type)
            
            # Draw inline code background if needed
            if format_type == 'inline_code':
                padding = 4
                bg_rect = [
                    x_position - padding,
                    current_height - padding,
                    x_position + word_width + padding,
                    current_height + font.font.height + padding
                ]
                d.rounded_rectangle(bg_rect, radius=4, fill=self.inline_code_bg)
            
            # Draw the word
            d.text((x_position, current_height), word_stripped, fill=color, font=font)
            
            # Update position
            x_position += word_width
            if has_trailing_space:
                x_position += space_width

        # Move to next line after finishing
        current_height += int(font.font.height * 1.5)

        return img, current_height


class DrawHeader:
    """Drawing strategy for headers with accent styling."""
    
    def __init__(self, text_color: str):
        self.text_color = text_color
        self.header_color = Config()["COLORS"].get("HEADER_COLOR", "#00d4ff")
        self.accent_color = Config()["COLORS"]["HIGHLIGHT"]

    def draw(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        current_height: int,
    ) -> Tuple[Image.Image, int]:
        d = ImageDraw.Draw(img)
        left_margin = Config()["PAGE_LAYOUT"].get("LEFT_MARGIN", Config()["PAGE_LAYOUT"]["RIGHT_MARGIN"])
        
        # Draw accent line before header
        accent_width = 4
        accent_height = font.font.height
        d.rectangle(
            [
                (left_margin - 20, current_height),
                (left_margin - 20 + accent_width, current_height + accent_height)
            ],
            fill=self.accent_color
        )
        
        # Draw header text
        d.text((left_margin, current_height), text, fill=self.header_color, font=font)
        
        current_height += int(font.font.height * 1.8)
        
        return img, current_height


class DrawTitle:
    """Drawing strategy for titles with impressive styling."""
    
    def __init__(self, text_color: str):
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


class DrawTable:
    """
    Class that represents a strategy to draw a table on an image using matplotlib.
    """

    def __init__(self, text_color: str):
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
        img_width *= 0.9
        fig_width = img_width / 80  # Convert pixel to inches, assuming 80 dpi
        fig_height = Config()["TABLE"]["HEIGHT"]

        # Set transparent background with the facecolor parameter
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor="none")
        ax.axis("off")
        table = Table(ax, bbox=[0, 0, 1, 1])

        nrows, ncols = df.shape
        width, height = 1.0 / ncols, 1.0 / nrows

        wrapping_width = 14  # TODO: Move to CONFIG Adjust this value as needed

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

            # if re.match(r"\*.*\*$", val):
            if val.startswith("*") or val.endswith("*"):
                cell.get_text().set_color(self.highlight_color)  # Set color to red
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

        return img, height + 50 # make configurable


class DrawBulletList:
    """
    Drawing strategy for bullet lists with stylish bullet points.
    """

    def __init__(self, text_color: str):
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


class DrawNumberedList:
    """
    Drawing strategy for numbered/ordered lists with modern styling.
    """

    def __init__(self, text_color: str):
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
            except Exception:
                number_font = font
            
            # Get text bounding box for centering
            bbox = d.textbbox((0, 0), number_str, font=number_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            d.text(
                (circle_x - text_width // 2, circle_y - text_height // 2 - 2),
                number_str,
                fill="#0f0f23",  # Dark color for contrast
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


class DrawBlockquote:
    """
    Drawing strategy for blockquotes with a stylish left border and background.
    """

    def __init__(self, text_color: str):
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
        temp_height = current_height
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
        # Draw subtle background
        d.rounded_rectangle(bg_rect, radius=8, fill="#1a1a2e")
        
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


class DrawHorizontalRule:
    """
    Drawing strategy for horizontal rules/dividers with modern styling.
    """

    def __init__(self, text_color: str):
        self.line_color = Config()["COLORS"].get("DIVIDER_COLOR", "#555555")
        self.accent_color = Config()["COLORS"]["HIGHLIGHT"]

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
        img_width = img.size[0]
        
        # Add some vertical spacing
        current_height += 25
        
        # Draw a stylish horizontal line
        line_y = current_height
        line_start = left_margin + 50
        line_end = img_width - right_margin - 50
        line_height = 2
        
        # Draw gradient-like line (fade from edges)
        center_x = (line_start + line_end) // 2
        
        # Draw main line
        d.rectangle(
            [(line_start, line_y), (line_end, line_y + line_height)],
            fill=self.line_color
        )
        
        # Draw accent diamond in the center
        diamond_size = 10
        d.polygon(
            [
                (center_x, line_y - diamond_size),
                (center_x + diamond_size, line_y + line_height // 2),
                (center_x, line_y + line_height + diamond_size),
                (center_x - diamond_size, line_y + line_height // 2),
            ],
            fill=self.accent_color
        )
        
        # Draw small dots on either side of the diamond
        dot_radius = 3
        dot_offset = 30
        for offset in [-dot_offset, dot_offset]:
            d.ellipse(
                [
                    (center_x + offset - dot_radius, line_y - dot_radius + 1),
                    (center_x + offset + dot_radius, line_y + dot_radius + 1)
                ],
                fill=self.accent_color
            )
        
        current_height += 35
        
        return img, int(current_height)


class DrawTaskList:
    """
    Drawing strategy for task lists (checkboxes) with modern styling.
    """

    def __init__(self, text_color: str):
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
                # Draw check symbol
                check_points = [
                    (box_x + 5, box_y + box_size // 2),
                    (box_x + box_size // 2 - 1, box_y + box_size - 6),
                    (box_x + box_size - 4, box_y + 5)
                ]
                d.line(check_points, fill="#0f0f23", width=2)
            
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
