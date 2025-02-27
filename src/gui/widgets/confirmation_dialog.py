from PyQt5 import QtWidgets, QtCore

class ConfirmationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ConfirmationDialog, self).__init__(parent)
        self.setWindowTitle("Confirmation")
        self.setModal(True)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.message_label = QtWidgets.QLabel("", self)
        self.layout.addWidget(self.message_label)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.confirm_button = QtWidgets.QPushButton("Confirm", self)
        self.cancel_button = QtWidgets.QPushButton("Cancel", self)

        self.button_layout.addWidget(self.confirm_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 10px;
            }
            QLabel {
                font-size: 16px;
                margin: 10px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def set_message(self, message):
        """Set the confirmation message."""
        self.message_label.setText(message)

    def exec_dialog(self):
        """Execute the dialog and return the result."""
        return self.exec_()
