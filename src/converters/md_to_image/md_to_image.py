import itertools
import logging
from typing import List, Optional
from PIL import Image

from src.converters.md_to_text_block.github_inliner import inline_github_urls
from src.converters.md_to_text_block.md_to_text_block import MarkdownToTextBlock
from src.input_output.markdown_reader import MarkdownReader
from src.rendering.base import Renderer

logger = logging.getLogger(__name__)


class MarkdownToImageConverter:
    """
    Converts given markdown to images.
    """

    def __init__(
        self,
        input_file: str,
        renderer: Optional[Renderer] = None,
    ) -> None:
        self.input_file = input_file
        self._renderer = renderer

    def _get_renderer(self) -> Renderer:
        """Resolve the renderer, lazily importing to avoid heavy deps at import time."""
        if self._renderer is not None:
            return self._renderer
        # Default: try Playwright, fall back to PIL
        try:
            from src.rendering.playwright_renderer import PlaywrightRenderer
            return PlaywrightRenderer()
        except Exception:
            from src.rendering.pil_renderer import PilRenderer
            logger.info("Playwright unavailable, falling back to PIL renderer")
            return PilRenderer()

    def convert(self) -> List[Image.Image]:
        """
        Convert markdown to images using the configured renderer.

        Returns:
            List[Image.Image]: Generated images.

        Raises:
            FileNotFoundError: If the input file does not exist.
            MarkdownReadError: If the file cannot be read.
            Exception: For other conversion errors (font issues, rendering failures, etc.)
        """
        markdown_reader = MarkdownReader()
        md_to_text = MarkdownToTextBlock()

        content = markdown_reader.read(self.input_file)
        text_blocks = md_to_text.run(content)
        flatten_text_blocks = list(itertools.chain.from_iterable(text_blocks))
        flatten_text_blocks = inline_github_urls(flatten_text_blocks)

        renderer = self._get_renderer()
        logger.info("Using renderer: %s", renderer.name)
        return renderer.render(flatten_text_blocks)
