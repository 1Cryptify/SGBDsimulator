from PyQt5 import QtWidgets, QtCore
from src.utils.logging_util import LoggingUtil

class ActivityLog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ActivityLog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.log_list = QtWidgets.QListWidget(self)
        self.clear_button = QtWidgets.QPushButton("Clear Logs", self)

        self.layout.addWidget(self.log_list)
        self.layout.addWidget(self.clear_button)
        self.save_button = QtWidgets.QPushButton("Save Logs", self)
        self.layout.addWidget(self.save_button)

        self.setStyleSheet("""
            QListWidget {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.clear_button.clicked.connect(self.clear_logs)
        self.save_button.clicked.connect(self.save_logs)

    def add_log_entry(self, message):
        """Add a new log entry to the list."""
        self.log_list.addItem(message)

    def clear_logs(self):
        """Clear all log entries."""
        self.log_list.clear()
