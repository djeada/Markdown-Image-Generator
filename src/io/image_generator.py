from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from typing import List

@dataclass
class TextBlock:
    type: str
    data: str

class ImageGenerator:
    def __init__(self, blocks: List[TextBlock], output_filename: str, bg_image=None, width=800, height=600, bg_color=(255, 255, 255), text_color=(0, 0, 0), font_path="arial.ttf"):
        self.blocks = blocks
        self.output_filename = output_filename
        self.bg_image = bg_image
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_path = font_path

    def generate_image(self):
        if self.bg_image:
            img = Image.open(self.bg_image).resize((self.width, self.height))
        else:
            img = Image.new('RGB', (self.width, self.height), color=self.bg_color)

        d = ImageDraw.Draw(img)

        y_text = 10
        for block in self.blocks:
            if block.type == 'header':
                font = ImageFont.truetype(self.font_path, size=20)
                d.text((10, y_text), block.data, fill=self.text_color, font=font)
                y_text += 30
            elif block.type == 'paragraph':
                font = ImageFont.truetype(self.font_path, size=15)
                d.text((10, y_text), block.data, fill=self.text_color, font=font)
                y_text += 20

        img.save(self.output_filename)

if __name__ == "__main__":
    blocks = [
        TextBlock('header', 'Header 1'),
        TextBlock('paragraph', 'This is a paragraph.'),
        TextBlock('header', 'Header 2'),
        TextBlock('paragraph', 'This is another paragraph.')
    ]
    generator = ImageGenerator(blocks, 'output.png', bg_image='img.png')
    generator.generate_image()
