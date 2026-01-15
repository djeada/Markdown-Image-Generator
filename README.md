# Markdown Image Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **Transform your Markdown documents into stunning, presentation-ready images with customizable themes and professional styling.**

The Markdown Image Generator is a powerful Python-based tool that converts Markdown documents into a series of visually appealing, high-quality images. Whether you're creating presentations, social media content, or educational materials, this tool bridges the gap between plain text documentation and visual storytelling.

## Table of Contents

- [Why Markdown Image Generator?](#why-markdown-image-generator)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Use Cases](#use-cases)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Why Markdown Image Generator?

Markdown is renowned for its simplicity and versatility, making it the go-to format for documentation, README files, and technical writing. However, when it comes to creating presentations, social media content, or educational materials, plain Markdown can fall short in visual appeal.

**The Markdown Image Generator solves this challenge by:**

- **Enabling Visual Communication**: Transform text-heavy Markdown into eye-catching images perfect for presentations and social sharing
- **Maintaining Content Integrity**: Preserve all Markdown formatting including headers, lists, code blocks, tables, and more
- **Offering Professional Styling**: Apply custom themes, gradients, and color schemes to match your brand or presentation style
- **Streamlining Workflow**: Automate the creation of slide decks and visual content directly from your existing Markdown documentation
- **Supporting Multiple Use Cases**: From conference presentations to educational materials, LinkedIn posts to Instagram carousels

## System Architecture

Below is a system diagram illustrating the workflow and component architecture of the Markdown Image Generator:

```
┌─────────────────┐       ┌──────────────────┐       ┌────────────────┐
│                 │       │                  │       │                │
│ Markdown File   │──────▶│ Markdown Reader  │──────▶│ Converters     │
│ (.md)           │       │ (input_output)   │       │ (converters)   │
│                 │       │                  │       │                │
└─────────────────┘       └──────────────────┘       └────────┬───────┘
                                                               │
                                                               │
                                                               ▼
                          ┌──────────────────┐       ┌────────────────┐
                          │                  │       │                │
                          │ Image Saver      │◀──────│ Image          │
                          │ (input_output)   │       │ Generation     │
                          │                  │       │                │
                          └──────────────────┘       └────────┬───────┘
                                                               │
                                                               ▼
                                                      ┌────────────────┐
                                                      │                │
                                                      │ Data Handling  │
                                                      │ (data)         │
                                                      │                │
                                                      └────────────────┘
```

**Component Overview:**

- **Markdown Reader**: Parses input `.md` files and extracts content structure
- **Converters**: Transform Markdown elements into renderable data structures
- **Data Handling**: Manages element properties, styling, and layout calculations
- **Image Generation**: Renders visual elements using PIL/Pillow with custom styling
- **Image Saver**: Handles output operations, file naming, and storage

## Key Features

### 🎨 Comprehensive Markdown Support

The generator provides full support for standard Markdown elements with enhanced visual styling:

| Element | Description |
|---------|-------------|
| **Headers & Titles** | Hierarchical section headers with customizable typography |
| **Paragraphs** | Clean text rendering with intelligent word wrapping |
| **Text Formatting** | Bold, italic, and combined styles with visual distinction |
| **Links** | Distinctive styling for hyperlinks with hover-like appearance |
| **Lists** | Both bulleted and numbered lists with customizable icons and colors |
| **Code Blocks** | Syntax-highlighted code with terminal-like styling and language detection |
| **Tables** | Professional table rendering with customizable headers and cell styling |
| **Blockquotes** | Elegant quote formatting with accent borders |
| **Horizontal Rules** | Decorative section dividers with ornamental elements |

### 🎭 Advanced Styling & Theming

- **Gradient Backgrounds**: Modern gradient effects for polished, professional appearance
- **Custom Color Schemes**: Full control over text, highlights, links, bullets, and backgrounds
- **Flexible Layouts**: Adjustable margins, image dimensions, and text wrapping
- **Theme Support**: Pre-built themes (dark/light) with easy customization
- **Background Images**: Option to use custom images as slide backgrounds
- **Font Customization**: Support for custom fonts and typography settings

### 🚀 Productivity Features

- **Batch Processing**: Convert entire Markdown documents into image series automatically
- **Command-Line Interface**: Simple CLI for integration into workflows and scripts
- **Configuration Files**: JSON-based configuration for consistent styling across projects
- **Preview Mode**: Display generated images directly or save them for later use
- **Flexible Output**: Control output directory, naming conventions, and image formats

## Use Cases

The Markdown Image Generator excels in various scenarios:

### 📊 Conference Presentations
Convert technical documentation into professional slide decks for conferences, meetups, and webinars. Maintain code syntax highlighting and technical formatting while creating visually engaging slides.

### 📱 Social Media Content
Create eye-catching images for:
- LinkedIn posts showcasing code snippets or technical concepts
- Instagram carousels explaining programming concepts
- Twitter threads with visual code examples
- Dev.to article headers and featured images

### 🎓 Educational Materials
Generate visual learning materials:
- Tutorial slides with step-by-step instructions
- Code examples with syntax highlighting
- Concept explanations with formatted text
- Course materials and handouts

### 📖 Documentation Enhancement
Visualize documentation sections:
- README highlights for repository social previews
- API documentation examples
- Quick reference guides
- Onboarding materials

### 💼 Professional Portfolio
Showcase your work:
- Project overviews with key features
- Technical capability demonstrations
- Case study presentations
- Portfolio pieces with code samples

## Usage Examples

### Example 1: Creating a Presentation

**Input Markdown** (`presentation.md`):
```markdown
### Packing Tips

Before your trip, make sure to pack these essentials:

- Passport and travel documents
- Clothing appropriate for the destination's weather
- Comfortable walking shoes
- Adapters and chargers for your electronic devices
- A good book or travel guide
- A sense of adventure and an open mind!
```

**Generated Output**:

![Example Output](https://github.com/djeada/Markdown-Image-Generator/assets/37275728/f0bf1aa4-d9ff-4561-ac19-2ba2cede88fd)

The generator transforms this simple Markdown into a professionally styled image with:
- Clean typography and hierarchy
- Customizable bullet point colors
- Proper spacing and margins
- Optional gradient background

### Example 2: Code Documentation

**Input:**
```markdown
## API Authentication

```python
import requests

def authenticate(api_key, endpoint):
    """Authenticate with the API."""
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(endpoint, headers=headers)
    return response.json()
```

Key features:
- Bearer token authentication
- RESTful API design
- Error handling included
```

This generates an image with syntax-highlighted code and formatted description text.

### Example 3: Technical Comparison Table

**Input:**
```markdown
| Framework | Performance | Learning Curve | Community |
|-----------|-------------|----------------|-----------|
| React     | Excellent   | Moderate       | Large     |
| Vue       | Excellent   | Easy           | Growing   |
| Angular   | Good        | Steep          | Large     |
```

The generator creates a professionally styled table with customizable header colors and cell formatting.

## Installation

### Prerequisites

Before installing the Markdown Image Generator, ensure your system meets the following requirements:

- **Python**: Version 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- **pip**: Python package installer (usually included with Python)
- **Git**: For cloning the repository ([Download Git](https://git-scm.com/downloads))

> **Note**: While the minimum requirement is Python 3.8, we recommend Python 3.9+ for optimal performance.

### Method 1: Installation via pip (Recommended)

Install directly from the repository:

```bash
pip install git+https://github.com/djeada/Markdown-Image-Generator.git
```

After installation, you can use the tool via the command line:

```bash
md-image-generator yourfile.md -o output_folder
```

> **Note**: If the `md-image-generator` command is not found after installation, you can alternatively run: `python -m src.main yourfile.md -o output_folder`

### Method 2: Installation from Source

For development or customization, clone and install from source:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/djeada/Markdown-Image-Generator.git
   ```

2. **Navigate to the Project Directory**:
   ```bash
   cd Markdown-Image-Generator
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional - Install in Development Mode**:
   ```bash
   pip install -e .
   ```

### Verification

Verify the installation by checking the version:

```bash
python -m src.main --version
```

You should see output displaying the current version of the Markdown Image Generator.

## Quick Start

Get up and running in under a minute:

1. **Create a Markdown file** (e.g., `presentation.md`):
   ```markdown
   # Welcome to My Presentation
   
   ## Key Points
   
   - First important point
   - Second important point
   - Third important point
   ```

2. **Generate images**:
   ```bash
   python -m src.main presentation.md -o output_images
   ```

3. **View your images**: Check the `output_images` folder for your generated image slides.

## Usage

### Basic Usage

Convert a Markdown file to images with default settings:

```bash
python -m src.main yourfile.md -o output_folder
```

This command will:
- Read and parse `yourfile.md`
- Generate images for each slide/section
- Save images to `output_folder` directory
- Display a preview of each generated image

### Command-Line Interface

```
usage: main.py [-h] [--version] [-o OUTPUT] [-c CONFIG] [--no-show] input_file

Convert a Markdown file to a series of images.

positional arguments:
  input_file            The input Markdown file path

optional arguments:
  -h, --help            Show this help message and exit
  --version             Show program's version number and exit
  -o, --output OUTPUT   The directory where output images will be saved
                        (default: current directory)
  -c, --config CONFIG   Path to custom configuration file
                        (default: config.json)
  --no-show             Do not display images on screen after generation
```

### Advanced Usage Examples

**Use a custom configuration file:**
```bash
python -m src.main presentation.md -o slides -c custom_config.json
```

**Generate images without preview:**
```bash
python -m src.main document.md -o images --no-show
```

**Process multiple files with different configs:**
```bash
python -m src.main intro.md -o output/intro -c dark_theme.json
python -m src.main main.md -o output/main -c light_theme.json
python -m src.main outro.md -o output/outro -c dark_theme.json
```

## Configuration

The Markdown Image Generator uses a JSON configuration file to customize the appearance and behavior of generated images. By default, it uses `config.json` in the project root, but you can specify a custom configuration file using the `-c` flag.

### Configuration Structure

#### Colors Configuration

Customize the color scheme for your images:

```json
{
  "COLORS": {
    "TEXT": "#FFFFFF",
    "BACKGROUND": "#000000",
    "HIGHLIGHT": "#ffab00",
    "ITALIC_COLOR": "#e0e0e0",
    "LINK_COLOR": "#5dade2",
    "BULLET_COLOR": "#ffab00",
    "NUMBER_COLOR": "#ffab00",
    "QUOTE_COLOR": "#CCCCCC",
    "DIVIDER_COLOR": "#555555"
  }
}
```

**Color Options Explained:**
- `TEXT`: Main text color
- `BACKGROUND`: Background color (overridden if gradient is enabled)
- `HIGHLIGHT`: Bold text and highlights
- `ITALIC_COLOR`: Italic text color
- `LINK_COLOR`: Hyperlink color
- `BULLET_COLOR`: Bullet point color
- `NUMBER_COLOR`: Numbered list color
- `QUOTE_COLOR`: Blockquote text color
- `DIVIDER_COLOR`: Horizontal rule color

#### Gradient Backgrounds

Enable modern gradient backgrounds for a professional look:

```json
{
  "THEME": {
    "NAME": "dark",
    "GRADIENT": {
      "ENABLED": true,
      "START_COLOR": "#1a1a2e",
      "END_COLOR": "#16213e"
    }
  }
}
```

**Gradient Options:**
- `ENABLED`: Set to `true` to enable gradient, `false` for solid background
- `START_COLOR`: Gradient start color (top)
- `END_COLOR`: Gradient end color (bottom)

#### Page Layout Configuration

Control image dimensions and margins:

```json
{
  "PAGE_LAYOUT": {
    "TOP_MARGIN": 250,
    "BOTTOM_MARGIN": 250,
    "RIGHT_MARGIN": 80,
    "IMAGE_WIDTH": 1080,
    "IMAGE_HEIGHT": 1080,
    "CHAR_WIDTH": 15,
    "DEFAULT_LINE_HEIGHT": 30,
    "LIST_LINE_HEIGHT": 20,
    "START_INDEX": 0
  }
}
```

**Layout Options:**
- `TOP_MARGIN`: Top margin in pixels
- `BOTTOM_MARGIN`: Bottom margin in pixels
- `RIGHT_MARGIN`: Right margin in pixels
- `IMAGE_WIDTH`: Image width in pixels (1080 is Instagram-friendly)
- `IMAGE_HEIGHT`: Image height in pixels
- `CHAR_WIDTH`: Character width for text wrapping calculations
- `DEFAULT_LINE_HEIGHT`: Line height for paragraphs
- `LIST_LINE_HEIGHT`: Line height for list items
- `START_INDEX`: Starting index for image numbering

#### Code Block Styling

Customize code block appearance:

```json
{
  "CODE_BLOCK": {
    "SCALE_FACTOR": 2,
    "BACKGROUND": "#1e1e1e",
    "RADIUS": 20,
    "TOP_PADDING": 50
  }
}
```

**Code Block Options:**
- `SCALE_FACTOR`: Scaling multiplier for code text size
- `BACKGROUND`: Code block background color
- `RADIUS`: Corner radius in pixels for rounded corners
- `TOP_PADDING`: Top padding in pixels

#### Table Styling

Configure table rendering:

```json
{
  "TABLE": {
    "SCALE_FACTOR": 1,
    "FOREGROUND": "#FFFFFF",
    "BACKGROUND": "#292929",
    "HIGHLIGHT": "#ffab00",
    "HEADER_BG_COLOR": "#8c52ff",
    "HEADER_FG_COLOR": "#FFFFFF",
    "HEIGHT": 8
  }
}
```

**Table Options:**
- `SCALE_FACTOR`: Scaling multiplier for table text
- `FOREGROUND`: Table text color
- `BACKGROUND`: Table cell background
- `HIGHLIGHT`: Table borders and highlights
- `HEADER_BG_COLOR`: Header row background color
- `HEADER_FG_COLOR`: Header row text color
- `HEIGHT`: Row height multiplier

### Pre-built Themes

The generator includes pre-built themes for common use cases:

- **Dark Theme**: High contrast for presentations (default)
- **Light Theme**: Clean, bright appearance for educational content

### Custom Theme Examples

**Professional Corporate Theme:**
```json
{
  "COLORS": {
    "TEXT": "#2c3e50",
    "BACKGROUND": "#ecf0f1",
    "HIGHLIGHT": "#3498db",
    "LINK_COLOR": "#2980b9"
  },
  "THEME": {
    "GRADIENT": {
      "ENABLED": true,
      "START_COLOR": "#ecf0f1",
      "END_COLOR": "#d5dbdb"
    }
  }
}
```

**Vibrant Creative Theme:**
```json
{
  "COLORS": {
    "TEXT": "#FFFFFF",
    "BACKGROUND": "#000000",
    "HIGHLIGHT": "#ff6b6b",
    "BULLET_COLOR": "#4ecdc4",
    "LINK_COLOR": "#ffe66d"
  },
  "THEME": {
    "GRADIENT": {
      "ENABLED": true,
      "START_COLOR": "#667eea",
      "END_COLOR": "#764ba2"
    }
  }
}
```

## Project Structure

Understanding the project architecture:

```
Markdown-Image-Generator/
├── src/                          # Source code
│   ├── converters/               # Markdown element converters
│   │   └── md_to_image/         # Core conversion logic
│   ├── data/                     # Data structures and models
│   ├── image_generation/         # Image rendering engine
│   ├── input_output/             # File I/O operations
│   ├── utils/                    # Utility functions
│   └── main.py                   # Entry point
├── demo/                         # Example Markdown files
│   ├── bullet_list_demo.md
│   ├── code_demo.md
│   ├── comprehensive_demo.md
│   ├── ordered_list_demo.md
│   ├── plain_paragraphs_demo.md
│   └── table_demo.md
├── resources/                    # Static assets
│   ├── intro.png                # Title page background
│   ├── page.png                 # Default page background
│   └── final.png                # Final page background
├── tests/                        # Test suite
├── config.json                   # Default configuration
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package setup
└── README.md                     # This file
```

### Key Components

- **Converters**: Transform Markdown syntax into structured data representations
- **Image Generation**: Handles PIL/Pillow-based rendering with custom styling
- **Data Layer**: Manages element properties, styling rules, and layout calculations
- **Input/Output**: Handles file reading, parsing, and image saving operations
- **Utils**: Shared utilities for text processing, color handling, and more

## Troubleshooting

### Common Issues and Solutions

#### Issue: ModuleNotFoundError: No module named 'PIL'

**Solution**: Install Pillow dependency
```bash
pip install Pillow
```

#### Issue: Font not found error

**Solution**: Update the font path in your config.json to point to a valid TrueType font:
```json
{
  "PATHS": {
    "FONT": "/path/to/your/font.ttf"
  }
}
```

Common font paths:
- **Ubuntu/Debian**: `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`
- **macOS**: `/System/Library/Fonts/Helvetica.ttc`
- **Windows**: `C:\\Windows\\Fonts\\Arial.ttf`

#### Issue: Images are too small or text is cut off

**Solution**: Adjust the page layout settings in config.json:
```json
{
  "PAGE_LAYOUT": {
    "IMAGE_WIDTH": 1920,
    "IMAGE_HEIGHT": 1080,
    "TOP_MARGIN": 150,
    "BOTTOM_MARGIN": 150
  }
}
```

#### Issue: Colors not displaying correctly

**Solution**: Ensure color values are in valid hex format with the `#` prefix:
```json
{
  "COLORS": {
    "TEXT": "#FFFFFF",  // Correct
    "BACKGROUND": "#000000"  // Correct
  }
}
```

#### Issue: Generated images have poor quality

**Solution**: The generator uses high-resolution rendering by default. If you need higher quality:
1. Increase the `IMAGE_WIDTH` and `IMAGE_HEIGHT` in config.json
2. Adjust `SCALE_FACTOR` for code blocks and tables
3. Use lossless PNG format (default behavior)

### Getting Help

If you encounter issues not covered here:

1. **Check existing issues**: [GitHub Issues](https://github.com/djeada/Markdown-Image-Generator/issues)
2. **Create a new issue**: Provide:
   - Your Python version (`python --version`)
   - Error message or unexpected behavior
   - Sample Markdown file demonstrating the issue
   - Your configuration file (if using custom config)
3. **Community support**: Engage with the community through issue discussions

## Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or sharing ideas, your input helps make this project better for everyone.

### How to Contribute

#### For Minor Changes
- **Bug fixes**: Feel free to submit a pull request directly
- **Documentation improvements**: Fix typos, clarify instructions, add examples
- **Code style improvements**: Enhance code readability and consistency

#### For Major Changes
1. **Open an issue first**: Describe your proposed feature or change
2. **Discuss the approach**: Get feedback from maintainers and community
3. **Submit a pull request**: Once the approach is agreed upon

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/Markdown-Image-Generator.git
   cd Markdown-Image-Generator
   ```
   
   > Replace `<YOUR_USERNAME>` with your GitHub username

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run tests**:
   ```bash
   pytest
   ```

### Contribution Guidelines

- **Code Quality**: Follow existing code style and conventions
- **Testing**: Add tests for new features; ensure existing tests pass
- **Documentation**: Update README and docstrings for new features
- **Commits**: Write clear, descriptive commit messages
- **Pull Requests**: Provide a clear description of changes and their purpose

### Areas for Contribution

We especially welcome contributions in these areas:

- 🎨 New themes and color schemes
- 📝 Additional Markdown element support (footnotes, task lists, etc.)
- 🐛 Bug fixes and performance improvements
- 📚 Documentation and example enhancements
- 🧪 Test coverage improvements
- 🌐 Internationalization support
- 🎯 New export formats (PDF, SVG, etc.)

### Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We're building this together!

## Roadmap

Future plans for the Markdown Image Generator:

### Version 0.2.0
- [ ] Support for additional Markdown extensions (footnotes, definition lists)
- [ ] PDF export functionality
- [ ] Batch processing improvements
- [ ] Animation support for transitions between slides

### Version 0.3.0
- [ ] Web-based GUI for easier configuration
- [ ] Template marketplace for pre-built themes
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Real-time preview during editing

### Long-term Goals
- Interactive HTML5 output format
- Video generation from Markdown slides
- Collaborative editing features
- Plugin system for extensibility

Want to contribute to any of these features? Check our [GitHub Issues](https://github.com/djeada/Markdown-Image-Generator/issues) or create a new one!

## FAQ

### Q: What image format does the generator output?
**A:** The generator outputs PNG format by default, providing high quality and lossless compression suitable for presentations and web use.

### Q: Can I use this for commercial presentations?
**A:** Yes! The project is licensed under MIT License, allowing commercial use. Just ensure any custom fonts or background images you use have appropriate licenses.

### Q: How do I create multiple slides from one Markdown file?
**A:** The generator automatically creates separate images for different sections. Use headers (e.g., `##`, `###`) to denote new slides.

### Q: Can I customize fonts?
**A:** Yes, specify a custom TrueType font path in the `PATHS.FONT` configuration option.

### Q: What's the recommended image size for social media?
**A:** 
- Instagram: 1080x1080 (square) or 1080x1350 (portrait)
- LinkedIn: 1200x627 or 1080x1080
- Twitter: 1200x675
- Default config (1080x1080) works well for most platforms

### Q: Does it support dark mode?
**A:** Yes! Dark theme is the default. You can customize colors or create your own theme via config.json.

### Q: Can I process multiple files at once?
**A:** Currently, you need to run the command for each file. Batch processing improvements are planned for version 0.2.0.

### Q: How do I contribute a new theme?
**A:** Create a JSON configuration file with your theme settings and submit it via pull request with example images.

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What This Means

✅ **You CAN:**
- Use this software commercially
- Modify the source code
- Distribute original or modified versions
- Use it privately

✅ **You MUST:**
- Include the original copyright notice
- Include the MIT License text

✅ **You CANNOT:**
- Hold the authors liable for any damages
- Use authors' names for endorsement without permission

## Acknowledgments

- Built with [Pillow (PIL)](https://python-pillow.org/) for image processing
- Syntax highlighting powered by [Pygments](https://pygments.org/)
- Markdown parsing with [Python-Markdown](https://python-markdown.github.io/)

Special thanks to all [contributors](https://github.com/djeada/Markdown-Image-Generator/graphs/contributors) who have helped improve this project!

---

**Made with ❤️ by the open-source community**

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs or requesting features
- 🔄 Sharing with others who might benefit
- 💡 Contributing improvements

For questions, issues, or suggestions, please visit our [GitHub Issues](https://github.com/djeada/Markdown-Image-Generator/issues) page.
