from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database_connector import DatabaseConnector
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SGBD Simulator")
        self.setGeometry(100, 100, 800, 600)
        
        # Layout central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Bouton test
        test_button = QPushButton("Tester Connexion")
        test_button.clicked.connect(self.test_connection)
        layout.addWidget(test_button)
        
        # Initialiser le connecteur
        self.db_connector = DatabaseConnector()
        
    def test_connection(self):
        if self.db_connector.connect():
            print("Connexion réussie!")
        else:
            print("Échec de la connexion")
