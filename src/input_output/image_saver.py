import logging
from pathlib import Path
from typing import Union, List, Optional
from PIL import Image

from src.utils.exceptions import ImageSaveError

logger = logging.getLogger(__name__)


class ImageSaver:
    """
    A class to save images to a specified directory.
    """

    def __init__(self, output_directory: Optional[str]):
        """
        Initializes the ImageSaver.

        Args:
            output_directory (Optional[str]): The directory where images will be saved.

        Raises:
            FileNotFoundError: If the output directory does not exist.
            NotADirectoryError: If the path exists but is not a directory.
        """
        if output_directory is not None:
            path = Path(output_directory)
            if not path.exists():
                raise FileNotFoundError(
                    f"Output directory does not exist: {output_directory}"
                )
            if not path.is_dir():
                raise NotADirectoryError(
                    f"Output path is not a directory: {output_directory}"
                )
        self.output_directory = output_directory

    def save_image(self, image: Image.Image, file_name: str) -> None:
        """
        Saves a single image.

        Args:
            image (Image.Image): The image to save.
            file_name (str): The file name to use for saving the image.

        Raises:
            ImageSaveError: If the image cannot be saved.
        """
        try:
            file_path = (
                str(Path(self.output_directory) / file_name)
                if self.output_directory
                else file_name
            )
            image.save(file_path)
        except OSError as e:
            raise ImageSaveError(f"Error saving image {file_name}: {e}") from e

    def save_images(self, images: Union[Image.Image, List[Image.Image]]) -> None:
        """
        Saves a list of images or a single image.

        Args:
            images (Union[List[Image.Image], Image.Image]): The image or list of images to save.

        Raises:
            ImageSaveError: If any image cannot be saved.
        """
        if isinstance(images, list):
            for idx, image in enumerate(images):
                self.save_image(image, f"output{idx}.png")
        else:
            self.save_image(images, "output.png")
