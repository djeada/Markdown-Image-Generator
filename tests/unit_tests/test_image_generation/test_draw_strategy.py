"""Tests for the draw_strategy module."""

import json
import pytest
from pathlib import Path
from PIL import Image, ImageFont

from src.image_generation.draw_strategies import (
    DrawDefault,
    DrawHeader,
    DrawTitle,
    DrawCode,
    DrawBulletList,
    DrawNumberedList,
    DrawBlockquote,
    DrawHorizontalRule,
    DrawTaskList,
)
from src.utils.config import Config


@pytest.fixture(autouse=True)
def setup_config(tmp_path):
    """Set up a valid config with a real font for draw tests."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not Path(font_path).exists():
        pytest.skip("DejaVu font not available")

    config_data = {
        "PATHS": {
            "DEFAULT_PAGE": "",
            "TITLE_PAGE": "",
            "FINAL_PAGE": "",
            "QUESTION_PAGE": "",
            "FONT": font_path,
        },
        "PAGE_LAYOUT": {
            "TOP_MARGIN": 100,
            "BOTTOM_MARGIN": 100,
            "RIGHT_MARGIN": 80,
            "LEFT_MARGIN": 80,
            "IMAGE_WIDTH": 500,
            "IMAGE_HEIGHT": 500,
            "CHAR_WIDTH": 15,
            "DEFAULT_LINE_HEIGHT": 30,
            "LIST_LINE_HEIGHT": 20,
            "START_INDEX": 0,
        },
        "COLORS": {
            "PAGE_NUMBER_FONT": "#292929",
            "TEXT": "#FFFFFF",
            "BACKGROUND": "#000000",
            "HIGHLIGHT": "#ffab00",
        },
        "CODE_BLOCK": {
            "SCALE_FACTOR": 2,
            "BACKGROUND": "#000000",
            "RADIUS": 20,
            "TOP_PADDING": 50,
        },
        "TABLE": {
            "SCALE_FACTOR": 1,
            "FOREGROUND": "#FFFFFF",
            "BACKGROUND": "#292929",
            "HIGHLIGHT": "#ffab00",
            "HEADER_BG_COLOR": "#8c52ff",
            "HEADER_FG_COLOR": "#000000",
            "HEIGHT": 8,
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config_data))
    Config().init_config(path=config_path)


@pytest.fixture
def font():
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=16)


@pytest.fixture
def base_image():
    return Image.new("RGB", (500, 500), "black")


class TestDrawDefault:
    """Tests for the DrawDefault class."""

    def setup_method(self):
        self.draw_default = DrawDefault(text_color="#FFFFFF")

    def test_parse_formatted_words_plain_text(self):
        text = "Hello world"
        result = self.draw_default.parse_formatted_words(text)
        assert len(result) == 2
        assert result[0] == ("Hello ", "normal")
        assert result[1] == ("world", "normal")

    def test_parse_formatted_words_bold_double_asterisks(self):
        text = "This is **bold** text"
        result = self.draw_default.parse_formatted_words(text)
        bold_words = [word for word, fmt in result if fmt == "bold"]
        assert len(bold_words) == 1
        assert "bold" in bold_words[0]

    def test_parse_formatted_words_bold_underscores(self):
        text = "This is __bold__ text"
        result = self.draw_default.parse_formatted_words(text)
        bold_words = [word for word, fmt in result if fmt == "bold"]
        assert len(bold_words) == 1
        assert "bold" in bold_words[0]

    def test_parse_formatted_words_multiple_bold(self):
        text = "**First** and **second** bold"
        result = self.draw_default.parse_formatted_words(text)
        bold_words = [word for word, fmt in result if fmt == "bold"]
        assert len(bold_words) == 2

    def test_parse_formatted_words_link(self):
        text = "Click [here](https://example.com) for more"
        result = self.draw_default.parse_formatted_words(text)
        link_words = [word for word, fmt in result if fmt == "link"]
        assert len(link_words) == 1
        assert "here" in link_words[0]

    def test_parse_formatted_words_inline_code(self):
        text = "Use `print()` function"
        result = self.draw_default.parse_formatted_words(text)
        code_words = [word for word, fmt in result if fmt == "inline_code"]
        assert len(code_words) == 1

    def test_parse_formatted_words_preserves_order(self):
        text = "One two three four"
        result = self.draw_default.parse_formatted_words(text)
        words = [word.strip() for word, _ in result]
        assert words == ["One", "two", "three", "four"]

    def test_get_color_for_format_bold(self):
        assert self.draw_default.get_color_for_format("bold") == self.draw_default.highlight_color

    def test_get_color_for_format_normal(self):
        assert self.draw_default.get_color_for_format("normal") == self.draw_default.text_color

    def test_get_color_for_format_link(self):
        assert self.draw_default.get_color_for_format("link") == self.draw_default.link_color

    def test_get_color_for_format_italic(self):
        assert self.draw_default.get_color_for_format("italic") == self.draw_default.italic_color

    def test_get_color_for_format_inline_code(self):
        assert self.draw_default.get_color_for_format("inline_code") == self.draw_default.inline_code_fg

    def test_draw_returns_image_and_height(self, base_image, font):
        img, height = self.draw_default.draw(base_image, "Hello world", font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100

    def test_draw_empty_text(self, base_image, font):
        img, height = self.draw_default.draw(base_image, "", font, 100)
        assert isinstance(img, Image.Image)


class TestDrawHeader:

    def test_draw_header(self, base_image, font):
        strategy = DrawHeader(text_color="#FFFFFF")
        img, height = strategy.draw(base_image, "My Header", font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100


class TestDrawTitle:

    def test_draw_title(self, base_image, font):
        strategy = DrawTitle(text_color="#FFFFFF")
        img, height = strategy.draw(base_image, "My Title", font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100

    def test_draw_long_title_wraps(self, base_image, font):
        strategy = DrawTitle(text_color="#FFFFFF")
        long_title = "This is a very long title that should wrap across multiple lines on a small image"
        img, height = strategy.draw(base_image, long_title, font, 100)
        assert height > 100


class TestDrawCode:

    def test_draw_code_block(self, base_image, font):
        strategy = DrawCode()
        code = '```python\nprint("hello")\n```'
        img, height = strategy.draw(base_image, code, font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100

    def test_extract_lexer_name(self):
        strategy = DrawCode()
        name, text = strategy._extract_lexer_name("```python\ncode here\n```")
        assert name == "python"
        assert "code here" in text

    def test_extract_lexer_name_default(self):
        strategy = DrawCode()
        name, text = strategy._extract_lexer_name("just code no markers")
        assert name == "text"

    def test_get_lexer_unknown_language(self):
        strategy = DrawCode()
        lexer = strategy._get_lexer("nonexistent_language_xyz")
        assert lexer.name == "Text only"


class TestDrawBulletList:

    def test_draw_bullet_list(self, base_image, font):
        strategy = DrawBulletList(text_color="#FFFFFF")
        text = "First item\nSecond item\nThird item"
        img, height = strategy.draw(base_image, text, font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100


class TestDrawNumberedList:

    def test_draw_numbered_list(self, base_image, font):
        strategy = DrawNumberedList(text_color="#FFFFFF")
        text = "First item\nSecond item\nThird item"
        img, height = strategy.draw(base_image, text, font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100


class TestDrawBlockquote:

    def test_draw_blockquote(self, base_image, font):
        strategy = DrawBlockquote(text_color="#FFFFFF")
        text = "This is a quote\nWith multiple lines"
        img, height = strategy.draw(base_image, text, font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100


class TestDrawHorizontalRule:

    def test_draw_horizontal_rule(self, base_image, font):
        strategy = DrawHorizontalRule(text_color="#FFFFFF")
        img, height = strategy.draw(base_image, "---", font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100


class TestDrawTaskList:

    def test_draw_task_list(self, base_image, font):
        strategy = DrawTaskList(text_color="#FFFFFF")
        text = "checked:Done task\nunchecked:Todo task"
        img, height = strategy.draw(base_image, text, font, 100)
        assert isinstance(img, Image.Image)
        assert height > 100

    def test_draw_task_list_empty_items_skipped(self, base_image, font):
        strategy = DrawTaskList(text_color="#FFFFFF")
        text = "\n\nchecked:Item\n"
        img, height = strategy.draw(base_image, text, font, 100)
        assert height > 100

