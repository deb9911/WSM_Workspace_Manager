from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QPoint, QSize, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QGuiApplication, QIcon
import json
import os


class Taskbar(QWidget):
    def __init__(self, show_main_window_callback):
        super().__init__()
        self.setWindowTitle("Workspace Taskbar")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

        # Initialize in horizontal expanded form
        self.init_horizontal_expanded()

        # Main Layout
        layout = QHBoxLayout()

        # Manager Button
        self.manager_button = QPushButton("Manager")
        self.manager_button.clicked.connect(show_main_window_callback)

        # Workspace Drawer Button
        self.drawer_button = QPushButton("Workspace Drawer")
        self.drawer_button.clicked.connect(self.toggle_drawer)

        # Close Button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_widget)

        # Add buttons to layout
        layout.addWidget(self.manager_button)
        layout.addWidget(self.drawer_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # Workspace Drawer (hidden initially)
        self.drawer = self.create_drawer()
        self.drawer.setVisible(False)
        self.drawer_animation = QPropertyAnimation(self.drawer, b"geometry")
        self.drawer_animation.setEasingCurve(QEasingCurve.InOutCubic)

    def init_horizontal_expanded(self):
        """Initialize the widget in a horizontal expanded form at the bottom of the screen."""
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(0, screen_geometry.height() - 50, screen_geometry.width(), 50)

    def create_drawer(self):
        """Create a sliding drawer with a list of installed applications."""
        drawer = QListWidget(self)
        drawer.setFixedSize(200, 300)  # Set desired drawer size
        apps = ["App1", "App2", "App3", "App4"]
        for app in apps:
            item = QListWidgetItem(app)
            drawer.addItem(item)
        return drawer

    def toggle_drawer(self):
        """Toggle the workspace drawer visibility with a slide effect."""
        if self.drawer.isVisible():
            self.drawer_animation.setStartValue(self.drawer.geometry())
            self.drawer_animation.setEndValue(QRect(self.geometry().right(), self.geometry().top(), 0, 300))
            self.drawer_animation.start()
            self.drawer.setVisible(False)
        else:
            self.drawer.setVisible(True)
            end_rect = QRect(self.geometry().right(), self.geometry().top(), 200, 300)
            self.drawer_animation.setStartValue(QRect(self.geometry().right(), self.geometry().top(), 0, 300))
            self.drawer_animation.setEndValue(end_rect)
            self.drawer_animation.start()

    def close_widget(self):
        """Close the widget."""
        self.close()

    def mousePressEvent(self, event):
        """Record the position where the user started dragging the widget."""
        self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        """Enable drag movement and snap to screen edges when near."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            screen_geometry = QGuiApplication.primaryScreen().geometry()

            # Snap to left or right edge if close enough
            if abs(self.x()) < 20:  # Snap to left edge
                self.setGeometry(0, 0, 50, screen_geometry.height())
            elif abs(self.x() + self.width() - screen_geometry.width()) < 20:  # Snap to right edge
                self.setGeometry(screen_geometry.width() - 50, 0, 50, screen_geometry.height())
            elif abs(self.y() + self.height() - screen_geometry.height()) < 20:  # Snap to bottom edge
                self.init_horizontal_expanded()  # Revert to horizontal layout at the bottom
            event.accept()

    def load_geometry(self):
        """Load the saved geometry (position and size) from a settings file."""
        settings_file = "../taskbar_settings.json"
        if os.path.exists(settings_file):
            with open(settings_file, "r") as file:
                settings = json.load(file)
                if "position" in settings and "size" in settings:
                    self.move(QPoint(*settings["position"]))
                    self.resize(QSize(*settings["size"]))
                else:
                    self.init_horizontal_expanded()
        else:
            self.init_horizontal_expanded()

    def save_geometry(self):
        """Save the current position and size of the taskbar."""
        settings = {
            "position": (self.x(), self.y()),
            "size": (self.width(), self.height())
        }
        with open("../taskbar_settings.json", "w") as file:
            json.dump(settings, file)

    def closeEvent(self, event):
        """Override close event to save geometry before closing."""
        self.save_geometry()
        super().closeEvent(event)
