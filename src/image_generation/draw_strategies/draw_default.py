import re
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

from src.image_generation.draw_strategies.base import DrawStrategy
from src.utils.config import Config


class DrawDefault(DrawStrategy):
    def __init__(
        self,
        text_color: str,
    ) -> None:
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
