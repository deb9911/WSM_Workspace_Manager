from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect, QMenu, QAction, QFileDialog, QDialog, QFormLayout, QLineEdit, QLabel, QTextEdit,
    QComboBox,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSize, QPoint, QProcess, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QGuiApplication, QIcon, QColor, QLinearGradient, QPainter, QBrush
import json
import os, sys

from app.clipboard_manager import ClipboardManager
from app.clipboard_notepad import ClipboardNotepad
from app.url_access import get_chrome_open_urls, get_edge_open_urls, get_firefox_open_urls
from app.file_indexer import index_files, load_file_index


def resource_path(relative_path):
    """Get the absolute path to a resource, works for both development and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller-specific temporary folder
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class FileIndexerThread(QThread):
    """Thread to handle background file indexing."""
    finished = pyqtSignal()

    def run(self):
        index_files([Path.home()])
        self.finished.emit()


class AddLauncherEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Launcher Entry")
        self.setFixedSize(400, 200)

        layout = QFormLayout()
        self.name_field = QLineEdit(self)
        self.path_field = QLineEdit(self)
        self.parameters_field = QLineEdit(self)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_for_executable)

        layout.addRow("Entry Name:", self.name_field)
        layout.addRow("Executable Path:", self.path_field)
        layout.addRow("", browse_button)
        layout.addRow("Parameters:", self.parameters_field)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def browse_for_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Executable")
        if file_path:
            self.path_field.setText(file_path)

    def get_entry_data(self):
        return {
            "name": self.name_field.text(),
            "path": self.path_field.text(),
            "parameters": self.parameters_field.text()
        }


class URLDialog(QDialog):
    def __init__(self, urls, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open URLs")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        self.url_text = QTextEdit(self)
        self.url_text.setReadOnly(True)
        self.url_text.setPlainText("\n".join(urls))

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        button_box.accepted.connect(self.save_urls)
        button_box.rejected.connect(self.reject)

        layout.addWidget(QLabel("Open URLs:"))
        layout.addWidget(self.url_text)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def save_urls(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save URLs", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.url_text.toPlainText())
        self.accept()


class FileSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Search")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter file name or extension (e.g., '.txt')")
        layout.addWidget(QLabel("Search Files:"))
        layout.addWidget(self.search_input)

        self.results_text = QTextEdit(self)
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        button_layout = QHBoxLayout()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.perform_search)
        save_button = QPushButton("Save Results")
        save_button.clicked.connect(self.save_results)
        button_layout.addWidget(search_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def perform_search(self):
        search_term = self.search_input.text().strip().lower()
        if not search_term:
            self.results_text.setText("Please enter a search term.")
            return

        file_index = load_file_index()
        results = []
        for filename, paths in file_index.items():
            if search_term in filename.lower():
                results.extend(paths)

        self.results_text.setPlainText("\n".join(results) if results else "No files found.")

    def save_results(self):
        results_text = self.results_text.toPlainText()
        if not results_text:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Search Results", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as file:
                file.write(results_text)


class Taskbar(QWidget):
    def __init__(self, show_main_window_callback):
        super().__init__()
        self.setWindowTitle("Workspace Taskbar")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
        self.is_minimized = False
        self.saved_geometry = None
        # Initialize UI and other components
        self.init_horizontal_expanded()
        self.clipboard_manager = ClipboardManager()
        self.notepad = None
        # Set up layout and UI components
        self.init_ui(show_main_window_callback)
        self.apply_styles()
        # Set up and defer file indexing
        self.indexer_thread = FileIndexerThread()
        self.indexer_thread.finished.connect(self.on_file_indexing_finished)
        # Run indexing in the background after the taskbar UI is shown
        QTimer.singleShot(1000, self.indexer_thread.start)  # Starts indexing 1 second after initialization

    def init_ui(self, show_main_window_callback):
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        button_size = QSize(40, 40)
        icon_size = QSize(24, 24)

        self.manager_button = self.create_button(resource_path("resources/icons/manager.png"), button_size, icon_size,
                                                 show_main_window_callback)
        self.clipboard_button = self.create_button(resource_path("resources/icons/clipboard.png"), button_size, icon_size,
                                                   self.show_clipboard_notepad)
        self.launcher_button = self.create_launcher_button(button_size, icon_size)
        self.url_list_button = self.create_button(resource_path("resources/icons/url_list.png"), button_size, icon_size,
                                                  self.show_url_list)
        self.search_button = self.create_button(resource_path("resources/icons/file_search.png"), button_size, icon_size,
                                                self.show_search_dialog)
        self.resize_button = self.create_button(resource_path("resources/icons/minimize_taskbar.png"), button_size, icon_size,
                                                self.toggle_minimize)
        self.close_button = self.create_button(resource_path("resources/icons/cross_taskbar_close.png"), button_size, icon_size,
                                               self.close_widget)

        # Add relocation dropdown
        self.relocation_dropdown = QComboBox()
        self.relocation_dropdown.addItems(["↓", "↑"])
        self.relocation_dropdown.currentTextChanged.connect(self.relocate_taskbar)
        self.main_layout.addWidget(self.relocation_dropdown)

        self.add_buttons_to_layout()
        self.setLayout(self.main_layout)
        self.apply_styles()

    def create_button(self, icon_path, button_size, icon_size, callback):
        button = QPushButton()
        button.setFixedSize(button_size)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(icon_size)
        button.clicked.connect(callback)
        return button

    def show_search_dialog(self):
        search_dialog = FileSearchDialog(self)
        search_dialog.exec_()

    def create_launcher_button(self, button_size, icon_size):
        launcher_button = QPushButton()
        launcher_button.setFixedSize(button_size)
        launcher_button.setIcon(QIcon("resources/icons/launcher.png"))
        launcher_button.setIconSize(icon_size)

        launcher_menu = QMenu()
        add_entry_action = QAction("+ Add New Entry", self)
        add_entry_action.triggered.connect(self.show_add_entry_dialog)
        launcher_menu.addAction(add_entry_action)
        launcher_button.setMenu(launcher_menu)
        self.load_launcher_entries(launcher_menu)
        return launcher_button

    def load_launcher_entries(self, launcher_menu):
        try:
            with open("launcher_entries.json", "r") as file:
                self.launcher_entries = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.launcher_entries = []

        for entry in self.launcher_entries:
            action = QAction(entry["name"], self)
            action.triggered.connect(lambda _, e=entry: self.execute_entry(e))
            launcher_menu.addAction(action)

    def show_add_entry_dialog(self):
        dialog = AddLauncherEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            entry_data = dialog.get_entry_data()
            self.launcher_entries.append(entry_data)
            self.save_launcher_entries()
            action = QAction(entry_data["name"], self)
            action.triggered.connect(lambda _, e=entry_data: self.execute_entry(e))
            self.launcher_button.menu().addAction(action)

    def save_launcher_entries(self):
        with open("launcher_entries.json", "w") as file:
            json.dump(self.launcher_entries, file, indent=4)

    def execute_entry(self, entry):
        process = QProcess(self)
        args = entry["parameters"].split() if entry["parameters"] else []
        process.start(entry["path"], args)

    def show_url_list(self):
        urls = self.get_all_open_urls()
        if urls:
            url_dialog = URLDialog(urls, self)
            url_dialog.exec_()

    def get_all_open_urls(self):
        urls = []
        urls.extend(get_chrome_open_urls())
        urls.extend(get_edge_open_urls())
        urls.extend(get_firefox_open_urls())
        return urls

    def relocate_taskbar(self, position):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        if position == "↑":
            self.setGeometry(0, 0, screen_geometry.width(), 50)
            self.set_horizontal_layout()
        elif position == "↓":
            self.setGeometry(0, screen_geometry.height() - 50, screen_geometry.width(), 50)
            self.set_horizontal_layout()

    def init_horizontal_expanded(self):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(0, screen_geometry.height() - 50, screen_geometry.width(), 50)

    def apply_styles(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(45, 45, 48))  # Dark gray gradient
        gradient.setColorAt(1, QColor(30, 30, 32))  # Slightly darker at the bottom
        p.setBrush(self.backgroundRole(), QBrush(gradient))
        self.setPalette(p)

        button_style = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #d3d3d3;
            }
        """
        for button in [self.manager_button, self.clipboard_button, self.launcher_button, self.url_list_button,
                       self.search_button, self.resize_button, self.close_button]:
            button.setStyleSheet(button_style)

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(15)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(2)
        shadow_effect.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow_effect)

    def add_buttons_to_layout(self):
        self.main_layout.addWidget(self.manager_button)
        self.main_layout.addWidget(self.clipboard_button)
        self.main_layout.addWidget(self.launcher_button)
        self.main_layout.addWidget(self.url_list_button)
        self.main_layout.addWidget(self.search_button)

        self.main_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.resize_button)
        self.main_layout.addWidget(self.relocation_dropdown)
        self.main_layout.addWidget(self.close_button)

    def set_vertical_layout(self):
        self.main_layout.setDirection(QVBoxLayout.TopToBottom)
        self.realign_buttons()

    def set_horizontal_layout(self):
        self.main_layout.setDirection(QHBoxLayout.LeftToRight)
        self.realign_buttons()

    def realign_buttons(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.add_buttons_to_layout()

    def show_clipboard_notepad(self):
        """Show clipboard notepad if not already visible, and handle any unexpected errors."""
        try:
            clipboard_history = self.clipboard_manager.get_clipboard_history()
            if not self.notepad or not self.notepad.isVisible():
                self.notepad = ClipboardNotepad(clipboard_history)
                self.notepad.show()
        except Exception as e:
            print(f"Error showing ClipboardNotepad: {e}")

    def toggle_minimize(self):
        if not self.is_minimized:
            self.saved_geometry = self.geometry()
            self.hide()
            self.show_minimized_widget()
        else:
            self.restore()
        self.is_minimized = not self.is_minimized

    def show_minimized_widget(self):
        # Prevent multiple minimized widgets from being created
        if hasattr(self, 'minimized_widget') and self.minimized_widget.isVisible():
            return

        self.minimized_widget = QWidget()
        self.minimized_widget.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.minimized_widget.setFixedSize(60, 60)
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.minimized_widget.move(screen_geometry.width() // 2 - 30, screen_geometry.height() - 70)

        layout = QVBoxLayout()
        icon_button = QPushButton()
        icon_button.setIcon(QIcon("resources/icons/suraj_icon_210.png"))
        icon_button.setIconSize(QSize(50, 50))
        icon_button.clicked.connect(self.restore)
        layout.addWidget(icon_button)
        self.minimized_widget.setLayout(layout)
        self.minimized_widget.show()

    def restore(self):
        if hasattr(self, 'minimized_widget') and self.minimized_widget.isVisible():
            self.minimized_widget.hide()
            self.minimized_widget.deleteLater()
            del self.minimized_widget  # Ensure the widget is fully removed
        self.setGeometry(self.saved_geometry)  # Restore original geometry
        self.show()

    def close_widget(self):
        self.close()

    def on_file_indexing_finished(self):
        print("File indexing completed.")

