class TextBlock:
    """
    A class representing a block of text.

    Attributes
    -------
    type : str
        The type of text block (header, paragraph, list, code, etc.)
    data : str
        The text content of the block.
    children : List[TextBlock]
        Any child text blocks of this block.
    """

    def __init__(self, type: str, data: str, children=None):
        self.type = type
        self.data = data
        self.children = children if children is not None else []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        children_str = ", ".join(str(child) for child in self.children)
        return f"Type: {self.type}, Data: {self.data}, Children: [{children_str}]"

    def __eq__(self, other):
        if isinstance(other, TextBlock):
            return (
                self.type == other.type
                and self.data == other.data
                and self.children == other.children
            )
        return False
