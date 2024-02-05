import pytest

from src.data.text_block import TextBlock, BlockType


@pytest.fixture
def sample_text_block():
    # Create a sample TextBlock instance for testing
    paragraph_block = TextBlock(BlockType.PARAGRAPH, "This is a paragraph.")
    header_block = TextBlock(BlockType.HEADER, "Header 1", children=[paragraph_block])
    return header_block


def test_add_child(sample_text_block):
    # Test adding a child TextBlock to the sample TextBlock
    new_child_block = TextBlock(BlockType.PARAGRAPH, "This is a child " "paragraph.")
    sample_text_block.add_child(new_child_block)
    assert len(sample_text_block.children) == 2
    assert sample_text_block.children[1] == new_child_block


def test_representation(sample_text_block):
    # Test the __repr__ method of TextBlock
    expected_repr = (
        "TextBlock(type=<BlockType.HEADER: 2>, data='Header 1', "
        "children=[TextBlock(type=<BlockType.PARAGRAPH: 1>, "
        "data='This is a paragraph.', children=[])])"
    )
    assert repr(sample_text_block) == expected_repr


def test_equality(sample_text_block):
    # Test the __eq__ method of TextBlock
    same_text_block = TextBlock(
        BlockType.HEADER,
        "Header 1",
        children=[TextBlock(BlockType.PARAGRAPH, "This is a paragraph.")],
    )
    different_text_block = TextBlock(
        BlockType.PARAGRAPH, "This is a different paragraph."
    )
    assert sample_text_block == same_text_block
    assert sample_text_block != different_text_block
