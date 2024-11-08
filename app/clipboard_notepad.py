from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit


class ClipboardNotepad(QDialog):
    def __init__(self, clipboard_history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipboard History")
        self.resize(400, 300)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        # Load clipboard history
        self.load_history(clipboard_history)

    def load_history(self, clipboard_history):
        """Load clipboard history into the text area."""
        self.text_edit.setPlainText("\n".join(clipboard_history))
