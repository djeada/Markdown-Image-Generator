"""Playwright (headless Chromium) rendering backend.

Converts TextBlocks → HTML+CSS, then uses Playwright to screenshot
each slide div into a PIL Image.
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from PIL import Image

from src.data.text_block import TextBlock
from src.rendering.base import Renderer
from src.rendering.html_builder import build_slides_html
from src.utils.config import Config
from src.utils.exceptions import ImageGenerationError

logger = logging.getLogger(__name__)

# Default search path for CSS themes
_CSS_THEMES_DIR = Path(__file__).resolve().parent.parent.parent / "themes" / "css"


def _load_css_theme(theme_name: str, themes_dir: Optional[Path] = None) -> str:
    """Load a CSS theme file by name.

    Args:
        theme_name: Theme name (e.g. 'dark_modern'). The .css extension is appended.
        themes_dir: Directory to search. Defaults to ``themes/css/``.

    Returns:
        CSS content as a string.

    Raises:
        ImageGenerationError: If the theme file is not found.
    """
    search_dir = themes_dir or _CSS_THEMES_DIR
    css_path = search_dir / f"{theme_name}.css"
    if not css_path.is_file():
        available = [p.stem for p in sorted(search_dir.glob("*.css"))]
        raise ImageGenerationError(
            f"CSS theme '{theme_name}' not found at {css_path}. "
            f"Available: {', '.join(available) or '(none)'}"
        )
    return css_path.read_text(encoding="utf-8")


class PlaywrightRenderer(Renderer):
    """Renders TextBlocks to images using headless Chromium via Playwright.

    Args:
        theme: CSS theme name (default: from config or 'dark_modern').
        font_path: Path to a .ttf/.otf font for @font-face injection.
        width: Slide width in pixels.
        height: Slide height in pixels.
        css_themes_dir: Override the CSS themes directory.
        device_scale_factor: Chromium device pixel ratio (default 2 for retina).
        custom_css: Path (string or :class:`~pathlib.Path`) to a custom CSS
            file.  When provided the file is loaded directly instead of
            resolving a named theme from the themes directory.
    """

    def __init__(
        self,
        theme: Optional[str] = None,
        font_path: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        css_themes_dir: Optional[Path] = None,
        device_scale_factor: float = 2.0,
        custom_css: Optional[str] = None,
    ) -> None:
        config = Config()
        self._theme = theme or config.get("THEME", {}).get("NAME", "dark_modern")
        self._font_path = font_path or config.get("PATHS", {}).get("FONT")
        self._width = width or config.get("PAGE_LAYOUT", {}).get("IMAGE_WIDTH", 1080)
        self._height = height or config.get("PAGE_LAYOUT", {}).get("IMAGE_HEIGHT", 1080)
        self._css_dir = css_themes_dir
        self._scale = device_scale_factor
        self._custom_css = custom_css

    @property
    def name(self) -> str:
        return "playwright"

    def _resolve_css(self) -> str:
        """Return CSS content — from a custom file or a named theme."""
        if self._custom_css:
            css_path = Path(self._custom_css)
            if not css_path.is_file():
                raise ImageGenerationError(
                    f"Custom CSS file not found: {css_path}"
                )
            return css_path.read_text(encoding="utf-8")
        return _load_css_theme(self._theme, self._css_dir)

    def render(self, blocks: List[TextBlock]) -> List[Image.Image]:
        """Render blocks to images via Playwright.

        Opens a headless Chromium browser, loads the HTML+CSS, then
        screenshots each ``.slide`` div individually.

        Returns:
            List of PIL Image objects (one per slide).
        """
        from playwright.sync_api import sync_playwright

        css = self._resolve_css()
        html_content = build_slides_html(
            blocks,
            css=css,
            font_path=self._font_path,
            width=self._width,
            height=self._height,
        )

        images: List[Image.Image] = []

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": self._width, "height": self._height},
                device_scale_factor=self._scale,
            )

            page.set_content(html_content, wait_until="networkidle")

            # Wait for the pagination JS to complete
            page.wait_for_selector(".slide", timeout=5000)

            slides = page.query_selector_all(".slide")
            if not slides:
                logger.warning("No slides generated from HTML content")
                browser.close()
                return images

            logger.info("Rendering %d slide(s) with Playwright", len(slides))

            for i, slide in enumerate(slides):
                png_bytes = slide.screenshot(type="png")
                img = Image.open(BytesIO(png_bytes)).convert("RGB")
                # Resize to target dimensions (screenshot may be scaled by device_scale_factor)
                if img.size != (self._width, self._height):
                    img = img.resize(
                        (self._width, self._height), Image.Resampling.LANCZOS
                    )
                images.append(img)

            browser.close()

        return images
