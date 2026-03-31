from abc import ABC, abstractmethod
from typing import Tuple

from PIL import Image, ImageFont


class DrawStrategy(ABC):
    """
    Abstract base class for different drawing strategies.
    """

    @abstractmethod
    def draw(
        self, img: Image.Image, text: str, font: ImageFont.FreeTypeFont, current_height: int
    ) -> Tuple[Image.Image, int]:
        """
        Abstract method to be implemented by concrete strategies to draw on the image.

        :param img: The image to draw on.
        :param text: The text to be drawn.
        :param font: The font of the text.
        :param current_height: The current height on the image to draw the text.
        :return: A tuple containing the image with the text drawn and the height of the drawn text in pixels.
        """
        pass
