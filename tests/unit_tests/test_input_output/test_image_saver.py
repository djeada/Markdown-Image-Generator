import pytest
import os
from PIL import Image

from src.input_output.image_saver import ImageSaver
from src.utils.exceptions import ImageSaveError


@pytest.fixture
def image_saver(tmp_path):
    return ImageSaver(str(tmp_path))


def test_save_single_image(image_saver):
    image = Image.new("RGB", (100, 100), color="red")
    file_name = "test_image.png"
    image_saver.save_image(image, file_name)

    assert (tmp_path := image_saver.output_directory) is not None
    saved_image_path = os.path.join(tmp_path, file_name)
    assert os.path.exists(saved_image_path)


def test_save_multiple_images(image_saver):
    images = [Image.new("RGB", (100, 100), color="red") for _ in range(3)]
    image_saver.save_images(images)

    assert (tmp_path := image_saver.output_directory) is not None
    for idx in range(3):
        saved_image_path = os.path.join(tmp_path, f"output{idx}.png")
        assert os.path.exists(saved_image_path)


def test_save_images_single_image(image_saver):
    image = Image.new("RGB", (50, 50), color="blue")
    image_saver.save_images(image)
    assert os.path.exists(os.path.join(image_saver.output_directory, "output.png"))


def test_init_nonexistent_directory():
    with pytest.raises(FileNotFoundError, match="does not exist"):
        ImageSaver("/nonexistent/path/for/sure")


def test_init_not_a_directory(tmp_path):
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("hi")
    with pytest.raises(NotADirectoryError, match="not a directory"):
        ImageSaver(str(file_path))


def test_init_none_directory():
    saver = ImageSaver(None)
    assert saver.output_directory is None


def test_save_to_readonly_dir(tmp_path):
    readonly = tmp_path / "readonly"
    readonly.mkdir()
    readonly.chmod(0o444)
    saver = ImageSaver(str(readonly))
    image = Image.new("RGB", (10, 10), color="green")
    with pytest.raises(ImageSaveError, match="Error saving image"):
        saver.save_image(image, "test.png")
    readonly.chmod(0o755)  # cleanup
