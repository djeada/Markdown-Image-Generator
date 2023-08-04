class MarkdownReader:
    """A class to read content from a markdown file."""

    def __init__(self):
        """Initializes the MarkdownReader."""
        pass

    def read(self, filename: str) -> str:
        """
        Reads the content of a markdown file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            str: The content of the file as a string. If an error occurs, None is returned.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return None
        except Exception as e:
            print(f"An error occurred while reading the file {filename}: {str(e)}")
            return None
