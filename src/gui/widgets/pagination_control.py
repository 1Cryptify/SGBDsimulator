from PyQt5 import QtWidgets, QtCore

class PaginationControl(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PaginationControl, self).__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.prev_button = QtWidgets.QPushButton("Previous", self)
        self.next_button = QtWidgets.QPushButton("Next", self)
        self.page_label = QtWidgets.QLabel("Page 1", self)

        self.layout.addWidget(self.prev_button)
        self.layout.addWidget(self.page_label)
        self.layout.addWidget(self.next_button)

        self.setStyleSheet("""
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
            QLabel {
                padding: 5px;
            }
        """)

        self.prev_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)

        self.current_page = 1

    def set_page(self, page):
        """Set the current page and update the label."""
        self.current_page = page
        self.page_label.setText(f"Page {self.current_page}")

    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.set_page(self.current_page)

    def next_page(self):
        """Navigate to the next page."""
        self.current_page += 1
        self.set_page(self.current_page)
