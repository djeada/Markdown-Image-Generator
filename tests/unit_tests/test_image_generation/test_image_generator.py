"""Tests for the ImageGenerator class."""

import json
import pytest
from pathlib import Path
from PIL import Image

from src.image_generation.image_generator import ImageGenerator
from src.utils.exceptions import ImageGenerationError
from src.data.text_block import TextBlock, BlockType
from src.utils.config import Config


@pytest.fixture(autouse=True)
def setup_config(tmp_path):
    """Set up a valid config with a real font for tests."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not Path(font_path).exists():
        pytest.skip("DejaVu font not available")

    config_data = {
        "PATHS": {
            "DEFAULT_PAGE": "",
            "TITLE_PAGE": "",
            "FINAL_PAGE": "",
            "QUESTION_PAGE": "",
            "FONT": font_path,
        },
        "PAGE_LAYOUT": {
            "TOP_MARGIN": 100,
            "BOTTOM_MARGIN": 100,
            "RIGHT_MARGIN": 80,
            "LEFT_MARGIN": 80,
            "IMAGE_WIDTH": 500,
            "IMAGE_HEIGHT": 500,
            "CHAR_WIDTH": 15,
            "DEFAULT_LINE_HEIGHT": 30,
            "LIST_LINE_HEIGHT": 20,
            "START_INDEX": 0,
        },
        "COLORS": {
            "PAGE_NUMBER_FONT": "#292929",
            "TEXT": "#FFFFFF",
            "BACKGROUND": "#000000",
            "HIGHLIGHT": "#ffab00",
        },
        "CODE_BLOCK": {
            "SCALE_FACTOR": 2,
            "BACKGROUND": "#000000",
            "RADIUS": 20,
            "TOP_PADDING": 50,
        },
        "TABLE": {
            "SCALE_FACTOR": 1,
            "FOREGROUND": "#FFFFFF",
            "BACKGROUND": "#292929",
            "HIGHLIGHT": "#ffab00",
            "HEADER_BG_COLOR": "#8c52ff",
            "HEADER_FG_COLOR": "#000000",
            "HEIGHT": 8,
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config_data))
    Config().init_config(path=config_path)


class TestImageGenerator:

    def test_init(self):
        gen = ImageGenerator()
        assert gen.width == 500
        assert gen.height == 500

    def test_get_font_for_block(self):
        gen = ImageGenerator()
        font = gen.get_font_for_block(BlockType.PARAGRAPH)
        assert font is not None
        assert font.size == gen.block_styles[BlockType.PARAGRAPH]["font_size"]

    def test_get_font_for_title(self):
        gen = ImageGenerator()
        font = gen.get_font_for_block(BlockType.TITLE)
        assert font.size == gen.block_styles[BlockType.TITLE]["font_size"]

    def test_get_font_missing_font_file(self):
        gen = ImageGenerator()
        gen.font_path = "/nonexistent/font.ttf"
        with pytest.raises(ImageGenerationError, match="Font file not found"):
            gen.get_font_for_block(BlockType.PARAGRAPH)

    def test_generate_images_single_paragraph(self):
        gen = ImageGenerator()
        blocks = [TextBlock("paragraph", "Hello world")]
        images = gen.generate_images(blocks)
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)

    def test_generate_images_header_block(self):
        gen = ImageGenerator()
        blocks = [TextBlock("header", "Section Title")]
        images = gen.generate_images(blocks)
        assert len(images) == 1

    def test_generate_images_multiple_blocks(self):
        gen = ImageGenerator()
        blocks = [
            TextBlock("title", "My Title"),
            TextBlock("paragraph", "First paragraph."),
            TextBlock("paragraph", "Second paragraph."),
        ]
        images = gen.generate_images(blocks)
        assert len(images) >= 1

    def test_generate_images_empty_blocks(self):
        gen = ImageGenerator()
        images = gen.generate_images([])
        assert images == []

    def test_draw_page_number(self):
        gen = ImageGenerator()
        img = Image.new("RGB", (500, 500), "black")
        # Should not raise
        gen.draw_page_number(img, 1)

    def test_block_styles_all_types_present(self):
        gen = ImageGenerator()
        for bt in BlockType:
            assert bt in gen.block_styles, f"Missing style for {bt}"

    def test_draw_text_on_image_paragraph(self):
        gen = ImageGenerator()
        img = Image.new("RGB", (500, 500), "black")
        block = TextBlock("paragraph", "Test text")
        height = gen.draw_text_on_image(img, block, 100)
        assert height > 100

    def test_draw_text_on_image_bullet_list(self):
        gen = ImageGenerator()
        img = Image.new("RGB", (500, 500), "black")
        block = TextBlock("bullet_list", "Item one\nItem two")
        height = gen.draw_text_on_image(img, block, 100)
        assert height > 100
