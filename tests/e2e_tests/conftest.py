import pytest
from pathlib import Path

@pytest.fixture
def temp_markdown_file(tmp_path):
    """Create a temporary markdown file with test content"""
    md_file = tmp_path / "test.md"
    md_file.write_text("""# Test Document

This is a test markdown document for E2E testing.

## Code Example
```python
def hello_world():
    print("Hello from Markdown!")
```

## List Items
- First item
- Second item
- Third item

## Table Example
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |
""")
    return md_file
