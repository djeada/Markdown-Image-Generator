import pytest

from src.converters.md_to_text_block.block_parser import (
    CodeBlockParser,
    HeaderParser,
    TableBlockParser,
    TitleParser,
)
from src.data.text_block import TextBlock


@pytest.fixture
def title_parser():
    return TitleParser()


@pytest.fixture
def header_parser():
    return HeaderParser()


@pytest.fixture
def code_block_parser():
    return CodeBlockParser()


@pytest.fixture
def table_block_parser():
    return TableBlockParser()


def test_title_parser(title_parser):
    assert title_parser.is_start_line("# This is a title")
    assert not title_parser.is_start_line("This is not a title")

    assert title_parser.is_end_line("# This is a title")

    assert title_parser.parse("# This is a title")
    block = title_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "title"
    assert block.data == "This is a title"


def test_header_parser(header_parser):
    assert header_parser.is_start_line("## This is a header")
    assert not header_parser.is_start_line("This is not a header")

    assert header_parser.is_end_line("## This is a header")

    assert header_parser.parse("## This is a header")
    block = header_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "header"
    assert block.data == "This is a header"


def test_code_block_parser(code_block_parser):
    assert code_block_parser.is_start_line("```python")
    assert not code_block_parser.is_end_line("```python")
    assert code_block_parser.is_end_line("```")

    code_block_parser.parse("```python\nThis is code\n```")

    block = code_block_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "code"
    # assert block.data == "This is code"


def test_table_block_parser(table_block_parser):
    assert table_block_parser.is_start_line("| Header 1 | Header 2 |")
    assert not table_block_parser.is_start_line("Not a table line")

    assert table_block_parser.is_end_line("Other content")

    table_block_parser.parse("| Header 1 | Header 2 |")
    table_block_parser.parse("| Row 1 | Data 1 |")

    block = table_block_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "table"
    assert block.data == "| Header 1 | Header 2 |\n| Row 1 | Data 1 |"
