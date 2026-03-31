"""PIL rendering backend — wraps the existing ImageGenerator."""

from typing import List

from PIL import Image

from src.data.text_block import TextBlock
from src.image_generation.image_generator import ImageGenerator
from src.rendering.base import Renderer


class PilRenderer(Renderer):
    """Renders TextBlocks to images using the legacy PIL/Pillow pipeline."""

    def __init__(self) -> None:
        self._generator = ImageGenerator()

    @property
    def name(self) -> str:
        return "pil"

    def render(self, blocks: List[TextBlock]) -> List[Image.Image]:
        return self._generator.generate_images(blocks)
