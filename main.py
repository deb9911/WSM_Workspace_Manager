import sys
from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow
from app.taskbar import Taskbar


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    taskbar = Taskbar(show_main_window_callback=window.show)
    taskbar.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
