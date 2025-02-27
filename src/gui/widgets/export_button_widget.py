from PyQt5 import QtWidgets, QtCore

class ExportButtonWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, button_style=None, export_handler=None):
        super(ExportButtonWidget, self).__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.export_button = QtWidgets.QPushButton("Export", self)
        self.export_button.setStyleSheet(button_style or "background-color: #007BFF; color: white; padding: 10px; border: none; border-radius: 5px;")
        self.export_button.clicked.connect(self.export)

        self.layout.addWidget(self.export_button)
        self.export_handler = export_handler  # Store the custom export handler

    def export(self):
        """Handle the export action."""
        if self.export_handler:
            try:
                self.export_handler()  # Call the custom export handler
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Export Error", f"An error occurred during export: {str(e)}")

    def set_export_handler(self, handler):
        """Set a custom export handler."""
        self.export_handler = handler
