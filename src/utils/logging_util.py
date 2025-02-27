import os
import datetime

class LoggingUtil:
    def __init__(self, log_file='activity_log.txt'):
        self.log_file = log_file
        self.ensure_log_file_exists()

    def ensure_log_file_exists(self):
        """Ensure the log file exists."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("Log File Created\n")

    def log(self, message):
        """Log a message with a timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_entry)

    def clear_logs(self):
        """Clear the log file."""
        with open(self.log_file, 'w') as f:
            f.truncate()  # Clear the log file
