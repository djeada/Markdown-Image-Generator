from pathlib import Path

from PIL import Image, ImageDraw
from src.data.background_image_type import BackgroundImageType
from src.utils.config import Config
from src.utils.other import hex_to_rgba


class BlockImageFactory:
    _config: Config = Config()

    PATHS_TO_IMAGES: dict = {
        BackgroundImageType.TITLE: _config["PATHS"]["TITLE_PAGE"],
        BackgroundImageType.NORMAL: _config["PATHS"]["DEFAULT_PAGE"],
        BackgroundImageType.FINAL: _config["PATHS"]["FINAL_PAGE"],
        BackgroundImageType.QUESTION: _config["PATHS"]["QUESTION_PAGE"],
    }

    @classmethod
    def _create_gradient_image(cls, width: int, height: int) -> Image.Image:
        """Create a vertical gradient background image."""
        theme_config = cls._config.get("THEME", {})
        gradient_config = theme_config.get("GRADIENT", {})
        
        start_color = gradient_config.get("START_COLOR", "#1a1a2e")
        end_color = gradient_config.get("END_COLOR", "#16213e")
        
        # Parse colors
        start_rgba = hex_to_rgba(start_color)
        end_rgba = hex_to_rgba(end_color)
        
        # Create base image
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(start_rgba[0] + (end_rgba[0] - start_rgba[0]) * ratio)
            g = int(start_rgba[1] + (end_rgba[1] - start_rgba[1]) * ratio)
            b = int(start_rgba[2] + (end_rgba[2] - start_rgba[2]) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image

    @classmethod
    def create_background_image(
        cls, block_type_str: str, width: int, height: int
    ) -> Image.Image:
        block_type = cls._translate_block_type(block_type_str)
        bg_image_path = cls.PATHS_TO_IMAGES.get(block_type)

        # Check if gradient is enabled
        theme_config = cls._config.get("THEME", {})
        gradient_config = theme_config.get("GRADIENT", {})
        gradient_enabled = gradient_config.get("ENABLED", False)

        try:
            if gradient_enabled:
                image = cls._create_gradient_image(width, height)
            elif bg_image_path is not None and Path(bg_image_path).is_file():
                image = Image.open(bg_image_path).resize((width, height))
            else:
                bg_color = cls._config.get("COLORS", {}).get("BACKGROUND", "black")
                image = Image.new("RGB", (width, height), color=bg_color)
        except IOError as e:
            raise RuntimeError(f"Failed to load or create the image: {e}")

        return image

    @staticmethod
    def _translate_block_type(block_type_str: str) -> BackgroundImageType:
        translation_map = {
            "title": BackgroundImageType.TITLE,
            "final": BackgroundImageType.FINAL,
            # Add other translations as necessary
        }
        return translation_map.get(block_type_str.lower(), BackgroundImageType.NORMAL)
