import logging
from typing import Union, List, Optional
from PIL import Image


class ImageSaver:
    """
    A class to save images to a specified directory.
    """

    def __init__(self, output_directory: Optional[str]):
        """
        Initializes the ImageSaver.

        Args:
            output_directory (Optional[str]): The directory where images will be saved.
        """
        self.output_directory = output_directory

    def save_image(self, image: Image, file_name: str) -> None:
        """
        Saves a single image.

        Args:
            image (Image): The image to save.
            file_name (str): The file name to use for saving the image.
        """
        try:
            file_path = (
                f"{self.output_directory}/{file_name}"
                if self.output_directory
                else file_name
            )
            image.save(file_path)
        except Exception as e:
            logging.error(f"Error saving image {file_name}: {e}")

    def save_images(self, images: Union[Image.Image, List[Image.Image]]) -> None:
        """
        Saves a list of images or a single image.

        Args:
            images (Union[List[Image], Image]): The image or list of images to save.
        """
        if isinstance(images, list):
            for idx, image in enumerate(images):
                self.save_image(image, f"output{idx}.png")
        else:
            self.save_image(images, "output.png")
