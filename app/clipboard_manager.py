from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QGuiApplication


class ClipboardManager:
    def __init__(self):
        self.clipboard = QGuiApplication.clipboard()
        self.clipboard_history = []  # Store history of copied texts
        self.previous_text = ""
        self.start_monitoring()

    def start_monitoring(self):
        """Start a timer to check clipboard every 3 seconds."""
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        self.clipboard_timer.start(3000)  # Check every 3 seconds

    def check_clipboard(self):
        """Check if clipboard content has changed and update history if needed."""
        current_text = self.clipboard.text()

        # Ensure non-empty, unique text and different from last entry
        if current_text and current_text != self.previous_text:
            self.clipboard_history.append(current_text)
            self.previous_text = current_text

            # Limit history size to avoid excessive memory use
            if len(self.clipboard_history) > 50:
                self.clipboard_history.pop(0)

    def get_clipboard_history(self):
        """Return the list of clipboard history."""
        return self.clipboard_history
