from src.converters.sections_parser import SectionParser


def test_parse_sections():
    parser = SectionParser()
    content = """## Header 1

This is a paragraph.

### Header 2

This is another paragraph.
"""

    sections = parser.parse(content)

    assert len(sections) == 2
    assert sections[0] == "## Header 1\n\nThis is a paragraph.\n"
    assert sections[1] == "### Header 2\n\nThis is another paragraph.\n"
