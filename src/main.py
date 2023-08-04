from src.converters.md_to_text_block import MarkdownToTextBlock
from src.input_output.markdown_reader import MarkdownReader
from src.input_output.image_generator import ImageGenerator


def main():
    # Instantiate your classes
    markdown_reader = MarkdownReader()
    image_generator = ImageGenerator()
    markdown_interpreter = MarkdownToTextBlock()

    # Read markdown file
    markdown_lines = markdown_reader.read("file.md")

    # Interpret markdown lines into blocks
    text_blocks = markdown_interpreter.interpret(markdown_lines)

    # Generate images from TextBlock objects
    for text_block in text_blocks:
        images = image_generator.generate_images(text_block)

        # Display images or save them somewhere
        for idx, image in enumerate(images):
            image.show()  # or save with: image.save(f'output{idx}.png')


if __name__ == "__main__":
    main()
