from PyQt5 import QtWidgets, QtCore

class FileUploader(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(FileUploader, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("Drag and drop files here or click to upload.", self)
        self.upload_button = QtWidgets.QPushButton("Upload", self)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.upload_button)

        self.setStyleSheet("""
            QLabel {
                padding: 20px;
                border: 2px dashed #007BFF;
                border-radius: 10px;
                text-align: center;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.upload_button.clicked.connect(self.browse_files)

    def browse_files(self):
        """Open a file dialog to select files for upload."""
        options = QtWidgets.QFileDialog.Options()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*);;Text Files (*.txt)", options=options)
        if files:
            self.label.setText("\n".join(files))  # Display selected file names

    def clear_files(self):
        """Clear the displayed file names."""
        self.label.setText("Drag and drop files here or click to upload.")
