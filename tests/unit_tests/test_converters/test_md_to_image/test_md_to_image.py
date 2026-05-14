"""Tests for MarkdownToImageConverter."""

from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from src.converters.md_to_image.md_to_image import MarkdownToImageConverter


class TestMarkdownToImageConverter:
    def test_convert_uses_provided_renderer(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Hello\n\nWorld\n")

        mock_renderer = MagicMock()
        mock_img = Image.new("RGB", (100, 100), "red")
        mock_renderer.render.return_value = [mock_img]

        converter = MarkdownToImageConverter(
            input_file=str(md_file), renderer=mock_renderer
        )
        images = converter.convert()

        assert len(images) == 1
        mock_renderer.render.assert_called_once()

    def test_convert_missing_file_raises(self, tmp_path):
        converter = MarkdownToImageConverter(
            input_file=str(tmp_path / "nonexistent.md"),
            renderer=MagicMock(),
        )
        with pytest.raises(FileNotFoundError):
            converter.convert()

    def test_get_renderer_falls_back_to_pil(self):
        with patch(
            "src.converters.md_to_image.md_to_image.playwright_runtime_available",
            return_value=False,
        ), patch("src.rendering.pil_renderer.ImageGenerator"):
            converter = MarkdownToImageConverter(input_file="dummy.md")
            renderer = converter._get_renderer()
            assert renderer.name == "pil"

    def test_get_renderer_does_not_swallow_playwright_initialization_errors(self):
        with patch(
            "src.converters.md_to_image.md_to_image.playwright_runtime_available",
            return_value=True,
        ), patch(
            "src.rendering.playwright_renderer.PlaywrightRenderer",
            side_effect=RuntimeError("broken renderer"),
        ):
            converter = MarkdownToImageConverter(input_file="dummy.md")

            with pytest.raises(RuntimeError, match="broken renderer"):
                converter._get_renderer()
