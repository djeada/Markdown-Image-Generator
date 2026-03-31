import logging
from pathlib import Path

from src.utils.exceptions import MarkdownReadError

logger = logging.getLogger(__name__)


class MarkdownReader:
    """
    A class to read content from a markdown file.
    """

    SUPPORTED_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}

    def __init__(self) -> None:
        pass

    def read(self, filename: str) -> str:
        """
        Reads the content of a markdown file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            str: The content of the file as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            MarkdownReadError: If the file has an unsupported extension or cannot be read.
        """
        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise MarkdownReadError(
                f"Unsupported file extension '{path.suffix}'. "
                f"Expected one of: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        try:
            with open(filename, "r", encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError as e:
            raise MarkdownReadError(
                f"File {filename} is not valid UTF-8: {e}"
            ) from e
        except OSError as e:
            raise MarkdownReadError(
                f"Could not read file {filename}: {e}"
            ) from e
