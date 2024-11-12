from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect, QMenu, QAction, QFileDialog, QDialog, QFormLayout, QLineEdit, QLabel
)
from PyQt5.QtCore import Qt, QPoint, QSize, QProcess
from PyQt5.QtGui import QGuiApplication, QIcon, QColor, QLinearGradient, QPainter, QBrush
import json
import os

from app.clipboard_manager import ClipboardManager
from app.clipboard_notepad import ClipboardNotepad  # Separate notepad view for clipboard history


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
        layout.addRow("", browse_button)  # Position the browse button next to the path field
        layout.addRow("Parameters:", self.parameters_field)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
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


class Taskbar(QWidget):
    def __init__(self, show_main_window_callback):
        super().__init__()
        self.setWindowTitle("Workspace Taskbar")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)

        self.is_minimized = False
        self.saved_geometry = None
        self.minimized_widget = None
        self.dragging = False
        self.is_vertical = False

        self.init_horizontal_expanded()

        self.clipboard_manager = ClipboardManager()

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        button_size = QSize(40, 40)
        icon_size = QSize(24, 24)

        self.manager_button = self.create_button("resources/icons/manager.png", button_size, icon_size, show_main_window_callback)
        self.clipboard_button = self.create_button("resources/icons/clipboard.png", button_size, icon_size, self.show_clipboard_notepad)
        self.resize_button = self.create_button("resources/icons/minimize_taskbar.png", button_size, icon_size, self.toggle_minimize)
        self.close_button = self.create_button("resources/icons/cross_taskbar_close.png", button_size, icon_size, self.close_widget)

        button_size = QSize(40, 40)
        icon_size = QSize(24, 24)

        # self.launcher_button = QPushButton("Launcher")
        self.launcher_button = QPushButton()
        self.launcher_menu = QMenu()
        self.launcher_button.setIcon(QIcon("resources/icons/launcher.png"))
        self.launcher_button.setMenu(self.launcher_menu)
        self.launcher_button.setFixedSize(button_size)
        self.launcher_button.setIconSize(icon_size)

        self.load_launcher_entries()

        add_entry_action = QAction("+ Add New Entry", self)
        add_entry_action.triggered.connect(self.show_add_entry_dialog)
        self.launcher_menu.addAction(add_entry_action)
        self.launcher_menu.addSeparator()

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

    def load_launcher_entries(self):
        self.launcher_entries = []
        try:
            with open("launcher_entries.json", "r") as file:
                self.launcher_entries = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        for entry in self.launcher_entries:
            self.add_launcher_entry_to_menu(entry)

    def save_launcher_entries(self):
        with open("launcher_entries.json", "w") as file:
            json.dump(self.launcher_entries, file, indent=4)

    def add_launcher_entry_to_menu(self, entry):
        action = QAction(entry["name"], self)
        action.triggered.connect(lambda _, e=entry: self.execute_entry(e))
        self.launcher_menu.addAction(action)

    def show_add_entry_dialog(self):
        dialog = AddLauncherEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            entry_data = dialog.get_entry_data()
            self.launcher_entries.append(entry_data)
            self.add_launcher_entry_to_menu(entry_data)
            self.save_launcher_entries()

    def execute_entry(self, entry):
        process = QProcess(self)
        args = entry["parameters"].split() if entry["parameters"] else []
        process.start(entry["path"], args)

    def init_horizontal_expanded(self):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(0, screen_geometry.height() - 50, screen_geometry.width(), 50)

    def apply_styles(self):
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
        for button in [self.manager_button, self.clipboard_button, self.resize_button, self.close_button, self.launcher_button]:
            button.setStyleSheet(button_style)

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(15)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(2)
        shadow_effect.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow_effect)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 220))
        gradient.setColorAt(1, QColor(240, 240, 240, 220))
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

    def add_buttons_to_layout(self):
        self.main_layout.addWidget(self.manager_button)
        self.main_layout.addWidget(self.clipboard_button)
        self.main_layout.addWidget(self.launcher_button)

        self.main_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.resize_button)
        self.main_layout.addWidget(self.close_button)

    def show_clipboard_notepad(self):
        clipboard_history = self.clipboard_manager.get_clipboard_history()
        if not hasattr(self, 'notepad') or not self.notepad.isVisible():
            self.notepad = ClipboardNotepad(clipboard_history)
            self.notepad.show()

    def toggle_minimize(self):
        if not self.is_minimized:
            self.saved_geometry = self.geometry()
            self.hide()
            self.show_minimized_widget()
        else:
            self.restore()
        self.is_minimized = not self.is_minimized

    def show_minimized_widget(self):
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
        if self.saved_geometry:
            self.setGeometry(self.saved_geometry)
            self.show()
            self.minimized_widget.hide()
            self.minimized_widget.deleteLater()
        self.is_minimized = False

    def close_widget(self):
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
            left_distance = abs(self.x())
            right_distance = abs(self.x() + self.width() - screen_geometry.width())
            top_distance = abs(self.y())
            bottom_distance = abs(self.y() + self.height() - screen_geometry.height())

            min_distance = min(left_distance, right_distance, top_distance, bottom_distance)
            if min_distance == left_distance:
                self.snap_to_left(screen_geometry)
            elif min_distance == right_distance:
                self.snap_to_right(screen_geometry)
            elif min_distance == top_distance:
                self.snap_to_top(screen_geometry)
            else:
                self.init_horizontal_expanded()

    def snap_to_left(self, screen_geometry):
        self.setGeometry(0, 0, 50, screen_geometry.height())
        self.set_vertical_layout()

    def snap_to_right(self, screen_geometry):
        self.setGeometry(screen_geometry.width() - 50, 0, 50, screen_geometry.height())
        self.set_vertical_layout()

    def snap_to_top(self, screen_geometry):
        self.setGeometry(0, 0, screen_geometry.width(), 50)
        self.set_horizontal_layout()

    def set_vertical_layout(self):
        self.is_vertical = True
        self.realign_buttons()

    def set_horizontal_layout(self):
        self.is_vertical = False
        self.realign_buttons()

    def realign_buttons(self):
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                self.main_layout.removeWidget(widget)
                widget.setParent(None)

        if self.is_vertical:
            self.main_layout.setDirection(QVBoxLayout.TopToBottom)
        else:
            self.main_layout.setDirection(QHBoxLayout.LeftToRight)

        self.add_buttons_to_layout()
