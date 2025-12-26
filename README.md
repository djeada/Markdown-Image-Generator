# Markdown Image Generator

The Markdown Image Generator is a Python-based project that transforms Markdown documents into a series of beautiful, presentation-ready images. It aims to provide a unique way to visualize Markdown content, especially useful for presentations, sharing over image-based platforms, or even for educational purposes.

## Overview

Markdown, a popular markup language, is widely used for its simplicity and versatility. However, presenting Markdown content in a visually engaging way can be challenging. The Markdown Image Generator addresses this by converting Markdown files into images, making it easier to share and present Markdown content in a more digestible format.

## System Diagram

Below is a system diagram illustrating the workflow of the Markdown Image Generator:

```
+-------------+       +------------------+       +----------------+       +---------------------+
|             |       |                  |       |                |       |                     |
| Markdown    +------>+ Markdown Reader  +------>+ Converters     +------>+ Image Generation    |
| File (.md)  |       | (input_output)   |       | (converters)   |       | (image_generation)  |
|             |       |                  |       |                |       |                     |
+-------------+       +------------------+       +----------------+       +---------------------+
                                                         |       
                                                         |       
                                                         |       
                                                         v       
                                                 +----------------+       +---------------+
                                                 |                |       |               |
                                                 | Data Handling  +------>+ Image Saver   |
                                                 | (data)         |       | (input_output)|
                                                 |                |       |               |
                                                 +----------------+       +---------------+
```

## Features

### Markdown Elements Support
- **Headers & Titles**: Beautifully rendered section headers
- **Paragraphs**: Clean text rendering with automatic text wrapping
- **Bullet Lists**: Stylish bullet points with customizable colors
- **Numbered Lists**: Circular numbered badges for ordered content
- **Code Blocks**: Syntax-highlighted code with a modern terminal-like appearance
- **Tables**: Professional table rendering with customizable colors
- **Blockquotes**: Elegant quote styling with accent border
- **Horizontal Rules**: Decorative dividers with diamond accents

### Styling & Customization
- Adjustable image size and text wrapping
- Custom styling for different block types
- Option to use background images for generated slides
- **Gradient backgrounds**: Modern gradient effects for a polished look
- Configurable colors for text, highlights, bullets, and more
- Theme support for consistent styling

## Usage Examples

For instance, the following Markdown content:

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

Is adeptly transformed into an image like this:

![tmpqa7jtwlt](https://github.com/djeada/Markdown-Image-Generator/assets/37275728/f0bf1aa4-d9ff-4561-ac19-2ba2cede88fd)

## Installation

To get started with the Markdown Image Generator, follow these simple steps:

### Prerequisites

Ensure you have the following prerequisites installed:
- Python 3.9 or newer
- pip (Python package installer)

### Step-by-Step Installation

1. **Clone the Repository**: First, clone the repository to your local machine using Git:

```bash
git clone https://github.com/djeada/Markdown-Image-Generator.git
```

2. **Navigate to the Project Directory**: Change into the project directory:

```bash
cd Markdown-Image-Generator
```

3. **Install Dependencies**: Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

After installation, you can start using the Markdown Image Generator to convert your Markdown files into images.

### Basic Usage

1. **Prepare Your Markdown File**: Write your Markdown content in a .md file.

2. **Run the Generator**: Use the following command to generate images from your Markdown file:

```bash
python -m src.main yourfile.md -o output_folder
```

Replace `yourfile.md` with the path to your Markdown file.

### Command Line Options

```
usage: main.py [-h] [--version] [-o OUTPUT] [-c CONFIG] [--no-show] input_file

Convert a Markdown file to a series of images.

positional arguments:
  input_file            The input Markdown file.

optional arguments:
  -h, --help            show this help message and exit
  --version             Show program's version number and exit
  -o, --output OUTPUT   The directory where the output images will be saved.
  -c, --config CONFIG   Path to the configuration file.
  --no-show             Do not display the images on the screen.
```

### Using Custom Configuration

You can customize the appearance by providing a custom config file:

```bash
python -m src.main yourfile.md -o output_folder -c my_config.json
```

## Configuration

The `config.json` file allows you to customize various aspects of the generated images:

### Colors Configuration

```json
{
    "COLORS": {
        "TEXT": "#FFFFFF",
        "BACKGROUND": "#000000",
        "HIGHLIGHT": "#ffab00",
        "BULLET_COLOR": "#ffab00",
        "NUMBER_COLOR": "#ffab00",
        "QUOTE_COLOR": "#CCCCCC",
        "DIVIDER_COLOR": "#555555"
    }
}
```

### Gradient Backgrounds

Enable beautiful gradient backgrounds:

```json
{
    "THEME": {
        "GRADIENT": {
            "ENABLED": true,
            "START_COLOR": "#1a1a2e",
            "END_COLOR": "#16213e"
        }
    }
}
```

### Page Layout

```json
{
    "PAGE_LAYOUT": {
        "TOP_MARGIN": 250,
        "BOTTOM_MARGIN": 250,
        "RIGHT_MARGIN": 80,
        "IMAGE_WIDTH": 1080,
        "IMAGE_HEIGHT": 1080
    }
}
```

## How to Contribute

Your contributions are invaluable to the project! If you're interested in making improvements:

- For minor updates, feel free to submit pull requests directly.
- For major changes, please start by opening an issue to discuss your ideas.
- Remember to update or add new tests as necessary to ensure the functionality remains robust.

## License and Acknowledgements

This project is released under the [MIT License](https://choosealicense.com/licenses/mit/), promoting open and collaborative software development.

We appreciate your interest and contributions to the Markdown Image Generator. Together, we can make it an even more powerful tool for the community.
