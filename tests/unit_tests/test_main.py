from unittest.mock import patch

from src.main import build_renderer


def test_build_renderer_auto_falls_back_to_pil_when_playwright_unavailable():
    with patch(
        "src.rendering.playwright_renderer.playwright_runtime_available",
        return_value=False,
    ), patch("src.rendering.pil_renderer.ImageGenerator"):
        renderer = build_renderer(
            renderer_name=None,
            theme=None,
            font_path=None,
            width=None,
            height=None,
            custom_css=None,
        )

    assert renderer.name == "pil"


def test_build_renderer_auto_prefers_playwright_when_available():
    with patch(
        "src.rendering.playwright_renderer.playwright_runtime_available",
        return_value=True,
    ), patch("src.rendering.playwright_renderer.PlaywrightRenderer") as mock_renderer:
        renderer = object()
        mock_renderer.return_value = renderer

        result = build_renderer(
            renderer_name=None,
            theme="dark_modern",
            font_path="font.ttf",
            width=800,
            height=600,
            custom_css="custom.css",
        )

    assert result is renderer
    mock_renderer.assert_called_once_with(
        theme="dark_modern",
        font_path="font.ttf",
        width=800,
        height=600,
        custom_css="custom.css",
    )


def test_build_renderer_explicit_playwright_bypasses_auto_fallback():
    with patch(
        "src.rendering.playwright_renderer.playwright_runtime_available",
        return_value=False,
    ), patch("src.rendering.playwright_renderer.PlaywrightRenderer") as mock_renderer:
        renderer = object()
        mock_renderer.return_value = renderer

        result = build_renderer(
            renderer_name="playwright",
            theme=None,
            font_path=None,
            width=None,
            height=None,
            custom_css=None,
        )

    assert result is renderer
    mock_renderer.assert_called_once_with(
        theme=None,
        font_path=None,
        width=None,
        height=None,
        custom_css=None,
    )
