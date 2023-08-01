class MarkdownReader:
    def __init__(self, filename):
        self.filename = filename

    def read_file(self):
        try:
            with open(self.filename, 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"File {self.filename} not found.")
            return None
