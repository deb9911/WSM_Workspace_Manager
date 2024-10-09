from PyQt5.QtWidgets import QPlainTextEdit

class FileEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(False)

    def load_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            self.setPlainText(content)
        # Add syntax highlighting logic here for Python, batch, and shell scripts
