import json
import os

class SettingsManager:
    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.default_settings = {
            "feature_x_enabled": False,
            "setting_y": 50,
            "user_name": "root",
            "user_email": "root@example.com",
        }
        self.load_settings()

    def save_settings(self):
        """Save the current settings to a file."""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)

    def load_settings(self):
        """Load settings from a file, or use default settings if the file does not exist."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = self.default_settings

    def reset_settings(self):
        """Reset settings to default values."""
        self.settings = self.default_settings
        self.save_settings()
