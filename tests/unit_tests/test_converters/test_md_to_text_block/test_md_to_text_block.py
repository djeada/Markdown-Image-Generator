from src.converters.md_to_text_block.md_to_text_block import MarkdownToTextBlock


def test_markdown_to_text_block_distinguishes_titles_from_headers():
    parser = MarkdownToTextBlock()

    blocks = parser.run("# Title\n\n## Section\n\n### Subsection\n\nParagraph text")
    flat_blocks = [block for section in blocks for block in section if block.data]

    assert [block.type for block in flat_blocks[:4]] == [
        "title",
        "header",
        "header",
        "paragraph",
    ]
    assert [block.data for block in flat_blocks[:3]] == [
        "Title",
        "Section",
        "Subsection",
    ]


def test_markdown_to_text_block_handles_unspaced_headings():
    parser = MarkdownToTextBlock()

    blocks = parser.run("#Title\n\n##Section")
    flat_blocks = [block for section in blocks for block in section if block.data]

    assert [block.type for block in flat_blocks] == ["title", "header"]
    assert [block.data for block in flat_blocks] == ["Title", "Section"]
