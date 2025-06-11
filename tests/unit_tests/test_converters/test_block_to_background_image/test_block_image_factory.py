from src.data.background_image_type import BackgroundImageType
from src.utils.config import Config
from PIL import Image
import pytest


@pytest.fixture(scope="function")
def block_image_factory(tmp_path):

    # Create temporary image files in the temporary directory
    title_image_path = tmp_path / "title.jpg"
    default_image_path = tmp_path / "default.jpg"
    final_image_path = tmp_path / "final.jpg"
    question_image_path = tmp_path / "question.jpg"

    # Create temporary images with specified dimensions
    width = 800
    height = 600

    Image.new("RGB", (width, height)).save(title_image_path)
    Image.new("RGB", (width, height)).save(default_image_path)
    Image.new("RGB", (width, height)).save(final_image_path)
    Image.new("RGB", (width, height)).save(question_image_path)

    # Mock the config with temporary image paths
    config_data = {
        "PATHS": {
            "TITLE_PAGE": str(title_image_path),
            "DEFAULT_PAGE": str(default_image_path),
            "FINAL_PAGE": str(final_image_path),
            "QUESTION_PAGE": str(question_image_path),
        }
    }

    Config()["PATHS"] = config_data["PATHS"]
    from src.converters.block_to_background_image.block_image_factory import (
        BlockImageFactory,
    )

    return BlockImageFactory()


@pytest.fixture(scope="function")
def block_image_factory_empty(tmp_path):

    config_data = {
        "PATHS": {
            "TITLE_PAGE": None,
            "DEFAULT_PAGE": None,
            "FINAL_PAGE": None,
            "QUESTION_PAGE": None,
        }
    }

    Config()["PATHS"] = config_data["PATHS"]
    from src.converters.block_to_background_image.block_image_factory import (
        BlockImageFactory,
    )

    return BlockImageFactory()


def test_create_background_image_with_existing_path(block_image_factory_empty):
    block_type_str = "title"
    width = 800
    height = 600

    # Create a temporary image with specified dimensions
    image = block_image_factory_empty.create_background_image(
        block_type_str, width, height
    )

    # Check if the image is an instance of PIL.Image
    assert isinstance(image, Image.Image)

    # Check if the image has the expected dimensions
    assert image.size == (width, height)


def test_create_background_image_with_non_existing_path(block_image_factory):

    # Mock the config with missing image paths
    config_data = {}
    block_image_factory._config = Config(config_data)

    block_type_str = "title"
    width = 800
    height = 600

    # Create a temporary image with specified dimensions
    image = block_image_factory.create_background_image(block_type_str, width, height)

    # Check if the image is an instance of PIL.Image
    assert isinstance(image, Image.Image)
    # Check if the image has the expected dimensions
    assert image.size == (width, height)


def test_translate_block_type(block_image_factory):
    assert (
        block_image_factory._translate_block_type("title") == BackgroundImageType.TITLE
    )
    assert (
        block_image_factory._translate_block_type("final") == BackgroundImageType.FINAL
    )
    assert (
        block_image_factory._translate_block_type("normal")
        == BackgroundImageType.NORMAL
    )
    assert (
        block_image_factory._translate_block_type("invalid")
        == BackgroundImageType.NORMAL
    )
