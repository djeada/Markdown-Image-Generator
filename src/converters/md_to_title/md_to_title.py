from src.data.text_block import TextBlock


class MarkdownToTitleBlock:
    def __init__(self):
        pass

    def interpret(self, content: str) -> TextBlock:
        block = TextBlock("title", content)
        return block
