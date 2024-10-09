from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog, QWidget, QVBoxLayout,
    QComboBox, QTextEdit, QMenuBar, QAction, QSplitter
)
from PyQt5.QtCore import Qt
from .file_tree import FileTree
from .file_editor import FileEditor
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workspace Manager")
        self.resize(800, 600)

        # Initialize tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_file_manager_tab(), "File Manager")
        self.tabs.addTab(self.create_activity_history_tab(), "Activity History")

        # Menu bar with options
        self.create_menu_bar()

        # Main layout
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.change_theme(0)  # Load the default theme (Light)

    def create_menu_bar(self):
        # Create a menu bar
        menu_bar = QMenuBar(self)

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Add "Select Directory" action
        select_directory_action = QAction("Select Directory", self)
        select_directory_action.triggered.connect(self.select_directory)
        file_menu.addAction(select_directory_action)

        # Theme menu
        theme_menu = menu_bar.addMenu("Theme")

        # Add theme options to menu
        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(lambda: self.change_theme(0))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme(1))
        theme_menu.addAction(dark_theme_action)

        self.setMenuBar(menu_bar)

    def create_file_manager_tab(self):
        self.file_tree = FileTree()
        self.file_editor = FileEditor()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.file_editor)

        # Connect file tree to editor
        self.file_tree.file_selected.connect(self.file_editor.load_file)

        file_manager_widget = QWidget()
        file_manager_layout = QVBoxLayout()
        file_manager_layout.addWidget(splitter)
        file_manager_widget.setLayout(file_manager_layout)

        return file_manager_widget

    def create_activity_history_tab(self):
        self.activity_history = QTextEdit()
        self.activity_history.setReadOnly(True)
        self.load_activity_history()

        history_widget = QWidget()
        history_layout = QVBoxLayout()
        history_layout.addWidget(self.activity_history)
        history_widget.setLayout(history_layout)

        return history_widget

    def load_activity_history(self):
        # Load from a log file or list - replace "app.log" with your log file path
        log_path = "app.log"
        if os.path.exists(log_path):
            with open(log_path, "r") as log_file:
                history = log_file.read()
                self.activity_history.setPlainText(history)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if dir_path:
            self.file_tree.set_directory(dir_path)

    def change_theme(self, index):
        theme_files = ["themes/light.qss", "themes/dark.qss"]
        theme_path = theme_files[index]
        self.load_theme(theme_path)

    def load_theme(self, theme_path):
        if os.path.exists(theme_path):
            with open(theme_path, "r") as file:
                self.setStyleSheet(file.read())
