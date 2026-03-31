"""Tests for the renderer abstraction, PIL renderer, and Playwright renderer."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.data.text_block import TextBlock
from src.rendering.base import Renderer
from src.rendering.pil_renderer import PilRenderer
from src.rendering.playwright_renderer import PlaywrightRenderer, _load_css_theme
from src.utils.exceptions import ImageGenerationError
from tests.test_utils import requires_playwright


# -- Renderer ABC -------------------------------------------------------------

class TestRendererABC:
    def test_cannot_instantiate_base(self):
        with pytest.raises(TypeError):
            Renderer()

    def test_subclass_must_implement_render(self):
        class BadRenderer(Renderer):
            @property
            def name(self) -> str:
                return "bad"

        with pytest.raises(TypeError):
            BadRenderer()

    def test_subclass_must_implement_name(self):
        class BadRenderer(Renderer):
            def render(self, blocks):
                return []

        with pytest.raises(TypeError):
            BadRenderer()


# -- PilRenderer ---------------------------------------------------------------

class TestPilRenderer:
    def test_name(self):
        with patch("src.rendering.pil_renderer.ImageGenerator"):
            renderer = PilRenderer()
            assert renderer.name == "pil"

    def test_delegates_to_image_generator(self):
        with patch("src.rendering.pil_renderer.ImageGenerator") as MockGen:
            mock_gen = MagicMock()
            MockGen.return_value = mock_gen
            mock_gen.generate_images.return_value = ["img1", "img2"]

            renderer = PilRenderer()
            blocks = [TextBlock("paragraph", "text")]
            result = renderer.render(blocks)

            mock_gen.generate_images.assert_called_once_with(blocks)
            assert result == ["img1", "img2"]


# -- _load_css_theme -----------------------------------------------------------

class TestLoadCssTheme:
    def test_loads_existing_theme(self, tmp_path):
        css = "body { color: red; }"
        (tmp_path / "my_theme.css").write_text(css)
        result = _load_css_theme("my_theme", themes_dir=tmp_path)
        assert result == css

    def test_raises_for_missing_theme(self, tmp_path):
        with pytest.raises(ImageGenerationError, match="not found"):
            _load_css_theme("nonexistent", themes_dir=tmp_path)

    def test_lists_available_themes_in_error(self, tmp_path):
        (tmp_path / "alpha.css").write_text("")
        (tmp_path / "beta.css").write_text("")
        with pytest.raises(ImageGenerationError, match="alpha.*beta"):
            _load_css_theme("missing", themes_dir=tmp_path)


# -- PlaywrightRenderer --------------------------------------------------------

class TestPlaywrightRenderer:
    def test_name(self):
        with patch("src.rendering.playwright_renderer._load_css_theme", return_value=""):
            renderer = PlaywrightRenderer(theme="dark_modern")
            assert renderer.name == "playwright"

    def test_resolve_css_custom(self, tmp_path):
        """Verify _resolve_css loads a custom CSS file."""
        css_file = tmp_path / "custom.css"
        css_file.write_text("body { background: blue; }")
        renderer = PlaywrightRenderer(custom_css=str(css_file))
        assert renderer._resolve_css() == "body { background: blue; }"

    def test_resolve_css_custom_missing_raises(self, tmp_path):
        renderer = PlaywrightRenderer(custom_css=str(tmp_path / "missing.css"))
        with pytest.raises(ImageGenerationError, match="not found"):
            renderer._resolve_css()

    @requires_playwright
    def test_render_integration(self):
        """Full integration test — requires Playwright + Chromium installed."""
        renderer = PlaywrightRenderer(theme="dark_modern", width=1080, height=1080)
        blocks = [
            TextBlock("title", "Integration Test"),
            TextBlock("paragraph", "This is a test paragraph."),
            TextBlock("bullet_list", "Item A\nItem B\nItem C"),
        ]
        images = renderer.render(blocks)

        assert len(images) >= 1
        for img in images:
            assert img.size == (1080, 1080)
            assert img.mode == "RGB"

    @requires_playwright
    def test_custom_dimensions(self):
        renderer = PlaywrightRenderer(
            theme="dark_modern", width=800, height=600
        )
        blocks = [TextBlock("paragraph", "Hello")]
        images = renderer.render(blocks)
        assert len(images) >= 1
        assert images[0].size == (800, 600)

    @requires_playwright
    def test_custom_font(self):
        """Verify render succeeds with a custom font path."""
        font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if not Path(font).exists():
            pytest.skip("DejaVu font not available")

        renderer = PlaywrightRenderer(theme="dark_modern", font_path=font)
        blocks = [TextBlock("paragraph", "Font test")]
        images = renderer.render(blocks)
        assert len(images) >= 1

    @requires_playwright
    def test_all_css_themes(self):
        """Verify all shipped CSS themes render without error."""
        for theme in ["dark_modern", "light_professional", "vibrant_creative"]:
            renderer = PlaywrightRenderer(theme=theme)
            blocks = [
                TextBlock("title", f"{theme} Theme"),
                TextBlock("paragraph", "Sample content"),
            ]
            images = renderer.render(blocks)
            assert len(images) >= 1, f"Theme {theme} produced no slides"
