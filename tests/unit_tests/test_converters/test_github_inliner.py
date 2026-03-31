"""Tests for the GitHub URL inliner preprocessor."""

import json
from unittest.mock import patch

import pytest

from src.data.text_block import TextBlock
from src.converters.md_to_text_block.github_inliner import (
    _github_raw_url,
    _is_github_url_block,
    _make_payload,
    inline_github_urls,
    LANG_MAP,
)


class TestGitHubRawUrl:
    def test_basic(self):
        url = _github_raw_url("user", "repo", "main", "src/file.py")
        assert url == "https://raw.githubusercontent.com/user/repo/main/src/file.py"

    def test_nested_path(self):
        url = _github_raw_url("org", "proj", "v2", "a/b/c/d.js")
        assert url == "https://raw.githubusercontent.com/org/proj/v2/a/b/c/d.js"


class TestIsGithubUrlBlock:
    def test_plain_github_url(self):
        block = TextBlock("paragraph", "https://github.com/user/repo/blob/main/src/file.py")
        assert _is_github_url_block(block) is True

    def test_markdown_link(self):
        block = TextBlock("paragraph", "[code](https://github.com/user/repo/blob/main/file.py)")
        assert _is_github_url_block(block) is True

    def test_not_paragraph(self):
        block = TextBlock("header", "https://github.com/user/repo/blob/main/file.py")
        assert _is_github_url_block(block) is False

    def test_mixed_text(self):
        block = TextBlock("paragraph", "See https://github.com/user/repo/blob/main/file.py here")
        assert _is_github_url_block(block) is False

    def test_non_github_url(self):
        block = TextBlock("paragraph", "https://example.com/file.py")
        assert _is_github_url_block(block) is False


class TestMakePayload:
    def test_python_file(self):
        payload = json.loads(_make_payload("user", "repo", "main", "src/main.py", "print('hi')"))
        assert payload["filename"] == "main.py"
        assert payload["language"] == "Python"
        assert payload["content"] == "print('hi')"
        assert payload["owner"] == "user"
        assert payload["repo"] == "repo"
        assert payload["path"] == "src/main.py"

    def test_markdown_file(self):
        payload = json.loads(_make_payload("u", "r", "main", "notes/doc.md", "# Title"))
        assert payload["filename"] == "doc.md"
        assert payload["language"] == "MD"  # .md not in LANG_MAP → fallback


class TestInlineGithubUrls:
    @patch("src.converters.md_to_text_block.github_inliner._fetch_url")
    def test_replaces_python_url_with_github_code(self, mock_fetch):
        mock_fetch.return_value = "def two_sum():\n    pass"

        blocks = [
            TextBlock("title", "Problem"),
            TextBlock("paragraph", "https://github.com/djeada/Leetcode-Solutions/blob/main/src/1_two_sum.py"),
            TextBlock("paragraph", "Done."),
        ]
        result = inline_github_urls(blocks)

        assert len(result) == 3
        assert result[0].type == "title"
        assert result[1].type == "github_code"
        assert result[2].type == "paragraph"

        payload = json.loads(result[1].data)
        assert payload["filename"] == "1_two_sum.py"
        assert payload["language"] == "Python"
        assert "def two_sum():" in payload["content"]

    @patch("src.converters.md_to_text_block.github_inliner._fetch_url")
    def test_replaces_md_url_with_github_notes(self, mock_fetch):
        mock_fetch.return_value = "## Notes\n\nUse hash map."

        blocks = [
            TextBlock("paragraph", "https://github.com/user/repo/blob/main/notes/doc.md"),
        ]
        result = inline_github_urls(blocks)

        assert len(result) == 1
        assert result[0].type == "github_notes"

        payload = json.loads(result[0].data)
        assert "Use hash map." in payload["content"]

    @patch("src.converters.md_to_text_block.github_inliner._fetch_url")
    def test_multiple_urls(self, mock_fetch):
        mock_fetch.side_effect = ["def solve(): pass", "## Approach\n\nUse DP."]

        blocks = [
            TextBlock("paragraph", "https://github.com/u/r/blob/main/src/solve.py"),
            TextBlock("paragraph", "https://github.com/u/r/blob/main/notes/solve.md"),
        ]
        result = inline_github_urls(blocks)

        assert result[0].type == "github_code"
        assert result[1].type == "github_notes"
        assert mock_fetch.call_count == 2

    @patch("src.converters.md_to_text_block.github_inliner._fetch_url")
    def test_fetch_failure_keeps_original(self, mock_fetch):
        mock_fetch.return_value = None

        blocks = [
            TextBlock("paragraph", "https://github.com/u/r/blob/main/missing.py"),
        ]
        result = inline_github_urls(blocks)

        assert len(result) == 1
        assert result[0].type == "paragraph"  # unchanged

    def test_non_url_blocks_unchanged(self):
        blocks = [
            TextBlock("title", "Hello"),
            TextBlock("paragraph", "Just plain text."),
            TextBlock("code", "x = 1"),
        ]
        result = inline_github_urls(blocks)
        assert result == blocks

    @patch("src.converters.md_to_text_block.github_inliner._fetch_url")
    def test_markdown_link_syntax(self, mock_fetch):
        mock_fetch.return_value = "x = 1"

        blocks = [
            TextBlock("paragraph", "[solution](https://github.com/u/r/blob/main/sol.py)"),
        ]
        result = inline_github_urls(blocks)
        assert result[0].type == "github_code"
