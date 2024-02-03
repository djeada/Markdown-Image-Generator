import sys
import textwrap
from typing import List, Optional

from src.converters.md_to_text_block.block_parser import (
    BlockParser,
    CodeBlockParser,
    TableBlockParser,
    HeaderParser,
)
from src.converters.md_to_text_block.sections_parser import SectionParser
from src.data.text_block import TextBlock


class MarkdownToTextBlock:
    """
    A class to interpret Markdown into text blocks.
    """

    def __init__(self, is_title: bool = False):
        self.is_title = is_title
        self.parser = SectionParser()
        self.parsers = [CodeBlockParser(), TableBlockParser(), HeaderParser()]

        self.active_parser = None

    def run(self, content: str, max_width: int = sys.maxsize) -> List[List[TextBlock]]:
        if self.is_title:
            return [[TextBlock("title", content)]]

        sections = self.parser.parse(content)
        return [self._parse_section(section, max_width) for section in sections]

    def _parse_section(self, section: str, max_width: int) -> List[TextBlock]:
        section_blocks = []
        lines = section.split("\n")

        for line in lines:
            parser = self._get_active_parser(line)
            if parser:
                parser.parse(line)
                if parser.is_end_line(line):
                    section_blocks.append(parser.get_block())
                    self.active_parser = None
            else:
                section_blocks.extend(self._wrap_line(line, max_width))

        return section_blocks

    def _get_active_parser(self, line: str) -> Optional[BlockParser]:
        if not self.active_parser:
            for parser in self.parsers:
                if parser.is_start_line(line):
                    self.active_parser = parser
                    return parser
        return self.active_parser

    @staticmethod
    def _wrap_line(line: str, max_width: int) -> List[TextBlock]:
        wrapped_lines = textwrap.wrap(line, width=max_width)
        return [TextBlock("paragraph", wl) for wl in wrapped_lines]
