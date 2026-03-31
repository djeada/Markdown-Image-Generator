"""Abstract base class for rendering backends."""

from abc import ABC, abstractmethod
from typing import List, Optional

from PIL import Image

from src.data.text_block import TextBlock


class Renderer(ABC):
    """Base class that all rendering backends must implement.

    A renderer converts a list of parsed TextBlocks into a list of
    PIL Image objects (one per page/slide).
    """

    @abstractmethod
    def render(self, blocks: List[TextBlock]) -> List[Image.Image]:
        """Render text blocks into images.

        Args:
            blocks: Flat list of parsed TextBlock objects.

        Returns:
            List of PIL Image objects, one per page/slide.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable renderer name (e.g. 'pil', 'playwright')."""
        ...
