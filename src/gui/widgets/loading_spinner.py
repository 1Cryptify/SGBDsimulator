from PyQt5 import QtWidgets, QtCore, QtGui

class LoadingSpinner(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LoadingSpinner, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.spinner = QtWidgets.QLabel("Loading...", self)
        self.spinner.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.spinner)

        self.setStyleSheet("""
            LoadingSpinner {
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        self.animation = QtGui.QMovie("../../img/spinner.gif")
        self.animation.setScaledSize(QtCore.QSize(64, 64))
        self.spinner.setMovie(self.animation)

    def show_spinner(self, message="Loading..."):
        """Show the spinner with a custom message."""
        # self.spinner.setText(message)
        self.animation.start()
        self.show()

    def hide_spinner(self):
        """Hide the spinner."""
        self.animation.stop()
        self.hide()