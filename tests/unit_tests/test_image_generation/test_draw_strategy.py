"""Tests for the draw_strategy module."""

import pytest
from src.image_generation.draw_strategy import DrawDefault


class TestDrawDefault:
    """Tests for the DrawDefault class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.draw_default = DrawDefault(text_color="#FFFFFF")

    def test_parse_formatted_words_plain_text(self):
        """Test parsing plain text without any formatting."""
        text = "Hello world"
        result = self.draw_default.parse_formatted_words(text)
        
        assert len(result) == 2
        assert result[0] == ("Hello ", "normal")
        assert result[1] == ("world", "normal")

    def test_parse_formatted_words_bold_double_asterisks(self):
        """Test parsing bold text with double asterisks."""
        text = "This is **bold** text"
        result = self.draw_default.parse_formatted_words(text)
        
        # Check that "bold" is marked as bold
        bold_words = [word for word, fmt in result if fmt == "bold"]
        assert len(bold_words) == 1
        assert "bold" in bold_words[0]

    def test_parse_formatted_words_bold_underscores(self):
        """Test parsing bold text with double underscores."""
        text = "This is __bold__ text"
        result = self.draw_default.parse_formatted_words(text)
        
        # Check that "bold" is marked as bold
        bold_words = [word for word, fmt in result if fmt == "bold"]
        assert len(bold_words) == 1
        assert "bold" in bold_words[0]

    def test_parse_formatted_words_multiple_bold(self):
        """Test parsing text with multiple bold sections."""
        text = "**First** and **second** bold"
        result = self.draw_default.parse_formatted_words(text)
        
        bold_words = [word for word, fmt in result if fmt == "bold"]
        assert len(bold_words) == 2

    def test_parse_formatted_words_link(self):
        """Test parsing markdown links."""
        text = "Click [here](https://example.com) for more"
        result = self.draw_default.parse_formatted_words(text)
        
        # Check that "here" is marked as link
        link_words = [word for word, fmt in result if fmt == "link"]
        assert len(link_words) == 1
        assert "here" in link_words[0]

    def test_parse_formatted_words_preserves_order(self):
        """Test that word order is preserved."""
        text = "One two three four"
        result = self.draw_default.parse_formatted_words(text)
        
        words = [word.strip() for word, _ in result]
        assert words == ["One", "two", "three", "four"]

    def test_get_color_for_format_bold(self):
        """Test color selection for bold format."""
        color = self.draw_default.get_color_for_format("bold")
        assert color == self.draw_default.highlight_color

    def test_get_color_for_format_normal(self):
        """Test color selection for normal format."""
        color = self.draw_default.get_color_for_format("normal")
        assert color == self.draw_default.text_color

    def test_get_color_for_format_link(self):
        """Test color selection for link format."""
        color = self.draw_default.get_color_for_format("link")
        assert color == self.draw_default.link_color

    def test_get_color_for_format_italic(self):
        """Test color selection for italic format."""
        color = self.draw_default.get_color_for_format("italic")
        assert color == self.draw_default.italic_color
