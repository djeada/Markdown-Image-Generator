import textwrap
from dataclasses import dataclass
from typing import List

@dataclass
class TextBlock:
    type: str
    data: str

class MarkdownInterpreter:
    def interpret(self, lines: List[str], max_width: int = 70) -> List[TextBlock]:
        blocks = []
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # Add a new block for the header
                blocks.append(TextBlock('header', line[1:].strip()))
            else:
                # Wrap the line to the maximum width, add each wrapped line as a separate block
                wrapped_lines = textwrap.wrap(line, width=max_width)
                for wrapped_line in wrapped_lines:
                    blocks.append(TextBlock('paragraph', wrapped_line))
        return blocks

if __name__ == "__main__":
    markdown_lines = [
        "# Header 1",
        "This is a long paragraph that will need to be split into multiple lines to fit within the maximum width. It contains a lot of text and could potentially span many lines.",
        "## Header 2",
        "This is another long paragraph that will need to be split into multiple lines to fit within the maximum width. It contains a lot of text and could potentially span many lines."
    ]

    interpreter = MarkdownInterpreter()
    blocks = interpreter.interpret(markdown_lines)

    for block in blocks:
        print(f'Type: {block.type}, Data: {block.data}')
