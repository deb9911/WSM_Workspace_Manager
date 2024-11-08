from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QPoint, QSize, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt5.QtGui import QGuiApplication, QIcon
import json
import os
import platform
import glob

from app.clipboard_manager import ClipboardManager
from app.clipboard_notepad import ClipboardNotepad  # Separate notepad view for clipboard history


class Taskbar(QWidget):
    def __init__(self, show_main_window_callback):
        super().__init__()
        self.setWindowTitle("Workspace Taskbar")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.is_minimized = False
        self.saved_geometry = None  # Save full geometry for restoration
        self.minimized_widget = None  # Reference to the minimized widget

        # Initialize expanded position
        self.init_horizontal_expanded()

        # Clipboard Manager for tracking clipboard history
        self.clipboard_manager = ClipboardManager()

        # Main layout setup
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Manager Button
        self.manager_button = QPushButton("Manager")
        self.manager_button.clicked.connect(show_main_window_callback)

        # Clipboard Button
        self.clipboard_button = QPushButton("Clipboard History")
        self.clipboard_button.clicked.connect(self.show_clipboard_notepad)

        # Workspace Drawer Button
        self.drawer_button = QPushButton("Workspace Drawer")
        self.drawer_button.clicked.connect(self.toggle_drawer)

        # Minimize Button
        self.minimize_button = QPushButton("▼")
        self.minimize_button.clicked.connect(self.toggle_minimize)

        # Close Button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_widget)

        # Add buttons to layout
        layout.addWidget(self.manager_button)
        layout.addWidget(self.clipboard_button)
        layout.addWidget(self.drawer_button)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # Workspace Drawer setup
        self.drawer = self.create_drawer()
        self.drawer.setVisible(False)
        self.drawer_animation = QPropertyAnimation(self.drawer, b"geometry")
        self.drawer_animation.setEasingCurve(QEasingCurve.InOutCubic)

    def init_horizontal_expanded(self):
        """Initialize the widget in a horizontal expanded form at the bottom of the screen."""
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(0, screen_geometry.height() - 50, screen_geometry.width(), 50)

    def show_clipboard_notepad(self):
        """Open a new window showing the clipboard history."""
        clipboard_history = self.clipboard_manager.get_clipboard_history()
        self.notepad = ClipboardNotepad(clipboard_history)
        self.notepad.show()

    def create_drawer(self):
        """Create a sliding drawer with a list of installed applications."""
        drawer = QListWidget(self)
        drawer.setFixedSize(200, 300)

        # Retrieve applications
        apps = self.get_installed_applications()
        for app in apps:
            item = QListWidgetItem(app)
            drawer.addItem(item)
        return drawer

    def get_installed_applications(self):
        """Return a list of installed applications, compatible with Windows and Linux."""
        apps = []
        if platform.system() == "Windows":
            start_menu_path = os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs")
            apps = [os.path.splitext(os.path.basename(p))[0] for p in glob.glob(f"{start_menu_path}\\*.lnk")]
        elif platform.system() == "Linux":
            app_dirs = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
            for app_dir in app_dirs:
                apps += [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(f"{app_dir}/*.desktop")]
        return apps or ["Sample App1", "Sample App2", "Sample App3"]

    def toggle_drawer(self):
        """Toggle the workspace drawer visibility with a slide effect."""
        if self.drawer.isVisible():
            end_rect = QRect(self.geometry().right(), self.geometry().top(), 0, 300)
            self.drawer_animation.setStartValue(self.drawer.geometry())
            self.drawer_animation.setEndValue(end_rect)
            self.drawer_animation.finished.connect(lambda: self.drawer.setVisible(False))
            self.drawer_animation.start()
        else:
            start_rect = QRect(self.geometry().right(), self.geometry().top(), 0, 300)
            end_rect = QRect(self.geometry().right(), self.geometry().top(), 200, 300)
            self.drawer.setGeometry(start_rect)
            self.drawer.setVisible(True)
            self.drawer_animation.setStartValue(start_rect)
            self.drawer_animation.setEndValue(end_rect)
            self.drawer_animation.start()

    def toggle_minimize(self):
        """Minimize the widget to a floating button or restore to full size."""
        if not self.is_minimized:
            # Save current geometry and minimize
            self.saved_geometry = self.geometry()
            self.hide()  # Hide the main widget
            self.show_minimized_widget()  # Show minimized widget with icon
        else:
            self.restore()  # Restore to previous saved geometry

        self.is_minimized = not self.is_minimized

    def show_minimized_widget(self):
        """Show a minimized widget with an icon that restores the main widget on click."""
        self.minimized_widget = QWidget()
        self.minimized_widget.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.minimized_widget.setFixedSize(60, 60)

        # Center minimized widget on the screen, above the taskbar
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.minimized_widget.move(screen_geometry.width() // 2 - 30, screen_geometry.height() - 70)

        # Set up layout with an icon button
        layout = QVBoxLayout()
        icon_button = QPushButton()
        icon_button.setIcon(QIcon("resources/icons/suraj_icon_210.png"))  # Load the provided icon
        icon_button.setIconSize(QSize(50, 50))
        icon_button.clicked.connect(self.restore)  # Restore on click
        layout.addWidget(icon_button)
        self.minimized_widget.setLayout(layout)
        self.minimized_widget.show()

    def restore(self):
        """Restore the widget to its saved full geometry."""
        if self.saved_geometry:
            self.setGeometry(self.saved_geometry)
            self.show()  # Show main widget
            self.minimized_widget.hide()  # Hide minimized widget
            self.minimized_widget.deleteLater()  # Remove minimized widget
        self.is_minimized = False

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
            screen_geometry = QGuiApplication.primaryScreen().availableGeometry()

            # Snap to edges when close to them
            if abs(self.x()) < 20 and abs(self.y()) < 20:  # Snap to top edge
                self.setGeometry(0, 0, screen_geometry.width(), 50)
            elif abs(self.x()) < 20:  # Snap to left edge
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
