from src.data.text_block import TextBlock

from abc import ABC, abstractmethod


class BlockParser(ABC):
    def __init__(self):
        self.reset()

    @abstractmethod
    def is_start_line(self, line: str) -> bool:
        pass

    @abstractmethod
    def is_end_line(self, line: str) -> bool:
        pass

    @abstractmethod
    def parse(self, line: str):
        pass

    @abstractmethod
    def get_block(self) -> TextBlock:
        pass

    @abstractmethod
    def reset(self):
        pass


class HeaderParser(BlockParser):
    def __init__(self):
        super().__init__()
        self.content = ""

    def is_start_line(self, line: str) -> bool:
        stripped_line = line.strip()
        return stripped_line.startswith("#")

    def is_end_line(self, line: str) -> bool:
        return True  # The header is only one line, so we end as soon as we start.

    def parse(self, line: str) -> bool:
        if self.is_start_line(line):
            self.content = line.split(" ", 1)[1].strip()
            return True
        return False

    def get_block(self) -> TextBlock:
        block = TextBlock("header", self.content)
        self.content = ""
        return block

    def reset(self):
        self.content = []


class CodeBlockParser(BlockParser):
    def __init__(self):
        super().__init__()
        self.is_parsing = False
        self.content = []

    def is_start_line(self, line: str) -> bool:
        stripped_line = line.strip()
        if not self.is_parsing and stripped_line == "```":
            self.is_parsing = True
            return True
        return False

    def is_end_line(self, line: str) -> bool:
        stripped_line = line.strip()
        if self.is_parsing and stripped_line == "```":
            self.is_parsing = False
            return True
        return False

    def parse(self, line: str):
        if not self.is_parsing:
            return

        line = line.replace("`", "").strip()
        if line:
            self.content.append(line)

    def get_block(self) -> TextBlock:
        block = TextBlock("code", "\n".join(self.content))
        self.content = []
        return block

    def reset(self):
        self.content = []


class BulletListBlockParser(BlockParser):
    def is_start_line(self, line: str) -> bool:
        line = line.strip()
        return line.startswith("* ") or line.startswith("- ")

    def is_end_line(self, line: str) -> bool:
        line = line.strip()
        return not self.is_start_line(line)

    def parse(self, line: str):
        self.content.append(line.strip()[2:])

    def get_block(self) -> TextBlock:
        return TextBlock("bullet", "\n".join(self.content))

    def reset(self):
        self.content = []


class TableBlockParser(BlockParser):
    def is_start_line(self, line: str) -> bool:
        line = line.strip()
        return "|" in line and "-" not in line

    def is_end_line(self, line: str) -> bool:
        line = line.strip()
        return "|" not in line

    def parse(self, line: str):
        self.content.append(line.strip())

    def get_block(self) -> TextBlock:
        return TextBlock("table", "\n".join(self.content))

    def reset(self):
        self.content = []


class TableBlockParser(BlockParser):
    def is_start_line(self, line: str) -> bool:
        return "|" in line and "-" not in line

    def is_end_line(self, line: str) -> bool:
        return "|" not in line

    def parse(self, line: str):
        self.content.append(line)

    def get_block(self) -> TextBlock:
        return TextBlock("table", "\n".join(self.content))

    def reset(self):
        self.content = []