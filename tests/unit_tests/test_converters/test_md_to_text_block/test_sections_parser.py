"""Tests for the SectionParser."""

import pytest

from src.converters.md_to_text_block.sections_parser import SectionParser


@pytest.fixture
def parser():
    return SectionParser()


class TestSectionParser:
    def test_empty_content(self, parser):
        result = parser.parse("")
        assert result == [""]

    def test_single_section(self, parser):
        content = "# Title\n\nSome content here."
        result = parser.parse(content)
        assert len(result) == 1
        assert "# Title" in result[0]
        assert "Some content here." in result[0]

    def test_multiple_sections(self, parser):
        content = "# Title\n\nIntro\n\n## Section 1\n\nContent 1\n\n## Section 2\n\nContent 2"
        result = parser.parse(content)
        assert len(result) == 3
        assert "# Title" in result[0]
        assert "## Section 1" in result[1]
        assert "## Section 2" in result[2]

    def test_no_headers(self, parser):
        content = "Just plain text\nwith multiple lines."
        result = parser.parse(content)
        assert len(result) == 1
        assert "Just plain text" in result[0]

    def test_nested_headers(self, parser):
        content = "# H1\n\nText\n\n## H2\n\nMore text\n\n### H3\n\nDeep text"
        result = parser.parse(content)
        assert len(result) == 3

    def test_content_before_first_header(self, parser):
        content = "Preamble text\n\n# Header\n\nContent"
        result = parser.parse(content)
        assert len(result) == 2
        assert "Preamble text" in result[0]
        assert "# Header" in result[1]

    def test_consecutive_headers(self, parser):
        content = "# First\n## Second\n### Third"
        result = parser.parse(content)
        assert len(result) == 3

    def test_header_with_leading_spaces(self, parser):
        content = "  # Indented Header\n\nContent"
        result = parser.parse(content)
        # Leading spaces still detected as header by lstrip()
        assert len(result) == 1
        assert "# Indented Header" in result[0]
