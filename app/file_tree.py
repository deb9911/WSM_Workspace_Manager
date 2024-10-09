from PyQt5.QtWidgets import QTreeView, QFileSystemModel
from PyQt5.QtCore import pyqtSignal

class FileTree(QTreeView):
    file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.model = QFileSystemModel()
        self.setModel(self.model)
        self.clicked.connect(self.on_file_selected)

    def set_directory(self, path):
        self.model.setRootPath(path)
        self.setRootIndex(self.model.index(path))

    def on_file_selected(self, index):
        file_path = self.model.filePath(index)
        if self.model.isDir(index):
            return
        self.file_selected.emit(file_path)
