from PyQt5 import QtWidgets, QtCore
from src.utils.settings_manager import SettingsManager

class UserProfile(QtWidgets.QWidget):
    def __init__(self, settings_manager, parent=None):
        super(UserProfile, self).__init__(parent)
        self.settings_manager = settings_manager
        self.layout = QtWidgets.QVBoxLayout(self)

        self.name_label = QtWidgets.QLabel("Name:", self)
        self.name_input = QtWidgets.QLineEdit(self)

        self.email_label = QtWidgets.QLabel("Email:", self)
        self.email_input = QtWidgets.QLineEdit(self)

        self.save_button = QtWidgets.QPushButton("Save", self)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.save_button)

        self.setStyleSheet("""
            QLabel {
                padding: 5px;
            }
            QLineEdit {
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

        self.load_profile()
        self.save_button.clicked.connect(self.save_profile)

    def load_profile(self):
        """Load the user profile information from the settings manager."""
        self.name_input.setText(self.settings_manager.settings["user_profile"]["name"])
        self.email_input.setText(self.settings_manager.settings["user_profile"]["email"])

    def save_profile(self):
        """Save the user profile information."""
        name = self.name_input.text()
        email = self.email_input.text()
        self.settings_manager.update_user_profile(name, email)
        print(f"Profile saved: Name - {name}, Email - {email}")
