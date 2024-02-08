from enum import Enum, auto
from typing import List, Optional


class BlockType(Enum):
    PARAGRAPH = auto()
    HEADER = auto()
    TABLE = auto()
    CODE = auto()
    TITLE = auto()


class TextBlock:
    """
    A class representing a block of text.

    Attributes
    ----------
    type : str
        The type of the text block (e.g., 'header', 'paragraph', 'list', 'code').
    data : str
        The text content of the block.
    children : List[TextBlock]
        A list of child text blocks.

    Methods
    -------
    add_child(child: TextBlock) -> None:
        Adds a child text block to this block.
    """

    def __init__(
        self, type: str, data: str, children: Optional[List["TextBlock"]] = None
    ):
        self.type = type
        self.data = data
        self.children = children if children is not None else []

    def add_child(self, child: "TextBlock") -> None:
        """Adds a child text block to this block."""
        self.children.append(child)

    def __repr__(self) -> str:
        return f"TextBlock(type={self.type!r}, data={self.data!r}, children={self.children!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, TextBlock)
            and (
                self.type,
                self.data,
                self.children,
            )
            == (other.type, other.data, other.children)
        )
