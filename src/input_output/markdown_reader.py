import logging
from typing import Optional


class MarkdownReader:
    """
    A class to read content from a markdown file.
    """

    def __init__(self):
        """
        Initializes the MarkdownReader.
        """
        # Initialization code can go here if needed in the future
        pass

    def read(self, filename: str) -> Optional[str]:
        """
        Reads the content of a markdown file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            Optional[str]: The content of the file as a string, or None if an error occurs.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"File {filename} not found.")
        except IOError as e:
            logging.error(
                f"An I/O error occurred while reading the file {filename}: {e}"
            )
        except Exception as e:  # General exception should be logged as well
            logging.error(
                f"An unexpected error occurred while reading the file {filename}: {e}"
            )

        return None
