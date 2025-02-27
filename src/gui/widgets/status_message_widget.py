from PyQt5 import QtWidgets, QtCore

class StatusMessageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(StatusMessageWidget, self).__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.message_label = QtWidgets.QLabel("", self)
        self.layout.addWidget(self.message_label)
        self.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; border-radius: 5px;")

    def set_message(self, message, duration=3000):
        """Set the message to be displayed and auto-hide after a duration."""
        self.message_label.setText(message)
        self.show()
        QtCore.QTimer.singleShot(duration, self.hide)

    def clear_message(self):
        """Clear the displayed message."""
        self.message_label.clear()
        self.hide()

    def show_success(self, message, duration=3000):
        """Show a success message."""
        self.setStyleSheet("background-color: #dff0d8; padding: 10px; border: 1px solid #d6e9c6; border-radius: 5px;")
        self.set_message(message, duration)

    def show_error(self, message, duration=3000):
        """Show an error message."""
        self.setStyleSheet("background-color: #f2dede; padding: 10px; border: 1px solid #ebccd1; border-radius: 5px;")
        self.set_message(message, duration)

    def show_info(self, message, duration=3000):
        """Show an info message."""
        self.setStyleSheet("background-color: #d9edf7; padding: 10px; border: 1px solid #bce8f1; border-radius: 5px;")
        self.set_message(message, duration)