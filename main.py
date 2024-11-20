import sys
from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow
from app.taskbar import Taskbar
import os


def resource_path(relative_path):
    """Get the absolute path to a resource in the PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):  # This attribute exists in PyInstaller executables
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


def main():
    app = QApplication(sys.argv)

    # Load the stylesheet (adjust path based on script's directory)
    # stylesheet_path = os.path.join(os.path.dirname(__file__), "static/taskbar.qss")
    stylesheet_path = resource_path("static/taskbar.qss")
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, "r") as style_file:
            app.setStyleSheet(style_file.read())
    else:
        print("Warning: Stylesheet not found at", stylesheet_path)

    # Initialize the main window and taskbar
    window = MainWindow()  # Ensure MainWindow is defined in main_window.py
    taskbar = Taskbar(show_main_window_callback=window.show)  # Pass show method for callback

    # Show the taskbar only
    taskbar.show()

    # Execute the app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
