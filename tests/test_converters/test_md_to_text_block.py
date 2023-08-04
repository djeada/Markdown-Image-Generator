from src.converters.md_to_text_block import MarkdownToTextBlock
from src.data.text_block import TextBlock


def test_markdown_interpreter():
    markdown_interpreter = MarkdownToTextBlock()

    # Define a simple markdown string and expected output
    content = """## Header 1

    This is a paragraph.

    ### Header 2

    This is another paragraph.

    * Bullet 1
    * Bullet 2
    * Bullet 3
    """

    expected_output = [
        [
            TextBlock("header", "Header 1"),
            TextBlock("paragraph", "This is a paragraph."),
        ],
        [
            TextBlock("header", "Header 2"),
            TextBlock("paragraph", "This is another paragraph."),
            TextBlock("bullet", "Bullet 1\nBullet 2\nBullet 3"),
        ],
    ]

    result = markdown_interpreter.interpret(content)
    assert result == expected_output


def test_markdown_interpreter_code_block():
    markdown_interpreter = MarkdownToTextBlock()

    section = """# Header 1

    * This is a bullet point.

    ```
    int a = 10;
    int b = 30;
    ```
    """
    result = markdown_interpreter._parse_section(section, 70)
    expected = [
        TextBlock("header", "Header 1"),
        TextBlock("bullet", "This is a bullet point."),
        TextBlock("code", "int a = 10;\nint b = 30;"),
    ]
    assert result == expected


def test_markdown_interpreter_tables():
    markdown_interpreter = MarkdownToTextBlock()

    section = """
        # Header

        Here is a table:

        | Column 1 | Column 2 |
        | -------- | -------- |
        | Data 1   | Data 2   |
        | Data 3   | Data 4   |
        """

    blocks = markdown_interpreter._parse_section(section, 70)

    assert len(blocks) == 3
    assert blocks[0] == TextBlock("header", "Header")
    assert blocks[1] == TextBlock("paragraph", "Here is a table:")
    assert blocks[2] == TextBlock(
        "table",
        "| Column 1 | Column 2 |\n| -------- | -------- |\n| Data 1   | Data 2   |\n| Data 3   | Data 4   |",
    )
