import pytest

from src.converters.md_to_text_block.block_parser import (
    CodeBlockParser,
    HeaderParser,
    TableBlockParser,
    TitleParser,
    BulletListParser,
    NumberedListParser,
    BlockquoteParser,
    HorizontalRuleParser,
    TaskListParser,
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


@pytest.fixture
def bullet_list_parser():
    return BulletListParser()


@pytest.fixture
def numbered_list_parser():
    return NumberedListParser()


@pytest.fixture
def blockquote_parser():
    return BlockquoteParser()


@pytest.fixture
def horizontal_rule_parser():
    return HorizontalRuleParser()


@pytest.fixture
def task_list_parser():
    return TaskListParser()


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


def test_bullet_list_parser(bullet_list_parser):
    """Test bullet list parsing with - prefix."""
    assert bullet_list_parser.is_start_line("- First item")
    assert not bullet_list_parser.is_start_line("Not a list item")

    # Reset to test * prefix
    bullet_list_parser.reset()
    assert bullet_list_parser.is_start_line("* Second item")

    # Reset and test full parsing
    bullet_list_parser.reset()
    bullet_list_parser.is_start_line("- First item")  # Trigger parsing mode
    bullet_list_parser.parse("- First item")
    bullet_list_parser.parse("- Second item")
    
    # End the list with a non-list line
    assert bullet_list_parser.is_end_line("Other content")

    block = bullet_list_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "bullet_list"
    assert block.data == "First item\nSecond item"


def test_numbered_list_parser(numbered_list_parser):
    """Test numbered list parsing with numeric prefix."""
    assert numbered_list_parser.is_start_line("1. First item")
    assert not numbered_list_parser.is_start_line("Not a list item")

    # Reset to test another numbered item
    numbered_list_parser.reset()
    assert numbered_list_parser.is_start_line("2. Second item")

    # Reset and test full parsing
    numbered_list_parser.reset()
    numbered_list_parser.is_start_line("1. First item")  # Trigger parsing mode
    numbered_list_parser.parse("1. First item")
    numbered_list_parser.parse("2. Second item")
    numbered_list_parser.parse("3. Third item")
    
    # End the list with a non-list line
    assert numbered_list_parser.is_end_line("Other content")

    block = numbered_list_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "numbered_list"
    assert block.data == "First item\nSecond item\nThird item"


def test_blockquote_parser(blockquote_parser):
    """Test blockquote parsing with > prefix."""
    assert blockquote_parser.is_start_line("> This is a quote")
    assert not blockquote_parser.is_start_line("Not a quote")

    blockquote_parser.parse("> This is a quote")
    blockquote_parser.parse("> Another line")
    
    # End the quote with a non-quote line
    assert blockquote_parser.is_end_line("Other content")

    block = blockquote_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "blockquote"
    assert block.data == "This is a quote\nAnother line"


def test_horizontal_rule_parser(horizontal_rule_parser):
    """Test horizontal rule parsing."""
    assert horizontal_rule_parser.is_start_line("---")
    assert horizontal_rule_parser.is_start_line("***")
    assert horizontal_rule_parser.is_start_line("___")
    assert not horizontal_rule_parser.is_start_line("--")  # Too short
    assert not horizontal_rule_parser.is_start_line("Not a rule")

    # Single line element
    assert horizontal_rule_parser.is_end_line("---")

    horizontal_rule_parser.parse("---")
    block = horizontal_rule_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "horizontal_rule"
    assert block.data == "---"


def test_task_list_parser(task_list_parser):
    """Test task list parsing with checkbox syntax."""
    # Test unchecked task
    assert task_list_parser.is_start_line("- [ ] Unchecked task")
    assert not task_list_parser.is_start_line("- Regular list item")
    
    # Reset to test checked task
    task_list_parser.reset()
    assert task_list_parser.is_start_line("- [x] Checked task")
    
    # Reset to test uppercase X
    task_list_parser.reset()
    assert task_list_parser.is_start_line("- [X] Checked task")
    
    # Reset to test * prefix
    task_list_parser.reset()
    assert task_list_parser.is_start_line("* [ ] Unchecked task")
    
    # Reset and test full parsing
    task_list_parser.reset()
    task_list_parser.is_start_line("- [x] First task")  # Trigger parsing mode
    task_list_parser.parse("- [x] First task")
    task_list_parser.parse("- [ ] Second task")
    task_list_parser.parse("- [X] Third task")
    
    # End the list with a non-task line
    assert task_list_parser.is_end_line("Other content")
    
    block = task_list_parser.get_block()
    assert isinstance(block, TextBlock)
    assert block.type == "task_list"
    assert "checked:First task" in block.data
    assert "unchecked:Second task" in block.data
    assert "checked:Third task" in block.data
