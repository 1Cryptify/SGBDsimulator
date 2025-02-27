from PyQt5 import QtWidgets, QtCore

class HelpDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.setWindowTitle("Help")
        self.setModal(True)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.help_text = QtWidgets.QTextEdit(self)
        self.help_text.setReadOnly(True)
        self.help_text.setPlainText("This is the help dialog. Here you can find information about the application.")

        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search help...")

        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.help_text)

        self.setStyleSheet("""
            QTextEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)

        self.search_input.textChanged.connect(self.filter_help_content)

    def filter_help_content(self):
        """Filter the help content based on the search input."""
        search_text = self.search_input.text().lower()
        # Logic to filter help content goes here
        # For now, we will just print the search text
        print(f"Searching for: {search_text}")
