from PyQt5 import QtWidgets, QtCore

class NotificationBanner(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NotificationBanner, self).__init__(parent)
        self.setFixedHeight(50)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.message_label = QtWidgets.QLabel("", self)
        self.layout.addWidget(self.message_label)
        self.setStyleSheet("background-color: #28a745; color: white; padding: 10px; border-radius: 5px;")

    def set_message(self, message, duration=3000):
        """Set the notification message and auto-hide after a duration."""
        self.message_label.setText(message)
        self.show()
        QtCore.QTimer.singleShot(duration, self.hide)

    def clear_message(self):
        """Clear the displayed message."""
        self.message_label.clear()
        self.hide()
