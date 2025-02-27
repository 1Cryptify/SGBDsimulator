from PyQt5 import QtWidgets, QtCore

class NotificationSettings(QtWidgets.QWidget):
    def __init__(self, settings_manager, parent=None):
        super(NotificationSettings, self).__init__(parent)
        self.settings_manager = settings_manager
        self.layout = QtWidgets.QVBoxLayout(self)

        self.enable_notifications = QtWidgets.QCheckBox("Enable Notifications", self)
        self.email_notifications = QtWidgets.QCheckBox("Email Notifications", self)
        self.sms_notifications = QtWidgets.QCheckBox("SMS Notifications", self)

        self.save_button = QtWidgets.QPushButton("Save Preferences", self)

        self.layout.addWidget(self.enable_notifications)
        self.layout.addWidget(self.email_notifications)
        self.layout.addWidget(self.sms_notifications)
        self.layout.addWidget(self.save_button)

        self.setStyleSheet("""
            QCheckBox {
                padding: 5px;
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

        self.load_preferences()
        self.save_button.clicked.connect(self.save_preferences)

    def load_preferences(self):
        """Load notification preferences from the settings manager."""
        self.enable_notifications.setChecked(self.settings_manager.settings.get("notifications_enabled", False))
        self.email_notifications.setChecked(self.settings_manager.settings.get("email_notifications", False))
        self.sms_notifications.setChecked(self.settings_manager.settings.get("sms_notifications", False))

    def save_preferences(self):
        """Save notification preferences."""
        self.settings_manager.settings["notifications_enabled"] = self.enable_notifications.isChecked()
        self.settings_manager.settings["email_notifications"] = self.email_notifications.isChecked()
        self.settings_manager.settings["sms_notifications"] = self.sms_notifications.isChecked()
        self.settings_manager.save_settings()
        print("Notification preferences saved.")
