import os
import signal
from PyQt5.QtWidgets import QApplication
import sys
from gui.main_window import MainWindow

def signal_handler(signum, frame):
    QApplication.quit()
    sys.exit(0)

def setup_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    app_name = "✨ SGDB Simulator ✨"
    border = "★" * (len(app_name) + 4)
    print("\033[38;5;219m" + border)  # Pink color
    print(f"♦ {app_name} ♦")
    print("\033[38;5;147m" + border)  # Purple color
    print("\033[1;36m═══════════════════════")  # Cyan color, bold
    print("\033[38;5;226m⚡ Welcome to SGDB! ⚡\033[0m")  # Yellow color

def main():
    signal.signal(signal.SIGINT, signal_handler)
    setup_console()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()