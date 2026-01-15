from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter
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
        """Create a modern gradient background image with optional effects."""
        theme_config = cls._config.get("THEME", {})
        gradient_config = theme_config.get("GRADIENT", {})
        
        start_color = gradient_config.get("START_COLOR", "#1a1a2e")
        end_color = gradient_config.get("END_COLOR", "#16213e")
        direction = gradient_config.get("DIRECTION", "vertical")
        
        # Parse colors
        start_rgba = hex_to_rgba(start_color)
        end_rgba = hex_to_rgba(end_color)
        
        # Create base image
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        if direction == "vertical":
            # Create vertical gradient
            for y in range(height):
                ratio = y / height
                r = int(start_rgba[0] + (end_rgba[0] - start_rgba[0]) * ratio)
                g = int(start_rgba[1] + (end_rgba[1] - start_rgba[1]) * ratio)
                b = int(start_rgba[2] + (end_rgba[2] - start_rgba[2]) * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        elif direction == "diagonal":
            # Create diagonal gradient
            for y in range(height):
                for x in range(width):
                    ratio = (x + y) / (width + height)
                    r = int(start_rgba[0] + (end_rgba[0] - start_rgba[0]) * ratio)
                    g = int(start_rgba[1] + (end_rgba[1] - start_rgba[1]) * ratio)
                    b = int(start_rgba[2] + (end_rgba[2] - start_rgba[2]) * ratio)
                    draw.point((x, y), fill=(r, g, b))
        elif direction == "radial":
            # Create radial gradient from center
            center_x, center_y = width // 2, height // 2
            max_dist = math.sqrt(center_x**2 + center_y**2)
            for y in range(height):
                for x in range(width):
                    dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    ratio = min(dist / max_dist, 1.0)
                    r = int(start_rgba[0] + (end_rgba[0] - start_rgba[0]) * ratio)
                    g = int(start_rgba[1] + (end_rgba[1] - start_rgba[1]) * ratio)
                    b = int(start_rgba[2] + (end_rgba[2] - start_rgba[2]) * ratio)
                    draw.point((x, y), fill=(r, g, b))
        else:
            # Default to horizontal gradient
            for x in range(width):
                ratio = x / width
                r = int(start_rgba[0] + (end_rgba[0] - start_rgba[0]) * ratio)
                g = int(start_rgba[1] + (end_rgba[1] - start_rgba[1]) * ratio)
                b = int(start_rgba[2] + (end_rgba[2] - start_rgba[2]) * ratio)
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
        
        # Add subtle noise/texture for modern look
        effects_config = cls._config.get("EFFECTS", {})
        if effects_config.get("TEXTURE", False):
            image = cls._add_subtle_texture(image)
        
        return image

    @classmethod
    def _add_subtle_texture(cls, image: Image.Image) -> Image.Image:
        """Add subtle noise texture for modern aesthetic."""
        import random
        pixels = image.load()
        width, height = image.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                noise = random.randint(-3, 3)
                pixels[x, y] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise))
                )
        
        return image

    @classmethod
    def _add_decorative_elements(cls, image: Image.Image) -> Image.Image:
        """Add subtle decorative elements to the background."""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Add subtle corner accents
        accent_config = cls._config.get("THEME", {}).get("ACCENT_GRADIENT", {})
        if accent_config.get("ENABLED", False):
            accent_color = hex_to_rgba(accent_config.get("START_COLOR", "#00d4ff"))
            # Draw subtle corner lines
            line_length = 60
            line_width = 2
            margin = 40
            
            # Top-left corner accent
            draw.line([(margin, margin), (margin + line_length, margin)], 
                     fill=accent_color[:3], width=line_width)
            draw.line([(margin, margin), (margin, margin + line_length)], 
                     fill=accent_color[:3], width=line_width)
            
            # Bottom-right corner accent
            draw.line([(width - margin - line_length, height - margin), 
                      (width - margin, height - margin)], 
                     fill=accent_color[:3], width=line_width)
            draw.line([(width - margin, height - margin - line_length), 
                      (width - margin, height - margin)], 
                     fill=accent_color[:3], width=line_width)
        
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
                # Add decorative elements for title pages
                if block_type == BackgroundImageType.TITLE:
                    image = cls._add_decorative_elements(image)
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
