# Markdown Image Generator

The Markdown Image Generator is a Python-based project that transforms Markdown documents into a series of images. It aims to provide a unique way to visualize Markdown content, especially useful for presentations, sharing over image-based platforms, or even for educational purposes.

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

- Parses different types of Markdown elements like headers, paragraphs, bullet lists, tables and code blocks.
- Each block of Markdown content is translated into a block of text in an image.
- Supports multiline blocks for code and tables.
- Adjustable image size and text wrapping.
- Supports custom styling for different block types.
- Option to use a background image for the generated images.

## Usage Examples

For instance, the following Markdown content:

```
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
python main.py yourfile.md
```

Replace `yourfile.md` with the path to your Markdown file.


## How to Contribute

Your contributions are invaluable to the project! If you're interested in making improvements:

- For minor updates, feel free to submit pull requests directly.
- For major changes, please start by opening an issue to discuss your ideas.
- Remember to update or add new tests as necessary to ensure the functionality remains robust.

## License and Acknowledgements

This project is released under the [MIT License](https://choosealicense.com/licenses/mit/), promoting open and collaborative software development.

We appreciate your interest and contributions to the Markdown Image Generator. Together, we can make it an even more powerful tool for the community.
