import pytest
import os
from PIL import Image

from src.input_output.image_saver import ImageSaver


@pytest.fixture
def image_saver(tmp_path):
    return ImageSaver(str(tmp_path))


def test_save_single_image(image_saver):
    # Create a test image
    image = Image.new("RGB", (100, 100), color="red")

    # Save the test image using the ImageSaver instance
    file_name = "test_image.png"
    image_saver.save_image(image, file_name)

    # Check if the image was saved to the temporary directory
    assert (tmp_path := image_saver.output_directory) is not None
    saved_image_path = os.path.join(tmp_path, file_name)
    assert os.path.exists(saved_image_path)


def test_save_multiple_images(image_saver):
    # Create multiple test images
    images = [Image.new("RGB", (100, 100), color="red") for _ in range(3)]

    # Save the test images using the ImageSaver instance
    image_saver.save_images(images)

    # Check if the images were saved to the temporary directory
    assert (tmp_path := image_saver.output_directory) is not None
    for idx in range(3):
        saved_image_path = os.path.join(tmp_path, f"output{idx}.png")
        assert os.path.exists(saved_image_path)
