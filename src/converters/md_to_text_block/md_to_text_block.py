import sys
import textwrap
from typing import List

from src.converters.md_to_text_block.block_parser import (
    TableBlockParser,
    CodeBlockParser,
    BulletListBlockParser,
    HeaderParser,
)
from src.converters.md_to_text_block.sections_parser import SectionParser
from src.data.text_block import TextBlock


class MarkdownToTextBlock:
    """
    A class used to interpret Markdown into text blocks.

    Methods
    -------
    interpret(content: str, max_width: int = 70) -> List[List[TextBlock]]
        Interprets a markdown content into a list of TextBlock objects.
    """

    def __init__(self):
        self.parser = SectionParser()
        self.parsers = [
            CodeBlockParser(),
            BulletListBlockParser(),
            TableBlockParser(),
            HeaderParser(),
        ]
        self.active_parser = None

    def interpret(
        self, content: str, max_width: int = sys.maxsize
    ) -> List[List[TextBlock]]:
        """
        Interprets a markdown content into a list of TextBlock objects.

        Parameters
        ----------
        content : str
            A string representing the entire markdown content.
        max_width : int, optional
            The maximum width for a line of text before it gets wrapped to the next line (default is 70).

        Returns
        -------
        List[List[TextBlock]]
            A list of TextBlock objects, each representing a block of interpreted markdown text.
        """
        sections = self.parser.parse(content)
        blocks = [self._parse_section(section, max_width) for section in sections]

        return blocks

    def _parse_section(self, section: str, max_width: int) -> List[TextBlock]:
        """
        Parses a single section of markdown text into a list of TextBlock objects.

        Parameters
        ----------
        section : str
            A string representing a section of markdown text.
        max_width : int
            The maximum width for a line of text before it gets wrapped to the next line.

        Returns
        -------
        List[TextBlock]
            A list of TextBlock objects, each representing a block of interpreted markdown text.
        """
        section_blocks = []
        lines = section.split("\n")
        self.active_parser = None

        for line in lines:
            # line = line.strip()
            if not self.active_parser:
                for parser in self.parsers:
                    if parser.is_start_line(line):
                        self.active_parser = parser
                        self.active_parser.parse(line)
                        break

                if not self.active_parser:
                    wrapped_lines = textwrap.wrap(line, width=max_width)
                    for wrapped_line in wrapped_lines:
                        section_blocks.append(TextBlock("paragraph", wrapped_line))

            elif self.active_parser:
                if self.active_parser.is_end_line(line):
                    section_blocks.append(self.active_parser.get_block())
                    self.active_parser.reset()
                    self.active_parser = None
                else:
                    self.active_parser.parse(
                        line
                    )  # Parse the line with the active parser
        return section_blocks
