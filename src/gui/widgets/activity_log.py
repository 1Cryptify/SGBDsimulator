from PyQt5 import QtWidgets, QtCore
from utils.logging_util import LoggingUtil

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

    def save_logs(self):
        """Save all log entries to a file."""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Logs",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            with open(filename, 'w') as f:
                for i in range(self.log_list.count()):
                    f.write(self.log_list.item(i).text() + '\n')