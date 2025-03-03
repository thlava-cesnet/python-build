
import os, sys
from PySide6.QtWidgets import QMessageBox, QDialog, QDialogButtonBox, QVBoxLayout, QLabel

class Warning(QDialog):
    def __init__(self, parent=None, title="About", text="S3 rclone pygui (c) 2025 CESNET", icon=None):
        # icons: QMessageBox.NoIcon QMessageBox.Information QMessageBox.Question QMessageBox.Warning QMessageBox.Critical
        super().__init__(parent)
        self.box = QMessageBox()
        self.box.setWindowTitle(title)
        self.box.setText(text)
        if icon: self.box.setIcon(icon)
        self.box.accepted.connect(self.accept)
        layout = QVBoxLayout()
        layout.addWidget(self.box)
        self.setLayout(layout)

class Confirm(QDialog):
    def __init__(self, parent=None, txt="OK?"):
        super().__init__(parent)
        QBtn = ( QDialogButtonBox.Ok | QDialogButtonBox.Cancel )
        self.box = QDialogButtonBox(QBtn)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        layout = QVBoxLayout()
        message = QLabel(txt)
        layout.addWidget(message)
        layout.addWidget(self.box)
        self.setLayout(layout)

def resource_path(relpath):
    try:
        base = sys._MEIPASS
    except Exception as e:
        base = os.path.abspath(".")
    return os.path.join(base, relpath)

        
__all__ = ['Warning', 'Confirm', 'resource_path']