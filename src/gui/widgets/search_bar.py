from PyQt5 import QtWidgets, QtCore, QtGui

class SearchBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SearchBar, self).__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search...")
        self.clear_button = QtWidgets.QPushButton("Clear", self)

        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.clear_button)

        self.setStyleSheet("QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 5px; }"
                           "QPushButton { background-color: #007BFF; color: white; padding: 5px; border: none; border-radius: 5px; }"
                           "QPushButton:hover { background-color: #0056b3; }")

        self.clear_button.clicked.connect(self.clear_search)

    def get_search_text(self):
        """Return the current text in the search input."""
        return self.search_input.text()

    def clear_search(self):
        """Clear the search input."""
        self.search_input.clear()

