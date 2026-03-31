import pytest

from src.input_output.markdown_reader import MarkdownReader
from src.utils.exceptions import MarkdownReadError


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
    non_existing_file = tmp_path / "non_existing.md"
    with pytest.raises(FileNotFoundError):
        markdown_reader.read(str(non_existing_file))


def test_read_unsupported_extension(tmp_path, markdown_reader):
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Hello", encoding="utf-8")
    with pytest.raises(MarkdownReadError, match="Unsupported file extension"):
        markdown_reader.read(str(txt_file))


def test_read_supported_extensions(tmp_path, markdown_reader):
    for ext in [".md", ".markdown", ".mdown", ".mkd"]:
        f = tmp_path / f"test{ext}"
        f.write_text("content", encoding="utf-8")
        assert markdown_reader.read(str(f)) == "content"


def test_read_invalid_utf8(tmp_path, markdown_reader):
    bad_file = tmp_path / "bad.md"
    bad_file.write_bytes(b"\xff\xfe invalid utf-8 \x80\x81")
    with pytest.raises(MarkdownReadError, match="not valid UTF-8"):
        markdown_reader.read(str(bad_file))


def test_read_empty_file(tmp_path, markdown_reader):
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("", encoding="utf-8")
    assert markdown_reader.read(str(empty_file)) == ""
