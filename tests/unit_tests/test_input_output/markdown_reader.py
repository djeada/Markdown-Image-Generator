import pytest
import os

from src.input_output.markdown_reader import MarkdownReader


@pytest.fixture
def markdown_reader():
    return MarkdownReader()


def test_read_existing_file(tmp_path, markdown_reader):
    # Create a temporary markdown file with content
    markdown_content = "This is a test markdown file."
    markdown_file = tmp_path / "test.md"
    markdown_file.write_text(markdown_content, encoding="utf-8")

    # Read the temporary markdown file using the MarkdownReader instance
    content = markdown_reader.read(str(markdown_file))

    # Check if the content matches
    assert content == markdown_content


def test_read_non_existing_file(tmp_path, markdown_reader):
    # Attempt to read a non-existing markdown file
    non_existing_file = tmp_path / "non_existing.md"

    # Read the non-existing markdown file using the MarkdownReader instance
    content = markdown_reader.read(str(non_existing_file))

    # Check if the content is None (indicating an error)
    assert content is None


def test_read_io_error(tmp_path, markdown_reader):
    # Attempt to read a file in a non-readable directory to trigger an IOError
    io_error_file = tmp_path / "io_error" / "test.md"

    # Attempt to read the file with an IOError using the MarkdownReader instance
    content = markdown_reader.read(str(io_error_file))

    # Check if the content is None (indicating an error)
    assert content is None
