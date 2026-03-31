"""Tests for the HTML builder module."""

import json

import pytest

from src.data.text_block import TextBlock
from src.rendering.html_builder import (
    _apply_inline_formatting,
    _render_paragraph,
    _render_title,
    _render_header,
    _render_code,
    _render_bullet_list,
    _render_numbered_list,
    _render_blockquote,
    _render_horizontal_rule,
    _render_table,
    _render_task_list,
    _render_github_code,
    _render_github_notes,
    blocks_to_html,
    build_slides_html,
)


# -- Inline formatting -------------------------------------------------------

class TestInlineFormatting:
    def test_bold(self):
        assert "<strong>bold</strong>" in _apply_inline_formatting("**bold**")

    def test_italic(self):
        assert "<em>italic</em>" in _apply_inline_formatting("*italic*")

    def test_inline_code(self):
        result = _apply_inline_formatting("`code`")
        assert '<code class="inline">code</code>' in result

    def test_link(self):
        result = _apply_inline_formatting("[click](http://example.com)")
        assert '<a href="http://example.com">click</a>' in result

    def test_strikethrough(self):
        assert "<del>old</del>" in _apply_inline_formatting("~~old~~")

    def test_html_escape(self):
        result = _apply_inline_formatting("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_nested_bold_italic(self):
        result = _apply_inline_formatting("**bold *nested***")
        assert "<strong>" in result


# -- Block renderers ----------------------------------------------------------

class TestBlockRenderers:
    def test_paragraph(self):
        block = TextBlock("paragraph", "Hello world")
        assert _render_paragraph(block) == "<p>Hello world</p>"

    def test_title(self):
        block = TextBlock("title", "My Title")
        result = _render_title(block)
        assert '<h1 class="title">My Title</h1>' == result

    def test_header(self):
        block = TextBlock("header", "Section")
        assert _render_header(block) == "<h2>Section</h2>"

    def test_code_block_with_language(self):
        block = TextBlock("code", "```python\nprint('hi')\n```")
        result = _render_code(block)
        assert 'class="language-python"' in result
        assert "print(&#x27;hi&#x27;)" in result
        assert "```" not in result

    def test_code_block_no_language(self):
        block = TextBlock("code", "```\nsome code\n```")
        result = _render_code(block)
        assert 'class="language-' not in result
        assert "some code" in result

    def test_bullet_list(self):
        block = TextBlock("bullet_list", "item 1\nitem 2\nitem 3")
        result = _render_bullet_list(block)
        assert "<ul>" in result
        assert result.count("<li>") == 3

    def test_numbered_list(self):
        block = TextBlock("numbered_list", "first\nsecond")
        result = _render_numbered_list(block)
        assert "<ol>" in result
        assert result.count("<li>") == 2

    def test_blockquote(self):
        block = TextBlock("blockquote", "wise words")
        result = _render_blockquote(block)
        assert "<blockquote>" in result
        assert "wise words" in result

    def test_horizontal_rule(self):
        block = TextBlock("horizontal_rule", "")
        assert _render_horizontal_rule(block) == "<hr>"

    def test_table(self):
        data = "Col1 | Col2\n---|---\nA | B\nC | D"
        block = TextBlock("table", data)
        result = _render_table(block)
        assert "<thead>" in result
        assert "<th>" in result
        assert result.count("<td>") == 4
        # Separator row should NOT appear
        assert "---" not in result

    def test_task_list_checked_and_unchecked(self):
        block = TextBlock("task_list", "checked:Done item\nunchecked:Pending item")
        result = _render_task_list(block)
        assert 'class="task checked"' in result
        assert 'class="task unchecked"' in result
        assert "Done item" in result
        assert "Pending item" in result


# -- blocks_to_html -----------------------------------------------------------

class TestBlocksToHtml:
    def test_empty_list(self):
        assert blocks_to_html([]) == ""

    def test_multiple_blocks(self):
        blocks = [
            TextBlock("title", "Title"),
            TextBlock("paragraph", "Body text"),
            TextBlock("horizontal_rule", ""),
        ]
        result = blocks_to_html(blocks)
        assert "<h1" in result
        assert "<p>" in result
        assert "<hr>" in result

    def test_unknown_type_falls_back_to_paragraph(self):
        block = TextBlock("unknown_type", "fallback text")
        result = blocks_to_html([block])
        assert "<p>fallback text</p>" == result


# -- build_slides_html --------------------------------------------------------

class TestBuildSlidesHtml:
    def test_returns_html_document(self):
        blocks = [TextBlock("paragraph", "Hello")]
        result = build_slides_html(blocks)
        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "</html>" in result

    def test_contains_pagination_script(self):
        blocks = [TextBlock("paragraph", "Hello")]
        result = build_slides_html(blocks)
        assert "Paginate content into fixed-size slides" in result

    def test_embeds_css(self):
        css = ".slide { background: red; }"
        result = build_slides_html([TextBlock("paragraph", "x")], css=css)
        assert ".slide { background: red; }" in result

    def test_embeds_font_face(self):
        result = build_slides_html(
            [TextBlock("paragraph", "x")],
            font_path="/usr/share/fonts/test.ttf",
        )
        assert "@font-face" in result
        assert "file:///usr/share/fonts/test.ttf" in result

    def test_no_font_face_when_no_font(self):
        result = build_slides_html([TextBlock("paragraph", "x")])
        assert "@font-face" not in result

    def test_custom_dimensions(self):
        result = build_slides_html(
            [TextBlock("paragraph", "x")], width=1920, height=1080
        )
        assert "1920" in result
        assert "1080" in result


# -- GitHub file renderers ----------------------------------------------------

class TestGithubCodeRenderer:
    def _make_block(self, **overrides):
        payload = {
            "owner": "user", "repo": "project", "ref": "main",
            "path": "src/main.py", "filename": "main.py",
            "language": "Python", "content": "def hello():\n    pass",
        }
        payload.update(overrides)
        return TextBlock("github_code", json.dumps(payload))

    def test_renders_file_header(self):
        result = _render_github_code(self._make_block())
        assert "github-file" in result
        assert "github-file-header" in result
        assert "main.py" in result
        assert "Python" in result

    def test_renders_repo_path(self):
        result = _render_github_code(self._make_block())
        assert "user/project" in result
        assert "src/main.py" in result

    def test_renders_code_content(self):
        result = _render_github_code(self._make_block())
        assert "def hello():" in result
        assert "code-block" in result

    def test_escapes_html_in_code(self):
        block = self._make_block(content="x = 1 < 2 && y > 3")
        result = _render_github_code(block)
        assert "&lt;" in result
        assert "&amp;" in result

    def test_language_class(self):
        result = _render_github_code(self._make_block())
        assert 'language-python' in result


class TestGithubNotesRenderer:
    def _make_block(self, **overrides):
        payload = {
            "owner": "user", "repo": "project", "ref": "main",
            "path": "notes/doc.md", "filename": "doc.md",
            "language": "Notes", "content": "## Heading\n\nSome explanation.\n\n- Point one\n- Point two",
        }
        payload.update(overrides)
        return TextBlock("github_notes", json.dumps(payload))

    def test_renders_file_header(self):
        result = _render_github_notes(self._make_block())
        assert "github-file" in result
        assert "github-notes" in result
        assert "doc.md" in result

    def test_renders_heading(self):
        result = _render_github_notes(self._make_block())
        assert "notes-heading" in result
        assert "Heading" in result

    def test_renders_paragraph(self):
        result = _render_github_notes(self._make_block())
        assert "Some explanation." in result

    def test_renders_list_items(self):
        result = _render_github_notes(self._make_block())
        assert "<li>" in result
        assert "Point one" in result

    def test_blocks_to_html_dispatch(self):
        """github_code and github_notes are in the block renderer dispatch."""
        code_block = TextBlock("github_code", json.dumps({
            "owner": "u", "repo": "r", "ref": "m", "path": "f.py",
            "filename": "f.py", "language": "Python", "content": "x=1",
        }))
        result = blocks_to_html([code_block])
        assert "github-file" in result
