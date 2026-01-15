from src.data.text_block import TextBlock

from abc import ABC, abstractmethod
import re


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


class TitleParser(BlockParser):
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
        block = TextBlock("title", self.content)
        self.content = ""
        return block

    def reset(self):
        self.content = []


class HeaderParser(TitleParser):
    def is_start_line(self, line: str) -> bool:
        stripped_line = line.strip()
        return stripped_line.startswith("##")

    def get_block(self) -> TextBlock:
        block = TextBlock("header", self.content)
        self.content = ""
        return block


class CodeBlockParser(BlockParser):
    def __init__(self):
        super().__init__()
        self.is_parsing = False
        self.content = []
        self.counter = 0

    def is_start_line(self, line: str) -> bool:
        stripped_line = line.strip()
        if not self.is_parsing and stripped_line.startswith("```"):
            self.is_parsing = True
            return True
        return False

    def is_end_line(self, line: str) -> bool:
        stripped_line = line.strip()
        if stripped_line.startswith("```"):
            if self.counter:
                self.content.append(stripped_line)
                self.is_parsing = False
                self.counter = 0
                return True
            else:
                self.counter += 1
        return False

    def parse(self, line: str):
        if not self.is_parsing:
            return

        # line = line.replace("`", "").strip()
        # if line:
        self.content.append(line)

    def get_block(self) -> TextBlock:
        block = TextBlock("code", "\n".join(self.content))
        self.content = []
        return block

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


class BulletListParser(BlockParser):
    """Parser for unordered bullet lists (- or * prefixed items)."""

    def __init__(self):
        super().__init__()
        self.content = []
        self.is_parsing = False

    def is_start_line(self, line: str) -> bool:
        stripped = line.strip()
        if not self.is_parsing and (
            stripped.startswith("- ") or stripped.startswith("* ")
        ):
            self.is_parsing = True
            return True
        return False

    def is_end_line(self, line: str) -> bool:
        stripped = line.strip()
        # End when we hit a non-list line (empty or different content)
        if self.is_parsing and not (
            stripped.startswith("- ") or stripped.startswith("* ")
        ):
            self.is_parsing = False
            return True
        return False

    def parse(self, line: str):
        stripped = line.strip()
        if stripped.startswith("- "):
            self.content.append(stripped[2:])
        elif stripped.startswith("* "):
            self.content.append(stripped[2:])

    def get_block(self) -> TextBlock:
        block = TextBlock("bullet_list", "\n".join(self.content))
        self.content = []
        return block

    def reset(self):
        self.content = []
        self.is_parsing = False


class NumberedListParser(BlockParser):
    """Parser for ordered numbered lists (1. 2. 3. prefixed items)."""

    def __init__(self):
        super().__init__()
        self.content = []
        self.is_parsing = False

    def is_start_line(self, line: str) -> bool:
        stripped = line.strip()
        if not self.is_parsing and re.match(r"^\d+\.\s", stripped):
            self.is_parsing = True
            return True
        return False

    def is_end_line(self, line: str) -> bool:
        stripped = line.strip()
        if self.is_parsing and not re.match(r"^\d+\.\s", stripped):
            self.is_parsing = False
            return True
        return False

    def parse(self, line: str):
        stripped = line.strip()
        match = re.match(r"^\d+\.\s(.+)$", stripped)
        if match:
            self.content.append(match.group(1))

    def get_block(self) -> TextBlock:
        block = TextBlock("numbered_list", "\n".join(self.content))
        self.content = []
        return block

    def reset(self):
        self.content = []
        self.is_parsing = False


class BlockquoteParser(BlockParser):
    """Parser for blockquotes (> prefixed lines)."""

    def __init__(self):
        super().__init__()
        self.content = []
        self.is_parsing = False

    def is_start_line(self, line: str) -> bool:
        stripped = line.strip()
        if not self.is_parsing and stripped.startswith(">"):
            self.is_parsing = True
            return True
        return False

    def is_end_line(self, line: str) -> bool:
        stripped = line.strip()
        if self.is_parsing and not stripped.startswith(">"):
            self.is_parsing = False
            return True
        return False

    def parse(self, line: str):
        stripped = line.strip()
        if stripped.startswith("> "):
            self.content.append(stripped[2:])
        elif stripped.startswith(">"):
            self.content.append(stripped[1:])

    def get_block(self) -> TextBlock:
        block = TextBlock("blockquote", "\n".join(self.content))
        self.content = []
        return block

    def reset(self):
        self.content = []
        self.is_parsing = False


class HorizontalRuleParser(BlockParser):
    """Parser for horizontal rules (---, ***, ___)."""

    def __init__(self):
        super().__init__()
        self.content = ""

    def is_start_line(self, line: str) -> bool:
        stripped = line.strip()
        return (
            len(stripped) >= 3
            and (
                all(c == "-" for c in stripped)
                or all(c == "*" for c in stripped)
                or all(c == "_" for c in stripped)
            )
            and not stripped.startswith("```")
        )

    def is_end_line(self, line: str) -> bool:
        return True  # Single line element

    def parse(self, line: str):
        self.content = "---"

    def get_block(self) -> TextBlock:
        block = TextBlock("horizontal_rule", self.content)
        self.content = ""
        return block

    def reset(self):
        self.content = ""


class TaskListParser(BlockParser):
    """Parser for task lists (- [ ] or - [x] prefixed items)."""

    def __init__(self):
        super().__init__()
        self.content = []
        self.is_parsing = False

    def is_start_line(self, line: str) -> bool:
        stripped = line.strip()
        if not self.is_parsing and (
            stripped.startswith("- [ ]") or stripped.startswith("- [x]") or
            stripped.startswith("- [X]") or stripped.startswith("* [ ]") or
            stripped.startswith("* [x]") or stripped.startswith("* [X]")
        ):
            self.is_parsing = True
            return True
        return False

    def is_end_line(self, line: str) -> bool:
        stripped = line.strip()
        # End when we hit a non-task-list line
        if self.is_parsing and not (
            stripped.startswith("- [ ]") or stripped.startswith("- [x]") or
            stripped.startswith("- [X]") or stripped.startswith("* [ ]") or
            stripped.startswith("* [x]") or stripped.startswith("* [X]")
        ):
            self.is_parsing = False
            return True
        return False

    def parse(self, line: str):
        stripped = line.strip()
        # Extract checked state and text
        if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
            self.content.append(("checked", stripped[5:].strip()))
        elif stripped.startswith("* [x]") or stripped.startswith("* [X]"):
            self.content.append(("checked", stripped[5:].strip()))
        elif stripped.startswith("- [ ]"):
            self.content.append(("unchecked", stripped[5:].strip()))
        elif stripped.startswith("* [ ]"):
            self.content.append(("unchecked", stripped[5:].strip()))

    def get_block(self) -> TextBlock:
        # Encode as "checked:text" or "unchecked:text" separated by newlines
        items = [f"{state}:{text}" for state, text in self.content]
        block = TextBlock("task_list", "\n".join(items))
        self.content = []
        return block

    def reset(self):
        self.content = []
        self.is_parsing = False
