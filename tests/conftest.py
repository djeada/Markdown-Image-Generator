import pytest
from pathlib import Path

@pytest.fixture
def demo_files():
    """Returns a list of demo markdown files."""
    demo_dir = Path(__file__).parent.parent / 'demo'
    return list(demo_dir.glob('*.md'))

@pytest.fixture
def resources_dir():
    """Returns the path to the resources directory."""
    return Path(__file__).parent.parent / 'resources'

@pytest.fixture
def temp_markdown_file(tmp_path):
    """Creates a temporary markdown file with some test content."""
    file_path = tmp_path / "test.md"
    content = """# Test Document
    
## Section 1
This is a test paragraph with some **bold** and *italic* text.

## Section 2
1. First item
2. Second item
3. Third item

## Code Example
```python
def hello():
    print("Hello, World!")
```
"""
    file_path.write_text(content)
    return file_path
