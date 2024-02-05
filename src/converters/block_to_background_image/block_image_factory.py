from PIL import Image
from src.data.background_image_type import BackgroundImageType
from src.utils.config import Config

class BlockImageFactory:
    _config: Config = Config()

    PATHS_TO_IMAGES: dict = {
        BackgroundImageType.TITLE: _config["PATHS"]["TITLE_PAGE"],
        BackgroundImageType.NORMAL: _config["PATHS"]["DEFAULT_PAGE"],
        BackgroundImageType.FINAL: _config["PATHS"]["FINAL_PAGE"],
        BackgroundImageType.QUESTION: _config["PATHS"]["QUESTION_PAGE"],
    }

    @classmethod
    def create_background_image(cls, block_type_str: str, width: int, height: int) -> Image.Image:
        block_type = cls._translate_block_type(block_type_str)
        bg_image_path = cls.PATHS_TO_IMAGES.get(block_type)

        try:
            if bg_image_path:
                image = Image.open(bg_image_path).resize((width, height))
            else:
                bg_color = cls._config.get("BG_COLOR", "black")
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
